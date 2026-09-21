# Manual

How to add things to your robot code: motors, servos, sensors, gamepad
controls, autonomous routines, helper classes. The last part covers adding
things to the tool itself.

Every complete example here (the ones starting with `# example:`) is
translated and compiled against the real FTC SDK by `python/tests/test_manual.py`,
so they are known to work. If you change an example, run the tests.

- [1. How it fits together](#1-how-it-fits-together)
- [2. Anatomy of an OpMode](#2-anatomy-of-an-opmode)
- [3. Adding any device: the recipe](#3-adding-any-device-the-recipe)
- [4. Motors](#4-motors)
- [5. Servos and CR servos](#5-servos-and-cr-servos)
- [6. Sensors](#6-sensors)
- [7. Gamepad controls](#7-gamepad-controls)
- [8. Telemetry](#8-telemetry)
- [9. Time and waiting](#9-time-and-waiting)
- [10. Autonomous](#10-autonomous)
- [11. Organizing code: constants, methods, other files](#11-organizing-code-constants-methods-other-files)
- [12. The starter pack](#12-the-starter-pack)
- [13. Python rules cheat sheet](#13-python-rules-cheat-sheet)
- [14. Troubleshooting](#14-troubleshooting)
- [15. Extending the tool](#15-extending-the-tool)
- [16. Saving data between matches](#16-saving-data-between-matches)
- [17. The simulator](#17-the-simulator)

---

## 1. How it fits together

```
your .py files ──► translator ──► Java ──► Control Hub (OnBot Java compiles it)
                                                 │
                                   Driver Hub lists your OpMode ◄┘
```

1. Write a Python file in the workspace.
2. Press **▶ Deploy to Hub** (status bar). Every `.py` file in the workspace is
   translated and uploaded; the hub compiles all of it together.
3. On the Driver Hub, pick the OpMode from the TeleOp or Autonomous list,
   press INIT, then START.

Errors show up in two stages, both as red squiggles in your Python:

- **Translation errors** before anything is uploaded (unsupported Python, a
  misspelled method, a `float` where Java needs an `int`).
- **Build errors** from the hub's Java compiler, mapped back to your line.

To see exactly what went to the robot: *REV FTC: Show Generated Java*.

## 2. Anatomy of an OpMode

```python
# example: anatomy/Basic.py
from ftc.opmode import LinearOpMode, TeleOp


@TeleOp(name="Basic", group="pyftc")      # name shown on the Driver Hub
class Basic(LinearOpMode):                # class name = file name, no spaces

    def runOpMode(self) -> None:          # the SDK calls this when you press INIT
        # INIT: runs once. Get hardware, set directions, reset encoders.
        self.telemetry.addLine("Ready")
        self.telemetry.update()

        self.waitForStart()               # waits here until START (or STOP)

        # START: loops until STOP is pressed
        while self.opModeIsActive():
            self.telemetry.addData("Runtime", self.getRuntime())
            self.telemetry.update()
```

- `@TeleOp` puts it in the TeleOp list, `@Autonomous` in the Autonomous list.
  `@Disabled` hides it without deleting it.
- Everything the SDK gives you hangs off `self`: `self.hardwareMap`,
  `self.telemetry`, `self.gamepad1`, `self.gamepad2`, `self.sleep(...)`.
- Always loop on `self.opModeIsActive()`, never `while True`: that is what
  notices the STOP button.
- One class per file keeps things simple. The class name must be unique across
  the whole workspace (all files end up in one Java package).

## 3. Adding any device: the recipe

Every device goes through the same three steps.

**1. Configure it on the Driver Hub.** *Configure Robot* → your configuration →
the hub (Control Hub or Expansion Hub) → the port type (Motors, Servos, I2C
Bus, Digital Devices, Analog Input) → pick the device type → give it a name.
Save and activate. The name is what code uses, spelling and spaces included.

**2. Declare and fetch it in code.**

```python
from ftc.hardware import DcMotor

class MyRobot(LinearOpMode):
    arm: DcMotor                                          # declare the field + its type

    def runOpMode(self) -> None:
        self.arm = self.hardwareMap.get(DcMotor, "arm")   # "arm" = name from step 1
```

**3. Use it** (sections 4–6).

Which Python type to ask for:

| Configured as (Driver Hub) | Python type | import from |
|---|---|---|
| any motor (Core Hex, UltraPlanetary, HD Hex, goBILDA, ...) | `DcMotor` (or `DcMotorEx` for velocity/current) | `ftc.hardware` |
| Servo | `Servo` | `ftc.hardware` |
| Continuous Rotation Servo, SPARK Mini | `CRServo` | `ftc.hardware` |
| REV Touch Sensor | `TouchSensor` | `ftc.hardware` |
| REV 2m Distance Sensor | `DistanceSensor` | `ftc.hardware` |
| REV Color Sensor V3 | `NormalizedColorSensor` or `DistanceSensor` | `ftc.hardware` |
| built-in IMU | `IMU` | `ftc.hardware` |
| Analog Input (potentiometer) | `AnalogInput` | `ftc.hardware` |
| Digital Device (limit switch, beam break) | `DigitalChannel` | `ftc.hardware` |

The fastest way to get this right: plug everything in, configure it, and
press **Spawn starter pack**. It writes steps 2 and 3 for every configured
device and lists what each type can do.

A name in code that doesn't match the configuration compiles fine but crashes
on INIT with "unable to find a hardware device with name ...". Check spelling
and that the right configuration is active.

## 4. Motors

```python
# example: motors/MotorBasics.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorSimple


@TeleOp(name="Motor basics", group="pyftc")
class MotorBasics(LinearOpMode):
    arm: DcMotor

    def runOpMode(self) -> None:
        self.arm = self.hardwareMap.get(DcMotor, "arm")

        # Which way is "forward"? Flip it here instead of negating powers everywhere.
        self.arm.setDirection(DcMotorSimple.Direction.REVERSE)

        # BRAKE holds position at 0 power, FLOAT coasts.
        self.arm.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE)

        # Encoders: reset to 0, then run with speed control.
        self.arm.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER)
        self.arm.setMode(DcMotor.RunMode.RUN_USING_ENCODER)

        self.waitForStart()
        while self.opModeIsActive():
            self.arm.setPower(-self.gamepad2.left_stick_y)    # -1.0 .. 1.0
            self.telemetry.addData("arm ticks", self.arm.getCurrentPosition())
            self.telemetry.update()
```

### Run to a position

```python
# example: motors/ArmToPosition.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor


@TeleOp(name="Arm to position", group="pyftc")
class ArmToPosition(LinearOpMode):
    arm: DcMotor
    ARM_DOWN: int = 0
    ARM_UP: int = 450          # ticks; read the real value off telemetry

    def runOpMode(self) -> None:
        self.arm = self.hardwareMap.get(DcMotor, "arm")
        self.arm.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER)
        # Order matters: set a target BEFORE switching to RUN_TO_POSITION.
        self.arm.setTargetPosition(self.ARM_DOWN)
        self.arm.setMode(DcMotor.RunMode.RUN_TO_POSITION)
        self.arm.setPower(0.6)     # max speed used to get there

        self.waitForStart()
        while self.opModeIsActive():
            if self.gamepad2.y:
                self.arm.setTargetPosition(self.ARM_UP)
            elif self.gamepad2.a:
                self.arm.setTargetPosition(self.ARM_DOWN)
            self.telemetry.addData("target", self.arm.getTargetPosition())
            self.telemetry.addData("actual", self.arm.getCurrentPosition())
            self.telemetry.addData("moving", self.arm.isBusy())
            self.telemetry.update()
```

Encoder ticks per output revolution are listed in the starter pack's hardware
comments (e.g. Core Hex 288). The value comes from the motor *type selected in
the configuration*, so pick the type that matches the real gearbox.

### Velocity and current: `DcMotorEx`

Ask for `DcMotorEx` instead of `DcMotor` (same configured motor):

```python
# example: motors/Shooter.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorEx
from ftc.navigation import CurrentUnit


@TeleOp(name="Shooter", group="pyftc")
class Shooter(LinearOpMode):
    shooter: DcMotorEx
    TARGET_TICKS_PER_SECOND: float = 1500.0

    def runOpMode(self) -> None:
        self.shooter = self.hardwareMap.get(DcMotorEx, "Shooter1")
        self.shooter.setMode(DcMotor.RunMode.RUN_USING_ENCODER)
        self.waitForStart()
        while self.opModeIsActive():
            if self.gamepad1.right_bumper:
                self.shooter.setVelocity(self.TARGET_TICKS_PER_SECOND)
            else:
                self.shooter.setVelocity(0)
            self.telemetry.addData("velocity", f"{self.shooter.getVelocity():.0f} ticks/s")
            self.telemetry.addData("current", f"{self.shooter.getCurrent(CurrentUnit.AMPS):.2f} A")
            self.telemetry.update()
```

## 5. Servos and CR servos

A **servo** goes to a position between 0.0 and 1.0 and holds it.

```python
# example: servos/Claw.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import Servo


@TeleOp(name="Claw", group="pyftc")
class Claw(LinearOpMode):
    claw: Servo
    OPEN: float = 0.2
    CLOSED: float = 0.65

    def runOpMode(self) -> None:
        self.claw = self.hardwareMap.get(Servo, "claw")
        # Optional: map 0..1 onto a smaller physical range.
        self.claw.scaleRange(0.1, 0.9)
        self.waitForStart()
        while self.opModeIsActive():
            if self.gamepad2.x:
                self.claw.setPosition(self.OPEN)
            elif self.gamepad2.b:
                self.claw.setPosition(self.CLOSED)
            self.telemetry.addData("claw", self.claw.getPosition())
            self.telemetry.update()
```

A servo moves to its position on the first `setPosition`. Setting it during INIT
makes the robot move at INIT, which may be against the rules for your event:
check before doing it.

A **CR (continuous rotation) servo** spins like a motor: `setPower(-1.0 .. 1.0)`.

```python
# example: servos/Intake.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import CRServo, DcMotorSimple


@TeleOp(name="Intake", group="pyftc")
class Intake(LinearOpMode):
    intake: CRServo

    def runOpMode(self) -> None:
        self.intake = self.hardwareMap.get(CRServo, "intake")
        self.intake.setDirection(DcMotorSimple.Direction.REVERSE)
        self.waitForStart()
        while self.opModeIsActive():
            self.intake.setPower(self.gamepad2.right_trigger - self.gamepad2.left_trigger)
```

## 6. Sensors

### IMU (built into the Control Hub)

The IMU must be told how the hub is mounted, or headings will be wrong.
`LogoFacingDirection` is the way the REV logo on the hub faces,
`UsbFacingDirection` the way its USB ports face.

```python
# example: sensors/Heading.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import IMU, RevHubOrientationOnRobot
from ftc.navigation import AngleUnit


@TeleOp(name="Heading", group="pyftc")
class Heading(LinearOpMode):
    imu: IMU

    def runOpMode(self) -> None:
        self.imu = self.hardwareMap.get(IMU, "imu")
        self.imu.initialize(IMU.Parameters(RevHubOrientationOnRobot(
            RevHubOrientationOnRobot.LogoFacingDirection.UP,
            RevHubOrientationOnRobot.UsbFacingDirection.FORWARD)))
        self.imu.resetYaw()
        self.waitForStart()
        while self.opModeIsActive():
            angles = self.imu.getRobotYawPitchRollAngles()
            self.telemetry.addData("yaw", f"{angles.getYaw(AngleUnit.DEGREES):.1f}")
            self.telemetry.addData("pitch", f"{angles.getPitch(AngleUnit.DEGREES):.1f}")
            self.telemetry.addData("roll", f"{angles.getRoll(AngleUnit.DEGREES):.1f}")
            self.telemetry.update()
```

Yaw is counter-clockwise positive, in -180..180.

### Touch, distance, color, analog, digital

```python
# example: sensors/SensorTour.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import AnalogInput, DigitalChannel, DistanceSensor, NormalizedColorSensor, TouchSensor
from ftc.navigation import DistanceUnit


@TeleOp(name="Sensor tour", group="pyftc")
class SensorTour(LinearOpMode):
    touch: TouchSensor
    distance: DistanceSensor
    color: NormalizedColorSensor
    pot: AnalogInput
    beam: DigitalChannel

    def runOpMode(self) -> None:
        self.touch = self.hardwareMap.get(TouchSensor, "touch")
        self.distance = self.hardwareMap.get(DistanceSensor, "distance")
        self.color = self.hardwareMap.get(NormalizedColorSensor, "color")
        self.pot = self.hardwareMap.get(AnalogInput, "pot")
        self.beam = self.hardwareMap.get(DigitalChannel, "beam")
        self.beam.setMode(DigitalChannel.Mode.INPUT)
        self.color.setGain(2.0)

        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("touch pressed", self.touch.isPressed())
            self.telemetry.addData("distance", f"{self.distance.getDistance(DistanceUnit.CM):.1f} cm")

            rgba = self.color.getNormalizedColors()
            self.telemetry.addData("color", f"r {rgba.red:.3f}  g {rgba.green:.3f}  b {rgba.blue:.3f}")
            if rgba.red > rgba.blue and rgba.red > rgba.green:
                self.telemetry.addLine("looks red")

            angle = self.pot.getVoltage() / self.pot.getMaxVoltage() * 270
            self.telemetry.addData("pot angle", f"{angle:.0f} deg")

            # getState() is True when the input is HIGH (for most switches: not pressed)
            self.telemetry.addData("beam", self.beam.getState())
            self.telemetry.update()
```

The REV Color Sensor V3 is also a distance sensor: fetch it once as
`NormalizedColorSensor` and once as `DistanceSensor` with the same name.

## 7. Gamepad controls

`self.gamepad1` is the first driver, `self.gamepad2` the second (a driver
becomes gamepad 1 by pressing START+A on their controller, gamepad 2 with
START+B).

| what | type | range / note |
|---|---|---|
| `left_stick_x`, `left_stick_y`, `right_stick_x`, `right_stick_y` | float | -1..1. **Y is negative when pushed up** |
| `left_trigger`, `right_trigger` | float | 0..1 |
| `a b x y` (PlayStation: `cross circle square triangle`) | bool | |
| `dpad_up dpad_down dpad_left dpad_right` | bool | |
| `left_bumper right_bumper` | bool | |
| `left_stick_button right_stick_button` | bool | pressing the stick in |
| `back start guide` (PS: `share options ps`) | bool | START+A/B pick the driver; avoid START |
| `touchpad`, `touchpad_finger_1_x`... | | PS4/PS5 only |

### Driving, press-once, toggles, rumble

```python
# example: gamepad/Controls.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorSimple, Servo
from ftc.util import Range


@TeleOp(name="Controls", group="pyftc")
class Controls(LinearOpMode):
    left: DcMotor
    right: DcMotor
    claw: Servo

    def runOpMode(self) -> None:
        self.left = self.hardwareMap.get(DcMotor, "Motor L")
        self.right = self.hardwareMap.get(DcMotor, "Motor D")
        self.right.setDirection(DcMotorSimple.Direction.REVERSE)
        self.claw = self.hardwareMap.get(Servo, "claw")

        slow_mode = False
        claw_open = False
        was_a = False          # button state in the previous loop
        was_b = False

        self.waitForStart()
        while self.opModeIsActive():
            # Arcade drive: left stick forward/back, right stick turns
            drive = -self.gamepad1.left_stick_y
            turn = self.gamepad1.right_stick_x
            scale = 0.4 if slow_mode else 1.0
            self.left.setPower(Range.clip(drive + turn, -1.0, 1.0) * scale)
            self.right.setPower(Range.clip(drive - turn, -1.0, 1.0) * scale)

            # Press-once: act only on the loop where A goes from up to down.
            # Checking `if self.gamepad1.a:` alone fires ~50 times per press.
            if self.gamepad1.a and not was_a:
                slow_mode = not slow_mode
                self.gamepad1.rumble(200)             # ms of feedback
            was_a = self.gamepad1.a

            # Toggle a servo with B
            if self.gamepad1.b and not was_b:
                claw_open = not claw_open
            was_b = self.gamepad1.b
            self.claw.setPosition(0.2 if claw_open else 0.65)

            # Deadzone: ignore tiny stick drift
            strafe = self.gamepad1.left_stick_x
            if abs(strafe) < 0.05:
                strafe = 0.0

            self.telemetry.addData("slow mode", slow_mode)
            self.telemetry.addData("claw open", claw_open)
            self.telemetry.update()
```

For tank drive instead: `left = -left_stick_y`, `right = -right_stick_y`.
To move a control to the second driver, replace `gamepad1` with `gamepad2`.

## 8. Telemetry

```python
self.telemetry.addData("caption", value)          # any value: number, bool, str
self.telemetry.addData("pos", f"{x:.2f}, {y:.2f}")  # format with f-strings
self.telemetry.addLine("just text")
self.telemetry.update()                             # nothing shows until this
```

- Call `update()` once per loop, after all the `addData` calls.
- f-string format specs that work: `:.2f` (2 decimals), `:5d` (width 5),
  `:+.1f` (always show sign), `:<10` (left align).

## 9. Time and waiting

```python
# example: time/Timing.py
from ftc.opmode import LinearOpMode, Autonomous
from ftc.hardware import DcMotor
from ftc.util import ElapsedTime


@Autonomous(name="Timing", group="pyftc")
class Timing(LinearOpMode):
    intake: DcMotor

    def runOpMode(self) -> None:
        self.intake = self.hardwareMap.get(DcMotor, "intake")
        timer = ElapsedTime()
        self.waitForStart()

        # Run for 2 seconds while still reacting to STOP
        timer.reset()
        self.intake.setPower(1.0)
        while self.opModeIsActive() and timer.seconds() < 2.0:
            self.telemetry.addData("elapsed", f"{timer.seconds():.1f}")
            self.telemetry.update()
        self.intake.setPower(0)

        self.sleep(500)                 # milliseconds, must be a whole number
        self.sleep(int(0.25 * 1000))    # computed? convert with int(...)
```

`self.sleep` blocks the whole OpMode (no telemetry, no gamepad). In TeleOp use
an `ElapsedTime` check inside the loop instead.

## 10. Autonomous

A complete autonomous with encoder driving and an IMU turn, using helper methods:

```python
# example: auto/SimpleAuto.py
from ftc.opmode import Autonomous, LinearOpMode
from ftc.hardware import DcMotor, DcMotorSimple, IMU, RevHubOrientationOnRobot
from ftc.navigation import AngleUnit
from ftc.util import ElapsedTime, Range


@Autonomous(name="Simple auto", group="pyftc", preselectTeleOp="Controls")
class SimpleAuto(LinearOpMode):
    left: DcMotor
    right: DcMotor
    imu: IMU

    TICKS_PER_REV: float = 560.0        # UltraPlanetary 20:1 from the config comments
    WHEEL_DIAMETER_CM: float = 9.0
    TURN_GAIN: float = 0.02

    def runOpMode(self) -> None:
        self.left = self.hardwareMap.get(DcMotor, "Motor L")
        self.right = self.hardwareMap.get(DcMotor, "Motor D")
        self.right.setDirection(DcMotorSimple.Direction.REVERSE)
        self.imu = self.hardwareMap.get(IMU, "imu")
        self.imu.initialize(IMU.Parameters(RevHubOrientationOnRobot(
            RevHubOrientationOnRobot.LogoFacingDirection.UP,
            RevHubOrientationOnRobot.UsbFacingDirection.FORWARD)))
        self.imu.resetYaw()

        self.waitForStart()
        self.drive_cm(60.0, 0.5)
        self.turn_to(90.0)
        self.drive_cm(30.0, 0.5)

    def cm_to_ticks(self, cm: float) -> int:
        circumference = 3.14159 * self.WHEEL_DIAMETER_CM
        return round(cm / circumference * self.TICKS_PER_REV)

    def drive_cm(self, cm: float, power: float) -> None:
        target = self.cm_to_ticks(cm)
        for motor in [self.left, self.right]:
            motor.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER)
            motor.setTargetPosition(target)
            motor.setMode(DcMotor.RunMode.RUN_TO_POSITION)
            motor.setPower(power)
        while self.opModeIsActive() and (self.left.isBusy() or self.right.isBusy()):
            self.telemetry.addData("left", self.left.getCurrentPosition())
            self.telemetry.addData("right", self.right.getCurrentPosition())
            self.telemetry.update()
        self.left.setPower(0)
        self.right.setPower(0)

    def turn_to(self, target_degrees: float) -> None:
        for motor in [self.left, self.right]:
            motor.setMode(DcMotor.RunMode.RUN_USING_ENCODER)
        timer = ElapsedTime()
        while self.opModeIsActive() and timer.seconds() < 3.0:
            heading = self.imu.getRobotYawPitchRollAngles().getYaw(AngleUnit.DEGREES)
            error = target_degrees - heading
            if abs(error) < 2.0:
                break
            power = Range.clip(error * self.TURN_GAIN, -0.5, 0.5)
            self.left.setPower(-power)      # positive yaw = counter-clockwise
            self.right.setPower(power)
        self.left.setPower(0)
        self.right.setPower(0)
```

- `preselectTeleOp="Controls"` makes the Driver Hub select that TeleOp when the
  autonomous ends.
- Every wait loop checks `self.opModeIsActive()` so STOP works mid-routine.
- A time limit on the turn loop means a bad sensor can't hang the autonomous.

## 11. Organizing code: constants, methods, other files

**Constants**: class attributes. `UPPER_CASE` with a value becomes a Java
constant (`static final`); use `self.NAME` to read it.

**Helper methods**: `def` inside the class. Parameters need type annotations;
a method returning something needs `-> type`. See `drive_cm` above.

**Helper classes in other files** keep OpModes short. Hardware is passed in:

```python
# example: split/Drivetrain.py
from ftc.hardware import DcMotor, DcMotorSimple, HardwareMap
from ftc.util import Range


class Drivetrain:
    left: DcMotor
    right: DcMotor

    def __init__(self, hardware_map: HardwareMap):
        self.left = hardware_map.get(DcMotor, "Motor L")
        self.right = hardware_map.get(DcMotor, "Motor D")
        self.right.setDirection(DcMotorSimple.Direction.REVERSE)

    def arcade(self, drive: float, turn: float) -> None:
        self.left.setPower(Range.clip(drive + turn, -1.0, 1.0))
        self.right.setPower(Range.clip(drive - turn, -1.0, 1.0))

    def stop(self) -> None:
        self.arcade(0.0, 0.0)
```

```python
# example: split/MainTeleOp.py
from ftc.opmode import LinearOpMode, TeleOp
from Drivetrain import Drivetrain


@TeleOp(name="Main TeleOp", group="pyftc")
class MainTeleOp(LinearOpMode):
    def runOpMode(self) -> None:
        drivetrain = Drivetrain(self.hardwareMap)
        self.waitForStart()
        while self.opModeIsActive():
            drivetrain.arcade(-self.gamepad1.left_stick_y, self.gamepad1.right_stick_x)
        drivetrain.stop()
```

Import your own classes with `from FileName import ClassName`. A helper class
has no `@TeleOp`, so it never shows up on the Driver Hub.

**Lists** for groups of things:

```python
motors: list[DcMotor] = [self.left, self.right]
for motor in motors:
    motor.setPower(0)
```

## 12. The starter pack

*Spawn starter pack* (REV FTC sidebar) reads the hub's **active**
configuration and writes an OpMode with:

- a field and `hardwareMap.get` for every configured device;
- a **gamepad control for every motor, CR servo and servo**, listed in a
  "Gamepad controls" table at the top of the file;
- IMU setup, and telemetry for every device plus a live gamepad readout;
- comments describing each device (hub, port, encoder ticks/rev, max RPM,
  whether its hub is connected) and everything each type can do.

How controls get assigned:

1. **Drivetrain**: motors whose name contains a left word and motors whose name
   contains a right word become arcade drive on gamepad 1 (left stick
   forward/back, right stick turns). Words recognised: `left/right`, `L/R`,
   `levi/desni`, `levo/desno`, `L/D`. So `Motor L` + `Motor D` or
   `frontLeft`, `backLeft`, `frontRight`, `backRight` all work. The right side
   is reversed. If your robot has no such names, rename the motors in the
   configuration or edit the generated file.
2. **Other motors and CR servos**, in configuration order, take the next free
   control: the two sticks' up/down (only if there's no drivetrain), triggers
   (RT forward / LT reverse), then button pairs held for forward/reverse:
   RB/LB, D-pad up/down, D-pad right/left, Y/A, B/X.
3. **Servos** take the next free button pair: hold one to move up, the other
   to move down, `SERVO_STEP` per loop.
4. When gamepad 1 runs out, assignment continues on gamepad 2.
5. **IMU**: BACK on gamepad 1 resets heading. **Touch/distance sensors**:
   telemetry only.

Tune `DRIVE_POWER`, `MECHANISM_POWER` and `SERVO_STEP` at the top of the class.
The starter pack is a starting point: it's your file, rename and rearrange
freely. Spawning again won't overwrite it without asking.

### Markers, and why they're there

The generated file carries five pairs of comments like this:

```python
# ── pyftc:imports ──
from ftc.opmode import LinearOpMode, TeleOp
# ── pyftc:imports:end ──
```

one pair each for `imports`, `hardware` (the per-hub/per-device description
comments), `devices` (the class-body field declarations), `init` (the
`hardwareMap.get` lookups, direction/IMU setup and servo starting positions -
everything that happens once, before `waitForStart()`), and `loop` (the
gamepad control code, inside `while self.opModeIsActive():`). There's also one
config line right after the docstring:

```python
# ── pyftc:config name="Galerija" fingerprint="9f2c1ab30c4d5e6f" generated="2026-09-20" ──
```

**Leave these lines alone.** Nothing else about the file is off-limits - rename
fields, reorder devices, rewrite every line of control logic, delete whole
methods - but if a marker comment itself goes missing or gets duplicated,
`starter-update` (below) refuses to touch the file at all rather than guess
where your code ends and generated code begins. It's cheap insurance: the
markers are just comments, Python ignores them completely.

### Updating an existing starter pack

When the hub's hardware configuration changes - a new sensor, a second
expansion hub, a motor unplugged - you don't have to spawn a fresh file and
redo your edits. *Spawn starter pack* on a file that already has the markers
runs an **update** instead of a full regeneration:

- a device the configuration gained gets a field, a `hardwareMap` lookup, a
  hardware-comment line and (if a gamepad slot is still free) a control, each
  inserted **immediately before its region's `:end` marker** - after
  everything already there, never in the middle of it;
- a device the configuration lost is **never deleted**. Its field gets a
  `# pyftc: no longer in the configuration` comment above it; its
  `hardwareMap.get` lookup and its control code are left exactly as they
  were. (This means that lookup will throw at INIT if you actually run the
  file unmodified - the comment is your cue to go deal with it, not a promise
  that the file still works as-is.)
- newly added devices get whatever gamepad control is still free, using the
  **same rules** as a fresh spawn (drivetrain detection aside - see below),
  continuing to gamepad 2 once gamepad 1 fills up;
- only the `fingerprint=` and `generated=` values on the config line change;
  nothing else on that line, and no other line in the file, is rewritten.

Two things it deliberately does **not** do:

- **It doesn't build you a new drivetrain.** If your file has no arcade drive
  yet and you add two new left/right-named motors, they get individual
  gamepad controls like any other motor, not a drivetrain - wiring up arcade
  drive after the fact means either spawning fresh or editing `loop` by hand.
  An *existing* drivetrain is recognised and its two sticks are correctly
  treated as spoken for.
- **It matches devices by name only.** There's no old `config.xml` to diff
  against - only what's already in the file. Renaming a device on the Driver
  Hub, or moving it to a different port, looks exactly like removing the old
  one and adding a new one under a different name. If that's not what you
  want, edit the field/lookup by hand instead of relying on the rename to be
  detected.

If the file's markers are missing or damaged, nothing is touched: the tool
reports it and gives you the newly-generated code as a block to paste in
yourself.

### The generated man page

Alongside the starter pack, *Spawn starter pack* also writes `<Name>.md`: a
full reference for this specific robot that doesn't fit in code comments -
every device's **complete** method list (not just the trimmed one-liners in
the `.py` file - full javadoc paragraphs, inherited methods included, grouped
by the class that declares them), which hub answered when it was generated,
the full control map and how to change it, and a walkthrough of the marker
regions above. It's regenerated wholesale on every spawn or update (it has no
markers of its own - there's nothing in it meant to survive hand edits). Run
it on demand for a file that already has a starter pack without touching the
`.py` file at all: `pyftc manual` (see below).

## 13. Python rules cheat sheet

It's Python syntax on top of Java's rules. The translator stops with a message
on the exact line instead of guessing.

| you write | works? | instead |
|---|---|---|
| `x = 0.5` then `x = 1` | yes, `x` is a float | |
| `def f(self, speed):` | no, needs a type | `def f(self, speed: float) -> None:` |
| `def f(self) :` returning a value | no | `def f(self) -> float:` |
| `self.sleep(0.5 * 1000)` | no, float where int needed | `self.sleep(int(0.5 * 1000))` or `self.sleep(500)` |
| `if x:` with a number | no, no truthiness | `if x != 0:` |
| `if motor:` | no | `if motor is not None:` |
| `a, b = 1, 2` / tuples | no | two assignments |
| `[m.getPower() for m in motors]` | no comprehensions | a `for` loop |
| `def helper():` at module level | no free functions | method, or `@staticmethod` in a class |
| `SPEED = 0.5` at module level | no globals | class attribute |
| `import numpy` / `time` / `random` | no | `math` for maths, `ElapsedTime` for time; other libraries don't exist on the robot |
| `xs[1:3]` slices | no | index or loop |
| `def f(self, x: float = 1.0)` defaults | no | two methods, or always pass it |
| `with`, `yield`, `async`, `lambda` in variables | no | |
| `print(x)` | yes, but goes to the robot log, not the Driver Hub | `self.telemetry.addData` |
| `f"{x:.2f}"`, `abs min max round int float str len`, `math.sqrt/sin/atan2/degrees...` | yes | |
| `x / y` on ints | yes, true division like Python | `//` for floor division |
| `list[float]`, `dict[str, int]` | yes | dict literals must start empty `{}` |
| `try/except/finally`, `raise ValueError("...")` | yes | |

SDK names keep their Java spelling: `setPower`, `getCurrentPosition`,
`hardwareMap`. Anything in FTC docs or samples translates line by line: drop
`;` and braces, add `self.`, write `DcMotor.class` as `DcMotor`, and put types
in annotations.

## 14. Troubleshooting

**First thing to try for any autocomplete problem:** press **Setup files** in the
REV FTC sidebar. It fixes stale paths, missing config and a missing link, and
its details (Show details) say which step failed.

**Nothing autocompletes at all** (`self.left.` offers nothing): you have no
Python language server. The Python extension stopped shipping one when it
dropped Jedi, and the engine that replaced it, Pylance, is licensed to run only
on Microsoft's own build of VS Code - on Code - OSS, VSCodium or any build that
installs extensions from Open VSX it will not load. Install basedpyright, which
is the same underlying engine (pyright) and does work there:

```bash
code --install-extension detachhead.basedpyright
```

Then reload the window. `REV FTC: Check Autocomplete` reports this case and
offers to install it for you. If you prefer Pylance, you need the official
VS Code build rather than the distribution's package.

**Autocomplete works for `self.left.` but not `import ftc.hardware`**: the stub
directory is not on the analysis path. `REV FTC: Check Autocomplete` prints the
exact path and where it should be listed; the extension writes both
`python.analysis.extraPaths` and `basedpyright.analysis.extraPaths` by itself,
but it deliberately never re-adds a path you removed on purpose.

**"No Control Hub found"**: on USB, check the cable and that REV Hardware
Client isn't holding the hub; on Wi-Fi, check you're connected to the robot's
network. The *Hub* view in the sidebar shows what the extension sees.

**Red squiggle: "cannot infer the type of 'x'"**: annotate the first assignment,
`x: float = ...`.

**Red squiggle: "X has no method 'y'"**: typo, or the method lives on a
different type (`DcMotorEx` has velocity methods, `DcMotor` doesn't).

**Build failed "in file(s) not managed by this extension"**: a hand-written
Java file in OnBot Java is broken, and the hub compiles everything together.
Fix or delete it in the OnBot Java editor.

**OpMode doesn't show on the Driver Hub**: check the Deploy notification said
the build succeeded; check the decorator (`@TeleOp`/`@Autonomous`) and that it
isn't `@Disabled`. Helper classes never show, by design.

**Crash on INIT "unable to find a hardware device"**: the name in
`hardwareMap.get` doesn't match the active configuration.

**Robot drives in circles / backwards**: flip `setDirection` on one side.

**A servo slams to one end on START**: it's going to the position you set;
change the initial position.

**Autocomplete doesn't work**: accept the "Enable FTC autocomplete" prompt, or
add the extension's `python` folder to `python.analysis.extraPaths` by hand.

---

## 15. Extending the tool

For changing the tool itself, not robot code. Architecture and the verified hub
protocol are in [ARCHITECTURE.md](ARCHITECTURE.md).

### Add support for a new SDK version

When the Robot Controller app is updated (the hub reports its SDK in the Hub view):

```bash
cd sdkgen && uv run python -m sdkgen --sdk 12.0.0 --out ../python
eval "$(scripts/javac-env.sh 12.0.0)"
cd python && uv run --no-project --with pytest pytest -q tests
```

Then point `DEFAULT_SDK` in `python/pyftc/typedb.py` at the new version (or
pass `--sdk`), and update the database path in `tests/conftest.py`.

### Add a Java standard-library class or method

The SDK database only covers FTC classes. The JDK classes the translator knows
about (`Math`, `String`, `List`, `Map`, ...) are a hand-written slice in
`JDK` in `python/pyftc/typedb.py`, in the same shape as the generated
database. Add the class there with the `_cls`/`_m` helpers. To let users import
it, map a Python module name to it in `_resolve_imports` in
`python/pyftc/translate.py`, and give it a stub under `python/ftc/`.

### Add a Python construct to the translator

`python/pyftc/translate.py`, class `ClassTranslator`:

- **expressions**: add `e_<AstNodeName>(self, node, expected) -> Expr`. It
  returns the Java text, its Java type, and its precedence. `self.expr(child)`
  translates children.
- **statements**: add a branch in `stmt()`.
- **builtins** like `len`: add `b_<name>(self, node, expected) -> Expr`.
- **Python method names on containers** (`append` → `add`): the
  `LIST_METHODS` / `STR_METHODS` tables.
- Raise `self.fail(node, "message")` for anything unsupported; the message is
  what the user sees.

Types are only tracked where the emitted Java depends on them; javac on the hub
is the real type checker.

Then add a test in `python/tests/test_translate.py`. Tests run against both the
hand-written fixture and the real SDK database, and `test_javac.py` compiles
every accepted program with javac.

### The `pyftc` CLI's starter-pack subcommands

All four take `--config <config.xml>` (from `adb cat /sdcard/FIRST/<name>.xml`);
`starter` and `manual` also take `--rcinfo <rcInfo.json>` (`GET /js/rcInfo.json`,
optional) and `--name <ClassName>`.

- `pyftc starter --config ... --rcinfo ... --name ...` - a fresh starter pack.
  Returns `{ok, python, fingerprint, manual}`.
- `pyftc manual --config ... --rcinfo ... --name ...` - just the man page, for
  a file whose starter pack already exists. Returns `{ok, markdown, fingerprint}`.
- `pyftc config-fingerprint --config ...` - the fingerprint alone, from the
  config XML only. Deliberately does not load the SDK type database (see
  "Fingerprint" below), so it's cheap enough to call on every hub refresh to
  decide whether anything changed at all. Returns `{ok, fingerprint}`.
- `pyftc starter-update --file <existing.py> --config ... --rcinfo ...` -
  extend an existing starter pack in place (see "Updating an existing starter
  pack" above). Returns
  `{ok, changed, applied, fingerprint, python?, block?, manual?, added, removed, hubsAdded, notes}`;
  `python`/`manual` are only present when `applied` is true, `block` only
  when it's false.

#### Fingerprint

`sha256` over the canonical sorted JSON of the configuration's hubs and
devices, truncated to 16 hex characters (`python/pyftc/markers.py`,
`compute_fingerprint`). It changes on a rename, a port move, an added or
removed device, or a new hub; it's stable across rcInfo (a hub being
unplugged doesn't count as a configuration change), and across the SDK
version resolving a config's XML tags to different Java types (there's no SDK
database involved in computing it at all - the XML tag itself stands in for
the resolved Java type, since for a fixed SDK version one determines the
other 1:1 anyway).

### Change the starter pack

- Layout, header comments, capability lists, and the Contract 4 markers:
  `python/pyftc/starter.py`.
- Gamepad assignment rules: `python/pyftc/controls.py`. The plan is built as
  data first (which device gets which control), then rendered into both the
  header table and the loop, so they can't disagree. Add a device kind in
  `_kind()`, and a branch in `_assign_device()` (shared by a fresh spawn and
  by `starter-update`'s newly-added devices).
- Marker finding/parsing/inserting, and the fingerprint: `python/pyftc/markers.py`.
- The update flow itself (diffing the new config against what a file's
  markers already record, by device name): `python/pyftc/update.py`.
- The generated man page: `python/pyftc/manual.py`.
- Tests: `python/tests/test_starter.py`, `test_markers.py`, `test_update.py`,
  `test_manual_gen.py` (three real-shaped configurations in `tests/fixtures/`).

### Add a manual example

Start a Python code block with `# example: <group>/<File>.py`. Blocks with the
same group are translated together as one project (for multi-file examples).
`test_manual.py` translates and compiles all of them.

### Extension

`extension/src/`: `commands/` (deploy, starter pack, show Java),
`hub/` (connection via Wi-Fi or adb, OnBot Java client, build-log parser),
`sidebar/`. Tests: `npm test` (unit), `npm run smoke` (real hub),
`npm run e2e` (real VS Code + real hub).

### Running all tests

```bash
eval "$(scripts/javac-env.sh)"                            # JDK 17 + SDK jars for javac checks
cd python && uv run --no-project --with pytest pytest -q tests
cd ../extension && npm test
```

## 16. Saving data between matches

Static fields don't survive a Robot Controller power cycle: the app process
(and everything only ever held in memory) restarts between matches, sometimes
even between OpModes. To carry a value from one match into the next -- a
measured drift correction, a chosen autonomous path, anything that needs to
outlive an app restart -- write it to a file and read it back at INIT.

`ftc.io` wraps the SDK's own recipe for this: `AppUtil.getInstance()` finds a
writable settings file, and `ReadWriteFile` (already in `ftc.util`) reads and
writes its contents as plain text. A typical pair is an `Aftercare` OpMode run
once after the match, and the main TeleOp reading the file back at the top of
`runOpMode`:

```python
# example: aftercare/Aftercare.py
from ftc.opmode import LinearOpMode, Autonomous
from ftc.io import File, AppUtil, ReadWriteFile


@Autonomous(name="Aftercare", group="pyftc")
class Aftercare(LinearOpMode):
    """Run this manually after a match to save whatever the next match should know."""

    def runOpMode(self) -> None:
        self.waitForStart()
        f: File = AppUtil.getInstance().getSettingsFile("specs.txt")
        ReadWriteFile.writeFile(f, "1.5,2.5")
        self.telemetry.addLine("saved")
        self.telemetry.update()
```

```python
# example: aftercare/Main.py
from ftc.opmode import LinearOpMode, TeleOp
from ftc.io import File, AppUtil, ReadWriteFile


@TeleOp(name="Main", group="pyftc")
class Main(LinearOpMode):
    heading: float = 0.0
    distance: float = 0.0

    def runOpMode(self) -> None:
        f: File = AppUtil.getInstance().getSettingsFile("specs.txt")
        if f.exists():
            parts = ReadWriteFile.readFile(f).split(",")
            self.heading = float(parts[0])
            self.distance = float(parts[1])
        # else: keep the defaults above -- first run, or a freshly wiped hub
        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("heading", self.heading)
            self.telemetry.addData("distance", self.distance)
            self.telemetry.update()
```

- **Where the file lives**: `AppUtil.getInstance().getSettingsFile(name)`
  resolves a relative name against `AppUtil.ROBOT_SETTINGS`, which the SDK
  source defines as `FIRST/settings/` under external storage -- on a Control
  Hub that's `/sdcard/FIRST/settings/<name>`. That's the same `/sdcard/FIRST/`
  folder the hardware configuration XML already lives in (see
  ARCHITECTURE.md's verified hub facts), just a `settings` subfolder of it, so
  it won't collide with the configuration file or OnBot Java's own sources.
- **It survives a reboot.** It's a plain file on the hub's internal storage,
  not app memory, so a power cycle (the whole point of this section) doesn't
  touch it -- only deleting the file, or wiping the hub, does.
- **Always check `exists()` before reading.** The first run after a fresh
  install or a wiped hub, there's nothing to read yet; `Main` above falls back
  to the class's own default field values (`heading`/`distance` at 0.0) when
  the file isn't there.
- **What's available**: only `File` (a handful of the real `java.io.File`
  methods -- construct, `exists`, `delete`, `mkdirs`, name/path queries,
  `length`) and `AppUtil.getInstance()`/`getSettingsFile(String)`. The rest of
  `AppUtil` (dialogs, USB, websockets, ~120 other methods) isn't reachable
  from a Python OpMode and was deliberately left out; see the comment above
  the type database entry in `python/pyftc/typedb.py` for why.
- **Not verified on real hardware.** Everything above is translated and
  compiled against the real SDK jars (`python/tests/test_manual.py`), and the
  paths quoted are read directly from the SDK's own source
  (`AppUtil.ROOT_FOLDER`/`FIRST_FOLDER`/`ROBOT_SETTINGS`), but nobody has run
  an `Aftercare` OpMode on a physical Control Hub, power-cycled it, and
  confirmed the Robot Controller app can actually write to
  `/sdcard/FIRST/settings/` at runtime and that the value is still there
  after reboot. That's a claim only the real hub can settle -- treat it as
  unverified until someone runs it at an event or on the bench.

## 17. The simulator

`REV FTC: Open Simulator` (the ▷ screen icon in the Hub sidebar and in the editor
title bar of a `.py` file) opens a panel beside your code. It translates your
OpModes exactly as a deploy would, compiles them, and runs them against
simulated hardware built from your robot configuration: the hub's active
configuration when a hub is connected, otherwise a configuration XML in the
workspace, otherwise the device list in a starter pack's comment block. No robot
needed.

- **Driver Hub** (right): pick the OpMode, INIT, START, STOP. Telemetry shows what
  the Driver Hub would show, including the SDK's 250 ms throttle (a line you add
  for a single loop may never arrive, on the robot too). Errors show the exception
  and the Python line; they also land in the Problems panel.
- **Gamepads**: choose the controller type (PS4/PS5 buttons are Cross/Circle/…,
  Xbox and Logitech are A/B/…; the code gets both names). Input comes from a
  plugged-in controller (the panel, or on Linux the system reader: hold START
  and press A to become gamepad1, START+B for gamepad2), from the keyboard
  ("Keys: Gamepad 1"), or by clicking the drawing. The line under the drawing is
  exactly what the code receives: pushing a stick up gives a negative `left_stick_y`.
- **3D bench**: every motor, servo and sensor floats in space. Drag to orbit,
  right-drag to pan, wheel to zoom, WASD to fly (when "Keys: Camera"). Click a
  device, then Move (G) / Rotate (R) it; the layout is saved in
  `.pyftc/sim-layout.json`. A spinning motor shows a curved arrow on its yellow
  shaft face (orange = clockwise, blue = counter-clockwise, as seen looking at the
  shaft) and a label with power, REVERSED and rpm. That arrow is after
  `setDirection()` and after the motor type's own reversal, so it is the way the
  shaft really turns. Servos show their 0..1 arc and where the horn is.
- **Sensors**: click and hold a touch sensor or limit switch; distance and colour
  sensors see the walls you add (or take a manual value in the inspector); rotate
  the Control Hub to move the IMU.
- **Code view and editor**: the lines that ran in the last loop are highlighted in
  your `.py` file and in the panel, with the values locals got; the OpMode's
  fields are listed live.
- **Debug**: set breakpoints in your `.py` file and press Debug (or `REV FTC: Debug
  in Simulator`). The OpMode stops on the line, sim time and the motors freeze,
  and Variables / Watch / Call Stack show Python names. Step goes one Python line
  at a time.
- **Warnings** point at logic mistakes: a motor set twice with different values
  in one loop (only the last one stays; the first reaches the motor for a few
  ms), a loop that never checks `opModeIsActive()` (STOP cannot stop it), a busy
  loop that never calls the SDK.

What it is not: the motors spin free on a bench, there is no robot driving on a
field. Motor speeds come from REV's published curves and the real UltraPlanetary
ratios (set your cartridge stack per motor in the inspector; the SDK itself
assumes 20:1). A few numbers are placeholders and are listed in
`docs/ARCHITECTURE.md`. The simulator needs a JDK (Java 11+); it finds one via
`revFtc.javaHome`, `JAVA_HOME` or `PATH`, or offers to download JDK 17.
