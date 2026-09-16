"""Every `# example: <group>/<File>.py` block in docs/MANUAL.md must translate
cleanly against the real SDK database, and compile with javac when it's
available. Blocks sharing a group are one project (multi-file examples)."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from pyftc.translate import ProjectTranslator
from pyftc.typedb import TypeDB

ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / "docs" / "MANUAL.md"
SDK_DB = ROOT / "python" / "pyftc" / "data" / "sdk-11.2.0.json"


def examples() -> dict[str, dict[str, str]]:
    groups: dict[str, dict[str, str]] = {}
    for block in re.findall(r"```python\n(.*?)```", MANUAL.read_text(), re.S):
        m = re.match(r"# example: ([\w-]+)/(\w+\.py)\n", block)
        if m:
            groups.setdefault(m.group(1), {})[m.group(2)] = block
    return groups


GROUPS = examples()


def test_manual_has_examples():
    assert len(GROUPS) >= 8


@pytest.mark.skipif(not SDK_DB.exists(), reason="generated SDK database missing; run sdkgen")
@pytest.mark.parametrize("group", sorted(GROUPS))
def test_example_translates_and_compiles(group: str, tmp_path: Path):
    paths = []
    for name, src in GROUPS[group].items():
        p = tmp_path / name
        p.write_text(src)
        paths.append(p)
    r = ProjectTranslator(TypeDB(json.loads(SDK_DB.read_text()))).translate(paths)
    problems = [(Path(d["source"]).name, d["line"], d["severity"], d["message"]) for d in r["diagnostics"]]
    assert r["ok"] and not problems, problems

    javac, cp = os.environ.get("PYFTC_JAVAC"), os.environ.get("PYFTC_SDK_CLASSPATH")
    if not (javac and cp):
        pytest.skip("translated OK; PYFTC_JAVAC / PYFTC_SDK_CLASSPATH not set, so NOT compiled")
    files = []
    for f in r["files"]:
        p = tmp_path / f"{f['className']}.java"
        p.write_text(f["java"])
        files.append(str(p))
    res = subprocess.run([javac, "-nowarn", "-Xlint:-options", "-source", "8", "-target", "8", "-cp", cp,
                          "-d", str(tmp_path / "classes"), *files], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr + "\n\n" + "\n\n".join(f["java"] for f in r["files"])
