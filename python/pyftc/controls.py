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

`starter-update` (update.py) needs the same assignment logic for devices
added after the fact, but seeded from whatever the *existing* file's loop
already spends: `scan_used` and `free_pools_for_update` reverse-parse the
generated "# "name": gamepad N: ..." comments (the only record of what was
handed out, since starter-update never re-derives state from the old XML)
back into pool entries, and `plan_added_devices` hands out what's left using
the exact same `_assign_device` a fresh generation uses, so the two paths
can't drift apart.
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

# Telemetry footer every starter pack ends its loop with. Static (no device
# depends on it), so it lives outside the pyftc:loop marker: a device added by
# starter-update lands right after the existing per-device code and before
# this, instead of after it.
GAMEPAD_READOUT = [
    "# Live gamepad readout, handy for checking which button is which",
    'self.telemetry.addData("Gamepad 1 sticks", f"L ({self.gamepad1.left_stick_x:.2f}, '
    '{self.gamepad1.left_stick_y:.2f})  R ({self.gamepad1.right_stick_x:.2f}, '
    '{self.gamepad1.right_stick_y:.2f})")',
    'self.telemetry.addData("Gamepad 1 triggers", f"L {self.gamepad1.left_trigger:.2f}  '
    'R {self.gamepad1.right_trigger:.2f}")',
    'self.telemetry.addData("Gamepad 1 A/B/X/Y", f"{self.gamepad1.a} {self.gamepad1.b} '
    '{self.gamepad1.x} {self.gamepad1.y}")',
]


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

    def key(self) -> tuple:
        """Identity for pool bookkeeping, independent of which Control
        instance: two Controls with the same key occupy the same slot."""
        if self.kind == "stick":
            return ("stick", self.stick)
        if self.kind == "triggers":
            return ("triggers", self.pad)
        return ("pair", self.buttons)


@dataclass
class ControlPlan:
    table: list[str] = field(default_factory=list)       # "# " lines for the header
    constants: list[str] = field(default_factory=list)   # class body lines
    init: list[str] = field(default_factory=list)        # after the hardwareMap lookups
    before_loop: list[str] = field(default_factory=list)
    loop: list[str] = field(default_factory=list)
    imports: dict[str, set[str]] = field(default_factory=dict)
    # field -> control description handed to that device, or None if it got
    # none left. Populated for every device plan_controls/plan_added_devices
    # actually assigns something to (drivetrain motors aren't, since their
    # "control" is the drivetrain itself, described separately).
    assigned: dict[str, str | None] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def need(self, module: str, name: str) -> None:
        self.imports.setdefault(module, set()).add(name)


def side_of(name: str) -> str | None:
    words = {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", name)}
    left, right = bool(words & LEFT_WORDS), bool(words & RIGHT_WORDS)
    if left == right:
        return None
    return "left" if left else "right"


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


def _take(pools: dict[str, list[Control]], want_pair: bool) -> Control | None:
    for pad in ("gamepad1", "gamepad2"):
        for c in pools[pad]:
            if not want_pair or c.kind == "pair":
                pools[pad].remove(c)
                return c
    return None


def _py_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _assign_device(d: Device, kind: str, pools: dict[str, list[Control]], p: ControlPlan) -> None:
    """One device's control: appends its header/loop/init lines to `p` and
    records what (if anything) it got in `p.assigned`. Shared by a fresh
    generation and by starter-update, so the two can't disagree about what a
    given free slot looks like."""
    if kind in ("motor", "crservo"):
        c = _take(pools, want_pair=False)
        if c is None:
            p.table.append(f'"{d.name}": no free control left, add one by hand')
            p.assigned[d.field] = None
            p.notes.append(f'"{d.name}": no free gamepad control left; add one by hand in the loop marker')
            return
        p.assigned[d.field] = c.describe()
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
        c = _take(pools, want_pair=True)
        if c is None:
            p.table.append(f'"{d.name}": no free button pair left, add one by hand')
            p.assigned[d.field] = None
            p.notes.append(f'"{d.name}": no free button pair left; add one by hand in the loop marker')
            return
        up, down = c.buttons
        pos = f"{d.field}_position"
        p.assigned[d.field] = c.describe(servo=True)
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
        p.assigned[d.field] = "gamepad 1: BACK resets the heading"
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
        p.assigned[d.field] = "telemetry only"
        p.loop += [f'self.telemetry.addData("{_py_str(d.name)} pressed", self.{d.field}.isPressed())', ""]
    elif kind == "distance":
        p.need("ftc.navigation", "DistanceUnit")
        p.assigned[d.field] = "telemetry only"
        p.loop += [f'self.telemetry.addData("{_py_str(d.name)}", '
                   f'f"{{self.{d.field}.getDistance(DistanceUnit.CM):.1f}} cm")', ""]


def plan_controls(devices: list[Device]) -> ControlPlan:
    p = ControlPlan()
    kinds = {d.field: _kind(d) for d in devices}
    motors = [d for d in devices if kinds[d.field] == "motor"]
    left = [d for d in motors if side_of(d.name) == "left"]
    right = [d for d in motors if side_of(d.name) == "right"]
    drive = bool(left and right)
    drive_fields = {d.field for d in left + right} if drive else set()

    pools = {pad: _pool(pad, sticks_free=not (drive and pad == "gamepad1")) for pad in ("gamepad1", "gamepad2")}

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
        if d.field in drive_fields:
            continue
        _assign_device(d, kinds[d.field], pools, p)

    if not p.table:
        p.table.append("No motors or servos in this configuration: only the gamepad readout below.")
    return p


def plan_added_devices(devices: list[Device], pools: dict[str, list[Control]]) -> ControlPlan:
    """Same per-device assignment as a fresh `plan_controls`, but for devices
    `starter-update` is adding to an existing file: no drivetrain synthesis
    (an existing file's arcade drive, if any, is left alone - see
    docs/MANUAL.md on starter-update's limits), no constants (the file
    already has DRIVE_POWER/MECHANISM_POWER/SERVO_STEP from its first
    generation), starting from whatever `pools` says is still free."""
    p = ControlPlan()
    for d in devices:
        _assign_device(d, _kind(d), pools, p)
    return p


# ---------------------------------------------------------------------------
# Reverse-parsing an existing file's loop marker, for starter-update.

_STICK_RE = re.compile(r"^gamepad (1|2): (left|right) stick up/down$")
_TRIGGER_RE = re.compile(r"^gamepad (1|2): right trigger forward, left trigger reverse$")
_PAIR_MOTOR_RE = re.compile(r"^gamepad (1|2): hold (.+?) forward, hold (.+?) reverse$")
_PAIR_SERVO_RE = re.compile(r"^gamepad (1|2): hold (.+?) / hold (.+?) to move it$")
_COMMENT_RE = re.compile(r'^#\s*"(?:[^"\\]|\\.)*"\s*:\s*(?P<desc>.+)$')
DRIVE_LINE = "# Drive: left stick forward/back, right stick turns"

_DISPLAY_TO_PAIR = {(BUTTON_NAMES[a], BUTTON_NAMES[b]): (a, b) for a, b in BUTTON_PAIRS}


def scan_used(loop_text: str) -> tuple[dict[str, set[tuple]], bool]:
    """Reverse-parse the "# "name": gamepad N: ..." comments a generated loop
    marker carries (the only record of what a device was given - starter-update
    does not re-run the original config through plan_controls) into the same
    keys `Control.key()` produces, plus whether an existing drivetrain claims
    gamepad1's sticks.

    Robustness note: this only recognises the exact phrasings `describe()`
    emits above. A control line a user hand-edited into something else is
    simply invisible to it - the device is presumed to keep whatever it has,
    which is the safe direction to be wrong in (worst case a new device is
    offered a slot that's actually still in use, surfaced as a plain gamepad
    control that then collides with an existing one - never data loss).
    """
    taken: dict[str, set[tuple]] = {"gamepad1": set(), "gamepad2": set()}
    drive = False
    for raw in loop_text.splitlines():
        line = raw.strip()
        if line == DRIVE_LINE:
            drive = True
            continue
        cm = _COMMENT_RE.match(line)
        if not cm:
            continue
        desc = cm.group("desc")
        m = _STICK_RE.match(desc)
        if m:
            taken[f"gamepad{m.group(1)}"].add(("stick", f"{m.group(2)}_stick_y"))
            continue
        m = _TRIGGER_RE.match(desc)
        if m:
            taken[f"gamepad{m.group(1)}"].add(("triggers", f"gamepad{m.group(1)}"))
            continue
        m = _PAIR_MOTOR_RE.match(desc) or _PAIR_SERVO_RE.match(desc)
        if m:
            pair = _DISPLAY_TO_PAIR.get((m.group(2), m.group(3)))
            if pair:
                taken[f"gamepad{m.group(1)}"].add(("pair", pair))
    return taken, drive


def free_pools_for_update(loop_text: str) -> dict[str, list[Control]]:
    taken, drive = scan_used(loop_text)
    pools: dict[str, list[Control]] = {}
    for pad in ("gamepad1", "gamepad2"):
        sticks_free = not (drive and pad == "gamepad1")
        pools[pad] = [c for c in _pool(pad, sticks_free) if c.key() not in taken[pad]]
    return pools
