"""Parses every .java source file under the extracted SDK tree and builds a
global registry of type declarations (top-level and nested), keyed by FQN.

The registry is intentionally global (spans all 8 artifacts, all packages,
including internal ones) because resolving a type name to an FQN sometimes
requires knowing about a class we will never emit to the output DB (e.g. a
same-package sibling that lives in an `.internal.` package). We filter which
classes get *emitted* separately, in extract.py.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import javalang
import javalang.tree as jt

TYPE_DECL_TYPES = (
    jt.ClassDeclaration,
    jt.InterfaceDeclaration,
    jt.EnumDeclaration,
    jt.AnnotationDeclaration,
)


@dataclass
class ClassEntry:
    fqn: str
    simple_name: str
    outer_fqn: str | None
    package: str
    node: object  # javalang type declaration node
    cu: object  # javalang.tree.CompilationUnit
    artifact: str
    file: Path


@dataclass
class Registry:
    by_fqn: dict[str, ClassEntry] = field(default_factory=dict)
    # package -> list of top-level simple names declared in that package
    by_package: dict[str, list[str]] = field(default_factory=dict)
    parse_failures: list[tuple[Path, str]] = field(default_factory=list)
    files_parsed: int = 0
    # fqn -> transitive extends/implements closure, memoized by resolve.py's
    # _ancestor_fqns (superclass-inherited nested-type resolution). Lives
    # here rather than as a module-level dict so it can never leak between
    # two Registry instances built in the same process (e.g. under pytest).
    ancestor_cache: dict[str, list[str]] = field(default_factory=dict)

    def children_simple_names(self, outer_fqn: str) -> list[str]:
        prefix = outer_fqn + "."
        out = []
        for fqn, entry in self.by_fqn.items():
            if entry.outer_fqn == outer_fqn:
                out.append(entry.simple_name)
        return out


def _walk_type_decl(node, outer_fqn: str | None, package: str, cu, artifact: str,
                     file: Path, registry: Registry) -> None:
    simple_name = node.name
    fqn = f"{outer_fqn}.{simple_name}" if outer_fqn else (
        f"{package}.{simple_name}" if package else simple_name
    )
    if fqn in registry.by_fqn:
        # Duplicate FQN across artifacts (shouldn't normally happen for real
        # SDK code); keep the first one and log to stderr.
        print(f"sdkgen: duplicate FQN {fqn} in {file}, keeping first", file=sys.stderr)
        return
    registry.by_fqn[fqn] = ClassEntry(
        fqn=fqn, simple_name=simple_name, outer_fqn=outer_fqn, package=package,
        node=node, cu=cu, artifact=artifact, file=file,
    )
    if outer_fqn is None:
        registry.by_package.setdefault(package, []).append(simple_name)

    # Recurse into nested type declarations only (skip methods/fields bodies).
    body = getattr(node, "body", None)
    if not body:
        return
    for member in body:
        if isinstance(member, TYPE_DECL_TYPES):
            _walk_type_decl(member, fqn, package, cu, artifact, file, registry)
        elif isinstance(member, jt.EnumBody if hasattr(jt, "EnumBody") else ()):
            pass
    # EnumDeclaration stores constants separately; enum constants can carry
    # anonymous class bodies but those aren't named types we need to resolve.


def parse_tree(registry: Registry, src_root: Path, artifact: str) -> None:
    """Parse every .java file under src_root (one artifact's extracted sources)."""
    for java_file in sorted(src_root.rglob("*.java")):
        registry.files_parsed += 1
        try:
            text = java_file.read_text(encoding="utf-8", errors="replace")
            cu = javalang.parse.parse(text)
        except Exception as exc:  # noqa: BLE001 - javalang raises various internal errors
            registry.parse_failures.append((java_file, str(exc)))
            print(f"sdkgen: parse failed: {java_file}: {exc}", file=sys.stderr)
            continue
        package = cu.package.name if cu.package else ""
        for type_decl in cu.types:
            if isinstance(type_decl, TYPE_DECL_TYPES):
                _walk_type_decl(type_decl, None, package, cu, artifact, java_file, registry)


def build_registry(artifact_dirs: dict[str, Path]) -> Registry:
    registry = Registry()
    for artifact, src_root in artifact_dirs.items():
        parse_tree(registry, src_root, artifact)
    return registry
