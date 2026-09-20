"""The generated man page (docs/ARCHITECTURE.md, Contract 4, item 4): a
comprehensive per-robot Markdown reference, returned alongside `starter` and
by the standalone `manual` subcommand, and regenerated wholesale by
`starter-update` every time (it carries no markers of its own - only the .py
file's comments are load-bearing enough to need them).

The .py file's own comments stay short on purpose (first sentence of each
javadoc, `SKIP_MEMBERS` trimmed); this is the exhaustive companion: full
javadoc paragraphs, every inherited method grouped by the class that
declares it, and the parts of the picture that don't fit in a comment at all
(the control map, the marker anatomy, where to go for more).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from .controls import plan_controls
from .jtypes import JType
from .starter import (
    SKIP_MEMBERS,
    SKIP_OWNERS,
    Device,
    _collect,
    _field_name,
    _num,
    _py_type,
)
from .typedb import TypeDB


def generate(db: TypeDB, config_xml: str, rcinfo: dict[str, Any], class_name: str, fingerprint: str) -> str:
    root = ET.fromstring(config_xml)
    devices: list[Device] = []
    hubs: list[tuple[str, str | None]] = []
    _collect(db, root, None, None, devices, hubs)
    used: set[str] = set()
    for d in devices:
        d.field = _field_name(d.name, used)

    config_name = rcinfo.get("activeConfigName", "?")
    robot = rcinfo.get("deviceName", "the robot")
    detected = {str(h.get("moduleAddress")): h for h in rcinfo.get("revHubNamesAndVersions", [])}
    controls = plan_controls(devices)

    L: list[str] = []
    L.append(f"# {class_name}: robot reference")
    L.append("")
    L.append(f'Generated from hardware configuration "{config_name}" on {robot}. Configuration '
             f"fingerprint `{fingerprint}` (`python -m pyftc config-fingerprint --config <config.xml>` "
             "on the same configuration reproduces it).")
    L.append("")
    L.append(f"This is generated wholesale every time `{class_name}.py`'s starter pack is spawned or "
             "updated. Unlike the `.py` file it carries no markers, so edit it freely, but don't expect "
             "an edit to survive the next regeneration.")
    L.append("")

    _this_robot(L, config_name, robot, rcinfo, hubs, detected)
    _devices_section(L, db, devices)
    _control_map(L, class_name, controls)
    _anatomy(L, class_name)
    _recipes(L)

    return "\n".join(L) + "\n"


def _this_robot(L: list[str], config_name: str, robot: str, rcinfo: dict[str, Any],
                 hubs: list[tuple[str, str | None]], detected: dict[str, Any]) -> None:
    L.append("## This robot")
    L.append("")
    L.append(f"- Configuration name: `{config_name}`")
    L.append(f"- Device name: `{robot}`")
    if rcinfo.get("rcVersion") or rcinfo.get("sdkVersion"):
        L.append(f"- RC app {rcinfo.get('rcVersion', '?')}, SDK {rcinfo.get('sdkVersion', '?')}, "
                 f"OS {rcinfo.get('chOsVersion', '?')}")
    L.append("")
    if hubs:
        L.append("| Hub | Address | Firmware | Answered when generated |")
        L.append("|---|---|---|---|")
        for hub_name, addr in hubs:
            h = detected.get(addr or "")
            fw = h.get("firmwareVersion", "?") if h else "?"
            L.append(f"| {hub_name} | {addr} | {fw} | {'yes' if h else 'no'} |")
    else:
        L.append("No hubs in this configuration.")
    L.append("")


def _devices_section(L: list[str], db: TypeDB, devices: list[Device]) -> None:
    L.append("## Devices")
    L.append("")
    if not devices:
        L.append("No devices in this configuration.")
        L.append("")
        return
    for d in devices:
        L.append(f'### "{d.name}" -> `self.{d.field}`')
        L.append("")
        where = f"port {d.port}" if d.port is not None else (f"I2C bus {d.bus}" if d.bus is not None else "no port")
        hub_desc = f"{d.hub} (address {d.hub_address})" if d.hub else "not on a hub"
        L.append(f"- Hub: {hub_desc}, {where}")
        simple = None
        if d.java_type:
            simple = (db.get(d.java_type) or {}).get("simpleName", "?")
            L.append(f"- Python type: `{simple}` (`{d.java_type}`)")
        else:
            L.append(f"- Unknown device type (`{d.tag}`): the SDK database has no class for it, so "
                     "the starter pack has no field or hardwareMap lookup for it either.")
        props = d.info.get("props") or {}
        if props.get("ticksPerRev"):
            L.append(f"- {_num(props['ticksPerRev'])} encoder ticks/rev")
        if props.get("maxRPM"):
            L.append(f"- {_num(props['maxRPM'])} max RPM")
        if props.get("gearing"):
            L.append(f"- {_num(props['gearing'])}:1 gearing")
        L.append("")
        if d.java_type and simple:
            L.append(f"Complete `{simple}` method list, own class first then inherited, grouped by the "
                     "class that declares each member (the `.py` file's comments only carry the first "
                     "sentence of each javadoc - this is the whole thing):")
            L.append("")
            groups = _grouped_capabilities(db, d.java_type)
            if not groups:
                L.append("(no methods found in the SDK type database)")
                L.append("")
            for owner, fields, methods in groups:
                L.append(f"**{owner}**")
                L.append("")
                for sig, doc in fields:
                    L.append(f"- `{sig}`" + (f" -- {doc}" if doc else ""))
                for sig, doc in methods:
                    L.append(f"- `{sig}`" + (f" -- {doc}" if doc else ""))
                L.append("")


def _control_map(L: list[str], class_name: str, controls) -> None:
    L.append("## Control map")
    L.append("")
    for line in controls.table:
        L.append(f"- {line}")
    L.append("")
    L.append(f"To change any of this: edit the code between `# ── pyftc:loop ──` and "
             f"`# ── pyftc:loop:end ──` in `{class_name}.py` directly (see \"Anatomy\" "
             "below for what else lives in there), or adjust `DRIVE_POWER`, `MECHANISM_POWER` and "
             "`SERVO_STEP` at the top of the class to change speed without touching which control does "
             "what.")
    L.append("")


def _anatomy(L: list[str], class_name: str) -> None:
    L.append("## Anatomy of the generated file")
    L.append("")
    L.append("Five marker regions, each a `# ── pyftc:<region> ──` / "
             "`# ── pyftc:<region>:end ──` pair of comments "
             "(docs/ARCHITECTURE.md, \"Contract 4\"):")
    L.append("")
    L.append("| Region | What lives there | Runs at |")
    L.append("|---|---|---|")
    L.append("| `imports` | `from ftc.* import ...` lines the devices and controls need | import time |")
    L.append("| `hardware` | the per-hub, per-device description comments | (comment only) |")
    L.append("| `devices` | one `field: Type` class attribute per known device | class body |")
    L.append("| `init` | `hardwareMap.get(...)` lookups, direction/IMU setup, servo starting "
             "positions | INIT |")
    L.append("| `loop` | the gamepad control code for each device | START, every iteration |")
    L.append("")
    L.append("Everything above `waitForStart()` runs once, when INIT is pressed. The "
             "`while self.opModeIsActive():` body runs every iteration from START until STOP.")
    L.append("")
    L.append("**Do not delete the marker comments.** `starter-update` finds them by exact text match "
             "and refuses to touch the file at all if any is missing or duplicated - it will not guess "
             "where your code ends and generated code begins; it hands back the new code separately "
             "instead (as `block` in the CLI's JSON) for you to place by hand. Renaming fields, "
             "reordering devices, rewriting the control logic: all fine, none of it touches the marker "
             "lines themselves. Just leave those comment lines alone.")
    L.append("")
    L.append(f"When the hardware configuration changes and you re-run *Spawn starter pack* on "
             f"`{class_name}.py` (or `starter-update` directly):")
    L.append("")
    L.append("- a **new device** gets a field, a `hardwareMap` lookup, a gamepad control (if one is "
             "still free) and a hardware-comment line, each inserted immediately before its region's "
             "`:end` marker - after everything already there, never in the middle of it;")
    L.append("- a **removed device**'s field is never deleted - it gets a "
             "`# pyftc: no longer in the configuration` comment above it instead, so code you wrote "
             "using it still shows up as a diff instead of silently vanishing;")
    L.append("- a device that's merely **renamed or moved to a different port** is not detected as "
             "\"the same device\" - matching is by name only, so this looks like an old device removed "
             "and a new one added;")
    L.append("- descriptive comments about the old configuration (including a stale \"no devices\" "
             "banner on a configuration that used to be empty) are never rewritten either - if one no "
             "longer matches reality, that's the trade-off for never eating your edits.")
    L.append("")


def _recipes(L: list[str]) -> None:
    L.append("## Recipes and limits")
    L.append("")
    L.append("Adding a device by hand instead of re-spawning: declare a field, "
             "`self.hardwareMap.get(...)` it in `runOpMode`, and drive it however you like - "
             '[docs/MANUAL.md](docs/MANUAL.md), section 3 ("Adding any device: the recipe"), has the '
             "full walkthrough.")
    L.append("")
    L.append("What Python the translator accepts and rejects, build/translation troubleshooting, "
             "autonomous, organizing code across files: all in [docs/MANUAL.md](docs/MANUAL.md) in the "
             "rev-vscode repository. This page is generated per-robot and intentionally doesn't repeat "
             "any of that.")
    L.append("")


def _grouped_capabilities(db: TypeDB, fqn: str) -> list[tuple[str, list[tuple[str, str]], list[tuple[str, str]]]]:
    """Like starter._capabilities, but never truncates javadoc and groups by
    the class that declares each member instead of flattening the chain -
    that's the whole point of the man page over the .py comments."""
    seen_methods: set[tuple[str, int]] = set()
    seen_fields: set[str] = set()
    groups: list[tuple[str, list[tuple[str, str]], list[tuple[str, str]]]] = []
    chain = [JType(fqn), *db.supertypes(JType(fqn))]
    for t in chain:
        if t.name in SKIP_OWNERS:
            continue
        c = db.get(t.name)
        if not c:
            continue
        fields: list[tuple[str, str]] = []
        for f in c.get("fields", []):
            if f.get("static") or f["name"] in SKIP_MEMBERS or f["name"] in seen_fields:
                continue
            seen_fields.add(f["name"])
            fields.append((f"{f['name']}: {_py_type(f['type'])}", " ".join(f.get("doc", "").split())))
        methods: list[tuple[str, str]] = []
        for m in c.get("methods", []):
            if m.get("static"):
                continue
            key = (m["name"], len(m["params"]))
            if key in seen_methods or m["name"] in SKIP_MEMBERS:
                continue
            seen_methods.add(key)
            params = ", ".join(f"{p['name']}: {_py_type(p['type'])}" for p in m["params"])
            ret = _py_type(m["returns"])
            sig = f"{m['name']}({params})" + ("" if ret == "None" else f" -> {ret}")
            methods.append((sig, " ".join(m.get("doc", "").split())))
        if fields or methods:
            groups.append((c.get("simpleName", t.simple), fields, methods))
    return groups
