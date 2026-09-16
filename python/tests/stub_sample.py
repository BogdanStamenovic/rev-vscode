from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, IMU, DcMotorSimple
from ftc.util import ElapsedTime


@TeleOp(name="Sample", group="pyftc")
class Sample(LinearOpMode):
    def runOpMode(self) -> None:
        m = self.hardwareMap.get(DcMotor, "Motor L")
        m.setDirection(DcMotorSimple.Direction.REVERSE)
        m.setMode(DcMotor.RunMode.RUN_USING_ENCODER)
        p: int = m.getCurrentPosition()
        self.telemetry.addData("pos", p)
        self.telemetry.update()
        self.waitForStart()
        while self.opModeIsActive():
            m.setPower(-self.gamepad1.left_stick_y)
