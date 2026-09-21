// Python source the fake simulator pretends to run; line numbers for events and traces are looked up
// from it so the code view lines up.
export const MAIN_PY = `from pyftc import *


class Cycle:
    def __init__(self):
        self.count = 0
        self.phase = 0
        self.last_ms = 0.0


@TeleOp(name="Main", group="pyftc")
class Main(LinearOpMode):
    def runOpMode(self):
        self.lf = self.hardwareMap.get(DcMotor, "LF")
        self.rf = self.hardwareMap.get(DcMotor, "RF")
        self.lb = self.hardwareMap.get(DcMotor, "LB")
        self.rb = self.hardwareMap.get(DcMotor, "RB")
        self.shooter = self.hardwareMap.get(DcMotor, "shooter")
        intake = self.hardwareMap.get(CRServo, "intake")
        chain_drop = self.hardwareMap.get(Servo, "chainDrop")

        self.lf.setDirection(DcMotorSimple.Direction.REVERSE)
        self.lb.setDirection(DcMotorSimple.Direction.REVERSE)

        self.cycle_register = {"MagDump": Cycle()}
        self.InUse = "MagDump"
        self.drive_scale = 1.0
        self.state = "IDLE"
        self.timer = ElapsedTime()

        self.telemetry.addLine("Initialised. Press START.")
        self.telemetry.update()
        self.waitForStart()
        self.timer.reset()
        was_cross = False

        while self.opModeIsActive():
            y = -self.gamepad1.left_stick_y
            x = self.gamepad1.right_stick_x

            self.lf.setPower(y + x)
            self.lb.setPower(y + x)
            self.rf.setPower(y - x)
            self.rb.setPower(y - x)

            cycle = self.cycle_register[self.InUse]
            if self.gamepad1.cross and not was_cross:
                cycle.phase = (cycle.phase + 1) % 3
                cycle.count += 1
                cycle.last_ms = self.timer.milliseconds()
            was_cross = self.gamepad1.cross

            if cycle.phase == 1:
                self.state = "SHOOTING"
                self.shooter.setPower(0.8)
            elif cycle.phase == 2:
                self.state = "DUMPING"
                self.shooter.setPower(0.3)
            else:
                self.state = "IDLE"
                self.shooter.setPower(0.3)

            intake.setPower(self.gamepad1.right_trigger - self.gamepad1.left_trigger)
            if cycle.phase == 2:
                chain_drop.setPosition(0.8)
            else:
                chain_drop.setPosition(0.25)

            if self.gamepad1.triangle:
                colector = self.hardwareMap.get(DcMotor, "Colector")

            self.telemetry.addData("Phase", cycle.phase)
            self.telemetry.addData("Drive", "y %.2f x %.2f" % (y, x))
            self.telemetry.update()
`;

const LINES = MAIN_PY.split('\n');

export function lineOf(snippet: string, nth = 0): number {
  let seen = 0;
  for (let i = 0; i < LINES.length; i++) {
    if (LINES[i].includes(snippet)) {
      if (seen === nth) return i + 1;
      seen++;
    }
  }
  throw new Error('fake source has no line containing ' + snippet);
}

export function linesBetween(from: string, to: string): number[] {
  const a = lineOf(from);
  const b = lineOf(to);
  const out: number[] = [];
  for (let i = a; i <= b; i++) out.push(i);
  return out;
}
