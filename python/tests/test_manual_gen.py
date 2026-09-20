"""manual.py: the generated man page (docs/ARCHITECTURE.md Contract 4, item
4), on the three real-shaped fixtures test_starter.py also uses."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyftc.manual import generate
from pyftc.markers import compute_fingerprint
from pyftc.typedb import TypeDB

FIXTURES = Path(__file__).parent / "fixtures"
SDK_DB = Path(__file__).resolve().parents[1] / "pyftc" / "data" / "sdk-11.2.0.json"
RCINFO = json.loads((FIXTURES / "rcInfo.json").read_text())

pytestmark = pytest.mark.skipif(not SDK_DB.exists(), reason="generated SDK database missing; run sdkgen")


@pytest.fixture(scope="module")
def sdk() -> TypeDB:
    return TypeDB(json.loads(SDK_DB.read_text()))


def build(sdk: TypeDB, config: str) -> str:
    config_xml = (FIXTURES / f"{config}.xml").read_text()
    fp = compute_fingerprint(config_xml)
    return generate(sdk, config_xml, RCINFO, f"{config}Starter", fp)


@pytest.mark.parametrize("config", ["Galerija", "Mixed", "Empty"])
def test_manual_has_the_required_sections(sdk, config):
    md = build(sdk, config)
    assert md.startswith(f"# {config}Starter: robot reference")
    for heading in ("## This robot", "## Devices", "## Control map",
                    "## Anatomy of the generated file", "## Recipes and limits"):
        assert heading in md, f"{config}: missing section {heading!r}"


@pytest.mark.parametrize("config", ["Galerija", "Mixed"])
def test_manual_lists_every_device_by_name_and_field(sdk, config):
    from pyftc.starter import Device, _collect, _field_name
    import xml.etree.ElementTree as ET

    md = build(sdk, config)
    root = ET.fromstring((FIXTURES / f"{config}.xml").read_text())
    devices: list[Device] = []
    hubs: list[tuple[str, str | None]] = []
    _collect(sdk, root, None, None, devices, hubs)
    used: set[str] = set()
    for d in devices:
        d.field = _field_name(d.name, used)
    for d in devices:
        assert f'"{d.name}" -> `self.{d.field}`' in md


def test_manual_carries_full_javadoc_not_the_py_comments_truncation(sdk):
    md = build(sdk, "Galerija")
    # setPowerFloat's javadoc is several sentences; starter.py's own comment
    # would truncate to the first one. The man page must carry more of it.
    assert "This is a breaking change in behavior from previous releases" in md


def test_manual_groups_inherited_methods_by_declaring_class(sdk):
    md = build(sdk, "Galerija")
    devices_section = md.split("## Devices", 1)[1].split("## Control map", 1)[0]
    # DcMotor extends DcMotorSimple extends HardwareDevice: methods declared
    # on the ancestors must appear under their own class heading, not folded
    # into DcMotor's.
    assert "**DcMotor**" in devices_section
    assert "**DcMotorSimple**" in devices_section
    assert "**HardwareDevice**" in devices_section
    assert "setPower(power: float)" in devices_section  # DcMotorSimple


def test_manual_control_map_matches_starter_pack_table(sdk):
    from pyftc.controls import plan_controls
    from pyftc.starter import Device, _collect, _field_name
    import xml.etree.ElementTree as ET

    md = build(sdk, "Galerija")
    root = ET.fromstring((FIXTURES / "Galerija.xml").read_text())
    devices: list[Device] = []
    hubs: list[tuple[str, str | None]] = []
    _collect(sdk, root, None, None, devices, hubs)
    used: set[str] = set()
    for d in devices:
        d.field = _field_name(d.name, used)
    controls = plan_controls(devices)
    control_section = md.split("## Control map", 1)[1].split("## Anatomy", 1)[0]
    for line in controls.table:
        assert line in control_section


def test_manual_links_to_docs_manual_instead_of_duplicating_it(sdk):
    md = build(sdk, "Mixed")
    recipes = md.split("## Recipes and limits", 1)[1]
    assert "docs/MANUAL.md" in recipes
    # It's a pointer, not a rewrite: the cheat-sheet/troubleshooting prose
    # itself shouldn't be duplicated here.
    assert "Not supported" not in recipes
    assert "translate-project" not in recipes


def test_manual_mentions_marker_regions_by_exact_name(sdk):
    md = build(sdk, "Galerija")
    anatomy = md.split("## Anatomy of the generated file", 1)[1].split("## Recipes", 1)[0]
    for region in ("imports", "hardware", "devices", "init", "loop"):
        assert f"`{region}`" in anatomy


def test_manual_notes_removed_devices_never_get_deleted(sdk):
    md = build(sdk, "Galerija")
    anatomy = md.split("## Anatomy of the generated file", 1)[1]
    assert "no longer in the configuration" in anatomy


def test_empty_config_manual_says_so(sdk):
    md = build(sdk, "Empty")
    assert "No devices in this configuration." in md
    assert "No hubs in this configuration." not in md  # Empty.xml still has a Control Hub, just no devices on it


def test_manual_fingerprint_matches_config(sdk):
    config_xml = (FIXTURES / "Galerija.xml").read_text()
    fp = compute_fingerprint(config_xml)
    md = generate(sdk, config_xml, RCINFO, "GalerijaStarter", fp)
    assert fp in md


def test_manual_hub_table_reports_which_hubs_answered(sdk):
    md = build(sdk, "Galerija")
    this_robot = md.split("## This robot", 1)[1].split("## Devices", 1)[0]
    # rcInfo.json only lists the Control Hub as having answered; Expansion Hub 2 didn't.
    assert "| Control Hub | 173 | 1.8.2 | yes |" in this_robot
    assert "| Expansion Hub 2 | 2 | ? | no |" in this_robot
