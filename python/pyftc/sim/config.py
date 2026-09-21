"""The robot configuration the simulator builds its hardware from.

Sources, in the order the extension tries them: the hub's active configuration
XML (fetched over adb by the extension), a configuration XML in the workspace,
or, with no hub and no XML, the device list a generated starter pack carries in
its `pyftc:hardware` marker block (Contract 4), which names every device with
its hub, port and type.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .. import markers
from ..typedb import TypeDB

CONTROL_HUB_ADDRESS = 173


def from_xml(db: TypeDB, xml: str, name: str, source: str) -> dict[str, Any]:
    root = ET.fromstring(xml)
    hubs: list[dict[str, Any]] = []
    devices: list[dict[str, Any]] = []
    _walk(db, root, None, hubs, devices)
    return {"name": name, "source": source, "hubs": hubs, "devices": devices}


def _walk(db: TypeDB, el: ET.Element, hub: str | None, hubs: list, devices: list) -> None:
    for child in el:
        tag = child.tag
        if tag == "LynxModule":
            port = child.get("port")
            address = int(port) if port and port.isdigit() else None
            hubs.append({"name": child.get("name", ""), "address": address,
                         "kind": "ControlHub" if address == CONTROL_HUB_ADDRESS else "ExpansionHub"})
            _walk(db, child, child.get("name", ""), hubs, devices)
        elif len(child):
            _walk(db, child, hub, hubs, devices)
        elif tag in ("LynxUsbDevice",):
            continue
        else:
            devices.append(_device(db, tag, child.get("name", ""), hub, child.get("port"), child.get("bus")))


def _device(db: TypeDB, tag: str, name: str, hub: str | None, port: str | None, bus: str | None) -> dict[str, Any]:
    info = db.xml_tags.get(tag, {})
    return {"name": name, "tag": tag, "hub": hub, "port": port, "bus": bus,
            "category": info.get("category"), "javaType": info.get("javaType"),
            "displayName": info.get("displayName"), "props": info.get("props") or {}}


HUB_LINE = re.compile(r"^# (?P<name>.+?) \(address (?P<address>\d+)")
DEVICE_LINE = re.compile(r'^#   "(?P<name>(?:[^"\\]|\\.)*)" -> self\.\w+: \S+\s+\((?P<display>.+), (?P<where>port \d+|I2C bus \d+|no port)\)\s*$')


def from_starter(db: TypeDB, source: str) -> dict[str, Any] | None:
    """Rebuild the configuration from a starter pack's hardware marker block, or None
    if the file has no such block."""
    lines = source.splitlines()
    try:
        begin = next(i for i, ln in enumerate(lines) if markers.render_begin("hardware") in ln)
        end = next(i for i, ln in enumerate(lines) if markers.render_end("hardware") in ln)
    except StopIteration:
        return None
    config_line = next((ln for ln in lines if "pyftc:config" in ln), "")
    m = re.search(r'name="([^"]*)"', config_line)
    by_display = {v.get("displayName"): tag for tag, v in db.xml_tags.items()}
    hubs: list[dict[str, Any]] = []
    devices: list[dict[str, Any]] = []
    current: str | None = None
    for ln in lines[begin + 1:end]:
        h = HUB_LINE.match(ln)
        if h and not ln.startswith("#   "):
            address = int(h.group("address"))
            current = h.group("name")
            hubs.append({"name": current, "address": address,
                         "kind": "ControlHub" if address == CONTROL_HUB_ADDRESS else "ExpansionHub"})
            continue
        if ln.startswith("# Other devices"):
            current = None
            continue
        d = DEVICE_LINE.match(ln)
        if not d:
            continue
        tag = by_display.get(d.group("display"))
        if tag is None:
            continue
        where = d.group("where")
        port = where.split()[-1] if where.startswith("port") else None
        bus = where.split()[-1] if where.startswith("I2C") else None
        name = d.group("name").replace('\\"', '"').replace("\\\\", "\\")
        devices.append(_device(db, tag, name, current, port, bus))
    return {"name": m.group(1) if m else "starter pack", "source": "starter", "hubs": hubs, "devices": devices}


def find_in_workspace(db: TypeDB, root: Path, sources: list[Path]) -> dict[str, Any] | None:
    """A configuration XML in the workspace, else one rebuilt from a starter pack."""
    for xml_path in sorted(root.rglob("*.xml")):
        if any(part.startswith(".") for part in xml_path.relative_to(root).parts[:-1]):
            continue
        try:
            text = xml_path.read_text()
            if "<Robot" in text and "LynxModule" in text:
                return from_xml(db, text, xml_path.stem, f"file:{xml_path}")
        except (OSError, ET.ParseError):
            continue
    for py in sources:
        try:
            cfg = from_starter(db, py.read_text())
        except OSError:
            continue
        if cfg and cfg["devices"]:
            cfg["source"] = f"starter:{py}"
            return cfg
    return None
