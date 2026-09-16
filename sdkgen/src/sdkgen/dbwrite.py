"""Assembles Contract 1's `classes` dict (with referenced-type closure) and
the full sdk-<version>.json document."""
from __future__ import annotations

import json
from pathlib import Path

from .extract import extract_full, extract_minimal
from .packages import build_package_module_map
from .registry import Registry
from .stringres import load_string_resources
from .xmltags import extract_xml_tags


def build_classes(registry: Registry) -> tuple[dict, dict[str, str]]:
    package_module_map = build_package_module_map(registry)
    classes: dict = {}
    referenced: set[str] = set()

    wanted_entries = [e for e in registry.by_fqn.values() if e.package in package_module_map]
    for entry in wanted_entries:
        module = package_module_map[entry.package] if entry.outer_fqn is None else None
        classes[entry.fqn] = extract_full(entry, registry, module, referenced)

    frontier = list(referenced - set(classes.keys()))
    seen = set(classes.keys())
    while frontier:
        fqn = frontier.pop()
        if fqn in seen:
            continue
        seen.add(fqn)
        entry = registry.by_fqn.get(fqn)
        if entry is None:
            continue  # JDK/Android type, not one of ours -- not modeled in `classes`
        classes[fqn] = extract_minimal(entry)
        outer = entry.outer_fqn
        while outer and outer not in seen:
            oentry = registry.by_fqn.get(outer)
            if oentry is None:
                break
            classes[outer] = extract_minimal(oentry)
            seen.add(outer)
            outer = oentry.outer_fqn

    return classes, package_module_map


def build_database(registry: Registry, version: str, aar_paths: list[Path]) -> dict:
    classes, _ = build_classes(registry)
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
