#!/usr/bin/env python3
"""Fake `python -m pyftc` CLI for extension tests (no real translator yet).

Selected via the revFtc.translatorCommand setting, e.g.:
    ["python3", "<extensionPath>/test/fixtures/fake_pyftc.py"]

Prints Contract 3-shaped JSON on stdout for `translate-project`, `starter`,
`config-fingerprint`, `starter-update` and `manual`, so the extension can be
exercised end to end without the real translator (which is being built
concurrently, per ARCHITECTURE.md).

Behavior is driven by the .py source content so tests can trigger each
branch:
  - a file containing the literal text "TRANSLATE_ERROR" produces a
    translation-time error diagnostic (exit 1, ok=false).
  - a file containing "TWO_CLASSES" produces two Java classes from one
    source file (per the "files[] is per class" contract clarification).
  - anything else produces one trivial valid OpMode class.

`config-fingerprint`/`starter`/`starter-update` all derive the fingerprint
the same way - sha256 of the config XML file's bytes, truncated to 16 hex
chars - so "does the config content match what a file was generated
against" is a real, testable comparison rather than a canned constant. This
is NOT how the real fingerprint is computed (ARCHITECTURE.md's Contract 3
hashes a canonical array of hubs/devices, not raw file bytes) - it only needs
to be *a* deterministic function of the config content for these tests to be
meaningful, and matching the real algorithm exactly is the other agent's
job, not this fixture's.

`starter-update`'s idea of "what changed" is deliberately simplistic and
test-directed rather than a real hardware diff: it reads directive comments
out of the INPUT .py file (never written to real output, and real pyftc
would never look for them) to decide what to simulate:
  - `# FAKE_UPDATE_NO_MARKERS` anywhere in the file: simulate the "markers
    missing" case (applied: false) regardless of fingerprint.
  - `# FAKE_UPDATE_ADD:<field>:<name>:<type>` (one per line): simulate an
    added device, spliced in before `# ── pyftc:devices:end ──` like the
    real CLI's insertion rule.
  - `# FAKE_UPDATE_REMOVE:<field>:<name>`: simulate a device that left the
    configuration - splices a `# pyftc: no longer in the configuration`
    comment + a `<field>: DcMotor` line before the same marker, per
    Contract 4's "never delete, just mark" rule.
  - `# FAKE_UPDATE_HUB:<name>:<address>`: simulate a newly seen expansion hub.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PACKAGE = "org.firstinspires.ftc.teamcode.pyftc"
DEVICES_END_MARKER = "# ── pyftc:devices:end ──"
HEADER_RE = re.compile(r'pyftc:config name="([^"]*)" fingerprint="([0-9a-f]+)" generated="([^"]*)"')


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


def fingerprint_of(config_path: str) -> str:
    return hashlib.sha256(Path(config_path).read_bytes()).hexdigest()[:16]


def manual_markdown(name: str, fingerprint: str) -> str:
    return f"# {name}\n\nGenerated man page for `{name}`.  \nfingerprint: `{fingerprint}`\n"


def cmd_starter(args: argparse.Namespace) -> int:
    fp = fingerprint_of(args.config)
    python_source = (
        f'# ── pyftc:config name="{args.name}" fingerprint="{fp}" generated="2026-09-20" ──\n'
        "import ftc\n\n"
        f"class {args.name}(ftc.opmode.LinearOpMode):\n"
        "    def run(self):\n"
        "        # ── pyftc:hardware ──\n"
        "        #   Kombjan (RevRoboticsCoreHexMotor) port 0\n"
        "        # ── pyftc:hardware:end ──\n"
        "        # ── pyftc:devices ──\n"
        "        kombjan: DcMotor\n"
        f"        {DEVICES_END_MARKER}\n"
        "        self.wait_for_start()\n"
        "        while self.op_mode_is_active():\n"
        "            self.telemetry.update()\n"
    )
    print(json.dumps({"ok": True, "python": python_source, "fingerprint": fp, "manual": manual_markdown(args.name, fp)}))
    return 0


def cmd_config_fingerprint(args: argparse.Namespace) -> int:
    print(json.dumps({"ok": True, "fingerprint": fingerprint_of(args.config)}))
    return 0


def cmd_manual(args: argparse.Namespace) -> int:
    fp = fingerprint_of(args.config)
    print(json.dumps({"ok": True, "markdown": manual_markdown(args.name, fp), "fingerprint": fp}))
    return 0


def cmd_starter_update(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text()
    new_fp = fingerprint_of(args.config)
    name_match = re.search(r"class (\w+)\(", text)
    name = name_match.group(1) if name_match else Path(args.file).stem

    if "FAKE_UPDATE_NO_MARKERS" in text or DEVICES_END_MARKER not in text:
        print(json.dumps({
            "ok": True, "changed": True, "applied": False, "fingerprint": new_fp,
            "block": f"# new code for {name}, place it under # ── pyftc:devices ── by hand\nwinch: DcMotor\n",
            "manual": manual_markdown(name, new_fp),
            "added": [], "removed": [], "hubsAdded": [], "notes": ["markers missing, nothing was touched"],
        }))
        return 0

    header = HEADER_RE.search(text)
    old_fp = header.group(2) if header else None
    if old_fp == new_fp:
        print(json.dumps({
            "ok": True, "changed": False, "applied": True, "fingerprint": new_fp,
            "manual": manual_markdown(name, new_fp),
            "added": [], "removed": [], "hubsAdded": [], "notes": [],
        }))
        return 0

    added = [
        {"name": n, "field": f, "type": t, "control": "gamepad 1: hold Y forward, hold A reverse"}
        for f, n, t in re.findall(r"# FAKE_UPDATE_ADD:(\w+):([^:\n]+):(\w+)", text)
    ]
    removed = [{"name": n, "field": f} for f, n in re.findall(r"# FAKE_UPDATE_REMOVE:(\w+):([^:\n]+)", text)]
    hubs_added = [{"name": n, "address": a} for n, a in re.findall(r"# FAKE_UPDATE_HUB:([^:\n]+):(\w+)", text)]

    insert_lines = []
    for d in added:
        insert_lines.append(f"        {d['field']}: {d['type']}  # added")
    for d in removed:
        insert_lines.append("        # pyftc: no longer in the configuration")
        insert_lines.append(f"        {d['field']}: DcMotor")
    insertion = ("\n".join(insert_lines) + "\n") if insert_lines else ""
    updated = text.replace(DEVICES_END_MARKER, insertion + DEVICES_END_MARKER, 1)
    if header:
        updated = updated.replace(header.group(0), f'pyftc:config name="{header.group(1)}" fingerprint="{new_fp}" generated="2026-09-20"', 1)

    print(json.dumps({
        "ok": True, "changed": True, "applied": True, "fingerprint": new_fp,
        "python": updated, "manual": manual_markdown(name, new_fp),
        "added": added, "removed": removed, "hubsAdded": hubs_added,
        "notes": ["fake starter-update applied"],
    }))
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

    cf = sub.add_parser("config-fingerprint")
    cf.add_argument("--config", required=True)
    cf.set_defaults(func=cmd_config_fingerprint)

    mn = sub.add_parser("manual")
    mn.add_argument("--config", required=True)
    mn.add_argument("--rcinfo", required=True)
    mn.add_argument("--name", required=True)
    mn.set_defaults(func=cmd_manual)

    su = sub.add_parser("starter-update")
    su.add_argument("--file", required=True)
    su.add_argument("--config", required=True)
    su.add_argument("--rcinfo", required=True)
    su.set_defaults(func=cmd_starter_update)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:  # usage/internal error: message on stderr, exit 2
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
