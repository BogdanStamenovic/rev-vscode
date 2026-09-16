from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .dbwrite import build_database, write_database
from .download import ensure_sdk_cache
from .handwritten import GAMEPAD_PY, INIT_PY, LANG_PY
from .registry import build_registry
from .stubgen import generate_module_files

DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache"


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

    (ftc_dir / "lang.py").write_text(LANG_PY, encoding="utf-8")
    (ftc_dir / "__init__.py").write_text(INIT_PY, encoding="utf-8")
    (ftc_dir / "gamepad.py").write_text(GAMEPAD_PY, encoding="utf-8")

    print(f"sdkgen: done in {time.time() - t0:.1f}s", file=sys.stderr)
    if registry.parse_failures:
        print("sdkgen: files that failed to parse:", file=sys.stderr)
        for f, err in registry.parse_failures:
            print(f"  {f}: {err}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
