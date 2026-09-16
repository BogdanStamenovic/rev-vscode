"""Resolves Android `@string/name` references used in xmlTag-carrying
annotations (e.g. `@DeviceProperties(name = "@string/rev_core_hex_name")`)
to their actual display text.

Deviation from the stated inputs: ARCHITECTURE.md only lists the
`-sources.jar` artifacts as inputs, but many `DeviceProperties.name()` /
`.description()` values are Android string-resource references rather than
literal text, and the literal text only exists in each artifact's compiled
`res/values/values.xml`, which ships inside the plain `.aar` (not the
sources jar). We additionally download the `.aar` (same Maven path, no
`-sources` suffix) purely to mine `res/values/values.xml` for this mapping;
none of its .class/.jar content is used.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

_STRING_RE = re.compile(r'<string\s+name="([^"]+)"[^>]*>(.*?)</string>', re.DOTALL)

_JAVA_ESCAPES = {
    "\\'": "'",
    '\\"': '"',
    "\\n": "\n",
    "\\t": "\t",
}


def _unescape(text: str) -> str:
    for esc, rep in _JAVA_ESCAPES.items():
        text = text.replace(esc, rep)
    # Collapse simple %1$s / %s format placeholders is unnecessary for our use
    # (display names never carry them); leave as-is otherwise.
    return text.strip()


def load_string_resources(aar_paths: list[Path]) -> dict[str, str]:
    resources: dict[str, str] = {}
    for aar in aar_paths:
        if not aar.exists():
            continue
        try:
            with zipfile.ZipFile(aar) as zf:
                try:
                    data = zf.read("res/values/values.xml").decode("utf-8", errors="replace")
                except KeyError:
                    continue
        except zipfile.BadZipFile:
            continue
        for name, value in _STRING_RE.findall(data):
            # Strip any nested tags (e.g. <xliff:g>) defensively.
            value = re.sub(r"<[^>]+>", "", value)
            resources.setdefault(name, _unescape(value))
    return resources


def resolve_string(value: str, resources: dict[str, str]) -> str:
    """`value` is either literal text or an `@string/xxx` reference."""
    if isinstance(value, str) and value.startswith("@string/"):
        key = value[len("@string/"):]
        return resources.get(key, _humanize(key))
    return value


def _humanize(identifier: str) -> str:
    words = re.split(r"[_\-]", identifier)
    return " ".join(w[:1].upper() + w[1:] for w in words if w)
