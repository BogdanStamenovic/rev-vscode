"""Build the simulation SDK ("simsdk") the simulator compiles and runs user code against.

Two jars come out, cached by a hash of their inputs:

- ``runtime.jar``: the simulator (org.pyftc.sim) plus the shims that replace the
  few SDK classes that cannot run off-Android (OpMode, LinearOpMode,
  ElapsedTime, RobotLog, the I2C sensor drivers, ...). At run time it goes on the
  classpath BEFORE the real SDK jars, so everything not shimmed is the real SDK.
- ``api.jar``: what user code is compiled against. It holds only classes the
  simulator actually supports: the shims, and real SDK classes whose bytecode
  does not reach Android or the wall clock (checked here from each class file's
  constant pool, then loaded for real by a JVM sweep). Code that uses anything
  else fails to compile, naming the class, instead of running against something
  that silently behaves differently from the robot.

The real SDK class files come from Maven Central (the same artifacts
scripts/javac-env.sh fetches); gson and gson-extras come from the RobotCore aar's own libs/.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

SIM_DIR = Path(__file__).parent
JAVA_DIR = SIM_DIR / "java"
REPO_ROOT = SIM_DIR.parent.parent.parent
MAVEN = "https://repo1.maven.org/maven2"
SDK_ARTIFACTS = ("RobotCore", "Hardware")

# Packages whose classes user code may use in the simulator. Everything else in
# the SDK (vision, cameras, Lynx internals, networking, other vendors' drivers)
# is not simulated.
ALLOWED_PACKAGES = (
    "com/qualcomm/robotcore/hardware/",
    "com/qualcomm/robotcore/util/",
    "com/qualcomm/robotcore/exception/",
    "org/firstinspires/ftc/robotcore/external/",
    "org/firstinspires/ftc/robotcore/external/navigation/",
    "org/firstinspires/ftc/robotcore/external/function/",
    "org/firstinspires/ftc/robotcore/external/matrices/",
    "com/qualcomm/hardware/motors/",
)
ALLOWED_CLASSES = {
    "com/qualcomm/robotcore/eventloop/opmode/TeleOp",
    "com/qualcomm/robotcore/eventloop/opmode/Autonomous",
    "com/qualcomm/robotcore/eventloop/opmode/Disabled",
    "com/qualcomm/hardware/rev/RevHubOrientationOnRobot",
    "com/qualcomm/hardware/rev/RevImuOrientationOnRobot",
    "com/qualcomm/hardware/rev/RevTouchSensor",
    "com/qualcomm/robotcore/hardware/configuration/typecontainers/MotorConfigurationType",
    "com/qualcomm/robotcore/hardware/configuration/typecontainers/ServoConfigurationType",
    "com/qualcomm/robotcore/hardware/configuration/typecontainers/UserConfigurationType",
    "com/qualcomm/robotcore/hardware/configuration/typecontainers/InstantiableUserConfigurationType",
    "com/qualcomm/robotcore/robocol/TelemetryMessage",
}
# Real classes that reference Android in code paths the simulator never runs,
# verified to work on a plain JVM (tests/test_sim.py drives each of them).
VERIFIED_DESPITE_ANDROID = {
    "com/qualcomm/robotcore/hardware/HardwareMap",
    "com/qualcomm/robotcore/hardware/Gamepad",
    "com/qualcomm/robotcore/hardware/DcMotorImpl",
    "com/qualcomm/robotcore/hardware/DcMotorImplEx",
    "com/qualcomm/robotcore/hardware/ServoImpl",
    "com/qualcomm/robotcore/hardware/ServoImplEx",
    "com/qualcomm/robotcore/hardware/CRServoImpl",
    "com/qualcomm/robotcore/hardware/CRServoImplEx",
    "com/qualcomm/robotcore/hardware/DigitalChannelImpl",
    "com/qualcomm/robotcore/hardware/AnalogInput",
    "com/qualcomm/robotcore/hardware/QuaternionBasedImuHelper",
    "com/qualcomm/robotcore/util/LastKnown",
    "com/qualcomm/robotcore/util/SerialNumber",
    # readFile/writeFile are plain java.io; only the asset/resource readers need Android.
    "com/qualcomm/robotcore/util/ReadWriteFile",
    # toColor() needs android.graphics.Color, which the simulator supplies (shim/android/graphics).
    "com/qualcomm/robotcore/hardware/NormalizedRGBA",
    "org/firstinspires/ftc/robotcore/external/matrices/OpenGLMatrix",
    "org/firstinspires/ftc/robotcore/external/navigation/Orientation",
}
# Simulator internals and type-only stand-ins that user code must never compile against.
NEVER_IN_API = {
    "com/qualcomm/robotcore/eventloop/opmode/SimOpModeAccess",
    "android/content/Context",
    "android/app/Application",
    "android/opengl/Matrix",
    "android/graphics/Color",
    "com/qualcomm/robotcore/util/Device",
    "com/qualcomm/robotcore/hardware/configuration/ConfigurationTypeManager",
}
TRACE_CLASS = "org/pyftc/sim/Trace"
FORBIDDEN_METHODS = {
    ("java/lang/System", "nanoTime"),
    ("java/lang/System", "currentTimeMillis"),
    ("java/lang/Thread", "sleep"),
}


class BuildError(Exception):
    pass


@dataclass
class SimSdk:
    runtime_jar: Path
    api_jar: Path
    sdk_jars: list[Path]
    libs: list[Path]
    simulated: dict
    debug_jar: Path

    def runtime_classpath(self) -> list[Path]:
        return [self.runtime_jar, *self.sdk_jars, *self.libs]


# ----------------------------------------------------------------------------- class files


def parse_class(data: bytes) -> dict:
    """Constant-pool level view of a class file: its name, flags, and every class and
    method it references."""
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("not a class file")
    count = struct.unpack_from(">H", data, 8)[0]
    pos = 10
    utf8: dict[int, str] = {}
    classes: dict[int, int] = {}
    refs: list[tuple[int, int]] = []
    nat: dict[int, tuple[int, int]] = {}
    i = 1
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            n = struct.unpack_from(">H", data, pos)[0]
            utf8[i] = data[pos + 2:pos + 2 + n].decode("utf-8", "replace")
            pos += 2 + n
        elif tag in (3, 4):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag == 7:
            classes[i] = struct.unpack_from(">H", data, pos)[0]
            pos += 2
        elif tag in (8, 16, 19, 20):
            pos += 2
        elif tag in (9, 10, 11):
            c, nt = struct.unpack_from(">HH", data, pos)
            refs.append((c, nt))
            pos += 4
        elif tag == 12:
            nat[i] = struct.unpack_from(">HH", data, pos)
            pos += 4
        elif tag == 15:
            pos += 3
        elif tag in (17, 18):
            pos += 4
        else:
            raise ValueError(f"bad constant pool tag {tag}")
        i += 1
    flags, this_class, super_class, n_ifaces = struct.unpack_from(">HHHH", data, pos)
    supers = [utf8[classes[super_class]]] if super_class else []
    for k in range(n_ifaces):
        supers.append(utf8[classes[struct.unpack_from(">H", data, pos + 8 + 2 * k)[0]]])
    referenced = {utf8[v] for v in classes.values() if v in utf8}
    methods = set()
    for c, nt in refs:
        if c in classes and nt in nat:
            methods.add((utf8.get(classes[c], ""), utf8.get(nat[nt][0], "")))
    return {"name": utf8[classes[this_class]], "flags": flags, "classes": referenced, "methods": methods,
            "supers": supers}


def _is_plain_type(flags: int) -> bool:
    return bool(flags & (0x0200 | 0x2000 | 0x4000))  # interface, annotation, enum


# ----------------------------------------------------------------------------- inputs


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
    except OSError as e:
        raise BuildError(f"could not download {url}: {e}") from e
    tmp.replace(dest)


def sdk_jars(sdk: str, cache: Path) -> list[Path]:
    out = []
    for art in SDK_ARTIFACTS:
        candidates = [
            Path(os.environ["PYFTC_SIM_SDK_DIR"]) / f"{art}.jar" if os.environ.get("PYFTC_SIM_SDK_DIR") else None,
            REPO_ROOT / ".cache" / "javac" / f"sdk-{sdk}" / f"{art}.jar",
            cache / f"sdk-{sdk}" / f"{art}.jar",
        ]
        found = next((c for c in candidates if c and c.is_file()), None)
        if not found:
            found = cache / f"sdk-{sdk}" / f"{art}.jar"
            aar = cache / f"sdk-{sdk}" / f"{art}-{sdk}.aar"
            _download(f"{MAVEN}/org/firstinspires/ftc/{art}/{sdk}/{art}-{sdk}.aar", aar)
            with zipfile.ZipFile(aar) as z:
                found.write_bytes(z.read("classes.jar"))
            aar.unlink()
        out.append(found)
    return out


def bundled_libs(sdk: str, cache: Path) -> list[Path]:
    """The gson and gson-extras jars the RobotCore aar ships in libs/ (the SDK's
    ConfigurationTypeManager needs both). Taken from the same aar, so the exact
    versions the Robot Controller app runs with."""
    libs_dir = cache / f"sdk-{sdk}" / "libs"
    wanted = ("gson-2.8.0.jar", "gson-extras-0.2.1.jar")
    if all((libs_dir / w).is_file() for w in wanted):
        return [libs_dir / w for w in wanted]
    aar = REPO_ROOT / "sdkgen" / ".cache" / f"RobotCore-{sdk}.aar"
    downloaded = False
    if not aar.is_file():
        aar = cache / f"sdk-{sdk}" / f"RobotCore-{sdk}.aar"
        _download(f"{MAVEN}/org/firstinspires/ftc/RobotCore/{sdk}/RobotCore-{sdk}.aar", aar)
        downloaded = True
    libs_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(aar) as z:
        for w in wanted:
            try:
                (libs_dir / w).write_bytes(z.read(f"libs/{w}"))
            except KeyError as e:
                raise BuildError(f"RobotCore-{sdk}.aar has no libs/{w}; this SDK version needs a simulator update") from e
    if downloaded:
        aar.unlink()
    return [libs_dir / w for w in wanted]


def java_sources(debug: bool = False) -> list[Path]:
    """Simulator sources (compiled for Java 8 so user code built with --release 8 links
    against them), or with debug=True the debug adapter, which needs the JDK's jdk.jdi."""
    debug_dir = JAVA_DIR / "debug"
    return sorted(p for p in JAVA_DIR.rglob("*.java") if (debug_dir in p.parents) == debug)


def _hash_inputs(sdk: str, jars: list[Path]) -> str:
    h = hashlib.sha256()
    h.update(sdk.encode())
    for p in java_sources() + java_sources(debug=True):
        h.update(str(p.relative_to(JAVA_DIR)).encode())
        h.update(p.read_bytes())
    h.update(Path(__file__).read_bytes())
    for j in jars:
        h.update(j.name.encode())
        h.update(str(j.stat().st_size).encode())
    return h.hexdigest()[:16]


# ----------------------------------------------------------------------------- build


def find_javac(explicit: str | None = None) -> Path:
    for c in (explicit, os.environ.get("PYFTC_JAVAC")):
        if c and Path(c).is_file():
            return Path(c)
    java_home = os.environ.get("JAVA_HOME")
    if java_home and (Path(java_home) / "bin" / "javac").is_file():
        return Path(java_home) / "bin" / "javac"
    found = shutil.which("javac")
    if found:
        return Path(found)
    bundled = sorted((REPO_ROOT / ".cache" / "javac").glob("jdk-*/bin/javac"))
    if bundled:
        return bundled[-1]
    raise BuildError("no javac found: set revFtc.javaHome / JAVA_HOME, or put a JDK (17 or newer) on PATH")


def java_for(javac: Path) -> Path:
    java = javac.with_name("java.exe" if javac.suffix == ".exe" else "java")
    if not java.is_file():
        raise BuildError(f"{javac} has no java launcher next to it")
    return java


def build(cache: Path, javac: Path, sdk: str = "11.2.0") -> SimSdk:
    cache.mkdir(parents=True, exist_ok=True)
    jars = sdk_jars(sdk, cache)
    libs = bundled_libs(sdk, cache)
    key = _hash_inputs(sdk, jars + libs)
    out = cache / f"simsdk-{sdk}-{key}"
    runtime_jar, api_jar, sim_json = out / "runtime.jar", out / "api.jar", out / "simulated.json"
    debug_jar = out / "debug.jar"
    if runtime_jar.is_file() and api_jar.is_file() and sim_json.is_file() and debug_jar.is_file():
        return SimSdk(runtime_jar, api_jar, jars, libs, json.loads(sim_json.read_text()), debug_jar)

    work = Path(tempfile.mkdtemp(prefix="simsdk-", dir=cache))
    try:
        classes = work / "classes"
        classes.mkdir()
        cp = os.pathsep.join(str(p) for p in [*jars, *libs])
        srcs = [str(p) for p in java_sources()]
        argfile = work / "sources.txt"
        argfile.write_text("\n".join(f'"{s}"' for s in srcs))
        r = subprocess.run([str(javac), "--release", "8", "-g", "-nowarn", "-Xlint:-options", "-encoding", "UTF-8",
                            "-cp", cp, "-d", str(classes), f"@{argfile}"], capture_output=True, text=True)
        if r.returncode != 0:
            raise BuildError("compiling the simulator failed:\n" + r.stderr[-8000:])
        dclasses = work / "debug-classes"
        dclasses.mkdir()
        r = subprocess.run([str(javac), "-nowarn", "-encoding", "UTF-8", "-cp", os.pathsep.join(str(p) for p in libs),
                            "-d", str(dclasses), *[str(p) for p in java_sources(debug=True)]], capture_output=True, text=True)
        if r.returncode != 0:
            raise BuildError("compiling the simulator's debug adapter failed (it needs a full JDK with jdk.jdi):\n" + r.stderr[-4000:])
        _write_jar(debug_jar, dclasses)
        shim_names = {str(p.relative_to(JAVA_DIR / "shim"))[:-5] for p in (JAVA_DIR / "shim").rglob("*.java")}
        _write_jar(runtime_jar, classes)
        simulated = _write_api_jar(api_jar, classes, jars, shim_names)
        _sweep(java_for(javac), runtime_jar, jars + libs, simulated, work)
        # Re-write the API jar without anything the sweep rejected.
        _write_api_jar(api_jar, classes, jars, shim_names, simulated)
        sim_json.write_text(json.dumps(simulated, indent=1, sort_keys=True))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return SimSdk(runtime_jar, api_jar, jars, libs, simulated, debug_jar)


def _write_jar(dest: Path, classes: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(classes.rglob("*.class")):
            z.write(p, str(p.relative_to(classes)))
    tmp.replace(dest)


def _top(name: str) -> str:
    return name.split("$", 1)[0]


def _write_api_jar(dest: Path, classes: Path, jars: list[Path], shim_names: set[str],
                   previous: dict | None = None) -> dict:
    simulated: dict = {"classes": {}, "rejected": {}} if previous is None else previous
    entries: list[tuple[str, bytes]] = []
    written: set[str] = set()
    for p in sorted(classes.rglob("*.class")):
        rel = str(p.relative_to(classes))[:-6]
        if rel == TRACE_CLASS:
            # Only the sim-trace hooks the translator emits in simulator builds.
            entries.append((rel, p.read_bytes()))
            continue
        if _top(rel) in shim_names and _top(rel) not in NEVER_IN_API:
            entries.append((rel, p.read_bytes()))
            written.add(rel)
            if "$" not in rel:
                simulated["classes"][rel.replace("/", ".")] = "simulator stand-in (same API, simulated hardware)"
    candidates: dict[str, list[tuple[str, bytes]]] = {}
    everything: dict[str, list[tuple[str, bytes]]] = {}
    for jar in jars:
        with zipfile.ZipFile(jar) as src:
            for info in src.infolist():
                if not info.filename.endswith(".class"):
                    continue
                rel = info.filename[:-6]
                top = _top(rel)
                everything.setdefault(top, []).append((rel, src.read(info)))
    for top, files in everything.items():
        if any(r in written for r, _ in files) or top in shim_names or top in NEVER_IN_API:
            continue
        if top not in ALLOWED_CLASSES and top.rsplit("/", 1)[0] + "/" not in ALLOWED_PACKAGES:
            continue
        candidates[top] = files
    for top, files in sorted(candidates.items()):
        fqn = top.replace("/", ".")
        if fqn in simulated["rejected"]:
            continue
        main = next((d for r, d in files if r == top), None)
        if main is None:
            continue
        parsed = parse_class(main)
        reason = _reject_reason(top, parsed)
        if reason:
            simulated["rejected"][fqn] = reason
            continue
        if previous is None:
            simulated["classes"][fqn] = ("interface/enum/annotation (no behaviour)" if _is_plain_type(parsed["flags"])
                                         else "real SDK class")
        entries.extend(files)
    # javac needs the supertypes of every API class to look up inherited members
    # (Gamepad extends RobocolParsableBase, ...). They are included as they are.
    included = {r for r, _ in entries}
    pending = [parse_class(d)["supers"] for r, d in entries if "$" not in r]
    while pending:
        for sup in pending.pop():
            top = _top(sup)
            if sup in included or top.startswith("java/") or top in NEVER_IN_API:
                continue
            files = everything.get(top)
            if not files:
                continue
            for r, d in files:
                if r not in included:
                    entries.append((r, d))
                    included.add(r)
            main = next((d for r, d in files if r == top), None)
            if main is not None:
                pending.append(parse_class(main)["supers"])
                if previous is None:
                    simulated["classes"].setdefault(top.replace("/", "."), "supertype of an API class")
    tmp = dest.with_suffix(".part")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, data in entries:
            z.writestr(rel + ".class", data)
    tmp.replace(dest)
    return simulated


def _reject_reason(name: str, parsed: dict) -> str | None:
    if _is_plain_type(parsed["flags"]) or name in VERIFIED_DESPITE_ANDROID or name in ALLOWED_CLASSES:
        return None
    android = sorted(c for c in parsed["classes"] if c.startswith(("android/", "androidx/")) and not c.startswith("androidx/annotation"))
    if android:
        return "uses Android (" + ", ".join(android[:3]) + ")"
    wall = sorted(f"{c.split('/')[-1]}.{m}" for c, m in parsed["methods"] if (c, m) in FORBIDDEN_METHODS)
    if wall:
        return "reads the wall clock (" + ", ".join(wall) + "), which would not follow simulated time"
    return None


SWEEP = r"""
import java.util.*;
public class Sweep {
  public static void main(String[] a) throws Exception {
    java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
    String n; StringBuilder out = new StringBuilder();
    while ((n = r.readLine()) != null) {
      try { Class<?> c = Class.forName(n, true, Sweep.class.getClassLoader()); c.getDeclaredMethods(); c.getDeclaredFields(); }
      catch (Throwable t) { out.append(n).append('\t').append(t.toString().replace('\n', ' ')).append('\n'); }
    }
    System.out.print(out);
  }
}
"""


def _sweep(java: Path, runtime_jar: Path, jars: list[Path], simulated: dict, work: Path) -> None:
    """Load and initialise every API class in a real JVM on the runtime classpath;
    anything that fails is removed from the API."""
    src = work / "sweep"
    src.mkdir()
    (src / "Sweep.java").write_text(SWEEP)
    javac = java.with_name("javac.exe" if java.suffix == ".exe" else "javac")
    r = subprocess.run([str(javac), "-nowarn", "-d", str(src), str(src / "Sweep.java")], capture_output=True, text=True)
    if r.returncode != 0:
        raise BuildError("sweep compile failed: " + r.stderr)
    cp = os.pathsep.join(str(p) for p in [src, runtime_jar, *jars])
    names = "\n".join(simulated["classes"]) + "\n"
    r = subprocess.run([str(java), "-cp", cp, "Sweep"], input=names, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise BuildError("sweep failed: " + r.stderr[-4000:])
    for line in r.stdout.splitlines():
        if "\t" in line:
            fqn, err = line.split("\t", 1)
            simulated["classes"].pop(fqn, None)
            simulated["rejected"][fqn] = "does not load on a plain JVM: " + err[:300]
