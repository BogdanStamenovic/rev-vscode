"""Gamepad control scheme for the starter pack.

Every starter pack gets working controls, whatever the configuration holds:
  - motors whose names say left/right (English or Serbian) become an arcade
    drivetrain on gamepad1's sticks;
  - every other motor and CR servo gets the next free control, analog first
    (sticks, then triggers), then button pairs;
  - servos get a button pair that nudges the position while held;
  - IMU, touch and distance sensors are read out on telemetry;
  - gamepad1 fills up first, then gamepad2.
The plan is data first (who gets what) so the header table and the loop code
cannot disagree.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .starter import Device

HW = "com.qualcomm.robotcore.hardware"
LEFT_WORDS = {"left", "l", "levi", "levo", "lijevi", "lijevo", "leva", "lijeva"}
RIGHT_WORDS = {"right", "r", "desni", "desno", "d", "desna"}

BUTTON_NAMES = {
    "right_bumper": "RB", "left_bumper": "LB", "dpad_up": "D-pad up", "dpad_down": "D-pad down",
    "dpad_right": "D-pad right", "dpad_left": "D-pad left", "y": "Y", "a": "A", "b": "B", "x": "X",
}
BUTTON_PAIRS = [("right_bumper", "left_bumper"), ("dpad_up", "dpad_down"), ("dpad_right", "dpad_left"),
                ("y", "a"), ("b", "x")]


@dataclass
class Control:
    pad: str                      # "gamepad1" / "gamepad2"
    kind: str                     # "stick" | "triggers" | "pair"
    stick: str = ""               # left_stick_y / right_stick_y
    buttons: tuple[str, str] = ("", "")

    def describe(self, servo: bool = False) -> str:
        pad = "gamepad 1" if self.pad == "gamepad1" else "gamepad 2"
        if self.kind == "stick":
            side = "left" if self.stick.startswith("left") else "right"
            return f"{pad}: {side} stick up/down"
        if self.kind == "triggers":
            return f"{pad}: right trigger forward, left trigger reverse"
        up, down = (BUTTON_NAMES[b] for b in self.buttons)
        return f"{pad}: hold {up} / hold {down}" if servo else f"{pad}: hold {up} forward, hold {down} reverse"


@dataclass
class ControlPlan:
    table: list[str] = field(default_factory=list)       # "# " lines for the header
    constants: list[str] = field(default_factory=list)   # class body lines
    init: list[str] = field(default_factory=list)        # after the hardwareMap lookups
    before_loop: list[str] = field(default_factory=list)
    loop: list[str] = field(default_factory=list)
    imports: dict[str, set[str]] = field(default_factory=dict)

    def need(self, module: str, name: str) -> None:
        self.imports.setdefault(module, set()).add(name)


def side_of(name: str) -> str | None:
    words = {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", name)}
    left, right = bool(words & LEFT_WORDS), bool(words & RIGHT_WORDS)
    if left == right:
        return None
    return "left" if left else "right"


def plan_controls(devices: list[Device]) -> ControlPlan:
    p = ControlPlan()
    kinds = {d.field: _kind(d) for d in devices}
    motors = [d for d in devices if kinds[d.field] == "motor"]
    left = [d for d in motors if side_of(d.name) == "left"]
    right = [d for d in motors if side_of(d.name) == "right"]
    drive = bool(left and right)
    drive_fields = {d.field for d in left + right} if drive else set()

    pools = {pad: _pool(pad, sticks_free=not (drive and pad == "gamepad1")) for pad in ("gamepad1", "gamepad2")}

    def take(want_pair: bool) -> Control | None:
        for pad in ("gamepad1", "gamepad2"):
            for c in pools[pad]:
                if not want_pair or c.kind == "pair":
                    pools[pad].remove(c)
                    return c
        return None

    p.constants += ["    DRIVE_POWER: float = 1.0      # 0..1, lower it for gentler driving",
                    "    MECHANISM_POWER: float = 0.8  # power for button-controlled motors",
                    "    SERVO_STEP: float = 0.01      # how far a servo moves per loop while a button is held"]

    if drive:
        p.need("ftc.hardware", "DcMotorSimple")
        p.need("ftc.util", "Range")
        names = ", ".join(f'"{d.name}"' for d in left) + " (left), " + ", ".join(f'"{d.name}"' for d in right) + " (right)"
        p.table.append(f"Drive {names}: gamepad 1 left stick forward/back, right stick turns")
        for d in right:
            p.init.append(f"self.{d.field}.setDirection(DcMotorSimple.Direction.REVERSE)  "
                          "# right side mirrored; remove if the robot drives in circles")
        p.loop += ["# Drive: left stick forward/back, right stick turns",
                   "drive = -self.gamepad1.left_stick_y  # stick up is negative",
                   "turn = self.gamepad1.right_stick_x",
                   "left_power = Range.clip(drive + turn, -1.0, 1.0) * self.DRIVE_POWER",
                   "right_power = Range.clip(drive - turn, -1.0, 1.0) * self.DRIVE_POWER"]
        p.loop += [f"self.{d.field}.setPower(left_power)" for d in left]
        p.loop += [f"self.{d.field}.setPower(right_power)" for d in right]
        p.loop.append('self.telemetry.addData("Drive", f"left {left_power:.2f}  right {right_power:.2f}")')
        p.loop.append("")

    for d in devices:
        kind = kinds[d.field]
        if d.field in drive_fields:
            continue
        if kind in ("motor", "crservo"):
            c = take(want_pair=False)
            if c is None:
                p.table.append(f'"{d.name}": no free control left, add one by hand')
                continue
            p.table.append(f'"{d.name}": {c.describe()}')
            p.loop.append(f'# "{d.name}": {c.describe()}')
            g = f"self.{c.pad}"
            if c.kind == "stick":
                p.loop.append(f"self.{d.field}.setPower(-{g}.{c.stick})")
            elif c.kind == "triggers":
                p.loop.append(f"self.{d.field}.setPower(({g}.right_trigger - {g}.left_trigger) * self.MECHANISM_POWER)")
            else:
                fwd, rev = c.buttons
                p.loop += [f"if {g}.{fwd}:", f"    self.{d.field}.setPower(self.MECHANISM_POWER)",
                           f"elif {g}.{rev}:", f"    self.{d.field}.setPower(-self.MECHANISM_POWER)",
                           "else:", f"    self.{d.field}.setPower(0)"]
            p.loop.append(f'self.telemetry.addData("{_py_str(d.name)}", f"power {{self.{d.field}.getPower():.2f}}")')
            p.loop.append("")
        elif kind == "servo":
            c = take(want_pair=True)
            if c is None:
                p.table.append(f'"{d.name}": no free button pair left, add one by hand')
                continue
            up, down = c.buttons
            pos = f"{d.field}_position"
            p.table.append(f'"{d.name}": {c.describe(servo=True)} to move it')
            p.before_loop.append(f"{pos} = 0.5  # servo jumps here on START; set your starting position")
            g = f"self.{c.pad}"
            p.loop += [f'# "{d.name}": {c.describe(servo=True)} to move it',
                       f"if {g}.{up}:", f"    {pos} = min({pos} + self.SERVO_STEP, 1.0)",
                       f"elif {g}.{down}:", f"    {pos} = max({pos} - self.SERVO_STEP, 0.0)",
                       f"self.{d.field}.setPosition({pos})",
                       f'self.telemetry.addData("{_py_str(d.name)}", f"position {{{pos}:.2f}}")', ""]
        elif kind == "imu":
            p.need("ftc.hardware", "RevHubOrientationOnRobot")
            p.need("ftc.navigation", "AngleUnit")
            p.table.append(f'"{d.name}": gamepad 1 BACK resets the heading to 0')
            p.init += [f"# Tell the IMU how the hub is mounted, or the heading will be wrong.",
                       f"self.{d.field}.initialize(IMU.Parameters(RevHubOrientationOnRobot(",
                       "    RevHubOrientationOnRobot.LogoFacingDirection.UP,",
                       "    RevHubOrientationOnRobot.UsbFacingDirection.FORWARD)))"]
            p.loop += [f'# "{d.name}": BACK resets the heading',
                       "if self.gamepad1.back:", f"    self.{d.field}.resetYaw()",
                       f"heading = self.{d.field}.getRobotYawPitchRollAngles().getYaw(AngleUnit.DEGREES)",
                       f'self.telemetry.addData("{_py_str(d.name)} heading", f"{{heading:.1f}} deg")', ""]
        elif kind == "touch":
            p.loop += [f'self.telemetry.addData("{_py_str(d.name)} pressed", self.{d.field}.isPressed())', ""]
        elif kind == "distance":
            p.need("ftc.navigation", "DistanceUnit")
            p.loop += [f'self.telemetry.addData("{_py_str(d.name)}", '
                       f'f"{{self.{d.field}.getDistance(DistanceUnit.CM):.1f}} cm")', ""]

    p.loop += ["# Live gamepad readout, handy for checking which button is which",
               'self.telemetry.addData("Gamepad 1 sticks", f"L ({self.gamepad1.left_stick_x:.2f}, '
               '{self.gamepad1.left_stick_y:.2f})  R ({self.gamepad1.right_stick_x:.2f}, '
               '{self.gamepad1.right_stick_y:.2f})")',
               'self.telemetry.addData("Gamepad 1 triggers", f"L {self.gamepad1.left_trigger:.2f}  '
               'R {self.gamepad1.right_trigger:.2f}")',
               'self.telemetry.addData("Gamepad 1 A/B/X/Y", f"{self.gamepad1.a} {self.gamepad1.b} '
               '{self.gamepad1.x} {self.gamepad1.y}")']
    if not p.table:
        p.table.append("No motors or servos in this configuration: only the gamepad readout below.")
    return p


def _kind(d: Device) -> str | None:
    return {f"{HW}.DcMotor": "motor", f"{HW}.CRServo": "crservo", f"{HW}.Servo": "servo", f"{HW}.IMU": "imu",
            f"{HW}.TouchSensor": "touch", f"{HW}.DistanceSensor": "distance"}.get(d.java_type or "")


def _pool(pad: str, sticks_free: bool) -> list[Control]:
    out = []
    if sticks_free:
        out += [Control(pad, "stick", stick="left_stick_y"), Control(pad, "stick", stick="right_stick_y")]
    out.append(Control(pad, "triggers"))
    out += [Control(pad, "pair", buttons=b) for b in BUTTON_PAIRS]
    return out


def _py_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')
