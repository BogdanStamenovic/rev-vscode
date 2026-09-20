"""`starter-update` (docs/ARCHITECTURE.md, Contract 3 + Contract 4): extend an
existing generated starter pack in place using its marker comments, without
ever rewriting or deleting a line the user wrote.

This module never parses the user's Python with `ast`. The only things that
tell it what's already in the file are markers.py's marker regions and the
small regex parsers below (hardwareMap.get lines, `field: Type` declarations,
hub-header comments, and controls.scan_used's reverse-parse of the loop's
`# "name": ...` comments). Anything those don't recognise - a control comment
a user hand-rewrote into something else, say - is simply invisible to them,
which is the safe direction to be wrong in: worst case a slot looks free when
it secretly isn't, never a deleted line. See controls.scan_used's docstring.

Device identity across an update is by **name only**: the new config.xml is
compared against the device names already recorded in the file's own `init`
region (there is no old config.xml to diff against - starter-update is only
ever given the new one). A rename or a port move is therefore indistinguishable
from a remove-and-add; that's a documented limit, not a bug (see
docs/MANUAL.md).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

from . import manual as manual_mod
from . import markers
from .controls import ControlPlan, free_pools_for_update, plan_added_devices
from .starter import Device, _collect, _device_lines, _field_name, _py_str
from .starter import generate as generate_fresh
from .typedb import TypeDB

_INIT_LOOKUP_RE = re.compile(
    r'^\s*self\.(?P<field>\w+)\s*=\s*self\.hardwareMap\.get\((?P<type>\w+),\s*"(?P<name>(?:[^"\\]|\\.)*)"\)\s*$'
)
_DEVICE_FIELD_RE = re.compile(r'^\s*(?P<field>\w+)\s*:\s*\w+\s*$')
_HUB_HEADER_RE = re.compile(r'^# (?P<hub>.+?) \(address (?P<addr>[^,)]*)(?:,[^)]*)?\)\s*$')
_CLASS_RE = re.compile(r'^class\s+(\w+)\s*\(')
_REMOVED_NOTE = "# pyftc: no longer in the configuration"


def apply_update(db: TypeDB, existing_python: str, config_xml: str, rcinfo: dict[str, Any]) -> dict[str, Any]:
    fingerprint = markers.compute_fingerprint(config_xml)
    class_name = _guess_class_name(existing_python)

    try:
        pf = markers.parse(existing_python)
    except markers.MarkerError as e:
        return {
            "ok": True, "changed": True, "applied": False, "fingerprint": fingerprint,
            "block": generate_fresh(db, config_xml, rcinfo, class_name),
            "added": [], "removed": [], "hubsAdded": [],
            "notes": [f"markers are missing or invalid, so the file was not touched: {e}"],
        }

    changed = pf.config_fingerprint != fingerprint
    if not changed:
        return {
            "ok": True, "changed": False, "applied": True, "fingerprint": fingerprint,
            "python": existing_python,
            "manual": manual_mod.generate(db, config_xml, rcinfo, class_name, fingerprint),
            "added": [], "removed": [], "hubsAdded": [], "notes": [],
        }

    root = ET.fromstring(config_xml)
    new_devices: list[Device] = []
    new_hubs: list[tuple[str, str | None]] = []
    _collect(db, root, None, None, new_devices, new_hubs)

    existing_lookups = _parse_lookups(pf.body("init"))
    existing_names = {name for (_, _, name) in existing_lookups}
    existing_fields = _parse_fields(pf.body("devices")) | {field for (field, _, _) in existing_lookups}
    existing_hubs = _parse_hub_headers(pf.body("hardware"))

    new_by_name = {d.name: d for d in new_devices}
    added_devices = [d for d in new_devices if d.name not in existing_names]
    removed = [(field, name) for (field, _, name) in existing_lookups if name not in new_by_name]
    hubs_added = [(name, addr) for (name, addr) in new_hubs if (name, addr or "") not in existing_hubs]

    used_fields = set(existing_fields)
    for d in added_devices:
        d.field = _field_name(d.name, used_fields)

    loop_text = "\n".join(pf.body("loop"))
    plan = plan_added_devices(added_devices, free_pools_for_update(loop_text))

    inserts = {
        "imports": _new_import_lines(pf.body("imports"), db, added_devices, plan),
        "hardware": _new_hardware_lines(db, added_devices),
        "devices": _new_device_field_lines(db, added_devices, pf.regions["devices"].indent),
        "init": _new_init_lines(db, added_devices, plan, pf.regions["init"].indent),
        "loop": [(pf.regions["loop"].indent + ln) if ln else "" for ln in plan.loop],
    }

    text = markers.apply_edits(pf, inserts, fingerprint, date.today().isoformat())
    if removed:
        text = _flag_removed(text, [field for field, _ in removed], pf.regions["devices"].indent)

    added_out = []
    notes = list(plan.notes)
    for d in added_devices:
        if d.java_type:
            type_name = (db.get(d.java_type) or {}).get("simpleName", d.tag)
        else:
            type_name = d.tag
            notes.append(f'"{d.name}": {d.tag!r} is not a known device type; no field or control was added for it')
        added_out.append({"name": d.name, "field": d.field, "type": type_name,
                          "control": plan.assigned.get(d.field) or ""})
    removed_out = [{"name": name, "field": field} for field, name in removed]
    hubs_added_out = [{"name": name, "address": addr or ""} for name, addr in hubs_added]
    if not added_devices and not removed and not hubs_added:
        notes.append("the configuration fingerprint changed but no device or hub was added or removed - "
                     "likely a rename or a port move, which starter-update can't tell apart from a "
                     "remove-and-add and so leaves alone (see docs/MANUAL.md)")

    return {
        "ok": True, "changed": True, "applied": True, "fingerprint": fingerprint,
        "python": text, "manual": manual_mod.generate(db, config_xml, rcinfo, class_name, fingerprint),
        "added": added_out, "removed": removed_out, "hubsAdded": hubs_added_out, "notes": notes,
    }


def _guess_class_name(source: str) -> str:
    for line in source.splitlines():
        m = _CLASS_RE.match(line.strip())
        if m:
            return m.group(1)
    return "StarterPack"


def _parse_lookups(init_body: list[str]) -> list[tuple[str, str, str]]:
    out = []
    for line in init_body:
        m = _INIT_LOOKUP_RE.match(line)
        if m:
            out.append((m.group("field"), m.group("type"), _unescape(m.group("name"))))
    return out


def _parse_fields(devices_body: list[str]) -> set[str]:
    return {m.group("field") for line in devices_body if (m := _DEVICE_FIELD_RE.match(line))}


def _parse_hub_headers(hardware_body: list[str]) -> set[tuple[str, str]]:
    return {(m.group("hub"), m.group("addr")) for line in hardware_body if (m := _HUB_HEADER_RE.match(line))}


def _new_import_lines(imports_body: list[str], db: TypeDB, added: list[Device], plan: ControlPlan) -> list[str]:
    have: dict[str, set[str]] = {}
    for line in imports_body:
        m = re.match(r'^from (?P<mod>[\w.]+) import (?P<names>.+)$', line.strip())
        if m:
            have.setdefault(m.group("mod"), set()).update(n.strip() for n in m.group("names").split(","))
    needed: dict[str, set[str]] = {mod: set(names) for mod, names in plan.imports.items()}
    for d in added:
        if d.java_type:
            c = db.get(d.java_type) or {}
            if c.get("module"):
                needed.setdefault(c["module"], set()).add(c["simpleName"])
    out = []
    for mod in sorted(needed):
        # A NEW line is added rather than merging into an existing `from mod
        # import ...` line, even when one already exists for this module:
        # editing that line would violate "never rewrite a line the user
        # might have touched" just as much as touching any other line would.
        missing = sorted(n for n in needed[mod] if n not in have.get(mod, set()))
        if missing:
            out.append(f"from {mod} import {', '.join(missing)}")
    return out


def _new_hardware_lines(db: TypeDB, added: list[Device]) -> list[str]:
    out = []
    for d in added:
        hub_ctx = f"{d.hub} (address {d.hub_address})" if d.hub else "not on a hub"
        lines = _device_lines(db, d)
        # Appended devices aren't nested under their hub's header block like
        # a fresh generation's are (that would mean rewriting the hub header
        # line to add them under it) - the hub is named inline instead.
        out.append(f"#   [{hub_ctx}] " + lines[0])
        out.extend("#   " + ln for ln in lines[1:])
    return out


def _new_device_field_lines(db: TypeDB, added: list[Device], indent: str) -> list[str]:
    return [f"{indent}{d.field}: {(db.get(d.java_type) or {}).get('simpleName', 'object')}"
            for d in added if d.java_type]


def _new_init_lines(db: TypeDB, added: list[Device], plan: ControlPlan, indent: str) -> list[str]:
    out = []
    for d in added:
        if not d.java_type:
            out.append(f"{indent}# {d.name!r}: {d.tag} is not a known device type, so it has no Python type")
            continue
        simple = (db.get(d.java_type) or {}).get("simpleName")
        out.append(f'{indent}self.{d.field} = self.hardwareMap.get({simple}, "{_py_str(d.name)}")')
    out.extend((indent + ln) if ln else "" for ln in plan.init)
    out.extend((indent + ln) if ln else "" for ln in plan.before_loop)
    return out


def _flag_removed(text: str, fields: list[str], indent: str) -> str:
    field_re = {f: re.compile(rf'^{re.escape(indent)}{re.escape(f)}\s*:\s*\w+\s*$') for f in fields}
    note = f"{indent}{_REMOVED_NOTE}"
    lines = text.splitlines()
    out: list[str] = []
    flagged: set[str] = set()
    for line in lines:
        for f, rx in field_re.items():
            if f not in flagged and rx.match(line):
                if not out or out[-1] != note:
                    out.append(note)
                flagged.add(f)
                break
        out.append(line)
    return "\n".join(out) + "\n"


def _unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)
