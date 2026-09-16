"""CLI used by the VS Code extension. stdout is JSON only (contract 3 in
docs/ARCHITECTURE.md): exit 0 ok, 1 user-code errors, 2 usage/internal error."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from .typedb import DEFAULT_SDK, TypeDB


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pyftc")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("translate-project", help="translate Python OpModes to OnBot Java sources")
    src = t.add_mutually_exclusive_group(required=True)
    src.add_argument("--root", type=Path)
    src.add_argument("--files", type=Path, nargs="+")
    t.add_argument("--sdk", default=DEFAULT_SDK)
    t.add_argument("--typedb", type=Path, help="type database path (default: bundled sdk-<ver>.json)")

    s = sub.add_parser("starter", help="generate a starter OpMode from a hub's hardware configuration")
    s.add_argument("--config", type=Path, required=True)
    s.add_argument("--rcinfo", type=Path)
    s.add_argument("--name", default="StarterPack")
    s.add_argument("--sdk", default=DEFAULT_SDK)
    s.add_argument("--typedb", type=Path)

    args = ap.parse_args(argv)
    try:
        db = TypeDB.load(args.sdk, args.typedb)
        if args.cmd == "translate-project":
            from .translate import ProjectTranslator, collect_sources
            paths = collect_sources(args.root) if args.root else [p.resolve() for p in args.files]
            result = ProjectTranslator(db).translate(paths)
            print(json.dumps(result))
            return 0 if result["ok"] else 1
        if args.cmd == "starter":
            from .starter import generate
            rcinfo = json.loads(args.rcinfo.read_text()) if args.rcinfo else {}
            rcinfo.pop("passphrase", None)
            python = generate(db, args.config.read_text(), rcinfo, args.name)
            print(json.dumps({"ok": True, "python": python}))
            return 0
    except Exception as e:  # noqa: BLE001 - boundary with the extension
        print(f"pyftc: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
