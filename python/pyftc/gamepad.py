"""Stream physical game-controller state as newline-delimited JSON so the
simulator can feed FTC OpMode code exactly what the Driver Station would.

stdout is JSON only (one object per line); diagnostics go to stderr; exit 0
on normal shutdown, 2 on a usage/internal error. See docs in the task that
generated this file (or ARCHITECTURE.md) for the message schema.

Faithfulness matters more than convenience here: this module exists to catch
sign/mapping bugs in OpMode code, so every normalisation and button mapping
below is pinned to a primary source (kernel uapi headers, kernel driver
tables, or the FTC SDK Gamepad.java source) rather than guessed.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import selectors
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# ioctl request numbers
#
# Linux computes ioctl request numbers with the generic scheme in
# asm-generic/ioctl.h: dir(2 bits) | size(14 bits) | type(8 bits) | nr(8 bits),
# packed as (dir << 30) | (size << 16) | (type << 8) | nr. type is the ASCII
# code for 'E' (0x45) for all evdev ioctls. Verified against the actual
# installed uapi headers on this machine (Arch's `linux-api-headers` package):
# /usr/include/linux/input.h (the EVIOCG* macros) and
# /usr/include/asm-generic/ioctl.h (the _IOC/_IOR macros themselves).
# --------------------------------------------------------------------------

_IOC_READ = 2
_IOC_NRBITS, _IOC_TYPEBITS, _IOC_SIZEBITS = 8, 8, 14
_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS


def _IOC(direction: int, type_: str, nr: int, size: int) -> int:
    return (direction << _IOC_DIRSHIFT) | (size << _IOC_SIZESHIFT) | (ord(type_) << _IOC_TYPESHIFT) | nr


def _IOR(type_: str, nr: int, size: int) -> int:
    return _IOC(_IOC_READ, type_, nr, size)


INPUT_ID_SIZE = 8  # struct input_id: 4 x __u16 (bustype, vendor, product, version)
INPUT_ABSINFO_SIZE = 24  # struct input_absinfo: 6 x __s32 (value, minimum, maximum, fuzz, flat, resolution)

EVIOCGVERSION = _IOR("E", 0x01, 4)
EVIOCGID = _IOR("E", 0x02, INPUT_ID_SIZE)  # == 0x80084502


def EVIOCGNAME(length: int) -> int:
    return _IOC(_IOC_READ, "E", 0x06, length)  # EVIOCGNAME(256) == 0x81004506


def EVIOCGPHYS(length: int) -> int:
    return _IOC(_IOC_READ, "E", 0x07, length)


def EVIOCGUNIQ(length: int) -> int:
    return _IOC(_IOC_READ, "E", 0x08, length)


def EVIOCGKEY(length: int) -> int:
    return _IOC(_IOC_READ, "E", 0x18, length)


def EVIOCGBIT(ev: int, length: int) -> int:
    return _IOC(_IOC_READ, "E", 0x20 + ev, length)


def EVIOCGABS(abs_code: int) -> int:
    return _IOR("E", 0x40 + abs_code, INPUT_ABSINFO_SIZE)  # EVIOCGABS(0) == 0x80184540


# --------------------------------------------------------------------------
# Event/button/axis codes, from /usr/include/linux/input-event-codes.h
# (installed on this machine as part of linux-api-headers; upstream this is
# include/uapi/linux/input-event-codes.h in torvalds/linux).
# --------------------------------------------------------------------------

EV_SYN, EV_KEY, EV_ABS = 0x00, 0x01, 0x03
SYN_REPORT, SYN_DROPPED = 0, 3

ABS_X, ABS_Y, ABS_Z = 0x00, 0x01, 0x02
ABS_RX, ABS_RY, ABS_RZ = 0x03, 0x04, 0x05
ABS_HAT0X, ABS_HAT0Y = 0x10, 0x11

# NOTE on BTN_SOUTH/EAST/WEST/NORTH vs the BTN_A/BTN_B/BTN_X/BTN_Y aliases:
# input-event-codes.h itself defines BTN_X as an alias for BTN_NORTH and
# BTN_Y as an alias for BTN_WEST. That is NOT the mapping Documentation/
# input/gamepad.rst recommends userspace use: gamepad.rst defines the four
# face buttons by clock position (NORTH=top, EAST=right, SOUTH=bottom,
# WEST=left) and says the bottom button is the primary action button
# (Xbox A / PlayStation Cross). Going clockwise from the top on a real Xbox
# pad: Y(top/NORTH), B(right/EAST), A(bottom/SOUTH), X(left/WEST) - which is
# exactly SOUTH=a, EAST=b, WEST=x, NORTH=y. So we map by the raw SOUTH/EAST/
# WEST/NORTH hex codes below and deliberately do not use the BTN_X/BTN_Y
# macro names, which would silently swap x and y.
BTN_SOUTH, BTN_EAST, BTN_NORTH, BTN_WEST = 0x130, 0x131, 0x133, 0x134
BTN_TL, BTN_TR = 0x136, 0x137
BTN_TL2, BTN_TR2 = 0x138, 0x139
BTN_SELECT, BTN_START, BTN_MODE = 0x13A, 0x13B, 0x13C
BTN_THUMBL, BTN_THUMBR = 0x13D, 0x13E
BTN_GAMEPAD = BTN_SOUTH
BTN_TOUCH = 0x14A
BTN_LEFT = 0x110
BTN_DPAD_UP, BTN_DPAD_DOWN, BTN_DPAD_LEFT, BTN_DPAD_RIGHT = 0x220, 0x221, 0x222, 0x223

BUTTON_CODE_TO_FIELD = {
    BTN_SOUTH: "a",
    BTN_EAST: "b",
    BTN_WEST: "x",
    BTN_NORTH: "y",
    BTN_TL: "left_bumper",
    BTN_TR: "right_bumper",
    BTN_SELECT: "back",
    BTN_START: "start",
    BTN_MODE: "guide",
    BTN_THUMBL: "left_stick_button",
    BTN_THUMBR: "right_stick_button",
}
DPAD_BUTTON_TO_FIELD = {
    BTN_DPAD_UP: "dpad_up",
    BTN_DPAD_DOWN: "dpad_down",
    BTN_DPAD_LEFT: "dpad_left",
    BTN_DPAD_RIGHT: "dpad_right",
}

# --------------------------------------------------------------------------
# Vendor/product ids, cited against real kernel sources (not guessed):
#   - Microsoft/Sony USB vendor ids are the standard USB-IF assigned ids.
#   - Logitech F310 in X (XInput) mode: drivers/input/joystick/xpad.c,
#     table entry `{ 0x046d, 0xc21d, "Logitech Gamepad F310", 0, XTYPE_XBOX360 }`.
#   - Logitech F310 in D (DirectInput) mode: drivers/hid/hid-ids.h,
#     `#define USB_DEVICE_ID_LOGITECH_DUAL_ACTION 0xc216` (the printed name on
#     the device is "Logitech Dual Action"; the F310 ships with a physical
#     X/D switch and this is its D-mode id). D-mode does not follow the
#     kernel gamepad spec (it looks like a joystick with a nonstandard axis
#     count), so we refuse to guess a mapping for it.
# --------------------------------------------------------------------------

VENDOR_LOGITECH = 0x046D
VENDOR_MICROSOFT = 0x045E
VENDOR_SONY = 0x054C
PRODUCT_F310_X_MODE = 0xC21D
PRODUCT_F310_D_MODE = 0xC216

F310_D_MODE_WARNING = (
    "Logitech F310 is in D mode. Flip the X/D switch on the back of the "
    "controller to X (the Driver Station also expects X mode)."
)


def classify_gamepad(vendor: int, product: int) -> tuple[str, str | None, bool]:
    """Returns (gamepadType, warning, usable). usable=False means: list the
    device in the `devices` message but never open it for state."""
    if vendor == VENDOR_LOGITECH and product == PRODUCT_F310_D_MODE:
        return "LOGITECH_F310", F310_D_MODE_WARNING, False
    if vendor == VENDOR_LOGITECH and product == PRODUCT_F310_X_MODE:
        return "LOGITECH_F310", None, True
    if vendor == VENDOR_MICROSOFT:
        return "XBOX_360", None, True
    if vendor == VENDOR_SONY:
        return "SONY_PS4", None, True
    return "UNKNOWN", None, True


def permission_error_message(path: str) -> str:
    return (
        f"No permission to read {path}. Joystick access is normally granted to the "
        f"logged-in user by systemd-logind's uaccess rule; check `getfacl {path}`, "
        f"or add a udev rule / add yourself to the 'input' group, then replug."
    )


# --------------------------------------------------------------------------
# Raw input_event parsing.
#
# struct input_event on a 64-bit non-__KERNEL__ build (glibc's <linux/input.h>,
# the only case this module runs under) is struct timeval {long tv_sec, long
# tv_usec} followed by __u16 type, __u16 code, __s32 value: 8+8+2+2+4 = 24
# bytes with native alignment (verified: struct.calcsize("llHHi") == 24 on
# this machine). We only need type/code/value, so the two leading longs are
# unpacked and discarded.
# --------------------------------------------------------------------------

_EVENT_STRUCT = struct.Struct("llHHi")
assert _EVENT_STRUCT.size == 24, "unexpected struct input_event size on this platform"


class EventParser:
    """Turns a raw byte stream (arbitrarily split across reads) into a list
    of (type, code, value) events. Pure: no file I/O."""

    def __init__(self) -> None:
        self._buf = bytearray()

    def feed(self, data: bytes) -> list[tuple[int, int, int]]:
        self._buf += data
        size = _EVENT_STRUCT.size
        count = len(self._buf) // size
        events = []
        for i in range(count):
            _sec, _usec, type_, code, value = _EVENT_STRUCT.unpack(self._buf[i * size : (i + 1) * size])
            events.append((type_, code, value))
        del self._buf[: count * size]
        return events


# --------------------------------------------------------------------------
# Device capabilities + the pure event -> SDK-state mapper.
# --------------------------------------------------------------------------


@dataclass
class DeviceCaps:
    path: str
    name: str
    vendor: int
    product: int
    abs_ranges: dict[int, tuple[int, int]] = field(default_factory=dict)  # code -> (min, max)
    key_codes: set[int] = field(default_factory=set)
    phys: str = ""
    uniq: str = ""

    @property
    def stable_id(self) -> str:
        if self.uniq:
            return f"uniq/{self.uniq}"
        if self.phys:
            return f"phys/{self.phys}"
        return self.path

    @property
    def vendor_hex(self) -> str:
        return f"{self.vendor:04x}"

    @property
    def product_hex(self) -> str:
        return f"{self.product:04x}"


def _initial_state() -> dict[str, float | bool]:
    return {
        "left_stick_x": 0.0, "left_stick_y": 0.0, "right_stick_x": 0.0, "right_stick_y": 0.0,
        "left_trigger": 0.0, "right_trigger": 0.0,
        "dpad_up": False, "dpad_down": False, "dpad_left": False, "dpad_right": False,
        "a": False, "b": False, "x": False, "y": False,
        "guide": False, "start": False, "back": False,
        "left_bumper": False, "right_bumper": False,
        "left_stick_button": False, "right_stick_button": False,
        "touchpad": False,
    }


STICK_AXIS_TO_FIELD = {ABS_X: "left_stick_x", ABS_Y: "left_stick_y", ABS_RX: "right_stick_x", ABS_RY: "right_stick_y"}


class Mapper:
    """Pure event -> FTC SDK Gamepad state mapper for one device. Takes the
    device's capabilities (so it knows which axes/buttons it actually has)
    and a stream of (type, code, value) events; produces state snapshots at
    each SYN_REPORT that actually changed something.

    Deliberately applies NO deadzone: the FTC SDK 11.2.0 Gamepad class (see
    RobotCore/.../Gamepad.java) has no joystick-deadzone logic at all (older
    SDKs had setJoystickDeadzone/DEFAULT_DEADZONE; that code is gone in
    11.2.0), so passing raw normalised values through is the faithful
    behaviour, not an oversight.
    """

    def __init__(self, caps: DeviceCaps) -> None:
        self.caps = caps
        self.state: dict[str, float | bool] = _initial_state()
        self.needs_resync = False
        self._pending_changed = False
        self._use_hat = ABS_HAT0X in caps.abs_ranges and ABS_HAT0Y in caps.abs_ranges
        self._left_trigger_axis: int | None = ABS_Z if ABS_Z in caps.abs_ranges else None
        self._right_trigger_axis: int | None = ABS_RZ if ABS_RZ in caps.abs_ranges else None

    def feed(self, events: list[tuple[int, int, int]]) -> list[dict[str, float | bool]]:
        snapshots: list[dict[str, float | bool]] = []
        for type_, code, value in events:
            if type_ == EV_KEY:
                self._apply_key(code, value)
            elif type_ == EV_ABS:
                self._apply_abs(code, value)
            elif type_ == EV_SYN:
                if code == SYN_DROPPED:
                    self.needs_resync = True
                    self._pending_changed = False
                elif code == SYN_REPORT and self._pending_changed and not self.needs_resync:
                    snapshots.append(dict(self.state))
                    self._pending_changed = False
        return snapshots

    def resync(self, abs_values: dict[int, int], pressed_keys: set[int]) -> dict[str, float | bool]:
        """Rebuild state from scratch after SYN_DROPPED, via fresh
        EVIOCGABS/EVIOCGKEY reads (the caller does the ioctls; this just
        applies the results)."""
        self.state = _initial_state()
        self.needs_resync = False
        self._pending_changed = False
        for code, value in abs_values.items():
            self._apply_abs(code, value)
        for code in pressed_keys:
            self._apply_key(code, 1)
        self._pending_changed = False
        return dict(self.state)

    def _set(self, field_name: str, value: float | bool) -> None:
        if self.state.get(field_name) != value:
            self.state[field_name] = value
            self._pending_changed = True

    def _apply_key(self, code: int, value: int) -> None:
        pressed = value != 0
        if code in BUTTON_CODE_TO_FIELD:
            self._set(BUTTON_CODE_TO_FIELD[code], pressed)
        elif not self._use_hat and code in DPAD_BUTTON_TO_FIELD:
            self._set(DPAD_BUTTON_TO_FIELD[code], pressed)
        elif code in (BTN_TOUCH, BTN_LEFT):
            # "on the same device" is automatic here: we only ever see this
            # device's own events, never another device's mouse click.
            self._set("touchpad", pressed)
        elif code == BTN_TL2 and self._left_trigger_axis is None:
            self._set("left_trigger", 1.0 if pressed else 0.0)
        elif code == BTN_TR2 and self._right_trigger_axis is None:
            self._set("right_trigger", 1.0 if pressed else 0.0)

    def _apply_abs(self, code: int, value: int) -> None:
        if code in STICK_AXIS_TO_FIELD:
            self._set(STICK_AXIS_TO_FIELD[code], self._normalise_stick(code, value))
        elif code == self._left_trigger_axis:
            self._set("left_trigger", self._normalise_trigger(code, value))
        elif code == self._right_trigger_axis:
            self._set("right_trigger", self._normalise_trigger(code, value))
        elif self._use_hat and code == ABS_HAT0X:
            self._set("dpad_left", value < 0)
            self._set("dpad_right", value > 0)
        elif self._use_hat and code == ABS_HAT0Y:
            self._set("dpad_up", value < 0)
            self._set("dpad_down", value > 0)

    def _normalise_stick(self, code: int, value: int) -> float:
        lo, hi = self.caps.abs_ranges[code]
        half = (hi - lo) / 2
        if half == 0:
            return 0.0
        centre = (hi + lo) / 2
        return max(-1.0, min(1.0, (value - centre) / half))

    def _normalise_trigger(self, code: int, value: int) -> float:
        lo, hi = self.caps.abs_ranges[code]
        span = hi - lo
        if span == 0:
            return 0.0
        return max(0.0, min(1.0, (value - lo) / span))


# --------------------------------------------------------------------------
# Driver-Station-style assignment: hold Start and tap A -> claim gamepad1,
# Start+B -> claim gamepad2. Claiming a held index moves it. While Start is
# held, Start/A/B are masked out of the forwarded state (they're reserved
# for the combo, not OpMode input).
# --------------------------------------------------------------------------


class Assigner:
    def __init__(self) -> None:
        self._by_index: dict[int, str] = {}
        self._prev: dict[str, dict[str, bool]] = {}

    def index_for(self, device_id: str) -> int | None:
        for index, held_by in self._by_index.items():
            if held_by == device_id:
                return index
        return None

    def remove_device(self, device_id: str) -> bool:
        """Returns True if this device held an index (caller should emit a
        zeroed state for that index and a devices update)."""
        released = False
        for index in [i for i, d in self._by_index.items() if d == device_id]:
            del self._by_index[index]
            released = True
        self._prev.pop(device_id, None)
        return released

    def auto_assign(self, device_id: str) -> bool:
        """For --auto: claim the first free slot for a not-yet-assigned
        device. Returns True if it changed an assignment."""
        if self.index_for(device_id) is not None:
            return False
        for index in (1, 2):
            if index not in self._by_index:
                self._by_index[index] = device_id
                return True
        return False

    def process(self, device_id: str, state: dict[str, float | bool]) -> tuple[dict[str, float | bool], bool]:
        """Applies claim-combo detection for one device's new state snapshot.
        Returns (masked_state_to_forward, assignment_changed)."""
        prev = self._prev.get(device_id, {"start": False, "a": False, "b": False})
        start, a, b = bool(state.get("start")), bool(state.get("a")), bool(state.get("b"))
        changed = False
        if start and a and not (prev["start"] and prev["a"]):
            changed = self._claim(1, device_id) or changed
        if start and b and not (prev["start"] and prev["b"]):
            changed = self._claim(2, device_id) or changed
        self._prev[device_id] = {"start": start, "a": a, "b": b}
        masked = dict(state)
        if start:
            masked["start"] = False
            masked["a"] = False
            masked["b"] = False
        return masked, changed

    def _claim(self, index: int, device_id: str) -> bool:
        if self._by_index.get(index) == device_id:
            return False
        for other in [i for i, d in self._by_index.items() if d == device_id]:
            del self._by_index[other]
        self._by_index[index] = device_id
        return True


# --------------------------------------------------------------------------
# Thin I/O layer: udev/capability-based discovery, ioctl probing.
# --------------------------------------------------------------------------


class ProbeError:
    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message


def _udev_says_joystick(path: str) -> bool | None:
    """True/False if the udev db has an opinion, None if it's unreadable (so
    the caller should fall back to capability-bit sniffing)."""
    try:
        rdev = os.stat(path).st_rdev
    except OSError:
        return False
    major, minor = os.major(rdev), os.minor(rdev)
    try:
        data = Path(f"/run/udev/data/c{major}:{minor}").read_text()
    except OSError:
        return None
    return "E:ID_INPUT_JOYSTICK=1" in data


def _get_bit(bitmap: bytes, bit: int) -> bool:
    byte = bit // 8
    if byte >= len(bitmap):
        return False
    return bool(bitmap[byte] & (1 << (bit % 8)))


def list_event_nodes() -> list[str]:
    try:
        return sorted(str(p) for p in Path("/dev/input").glob("event*"))
    except OSError:
        return []


def probe_device(path: str, *, opener=os.open, ioctl=fcntl.ioctl) -> DeviceCaps | ProbeError:
    """Opens the node read-only/non-blocking and reads its capabilities via
    ioctl. `opener`/`ioctl` are injectable so tests can simulate EACCES
    without touching a real device node."""
    try:
        fd = opener(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as e:
        if isinstance(e, PermissionError) or e.errno in (13, 1):  # EACCES, EPERM
            return ProbeError(path, permission_error_message(path))
        return ProbeError(path, f"Could not open {path}: {e}")
    try:
        return _probe_open_fd(path, fd, ioctl)
    finally:
        os.close(fd)


def _probe_open_fd(path: str, fd: int, ioctl) -> DeviceCaps:
    id_buf = ioctl(fd, EVIOCGID, bytes(INPUT_ID_SIZE))
    _bustype, vendor, product, _version = struct.unpack("HHHH", id_buf)

    name_buf = ioctl(fd, EVIOCGNAME(256), bytes(256))
    name = name_buf.split(b"\x00", 1)[0].decode(errors="replace")

    phys = _ioctl_string(fd, ioctl, EVIOCGPHYS(256))
    uniq = _ioctl_string(fd, ioctl, EVIOCGUNIQ(256))

    key_bits = ioctl(fd, EVIOCGBIT(EV_KEY, 96), bytes(96))
    key_codes = {code for code in range(96 * 8) if _get_bit(key_bits, code)}

    abs_bits = ioctl(fd, EVIOCGBIT(EV_ABS, 8), bytes(8))
    abs_ranges: dict[int, tuple[int, int]] = {}
    for code in range(64):
        if not _get_bit(abs_bits, code):
            continue
        info = ioctl(fd, EVIOCGABS(code), bytes(INPUT_ABSINFO_SIZE))
        _value, minimum, maximum, _fuzz, _flat, _resolution = struct.unpack("iiiiii", info)
        abs_ranges[code] = (minimum, maximum)

    return DeviceCaps(path=path, name=name, vendor=vendor, product=product,
                       abs_ranges=abs_ranges, key_codes=key_codes, phys=phys, uniq=uniq)


def _ioctl_string(fd: int, ioctl, request: int) -> str:
    try:
        buf = ioctl(fd, request, bytes(256))
    except OSError:
        return ""
    return buf.split(b"\x00", 1)[0].decode(errors="replace")


def read_initial_key_state(fd: int, key_codes: set[int], *, ioctl=fcntl.ioctl) -> set[int]:
    buf = ioctl(fd, EVIOCGKEY(96), bytes(96))
    return {code for code in key_codes if _get_bit(buf, code)}


def read_current_abs_values(fd: int, abs_codes: set[int], *, ioctl=fcntl.ioctl) -> dict[int, int]:
    values: dict[int, int] = {}
    for code in abs_codes:
        info = ioctl(fd, EVIOCGABS(code), bytes(INPUT_ABSINFO_SIZE))
        value, _minimum, _maximum, _fuzz, _flat, _resolution = struct.unpack("iiiiii", info)
        values[code] = value
    return values


def is_gamepad_candidate(caps: DeviceCaps) -> bool:
    """Capability-bit fallback used when the udev db couldn't tell us: has a
    gamepad-shaped button (BTN_GAMEPAD/BTN_SOUTH) and at least one stick axis."""
    return BTN_GAMEPAD in caps.key_codes and ABS_X in caps.abs_ranges


# --------------------------------------------------------------------------
# Runtime: ties the pure pieces to real fds via selectors, handles hotplug,
# coalescing and keepalives, and emits the newline-delimited JSON protocol.
# --------------------------------------------------------------------------

COALESCE_SECONDS = 0.010
KEEPALIVE_SECONDS = 0.500
RESCAN_SECONDS = 1.0


@dataclass
class _OpenDevice:
    caps: DeviceCaps
    fd: int
    parser: EventParser
    mapper: Mapper
    gamepad_type: str
    warning: str | None
    usable: bool
    dirty_since: float | None = None
    last_emit: float = 0.0


class Runner:
    def __init__(self, out=sys.stdout, err=sys.stderr, auto: bool = False) -> None:
        self.out = out
        self.err = err
        self.auto = auto
        self.assigner = Assigner()
        self.devices: dict[str, _OpenDevice] = {}
        self.sel = selectors.DefaultSelector()
        self._last_devices_signature: tuple | None = None
        self._stop = False

    def emit(self, message: dict) -> None:
        self.out.write(json.dumps(message) + "\n")
        self.out.flush()

    def diag(self, message: str) -> None:
        print(message, file=self.err)

    def rescan(self) -> list[str]:
        errors: list[str] = []
        seen_paths = set()
        for path in list_event_nodes():
            seen_paths.add(path)
            if any(dev.caps.path == path for dev in self.devices.values()):
                continue
            udev = _udev_says_joystick(path)
            if udev is False:
                continue
            result = probe_device(path)
            if isinstance(result, ProbeError):
                errors.append(result.message)
                self.diag(f"pyftc.gamepad: {result.message}")
                continue
            caps = result
            if udev is None and not is_gamepad_candidate(caps):
                continue
            gamepad_type, warning, usable = classify_gamepad(caps.vendor, caps.product)
            fd = -1
            mapper = Mapper(caps)
            if usable:
                try:
                    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                except PermissionError:
                    errors.append(permission_error_message(path))
                    self.diag(f"pyftc.gamepad: {permission_error_message(path)}")
                    continue
                self.sel.register(fd, selectors.EVENT_READ, caps.stable_id)
            dev = _OpenDevice(caps=caps, fd=fd, parser=EventParser(), mapper=mapper,
                               gamepad_type=gamepad_type, warning=warning, usable=usable)
            self.devices[caps.stable_id] = dev
            if usable and self.auto:
                self.assigner.auto_assign(caps.stable_id)

        removed = [dev_id for dev_id, dev in self.devices.items() if dev.caps.path not in seen_paths]
        for dev_id in removed:
            self._remove_device(dev_id)
        return errors

    def _remove_device(self, device_id: str) -> None:
        dev = self.devices.pop(device_id, None)
        if dev is None:
            return
        if dev.fd >= 0:
            try:
                self.sel.unregister(dev.fd)
            except KeyError:
                pass
            try:
                os.close(dev.fd)
            except OSError:
                pass
        released_index = self.assigner.index_for(device_id)
        self.assigner.remove_device(device_id)
        if released_index is not None:
            self.emit({"type": "state", "index": released_index, "id": device_id,
                       "gamepadType": dev.gamepad_type, "state": _initial_state()})

    def devices_message(self, errors: list[str]) -> dict:
        devices_list = []
        for dev_id, dev in self.devices.items():
            devices_list.append({
                "id": dev_id, "path": dev.caps.path, "name": dev.caps.name,
                "vendor": dev.caps.vendor_hex, "product": dev.caps.product_hex,
                "gamepadType": dev.gamepad_type,
                "assigned": self.assigner.index_for(dev_id) if dev.usable else None,
                "warning": dev.warning,
            })
        return {"type": "devices", "devices": devices_list, "errors": errors}

    def _maybe_emit_devices(self, errors: list[str]) -> None:
        signature = tuple(
            (dev_id, self.assigner.index_for(dev_id))
            for dev_id in self.devices
        )
        if signature != self._last_devices_signature or errors:
            self.emit(self.devices_message(errors))
            self._last_devices_signature = signature

    def run(self) -> int:
        errors = self.rescan()
        self._maybe_emit_devices(errors)
        last_rescan = time.monotonic()
        try:
            while not self._stop:
                now = time.monotonic()
                timeout = min(RESCAN_SECONDS - (now - last_rescan), COALESCE_SECONDS, KEEPALIVE_SECONDS)
                events = self.sel.select(timeout=max(0.0, timeout))
                for key, _mask in events:
                    self._handle_readable(key.fd, key.data)
                now = time.monotonic()
                self._flush_dirty(now)
                self._send_keepalives(now)
                if now - last_rescan >= RESCAN_SECONDS:
                    errors = self.rescan()
                    self._maybe_emit_devices(errors)
                    last_rescan = now
        except KeyboardInterrupt:
            pass
        return 0

    def _handle_readable(self, fd: int, device_id: str) -> None:
        dev = self.devices.get(device_id)
        if dev is None or dev.fd != fd:
            return
        try:
            data = os.read(fd, 24 * 64)
        except BlockingIOError:
            return
        except OSError:
            self._remove_device(device_id)
            return
        if not data:
            self._remove_device(device_id)
            return
        events = dev.parser.feed(data)
        snapshots = dev.mapper.feed(events)
        if dev.mapper.needs_resync:
            self._resync(device_id, dev)
        for _snapshot in snapshots:
            dev.dirty_since = dev.dirty_since or time.monotonic()

    def _resync(self, device_id: str, dev: _OpenDevice) -> None:
        try:
            pressed = read_initial_key_state(dev.fd, dev.caps.key_codes)
            abs_values = read_current_abs_values(dev.fd, set(dev.caps.abs_ranges))
        except OSError:
            return
        dev.mapper.resync(abs_values, pressed)
        dev.dirty_since = time.monotonic()

    def _flush_dirty(self, now: float) -> None:
        for device_id, dev in self.devices.items():
            if dev.dirty_since is None or (now - dev.dirty_since) < COALESCE_SECONDS:
                continue
            masked, changed = self.assigner.process(device_id, dev.mapper.state)
            dev.dirty_since = None
            index = self.assigner.index_for(device_id)
            if index is not None:
                self.emit({"type": "state", "index": index, "id": device_id,
                           "gamepadType": dev.gamepad_type, "state": masked})
                dev.last_emit = now
            if changed:
                self._maybe_emit_devices([])

    def _send_keepalives(self, now: float) -> None:
        for device_id, dev in self.devices.items():
            index = self.assigner.index_for(device_id)
            if index is None:
                continue
            if now - dev.last_emit >= KEEPALIVE_SECONDS:
                masked, _changed = self.assigner.process(device_id, dev.mapper.state)
                self.emit({"type": "state", "index": index, "id": device_id,
                           "gamepadType": dev.gamepad_type, "state": masked})
                dev.last_emit = now


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pyftc.gamepad")
    ap.add_argument("--auto", action="store_true",
                     help="assign the first two controllers found to gamepad1/gamepad2 automatically")
    args = ap.parse_args(argv)
    runner = Runner(auto=args.auto)
    try:
        return runner.run()
    except Exception as e:  # noqa: BLE001 - boundary with the CLI/extension
        print(json.dumps({"type": "error", "message": str(e)}))
        print(f"pyftc.gamepad: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
