from __future__ import annotations

import re

HEAD = """
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorSimple, Servo
from ftc.util import ElapsedTime, Range
import math

@TeleOp(name="T", group="g")
class Robot(LinearOpMode):
    motor: DcMotor
"""


def body(code: str) -> str:
    lines = ["    def runOpMode(self) -> None:"] + ["        " + ln for ln in code.strip("\n").splitlines()]
    return HEAD.strip("\n") + "\n" + "\n".join(lines) + "\n"


def java(result) -> str:
    assert result["files"], result
    return result["files"][0]["java"]


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def errors(result) -> list[str]:
    return [d["message"] for d in result["diagnostics"] if d["severity"] == "error"]


def test_opmode_shell(translate):
    r = translate(body("self.waitForStart()"))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    # Robot.py is the only file in the project, at the root: one Java package
    # per Python file (docs/ARCHITECTURE.md Contract 3), named after the
    # file's own path -- here just "Robot".
    assert "package org.firstinspires.ftc.teamcode.pyftc.Robot;" in j
    assert '@TeleOp(name = "T", group = "g")' in j
    assert "public class Robot extends LinearOpMode {" in j
    assert "import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;" in j
    assert "@Override\n    public void runOpMode() {" in j
    assert r["files"][0]["hubPath"] == "/src/org/firstinspires/ftc/teamcode/pyftc/Robot/Robot.java"
    assert r["files"][0]["package"] == "org.firstinspires.ftc.teamcode.pyftc.Robot"


def test_hardware_map_class_literal_and_generic_return(translate):
    r = translate(body('m = self.hardwareMap.get(DcMotor, "left")\nm.setPower(0.5)'))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert 'DcMotor m = hardwareMap.get(DcMotor.class, "left");' in j
    assert "m.setPower(0.5);" in j


def test_device_mapping_generic_field(translate):
    r = translate(body('m = self.hardwareMap.dcMotor.get("left")\nm.getCurrentPosition()'))
    assert r["ok"], r["diagnostics"]
    assert 'DcMotor m = hardwareMap.dcMotor.get("left");' in java(r)


def test_nested_enum_and_import_of_outer(translate):
    r = translate(body("self.motor.setMode(DcMotor.RunMode.RUN_TO_POSITION)"))
    assert r["ok"], r["diagnostics"]
    assert "motor.setMode(DcMotor.RunMode.RUN_TO_POSITION);" in java(r)


def test_int_division_is_true_division(translate):
    r = translate(body("a = 7\nb = 2\nc = a / b\nd = a // b\ne = a % b\nf = -7.5 % 2"))
    j = java(r)
    assert r["ok"], r["diagnostics"]
    assert "double c = (double) a / b;" in j
    assert "int d = Math.floorDiv(a, b);" in j
    assert "int e = Math.floorMod(a, b);" in j
    assert "double f = ((-7.5 % 2" in j


def test_local_widening_int_then_float(translate):
    r = translate(body("x = 0\nwhile self.opModeIsActive():\n    x = x + 0.5"))
    assert r["ok"], r["diagnostics"]
    assert "double x = 0.0;" in java(r) or "double x = 0;" in java(r)


def test_hoisting_to_smallest_block(translate):
    src = body("""
while self.opModeIsActive():
    if self.gamepad1.a:
        speed = 1.0
    else:
        speed = 0.5
    self.motor.setPower(speed)
""")
    r = translate(src)
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert squash("while (opModeIsActive()) { double speed = 0.0; if (gamepad1.a) {") in squash(j)


def test_block_local_declared_inline(translate):
    r = translate(body("while self.opModeIsActive():\n    p = self.gamepad1.left_stick_y\n    self.motor.setPower(p)"))
    assert r["ok"], r["diagnostics"]
    assert "double p = gamepad1.left_stick_y;" in java(r)


def test_range_loops(translate):
    r = translate(body("for i in range(3):\n    self.sleep(10)\nfor k in range(10, 0, -2):\n    self.sleep(k)"))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert "for (int i = 0; i < 3; i++) {" in j
    assert "for (int k = 10; k > 0; k += -2) {" in j


def test_loop_var_used_after_loop(translate):
    r = translate(body("for i in range(3):\n    pass\nself.sleep(i)"))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert "int i = 0;" in j
    assert re.search(r"for \(int i_\d+ = 0; i_\d+ < 3; i_\d+\+\+\) \{\s+i = i_\d+;", j)


def test_list_ops(translate):
    r = translate(body("xs: list[float] = [1, 2]\nxs.append(3.5)\nxs[0] = 4\nn = len(xs)\nlast = xs[-1]\nfor x in xs:\n    self.motor.setPower(x)"))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert "List<Double> xs = new ArrayList<>(Arrays.asList(1.0, 2.0));" in j
    assert "xs.add(3.5);" in j
    assert "xs.set(0, 4.0);" in j
    assert "int n = xs.size();" in j
    assert "double last = xs.get(xs.size() - 1);" in j
    assert "for (double x : xs) {" in j


def test_fstring_plain_and_formatted(translate):
    r = translate(body('p = self.motor.getCurrentPosition()\nself.telemetry.addLine(f"pos {p}")\n'
                       'self.telemetry.addLine(f"pow {self.motor.getPower():.2f}")'))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert 'telemetry.addLine("pos " + p);' in j
    assert 'telemetry.addLine(String.format("pow %.2f", motor.getPower()));' in j


def test_string_equality_uses_equals(translate):
    r = translate(body('mode = "a"\nif mode == "b":\n    pass\nif mode != "c":\n    pass'))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert 'if (mode.equals("b")) {' in j
    assert 'if (!mode.equals("c")) {' in j


def test_is_none(translate):
    r = translate(body("if self.motor is not None and not self.gamepad1.a:\n    pass"))
    assert r["ok"], r["diagnostics"]
    assert "if (motor != null && !gamepad1.a) {" in java(r)


def test_chained_comparison(translate):
    r = translate(body("x = 0.3\nif 0 < x <= 1:\n    pass"))
    assert "if (0 < x && x <= 1.0) {" in java(r)


def test_keyword_args_mapped_to_java_params(translate):
    r = translate(body("Range.clip(max=1.0, number=0.5, min=0.0)"))
    assert r["ok"], r["diagnostics"]
    assert "Range.clip(0.5, 0.0, 1.0);" in java(r)


def test_overload_by_type(translate):
    r = translate(body("a = Range.clip(5, 0, 3)\nb = Range.clip(0.5, 0.0, 1.0)"))
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert "int a = Range.clip(5, 0, 3);" in j
    assert "double b = Range.clip(0.5, 0.0, 1.0);" in j


def test_float_to_int_param_is_an_error(translate):
    r = translate(body("self.sleep(0.5 * 1000)"))
    assert not r["ok"]
    assert any("int(" in m for m in errors(r))


def test_int_cast_then_ok(translate):
    r = translate(body("self.sleep(int(0.5 * 1000))"))
    assert r["ok"], r["diagnostics"]
    assert "sleep((int) (0.5 * 1000.0));" in java(r) or "sleep((int) (0.5 * 1000));" in java(r)


def test_unknown_method_reported_with_position(translate):
    r = translate(body("self.motor.setPowr(1.0)"))
    assert not r["ok"]
    d = r["diagnostics"][0]
    assert "has no method 'setPowr'" in d["message"]
    assert d["line"] == 10


def test_wrong_arity_lists_signature(translate):
    r = translate(body("self.motor.setPower()"))
    assert any("setPower(power: float)" in m for m in errors(r))


def test_truthiness_rejected(translate):
    r = translate(body("x = 1\nif x:\n    pass"))
    assert any("not bool" in m for m in errors(r))


def test_unsupported_constructs_have_clear_messages(translate):
    r = translate(body("xs = [i for i in range(3)]\na, b = 1, 2"))
    msgs = errors(r)
    assert any("list comprehensions" in m for m in msgs)
    assert any("tuple unpacking" in m for m in msgs)


def test_module_level_function_rejected(translate):
    r = translate("def helper():\n    pass\n")
    assert any("module-level functions" in m for m in errors(r))


def test_disallowed_import(translate):
    r = translate("import numpy\n")
    assert any("numpy" in m for m in errors(r))


def test_while_true_warns_in_linear_opmode(translate):
    r = translate(body("while True:\n    break"))
    assert r["ok"]
    assert any("opModeIsActive" in d["message"] for d in r["diagnostics"] if d["severity"] == "warning")


def test_comments_carried_over(translate):
    src = body("# init section\nself.waitForStart()  # go\n# loop\nwhile self.opModeIsActive():\n    pass")
    r = translate(src)
    j = java(r)
    assert "// init section" in j
    assert "waitForStart(); // go" in j
    assert "// loop" in j


def test_line_map_points_at_python(translate):
    src = body('self.motor.setPower(1.0)')
    r = translate(src)
    f = r["files"][0]
    java_lines = f["java"].splitlines()
    idx = next(i for i, ln in enumerate(java_lines) if "setPower" in ln)
    py_line = f["lineMap"][idx]
    assert src.splitlines()[py_line - 1].strip() == "self.motor.setPower(1.0)"


def test_helper_class_across_files(translate):
    helper = """
from ftc.hardware import DcMotor

class Arm:
    motor: DcMotor
    TICKS: int = 288

    def __init__(self, motor: DcMotor):
        self.motor = motor

    def rotations(self) -> float:
        return self.motor.getCurrentPosition() / self.TICKS
"""
    main = body('arm = Arm(self.hardwareMap.get(DcMotor, "arm"))\nr = arm.rotations()\nself.telemetry.addData("r", r)')
    main = main.replace("import math", "import math\nfrom Arm import Arm")
    r = translate(main, extra={"Arm.py": helper})
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f["java"] for f in r["files"]}
    assert 'Arm arm = new Arm(hardwareMap.get(DcMotor.class, "arm"));' in by_name["Robot"]
    assert "double r = arm.rotations();" in by_name["Robot"]
    assert "public Arm(DcMotor motor) {" in by_name["Arm"]
    assert "this.motor = motor;" in by_name["Arm"]
    assert "static final int TICKS = 288;" in by_name["Arm"]
    assert "return (double) motor.getCurrentPosition() / TICKS;" in by_name["Arm"]


# ---------------------------------------------------------------- one Java package per Python file


def test_two_files_can_each_define_a_class_with_the_same_name(translate):
    """One Java package per Python file (docs/ARCHITECTURE.md Contract 3):
    two unrelated packs can each have their own helper class called `Cycle`
    without colliding, the way they would sharing one flat package."""
    main = """
from ftc.opmode import LinearOpMode, TeleOp

class Cycle:
    count: int = 0

    def tick(self) -> int:
        self.count += 1
        return self.count

@TeleOp(name="T", group="g")
class Robot(LinearOpMode):
    def runOpMode(self) -> None:
        c = Cycle()
        c.tick()
        self.waitForStart()
"""
    shooter = """
class Cycle:
    label: str = "shooter"

    def describe(self) -> str:
        return self.label
"""
    r = translate(main, name="main.py", extra={"shooter.py": shooter})
    assert r["ok"], r["diagnostics"]
    cycles = [f for f in r["files"] if f["className"] == "Cycle"]
    assert len(cycles) == 2
    assert {f["package"] for f in cycles} == {
        "org.firstinspires.ftc.teamcode.pyftc.main",
        "org.firstinspires.ftc.teamcode.pyftc.shooter",
    }
    assert {f["hubPath"] for f in cycles} == {
        "/src/org/firstinspires/ftc/teamcode/pyftc/main/Cycle.java",
        "/src/org/firstinspires/ftc/teamcode/pyftc/shooter/Cycle.java",
    }


def test_cross_file_import_field_and_classvar_access_across_packages(translate):
    """`from shooter import Shooter` used from main.py: an instance field
    access (`self.shooter.motor`) and a ClassVar access
    (`Shooter.ready_count`) both now cross a package boundary, so both need
    to be emitted `public` (see ClassTranslator.run()'s field modifiers) or
    javac would reject them."""
    shooter = """
from typing import ClassVar
from ftc.hardware import DcMotor

class Shooter:
    motor: DcMotor
    ready_count: ClassVar[int] = 0

    def __init__(self, motor: DcMotor):
        self.motor = motor

    def spin(self) -> None:
        self.motor.setPower(1.0)
"""
    main = """
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor
from shooter import Shooter

@TeleOp(name="T", group="g")
class Robot(LinearOpMode):
    shooter: Shooter

    def runOpMode(self) -> None:
        self.shooter = Shooter(self.hardwareMap.get(DcMotor, "shooter"))
        self.waitForStart()
        self.shooter.spin()
        m = self.shooter.motor
        Shooter.ready_count = 1
"""
    r = translate(main, name="main.py", extra={"shooter.py": shooter})
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f for f in r["files"]}
    assert by_name["Robot"]["package"] == "org.firstinspires.ftc.teamcode.pyftc.main"
    assert by_name["Shooter"]["package"] == "org.firstinspires.ftc.teamcode.pyftc.shooter"
    assert "import org.firstinspires.ftc.teamcode.pyftc.shooter.Shooter;" in by_name["Robot"]["java"]
    assert "public DcMotor motor;" in by_name["Shooter"]["java"]
    assert "public static int ready_count = 0;" in by_name["Shooter"]["java"]
    assert "Shooter.ready_count = 1;" in by_name["Robot"]["java"]
    assert "DcMotor m = shooter.motor;" in by_name["Robot"]["java"]


def test_plain_import_of_project_module_then_attribute_access(translate):
    """`import shooter` then `shooter.Shooter(...)` -- the single-segment
    plain-import form, cheap enough to support directly rather than making
    it a blanket error like the dotted form below."""
    shooter = """
from ftc.hardware import DcMotor

class Shooter:
    motor: DcMotor

    def __init__(self, motor: DcMotor):
        self.motor = motor
"""
    main = """
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor
import shooter

@TeleOp(name="T", group="g")
class Robot(LinearOpMode):
    def runOpMode(self) -> None:
        s = shooter.Shooter(self.hardwareMap.get(DcMotor, "shooter"))
        self.waitForStart()
"""
    r = translate(main, name="main.py", extra={"shooter.py": shooter})
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f["java"] for f in r["files"]}
    assert 'Shooter s = new Shooter(hardwareMap.get(DcMotor.class, "shooter"));' in by_name["Robot"]
    assert "import org.firstinspires.ftc.teamcode.pyftc.shooter.Shooter;" in by_name["Robot"]


def test_dotted_plain_import_of_project_module_is_a_clear_error(translate):
    """`import autos.left` only binds the top package (`autos`) in real
    Python; reaching `.left` off it needs package machinery this translator
    does not model. Must be a clear error pointing at the fix, not a guess."""
    left = "class LeftAuto:\n    pass\n"
    main = body("pass")
    main = main.replace("import math", "import math\nimport autos.left")
    r = translate(main, extra={"autos/left.py": left})
    assert not r["ok"]
    msgs = errors(r)
    assert any("import autos.left" in m and "from autos.left import ClassName" in m for m in msgs), msgs


def test_subfolder_module_import(translate):
    """`from autos.left import X`: a helper class in a subfolder, resolved by
    its real (unsanitized) module path -- not by matching the last dotted
    segment against any file with that name, the way the old flat-package
    translator used to."""
    left = """
class LeftAuto:
    STEPS: int = 4
"""
    main = body("n = LeftAuto.STEPS")
    main = main.replace("import math", "import math\nfrom autos.left import LeftAuto")
    r = translate(main, extra={"autos/left.py": left})
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f for f in r["files"]}
    assert by_name["LeftAuto"]["package"] == "org.firstinspires.ftc.teamcode.pyftc.autos.left"
    assert by_name["LeftAuto"]["hubPath"] == "/src/org/firstinspires/ftc/teamcode/pyftc/autos/left/LeftAuto.java"
    assert "int n = LeftAuto.STEPS;" in by_name["Robot"]["java"]


def test_reference_to_other_files_class_without_import_is_a_clear_error(translate):
    """A class in another file that was never imported must not resolve by a
    silent cross-file lookup -- real Python would raise NameError too. This
    must be a translator error on the line that actually uses it."""
    helper = """
class Arm:
    TICKS: int = 288
"""
    main = body("a = Arm()")
    r = translate(main, extra={"Arm.py": helper})
    assert not r["ok"]
    msgs = errors(r)
    assert any("not callable" in m and "Arm" in m for m in msgs), msgs
    used_line = main.splitlines().index("        a = Arm()") + 1
    err = next(d for d in r["diagnostics"] if d["severity"] == "error")
    assert err["line"] == used_line


def test_package_segment_sanitizing(translate):
    """A folder/file name that is not a valid Java identifier still gets a
    package (sanitize_package_segment): invalid characters become '_', a
    segment starting with a digit gets a leading '_', a Java keyword gets a
    trailing '_'."""
    empty = "class {name}:\n    pass\n"
    r = translate(body("self.waitForStart()"), extra={
        "my-pack.py": empty.format(name="LeftHelper"),
        "3wheel.py": empty.format(name="ThreeWheelHelper"),
        "class.py": empty.format(name="ClassHelper"),
    })
    assert r["ok"], r["diagnostics"]
    by_class = {f["className"]: f for f in r["files"]}
    assert by_class["LeftHelper"]["package"] == "org.firstinspires.ftc.teamcode.pyftc.my_pack"
    assert by_class["ThreeWheelHelper"]["package"] == "org.firstinspires.ftc.teamcode.pyftc._3wheel"
    assert by_class["ClassHelper"]["package"] == "org.firstinspires.ftc.teamcode.pyftc.class_"


def test_package_collision_across_sanitized_names_is_an_error(translate):
    """Two files whose names differ only by a character sanitizing erases
    ('my-pack.py' and 'my_pack.py' both become 'my_pack') must not silently
    share a package -- that would merge their classes without warning. It is
    a translator error naming both files."""
    a = "class A:\n    pass\n"
    b = "class B:\n    pass\n"
    r = translate(body("self.waitForStart()"), extra={"my-pack.py": a, "my_pack.py": b})
    assert not r["ok"]
    msgs = errors(r)
    assert any("my-pack.py" in m and "my_pack.py" in m and "same Java package" in m for m in msgs), msgs


def test_self_field_inferred_from_hardware_map(translate):
    src = HEAD.replace("    motor: DcMotor\n", "") + (
        "    def runOpMode(self) -> None:\n"
        '        self.claw = self.hardwareMap.get(Servo, "claw")\n'
        "        self.claw.setPosition(Servo.MAX_POSITION)\n")
    r = translate(src)
    assert r["ok"], r["diagnostics"]
    j = java(r)
    assert "Servo claw;" in j
    assert "claw.setPosition(Servo.MAX_POSITION);" in j


def test_try_except(translate):
    r = translate(body("try:\n    self.sleep(1)\nexcept Exception as e:\n    self.telemetry.addLine(e.getMessage())\nfinally:\n    pass"))
    assert r["ok"], r["diagnostics"]
    assert squash("try { sleep(1); } catch (Exception e) { telemetry.addLine(e.getMessage()); } finally { }") in squash(java(r))


def test_elif_chain(translate):
    r = translate(body("x = 1\nif x == 1:\n    pass\nelif x == 2:\n    pass\nelif x == 3:\n    pass\nelse:\n    pass"))
    assert r["ok"], r["diagnostics"]
    assert squash("if (x == 1) { } else if (x == 2) { } else if (x == 3) { } else { }") in squash(java(r))


def test_enumerate(translate):
    r = translate(body("xs: list[float] = [0.1]\nfor i, x in enumerate(xs):\n    self.sleep(i)"))
    assert r["ok"], r["diagnostics"]
    assert squash("for (int i = 0; i < xs.size(); i++) { double x = xs.get(i);") in squash(java(r))


def test_java_keyword_identifier(translate):
    r = translate(body("new = 1\nself.sleep(new)"))
    assert r["ok"], r["diagnostics"]
    assert "int new_ = 1;" in java(r)


def test_syntax_error_reported(translate):
    r = translate("class X(:\n")
    assert not r["ok"]
    assert "syntax error" in r["diagnostics"][0]["message"]


def test_primitive_boxes_to_object_param(translate):
    r = translate(body('self.telemetry.addData("pressed", self.gamepad1.a)\nself.telemetry.addData("n", 3)'))
    assert r["ok"], r["diagnostics"]
    assert 'telemetry.addData("pressed", gamepad1.a);' in java(r)


def test_nested_class_constructor(translate):
    src = body('p = IMU.Parameters(RevHubOrientationOnRobot(RevHubOrientationOnRobot.LogoFacingDirection.UP, '
               'RevHubOrientationOnRobot.UsbFacingDirection.FORWARD))')
    src = src.replace("import math", "import math\nfrom ftc.hardware import IMU, RevHubOrientationOnRobot")
    r = translate(src)
    if not r["ok"] and any("RevHubOrientationOnRobot" in m for m in errors(r)):
        import pytest
        pytest.skip("fixture DB has no RevHubOrientationOnRobot; covered by the sdk variant")
    assert r["ok"], r["diagnostics"]
    assert "IMU.Parameters p = new IMU.Parameters(new RevHubOrientationOnRobot(" in java(r)


# ---------------------------------------------------------------- ftc.io: saving data across a power cycle

def test_aftercare_writes_settings_file_and_main_reads_it_with_fallback(translate):
    """The real end-to-end recipe from docs/MANUAL.md: an Aftercare OpMode
    writes a settings file after a match, and a Main OpMode reads it back at
    INIT next time, falling back to the class's default field values when the
    file doesn't exist yet (first run, or a fresh hub)."""
    src = """
from ftc.opmode import LinearOpMode, TeleOp, Autonomous
from ftc.io import File, AppUtil, ReadWriteFile

@Autonomous(name="Aftercare", group="pyftc")
class Aftercare(LinearOpMode):
    def runOpMode(self) -> None:
        self.waitForStart()
        f: File = AppUtil.getInstance().getSettingsFile("specs.txt")
        ReadWriteFile.writeFile(f, "1.5,2.5")


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
        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("heading", self.heading)
            self.telemetry.addData("distance", self.distance)
            self.telemetry.update()
"""
    r = translate(src)
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f["java"] for f in r["files"]}
    assert 'File f = AppUtil.getInstance().getSettingsFile("specs.txt");' in by_name["Aftercare"]
    assert 'ReadWriteFile.writeFile(f, "1.5,2.5");' in by_name["Aftercare"]
    assert "import java.io.File;" in by_name["Aftercare"]
    assert "if (f.exists()) {" in by_name["Main"]
    assert 'String[] parts = ReadWriteFile.readFile(f).split(",");' in by_name["Main"]
    assert "heading = Double.parseDouble(parts[0]);" in by_name["Main"]
    assert "distance = Double.parseDouble(parts[1]);" in by_name["Main"]
    assert "double heading = 0.0;" in by_name["Main"]
    assert "double distance = 0.0;" in by_name["Main"]


# ---------------------------------------------------------------- ClassVar: static fields, done deliberately

def test_classvar_static_field_written_by_one_opmode_read_by_another(translate):
    """A field one match's aftercare OpMode writes and the next match's main
    OpMode reads has to be an actual Java `static` field -- Shared.field only
    compiles when Shared declares it that way. ClassVar[...] is how a Python
    OpMode author asks for that."""
    shared = """
from typing import ClassVar

class Shared:
    last_heading: ClassVar[float] = 0.0
"""
    main = """
from ftc.opmode import LinearOpMode, TeleOp, Autonomous
from Shared import Shared

@Autonomous(name="Aftercare", group="pyftc")
class Aftercare(LinearOpMode):
    def runOpMode(self) -> None:
        self.waitForStart()
        Shared.last_heading = 12.0


@TeleOp(name="Main", group="pyftc")
class Main(LinearOpMode):
    def runOpMode(self) -> None:
        self.waitForStart()
        while self.opModeIsActive():
            self.telemetry.addData("heading", Shared.last_heading)
            self.telemetry.update()
"""
    r = translate(main, extra={"Shared.py": shared})
    assert r["ok"], r["diagnostics"]
    by_name = {f["className"]: f["java"] for f in r["files"]}
    assert "static double last_heading = 0.0;" in by_name["Shared"]
    assert "Shared.last_heading = 12.0;" in by_name["Aftercare"]
    assert 'telemetry.addData("heading", Shared.last_heading);' in by_name["Main"]


def test_class_name_access_to_non_classvar_field_is_a_clear_error(translate):
    """Without ClassVar, `last_heading` is an ordinary instance field;
    `Shared.last_heading = ...` translates syntactically but javac would
    reject it ('non-static variable ... cannot be referenced from a static
    context'). This must be a translator diagnostic, not a broken build."""
    shared = """
class Shared:
    last_heading: float = 0.0
"""
    main = body("Shared.last_heading = 12.0")
    main = main.replace("import math", "import math\nfrom Shared import Shared")
    r = translate(main, extra={"Shared.py": shared})
    assert not r["ok"]
    msgs = errors(r)
    assert any("ClassVar" in m and "last_heading" in m for m in msgs), msgs


def test_typing_import_of_unsupported_name_is_rejected(translate):
    """`from typing import ...` used to `continue` unconditionally, silently
    accepting any name (Union, Dict, Protocol, ...) with no effect at
    runtime. Only the names resolve_annotation() actually implements are
    legitimate; anything else must be a diagnostic."""
    r = translate(body("pass").replace("import math", "import math\nfrom typing import Protocol"))
    assert not r["ok"]
    assert any("Protocol" in m and "typing" in m for m in errors(r))


def test_typing_classvar_and_final_still_import_cleanly(translate):
    r = translate(body("pass").replace("import math", "import math\nfrom typing import ClassVar, Optional, Final"))
    assert r["ok"], r["diagnostics"]
