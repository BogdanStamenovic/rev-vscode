# Architecture

Write FTC/FGC robot code in Python inside VS Code; it is translated to Java and
compiled on the Control Hub by OnBot Java, exactly as if it had been typed into
the OnBot Java editor. The hub never knows Python was involved.

```
┌──────────────────────────── VS Code ─────────────────────────────┐
│ extension/ (TypeScript)                                          │
│   HubConnection ── direct http://192.168.43.1:8080 (Wi-Fi)       │
│                └─ adb forward tcp:<free> tcp:8080     (USB)      │
│   Deploy:  pyftc translate-project ─► POST /java/file/save       │
│            ─► GET /java/build/start ─► poll /java/build/status   │
│            ─► GET /java/build/log ─► diagnostics on .py lines    │
│   Starter pack: adb cat /sdcard/FIRST/<active>.xml + rcInfo.json │
│            ─► pyftc starter ─► new .py file in the workspace     │
│   Hub view: rcInfo, hubs, active config devices                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ spawns (stdin/stdout JSON)
┌────────────────────────▼─────────────────────────────────────────┐
│ python/pyftc  translator + starter generator (stdlib only)       │
│ python/ftc    generated stub modules, for autocomplete only      │
│ python/pyftc/data/sdk-<ver>.json   type database                 │
└────────────────────────▲─────────────────────────────────────────┘
                         │ generated offline by
┌────────────────────────┴─────────────────────────────────────────┐
│ sdkgen/  downloads FTC SDK *-sources.jar from Maven Central,     │
│          parses Java 8 with javalang, emits type DB + stubs      │
└──────────────────────────────────────────────────────────────────┘
```

## Why these choices

- **Translate to OnBot Java, don't embed Python.** FGC 2026 manual (after R17):
  teams should use Blocks or OnBot Java; no support otherwise. Generated Java
  stays on the hub, readable and hand-editable if the laptop dies at the event.
- **Generate stubs and type info from the real SDK sources** (Maven publishes
  `-sources.jar` for every FTC artifact). Hand-written stubs rot and lie; these
  carry the real parameter names and javadoc, and one generator run retargets a
  new SDK version.
- **Java names stay Java names.** `motor.setPower(0.5)`, not `set_power`. Every
  FTC doc, sample and forum answer then applies verbatim, and the translator
  needs no renaming table that could drift.
- **Translator in Python** using the stdlib `ast`, so the source is parsed by
  the same grammar that the editor and the user already rely on.

## Verified hub facts (Control Hub, RC 11.2, SDK 11.2.0, checked 2026-09-16)

- OnBot Java HTTP, NanoHTTPD, no auth:
  - `POST /java/file/save?f=/src/<pkg path>/<Name>.java` form body `data=<source>`
  - `POST /java/file/delete` form body `delete=["src/<path>", ...]` (JSON array, no leading slash)
  - `GET /java/file/tree` → `{"src": ["/org/...", ...]}`
  - `GET /java/build/start` → start timestamp (plain number)
  - `GET /java/build/status` → `{completed, running, successful, startTimestamp, timestamp}`.
    Poll until `completed && startTimestamp == <start>`. Do not use `/java/build/wait`;
    it returns immediately while the build is only PENDING.
  - `GET /java/build/log` → lines like `org/.../X.java(11:18): ERROR: cannot find symbol`
    followed by indented continuation lines. Empty on success.
  - Compiler is javac `-source 1.8 -target 1.8`: no `var`, lambdas allowed.
  - Build compiles *everything* under `/src`, so a broken hand-written file breaks our build too.
- `GET /js/rcInfo.json` → `activeConfigName`, `rcVersion`, `sdkVersion`, `deviceName`,
  `revHubNamesAndVersions[]`, … **and `passphrase` (the Wi-Fi password): never log or display it.**
- Hardware config lives at `/sdcard/FIRST/<activeConfigName>.xml`, read via adb. No HTTP endpoint.
- Over USB, adb sees the hub by serial; `adb forward tcp:N tcp:8080` exposes the web server.
  Over Wi-Fi, the hub is `192.168.43.1:8080` and adb is `192.168.43.1:5555`.
- Generated code goes in package `org.firstinspires.ftc.teamcode.pyftc`, path
  `/src/org/firstinspires/ftc/teamcode/pyftc/`. Deploy owns that folder only.

## Contract 1: type database `python/pyftc/data/sdk-<version>.json`

```jsonc
{
  "sdkVersion": "11.2.0",
  "classes": {
    "<FQN, nested with '.', e.g. com.qualcomm.robotcore.hardware.DcMotor.RunMode>": {
      "kind": "class" | "interface" | "enum" | "annotation",
      "simpleName": "RunMode",
      "outer": "com.qualcomm.robotcore.hardware.DcMotor" | null,
      "module": "ftc.hardware" | null,          // python module exporting it (top-level classes only)
      "typeParams": ["T"],
      "extends": ["<FQN type string>"],          // superclass + interfaces, generics kept
      "abstract": false,
      "methods": [{
        "name": "setPower", "static": false, "abstract": false,
        "typeParams": [],                          // e.g. ["T extends com.qualcomm.robotcore.hardware.HardwareDevice"]
        "params": [{"name": "power", "type": "double", "varargs": false}],
        "returns": "void",
        "doc": "first paragraph of javadoc, plain text"
      }],
      "constructors": [{"params": [...], "doc": ""}],
      "fields": [{"name": "MAX_POSITION", "type": "double", "static": true, "final": true, "doc": ""}],
      "enumConstants": ["RUN_WITHOUT_ENCODER", ...],
      "doc": ""
    }
  },
  "xmlTags": {
    "RevRoboticsCoreHexMotor": {
      "javaType": "com.qualcomm.robotcore.hardware.DcMotor",  // the interface a user should hardwareMap.get
      "implClass": "<FQN or null>",
      "category": "motor" | "servo" | "crservo" | "imu" | "i2c" | "analog" | "digital" | "other",
      "displayName": "REV Robotics Core Hex Motor",
      "props": {"ticksPerRev": 288, "maxRPM": 125, "gearing": 72}   // whatever the annotation carries
    }
  }
}
```

Type strings: primitives as-is (`int`, `double`, `boolean`, `void`), arrays `int[]`,
everything else fully qualified with generics (`java.util.List<com.qualcomm...LynxModule>`),
type variables bare (`T`). JDK/Android types resolved via the source file's imports,
falling back to `java.lang.X`.

Only public/protected API. `protected` members are kept because OpMode fields
(`hardwareMap`, `telemetry`, `gamepad1`) are how user code reaches everything.

## Contract 2: Python modules users import

| module          | Java packages                                                                 |
|-----------------|-------------------------------------------------------------------------------|
| `ftc.opmode`    | `com.qualcomm.robotcore.eventloop.opmode`                                     |
| `ftc.hardware`  | `com.qualcomm.robotcore.hardware`, `com.qualcomm.hardware.rev`, `...hardware.lynx`, other `com.qualcomm.hardware.*` |
| `ftc.gamepad`   | re-exports `Gamepad` (lives in hardware)                                      |
| `ftc.telemetry` | `org.firstinspires.ftc.robotcore.external` (Telemetry, Func, …)               |
| `ftc.navigation`| `org.firstinspires.ftc.robotcore.external.navigation`                         |
| `ftc.util`      | `com.qualcomm.robotcore.util`                                                 |
| `ftc.io`        | hand-written: `File` (`java.io.File`, not in any SDK sources jar) and `AppUtil` (`org.firstinspires.ftc.robotcore.internal.system.AppUtil`, narrowed by hand to `getInstance()`/`getSettingsFile(String)` -- see python/pyftc/typedb.py); re-exports `ReadWriteFile` from `ftc.util` |
| `ftc.vision`    | `org.firstinspires.ftc.vision`, `.apriltag`, `.opencv`                        |
| `ftc.lang`      | hand-written: `long`, `short`, `byte`, `char` int aliases and `float32` for Java `float` |
| `ftc.internal`  | no package of its own: catch-all for a class with no row above that a stubbed signature elsewhere still needs to resolve (transitive closure over methods/fields/extends/generic args from the packages above, e.g. `DcMotor.getMotorType() -> MotorConfigurationType`); not meant to be imported from directly |

Every generated stub class has `__java__ = "<FQN>"`; the translator trusts the type DB,
not the stub, but the attribute makes the mapping visible on hover.

## Contract 3: `python -m pyftc` CLI

stdout is JSON only, diagnostics never go to stderr. Exit 0 = ok, 1 = user code errors
(JSON still printed), 2 = usage/internal error (message on stderr).

`python -m pyftc translate-project --root <dir> [--sdk 11.2.0]`
```jsonc
{ "ok": true,
  "files": [{
    "source": "/abs/path/Drive.py",
    "className": "Drive",
    "hubPath": "/src/org/firstinspires/ftc/teamcode/pyftc/Drive.java",
    "java": "package ...",
    "lineMap": [0, 3, 3, 4],        // lineMap[javaLine-1] = python line (1-based), 0 = synthetic
    "diagnostics": [] }],
  "diagnostics": [{"source": "/abs/Drive.py", "line": 12, "col": 4, "endLine": 12, "endCol": 9,
                   "severity": "error" | "warning", "message": "..."}] }
```

`python -m pyftc starter --config <config.xml> --rcinfo <rcInfo.json> --name <ClassName>`
```jsonc
{ "ok": true,
  "python": "<source of the starter OpMode>",
  "fingerprint": "<16 hex chars, see below>",
  "manual": "<markdown reference for this robot>" }
```

`python -m pyftc manual --config <config.xml> --rcinfo <rcInfo.json> --name <ClassName>`
→ `{"ok": true, "markdown": "...", "fingerprint": "..."}`
Regenerates only the man page, for a file whose starter pack already exists.

`python -m pyftc config-fingerprint --config <config.xml>`
→ `{"ok": true, "fingerprint": "..."}`
Cheap enough to run on every hub refresh; it never parses the SDK type database.

`python -m pyftc starter-update --file <existing.py> --config <config.xml> --rcinfo <rcInfo.json>`
```jsonc
{ "ok": true,
  "changed": true,              // false when the fingerprint already matches
  "applied": true,              // false when the file's markers are gone: nothing was rewritten
  "fingerprint": "...",
  "python": "<the whole updated file>",   // only when applied
  "block": "<the new code, for pasting>", // only when applied is false
  "manual": "<regenerated markdown>",
  "added":   [{"name": "arm", "field": "arm", "type": "DcMotor",
               "control": "gamepad 1: hold Y forward, hold A reverse"}],
  "removed": [{"name": "old", "field": "old"}],
  "hubsAdded": [{"name": "Expansion Hub 2", "address": "3"}],
  "notes": ["..."] }
```

### Fingerprint

`sha256` over a canonical JSON array of the configuration's hubs and devices —
each device as `[name, tag, port, bus, hub, hubAddress, javaType]`, hubs as
`[name, address]`, both sorted — truncated to 16 hex characters. It covers
exactly what changes the generated code: renames, added and removed devices,
port moves and new expansion hubs. It deliberately ignores rcInfo (firmware
versions, which hub answered) so a robot that is merely unplugged does not
look like a configuration change.

## Contract 4: markers in a generated starter pack

`starter-update` never parses the user's code. It finds these comment lines,
appends inside them, and leaves every other line untouched:

```python
# ── pyftc:config name="Galerija" fingerprint="9f2c1ab30c4d5e6f" generated="2026-09-20" ──
# ── pyftc:imports ──            … # ── pyftc:imports:end ──
# ── pyftc:hardware ──           … # ── pyftc:hardware:end ──   (the comment block)
    # ── pyftc:devices ──        … # ── pyftc:devices:end ──    (class body: fields)
        # ── pyftc:init ──       … # ── pyftc:init:end ──       (hardwareMap lookups)
            # ── pyftc:loop ──   … # ── pyftc:loop:end ──       (control code)
```

Rules, so the update can never eat someone's work:

- New code is inserted immediately **before** the matching `:end` marker, at
  that marker's indentation.
- Nothing between the markers is rewritten or deleted, including lines the user
  edited. A device that left the configuration gets a `# pyftc: no longer in the
  configuration` comment above its field, never a deletion.
- Only the `fingerprint=` and `generated=` values on the config line are edited.
- If any marker is missing, the update refuses to touch the file, returns
  `applied: false`, and hands back the code as `block` for the user to place.

## The simulator

Runs the **exact Java the translator deploys** (plus same-line trace hooks, see
below) against simulated hardware, so a motor that turns the wrong way, a phase
machine that never advances, or an exception on a misspelled device name shows up
at the desk instead of on the robot.

```
┌──────────── VS Code ─────────────────────────────────────────────────────────┐
│ webview (three.js bench, Driver Hub, gamepads, code trace)                    │
│      ▲ postMessage (UI messages + Contract 5 relayed)                         │
│ extension/src/sim: panel.ts ─ session.ts ─ jdk.ts ─ controllers.ts            │
│   pyftc sim-prepare ──► translate (--sim-trace) ─► javac --release 8 -g       │
│                         against api.jar ─► manifest.json                      │
│   java org.pyftc.sim.Main (NDJSON on stdio, Contract 5, JDWP agent on)        │
│   python -m pyftc gamepad (evdev controllers)   debug adapter (JDI, DAP)      │
└───────────────────────────────────────────────────────────────────────────────┘
```

### How the SDK is simulated

- **Real SDK classes wherever they run off Android.** HardwareMap, DcMotorImpl(Ex),
  ServoImpl(Ex), CRServoImpl(Ex), DigitalChannelImpl, AnalogInput, RevTouchSensor,
  Gamepad (its own serialisation, button aliases and edge detection), TelemetryImpl
  (its 250 ms transmit throttle), LastKnown, Range, the navigation types,
  QuaternionBasedImuHelper, RevHubOrientationOnRobot and the motor type annotations
  are the classes from the RobotCore/Hardware 11.2.0 jars on Maven Central.
- **Simulated Lynx controllers** under them: `SimDcMotorController`,
  `SimServoController`, `SimDigitalController`, `SimAnalogController` are ports of
  the SDK's `Lynx*Controller` classes (caching, clipping, int power quantisation,
  mode changes, TargetPositionNotSetException, interrupted-thread behaviour kept
  line for line); where the SDK sends a Lynx command they charge its bus time and
  set the simulated hub. This is the layer where the real SDK talks to hardware.
- **Stand-ins (same FQN, same public API) only where the real class cannot run**:
  OpModeInternal/OpMode/LinearOpMode (ported; clock and thread handling),
  ElapsedTime (ported; reads sim time), RobotLog, AppUtil (settings files under
  `.pyftc/sim-files/FIRST`), ConfigurationTypeManager, Device, OpModeManagerImpl
  (only ForceStopException and updateTelemetryNow), the I2C drivers
  Rev2mDistanceSensor, RevColorSensorV3 (the real driver's arithmetic),
  BHI260IMU / LynxEmbeddedBNO055IMUNew (feeding the real IMU helper), and
  `android.opengl.Matrix` / `android.graphics.Color` in pure Java.
- **Compile-time allow list.** User code is compiled against `api.jar`: the stand-ins
  plus real classes whose bytecode reaches neither Android nor the wall clock
  (checked from each class file's constant pool, then loaded in a JVM sweep). A
  class outside it fails the simulator build on the Python line, naming the class;
  it is never run against something that silently differs from the robot. The list
  is generated (below).
- **Deterministic lockstep time** (`SimClock`): the OpMode thread and the scheduler
  never run at once. Each SDK call costs sim time (a Lynx command 2 or 3 ms, other
  calls a small CPU cost); when the OpMode gets ahead of physics it parks, physics
  steps at 1 ms until it catches up, and hands back. The result depends only on the
  calls made, not on the host's speed. A loop that makes no SDK call at all cannot
  be paced; after a wall-clock timeout physics runs on and a warning names the line.
- **STOP follows the RC**: interrupt, 900 ms, then hardware access throws
  ForceStopException ("User OpMode was stuck in stop(), but was able to be force
  stopped…"); if the thread is still alive 100 ms later the simulator process
  restarts, as the RC app does. After an OpMode ends the SDK's DefaultOpMode zeroes
  every motor and the hub failsafe cuts all outputs 100 ms later.
- **Trace build** (`ProjectTranslator(sim_trace=True)`, only via `sim-prepare`):
  every statement gets a same-line `Trace.l(file, line);` prefix and every local
  assignment a same-line `Trace.a(...)` suffix, so lineMap is identical to the robot
  build; the hooks charge no time. `tests/test_sim.py` runs a scripted session on
  both builds and requires identical output.
- **Debugger**: the sim JVM always has a localhost JDWP agent (`quiet=y`). The
  `revftc-sim` debug type's adapter (`python/pyftc/sim/java/debug`, compiled
  separately against `jdk.jdi`) attaches with JDI; breakpoints, stepping (by Python
  line), call stack, locals, `self` fields and watch expressions are in Python
  files, lines and names. While the OpMode thread is stopped the adapter sets
  `Scheduler.debuggerHold`, so sim time and the motors freeze.

## Contract 5: simulator process protocol

`java -cp <runtime.jar>:<classes>:<RobotCore.jar>:<Hardware.jar>:<gson, gson-extras> org.pyftc.sim.Main
--manifest manifest.json --constants constants.json [--layout sim-layout.json]
[--fast] [--emit-ms N] [--script cmds.jsonl] [--until SEC] [--record out.jsonl]`

stdin/stdout, one JSON object per line. stdout is the protocol only (System.out
is redirected to stderr). `--fast` runs unpaced (headless tests); without it sim
time is paced to the wall clock times `speed`.

Units and frames: metres, degrees (radians where a field says `Rad`), sim time
`t` in seconds. Scene frame is three.js's: +Y up, robot forward -Z, right +X.
Every actuator's local +Z is its output shaft; `omegaRadS > 0` / `spin: "CCW"` is
counter-clockwise **looking at the shaft face**.

**Commands (extension → sim)**, any may carry `"at": <sim seconds>`:

| type | fields | |
|---|---|---|
| `init` | `opMode` | construct the OpMode (field initialisers run now, as on the RC) and start its thread |
| `start` / `stop` | | START / STOP |
| `gamepad` | `index` 1\|2, `gamepadType` (`LOGITECH_F310`, `XBOX_360`, `SONY_PS4`, `UNKNOWN`), `state` | SDK field names; sticks -1..1 with up = -1, triggers 0..1, buttons `a b x y dpad_* guide start back left_bumper right_bumper left_stick_button right_stick_button touchpad`. PlayStation names are not sent: the SDK derives cross/circle/square/triangle itself |
| `sensor` | `device`, `value` | `{pressed}` touch, `{state}` digital, `{volts}` analog, `{angleDeg}` potentiometer, `{mm: n\|null}` distance, `{r,g,b,distanceMm}` colour |
| `layout` | `layout` (Contract 6) | hub pose (IMU), UltraPlanetary stack, loads, servo range, sensor overrides |
| `pause` / `resume` / `speed {factor}` / `quit` | | |

**Events (sim → extension)**:

- `ready`: `protocol`, `sdkVersion`, `opModes[{name, group, kind, className, source}]`,
  `devices[{name, kind, tag, hub, port, bus, motor{orientation, ticksPerRev, gearRatio,
  freeSpeedRpm, cartridges, sdkTicksPerRev, sdkMaxRPM, specVerified, note}, servo{rangeDeg, continuous}}]`,
  `hubs[]`, `config{name, source}`, `notSimulated[]`, `trace`. Device kinds: `motor`,
  `crservo`, `servo`, `touch`, `digital`, `analog`, `potentiometer`, `distance`, `color`,
  `imu`, `voltage`, `unsupported`.
- `state` (about 30/s): `t`, `phase` (`idle init running stopping stopped crashed`),
  `opMode`, `loopMs`, `paused`, `debuggerHold`, `devices{name: …}` (motor: `power` as
  `getPower()` would return it, `direction`, `orientation`, `reversed` (direction and
  motor type combined), `applied`, `spin`, `omegaRadS`, `rpm`, `angleRad`, `mode`,
  `zeroPower`, `enabled`, `position`, `target`, `busy`, `velocity`, `currentA`; servo:
  `position`, `direction`, `reversed`, `pwmUs`, `angleDeg`, `targetAngleDeg`, `rangeDeg`,
  `enabled`; crservo: `power`, `spin`, `omegaRadS`, `angleRad`, `pwmUs`; sensors their
  readings; hubs `voltage`), `gamepads[2]`, `events[]` (each changed device command,
  input change and phase change: `t`, `dev`, `op`, `v`, `py{file,line}`; motor powers
  also carry `hub`, the value after the direction was applied).
- `trace` (with every `state`): `lines{file: [python lines run in the last complete
  loop iteration]}`, `changed[{name, value, file, line}]`, `locals{"Class.method": {name: value}}`,
  `fields` (the OpMode's own fields, by reflection; devices as `{"@device": name}`).
- `telemetry`: `lines` exactly as the Driver Hub would get them (after the SDK's throttle).
- `exception`: `exception`, `message`, `phase`, `py{file,line}` (top user frame), `frames[]`,
  `driverHub` (the first 15 lines of the stack trace, as the RC sends it), `hint`.
- `warning`: `code` (`double-write`, `stuck-stop`, `no-sdk-calls`, `returned-early`,
  `not-simulated`), `message`, `py`, `related[]`.
- `log {level, message}`; `fatal {message, restart?}` then exit (3 = restart requested).

**UI messages (webview ↔ extension)**, besides `{type:"sim", msg}` relaying both ways:
webview → `ready`, `env {gamepadApi, detail, featurePolicyGamepad}`, `layoutChanged`,
`openSource {file,line}`, `rebuild`, `debug`, `openGamepadBridge`; extension →
`hello {layout}`, `status {state, message}`, `compileErrors[]`, `sources {file: text}`,
`bridgeGamepad {index, gamepadType, state, deviceName}`, `systemGamepads {devices, error}`,
`bridgeInfo {url}`.

## Contract 6: scene layout `.pyftc/sim-layout.json`

```jsonc
{
  "version": 1,
  "hubs": {"Control Hub": {"position": [0, 0.05, 0], "rotation": [0, 0, 0]}},
  "devices": {
    "<configured name>": {
      "position": [x, y, z], "rotation": [rx, ry, rz],     // metres; degrees, three.js XYZ Euler
      "motor": {"cartridges": ["4:1", "5:1"], "load": "free" | "wheel" | "arm"},
      "servo": {"rangeDeg": 270},
      "sensor": {"override": <sensor value>, "potentiometer": true}
    }
  },
  "obstacles": [{"kind": "box", "position": [..], "size": [..], "color": "#3060ff"}],
  "camera": {"position": [..], "target": [..]}
}
```

The hub model's reference pose is the SDK's (`RevHubOrientationOnRobot` logo UP, USB
FORWARD): REV logo on its +Y face, USB ports on its -Z face. Rotating the hub in the
scene is what the IMU measures. Unknown keys are preserved.

## FGC 2026 kit coverage

From `FGC2026_Kit_Bill_of_Materials.pdf` (REV-45-3691), every electronic part:

| part | qty | SDK config tag / type | simulator |
|---|---|---|---|
| Control Hub REV-31-1595 | 1 | LynxModule address 173; `ControlHubImuBHI260AP` (IMU) | full: 4 motor, 6 servo, 8 digital, 4 analog ports, IMU from the hub pose, battery voltage |
| Expansion Hub REV-31-1153 | 1 | LynxModule | full (3 ms per command instead of 2) |
| UltraPlanetary Gearbox Kit & HD Hex Motor REV-41-1600 | 7 | `RevRoboticsUltraplanetaryHDHexMotor` / DcMotor(Ex) | full; published motor curve, actual cartridge ratios (stack set per motor) |
| Core Hex Motor REV-41-1300 | 3 | `RevRoboticsCoreHexMotor` / DcMotor(Ex) | full; no-load current not published (placeholder 0) |
| Smart Robot Servo V2 REV-41-3334 | 6 | `Servo`, `ServoFullRange`, `ContinuousRotationServo` | full: 270° over 500–2500 µs, 0.14 s/60°; continuous-mode speed and turning sense are placeholders |
| SRS Programmer REV-31-1108 | 1 | none (sets the servo's mode) | choose the config tag (Servo vs ContinuousRotationServo) |
| Touch Sensor REV-31-1425 | 2 | `RevTouchSensor` / TouchSensor, or `DigitalDevice` | full (active low) |
| Magnetic Limit Switch REV-31-1462 | 2 | `DigitalDevice` / DigitalChannel | full (active low, clickable) |
| Potentiometer REV-31-1155 | 1 | `AnalogInput` | partial: 270° linear to 3.3 V is a placeholder curve |
| 2m Distance Sensor REV-31-1505 | 1 | `REV_VL53L0X_RANGE_SENSOR` / DistanceSensor | partial: scene raycast or override; out-of-range reading is a placeholder (8190 mm) |
| Color Sensor V3 REV-31-1557 | 2 | `RevColorSensorV3` / ColorSensor, NormalizedColorSensor, DistanceSensor | partial: the driver's own maths and proximity curve; absolute raw counts are a placeholder brightness model |
| 12V Slim Battery REV-31-1302 | 2 | VoltageSensor (per hub) | nominal 12.0 V, no sag |
| REV USB PS4 Compatible Gamepad REV-31-2983 | 2 | Gamepad `SONY_PS4` | full: webview Gamepad API, evdev reader, bridge page, keyboard |
| Driver Hub REV-31-1596 | 1 | – | the panel's Driver Hub (INIT/START/STOP, telemetry, errors) |
| Logitech C270 camera REV-39-1598 | 1 | Webcam / VisionPortal | **not simulated** (vision classes fail the simulator build) |
| Ultra 90 Degree Gearbox REV-41-2080 | 2 | – (mechanical, 1:1) | not modelled (1:1 does not change speed; the turned axis is just placement) |

Mechanical parts (gears, sprockets, wheels, extrusion…) are not simulated in v1.

<!-- sim-generated:begin (python -m pyftc.sim.docgen) -->

### Physical constants

| constant | value | unit | verified | source |
|---|---|---|---|---|
| `battery.nominalVoltage` | 12.0 | V | yes | https://www.revrobotics.com/rev-31-1302/ (REV-31-1302 12V Slim Battery: "12V", 3000 mAh NiMH) — A charged NiMH pack reads above nominal; the simulator holds the nominal value and models no sag. |
| `hdHex.voltage` | 12.0 | V | yes | https://www.revrobotics.com/rev-41-1291/ ("12V DC") |
| `hdHex.freeSpeed` | 6000 | rpm (motor shaft) | yes | https://www.revrobotics.com/rev-41-1291/ ; https://docs.revrobotics.com/duo-build/motion/motors/hd-hex-motor ("6000 rpm") |
| `hdHex.stallTorque` | 0.105 | N·m (motor shaft) | yes | https://www.revrobotics.com/rev-41-1291/ ("0.105 Nm") |
| `hdHex.stallCurrent` | 8.5 | A | yes | https://www.revrobotics.com/rev-41-1291/ ("8.5A") |
| `hdHex.freeCurrent` | 0.4 | A | yes | https://www.revrobotics.com/rev-41-1291/ ("400mA" no-load current) |
| `hdHex.countsPerMotorRev` | 28 | counts/rev | yes | https://docs.revrobotics.com/duo-build/motion/motors/hd-hex-motor ("At the motor - 28 counts/revolution") |
| `hdHex.rotorInertia` | 5e-06 | kg·m² (motor shaft) | **no, placeholder** | placeholder: REV publishes no rotor inertia; only affects how fast a free shaft spins up |
| `ultraPlanetary.cartridge3` | 2.89 | :1 | yes | https://www.revrobotics.com/rev-41-1601/ ("Actual Gear Ratio: 2.89:1"); REV-41-1600-UM-02 p.11 |
| `ultraPlanetary.cartridge4` | 3.61 | :1 | yes | https://www.revrobotics.com/rev-41-1602/ ("Actual Gear Ratio: 3.61:1"); REV-41-1600-UM-02 p.11 |
| `ultraPlanetary.cartridge5` | 5.23 | :1 | yes | https://www.revrobotics.com/rev-41-1603/ ("Actual Gear Ratio: 5.23:1"); REV-41-1600-UM-02 p.11 |
| `ultraPlanetary.defaultStack` | 2 | stages (4:1 + 5:1, nominal 20:1) | **no, placeholder** | placeholder: the SDK's UltraPlanetary motor type assumes nominal 20:1 (@MotorType gearing=20); the real stack is whatever the team built, set it per motor in the simulator |
| `ultraPlanetary.efficiency` | 1.0 | fraction | **no, placeholder** | placeholder: REV publishes no UltraPlanetary efficiency |
| `ultra90.ratio` | 1.0 | :1 | yes | https://www.revrobotics.com/rev-41-2080/ ("Gear Ratio: 1:1") |
| `coreHex.voltage` | 12.0 | V | yes | https://www.revrobotics.com/rev-41-1300/ ("12V DC") |
| `coreHex.gearRatio` | 72 | :1 | yes | https://www.revrobotics.com/rev-41-1300/ ("72:1") — The SDK's @MotorType for Core Hex says gearing=36.25, maxRPM=137; REV's product page says 72:1, 125 rpm. The simulator uses REV's numbers for physics and the SDK's for the SDK's own ticks-per-second scaling. |
| `coreHex.freeSpeed` | 125 | rpm (output) | yes | https://www.revrobotics.com/rev-41-1300/ ("125 RPM") |
| `coreHex.stallTorque` | 3.2 | N·m (output) | yes | https://www.revrobotics.com/rev-41-1300/ ("3.2 N-m") |
| `coreHex.stallCurrent` | 4.4 | A | yes | https://www.revrobotics.com/rev-41-1300/ ("4.4 A") |
| `coreHex.freeCurrent` | 0.0 | A | **no, placeholder** | NOT FOUND: REV does not publish the Core Hex no-load current; 0 means no friction is modelled |
| `coreHex.countsPerMotorRev` | 4 | counts/rev | yes | https://docs.revrobotics.com/duo-build/motion/motors/core-hex-motor ("At the motor - 4 counts/revolution"; 288 at the output) |
| `coreHex.rotorInertia` | 2e-06 | kg·m² (motor shaft) | **no, placeholder** | placeholder: not published |
| `genericMotor.stallTorqueAtOutputPerRatio` | 0.105 | N·m per unit gear ratio | **no, placeholder** | placeholder for motor types that are not in the FGC kit (NeveRest, goBILDA, Tetrix...): free speed and gearing come from the SDK's @MotorType annotation, torque is this placeholder times the gearing |
| `loads.freeShaftInertia` | 2e-05 | kg·m² (output) | **no, placeholder** | placeholder: hex shaft + hub + gear on an otherwise free output |
| `loads.robotMass` | 12.0 | kg | **no, placeholder** | placeholder: bench approximation of the robot mass shared by the drive wheels; only sets how fast drive wheels spin up |
| `loads.armInertia` | 0.02 | kg·m² (output) | **no, placeholder** | placeholder for an arm-type load |
| `srs.rangeDeg` | 270 | deg over 500..2500 µs | yes | https://docs.revrobotics.com/rev-crossover-products/servo/smart-robot-servo-v2 ("The default range for the SRS V2 is 270°. This range is mapped to an input pulse range of 500μs to 2500μs with 1500μs as the center point.") |
| `srs.pulseMinUs` | 500 | µs | yes | same page as rangeDeg |
| `srs.pulseMaxUs` | 2500 | µs | yes | same page as rangeDeg |
| `srs.speedSecPer60Deg` | 0.14 | s/60° at 6 V | yes | https://www.revrobotics.com/Smart-servo-v2 ("Speed: 0.14 sec/60°") |
| `srs.continuousFreeSpeed` | 71.4 | rpm at full pulse | **no, placeholder** | placeholder: REV publishes no continuous-mode speed; this is the angular-mode slew rate (60°/0.14 s) reused |
| `srs.pulseIncreasesCounterClockwise` | 1 | 1 = a longer pulse turns the output CCW seen from the spline | **no, placeholder** | placeholder: REV does not document which way the SRS turns for a longer pulse; the servo arc labels 0 and 1 so the relative motion is still right |
| `sdkServo.defaultPulseLowerUs` | 600 | µs | yes | FTC SDK 11.2.0 PwmControl.PwmRange.usPulseLowerDefault = 600 (RobotCore-11.2.0-sources.jar) |
| `sdkServo.defaultPulseUpperUs` | 2400 | µs | yes | FTC SDK 11.2.0 PwmControl.PwmRange.usPulseUpperDefault = 2400 (RobotCore-11.2.0-sources.jar) — With the default 'Servo' configuration type, positions 0..1 drive 600..2400 µs, i.e. 243° of an SRS's 270°; 'ServoFullRange' uses 500..2500. |
| `distance2m.minMm` | 50 | mm | yes | https://docs.revrobotics.com/rev-crossover-products/sensors/2m-distance/specs ("Measurement Range \| 5 \| - \| 200 \| cm") |
| `distance2m.maxMm` | 2000 | mm | yes | same page |
| `distance2m.outOfRangeMm` | 8190 | mm | **no, placeholder** | placeholder: what the VL53L0X reports with nothing in range is not documented by REV or the FTC SDK (the SDK only passes the chip's reading through: VL53L0X.getDistance); 8190 is the commonly reported chip value |
| `colorV3.proximityMaxMm` | 100 | mm | yes | https://docs.revrobotics.com/rev-crossover-products/sensors/color-sensor/specs ("Proximity Sensor Range \| 1 \| - \| 10 \| cm") |
| `colorV3.countsWhiteAt10mm` | 2000 | raw green counts | **no, placeholder** | placeholder: raw colour counts depend on gain, integration time and the target; REV publishes no reference. Thresholds on raw red()/green()/blue() will differ from the real sensor. |
| `potentiometer.rangeDeg` | 270 | deg | yes | https://docs.revrobotics.com/rev-crossover-products/sensors/potentiometer/specifications ("Range of Motion \| 270°") |
| `potentiometer.maxVolts` | 3.3 | V at full rotation | **no, placeholder** | placeholder: linear 0..3.3 V over 270° assumed; REV states the hub reads 0-5 V and the SDK's getMaxVoltage() is 3.3, but gives no output curve for the potentiometer |
| `lynx.commandMsControlHub` | 2.0 | ms per Lynx command | **no, placeholder** | gm0.org (community, not REV): https://gm0.org/en/latest/docs/software/adv-control-system/sdk-communication.html "approximately 2 milliseconds over UART" |
| `lynx.commandMsExpansionHub` | 3.0 | ms per Lynx command | **no, placeholder** | gm0.org (community, not REV): same page, "approximately 3 milliseconds over USB"; an RS485-linked Expansion Hub is assumed to cost the same |
| `lynx.i2cMs` | 7.0 | ms per I2C read | **no, placeholder** | gm0.org (community, not REV): same page, "upwards of 7 milliseconds over USB" |
| `lynx.targetPositionTolerance` | 5 | ticks | yes | FTC SDK 11.2.0 LynxConstants.DEFAULT_TARGET_POSITION_TOLERANCE = 5 |
| `lynx.failsafeDelayMs` | 100 | ms | yes | FTC SDK 11.2.0 OpModeManagerImpl.DefaultOpMode SAFE_WAIT_NANOS = 100 ms (motors set to 0 at stop, hub failsafe after) |
| `firmware.velocityLoopKp` | 0.0005 | power per (tick/s) of error | **no, placeholder** | approximation: the hub firmware's velocity PIDF is closed source; RUN_USING_ENCODER / RUN_TO_POSITION speeds are approximate |
| `firmware.positionLoopGain` | 5.0 | (tick/s) per tick of error | **no, placeholder** | approximation of the hub firmware's position loop (closed source) |
| `sim.sdkCallCostUs` | 20 | µs of sim time per SDK call that does not reach a hub | **no, placeholder** | placeholder for the Control Hub CPU time of an SDK call; sets loop time when a loop sends no hub commands |
| `sim.stepMs` | 1 | ms | yes | simulator design: fixed physics step |

### What is simulated

**Classes user code can use in the simulator** (anything else fails to compile there, naming the class):

- interface/enum/annotation (no behaviour) (117): `GoBILDA5201Series`, `GoBILDA5202Series`, `Matrix12vMotor`, `NeveRest20Gearmotor`, `NeveRest3_7GearmotorV1`, `NeveRest40Gearmotor`, `NeveRest60Gearmotor`, `RevRobotics20HdHexMotor`, `RevRobotics40HdHexMotor`, `RevRoboticsCoreHexMotor`, `RevRoboticsHdHexMotor`, `RevRoboticsUltraPlanetaryHdHexMotor`, `StudicaMaverickMotor`, `TetrixMotor`, `Autonomous`, `Disabled`, `TeleOp`, `AccelerationSensor`, `AnalogInputController`, `AnalogSensor`, `Blinker`, `CRServo`, `ColorRangeSensor`, `ColorSensor`, `CompassSensor`, `ControlSystem`, `DcMotor`, `DcMotorController`, `DcMotorControllerEx`, `DcMotorEx`, `DcMotorSimple`, `DeviceManager`, `DigitalChannel`, `DigitalChannelController`, `DistanceSensor`, `Engagable`, `GyroSensor`, `Gyroscope`, `HardwareDevice`, `HardwareDeviceCloseOnTearDown`, `HardwareDeviceHealth`, `I2cAddrConfig`, `I2cAddressableDevice`, `I2cDevice`, `I2cDeviceSynch`, `I2cDeviceSynchReadHistory`, `I2cDeviceSynchSimple`, `I2cWaitControl`, `IMU`, `ImuOrientationOnRobot`, `IntegratingGyroscope`, `IrSeekerSensor`, `Light`, `LightSensor`, `LynxModuleImuType`, `MotorControlAlgorithm`, `NormalizedColorSensor`, `OpticalDistanceSensor`, `OrientationSensor`, `PWMOutput`, `PWMOutputController`, `PWMOutputControllerEx`, `PWMOutputEx`, `PwmControl`, `RobotConfigNameable`, `RobotCoreLynxController`, `RobotCoreLynxModule`, `RobotCoreLynxUsbDevice`, `Servo`, `ServoController`, `ServoControllerEx`, `SwitchableLight`, `TouchSensor`, `TouchSensorMultiplexer`, `UltrasonicSensor`, `VisuallyIdentifiableHardwareDevice`, `VoltageSensor`, `GlobalWarningSource`, `SortOrder`, `WebHandlerManager`, `WebServer`, `Const`, `Consumer`, `Event`, `ExportAprilTagLibraryToBlocks`, `ExportClassToBlocks`, `ExportEnumToBlocks`, `ExportToBlocks`, `Func`, `Function`, `NonConst`, `Predicate`, `State`, `Supplier`, `Telemetry`, `ThrowingCallable`, `Consumer`, `ContinuationResult`, `Function`, `InterruptableThrowingCallable`, `InterruptableThrowingRunnable`, `InterruptableThrowingSupplier`, `Predicate`, `Supplier`, `ThrowingCallable`, `ThrowingRunnable`, `ThrowingSupplier`, `AngleUnit`, `AxesOrder`, `AxesReference`, `Axis`, `CurrentUnit`, `DistanceUnit`, `Rotation`, `TempUnit`, `UnnormalizedAngleUnit`, `VoltageUnit`
- real SDK class (82): `RevHubOrientationOnRobot`, `RevImuOrientationOnRobot`, `RevTouchSensor`, `DuplicateNameException`, `RobotCoreException`, `RobotProtocolException`, `TargetPositionNotSetException`, `AnalogInput`, `CRServoImpl`, `CRServoImplEx`, `DcMotorImpl`, `DcMotorImplEx`, `DigitalChannelImpl`, `EmbeddedControlHubModule`, `Gamepad`, `GamepadStateChanges`, `HardwareDeviceHealthImpl`, `HardwareMap`, `I2cAddr`, `I2cDeviceSynchDevice`, `I2cDeviceSynchDeviceWithParameters`, `I2cDeviceSynchImplOnSimple`, `I2cDeviceSynchReadHistoryImpl`, `LightMultiplexor`, `LynxModuleDescription`, `LynxModuleMeta`, `LynxModuleMetaList`, `NormalizedRGBA`, `PIDCoefficients`, `PIDFCoefficients`, `PWMOutputImplEx`, `QuaternionBasedImuHelper`, `ServoImpl`, `ServoImplEx`, `TimestampedData`, `InstantiableUserConfigurationType`, `MotorConfigurationType`, `ServoConfigurationType`, `UserConfigurationType`, `TelemetryMessage`, `AndroidSerialNumberNotFoundException`, `DifferentialControlLoopCoefficients`, `Intents`, `LastKnown`, `MovingStatistics`, `Network`, `NextLock`, `Range`, `ReadWriteFile`, `RollingAverage`, `RunShellCommand`, `SerialNumber`, `Statistics`, `TypeConversion`, `Version`, `WeakReferenceSet`, `BlocksOpModeCompanion`, `ClassFactory`, `StateMachine`, `StateTransition`, `ColumnMajorMatrixF`, `ColumnMatrixF`, `DenseMatrixF`, `GeneralMatrixF`, `MatrixF`, `OpenGLMatrix`, `RowMajorMatrixF`, `RowMatrixF`, `SliceMatrixF`, `VectorF`, `Acceleration`, `AngularVelocity`, `MagneticFlux`, `NavUtil`, `Orientation`, `Pose2D`, `Pose3D`, `Position`, `Quaternion`, `Temperature`, `Velocity`, `YawPitchRollAngles`
- simulator stand-in (same API, simulated hardware) (11): `BHI260IMU`, `LynxEmbeddedBNO055IMUNew`, `Rev2mDistanceSensor`, `RevColorSensorV3`, `LinearOpMode`, `OpMode`, `OpModeInternal`, `OpModeManagerImpl`, `ElapsedTime`, `RobotLog`, `AppUtil`
- supertype of an API class (5): `PWMOutputImpl`, `ConfigurationType`, `RobotArmingStateNotifier`, `RobocolParsable`, `RobocolParsableBase`

**Rejected from the allowed packages, with the reason:**

- `com.qualcomm.robotcore.hardware.I2cWarningManager`: uses Android (android/app/Application)
- `com.qualcomm.robotcore.hardware.LED`: uses Android (android/app/Application)
- `com.qualcomm.robotcore.hardware.LightBlinker`: uses Android (android/graphics/Color)
- `com.qualcomm.robotcore.hardware.PWMOutputImpl`: uses Android (android/app/Application)
- `com.qualcomm.robotcore.hardware.ScannedDevices`: uses Android (android/text/TextUtils)
- `com.qualcomm.robotcore.hardware.TimestampedI2cData`: reads the wall clock (System.nanoTime), which would not follow simulated time
- `com.qualcomm.robotcore.hardware.USBAccessibleLynxModule`: uses Android (android/app/Application, android/text/TextUtils)
- `com.qualcomm.robotcore.util.BatteryChecker`: uses Android (android/content/Context, android/content/Intent, android/content/IntentFilter)
- `com.qualcomm.robotcore.util.ClassUtil`: uses Android (android/app/Application, android/content/res/Resources)
- `com.qualcomm.robotcore.util.ClockWarningSource`: uses Android (android/app/Application, android/content/SharedPreferences, android/content/SharedPreferences$OnSharedPreferenceChangeListener)
- `com.qualcomm.robotcore.util.Dimmer`: uses Android (android/app/Activity, android/os/Handler, android/view/Window)
- `com.qualcomm.robotcore.util.ImmersiveMode`: uses Android (android/view/View)
- `com.qualcomm.robotcore.util.IncludedFirmwareFileInfo`: does not load on a plain JVM: java.lang.NoSuchFieldError: UPDATES_DIR
- `com.qualcomm.robotcore.util.ShortHash`: uses Android (android/util/Log)
- `com.qualcomm.robotcore.util.SoftwareVersionWarningSource`: uses Android (android/app/Application, android/content/SharedPreferences, android/content/SharedPreferences$OnSharedPreferenceChangeListener)
- `com.qualcomm.robotcore.util.ThreadPool`: uses Android (android/os/Debug, android/util/LongSparseArray)
- `com.qualcomm.robotcore.util.Util`: uses Android (android/widget/TextView)
- `org.firstinspires.ftc.robotcore.external.JavaUtil`: uses Android (android/app/Activity, android/content/Context, android/content/res/Resources)
- `org.firstinspires.ftc.robotcore.external.SignificantMotionDetection`: uses Android (android/app/Activity, android/content/Context, android/hardware/Sensor)
- `org.firstinspires.ftc.robotcore.external.function.Continuation`: uses Android (android/os/Handler, android/os/Looper)
- `org.firstinspires.ftc.robotcore.external.navigation.MotionDetection`: uses Android (android/app/Application, android/content/Context, android/hardware/Sensor)

<!-- sim-generated:end -->

### What a field/robot simulation would need next

The bench stops at the output shafts. Driving on the field or climbing needs: (1) a
rigid-body robot model (mass, inertia, wheel contact with omni/mecanum rollers,
friction) fed by the output torques the motor model already computes, e.g. MuJoCo as
in `FGC_2026_Korea/09_sim`, stepped by the same 1 ms scheduler; (2) mechanism models
per subsystem (arm with gravity, winch, the climb); (3) the field and game pieces as
collision geometry, which the distance/colour raycasts would then see; (4) a
`robot` block in Contract 6 tying devices to bodies and joints, and a `pose` field in
`state`. Contract 5 needs no change for the OpMode side: the code already only sees
the SDK.
