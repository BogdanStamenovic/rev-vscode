"""Verifies the transitive-closure property sdkgen is supposed to guarantee
(see docs/ARCHITECTURE.md, the "Contract 2" table, and sdkgen/src/sdkgen/
dbwrite.py's build_classes): every Java type named in a stubbed class's
signature is itself either stubbed, or a documented, genuinely-unstubbable
external type -- never a silent, unexplained dead end.

Deliberately stdlib-only and independent of the sdkgen package (python/pyftc
is stdlib-only by project rule, and sdkgen is a separate uv project sdkgen/
does not ship as a runtime dependency of python/). This reads the generated
artifacts -- python/pyftc/data/sdk-<ver>.json and python/ftc/*.py -- exactly
as Pylance and the translator would.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON_ROOT = Path(__file__).resolve().parents[1]
FTC_DIR = PYTHON_ROOT / "ftc"
SDK_DB = PYTHON_ROOT / "pyftc" / "data" / "sdk-11.2.0.json"

pytestmark = pytest.mark.skipif(not SDK_DB.exists(), reason="generated SDK database missing; run sdkgen")

# ---------------------------------------------------------------------------
# Type-string parsing, deliberately mirroring sdkgen/src/sdkgen/pytypes.py's
# classification tables (primitives / java.lang / collections) rather than
# importing them, so this test exercises the *contract* the generated JSON
# promises, not sdkgen's own code.
# ---------------------------------------------------------------------------

PRIMITIVES = {"int", "double", "boolean", "void", "long", "short", "byte", "char", "float"}

JAVA_LANG_SPECIAL_CASED = {
    "java.lang.String", "java.lang.CharSequence", "java.lang.Integer", "java.lang.Short",
    "java.lang.Byte", "java.lang.Long", "java.lang.Double", "java.lang.Float",
    "java.lang.Boolean", "java.lang.Character", "java.lang.Object", "java.lang.Void",
    "java.lang.Number", "java.lang.Class",
}

COLLECTIONS = {
    "java.util.List", "java.util.ArrayList", "java.util.Collection", "java.util.Iterable",
    "java.util.Queue", "java.util.Deque", "java.util.LinkedList",
    "java.util.Set", "java.util.HashSet", "java.util.TreeSet", "java.util.SortedSet", "java.util.LinkedHashSet",
    "java.util.Map", "java.util.HashMap", "java.util.TreeMap", "java.util.SortedMap", "java.util.LinkedHashMap",
}

# Package prefixes for real dependencies that have no *-sources.jar in the
# FTC SDK's own Maven artifacts (verified by hand against sdkgen/.cache/src:
# no android/, org/opencv, org/json, org/openftc, org/xmlpull, com/google/gson
# directory exists anywhere under it) -- so sdkgen's registry never has a
# declaration for them, and closure has nothing to extract. This is the
# explicit "leave as Any" list from the ticket (android/opencv/json/io/nio)
# plus every other non-SDK dependency actually observed in FTC SDK 11.2.0
# signatures once the DB was made total (java.net, java.util.concurrent and
# friends, java.lang.reflect, the JDK's own java.lang, and three small
# third-party libraries: gson, xmlpull, openftc's easyopencv/apriltag, and
# threetenbp).
EXTERNAL_PREFIXES = (
    "android.", "org.opencv.", "org.json.", "java.io.", "java.nio.",
    "java.net.", "javax.net.", "java.security.", "java.util.", "java.lang.",
    "com.google.gson.", "org.xmlpull.", "org.openftc.", "org.threeten.",
)

# Pre-existing, out-of-scope bug: sdkgen/src/sdkgen/resolve.py's simple-name
# resolution (TypeContext.resolve_simple_name) only looks at the *lexical*
# outer-class chain, not a superclass's nested types -- so a method that
# refers to an inherited nested type by simple name (legal in Java) resolves
# to nothing, and resolve_or_java_lang() falls back to a wrong
# `java.lang.<Name>`/`<package>.<Outer>.<Name>` FQN. That string is baked
# into the DB already wrong; closure only ever walks *correct* FQNs, so it
# can't fix these. Exact FQNs only (not a prefix) so a real new gap
# elsewhere under these packages still fails this test loudly. Most land
# under java.lang.* and are covered by that prefix already; these three
# don't (they look like real SDK types), so they're listed explicitly.
KNOWN_RESOLVER_FALLBACK_BUGS = {
    "com.qualcomm.robotcore.hardware.DcMotor.Direction",
    "com.qualcomm.robotcore.hardware.usb.RobotUsbModule.ARMINGSTATE",
    "com.qualcomm.robotcore.wifi.WifiDirectAssistant.ConnectStatus",
}


def _split_top_level_commas(s: str) -> list[str]:
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return [p.strip() for p in parts if p.strip()]


def _base_and_args(type_str: str) -> tuple[str, list[str]]:
    s = type_str.strip()
    while s.endswith("[]"):
        s = s[:-2].strip()
    if s.endswith(">") and "<" in s:
        idx = s.index("<")
        return s[:idx], _split_top_level_commas(s[idx + 1: -1])
    return s, []


def _module_reachable(fqn: str, classes: dict) -> bool:
    """True if `fqn` is a class Pylance can actually see: present in the DB
    and its (possibly inherited-via-outer) module is set. Mirrors
    RenderContext.top_level_path in sdkgen/src/sdkgen/pytypes.py."""
    seen: set[str] = set()
    cur = fqn
    while cur is not None and cur not in seen:
        seen.add(cur)
        c = classes.get(cur)
        if c is None:
            return False
        if c.get("module") is not None:
            return True
        cur = c.get("outer")
    return False


def _find_dead_ends(type_str: str, classes: dict, out: set[str]) -> None:
    """Recursively collects every base type inside `type_str` that would
    render as `Any` and isn't accounted for by EXTERNAL_PREFIXES or
    KNOWN_RESOLVER_FALLBACK_BUGS -- i.e. a genuine, unexplained closure gap."""
    base, args = _base_and_args(type_str)
    if base in PRIMITIVES or "." not in base:
        pass  # primitive, or a bare type variable
    elif base in JAVA_LANG_SPECIAL_CASED:
        pass
    elif base in COLLECTIONS:
        for a in args:
            _find_dead_ends(a, classes, out)
        return
    elif _module_reachable(base, classes):
        pass
    elif base.startswith(EXTERNAL_PREFIXES) or base in KNOWN_RESOLVER_FALLBACK_BUGS:
        pass  # accounted for, documented dead end
    else:
        out.add(base)
    for a in args:
        _find_dead_ends(a, classes, out)


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


@pytest.fixture(scope="module")
def classes() -> dict:
    return json.loads(SDK_DB.read_text())["classes"]


def test_every_class_in_the_db_is_stubbed(classes: dict) -> None:
    """The whole point of the closure: nothing left in Contract 1's `classes`
    dict should be an orphaned, module-less placeholder (the old
    extract_minimal shallow stand-in). Every class either has its own module
    or resolves to one via its outer chain."""
    orphaned = [fqn for fqn in classes if not _module_reachable(fqn, classes)]
    assert not orphaned, f"{len(orphaned)} classes in the DB have no resolvable module: {sorted(orphaned)[:20]}..."


def test_closure_property(classes: dict) -> None:
    """Every Java type named in a stubbed class's signature is either
    stubbed/importable, or in the explicit allow-list of unstubbable
    external types. A failure here means closure missed a real, extractable
    SDK type -- not that the allow-list needs to grow (grow the allow-list
    only for a genuinely new external dependency, verified against
    sdkgen/.cache/src the way the ones above were)."""
    dead_ends: set[str] = set()
    for c in classes.values():
        for ts in _iter_type_strings(c):
            _find_dead_ends(ts, classes, dead_ends)
    assert not dead_ends, (
        f"{len(dead_ends)} type(s) referenced from a stubbed signature are neither stubbed nor "
        f"an acknowledged external type: {sorted(dead_ends)}"
    )


@pytest.mark.parametrize("fqn", [
    "com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType",
    "com.qualcomm.robotcore.hardware.configuration.typecontainers.ServoConfigurationType",
    "org.firstinspires.ftc.robotcore.external.hardware.camera.WebcamName",
])
def test_previously_dead_ending_types_are_now_stubbed(classes: dict, fqn: str) -> None:
    """The three user-reachable examples from the ticket:
    DcMotor.getMotorType() -> MotorConfigurationType, ServoConfigurationType,
    WebcamName. Pinned individually so a regression here fails on the exact
    type, not just an aggregate count."""
    assert fqn in classes, f"{fqn} is missing from the type database entirely"
    assert _module_reachable(fqn, classes), f"{fqn} is in the DB but not reachable to any ftc.* module"


def _ftc_modules() -> list[str]:
    return sorted(p.stem for p in FTC_DIR.glob("*.py") if p.stem != "__init__")


@pytest.mark.parametrize("module", _ftc_modules())
def test_ftc_module_imports_cleanly(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", f"import ftc.{module}"],
        cwd=str(PYTHON_ROOT), capture_output=True, text=True,
    )
    assert result.returncode == 0, f"import ftc.{module} failed:\n{result.stderr}"


def _top_level_ftc_imports(tree: ast.Module) -> set[str]:
    """Only *unconditional* (runtime) `ftc.*` imports -- the ones a Python
    `class Foo(Base):` statement actually needs eagerly. Imports guarded by
    `if TYPE_CHECKING:` are deliberately excluded: per stubgen.py, those are
    always safe with `from __future__ import annotations` and are the
    documented escape hatch for a same-direction type-only reference, not a
    real load-time dependency that could create a circular import."""
    deps: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("ftc."):
            deps.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ftc."):
                    deps.add(alias.name)
    return deps


def test_no_ftc_import_cycles() -> None:
    graph = {}
    for path in FTC_DIR.glob("*.py"):
        mod = f"ftc.{path.stem}" if path.stem != "__init__" else "ftc"
        graph[mod] = _top_level_ftc_imports(ast.parse(path.read_text(encoding="utf-8")))

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {m: WHITE for m in graph}
    cycles: list[list[str]] = []

    def dfs(u: str, path: list[str]) -> None:
        color[u] = GRAY
        for v in graph.get(u, ()):
            if color.get(v) == GRAY:
                cycles.append(path + [v])
            elif color.get(v, WHITE) == WHITE:
                dfs(v, path + [v])
        color[u] = BLACK

    for m in graph:
        if color[m] == WHITE:
            dfs(m, [m])

    assert not cycles, f"import cycle(s) among ftc.* modules: {cycles}"
