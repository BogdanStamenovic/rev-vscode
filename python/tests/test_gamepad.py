"""No physical controller is required for any of these: capabilities are
built by hand and event streams come from tests/fixtures/gamepad/*.bin
(generated once via struct.pack, not regenerated at test time), so the
suite runs the same on CI as on a workstation with a gamepad plugged in."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pyftc import gamepad as g  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "gamepad"


def read_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def xbox_caps() -> g.DeviceCaps:
    return g.DeviceCaps(
        path="/dev/input/event0", name="Xbox 360 Controller", vendor=0x045E, product=0x028E,
        abs_ranges={
            g.ABS_X: (-32768, 32767), g.ABS_Y: (-32768, 32767),
            g.ABS_RX: (-32768, 32767), g.ABS_RY: (-32768, 32767),
            g.ABS_Z: (0, 1023), g.ABS_RZ: (0, 1023),
            g.ABS_HAT0X: (-1, 1), g.ABS_HAT0Y: (-1, 1),
        },
        key_codes={g.BTN_SOUTH, g.BTN_EAST, g.BTN_NORTH, g.BTN_WEST, g.BTN_TL, g.BTN_TR,
                   g.BTN_SELECT, g.BTN_START, g.BTN_MODE, g.BTN_THUMBL, g.BTN_THUMBR},
    )


def ds4_caps() -> g.DeviceCaps:
    return g.DeviceCaps(
        path="/dev/input/event1", name="Sony DualShock 4", vendor=0x054C, product=0x09CC,
        abs_ranges={
            g.ABS_X: (0, 255), g.ABS_Y: (0, 255), g.ABS_RX: (0, 255), g.ABS_RY: (0, 255),
        },
        key_codes={g.BTN_SOUTH, g.BTN_EAST, g.BTN_TL2, g.BTN_TR2, g.BTN_TOUCH,
                   g.BTN_DPAD_UP, g.BTN_DPAD_DOWN, g.BTN_DPAD_LEFT, g.BTN_DPAD_RIGHT,
                   g.BTN_START, g.BTN_SELECT},
    )


def f310x_caps() -> g.DeviceCaps:
    return g.DeviceCaps(
        path="/dev/input/event2", name="Logitech Gamepad F310", vendor=0x046D, product=0xC21D,
        abs_ranges={g.ABS_X: (-32768, 32767), g.ABS_Y: (-32768, 32767)},
        key_codes={g.BTN_SOUTH, g.BTN_EAST, g.BTN_NORTH, g.BTN_WEST},
    )


# --------------------------------------------------------------------------
# ioctl request numbers
# --------------------------------------------------------------------------

def test_ioctl_numbers_match_kernel_headers():
    # Cross-checked against /usr/include/linux/input.h on a real Arch
    # install (linux-api-headers) - see the module docstring for the formula.
    assert g.EVIOCGID == 0x80084502
    assert g.EVIOCGABS(0) == 0x80184540
    assert g.EVIOCGNAME(256) == 0x81004506


def test_eviocgbit_and_eviocgkey_use_read_direction_and_correct_nr():
    # _IOC(_IOC_READ, 'E', 0x20 + ev, len) and _IOC(_IOC_READ, 'E', 0x18, len)
    assert g.EVIOCGBIT(g.EV_KEY, 96) == (2 << 30) | (96 << 16) | (ord("E") << 8) | (0x20 + g.EV_KEY)
    assert g.EVIOCGKEY(96) == (2 << 30) | (96 << 16) | (ord("E") << 8) | 0x18


# --------------------------------------------------------------------------
# EventParser
# --------------------------------------------------------------------------

def test_event_parser_decodes_a_full_stream():
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    assert (g.EV_ABS, g.ABS_Y, -32768) in events
    assert (g.EV_SYN, g.SYN_REPORT, 0) in events


def test_event_parser_handles_a_stream_split_mid_struct():
    data = read_fixture("xbox_events.bin")
    cut = 24 * 2 + 10  # inside the third event's 24-byte struct
    parser = g.EventParser()
    first = parser.feed(data[:cut])
    second = parser.feed(data[cut:])
    assert first == g.EventParser().feed(data[:24 * 2])  # only whole structs parsed so far
    assert first + second == g.EventParser().feed(data)


# --------------------------------------------------------------------------
# Mapper: axis sign/scale faithfulness
# --------------------------------------------------------------------------

def test_stick_up_is_negative_y_and_right_is_positive_x():
    caps = xbox_caps()
    mapper = g.Mapper(caps)
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    snapshots = mapper.feed(events)
    assert snapshots[0]["left_stick_y"] == -1.0
    assert snapshots[0]["left_stick_x"] == 1.0


def test_full_trigger_press_is_1_0():
    mapper = g.Mapper(xbox_caps())
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    snapshots = mapper.feed(events)
    trigger_snapshot = next(s for s in snapshots if s["right_trigger"] == 1.0)
    assert trigger_snapshot["right_trigger"] == 1.0


def test_btn_south_is_a_and_btn_east_is_b():
    mapper = g.Mapper(xbox_caps())
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    snapshots = mapper.feed(events)
    assert any(s["a"] for s in snapshots)
    assert any(s["b"] for s in snapshots)


def test_hat_up_is_dpad_up():
    mapper = g.Mapper(xbox_caps())
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    snapshots = mapper.feed(events)
    assert any(s["dpad_up"] for s in snapshots)


def test_syn_report_batches_multiple_axis_changes_into_one_snapshot():
    mapper = g.Mapper(xbox_caps())
    events = g.EventParser().feed(read_fixture("xbox_events.bin"))
    snapshots = mapper.feed(events)
    first = snapshots[0]
    assert first["left_stick_y"] == -1.0 and first["left_stick_x"] == 1.0


def test_no_deadzone_small_stick_values_pass_through():
    # SDK 11.2.0 Gamepad.java has no joystick-deadzone logic (verified by
    # reading the source: no setJoystickDeadzone/DEFAULT_DEADZONE exists in
    # this version), so a tiny off-centre value must NOT be squashed to 0.
    caps = xbox_caps()
    mapper = g.Mapper(caps)
    lo, hi = caps.abs_ranges[g.ABS_X]
    centre = (lo + hi) / 2
    tiny_offset = int((hi - lo) * 0.02)  # ~2% off-centre, well inside a typical deadzone
    events = [(g.EV_ABS, g.ABS_X, int(centre) + tiny_offset), (g.EV_SYN, g.SYN_REPORT, 0)]
    snapshots = mapper.feed(events)
    assert snapshots[0]["left_stick_x"] != 0.0


# --------------------------------------------------------------------------
# Mapper: DualShock4-style device (0..255 axes, digital triggers, digital dpad)
# --------------------------------------------------------------------------

def test_ds4_axis_normalisation_and_digital_trigger_and_dpad():
    mapper = g.Mapper(ds4_caps())
    events = g.EventParser().feed(read_fixture("ds4_events.bin"))
    snapshots = mapper.feed(events)
    # after full stream: full up -> -1.0, full right -> 1.0
    up_snapshot = next(s for s in snapshots if s["left_stick_y"] == -1.0)
    assert up_snapshot is not None
    right_snapshot = next(s for s in snapshots if s["left_stick_x"] == 1.0)
    assert right_snapshot is not None
    # digital trigger fallback: BTN_TL2 press -> left_trigger 1.0 (no analog axis present)
    assert any(s.get("left_trigger") == 1.0 for s in snapshots)
    assert any(s.get("dpad_left") for s in snapshots)
    assert any(s.get("touchpad") for s in snapshots)


# --------------------------------------------------------------------------
# gamepadType classification, incl. F310 D-mode refusal
# --------------------------------------------------------------------------

def test_classify_xbox_and_sony_and_unknown():
    assert g.classify_gamepad(0x045E, 0x028E) == ("XBOX_360", None, True)
    assert g.classify_gamepad(0x054C, 0x09CC) == ("SONY_PS4", None, True)
    assert g.classify_gamepad(0x1234, 0x5678) == ("UNKNOWN", None, True)


def test_classify_f310_x_mode_is_usable():
    gamepad_type, warning, usable = g.classify_gamepad(0x046D, 0xC21D)
    assert gamepad_type == "LOGITECH_F310"
    assert warning is None
    assert usable is True


def test_classify_f310_d_mode_warns_and_is_unusable():
    gamepad_type, warning, usable = g.classify_gamepad(0x046D, 0xC216)
    assert gamepad_type == "LOGITECH_F310"
    assert usable is False
    assert warning == (
        "Logitech F310 is in D mode. Flip the X/D switch on the back of the "
        "controller to X (the Driver Station also expects X mode)."
    )


def test_f310_x_mode_stream_maps_west_to_x_and_north_to_y():
    mapper = g.Mapper(f310x_caps())
    events = g.EventParser().feed(read_fixture("f310x_events.bin"))
    snapshots = mapper.feed(events)
    assert snapshots[0]["left_stick_x"] == -1.0
    assert any(s.get("x") for s in snapshots)
    assert any(s.get("y") for s in snapshots)


# --------------------------------------------------------------------------
# Assigner: Start+A/B claim combo, masking, reassignment, removal
# --------------------------------------------------------------------------

def test_start_a_assigns_index_1_and_masks_start_and_a():
    assigner = g.Assigner()
    state = dict(g._initial_state())
    state["start"] = True
    masked, changed = assigner.process("dev1", state)
    assert changed is False  # 'a' hasn't gone True yet
    assert masked["start"] is False  # start alone is already masked while held

    state["a"] = True
    masked, changed = assigner.process("dev1", state)
    assert changed is True
    assert assigner.index_for("dev1") == 1
    assert masked["start"] is False
    assert masked["a"] is False


def test_start_b_assigns_index_2():
    assigner = g.Assigner()
    state = dict(g._initial_state())
    state["start"] = True
    assigner.process("dev1", state)
    state["b"] = True
    masked, changed = assigner.process("dev1", state)
    assert changed is True
    assert assigner.index_for("dev1") == 2
    assert masked["b"] is False


def test_reassignment_moves_the_index():
    assigner = g.Assigner()
    s1 = dict(g._initial_state(), start=True, a=True)
    assigner.process("dev1", s1)
    assert assigner.index_for("dev1") == 1

    s2 = dict(g._initial_state(), start=True, a=True)
    assigner.process("dev2", s2)
    assert assigner.index_for("dev2") == 1
    assert assigner.index_for("dev1") is None


def test_removal_releases_the_index():
    assigner = g.Assigner()
    assigner.process("dev1", dict(g._initial_state(), start=True, a=True))
    assert assigner.index_for("dev1") == 1
    released = assigner.remove_device("dev1")
    assert released is True
    assert assigner.index_for("dev1") is None


def test_auto_assign_fills_first_two_free_slots():
    assigner = g.Assigner()
    assert assigner.auto_assign("dev1") is True
    assert assigner.index_for("dev1") == 1
    assert assigner.auto_assign("dev2") is True
    assert assigner.index_for("dev2") == 2
    assert assigner.auto_assign("dev3") is False  # no free slot
    assert assigner.index_for("dev3") is None


def test_ordinary_button_presses_are_not_masked_when_start_is_not_held():
    assigner = g.Assigner()
    state = dict(g._initial_state(), a=True)
    masked, changed = assigner.process("dev1", state)
    assert changed is False
    assert masked["a"] is True  # only masked while start is held


# --------------------------------------------------------------------------
# EACCES handling: documented error text, no privilege escalation attempted
# --------------------------------------------------------------------------

def test_eacces_on_open_produces_the_documented_error_and_never_retries_privileged():
    calls = []

    def fake_opener(path, flags):
        calls.append((path, flags))
        raise PermissionError(13, "Permission denied")

    result = g.probe_device("/dev/input/event99", opener=fake_opener)
    assert isinstance(result, g.ProbeError)
    assert result.message == g.permission_error_message("/dev/input/event99")
    assert "getfacl" in result.message
    assert "input" in result.message
    assert calls == [("/dev/input/event99", __import__("os").O_RDONLY | __import__("os").O_NONBLOCK)]
    # only one open attempt: no retry loop, and nothing here can plausibly sudo
    assert len(calls) == 1


def test_permission_error_message_names_the_exact_node():
    msg = g.permission_error_message("/dev/input/event7")
    assert "/dev/input/event7" in msg
    assert "sudo" not in msg.lower()


# --------------------------------------------------------------------------
# SYN_DROPPED resync
# --------------------------------------------------------------------------

def test_syn_dropped_suppresses_emission_until_resync():
    mapper = g.Mapper(xbox_caps())
    events = [(g.EV_ABS, g.ABS_X, 32767), (g.EV_SYN, g.SYN_DROPPED, 0), (g.EV_SYN, g.SYN_REPORT, 0)]
    snapshots = mapper.feed(events)
    assert snapshots == []
    assert mapper.needs_resync is True

    snapshot = mapper.resync({g.ABS_X: 32767}, {g.BTN_SOUTH})
    assert snapshot["left_stick_x"] == 1.0
    assert snapshot["a"] is True
    assert mapper.needs_resync is False
