"""Assembles Contract 1's `classes` dict (with referenced-type closure) and
the full sdk-<version>.json document."""
from __future__ import annotations

import json
from pathlib import Path

from .extract import extract_full
from .packages import build_package_module_map
from .registry import Registry
from .stringres import load_string_resources
from .xmltags import extract_xml_tags

#: Fallback module for a class that's reachable (by closure) from a stubbed
#: signature but whose own Java package has no Contract-2 mapping. Kept
#: separate from FIXED_PACKAGE_MODULE/build_package_module_map because it's
#: not a package rule -- it's "anything closure pulls in that didn't already
#: have a home" -- and it must not shadow a real seed package.
FALLBACK_MODULE = "ftc.internal"


def _module_for(entry, package_module_map: dict[str, str]) -> str | None:
    """Contract 1: module is only ever set on a top-level class; a nested
    class resolves its module by walking `outer` (see stubgen/pytypes
    top_level_path). A top-level class either lands in its Contract-2 module
    or, if closure pulled it in from an unmapped package, in ftc.internal."""
    if entry.outer_fqn is not None:
        return None
    return package_module_map.get(entry.package, FALLBACK_MODULE)


def build_classes(registry: Registry) -> tuple[dict, dict[str, str], set[str]]:
    """Seeds `classes` from the Contract-2 package list, then closes it under
    everything reachable from an included class's methods/fields/extends/
    generic args -- repeatedly, to a fixpoint, so a type pulled in on one
    pass can itself pull in more (e.g. DcMotor -> MotorConfigurationType ->
    Manufacturer). Every class in the result gets the *same* full extraction
    (extract_full): a shallow stand-in would leave the newly-reachable
    classes themselves dead-ending at Any one level down.

    Returns (classes, package_module_map, unresolvable) where `unresolvable`
    is every FQN string that showed up in a signature but has no entry in
    the registry at all -- i.e. it isn't declared anywhere in the FTC SDK's
    own *-sources.jar artifacts (android.*, org.opencv.*, a resolve.py
    simple-name fallback, ...). Those can't be extracted; they stay `Any`.
    """
    package_module_map = build_package_module_map(registry)
    classes: dict = {}
    referenced: set[str] = set()
    unresolvable: set[str] = set()

    wanted_entries = [e for e in registry.by_fqn.values() if e.package in package_module_map]
    for entry in wanted_entries:
        classes[entry.fqn] = extract_full(entry, registry, _module_for(entry, package_module_map), referenced)

    seen = set(classes.keys())
    frontier = list(referenced - seen)
    while frontier:
        fqn = frontier.pop()
        if fqn in seen:
            continue
        seen.add(fqn)
        entry = registry.by_fqn.get(fqn)
        if entry is None:
            unresolvable.add(fqn)
            continue
        classes[fqn] = extract_full(entry, registry, _module_for(entry, package_module_map), referenced)
        # A newly-pulled nested class needs its outer chain present too, or
        # its module can never be resolved (nested classes carry module=None
        # by contract and rely on the outer walk to find one).
        if entry.outer_fqn and entry.outer_fqn not in seen:
            frontier.append(entry.outer_fqn)
        frontier.extend(referenced - seen)

    _settle_internal_module_placement(classes)

    return classes, package_module_map, unresolvable


def _top_level_owner(fqn: str, classes: dict) -> str | None:
    cur = fqn
    while classes.get(cur, {}).get("outer") is not None:
        cur = classes[cur]["outer"]
    return cur if cur in classes else None


def _settle_internal_module_placement(classes: dict) -> None:
    """Closure can introduce a real Java inheritance edge in *both*
    directions between ftc.internal and a fixed Contract-2 module (e.g. some
    ftc.hardware class extends an internal-only interface, while a different
    internal-only class extends something in ftc.hardware). stubgen.py's
    base-class imports are eager (a Python `class Foo(Base):` needs the real
    Base object, not a deferred annotation), so a bidirectional edge there
    is an actual circular import, not just an untidy dependency.

    Contract-2's six fixed modules are never touched here -- their
    assignment is the public contract and must stay stable across a
    regenerate. Only classes closure itself just dropped into
    FALLBACK_MODULE are free to move, and only to a fixed module they
    already have a real inheritance relationship with (so this can only
    ever tighten an edge into an existing module, never invent a new one).
    Iterates to a fixed point: moving one class can expose another (e.g.
    moving RobotUsbModule into ftc.hardware means its own base,
    RobotArmingStateNotifier, now needs to move too).
    """
    changed = True
    while changed:
        changed = False
        for fqn, c in list(classes.items()):
            if c["outer"] is not None:
                continue  # module lives on the top-level entry only
            owner_module = c["module"]
            for ext in c["extends"]:
                base_fqn = ext.split("<", 1)[0].rstrip("[]")
                base_top = _top_level_owner(base_fqn, classes)
                if base_top is None or base_top == fqn:
                    continue
                base_module = classes[base_top]["module"]
                if base_module == owner_module:
                    continue
                if owner_module == FALLBACK_MODULE and base_module != FALLBACK_MODULE:
                    # An internal-only class subclassing a real Contract-2
                    # type is a member of that type's family -- give it that
                    # module instead of the synthetic catch-all.
                    classes[fqn]["module"] = base_module
                    changed = True
                elif base_module == FALLBACK_MODULE and owner_module != FALLBACK_MODULE:
                    # A fixed-module class subclassing something that only
                    # lives in ftc.internal: that base belongs with its one
                    # real subclass family instead.
                    classes[base_top]["module"] = owner_module
                    changed = True
                # else: both sides are already-fixed Contract-2 modules and
                # still disagree -- a genuine cycle in the SDK's own class
                # hierarchy, not one closure introduced. Left alone here;
                # python/tests/test_stubs.py's cycle check would catch it.


def build_database(registry: Registry, version: str, aar_paths: list[Path]) -> dict:
    classes, _, _ = build_classes(registry)
    string_resources = load_string_resources(aar_paths)
    xml_tags = extract_xml_tags(registry, string_resources)
    return {
        "sdkVersion": version,
        "classes": classes,
        "xmlTags": xml_tags,
    }


def write_database(db: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
