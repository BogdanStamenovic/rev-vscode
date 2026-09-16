# rev-vscode

Write FTC / FIRST Global robot code in Python in VS Code. It gets translated
to Java and compiled on the REV Control Hub by OnBot Java, exactly as if
someone had typed Java into the OnBot Java editor. The hub never finds out.

It exists because the robot only speaks Java and its owner does not want to.

**How to add motors, servos, sensors, gamepad controls and autonomous code: [docs/MANUAL.md](docs/MANUAL.md).**

## What works today

Verified against a real Control Hub (RC app 11.2, SDK 11.2.0) over USB:

- **Deploy** (`▶ Deploy to Hub` in the status bar): translates every `.py` file
  in the workspace, uploads the Java, builds on the hub, and puts javac errors
  on the right line of your *Python* file. Deleting a `.py` removes its Java
  from the hub on the next deploy.
- **Spawn starter pack** (sidebar button): reads the hub's active hardware
  configuration and writes a Python OpMode with a field per device, the
  `hardwareMap` lookups, an init section, and a loop that runs until STOP.
  Every motor, CR servo and servo gets a gamepad control (left/right-named
  motors become arcade drive), listed in a controls table at the top. The
  comments list every device (hub, port, encoder ticks, RPM, whether its hub is
  currently connected) and everything each device type can do, with the SDK's
  own javadoc.
- **Autocomplete**: `from ftc.hardware import DcMotor` etc. resolves to stub
  modules generated from the real SDK sources, so Pylance knows parameter names,
  types and docs. `self.hardwareMap.get(DcMotor, "left")` is typed as `DcMotor`.
- **Show generated Java**: see exactly what goes to the robot.
- **Hub sidebar**: connection (Wi-Fi or USB), RC/SDK/OS versions, hubs and
  firmware, configured devices.

Connection is automatic: `192.168.43.1:8080` if you are on the robot's Wi-Fi,
otherwise an `adb forward` over USB (it finds REV Hardware Client's bundled adb).

## What does not exist yet

- **REV Hardware Client replacement features** (firmware/OS/app updates,
  backups, log viewer). The research is done: its Quarkus backend runs headless
  and its API is mapped (see `docs/ARCHITECTURE.md`). It is not wired into the
  extension, so keep the Hardware Client around for updates.
- **Running OpModes** from VS Code. You still press INIT/START on the Driver Hub.
- **Full Python.** See below; this is Java wearing a Python costume.
- Only **SDK 11.2.0** has a type database. The hub offers 12.0; if you update the
  Robot Controller app, regenerate (`sdkgen`, below) or new APIs won't autocomplete
  or translate.

## The Python you can write

```python
from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor, DcMotorSimple
from ftc.util import Range


@TeleOp(name="Drive", group="pyftc")
class Drive(LinearOpMode):
    left: DcMotor
    MAX_SPEED: float = 0.8          # UPPER_CASE with a value -> static final

    def runOpMode(self) -> None:
        self.left = self.hardwareMap.get(DcMotor, "Motor L")
        self.left.setDirection(DcMotorSimple.Direction.REVERSE)
        self.waitForStart()
        while self.opModeIsActive():
            power = Range.clip(-self.gamepad1.left_stick_y, -1, 1) * self.MAX_SPEED
            self.left.setPower(power)
            self.telemetry.addData("power", f"{power:.2f}")
            self.telemetry.update()
```

Rules, all enforced with an error on the offending line rather than a guess:

- **SDK names stay Java names** (`setPower`, not `set_power`), so every FTC
  sample and forum answer applies as written.
- **Types**: method parameters need annotations; locals are inferred (Java 8 has
  no `var`, so something has to be). A local assigned `0` and later `0.5` becomes
  a `double`. When inference can't tell, you're asked to annotate.
- **Python semantics are kept where Java differs**: `/` on ints is true division,
  `//` and `%` floor like Python, `==` on strings compares contents,
  `xs[-1]` works.
- **Supported**: classes (one superclass, helper classes across files),
  `@staticmethod`, `if/elif/else`, `while`, `for` over `range`/lists/arrays,
  `enumerate`, `try/except/finally`, `raise`, f-strings (including `:.2f`),
  `list[T]`, `dict[K, V]` (empty literal, then index), `math.*`, `abs/min/max/
  round/int/float/str/len/isinstance`, lambdas, keyword arguments (matched to
  the SDK's real parameter names).
- **Not supported**: module-level functions or variables, tuples and unpacking,
  comprehensions, generators, `with`, slices, default arguments, `*args`,
  anything imported except `ftc.*`, `math`, and your own files.
- `float` passed where Java wants `int` is an error, not a silent truncation.
  Wrap it in `int(...)`.
- Comments and blank lines are carried into the Java, so the code on the hub is
  readable if you ever have to fix it in the OnBot Java editor at an event.

## Install

Needs VS Code, Python 3.10+ (stdlib only), and for USB either REV Hardware
Client 2 or `adb` on PATH.

```bash
git clone https://github.com/BogdanStamenovic/rev-vscode && cd rev-vscode/extension
npm ci && npm run package
code --install-extension dist/rev-vscode.vsix
```

Open the folder with your robot code, accept "Enable FTC autocomplete", and use
the REV FTC sidebar.

## FIRST Global rules

The FGC 2026 manual says teams should program in Blocks or OnBot Java, and
support is only given for those. What lands on the hub *is* OnBot Java, so the
robot is in a supported state. Whether the people at the help desk accept
"I wrote it in Python" is not something this tool can settle.

## Layout

| path | what |
|---|---|
| `python/pyftc/` | translator (`translate.py`), type model, starter pack generator, CLI |
| `python/ftc/` | generated stub modules for autocomplete |
| `python/pyftc/data/sdk-11.2.0.json` | generated type database |
| `sdkgen/` | generator: SDK sources jars from Maven Central → the two above |
| `extension/` | VS Code extension (TypeScript) |
| `docs/MANUAL.md` | how to add devices, controls, autonomous; extending the tool |
| `docs/ARCHITECTURE.md` | design, contracts, verified hub protocol |

## Tests

```bash
# translator: runs every test against a hand-written type DB and the real one,
# and compiles every accepted program with javac against the SDK jars
eval "$(scripts/javac-env.sh)"
cd python && uv run --no-project --with pytest pytest -q tests

cd extension
npm test                                   # unit tests
npm run smoke                              # real hub: save/build/error/cleanup
E2E_HUB_URL=http://127.0.0.1:18080 npm run e2e   # real VS Code + real hub
```

The hub tests need a Control Hub attached (`adb forward tcp:18080 tcp:8080` for
the URL above). They leave only the generated starter pack on the hub.

Regenerate for another SDK version:

```bash
cd sdkgen && uv run python -m sdkgen --sdk 11.2.0 --out ../python
```

## License

MIT
