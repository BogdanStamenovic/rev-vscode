from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from pyftc.starter import generate
from pyftc.translate import ProjectTranslator
from pyftc.typedb import TypeDB

FIXTURES = Path(__file__).parent / "fixtures"
SDK_DB = Path(__file__).resolve().parents[1] / "pyftc" / "data" / "sdk-11.2.0.json"
RCINFO = json.loads((FIXTURES / "rcInfo.json").read_text())

pytestmark = pytest.mark.skipif(not SDK_DB.exists(), reason="generated SDK database missing; run sdkgen")


@pytest.fixture(scope="module")
def sdk() -> TypeDB:
    return TypeDB(json.loads(SDK_DB.read_text()))


def build(sdk: TypeDB, config: str, tmp_path: Path) -> tuple[str, dict]:
    name = f"{config}Starter"
    src = generate(sdk, (FIXTURES / f"{config}.xml").read_text(), RCINFO, name)
    path = tmp_path / f"{name}.py"
    path.write_text(src)
    # a fresh DB: translation registers the user's classes into it
    result = ProjectTranslator(TypeDB(json.loads(SDK_DB.read_text()))).translate([path])
    return src, result


@pytest.mark.parametrize("config", ["Galerija", "Mixed", "Empty"])
def test_starter_translates_cleanly(sdk, config, tmp_path):
    src, r = build(sdk, config, tmp_path)
    assert r["ok"], r["diagnostics"]
    assert not r["diagnostics"], r["diagnostics"]
    assert "# ── Gamepad controls" in src
    assert "self.gamepad1" in src, "every starter pack must use the gamepad"
    assert "What a Gamepad can do" in src


@pytest.mark.skipif(not (os.environ.get("PYFTC_JAVAC") and os.environ.get("PYFTC_SDK_CLASSPATH")),
                    reason="PYFTC_JAVAC / PYFTC_SDK_CLASSPATH not set: starter Java was NOT compiled")
@pytest.mark.parametrize("config", ["Galerija", "Mixed", "Empty"])
def test_starter_compiles(sdk, config, tmp_path):
    _, r = build(sdk, config, tmp_path)
    files = []
    for f in r["files"]:
        p = tmp_path / f"{f['className']}.java"
        p.write_text(f["java"])
        files.append(str(p))
    res = subprocess.run([os.environ["PYFTC_JAVAC"], "-nowarn", "-Xlint:-options", "-source", "8", "-target", "8",
                          "-cp", os.environ["PYFTC_SDK_CLASSPATH"], "-d", str(tmp_path / "classes"), *files],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_galerija_controls(sdk, tmp_path):
    src, _ = build(sdk, "Galerija", tmp_path)
    assert 'Drive "Motor L" (left), "Motor D" (right)' in src
    assert "self.motor_d.setDirection(DcMotorSimple.Direction.REVERSE)" in src
    assert "self.motor_l.setPower(left_power)" in src
    assert '"Kombjan": gamepad 1: right trigger forward, left trigger reverse' in src
    assert "self.imu.initialize(IMU.Parameters(" in src


def test_mixed_controls(sdk, tmp_path):
    src, _ = build(sdk, "Mixed", tmp_path)
    assert "self.front_left.setPower(left_power)" in src and "self.back_right.setPower(right_power)" in src
    assert '"claw": gamepad 1: hold RB / hold LB to move it' in src
    assert "claw_position = 0.5" in src
    assert 'self.limit.isPressed()' in src
    assert "getDistance(DistanceUnit.CM)" in src


def test_no_drive_uses_sticks_for_motors(sdk, tmp_path):
    xml = (FIXTURES / "Galerija.xml").read_text().replace('"Motor L"', '"Arm"').replace('"Motor D"', '"Lift"')
    src = generate(sdk, xml, RCINFO, "NoDrive")
    assert "Drive " not in src.split("# ── Connected hardware")[0]
    assert '"Kombjan": gamepad 1: left stick up/down' in src
    assert '"Shooter 3": gamepad 1: right stick up/down' in src


def test_overflow_goes_to_gamepad2(sdk, tmp_path):
    motors = "".join(f'<RevRoboticsCoreHexMotor name="m{i}" port="{i % 4}" />' for i in range(12))
    xml = f'<Robot type="FirstInspires-FTC"><LynxUsbDevice name="p" serialNumber="(embedded)" parentModuleAddress="173"><LynxModule name="Control Hub" port="173">{motors}</LynxModule></LynxUsbDevice></Robot>'
    src = generate(sdk, xml, RCINFO, "Many")
    assert "gamepad 2" in src
    assert "self.gamepad2." in src
