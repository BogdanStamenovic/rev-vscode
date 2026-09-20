"""Marker comments in a generated starter pack (docs/ARCHITECTURE.md, Contract 4)
and the configuration fingerprint that goes on the config header line.

`starter-update` (update.py) never parses the user's Python with `ast`. It
only ever looks for these comment lines and edits text immediately next to
them, so a user's hand-written code between the markers is never at risk.
This module owns finding, validating and editing those lines; it is
deliberately strict (docs/ARCHITECTURE.md, "Contract 4"): a missing or
duplicated marker means "I don't know what this file looks like", and the
right response to that is to refuse, not to guess.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# The five regions Contract 4 lists, in the order they appear in a generated
# file. Order matters when applying edits (see `insert_before_end`).
REGIONS = ("imports", "hardware", "devices", "init", "loop")

_DASH = "─"  # '─', box-drawing light horizontal, used purely as decoration.

# Strict on the "pyftc:<token>" sentinel (that's the contract); lenient on the
# amount of decorative dashes/spaces around it, since that's cosmetic, not a
# guess about content.
_DECOR = r"[\s─-]*"
CONFIG_RE = re.compile(
    r'^(?P<indent>[ \t]*)#' + _DECOR + r'pyftc:config\s+name="(?P<name>(?:[^"\\]|\\.)*)"\s+'
    r'fingerprint="(?P<fp>[0-9a-fA-F]{16})"\s+generated="(?P<gen>\d{4}-\d{2}-\d{2})"' + _DECOR + r'$'
)
MARKER_RE = re.compile(r'^(?P<indent>[ \t]*)#' + _DECOR + r'pyftc:(?P<region>[a-z]+)(?P<is_end>:end)?' + _DECOR + r'$')


class MarkerError(ValueError):
    """The file's Contract 4 markers are missing, duplicated or malformed.
    Callers (update.py) must treat this as "refuse to touch the file", never
    as "guess and proceed"."""


@dataclass
class Region:
    begin: int  # line index (0-based) of the "pyftc:<region>" line
    end: int    # line index of the matching "pyftc:<region>:end" line
    indent: str


@dataclass
class ParsedFile:
    lines: list[str]
    config_line: int
    config_name: str
    config_fingerprint: str
    config_generated: str
    regions: dict[str, Region] = field(default_factory=dict)

    def body(self, region: str) -> list[str]:
        r = self.regions[region]
        return self.lines[r.begin + 1:r.end]


def parse(source: str) -> ParsedFile:
    """Find and validate every Contract-4 marker in `source`. Raises
    MarkerError naming exactly what is wrong (missing, duplicated, or an
    :end whose indentation doesn't match its begin) rather than patching
    around it."""
    lines = source.splitlines()
    config_line = -1
    config_match: re.Match[str] | None = None
    begins: dict[str, int] = {}
    ends: dict[str, int] = {}
    indents: dict[str, tuple[str, str]] = {}

    for i, line in enumerate(lines):
        cm = CONFIG_RE.match(line)
        if cm:
            if config_line != -1:
                raise MarkerError("duplicated pyftc:config header line")
            config_line, config_match = i, cm
            continue
        mm = MARKER_RE.match(line)
        if not mm:
            continue
        region = mm.group("region")
        if region not in REGIONS:
            raise MarkerError(f"unknown marker region {region!r} on line {i + 1}")
        if mm.group("is_end"):
            if region in ends:
                raise MarkerError(f"duplicated pyftc:{region}:end marker")
            ends[region] = i
        else:
            if region in begins:
                raise MarkerError(f"duplicated pyftc:{region} marker")
            begins[region] = i
        indents.setdefault(region, ["", ""])
        idx = 1 if mm.group("is_end") else 0
        indents[region][idx] = mm.group("indent")

    if config_line == -1 or config_match is None:
        raise MarkerError("missing pyftc:config header line")

    regions: dict[str, Region] = {}
    for r in REGIONS:
        if r not in begins:
            raise MarkerError(f"missing pyftc:{r} marker")
        if r not in ends:
            raise MarkerError(f"missing pyftc:{r}:end marker")
        if ends[r] <= begins[r]:
            raise MarkerError(f"pyftc:{r}:end appears before pyftc:{r}")
        begin_indent, end_indent = indents[r]
        if begin_indent != end_indent:
            raise MarkerError(f"pyftc:{r} and pyftc:{r}:end have different indentation")
        regions[r] = Region(begins[r], ends[r], begin_indent)

    return ParsedFile(
        lines=lines,
        config_line=config_line,
        config_name=config_match.group("name"),
        config_fingerprint=config_match.group("fp"),
        config_generated=config_match.group("gen"),
        regions=regions,
    )


def render_config_line(name: str, fingerprint: str, generated: str) -> str:
    return f'# {_DASH * 2} pyftc:config name="{_escape(name)}" fingerprint="{fingerprint}" generated="{generated}" {_DASH * 2}'


def render_begin(region: str, indent: str = "") -> str:
    return f"{indent}# {_DASH * 2} pyftc:{region} {_DASH * 2}"


def render_end(region: str, indent: str = "") -> str:
    return f"{indent}# {_DASH * 2} pyftc:{region}:end {_DASH * 2}"


def apply_edits(pf: ParsedFile, inserts: dict[str, list[str]], fingerprint: str, generated: str) -> str:
    """Insert `inserts[region]` immediately before that region's `:end`
    marker (Contract 4), for every region present in `inserts`, and rewrite
    only the fingerprint/generated values on the config line. Returns the
    whole file. Never touches any other line.

    `inserts[region]` lines are used verbatim - callers must indent them to
    `pf.regions[region].indent` themselves (this function has no opinion on
    indentation beyond preserving what's already there)."""
    lines = list(pf.lines)
    lines[pf.config_line] = render_config_line(pf.config_name, fingerprint, generated)
    # Insert bottom-to-top so earlier line indices in `pf.regions` stay valid
    # for regions not yet processed.
    for region in sorted(inserts, key=lambda r: pf.regions[r].end, reverse=True):
        new_lines = inserts[region]
        if not new_lines:
            continue
        end_idx = pf.regions[region].end
        lines[end_idx:end_idx] = new_lines
    return "\n".join(lines) + "\n"


def insert_above_line(lines: list[str], line_idx: int, new_line: str) -> list[str]:
    """Insert `new_line` immediately above `lines[line_idx]`. Used for the
    'no longer in the configuration' comment (Contract 4) so the field line
    itself is never touched."""
    out = list(lines)
    out[line_idx:line_idx] = [new_line]
    return out


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------------------
# Fingerprint (docs/ARCHITECTURE.md, Contract 3 "Fingerprint")


def compute_fingerprint(config_xml: str) -> str:
    """sha256, truncated to 16 hex chars, over the canonical sorted JSON of
    the configuration's hubs and devices. Deliberately does not touch the SDK
    type database (Contract 3: `config-fingerprint` "never parses the SDK
    type database", so it stays cheap enough to run on every hub refresh, and
    keeps working while another process is regenerating that file).

    The contract's device tuple is `[name, tag, port, bus, hub, hubAddress,
    javaType]`. javaType is normally an SDK lookup from the xml tag, but for a
    fixed SDK version the tag determines it 1:1 - so the tag is reused for
    that slot instead of resolving it. That keeps the shape the contract
    describes without any SDK dependency, and doesn't lose any sensitivity:
    an SDK upgrade changing what a tag maps to is not a "configuration
    change" this fingerprint is trying to catch anyway.
    """
    root = ET.fromstring(config_xml)
    devices: list[list[str]] = []
    hubs: list[list[str]] = []

    def walk(el: ET.Element, hub: str | None, hub_addr: str | None) -> None:
        for child in el:
            tag = child.tag
            name = child.get("name", "")
            if tag == "LynxModule":
                hubs.append([name, child.get("port") or ""])
                walk(child, name, child.get("port"))
            elif len(child):
                walk(child, hub, hub_addr)
            elif tag == "LynxUsbDevice":
                continue
            else:
                devices.append([name, tag, child.get("port") or "", child.get("bus") or "",
                                hub or "", hub_addr or "", tag])

    walk(root, None, None)
    canonical = [sorted(hubs), sorted(devices)]
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
