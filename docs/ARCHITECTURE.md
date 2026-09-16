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
| `ftc.vision`    | `org.firstinspires.ftc.vision`, `.apriltag`, `.opencv`                        |
| `ftc.lang`      | hand-written: `long`, `short`, `byte`, `char` int aliases and `float32` for Java `float` |

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
→ `{"ok": true, "python": "<source of the starter OpMode>"}`
