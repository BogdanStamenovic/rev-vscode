#!/usr/bin/env python3
"""Fake `python -m pyftc` CLI for extension tests (no real translator yet).

Selected via the revFtc.translatorCommand setting, e.g.:
    ["python3", "<extensionPath>/test/fixtures/fake_pyftc.py"]

Prints Contract 3-shaped JSON on stdout for `translate-project` and
`starter`, so the extension can be exercised end to end without the real
translator (which is being built concurrently, per ARCHITECTURE.md).

Behavior is driven by the .py source content so tests can trigger each
branch:
  - a file containing the literal text "TRANSLATE_ERROR" produces a
    translation-time error diagnostic (exit 1, ok=false).
  - a file containing "TWO_CLASSES" produces two Java classes from one
    source file (per the "files[] is per class" contract clarification).
  - anything else produces one trivial valid OpMode class.
"""
import argparse
import json
import sys
from pathlib import Path

PACKAGE = "org.firstinspires.ftc.teamcode.pyftc"


def hub_path(class_name: str) -> str:
    return f"/src/org/firstinspires/ftc/teamcode/pyftc/{class_name}.java"


def make_class(source: str, class_name: str) -> dict:
    java = (
        f"package {PACKAGE};\n"
        "import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;\n"
        "import com.qualcomm.robotcore.eventloop.opmode.TeleOp;\n"
        "\n"
        f"@TeleOp(name = \"{class_name}\")\n"
        f"public class {class_name} extends LinearOpMode {{\n"
        "    @Override\n"
        "    public void runOpMode() {\n"
        "        waitForStart();\n"
        "        while (opModeIsActive()) {\n"
        "            telemetry.update();\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    # lineMap[javaLine-1] = python line (1-based); 0 = synthetic. Line 8
    # ("telemetry.update()") maps back to python line 5 for lineMap tests.
    line_count = java.count("\n")
    line_map = [0] * line_count
    line_map[7] = 5
    return {
        "source": source,
        "className": class_name,
        "hubPath": hub_path(class_name),
        "java": java,
        "lineMap": line_map,
        "diagnostics": [],
    }


def translate_sources(sources: list[str]) -> dict:
    files = []
    diagnostics = []
    for source in sources:
        text = Path(source).read_text() if Path(source).exists() else ""
        class_name = Path(source).stem
        if "TRANSLATE_ERROR" in text:
            diagnostics.append({
                "source": source,
                "line": 1,
                "col": 0,
                "endLine": 1,
                "endCol": 5,
                "severity": "error",
                "message": "fake_pyftc: simulated translation error",
            })
            continue
        if "TWO_CLASSES" in text:
            files.append(make_class(source, class_name + "A"))
            files.append(make_class(source, class_name + "B"))
        else:
            files.append(make_class(source, class_name))
    ok = not any(d["severity"] == "error" for d in diagnostics)
    return {"ok": ok, "files": files, "diagnostics": diagnostics}


def cmd_translate_project(args: argparse.Namespace) -> int:
    if args.root:
        sources = sorted(str(p.resolve()) for p in Path(args.root).glob("*.py"))
    else:
        sources = [str(Path(p).resolve()) for p in args.files]
    result = translate_sources(sources)
    print(json.dumps(result))
    return 0 if result["ok"] else 1


def cmd_starter(args: argparse.Namespace) -> int:
    python_source = (
        "import ftc\n\n"
        f"class {args.name}(ftc.opmode.LinearOpMode):\n"
        "    def run(self):\n"
        "        # Hardware (from config):\n"
        "        #   Kombjan (RevRoboticsCoreHexMotor) port 0\n"
        "        self.wait_for_start()\n"
        "        while self.op_mode_is_active():\n"
        "            self.telemetry.update()\n"
    )
    print(json.dumps({"ok": True, "python": python_source}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="pyftc")
    sub = parser.add_subparsers(dest="command", required=True)

    tp = sub.add_parser("translate-project")
    tp.add_argument("--root")
    tp.add_argument("--files", nargs="*", default=[])
    tp.add_argument("--sdk")
    tp.set_defaults(func=cmd_translate_project)

    st = sub.add_parser("starter")
    st.add_argument("--config", required=True)
    st.add_argument("--rcinfo", required=True)
    st.add_argument("--name", required=True)
    st.set_defaults(func=cmd_starter)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:  # usage/internal error: message on stderr, exit 2
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
