"""starter-update (docs/ARCHITECTURE.md Contract 3 + 4): every claim the
contract makes about never touching a line the user wrote, needs checking
against actual generated+updated text, not just "it returned something"."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from pyftc import markers
from pyftc.starter import generate
from pyftc.translate import ProjectTranslator
from pyftc.typedb import TypeDB
from pyftc.update import apply_update

FIXTURES = Path(__file__).parent / "fixtures"
SDK_DB = Path(__file__).resolve().parents[1] / "pyftc" / "data" / "sdk-11.2.0.json"
RCINFO = json.loads((FIXTURES / "rcInfo.json").read_text())

pytestmark = pytest.mark.skipif(not SDK_DB.exists(), reason="generated SDK database missing; run sdkgen")


@pytest.fixture(scope="module")
def sdk() -> TypeDB:
    return TypeDB(json.loads(SDK_DB.read_text()))


def fresh(sdk: TypeDB, config: str, name: str = "Robot") -> str:
    return generate(sdk, (FIXTURES / f"{config}.xml").read_text(), RCINFO, name)


def xml(config: str) -> str:
    return (FIXTURES / f"{config}.xml").read_text()


# ---------------------------------------------------------------------------
# No-op: fingerprint unchanged


def test_unchanged_config_is_a_noop(sdk):
    src = fresh(sdk, "Galerija")
    r = apply_update(sdk, src, xml("Galerija"), RCINFO)
    assert r["ok"] and r["applied"] and not r["changed"]
    assert r["python"] == src
    assert r["added"] == [] and r["removed"] == [] and r["hubsAdded"] == []


# ---------------------------------------------------------------------------
# Missing markers: refuse, hand back a fresh block, change nothing


# Indentation generate() actually uses for each region's markers (Contract 4:
# module level for imports/hardware, class body for devices, method body for
# init, while-loop body for loop).
REGION_INDENT = {"imports": "", "hardware": "", "devices": "    ", "init": "        ", "loop": "            "}


@pytest.mark.parametrize("region", markers.REGIONS)
def test_missing_marker_refuses_and_changes_nothing(sdk, region):
    src = fresh(sdk, "Galerija")
    begin_line = markers.render_begin(region, REGION_INDENT[region])
    assert begin_line in src, f"fixture doesn't contain the expected {region} marker line"
    broken = src.replace(begin_line, f"{REGION_INDENT[region]}# gone", 1)
    r = apply_update(sdk, broken, xml("Galerija"), RCINFO)
    assert r["ok"] is True
    assert r["applied"] is False
    assert "python" not in r and "manual" not in r
    assert "block" in r and isinstance(r["block"], str) and r["block"]
    assert r["added"] == [] and r["removed"] == [] and r["hubsAdded"] == []
    assert r["notes"] and region in r["notes"][0]


def test_duplicated_marker_refuses(sdk):
    src = fresh(sdk, "Galerija")
    broken = src.replace(markers.render_end("imports"), markers.render_end("imports") + "\n" +
                          markers.render_begin("imports") + "\n" + markers.render_end("imports"), 1)
    r = apply_update(sdk, broken, xml("Galerija"), RCINFO)
    assert r["applied"] is False
    assert "duplicat" in r["notes"][0]


# ---------------------------------------------------------------------------
# Insertion into each region + user edits survive verbatim


@pytest.fixture(scope="module")
def added_config() -> str:
    # Galerija.xml plus one new motor on the existing Control Hub, one new
    # servo on the existing Expansion Hub 2, and a brand new Expansion Hub 3
    # with its own motor - exercises "add to an existing hub" and "add a hub"
    # in the same update.
    src = xml("Galerija")
    src = src.replace(
        '<ControlHubImuBHI260AP name="imu" port="0" bus="0" />',
        '<ControlHubImuBHI260AP name="imu" port="0" bus="0" /><Servo name="claw" port="0" />',
    )
    src = src.replace(
        "</LynxUsbDevice>",
        '<LynxModule name="Expansion Hub 3" port="3">'
        '<RevRoboticsCoreHexMotor name="Arm" port="0" /></LynxModule></LynxUsbDevice>',
    )
    return src


@pytest.fixture
def updated(sdk, added_config):
    src = fresh(sdk, "Galerija")
    # Simulate a user having hand-edited generated code: a renamed local
    # variable's comment, changed DRIVE_POWER, and an extra statement they
    # added inside the loop marker right after Kombjan's control block.
    edited = src.replace("DRIVE_POWER: float = 1.0", "DRIVE_POWER: float = 0.5  # tuned down for testing")
    edited = edited.replace(
        'self.telemetry.addData("Kombjan", f"power {self.kombjan.getPower():.2f}")',
        'self.telemetry.addData("Kombjan", f"power {self.kombjan.getPower():.2f}")\n'
        '            self.telemetry.addData("hand-written line", "still here")',
    )
    r = apply_update(sdk, edited, added_config, RCINFO)
    assert r["ok"] and r["applied"], r
    return edited, r


def test_added_devices_and_hub_reported(updated):
    _, r = updated
    added_names = {d["name"] for d in r["added"]}
    assert added_names == {"claw", "Arm"}
    assert r["hubsAdded"] == [{"name": "Expansion Hub 3", "address": "3"}]
    assert r["removed"] == []


def test_insertion_into_imports_region(updated):
    _, r = updated
    pf = markers.parse(r["python"])
    assert any("Servo" in line for line in pf.body("imports"))


def test_insertion_into_hardware_region(updated):
    _, r = updated
    pf = markers.parse(r["python"])
    body = "\n".join(pf.body("hardware"))
    assert '"claw"' in body and '"Arm"' in body


def test_insertion_into_devices_region(updated):
    _, r = updated
    pf = markers.parse(r["python"])
    body = pf.body("devices")
    assert any(re.match(r"^\s*claw\s*:\s*Servo\s*$", line) for line in body)
    assert any(re.match(r"^\s*arm\s*:\s*DcMotor\s*$", line) for line in body)


def test_insertion_into_init_region(updated):
    _, r = updated
    pf = markers.parse(r["python"])
    body = "\n".join(pf.body("init"))
    assert 'self.claw = self.hardwareMap.get(Servo, "claw")' in body
    assert 'self.arm = self.hardwareMap.get(DcMotor, "Arm")' in body


def test_insertion_into_loop_region(updated):
    _, r = updated
    pf = markers.parse(r["python"])
    body = "\n".join(pf.body("loop"))
    assert "self.claw.setPosition" in body
    assert "self.arm.setPower" in body


def test_new_code_lands_immediately_before_end_marker(updated):
    # Non-blank tail: `loop`'s per-device blocks end with a blank separator
    # line by design (matches every other device block, see controls.py), so
    # the very last line can legitimately be blank - what matters is that the
    # last *non-blank* content above :end is part of what was just added, not
    # some pre-existing line the insertion should have landed after instead.
    _, r = updated
    lines = r["python"].splitlines()
    markers_for = {"imports": "Servo", "hardware": "Arm", "devices": "arm: DcMotor",
                   "init": 'self.arm = self.hardwareMap.get(DcMotor, "Arm")', "loop": "self.arm.setPower"}
    for region, needle in markers_for.items():
        pf = markers.parse(r["python"])
        end = pf.regions[region].end
        i = end - 1
        while i > pf.regions[region].begin and not lines[i].strip():
            i -= 1
        # a couple of lines' slack: some device blocks (e.g. the hardware
        # comment's ticks/RPM/gearing continuation) span more than one line,
        # so the very last non-blank line isn't always the one carrying the
        # device's name - it's still part of the same just-added block.
        tail = "\n".join(lines[max(pf.regions[region].begin, i - 2):i + 1])
        assert needle in tail, f"{region}: last non-blank lines above :end were {tail!r}"


def test_hand_edited_lines_survive_verbatim(updated):
    edited, r = updated
    assert "DRIVE_POWER: float = 0.5  # tuned down for testing" in r["python"]
    assert 'self.telemetry.addData("hand-written line", "still here")' in r["python"]
    # and every line that existed before the update is still present somewhere,
    # in original form (order-preserving: update only ever inserts, never edits)
    before_lines = [l for l in edited.splitlines() if 'pyftc:config' not in l]
    after_lines = r["python"].splitlines()
    j = 0
    for line in before_lines:
        while j < len(after_lines) and after_lines[j] != line:
            j += 1
        assert j < len(after_lines), f"line dropped by update: {line!r}"
        j += 1


def test_config_header_only_fingerprint_and_generated_change(updated):
    edited, r = updated
    before = markers.parse(edited)
    after = markers.parse(r["python"])
    assert after.config_name == before.config_name
    assert after.config_fingerprint != before.config_fingerprint
    assert after.config_fingerprint == r["fingerprint"]


def test_controls_avoid_already_used(updated):
    # Galerija's fresh pack already spends gamepad1's triggers (Kombjan) and
    # three button pairs (Shooter 3 / Shooter1 / Shooter2 - RB/LB, D-pad
    # up/down, D-pad right/left). Only Y/A and B/X are left on gamepad1
    # before IMU's fixed BACK; the two newly added devices must land there
    # and not reuse anything already spent.
    _, r = updated
    controls = {d["name"]: d["control"] for d in r["added"]}
    assert controls["claw"] == "gamepad 1: hold Y / hold A"
    assert controls["Arm"] == "gamepad 1: hold B forward, hold X reverse"
    for taken in ("right trigger", "RB", "LB", "D-pad up", "D-pad down", "D-pad right", "D-pad left"):
        assert taken not in controls["claw"] and taken not in controls["Arm"]


# ---------------------------------------------------------------------------
# Removed devices


def test_removed_device_is_flagged_not_deleted(sdk):
    src = fresh(sdk, "Galerija")
    config = xml("Galerija").replace(
        '<RevRoboticsUltraplanetaryHDHexMotor name="Shooter1" port="0" />', "",
    )
    r = apply_update(sdk, src, config, RCINFO)
    assert r["removed"] == [{"name": "Shooter1", "field": "shooter1"}]
    lines = r["python"].splitlines()
    idx = next(i for i, l in enumerate(lines) if re.match(r"^\s*shooter1\s*:\s*DcMotor\s*$", l))
    assert lines[idx - 1].strip() == "# pyftc: no longer in the configuration"
    # the field declaration itself is untouched
    assert "shooter1: DcMotor" in r["python"]
    # its hardwareMap lookup and loop control code are not deleted either
    assert 'self.hardwareMap.get(DcMotor, "Shooter1")' in r["python"]


def test_removed_device_flag_is_not_duplicated_on_repeated_update(sdk):
    src = fresh(sdk, "Galerija")
    config = xml("Galerija").replace(
        '<RevRoboticsUltraplanetaryHDHexMotor name="Shooter1" port="0" />', "",
    )
    r1 = apply_update(sdk, src, config, RCINFO)
    # Add an unrelated device on top of the still-missing Shooter1, forcing a second real update.
    config2 = config.replace(
        '<RevRoboticsCoreHexMotor name="Kombjan" port="0" />',
        '<RevRoboticsCoreHexMotor name="Kombjan" port="0" /><Servo name="claw2" port="1" />',
    )
    r2 = apply_update(sdk, r1["python"], config2, RCINFO)
    assert r2["python"].count("# pyftc: no longer in the configuration") == 1


# ---------------------------------------------------------------------------
# Overflow to gamepad2, from an update (not just a fresh generate)


def test_update_overflows_to_gamepad2(sdk):
    src = fresh(sdk, "Empty")
    motors = "".join(f'<RevRoboticsCoreHexMotor name="m{i}" port="{i % 4}" />' for i in range(12))
    config = (f'<Robot type="FirstInspires-FTC"><LynxUsbDevice name="p" serialNumber="(embedded)" '
              f'parentModuleAddress="173"><LynxModule name="Control Hub" port="173">{motors}'
              f'</LynxModule></LynxUsbDevice></Robot>')
    r = apply_update(sdk, src, config, RCINFO)
    assert r["applied"]
    assert len(r["added"]) == 12
    assert any("gamepad 2" in (d["control"] or "") for d in r["added"])
    assert "self.gamepad2." in r["python"]


def test_device_with_no_free_control_gets_a_note_not_a_theft(sdk):
    src = fresh(sdk, "Empty")
    # 7 controls per pad (2 sticks + triggers + 4 pairs... actually 2 stick + 1 trigger + 5 pairs = 8) x2 pads = 16 free slots.
    motors = "".join(f'<RevRoboticsCoreHexMotor name="m{i}" port="{i % 4}" />' for i in range(20))
    config = (f'<Robot type="FirstInspires-FTC"><LynxUsbDevice name="p" serialNumber="(embedded)" '
              f'parentModuleAddress="173"><LynxModule name="Control Hub" port="173">{motors}'
              f'</LynxModule></LynxUsbDevice></Robot>')
    r = apply_update(sdk, src, config, RCINFO)
    starved = [d for d in r["added"] if d["control"] == ""]
    assert starved, "expected at least one device to run out of free controls"
    assert any("no free" in n for n in r["notes"])


# ---------------------------------------------------------------------------
# The big one: starter pack, then updated starter pack, both compile


JAVAC = os.environ.get("PYFTC_JAVAC")
CLASSPATH = os.environ.get("PYFTC_SDK_CLASSPATH")
javac_only = pytest.mark.skipif(not (JAVAC and CLASSPATH),
                                reason="PYFTC_JAVAC / PYFTC_SDK_CLASSPATH not set (run scripts/javac-env.sh)")


def _translate_and_compile(sdk: TypeDB, source: str, class_name: str, tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    p = tmp_path / f"{class_name}.py"
    p.write_text(source)
    result = ProjectTranslator(TypeDB(json.loads(SDK_DB.read_text()))).translate([p])
    assert result["ok"] and not result["diagnostics"], result["diagnostics"]
    files = []
    for f in result["files"]:
        jp = tmp_path / f"{f['className']}.java"
        jp.write_text(f["java"])
        files.append(str(jp))
    res = subprocess.run([JAVAC, "-nowarn", "-Xlint:-options", "-source", "8", "-target", "8",
                          "-cp", CLASSPATH, "-d", str(tmp_path / "classes"), *files],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


@javac_only
def test_starter_then_updated_starter_both_compile(sdk, added_config, tmp_path):
    fresh_src = fresh(sdk, "Galerija", "Galerija")
    _translate_and_compile(sdk, fresh_src, "Galerija", tmp_path / "fresh")

    r = apply_update(sdk, fresh_src, added_config, RCINFO)
    assert r["applied"]
    _translate_and_compile(sdk, r["python"], "Galerija", tmp_path / "updated")


@javac_only
def test_empty_then_updated_with_new_hub_compiles(sdk, tmp_path):
    fresh_src = fresh(sdk, "Empty", "Bot")
    _translate_and_compile(sdk, fresh_src, "Bot", tmp_path / "fresh")

    config = ('<Robot type="FirstInspires-FTC"><LynxUsbDevice name="p" serialNumber="(embedded)" '
              'parentModuleAddress="173"><LynxModule name="Control Hub" port="173" />'
              '<LynxModule name="Expansion Hub 2" port="2">'
              '<RevRoboticsCoreHexMotor name="Left" port="0" />'
              '<RevRoboticsCoreHexMotor name="Right" port="1" />'
              '</LynxModule></LynxUsbDevice></Robot>')
    r = apply_update(sdk, fresh_src, config, RCINFO)
    assert r["applied"]
    assert r["hubsAdded"] == [{"name": "Expansion Hub 2", "address": "2"}]
    _translate_and_compile(sdk, r["python"], "Bot", tmp_path / "updated")
