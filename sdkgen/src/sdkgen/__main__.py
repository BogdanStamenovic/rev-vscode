from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .dbwrite import build_database, write_database
from .download import ensure_sdk_cache
from .handwritten import GAMEPAD_PY, INIT_PY, IO_PY, LANG_PY
from .pytypes import unresolved_bases
from .registry import build_registry
from .stubgen import generate_module_files

DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache"


def _iter_type_strings(c: dict):
    for m in c.get("methods") or []:
        for p in m.get("params") or []:
            yield p["type"]
        yield m.get("returns", "void")
    for ctor in c.get("constructors") or []:
        for p in ctor.get("params") or []:
            yield p["type"]
    for f in c.get("fields") or []:
        yield f["type"]
    for e in c.get("extends") or []:
        yield e
    for tp in c.get("typeParams") or []:
        if " extends " in tp:
            yield tp.split(" extends ", 1)[1]


#: Types this closure pass would flag as unresolved (nothing in any FTC SDK
#: sources jar declares them, so `classes` has no entry) but that are in
#: fact real, hand-written stubs living outside the generated ftc/*.py files
#: sdkgen itself writes -- see python/pyftc/typedb.py's hand-written slice
#: and python/ftc/io.py. Excluded here so a regenerate doesn't relist a type
#: as an unstubbed gap when it's actually stubbed by hand.
HAND_STUBBED_ELSEWHERE = {"java.io.File"}


def _write_internal_type_list(classes: dict, ftc_dir: Path) -> int:
    """Appends a documented, sorted list of every Java type still rendering
    as `Any` in the generated stubs (module-level, in ftc/internal.py) --
    per ARCHITECTURE.md's closure requirement, these gaps must be visible,
    not silent. Returns the count for the stderr summary."""
    causes: set[str] = set()
    for c in classes.values():
        for ts in _iter_type_strings(c):
            causes |= unresolved_bases(ts, classes)
    causes -= HAND_STUBBED_ELSEWHERE
    if not causes:
        return 0
    lines = [
        "",
        "",
        "# Referenced from a stubbed signature somewhere in ftc.*, but not",
        "# extractable: no declaration for these exists in any FTC SDK",
        "# *-sources.jar artifact (Android framework, OpenCV, org.json, the",
        "# JDK itself, or a couple of third-party libraries the SDK depends",
        "# on without shipping sources for). A signature naming one of these",
        "# still renders `Any` for that parameter/return/field -- this list",
        "# exists so that's a documented gap, not a silent one.",
        "UNSTUBBABLE_JAVA_TYPES = [",
    ]
    lines.extend(f'    "{fqn}",' for fqn in sorted(causes))
    lines.append("]")
    path = ftc_dir / "internal.py"
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(causes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdkgen")
    parser.add_argument("--sdk", required=True, help="FTC SDK version, e.g. 11.2.0")
    parser.add_argument("--out", required=True, help="output root (contains pyftc/ and ftc/), "
                                                       "typically rev-vscode/python")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR),
                         help="jar/aar download+extract cache (gitignored); reused if present")
    args = parser.parse_args(argv)

    cache_dir = Path(args.cache_dir)
    out_root = Path(args.out)

    t0 = time.time()
    artifact_dirs, aar_paths = ensure_sdk_cache(cache_dir, args.sdk)

    registry = build_registry(artifact_dirs)
    print(f"sdkgen: parsed {registry.files_parsed} files in {time.time() - t0:.1f}s, "
          f"{len(registry.parse_failures)} parse failures", file=sys.stderr)

    db = build_database(registry, args.sdk, aar_paths)
    db_path = out_root / "pyftc" / "data" / f"sdk-{args.sdk}.json"
    write_database(db, db_path)
    print(f"sdkgen: wrote {db_path} ({len(db['classes'])} classes, {len(db['xmlTags'])} xmlTags)",
          file=sys.stderr)

    ftc_dir = out_root / "ftc"
    counts = generate_module_files(db["classes"], registry, ftc_dir)
    for module, n in counts.items():
        print(f"sdkgen: {module}: {n} top-level classes", file=sys.stderr)

    n_unstubbable = _write_internal_type_list(db["classes"], ftc_dir)
    print(f"sdkgen: {n_unstubbable} distinct Java types remain unstubbed (Any) -- "
          f"see ftc/internal.py:UNSTUBBABLE_JAVA_TYPES", file=sys.stderr)

    (ftc_dir / "lang.py").write_text(LANG_PY, encoding="utf-8")
    (ftc_dir / "__init__.py").write_text(INIT_PY, encoding="utf-8")
    (ftc_dir / "gamepad.py").write_text(GAMEPAD_PY, encoding="utf-8")
    (ftc_dir / "io.py").write_text(IO_PY, encoding="utf-8")

    print(f"sdkgen: done in {time.time() - t0:.1f}s", file=sys.stderr)
    if registry.parse_failures:
        print("sdkgen: files that failed to parse:", file=sys.stderr)
        for f, err in registry.parse_failures:
            print(f"  {f}: {err}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
