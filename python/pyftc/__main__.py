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

    mn = sub.add_parser("manual", help="regenerate just the man page for an already-spawned starter pack")
    mn.add_argument("--config", type=Path, required=True)
    mn.add_argument("--rcinfo", type=Path)
    mn.add_argument("--name", default="StarterPack")
    mn.add_argument("--sdk", default=DEFAULT_SDK)
    mn.add_argument("--typedb", type=Path)

    cf = sub.add_parser("config-fingerprint", help="fingerprint a hardware configuration (no SDK database needed)")
    cf.add_argument("--config", type=Path, required=True)

    u = sub.add_parser("starter-update", help="extend an existing starter pack's markers in place")
    u.add_argument("--file", type=Path, required=True)
    u.add_argument("--config", type=Path, required=True)
    u.add_argument("--rcinfo", type=Path)
    u.add_argument("--sdk", default=DEFAULT_SDK)
    u.add_argument("--typedb", type=Path)

    sp = sub.add_parser("sim-prepare", help="translate and compile OpModes for the simulator (docs/ARCHITECTURE.md, Contract 5)")
    sp_src = sp.add_mutually_exclusive_group(required=True)
    sp_src.add_argument("--root", type=Path)
    sp_src.add_argument("--files", type=Path, nargs="+")
    sp.add_argument("--out", type=Path, required=True, help="build directory (classes, manifest.json)")
    sp.add_argument("--cache", type=Path, required=True, help="where the simulation SDK and FTC SDK jars are cached")
    sp.add_argument("--javac", help="javac to use (default: JAVA_HOME, PATH)")
    sp.add_argument("--config", type=Path, help="hardware configuration XML (from the hub or the workspace)")
    sp.add_argument("--config-source", default="file", help="where --config came from: hub or file")
    sp.add_argument("--no-trace", action="store_true", help="build without the line/variable trace hooks")
    sp.add_argument("--sdk", default=DEFAULT_SDK)

    gp = sub.add_parser("gamepad", help="stream physical controllers as FTC Gamepad state (JSON lines)")
    gp.add_argument("gamepad_args", nargs=argparse.REMAINDER)

    args = ap.parse_args(argv)
    if args.cmd == "gamepad":
        from .gamepad import main as gamepad_main
        return gamepad_main(args.gamepad_args)
    if args.cmd == "sim-prepare":
        return _sim_prepare(args)
    try:
        if args.cmd == "config-fingerprint":
            # Deliberately does not touch TypeDB.load: this has to stay cheap
            # enough to run on every hub refresh, and keep working while
            # another process is regenerating the SDK database file.
            from .markers import compute_fingerprint
            fingerprint = compute_fingerprint(args.config.read_text())
            print(json.dumps({"ok": True, "fingerprint": fingerprint}))
            return 0

        db = TypeDB.load(args.sdk, args.typedb)
        if args.cmd == "translate-project":
            from .translate import ProjectTranslator, collect_sources
            paths = collect_sources(args.root) if args.root else [p.resolve() for p in args.files]
            result = ProjectTranslator(db).translate(paths, root=args.root)
            print(json.dumps(result))
            return 0 if result["ok"] else 1
        if args.cmd == "starter":
            from .markers import compute_fingerprint
            from .manual import generate as generate_manual
            from .starter import generate
            rcinfo = _read_rcinfo(args.rcinfo)
            config_xml = args.config.read_text()
            python = generate(db, config_xml, rcinfo, args.name)
            fingerprint = compute_fingerprint(config_xml)
            manual = generate_manual(db, config_xml, rcinfo, args.name, fingerprint)
            print(json.dumps({"ok": True, "python": python, "fingerprint": fingerprint, "manual": manual}))
            return 0
        if args.cmd == "manual":
            from .markers import compute_fingerprint
            from .manual import generate as generate_manual
            rcinfo = _read_rcinfo(args.rcinfo)
            config_xml = args.config.read_text()
            fingerprint = compute_fingerprint(config_xml)
            manual = generate_manual(db, config_xml, rcinfo, args.name, fingerprint)
            print(json.dumps({"ok": True, "markdown": manual, "fingerprint": fingerprint}))
            return 0
        if args.cmd == "starter-update":
            from .update import apply_update
            rcinfo = _read_rcinfo(args.rcinfo)
            result = apply_update(db, args.file.read_text(), args.config.read_text(), rcinfo)
            print(json.dumps(result))
            return 0
    except Exception as e:  # noqa: BLE001 - boundary with the extension
        print(f"pyftc: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 2
    return 2


def _sim_prepare(args: argparse.Namespace) -> int:
    from .sim import build as simbuild
    from .sim import config as simconfig
    from .sim.prepare import prepare
    from .translate import collect_sources
    try:
        db = TypeDB.load(args.sdk)
        javac = simbuild.find_javac(args.javac)
        sources = collect_sources(args.root) if args.root else [p.resolve() for p in args.files]
        cfg = None
        if args.config:
            cfg = simconfig.from_xml(db, args.config.read_text(), args.config.stem, args.config_source)
        result = prepare(sources, args.out, args.cache, javac, sdk=args.sdk, config=cfg,
                         workspace=args.root, trace=not args.no_trace, db=db)
    except simbuild.BuildError as e:
        print(f"pyftc: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 - boundary with the extension
        print(f"pyftc: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0 if result["ok"] else 1


def _read_rcinfo(path: Path | None) -> dict:
    rcinfo = json.loads(path.read_text()) if path else {}
    rcinfo.pop("passphrase", None)
    return rcinfo


if __name__ == "__main__":
    sys.exit(main())
