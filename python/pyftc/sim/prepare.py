"""Everything the Java simulator process needs, from a workspace of Python OpModes.

1. Translate with the same translator that deploys to the robot, in its
   sim-trace mode (same Java plus same-line trace hooks; lineMap identical).
2. Compile with javac against the simulation SDK's API jar (only what the
   simulator supports). A compile error there, after the translator has already
   checked the code against the full SDK, means the code uses something the
   simulator does not simulate; it is reported on the Python line, naming it.
3. Write manifest.json: hardware configuration, OpMode classes, lineMaps.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..translate import ProjectTranslator
from ..typedb import TypeDB
from . import build as simbuild
from . import config as simconfig

SIM_DIR = Path(__file__).parent
CONSTANTS = SIM_DIR / "constants.json"
JAVAC_ERROR = re.compile(r"^(?P<file>.+?\.java):(?P<line>\d+): error: (?P<msg>.*)$")


def prepare(sources: list[Path], out_dir: Path, cache: Path, javac: Path, sdk: str = "11.2.0",
            config: dict[str, Any] | None = None, workspace: Path | None = None,
            trace: bool = True, db: TypeDB | None = None) -> dict[str, Any]:
    db = db or TypeDB.load(sdk)
    sdkbuild = simbuild.build(cache, javac, sdk)

    result = ProjectTranslator(db, sim_trace=trace).translate(sources, root=workspace)
    diagnostics = list(result["diagnostics"])
    if not result["ok"]:
        return {"ok": False, "stage": "translate", "diagnostics": diagnostics}

    if config is None:
        config = simconfig.find_in_workspace(db, workspace or _common_root(sources), sources)
    if config is None:
        config = {"name": "(none)", "source": "none", "hubs": [], "devices": []}
        diagnostics.append(_diag(str(sources[0]) if sources else "", 1,
                                 "No hardware configuration found (no hub, no configuration XML in the workspace, no starter pack): the simulator has no devices, so every hardwareMap.get() will fail.",
                                 "warning"))

    if out_dir.exists():
        shutil.rmtree(out_dir)
    classes_dir = out_dir / "classes"
    classes_dir.mkdir(parents=True)
    by_path: dict[str, dict[str, Any]] = {}
    for f in result["files"]:
        # One package per pack (docs/ARCHITECTURE.md Contract 3): write each
        # .java under its own hubPath-shaped subdirectory, not flattened into
        # one folder, or two packs' same-named helper class (e.g. `Cycle`)
        # would silently overwrite each other on disk before javac ever sees
        # the collision.
        p = out_dir / f["hubPath"].lstrip("/")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f["java"])
        by_path[str(p)] = f

    if by_path:
        argfile = out_dir / "sources.txt"
        argfile.write_text("\n".join(f'"{p}"' for p in by_path))
        r = subprocess.run([str(javac), "--release", "8", "-g", "-nowarn", "-Xlint:-options", "-encoding", "UTF-8",
                            "-Xmaxerrs", "200", "-cp", str(sdkbuild.api_jar), "-d", str(classes_dir), f"@{argfile}"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            compile_diags = map_javac_errors(r.stderr, by_path, sdkbuild.simulated)
            if not compile_diags:
                compile_diags = [_diag(str(sources[0]) if sources else "", 1, "javac failed:\n" + r.stderr[-3000:], "error")]
            return {"ok": False, "stage": "compile", "diagnostics": diagnostics + compile_diags}

    manifest = {
        "sdkVersion": sdk,
        "config": config,
        "classes": [{"className": f"{f['package']}.{f['className']}", "source": f["source"]} for f in result["files"]],
        "lineMaps": {f"{f['package']}.{f['className']}": {"source": f["source"], "lineMap": f["lineMap"]}
                     for f in result["files"]},
        "traceFiles": result.get("traceFiles", []),
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=1))
    classpath = [str(p) for p in [sdkbuild.runtime_jar, classes_dir, *sdkbuild.sdk_jars, *sdkbuild.libs]]
    return {
        "ok": True,
        "diagnostics": diagnostics,
        "java": str(simbuild.java_for(javac)),
        "classpath": classpath,
        "mainClass": "org.pyftc.sim.Main",
        "manifest": str(manifest_path),
        "constants": str(CONSTANTS),
        "classesDir": str(classes_dir),
        "debugClasspath": [str(sdkbuild.debug_jar), *[str(p) for p in sdkbuild.libs]],
        "config": {"name": config["name"], "source": config["source"], "devices": len(config["devices"])},
        "simulated": sorted(sdkbuild.simulated["classes"]),
    }


def java_command(prep: dict[str, Any], layout: Path | None = None, extra: list[str] | None = None) -> list[str]:
    cmd = [prep["java"], "-Xss4m", "-cp", os.pathsep.join(prep["classpath"]), prep["mainClass"],
           "--manifest", prep["manifest"], "--constants", prep["constants"]]
    if layout is not None:
        cmd += ["--layout", str(layout)]
    return cmd + (extra or [])


def _common_root(sources: list[Path]) -> Path:
    if not sources:
        return Path.cwd()
    return Path(os.path.commonpath([str(p.parent) for p in sources]))


def _diag(source: str, line: int, message: str, severity: str) -> dict[str, Any]:
    return {"source": source, "line": line, "col": 0, "endLine": line, "endCol": 200,
            "severity": severity, "message": message}


def map_javac_errors(stderr: str, by_path: dict[str, dict[str, Any]], simulated: dict) -> list[dict[str, Any]]:
    """javac errors from the simulation build, on the Python line, explaining that the
    construct is not simulated (the translator already accepted it for the robot)."""
    out: list[dict[str, Any]] = []
    lines = stderr.splitlines()
    seen: set[tuple[str, int, str]] = set()
    for i, ln in enumerate(lines):
        m = JAVAC_ERROR.match(ln)
        if not m:
            continue
        f = by_path.get(m.group("file"))
        if f is None:
            continue
        java_line = int(m.group("line"))
        lm = f["lineMap"]
        py_line = lm[java_line - 1] if 0 < java_line <= len(lm) and lm[java_line - 1] > 0 else 1
        detail = [m.group("msg")]
        for extra in lines[i + 1:i + 6]:
            if JAVAC_ERROR.match(extra):
                break
            s = extra.strip()
            if s.startswith(("symbol:", "location:", "class file for", "package ")):
                detail.append(s)
        message, name = _explain(detail, simulated)
        if not (0 < java_line <= len(lm) and lm[java_line - 1] > 0) and name:
            # Imports are synthetic lines; point at the first Python line that uses the name.
            py_line = _first_use(f["source"], name.rsplit(".", 1)[-1]) or py_line
        key = (f["source"], py_line, message)
        if key in seen:
            continue
        seen.add(key)
        out.append(_diag(f["source"], py_line, message, "error"))
    return out


def _first_use(source: str, simple: str) -> int | None:
    try:
        lines = Path(source).read_text().splitlines()
    except OSError:
        return None
    pat = re.compile(rf"\b{re.escape(simple)}\b")
    first_import = None
    for i, ln in enumerate(lines, 1):
        if pat.search(ln):
            if ln.lstrip().startswith(("from ", "import ")):
                first_import = first_import or i
                continue
            return i
    return first_import


def _explain(detail: list[str], simulated: dict) -> tuple[str, str | None]:
    text = " ".join(detail)
    name = None
    for pat in (r"class file for ([\w.$]+) not found", r"symbol:\s+class (\w+)", r"package ([\w.]+) does not exist",
                r"cannot access ([\w.$]+)", r"symbol:\s+method (\w+)", r"symbol:\s+variable (\w+)"):
        m = re.search(pat, text)
        if m:
            name = m.group(1)
            break
    if name:
        reason = ""
        for fqn, why in simulated.get("rejected", {}).items():
            if fqn == name or fqn.endswith("." + name):
                reason = f" ({why})"
                break
        return (f"The simulator does not support {name}{reason}. This code is fine for the robot, "
                f"but it cannot run in the simulator. [javac: {detail[0]}]"), name
    return "The simulator could not compile this line: " + text, None
