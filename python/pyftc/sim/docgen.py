"""Regenerate the simulator tables in docs/ARCHITECTURE.md: every physical constant
with its source (constants.json) and what the simulation SDK supports
(simulated.json from a build). tests/test_sim.py checks the doc is current.

    python -m pyftc.sim.docgen [--cache DIR] [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import build as simbuild

SIM_DIR = Path(__file__).parent
DOC = SIM_DIR.parent.parent.parent / "docs" / "ARCHITECTURE.md"
BEGIN = "<!-- sim-generated:begin (python -m pyftc.sim.docgen) -->"
END = "<!-- sim-generated:end -->"


def constants_table() -> list[str]:
    data = json.loads((SIM_DIR / "constants.json").read_text())
    rows = ["| constant | value | unit | verified | source |", "|---|---|---|---|---|"]
    for group, entries in data.items():
        if group.startswith("_"):
            continue
        for name, e in entries.items():
            src = e["source"].replace("|", "\\|")
            if e.get("note"):
                src += " — " + e["note"].replace("|", "\\|")
            rows.append(f"| `{group}.{name}` | {e['value']} | {e['unit']} | {'yes' if e['verified'] else '**no, placeholder**'} | {src} |")
    return rows


def simulated_lists(simulated: dict) -> list[str]:
    out = ["**Classes user code can use in the simulator** (anything else fails to compile there, naming the class):", ""]
    by_how: dict[str, list[str]] = {}
    for fqn, how in simulated["classes"].items():
        by_how.setdefault(how, []).append(fqn)
    for how in sorted(by_how):
        names = sorted(by_how[how])
        out.append(f"- {how} ({len(names)}): " + ", ".join(f"`{n.rsplit('.', 1)[-1]}`" for n in names))
    out += ["", "**Rejected from the allowed packages, with the reason:**", ""]
    for fqn, why in sorted(simulated["rejected"].items()):
        out.append(f"- `{fqn}`: {why}")
    return out


def render(simulated: dict) -> str:
    lines = [BEGIN, "", "### Physical constants", "", *constants_table(), "", "### What is simulated", "", *simulated_lists(simulated), "", END]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pyftc.sim.docgen")
    ap.add_argument("--cache", type=Path, default=simbuild.REPO_ROOT / ".cache" / "sim")
    ap.add_argument("--check", action="store_true", help="exit 1 if the doc is out of date instead of writing it")
    args = ap.parse_args(argv)
    sdk = simbuild.build(args.cache, simbuild.find_javac())
    text = DOC.read_text()
    if BEGIN not in text or END not in text:
        print(f"{DOC} has no generated section markers", file=sys.stderr)
        return 2
    new = text[:text.index(BEGIN)] + render(sdk.simulated) + text[text.index(END) + len(END):]
    if args.check:
        return 0 if new == text else 1
    DOC.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
