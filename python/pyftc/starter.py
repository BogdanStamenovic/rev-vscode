"""Starter OpMode generated from the hub's active hardware configuration: a
field and a hardwareMap lookup per configured device, with comments listing
where each device is plugged in and everything its Java type can do."""

from __future__ import annotations

import keyword
import re
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from typing import Any

from .controls import plan_controls
from .jtypes import JType, parse_type
from .translate import JAVA_KEYWORDS
from .typedb import TypeDB

# Supertypes whose methods are noise in a capability list.
SKIP_OWNERS = {"java.lang.Object"}
HW = "com.qualcomm.robotcore.hardware"
# Gamepad internals that are public in Java but useless (or misleading) to a driver.
SKIP_MEMBERS = {"ledQueue", "rumbleQueue", "nextRumbleApproxFinishTime", "userForEffects", "user", "id",
                "timestamp", "type", "copy", "fromByteArray", "toByteArray", "getRobocolMsgType",
                "setGamepadId", "getGamepadId", "setUser", "getUser", "setTimestamp", "refreshTimestamp",
                "updateButtonAliases", "copyFrom", "reset", "setJoystickDeadzone", "atRest", "toString",
                "getGamepadType", "type()"}
PY_TYPES = {"double": "float", "float": "float", "int": "int", "long": "int", "short": "int", "byte": "int",
            "boolean": "bool", "java.lang.String": "str", "void": "None", "char": "str",
            "java.lang.CharSequence": "str"}


@dataclass
class Device:
    name: str
    tag: str
    port: str | None
    bus: str | None
    hub: str | None
    hub_address: str | None
    java_type: str | None
    info: dict[str, Any]
    field: str = ""


def generate(db: TypeDB, config_xml: str, rcinfo: dict[str, Any], class_name: str) -> str:
    if not class_name.isidentifier() or keyword.iskeyword(class_name) or class_name in JAVA_KEYWORDS:
        raise ValueError(f"'{class_name}' is not a valid class name")
    root = ET.fromstring(config_xml)
    devices: list[Device] = []
    hubs: list[tuple[str, str | None]] = []
    _collect(db, root, None, None, devices, hubs)

    used: set[str] = set()
    for d in devices:
        d.field = _field_name(d.name, used)

    detected = {str(h.get("moduleAddress")): h for h in rcinfo.get("revHubNamesAndVersions", [])}
    config_name = rcinfo.get("activeConfigName", "?")
    robot = rcinfo.get("deviceName", "the robot")

    L: list[str] = []
    L.append(f'"""Starter pack for {robot}, generated {date.today().isoformat()} from hardware configuration '
             f'"{config_name}".')
    L.append("")
    L.append("Press INIT on the Driver Hub: everything above waitForStart() runs once.")
    L.append("Press START: the while loop runs until STOP.")
    L.append('"""')
    L.append("")

    controls = plan_controls(devices)
    imports: dict[str, set[str]] = {"ftc.opmode": {"LinearOpMode", "TeleOp"}}
    for mod, names in controls.imports.items():
        imports.setdefault(mod, set()).update(names)
    for d in devices:
        if d.java_type:
            c = db.get(d.java_type) or {}
            if c.get("module"):
                imports.setdefault(c["module"], set()).add(c["simpleName"])
    for mod in sorted(imports):
        L.append(f"from {mod} import {', '.join(sorted(imports[mod]))}")
    L.append("")
    L.append("")

    L.append("# ── Gamepad controls " + "─" * 57)
    L.extend(f"#   {line}" for line in controls.table)
    L.append("#")
    L.append("# ── Connected hardware " + "─" * 55)
    if not hubs and not devices:
        L.append("# The active configuration has no devices. Configure the robot on the Driver Hub first.")
    for hub_name, addr in hubs:
        status = ""
        if rcinfo:
            h = detected.get(addr or "")
            status = f", firmware {h.get('firmwareVersion')}, connected" if h else ", NOT detected right now"
        L.append(f"# {hub_name} (address {addr}{status})")
        for d in [d for d in devices if d.hub_address == addr and d.hub == hub_name]:
            L.extend("#   " + line for line in _device_lines(db, d))
    loose = [d for d in devices if d.hub is None]
    if loose:
        L.append("# Other devices")
        for d in loose:
            L.extend("#   " + line for line in _device_lines(db, d))
    L.append("#")

    types_seen: list[str] = []
    for d in devices:
        if d.java_type and d.java_type not in types_seen:
            types_seen.append(d.java_type)
    types_seen.append(f"{HW}.Gamepad")
    for fqn in types_seen:
        simple = fqn.rsplit(".", 1)[-1]
        article = "an" if simple[0] in "AEIOU" else "a"
        L.append(f"# ── What {article} {simple} can do " + "─" * max(4, 57 - len(article) - len(simple)))
        L.extend(f"#   {line}" for line in _capabilities(db, fqn))
        L.append("#")
    if L[-1] == "#":
        L.pop()
    L.append("")
    L.append("")

    L.append(f'@TeleOp(name="{_title(class_name)}", group="pyftc")')
    L.append(f"class {class_name}(LinearOpMode):")
    for d in devices:
        if d.java_type:
            L.append(f"    {d.field}: {(db.get(d.java_type) or {}).get('simpleName', 'object')}")
    L.append("")
    L.extend(controls.constants)
    L.append("")
    L.append("    def runOpMode(self) -> None:")
    L.append("        # ── On ready: runs once when INIT is pressed ──")
    for d in devices:
        if not d.java_type:
            L.append(f"        # {d.name!r}: {d.tag} is not a known device type, so it has no Python type")
            continue
        simple = (db.get(d.java_type) or {}).get("simpleName")
        L.append(f'        self.{d.field} = self.hardwareMap.get({simple}, "{_py_str(d.name)}")')
    L.extend(("        " + ln) if ln else "" for ln in controls.init)
    L.append("")
    L.append('        self.telemetry.addLine("Ready. Press START.")')
    L.append("        self.telemetry.update()")
    L.append("        self.waitForStart()")
    L.append("")
    L.append("        # ── On start: loops until STOP is pressed ──")
    L.extend("        " + ln for ln in controls.before_loop)
    L.append("        while self.opModeIsActive():")
    L.extend(("            " + ln) if ln else "" for ln in controls.loop)
    L.append('            self.telemetry.addData("Runtime", f"{self.getRuntime():.1f} s")')
    L.append("            self.telemetry.update()")
    return "\n".join(L) + "\n"


def _collect(db: TypeDB, el: ET.Element, hub: str | None, hub_addr: str | None,
             devices: list[Device], hubs: list[tuple[str, str | None]]) -> None:
    for child in el:
        tag = child.tag
        name = child.get("name", "")
        if tag == "LynxModule":
            hubs.append((name, child.get("port")))
            _collect(db, child, name, child.get("port"), devices, hubs)
        elif len(child):
            _collect(db, child, hub, hub_addr, devices, hubs)
        elif tag == "LynxUsbDevice":
            continue
        else:
            info = db.xml_tags.get(tag, {})
            java_type = info.get("javaType")
            if java_type and java_type not in db.classes:
                java_type = None
            devices.append(Device(name, tag, child.get("port"), child.get("bus"), hub, hub_addr, java_type, info))


def _device_lines(db: TypeDB, d: Device) -> list[str]:
    where = []
    if d.bus is not None and d.info.get("category") in ("i2c", "imu"):
        where.append(f"I2C bus {d.bus}")
    elif d.port is not None:
        where.append(f"port {d.port}")
    t = (db.get(d.java_type) or {}).get("simpleName") if d.java_type else None
    title = d.info.get("displayName") or d.tag
    lines = [f'"{d.name}" -> self.{d.field}: {t or "unknown type"}  ({title}, {", ".join(where) or "no port"})']
    props = d.info.get("props") or {}
    extras = []
    if props.get("ticksPerRev"):
        extras.append(f"{_num(props['ticksPerRev'])} encoder ticks/rev")
    if props.get("maxRPM"):
        extras.append(f"{_num(props['maxRPM'])} max RPM")
    if props.get("gearing"):
        extras.append(f"{_num(props['gearing'])}:1 gearing")
    if extras:
        lines.append("    " + ", ".join(extras))
    return lines


def _capabilities(db: TypeDB, fqn: str) -> list[str]:
    seen: set[tuple[str, int]] = set()
    rows: list[tuple[str, str]] = []
    chain = [JType(fqn), *db.supertypes(JType(fqn))]
    for t in chain:
        if t.name in SKIP_OWNERS:
            continue
        c = db.get(t.name)
        if not c:
            continue
        for m in c.get("methods", []):
            if m.get("static"):
                continue
            key = (m["name"], len(m["params"]))
            if key in seen or m["name"] in SKIP_MEMBERS:
                continue
            seen.add(key)
            params = ", ".join(f"{p['name']}: {_py_type(p['type'])}" for p in m["params"])
            ret = _py_type(m["returns"])
            sig = f"{m['name']}({params})" + ("" if ret == "None" else f" -> {ret}")
            rows.append((sig, _first_sentence(m.get("doc", ""))))
    for f in (db.get(fqn) or {}).get("fields", []):
        if not f.get("static") and f["name"] not in SKIP_MEMBERS:
            rows.append((f"{f['name']}: {_py_type(f['type'])}", _first_sentence(f.get("doc", ""))))
    out = []
    for sig, doc in rows:
        out.append(sig)
        if doc:
            out.extend("    " + w for w in textwrap.wrap(doc, 72))
    return out or ["(no methods found in the SDK type database)"]


def _py_type(text: str) -> str:
    try:
        t = parse_type(text)
    except ValueError:
        return text
    if t.dims:
        return f"list[{_py_type(str(JType(t.name, t.args)))}]"
    if t.name in PY_TYPES:
        return PY_TYPES[t.name]
    if t.name == "java.util.List" and t.args:
        return f"list[{_py_type(str(t.args[0]))}]"
    return t.simple


def _first_sentence(doc: str) -> str:
    doc = " ".join(doc.split())
    m = re.match(r"(.+?[.!?])(\s|$)", doc)
    s = m.group(1) if m else doc
    return s if len(s) <= 140 else s[:137] + "..."


def _field_name(name: str, used: set[str]) -> str:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)  # frontLeft -> front_Left
    base = re.sub(r"[^0-9a-zA-Z]+", "_", spaced).strip("_").lower() or "device"
    if base[0].isdigit():
        base = "d_" + base
    if keyword.iskeyword(base) or base in JAVA_KEYWORDS or base in {"telemetry", "gamepad1", "gamepad2", "hardwareMap"}:
        base += "_"
    out, i = base, 2
    while out in used:
        out, i = f"{base}_{i}", i + 1
    used.add(out)
    return out


def _title(class_name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", class_name)


def _py_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _num(v: Any) -> str:
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
