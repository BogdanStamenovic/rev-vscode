"""Headless tests of the simulator: the translated Java runs in the Java sim process
with scripted Driver Station input; assertions are on the protocol stream
(docs/ARCHITECTURE.md, Contract 5).

Needs a JDK (javac + java); skipped loudly without one. `scripts/javac-env.sh`
fetches JDK 17. The first run builds the simulation SDK into .cache/sim.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from pyftc.sim import build as simbuild
from pyftc.sim import config as simconfig
from pyftc.sim.prepare import java_command, prepare
from pyftc.starter import generate
from pyftc.translate import ProjectTranslator
from pyftc.typedb import TypeDB

HERE = Path(__file__).parent
FIX = HERE / "fixtures"
CACHE = HERE.parent.parent / ".cache" / "sim"

try:
    JAVAC = simbuild.find_javac()
except simbuild.BuildError as e:  # pragma: no cover
    JAVAC = None
    WHY = str(e)

pytestmark = pytest.mark.skipif(JAVAC is None, reason="no JDK found: simulator NOT tested (run scripts/javac-env.sh)")


@pytest.fixture(scope="module")
def db() -> TypeDB:
    return TypeDB.load("11.2.0")


def run(db: TypeDB, tmp: Path, sources: dict[str, str], config: dict, script: list[dict], until: float,
        trace: bool = True, layout: dict | None = None) -> list[dict]:
    ws = tmp / "ws"
    ws.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, text in sources.items():
        p = ws / name
        p.write_text(text)
        paths.append(p)
    prep = prepare(paths, tmp / "build", CACHE, JAVAC, config=config, trace=trace, db=db)
    assert prep["ok"], json.dumps(prep["diagnostics"], indent=1)
    script_path = tmp / "script.jsonl"
    script_path.write_text("\n".join(json.dumps(c) for c in script))
    layout_path = None
    if layout is not None:
        layout_path = tmp / "layout.json"
        layout_path.write_text(json.dumps(layout))
    cmd = java_command(prep, layout_path, ["--fast", "--emit-ms", "20", "--script", str(script_path), "--until", str(until)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    msgs = [json.loads(line) for line in r.stdout.splitlines() if line.strip()]
    assert not [m for m in msgs if m["type"] == "fatal"], r.stderr[-3000:]
    return msgs


def states(msgs: list[dict]) -> list[dict]:
    return [m for m in msgs if m["type"] == "state"]


def at(msgs: list[dict], t: float) -> dict:
    """The last state at or before sim time t."""
    return [s for s in states(msgs) if s["t"] <= t + 1e-9][-1]


def events(msgs: list[dict], dev: str | None = None) -> list[dict]:
    out = [e for s in states(msgs) for e in s["events"]]
    return [e for e in out if dev is None or e["dev"] == dev]


def gp(t: float, index: int = 1, **state) -> dict:
    return {"type": "gamepad", "index": index, "gamepadType": "SONY_PS4", "state": state, "at": t}


def opmode(body: str, fields: str = "", imports: str = "") -> str:
    return f'''from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorSimple, Servo, CRServo, TouchSensor, DistanceSensor, IMU
from ftc.navigation import DistanceUnit, AngleUnit
{imports}

@TeleOp(name="T", group="test")
class T(LinearOpMode):
{fields or "    x: int = 0"}

    def runOpMode(self) -> None:
{body}
'''


MIXED = (FIX / "Mixed.xml").read_text()


# --------------------------------------------------------------------------- starter pack


def test_starter_pack_drive_servo_and_cr_servo(db, tmp_path):
    rcinfo = json.loads((FIX / "rcInfo.json").read_text())
    src = generate(db, MIXED, rcinfo, "MixedPack")
    cfg = simconfig.from_xml(db, MIXED, "Mixed", "file")
    script = [{"type": "init", "opMode": "Mixed Pack", "at": 0.1}, {"type": "start", "at": 0.5},
              gp(1.0, left_stick_y=-1.0), gp(2.0), gp(2.0, right_bumper=True), gp(2.5),
              gp(2.6, right_trigger=1.0), gp(3.0), {"type": "stop", "at": 3.2}]
    msgs = run(db, tmp_path, {"MixedPack.py": src}, cfg, script, 3.6)
    ready = next(m for m in msgs if m["type"] == "ready")
    assert [o["name"] for o in ready["opModes"]] == ["Mixed Pack"]

    s = at(msgs, 1.9)["devices"]
    drive = src.split("DRIVE_POWER: float = ")[1].split()[0]
    for name in ("frontLeft", "backLeft", "frontRight", "backRight"):
        assert s[name]["power"] == pytest.approx(float(drive), abs=1e-3), name
    # The right side is setDirection(REVERSE): same commanded power, opposite physical rotation.
    assert s["frontLeft"]["direction"] == "FORWARD" and s["frontRight"]["direction"] == "REVERSE"
    assert s["frontRight"]["reversed"] is True and s["frontLeft"]["reversed"] is False
    assert s["frontLeft"]["spin"] != s["frontRight"]["spin"]
    assert {s["frontLeft"]["spin"], s["frontRight"]["spin"]} == {"CW", "CCW"}
    # UltraPlanetary is a CW motor type: FORWARD + positive power turns it clockwise seen from the shaft.
    assert s["frontLeft"]["spin"] == "CW"
    assert s["frontLeft"]["rpm"] > 100

    # RB held for 0.5 s: claw steps +0.01 per loop from 0.5, clamped at 1.0.
    before = at(msgs, 1.99)["devices"]["claw"]["position"]
    after = at(msgs, 2.49)["devices"]["claw"]["position"]
    assert before == pytest.approx(0.5, abs=1e-6)
    assert 0.5 < after <= 1.0
    assert at(msgs, 2.49)["devices"]["wrist"]["position"] == pytest.approx(0.5, abs=1e-6)

    s = at(msgs, 2.95)["devices"]["intake"]
    assert s["kind"] == "crservo" and s["power"] == pytest.approx(0.8, abs=0.01) and s["spin"] != "stopped"

    # After STOP the SDK's DefaultOpMode zeroes every motor, then the hub failsafe disables them.
    end = at(msgs, 3.5)["devices"]
    assert end["frontLeft"]["power"] == 0 and end["frontLeft"]["enabled"] is False
    assert at(msgs, 3.5)["phase"] == "stopped"


def test_power_and_position_clip_like_the_sdk(db, tmp_path):
    body = '''        m = self.hardwareMap.get(DcMotor, "frontLeft")
        s = self.hardwareMap.get(Servo, "claw")
        self.waitForStart()
        m.setPower(1.7)
        s.setPosition(1.3)
        self.telemetry.addData("p", m.getPower())
        self.telemetry.addData("s", s.getPosition())
        self.telemetry.update()
        while self.opModeIsActive():
            self.idle()'''
    msgs = run(db, tmp_path, {"T.py": opmode(body)}, simconfig.from_xml(db, MIXED, "Mixed", "file"),
               [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}], 1.0)
    tel = [m for m in msgs if m["type"] == "telemetry"][-1]["lines"]
    assert tel == ["p : 1", "s : 1"]
    d = at(msgs, 0.9)["devices"]
    assert d["frontLeft"]["power"] == 1.0 and d["claw"]["position"] == 1.0
    assert d["claw"]["pwmUs"] == 2400  # default "Servo" PWM range 600..2400 us


# --------------------------------------------------------------------------- exceptions


def test_misspelled_device_name_maps_to_python_line(db, tmp_path):
    body = '''        self.waitForStart()
        motor = self.hardwareMap.get(DcMotor, "frontleft")
        motor.setPower(1)'''
    src = opmode(body)
    line = src.splitlines().index('        motor = self.hardwareMap.get(DcMotor, "frontleft")') + 1
    msgs = run(db, tmp_path, {"T.py": src}, simconfig.from_xml(db, MIXED, "Mixed", "file"),
               [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}], 1.0)
    exc = [m for m in msgs if m["type"] == "exception"]
    assert len(exc) == 1
    e = exc[0]
    assert e["exception"] == "java.lang.IllegalArgumentException"
    assert e["message"] == 'Unable to find a hardware device with name "frontleft" and type DcMotor'
    assert e["py"]["file"].endswith("T.py") and e["py"]["line"] == line
    assert '"frontLeft"' in e["hint"]
    assert e["driverHub"].startswith("java.lang.IllegalArgumentException: Unable to find")
    assert at(msgs, 0.9)["phase"] == "crashed"


def test_null_device_field_is_an_npe_on_the_right_line(db, tmp_path):
    fields = "    arm: DcMotor"
    body = '''        self.waitForStart()
        self.arm.setPower(0.5)'''
    src = opmode(body, fields)
    line = src.splitlines().index("        self.arm.setPower(0.5)") + 1
    msgs = run(db, tmp_path, {"T.py": src}, simconfig.from_xml(db, MIXED, "Mixed", "file"),
               [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}], 0.8)
    e = next(m for m in msgs if m["type"] == "exception")
    assert e["exception"] == "java.lang.NullPointerException" and e["py"]["line"] == line


# --------------------------------------------------------------------------- STOP handling


def test_loop_ignoring_stop_is_force_stopped_not_hung(db, tmp_path):
    body = '''        m = self.hardwareMap.get(DcMotor, "frontLeft")
        self.waitForStart()
        while True:
            m.setPower(0.5)
            m.setPower(0.4)'''
    src = opmode(body)
    loop_lines = {src.splitlines().index("            m.setPower(0.5)") + 1, src.splitlines().index("            m.setPower(0.4)") + 1}
    msgs = run(db, tmp_path, {"T.py": src}, simconfig.from_xml(db, MIXED, "Mixed", "file"),
               [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}, {"type": "stop", "at": 1.0}], 3.0)
    warn = [m for m in msgs if m["type"] == "warning" and m["code"] == "stuck-stop"]
    assert warn, [m for m in msgs if m["type"] == "warning"]
    assert "was able to be force stopped" in warn[0]["message"]
    assert warn[0]["py"]["line"] in loop_lines
    stopped = [s for s in states(msgs) if s["phase"] == "stopped"]
    assert stopped and 1.9 <= stopped[0]["t"] <= 2.1  # 900 ms + the stop-timeout window, in sim time
    assert at(msgs, 2.9)["devices"]["frontLeft"]["power"] == 0


def test_double_write_in_one_loop_is_reported(db, tmp_path):
    body = '''        m = self.hardwareMap.get(DcMotor, "frontLeft")
        self.waitForStart()
        while self.opModeIsActive():
            m.setPower(0.5)
            m.setPower(0.4)'''
    msgs = run(db, tmp_path, {"T.py": opmode(body)}, simconfig.from_xml(db, MIXED, "Mixed", "file"),
               [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}], 1.0)
    w = [m for m in msgs if m["type"] == "warning" and m["code"] == "double-write"]
    assert w and w[0]["device"] == "frontLeft" and "0.50" in w[0]["message"] and "0.40" in w[0]["message"]


# --------------------------------------------------------------------------- acceptance: the team's OpMode


def test_fgc_main_magdump_cycle(db, tmp_path):
    """Copy of FGC_2026_Korea/code/main.py (the team's real OpMode). MagDump: cross
    cycles phase 0 -> 1 (shooter spins up) -> 2 (collector reversed at 1) -> 0 (both off),
    with a 500 ms debounce."""
    if not (FIX / "sim" / "fgc_main.py").exists():
        # The team's competition code stays out of this public repo; the
        # fixture exists only on machines that have it.
        pytest.skip("team OpMode copy not present (kept out of the public repo)")
    cfg = simconfig.from_starter(db, (FIX / "sim" / "fgc_starter.txt").read_text())
    press = lambda t: [gp(t, a=True), gp(t + 0.1)]  # noqa: E731
    script = [{"type": "init", "opMode": "Main", "at": 0.1}, {"type": "start", "at": 1.0},
              *press(1.5), *press(3.0), *press(3.2), *press(4.0), *press(5.0), {"type": "stop", "at": 6.0}]
    main_src = (FIX / "sim" / "fgc_main.py").read_text()
    msgs = run(db, tmp_path, {"main.py": main_src}, cfg, script, 6.4)
    # The team edits this file; read the spin-up power from the copy instead of assuming it.
    spin_up = float(re.search(r"MagDump==1 and .*\n\s*self\.shooter\.setPower\(([-\d.]+)\)", main_src).group(1))

    def phase(t):
        tr = [m for m in msgs if m["type"] == "trace" and m["t"] <= t][-1]
        return tr["fields"]["cycle_register"]["@entries"]["MagDump"]["phase"]

    def power(t, name):
        return at(msgs, t)["devices"][name]["power"]

    # Finding: the press 0.5 s after START is ignored. register_cyclePhase stores
    # last_ms = timer.milliseconds() (time since INIT, 900 ms here), then timer.reset(),
    # so no phase can change until INIT time + 500 ms has passed after START.
    tr = [m for m in msgs if m["type"] == "trace" and m["t"] >= 1.05][0]
    assert tr["fields"]["cycle_register"]["@entries"]["MagDump"]["last_ms"] == pytest.approx(900.0, abs=1)
    assert phase(1.9) == 0 and power(1.9, "shooter") == 0

    assert phase(3.09) == 1 and power(3.09, "shooter") == pytest.approx(spin_up, abs=1e-4)
    assert phase(3.39) == 1  # 3.2 press is inside the 500 ms debounce
    assert phase(4.09) == 2
    col = at(msgs, 4.2)["devices"]["Collector"]
    assert col["direction"] == "REVERSE" and col["power"] == pytest.approx(1.0) and col["spin"] != "stopped"
    assert power(4.2, "shooter") == pytest.approx(spin_up, abs=1e-4)
    assert phase(5.09) == 0 and power(5.09, "shooter") == 0 and power(5.09, "Collector") == 0

    shots = [e for e in events(msgs, "Collector") if e["op"] == "setPower"]
    assert shots[0]["v"] == pytest.approx(1.0) and shots[0]["hub"] == pytest.approx(-1.0)
    assert shots[0]["py"]["line"] == (FIX / "sim" / "fgc_main.py").read_text().splitlines().index(
        '                self.shooter_intake().setPower(1)') + 1


# --------------------------------------------------------------------------- trace instrumentation


def test_trace_build_behaves_exactly_like_the_plain_build(db, tmp_path):
    rcinfo = json.loads((FIX / "rcInfo.json").read_text())
    src = generate(db, MIXED, rcinfo, "MixedPack")
    cfg = simconfig.from_xml(db, MIXED, "Mixed", "file")
    script = [{"type": "init", "opMode": "Mixed Pack", "at": 0.1}, {"type": "start", "at": 0.5},
              gp(0.7, left_stick_y=-0.6, right_stick_x=0.3), gp(1.2, right_bumper=True), gp(1.6), {"type": "stop", "at": 2.0}]
    a = run(db, tmp_path / "a", {"MixedPack.py": src}, cfg, script, 2.4, trace=True)
    b = run(db, tmp_path / "b", {"MixedPack.py": src}, cfg, script, 2.4, trace=False)
    def strip(ms: list[dict], root: Path) -> str:
        # The two runs live in different directories; everything else must match exactly.
        return json.dumps([m for m in ms if m["type"] not in ("trace", "ready")]).replace(str(root), "<ws>")
    assert strip(a, tmp_path / "a") == strip(b, tmp_path / "b")
    traced = [m for m in a if m["type"] == "trace" and m["t"] > 1.3][0]
    lines = traced["lines"][next(iter(traced["lines"]))]
    claw_up = src.splitlines().index("                claw_position = min(claw_position + self.SERVO_STEP, 1.0)") + 1
    assert claw_up in lines
    assert any(c["name"] == "claw_position" for c in traced["changed"])


def test_plain_translation_has_no_trace_hooks(db, tmp_path):
    p = tmp_path / "T.py"
    p.write_text(opmode("        self.waitForStart()\n        x = 1"))
    out = ProjectTranslator(db).translate([p])
    assert "org.pyftc.sim" not in out["files"][0]["java"] and "traceFiles" not in out
    traced = ProjectTranslator(TypeDB.load("11.2.0"), sim_trace=True).translate([p])
    assert traced["files"][0]["lineMap"] == out["files"][0]["lineMap"]


# --------------------------------------------------------------------------- config, sensors, IMU


def test_config_from_starter_markers(db):
    cfg = simconfig.from_starter(db, (FIX / "sim" / "fgc_starter.txt").read_text())
    assert cfg["name"] == "FGC2026-Incheon"
    assert [(h["name"], h["address"], h["kind"]) for h in cfg["hubs"]] == [
        ("Expansion Hub 2", 2, "ExpansionHub"), ("Control Hub", 173, "ControlHub")]
    by = {d["name"]: d for d in cfg["devices"]}
    assert len(by) == 13
    assert (by["Fishing"]["tag"], by["Fishing"]["hub"], by["Fishing"]["port"]) == ("RevRoboticsCoreHexMotor", "Expansion Hub 2", "3")
    assert by["ShooterIntake"]["tag"] == "ContinuousRotationServo"
    assert (by["imu"]["tag"], by["imu"]["bus"]) == ("ControlHubImuBHI260AP", "0")


def test_unsupported_class_fails_at_compile_naming_it(db, tmp_path):
    src = opmode('''        hubs = self.hardwareMap.getAll(LynxModule)
        self.waitForStart()''', imports="from ftc.hardware import LynxModule")
    line = src.splitlines().index("        hubs = self.hardwareMap.getAll(LynxModule)") + 1
    p = tmp_path / "T.py"
    p.write_text(src)
    r = prepare([p], tmp_path / "build", CACHE, JAVAC, config=simconfig.from_xml(db, MIXED, "Mixed", "file"), db=db)
    assert not r["ok"] and r["stage"] == "compile"
    d = r["diagnostics"][0]
    assert d["line"] == line and "does not support" in d["message"] and "LynxModule" in d["message"]


def test_touch_and_distance_sensors(db, tmp_path):
    body = '''        t = self.hardwareMap.get(TouchSensor, "limit")
        d = self.hardwareMap.get(DistanceSensor, "range")
        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("pressed", t.isPressed())
            self.telemetry.addData("cm", d.getDistance(DistanceUnit.CM))
            self.telemetry.update()'''
    script = [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.2},
              {"type": "sensor", "device": "range", "value": {"mm": 412}, "at": 0.2},
              {"type": "sensor", "device": "limit", "value": {"pressed": True}, "at": 1.0},
              {"type": "sensor", "device": "range", "value": {"mm": None}, "at": 1.0}]
    msgs = run(db, tmp_path, {"T.py": opmode(body)}, simconfig.from_xml(db, MIXED, "Mixed", "file"), script, 1.8)
    tel = [m for m in msgs if m["type"] == "telemetry"]
    early = [m["lines"] for m in tel if 0.3 < m["t"] < 0.95][-1]
    late = [m["lines"] for m in tel if m["t"] > 1.3][-1]
    assert early == ["pressed : false", "cm : 41.2"]
    assert late[0] == "pressed : true"
    assert late[1] == "cm : 819"  # nothing in range: the placeholder chip reading (constants.json)


def test_imu_yaw_follows_the_hub_pose(db, tmp_path):
    body = '''        imu = self.hardwareMap.get(IMU, "imu")
        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("yaw", round(imu.getRobotYawPitchRollAngles().getYaw(AngleUnit.DEGREES)))
            self.telemetry.update()'''
    turned = {"version": 1, "hubs": {"Control Hub": {"position": [0, 0, 0], "rotation": [0, 90, 0]}}}
    script = [{"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.2},
              {"type": "layout", "layout": turned, "at": 0.8}]
    msgs = run(db, tmp_path, {"T.py": opmode(body)}, simconfig.from_xml(db, MIXED, "Mixed", "file"), script, 1.6)
    tel = [m for m in msgs if m["type"] == "telemetry"]
    assert [m["lines"] for m in tel if m["t"] < 0.75][-1] == ["yaw : 0"]
    # Turning the hub 90 degrees counter-clockwise seen from above = yaw +90 (FTC convention).
    assert [m["lines"] for m in tel if m["t"] > 1.2][-1] == ["yaw : 90"]


def test_busy_loop_without_sdk_calls_restarts_like_the_robot_controller(db, tmp_path):
    body = '''        self.waitForStart()
        while True:
            self.x = self.x + 1'''
    src = opmode(body)
    loop_line = src.splitlines().index("            self.x = self.x + 1") + 1
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "T.py").write_text(src)
    prep = prepare([ws / "T.py"], tmp_path / "build", CACHE, JAVAC, config=simconfig.from_xml(db, MIXED, "Mixed", "file"), db=db)
    assert prep["ok"]
    script = tmp_path / "s.jsonl"
    script.write_text("\n".join(json.dumps(c) for c in [
        {"type": "init", "opMode": "T", "at": 0.1}, {"type": "start", "at": 0.3}, {"type": "stop", "at": 1.0}]))
    r = subprocess.run(java_command(prep, None, ["--fast", "--script", str(script), "--until", "5"]),
                       capture_output=True, text=True, timeout=120)
    msgs = [json.loads(line) for line in r.stdout.splitlines() if line.strip()]
    stuck = [m for m in msgs if m["type"] == "warning" and m["code"] == "stuck-stop"]
    assert stuck and "stuck in stop(). Restarting robot controller app." in stuck[0]["message"]
    assert stuck[0]["py"]["line"] == loop_line
    fatal = [m for m in msgs if m["type"] == "fatal"]
    assert fatal and fatal[0]["restart"] is True and r.returncode == 3


# --------------------------------------------------------------------------- debugger


class Dap:
    """Minimal DAP client over the adapter's stdio."""

    def __init__(self, cmd: list[str]):
        import queue
        import threading
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.q: queue.Queue = queue.Queue()
        self.seq = 1
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self) -> None:
        f = self.p.stdout
        while True:
            header = b""
            while not header.endswith(b"\r\n\r\n"):
                c = f.read(1)
                if not c:
                    return
                header += c
            n = int([h for h in header.decode().split("\r\n") if h.lower().startswith("content-length")][0].split(":")[1])
            self.q.put(json.loads(f.read(n)))

    def request(self, command: str, **arguments) -> dict:
        seq = self.seq
        self.seq += 1
        body = json.dumps({"seq": seq, "type": "request", "command": command, "arguments": arguments}).encode()
        self.p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(body) + body)
        self.p.stdin.flush()
        return self.wait(lambda m: m.get("type") == "response" and m.get("request_seq") == seq)

    def wait(self, pred, timeout: float = 30) -> dict:
        import time
        end = time.time() + timeout
        seen = []
        while time.time() < end:
            try:
                m = self.q.get(timeout=0.5)
            except Exception:  # noqa: BLE001 - queue.Empty
                continue
            seen.append(m)
            if pred(m):
                return m
        raise AssertionError(f"timed out; saw {seen[-5:]}")


def test_debugger_breakpoint_step_and_variables_in_python_terms(db, tmp_path):
    import socket
    import threading
    body = '''        m = self.hardwareMap.get(DcMotor, "frontLeft")
        self.waitForStart()
        while self.opModeIsActive():
            speed = -self.gamepad1.left_stick_y * 0.5
            self.x = self.x + 1
            m.setPower(speed)'''
    src = opmode(body)
    lines = src.splitlines()
    bp = lines.index("            speed = -self.gamepad1.left_stick_y * 0.5") + 1
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "T.py").write_text(src)
    prep = prepare([ws / "T.py"], tmp_path / "build", CACHE, JAVAC, config=simconfig.from_xml(db, MIXED, "Mixed", "file"), db=db)
    assert prep["ok"]
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    cmd = java_command(prep)
    cmd.insert(1, f"-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=127.0.0.1:{port},quiet=y")
    sim = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    states_seen: list[dict] = []
    threading.Thread(target=lambda: [states_seen.append(json.loads(ln)) for ln in sim.stdout], daemon=True).start()

    def sim_send(cmd_obj: dict) -> None:
        sim.stdin.write(json.dumps(cmd_obj) + "\n")
        sim.stdin.flush()

    import time
    for _ in range(100):
        if any(m["type"] == "ready" for m in list(states_seen)):
            break
        time.sleep(0.1)
    dap = Dap([prep["java"], "-cp", ":".join(prep["debugClasspath"]), "org.pyftc.sim.debug.DapServer",
               "--port", str(port), "--manifest", prep["manifest"]])
    try:
        assert dap.request("initialize", adapterID="revftc-sim")["success"]
        assert dap.request("attach")["success"]
        r = dap.request("setBreakpoints", source={"path": str(ws / "T.py")}, breakpoints=[{"line": bp}])
        bp_id = r["body"]["breakpoints"][0]["id"]
        dap.request("configurationDone")
        sim_send({"type": "gamepad", "index": 1, "gamepadType": "SONY_PS4", "state": {"left_stick_y": -1.0}})
        sim_send({"type": "init", "opMode": "T"})
        # The class is prepared when INIT constructs the OpMode; the breakpoint is confirmed then.
        if not r["body"]["breakpoints"][0]["verified"]:
            changed = dap.wait(lambda m: m.get("event") == "breakpoint")
            assert changed["body"]["breakpoint"] == {"id": bp_id, "verified": True, "line": bp}
        time.sleep(0.5)
        sim_send({"type": "start"})
        stop = dap.wait(lambda m: m.get("event") == "stopped")
        assert stop["body"]["reason"] == "breakpoint"
        frames = dap.request("stackTrace", threadId=stop["body"]["threadId"])["body"]["stackFrames"]
        assert frames[0]["line"] == bp and frames[0]["source"]["path"].endswith("T.py")
        assert frames[0]["name"] == "T.runOpMode"

        # Sim time is frozen while stopped: the motor state does not advance.
        time.sleep(0.3)
        held = [m for m in list(states_seen) if m["type"] == "state"][-1]
        time.sleep(0.5)
        later = [m for m in list(states_seen) if m["type"] == "state"][-1]
        assert held["debuggerHold"] is True and later["t"] == held["t"]

        dap.request("next", threadId=stop["body"]["threadId"])
        stop2 = dap.wait(lambda m: m.get("event") == "stopped")
        frames = dap.request("stackTrace", threadId=stop2["body"]["threadId"])["body"]["stackFrames"]
        assert frames[0]["line"] == bp + 1  # one Python line, however many Java lines it became
        scopes = dap.request("scopes", frameId=frames[0]["id"])["body"]["scopes"]
        local_vars = dap.request("variables", variablesReference=scopes[0]["variablesReference"])["body"]["variables"]
        speed = next(v for v in local_vars if v["name"] == "speed")
        assert speed["value"] == "0.5" and speed["type"] == "float"
        fields = dap.request("variables", variablesReference=scopes[1]["variablesReference"])["body"]["variables"]
        assert [f["name"] for f in fields] == ["x"]
        ev = dap.request("evaluate", expression="self.x", frameId=frames[0]["id"])
        assert ev["body"]["result"] == "0"
        dap.request("setBreakpoints", source={"path": str(ws / "T.py")}, breakpoints=[])
        dap.request("continue", threadId=stop2["body"]["threadId"])
        time.sleep(1.0)
        after = [m for m in list(states_seen) if m["type"] == "state"][-1]
        assert after["debuggerHold"] is False and after["t"] > later["t"]
        assert after["devices"]["frontLeft"]["power"] == pytest.approx(0.5, abs=1e-4)  # hub power is quantised to 1/32767
        dap.request("disconnect")
    finally:
        dap.p.kill()
        sim.kill()


def test_architecture_doc_tables_are_current():
    from pyftc.sim import docgen
    assert docgen.main(["--cache", str(CACHE), "--check"]) == 0, "run: python -m pyftc.sim.docgen"
