"""Compile translator output with a real javac against the real FTC SDK jars,
using the same -source/-target 1.8 as OnBot Java on the hub.

Needs PYFTC_JAVAC (path to javac, JDK 17 works) and PYFTC_SDK_CLASSPATH
(colon-separated: the SDK artifacts' classes.jar files plus an android.jar).
Skipped loudly otherwise; `scripts/javac-env.sh` fetches both.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import test_translate

JAVAC = os.environ.get("PYFTC_JAVAC")
CLASSPATH = os.environ.get("PYFTC_SDK_CLASSPATH")

pytestmark = pytest.mark.skipif(
    not (JAVAC and CLASSPATH),
    reason="PYFTC_JAVAC / PYFTC_SDK_CLASSPATH not set: generated Java was NOT compiled (run scripts/javac-env.sh)",
)


def _compile(files: list[dict], out: Path) -> subprocess.CompletedProcess[str]:
    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)
    paths = []
    for f in files:
        p = src / f"{f['className']}.java"
        p.write_text(f["java"])
        paths.append(str(p))
    return subprocess.run(
        [JAVAC, "-nowarn", "-Xlint:-options", "-source", "8", "-target", "8", "-cp", CLASSPATH,
         "-d", str(out / "classes"), *paths],
        capture_output=True, text=True,
    )


TESTS = [name for name in dir(test_translate) if name.startswith("test_")]


@pytest.mark.parametrize("name", TESTS)
def test_translations_compile(name: str, translate, tmp_path: Path) -> None:
    results = []

    def capture(*args, **kwargs):
        r = translate(*args, **kwargs)
        results.append(r)
        return r

    try:
        getattr(test_translate, name)(capture)
    except AssertionError:
        pytest.skip("translator test itself fails; see test_translate.py")
    compiled = 0
    for i, r in enumerate(results):
        if not r["ok"]:
            continue
        res = _compile(r["files"], tmp_path / str(i))
        java = "\n\n".join(f["java"] for f in r["files"])
        assert res.returncode == 0, f"javac failed:\n{res.stderr}\n--- generated ---\n{java}"
        compiled += 1
    if not compiled:
        pytest.skip("test only produces rejected programs")
