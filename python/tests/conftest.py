"""A tiny hand-written slice of the SDK type database, so translator tests do
not depend on the generated one (and pin down exactly what they rely on)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pyftc.translate import ProjectTranslator  # noqa: E402
from pyftc.typedb import TypeDB  # noqa: E402

HW = "com.qualcomm.robotcore.hardware"
OM = "com.qualcomm.robotcore.eventloop.opmode"
EXT = "org.firstinspires.ftc.robotcore.external"


def m(name: str, params: list[tuple[str, str]] = (), returns: str = "void", static: bool = False,
      type_params: list[str] | None = None, abstract: bool = False) -> dict[str, Any]:
    return {"name": name, "static": static, "abstract": abstract, "typeParams": type_params or [],
            "params": [{"name": n, "type": t, "varargs": t.endswith("...")} for n, t in params],
            "returns": returns, "doc": f"Doc for {name}."}


def c(fqn: str, kind: str = "class", module: str | None = None, extends: list[str] = (), methods: list = (),
      fields: list = (), enum: list[str] = (), outer: str | None = None, type_params: list[str] = (),
      ctors: list = ()) -> tuple[str, dict[str, Any]]:
    return fqn, {"kind": kind, "simpleName": fqn.rsplit(".", 1)[-1], "outer": outer, "module": module,
                 "typeParams": list(type_params), "extends": list(extends), "abstract": False,
                 "methods": list(methods), "fields": list(fields), "enumConstants": list(enum), "doc": "",
                 "constructors": [{"params": [{"name": n, "type": t, "varargs": False} for n, t in k], "doc": ""}
                                  for k in ctors]}


def f(name: str, type_: str, static: bool = False) -> dict[str, Any]:
    return {"name": name, "type": type_, "static": static, "final": static, "doc": ""}


FIXTURE = {
    "sdkVersion": "test",
    "classes": dict([
        c(f"{OM}.OpMode", module="ftc.opmode", fields=[
            f("hardwareMap", f"{HW}.HardwareMap"), f("telemetry", f"{EXT}.Telemetry"),
            f("gamepad1", f"{HW}.Gamepad"), f("gamepad2", f"{HW}.Gamepad")],
          methods=[m("getRuntime", returns="double"), m("resetRuntime")]),
        c(f"{OM}.LinearOpMode", module="ftc.opmode", extends=[f"{OM}.OpMode"], methods=[
            m("runOpMode", abstract=True), m("waitForStart"), m("opModeIsActive", returns="boolean"),
            m("isStopRequested", returns="boolean"), m("sleep", [("milliseconds", "long")]), m("idle")]),
        c(f"{OM}.TeleOp", kind="annotation", module="ftc.opmode"),
        c(f"{OM}.Autonomous", kind="annotation", module="ftc.opmode"),
        c(f"{OM}.Disabled", kind="annotation", module="ftc.opmode"),
        c(f"{HW}.HardwareDevice", kind="interface", module="ftc.hardware", methods=[
            m("getDeviceName", returns="java.lang.String"), m("getVersion", returns="int")]),
        c(f"{HW}.DcMotorSimple", kind="interface", module="ftc.hardware", extends=[f"{HW}.HardwareDevice"], methods=[
            m("setPower", [("power", "double")]), m("getPower", returns="double"),
            m("setDirection", [("direction", f"{HW}.DcMotorSimple.Direction")])]),
        c(f"{HW}.DcMotorSimple.Direction", kind="enum", outer=f"{HW}.DcMotorSimple", enum=["FORWARD", "REVERSE"]),
        c(f"{HW}.DcMotor", kind="interface", module="ftc.hardware", extends=[f"{HW}.DcMotorSimple"], methods=[
            m("getCurrentPosition", returns="int"), m("setTargetPosition", [("position", "int")]),
            m("setMode", [("mode", f"{HW}.DcMotor.RunMode")]),
            m("setZeroPowerBehavior", [("zeroPowerBehavior", f"{HW}.DcMotor.ZeroPowerBehavior")])]),
        c(f"{HW}.DcMotor.RunMode", kind="enum", outer=f"{HW}.DcMotor",
          enum=["RUN_WITHOUT_ENCODER", "RUN_USING_ENCODER", "RUN_TO_POSITION", "STOP_AND_RESET_ENCODER"]),
        c(f"{HW}.DcMotor.ZeroPowerBehavior", kind="enum", outer=f"{HW}.DcMotor", enum=["BRAKE", "FLOAT"]),
        c(f"{HW}.Servo", kind="interface", module="ftc.hardware", extends=[f"{HW}.HardwareDevice"], methods=[
            m("setPosition", [("position", "double")]), m("getPosition", returns="double")],
          fields=[f("MAX_POSITION", "double", static=True)]),
        c(f"{HW}.HardwareMap", module="ftc.hardware", fields=[
            f("dcMotor", f"{HW}.HardwareMap.DeviceMapping<{HW}.DcMotor>")], methods=[
            m("get", [("classOrInterface", "java.lang.Class<T>"), ("deviceName", "java.lang.String")], "T",
              type_params=[f"T extends {HW}.HardwareDevice"])]),
        c(f"{HW}.HardwareMap.DeviceMapping", outer=f"{HW}.HardwareMap", type_params=["DEVICE_TYPE extends HardwareDevice"],
          methods=[m("get", [("deviceName", "java.lang.String")], "DEVICE_TYPE")]),
        c(f"{HW}.Gamepad", module="ftc.hardware", fields=[
            f("left_stick_x", "float"), f("left_stick_y", "float"), f("right_stick_x", "float"),
            f("a", "boolean"), f("b", "boolean"), f("right_trigger", "float")],
          methods=[m("rumble", [("durationMs", "int")])]),
        c(f"{EXT}.Telemetry", kind="interface", module="ftc.telemetry", methods=[
            m("addData", [("caption", "java.lang.String"), ("value", "java.lang.Object")], f"{EXT}.Telemetry.Item"),
            m("addData", [("caption", "java.lang.String"), ("format", "java.lang.String"), ("args", "java.lang.Object...")],
              f"{EXT}.Telemetry.Item"),
            m("addLine", [("lineCaption", "java.lang.String")], f"{EXT}.Telemetry.Line"),
            m("update", returns="boolean")]),
        c(f"{EXT}.Telemetry.Item", kind="interface", outer=f"{EXT}.Telemetry"),
        c(f"{EXT}.Telemetry.Line", kind="interface", outer=f"{EXT}.Telemetry"),
        c("com.qualcomm.robotcore.util.ElapsedTime", module="ftc.util", ctors=[[]], methods=[
            m("seconds", returns="double"), m("milliseconds", returns="double"), m("reset")]),
        c("com.qualcomm.robotcore.util.Range", module="ftc.util", methods=[
            m("clip", [("number", "double"), ("min", "double"), ("max", "double")], "double", static=True),
            m("clip", [("number", "int"), ("min", "int"), ("max", "int")], "int", static=True)]),
        c(f"{HW}.IMU", kind="interface", module="ftc.hardware", extends=[f"{HW}.HardwareDevice"], methods=[
            m("resetYaw")]),
    ]),
    "xmlTags": {
        "RevRoboticsCoreHexMotor": {"javaType": f"{HW}.DcMotor", "implClass": None, "category": "motor",
                                    "displayName": "REV Robotics Core Hex Motor",
                                    "props": {"ticksPerRev": 288, "maxRPM": 125, "gearing": 72}},
        "RevRoboticsUltraplanetaryHDHexMotor": {"javaType": f"{HW}.DcMotor", "implClass": None, "category": "motor",
                                                "displayName": "REV Robotics Ultraplanetary HD Hex Motor",
                                                "props": {"ticksPerRev": 28, "maxRPM": 6000, "gearing": 1}},
        "ControlHubImuBHI260AP": {"javaType": f"{HW}.IMU", "implClass": None, "category": "imu",
                                  "displayName": "REV internal BHI260AP IMU", "props": {}},
    },
}


@pytest.fixture(params=["fixture", "sdk"])
def db(request) -> TypeDB:
    """Every translator test runs against the hand-written slice and the
    generated SDK database, so the tests pin behaviour and also prove the real
    database carries what they rely on."""
    import copy
    if request.param == "sdk":
        path = Path(__file__).resolve().parents[1] / "pyftc" / "data" / "sdk-11.2.0.json"
        if not path.exists():
            pytest.skip("generated SDK database missing; run sdkgen")
        return TypeDB(json.loads(path.read_text()))
    return TypeDB(copy.deepcopy(FIXTURE))


@pytest.fixture
def translate(db: TypeDB, tmp_path: Path):
    def run(source: str, name: str = "Robot.py", extra: dict[str, str] | None = None) -> dict[str, Any]:
        paths = []
        for fname, src in {name: source, **(extra or {})}.items():
            p = tmp_path / fname
            p.write_text(textwrap_dedent(src))
            paths.append(p)
        return ProjectTranslator(db).translate(paths)
    return run


def textwrap_dedent(s: str) -> str:
    import textwrap
    return textwrap.dedent(s).lstrip("\n")
