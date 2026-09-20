"""markers.py: Contract 4's marker parsing/insertion, and the Contract 3
fingerprint. These are the load-bearing primitives starter-update depends on
(see test_update.py for the end-to-end behavior); this file pins down their
contract in isolation, including the "strict: refuse, don't guess" rule."""

from __future__ import annotations

import pytest

from pyftc import markers

GOOD = '''"""doc"""

# ── pyftc:config name="X" fingerprint="0123456789abcdef" generated="2026-09-20" ──

# ── pyftc:imports ──
from ftc.opmode import LinearOpMode, TeleOp
# ── pyftc:imports:end ──


# ── pyftc:hardware ──
# Control Hub (address 173)
#   "m" -> self.m: DcMotor
# ── pyftc:hardware:end ──
#

class X(LinearOpMode):
    # ── pyftc:devices ──
    m: DcMotor
    # ── pyftc:devices:end ──

    def runOpMode(self) -> None:
        # ── pyftc:init ──
        self.m = self.hardwareMap.get(DcMotor, "m")
        # ── pyftc:init:end ──
        self.waitForStart()
        while self.opModeIsActive():
            # ── pyftc:loop ──
            self.m.setPower(1)
            # ── pyftc:loop:end ──
'''


def test_parse_finds_config_header_and_all_five_regions():
    pf = markers.parse(GOOD)
    assert pf.config_name == "X"
    assert pf.config_fingerprint == "0123456789abcdef"
    assert pf.config_generated == "2026-09-20"
    assert set(pf.regions) == set(markers.REGIONS) == {"imports", "hardware", "devices", "init", "loop"}


def test_region_body_is_exactly_between_the_markers():
    pf = markers.parse(GOOD)
    assert pf.body("imports") == ["from ftc.opmode import LinearOpMode, TeleOp"]
    assert pf.body("loop") == ["            self.m.setPower(1)"]


def test_region_indent_recorded_per_contract_4_diagram():
    pf = markers.parse(GOOD)
    assert pf.regions["imports"].indent == ""
    assert pf.regions["hardware"].indent == ""
    assert pf.regions["devices"].indent == "    "
    assert pf.regions["init"].indent == "        "
    assert pf.regions["loop"].indent == "            "


@pytest.mark.parametrize("region", markers.REGIONS)
def test_missing_begin_marker_is_an_error(region):
    line = next(l for l in GOOD.splitlines() if f"pyftc:{region}" in l and "end" not in l)
    broken = GOOD.replace(line, "# nothing here", 1)
    with pytest.raises(markers.MarkerError, match=region):
        markers.parse(broken)


@pytest.mark.parametrize("region", markers.REGIONS)
def test_missing_end_marker_is_an_error(region):
    line = next(l for l in GOOD.splitlines() if f"pyftc:{region}:end" in l)
    broken = GOOD.replace(line, "# nothing here", 1)
    with pytest.raises(markers.MarkerError, match=region):
        markers.parse(broken)


def test_duplicated_begin_marker_is_an_error():
    broken = GOOD.replace(
        "# ── pyftc:imports ──\n",
        "# ── pyftc:imports ──\n# ── pyftc:imports ──\n",
        1,
    )
    with pytest.raises(markers.MarkerError, match="duplicat"):
        markers.parse(broken)


def test_duplicated_end_marker_is_an_error():
    broken = GOOD.replace(
        "# ── pyftc:imports:end ──",
        "# ── pyftc:imports:end ──\n# ── pyftc:imports:end ──",
        1,
    )
    with pytest.raises(markers.MarkerError, match="duplicat"):
        markers.parse(broken)


def test_missing_config_header_is_an_error():
    broken = "\n".join(l for l in GOOD.splitlines() if "pyftc:config" not in l)
    with pytest.raises(markers.MarkerError, match="config"):
        markers.parse(broken)


def test_duplicated_config_header_is_an_error():
    config_line = next(l for l in GOOD.splitlines() if "pyftc:config" in l)
    broken = GOOD.replace(config_line, config_line + "\n" + config_line, 1)
    with pytest.raises(markers.MarkerError, match="config"):
        markers.parse(broken)


def test_mismatched_begin_end_indent_is_an_error():
    broken = GOOD.replace("    # ── pyftc:devices:end ──", "        # ── pyftc:devices:end ──", 1)
    with pytest.raises(markers.MarkerError, match="indent"):
        markers.parse(broken)


# ---------------------------------------------------------------------------
# apply_edits: insertion + header rewrite, nothing else


def test_insert_before_end_lands_immediately_above_end_marker():
    pf = markers.parse(GOOD)
    text = markers.apply_edits(pf, {"devices": ["    n: Servo"]}, "abc0123456789def", "2026-09-21")
    lines = text.splitlines()
    end_idx = next(i for i, l in enumerate(lines) if "pyftc:devices:end" in l)
    assert lines[end_idx - 1] == "    n: Servo"


def test_apply_edits_rewrites_only_fingerprint_and_generated_on_header():
    pf = markers.parse(GOOD)
    text = markers.apply_edits(pf, {}, "fedcba9876543210", "2099-01-01")
    assert 'name="X"' in text
    assert 'fingerprint="fedcba9876543210"' in text
    assert 'generated="2099-01-01"' in text
    assert 'fingerprint="0123456789abcdef"' not in text


def test_apply_edits_with_no_inserts_changes_nothing_but_the_header():
    pf = markers.parse(GOOD)
    text = markers.apply_edits(pf, {}, pf.config_fingerprint, pf.config_generated)
    assert text == GOOD.rstrip("\n") + "\n" or text.splitlines() == GOOD.splitlines()


def test_apply_edits_into_multiple_regions_does_not_shift_earlier_regions():
    pf = markers.parse(GOOD)
    text = markers.apply_edits(
        pf,
        {"imports": ["from ftc.hardware import Servo"], "loop": ["            self.m.setPower(0)"]},
        pf.config_fingerprint, pf.config_generated,
    )
    pf2 = markers.parse(text)
    assert pf2.body("imports")[-1] == "from ftc.hardware import Servo"
    assert pf2.body("loop")[-1] == "            self.m.setPower(0)"
    assert pf2.body("hardware") == pf.body("hardware")
    assert pf2.body("devices") == pf.body("devices")


# ---------------------------------------------------------------------------
# Fingerprint (Contract 3)

XML = '''<Robot type="FirstInspires-FTC">
  <LynxUsbDevice name="p" serialNumber="(embedded)" parentModuleAddress="173">
    <LynxModule name="Control Hub" port="173">
      <RevRoboticsCoreHexMotor name="Kombjan" port="0" />
    </LynxModule>
  </LynxUsbDevice>
</Robot>'''


def test_fingerprint_is_16_hex_chars():
    fp = markers.compute_fingerprint(XML)
    assert len(fp) == 16
    int(fp, 16)  # doesn't raise


def test_fingerprint_is_stable():
    assert markers.compute_fingerprint(XML) == markers.compute_fingerprint(XML)


def test_fingerprint_signature_takes_no_rcinfo():
    # A hub going offline (rcInfo changing) can't move the fingerprint if the
    # function computing it never even accepts rcInfo as input.
    import inspect
    params = list(inspect.signature(markers.compute_fingerprint).parameters)
    assert params == ["config_xml"]


def test_fingerprint_changes_on_rename():
    renamed = XML.replace("Kombjan", "Kombjan2")
    assert markers.compute_fingerprint(XML) != markers.compute_fingerprint(renamed)


def test_fingerprint_changes_on_port_move():
    moved = XML.replace('port="0"', 'port="1"')
    assert markers.compute_fingerprint(XML) != markers.compute_fingerprint(moved)


def test_fingerprint_changes_on_add():
    added = XML.replace(
        "</LynxModule>",
        '<RevRoboticsCoreHexMotor name="Second" port="1" /></LynxModule>',
    )
    assert markers.compute_fingerprint(XML) != markers.compute_fingerprint(added)


def test_fingerprint_changes_on_remove():
    removed = XML.replace('<RevRoboticsCoreHexMotor name="Kombjan" port="0" />\n', "")
    assert markers.compute_fingerprint(XML) != markers.compute_fingerprint(removed)


def test_fingerprint_changes_on_new_expansion_hub():
    added_hub = XML.replace(
        "</LynxUsbDevice>",
        '<LynxModule name="Expansion Hub 2" port="2" /></LynxUsbDevice>',
    )
    assert markers.compute_fingerprint(XML) != markers.compute_fingerprint(added_hub)


def test_fingerprint_matches_starter_generate():
    # starter.generate() embeds a fingerprint into the config header line via
    # the exact same function - the CLI's `starter` and `config-fingerprint`
    # commands must never disagree about a given config.xml.
    import json
    from pathlib import Path

    from pyftc.starter import generate
    from pyftc.typedb import TypeDB

    sdk_db = Path(__file__).resolve().parents[1] / "pyftc" / "data" / "sdk-11.2.0.json"
    if not sdk_db.exists():
        pytest.skip("generated SDK database missing; run sdkgen")
    db = TypeDB(json.loads(sdk_db.read_text()))
    src = generate(db, XML, {}, "Robot")
    pf = markers.parse(src)
    assert pf.config_fingerprint == markers.compute_fingerprint(XML)
