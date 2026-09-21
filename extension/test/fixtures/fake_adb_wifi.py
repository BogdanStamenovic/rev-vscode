#!/usr/bin/env python3
"""Fake `adb` reproducing the Wi-Fi failure seen on the real hub.

The property that matters, and that real adb has: `adb connect` against an
address that already has an entry answers "already connected to ..." and
leaves the entry as it is - including when that entry is "offline". The old
code treated that answer as success, so a stale offline entry made every
read fail until the link happened to reset itself.

State lives in $FAKE_ADB_STATE_DIR:
  entry          absent (no file), or "device" / "offline"
  connect        what a fresh `adb connect` produces: device (default), offline, fail
  truncate_once  if present, the next `cat` returns cut-short XML, then it is removed
  drop_once      if present, the next `cat` fails "device offline" and marks the entry offline
  calls.log      one line per invocation: start/end time and argv, for overlap checks
"""
import os
import sys
import time

D = os.environ["FAKE_ADB_STATE_DIR"]
ADDR = "192.168.43.1:5555"


def path(name):
    return os.path.join(D, name)


def read(name, default=None):
    try:
        with open(path(name)) as f:
            return f.read().strip()
    except FileNotFoundError:
        return default


def write(name, value):
    with open(path(name), "w") as f:
        f.write(value)


def main(args):
    entry = read("entry")
    if args == ["devices"]:
        print("List of devices attached")
        if entry:
            print(f"{ADDR}\t{entry}")
        return 0
    if args[:1] == ["connect"]:
        if entry:
            print(f"already connected to {args[1]}")
            return 0
        outcome = read("connect", "device")
        if outcome == "fail":
            print(f"failed to connect to '{args[1]}': No route to host")
            return 1
        write("entry", outcome)
        print(f"connected to {args[1]}")
        return 0
    if args[:1] == ["disconnect"]:
        if entry:
            os.remove(path("entry"))
            print(f"disconnected {args[1]}")
            return 0
        print(f"error: no such device '{args[1]}'")
        return 1
    if args[:2] == ["-s", ADDR]:
        rest = args[2:]
        if not entry:
            sys.stderr.write(f"error: device '{ADDR}' not found\n")
            return 1
        if rest == ["get-state"]:
            if entry == "device":
                print("device")
                return 0
            sys.stderr.write(f"error: device {entry}\n")
            return 1
        if rest[:2] == ["shell", "cat"]:
            if entry != "device":
                sys.stderr.write(f"adb: device {entry}\n")
                return 1
            if read("drop_once") is not None:
                os.remove(path("drop_once"))
                write("entry", "offline")
                sys.stderr.write("adb: device offline\n")
                return 1
            with open(os.environ["FAKE_HUB_CONFIG_XML"]) as f:
                xml = f.read()
            if read("truncate_once") is not None:
                os.remove(path("truncate_once"))
                xml = xml[: len(xml) // 2]
            sys.stdout.write(xml)
            return 0
    sys.stderr.write(f"fake_adb_wifi: unsupported {args}\n")
    return 2


start = time.monotonic()
time.sleep(0.03)  # long enough that overlapping processes would be visible in calls.log
code = main(sys.argv[1:])
with open(path("calls.log"), "a") as f:
    f.write(f"{start:.4f} {time.monotonic():.4f} {' '.join(sys.argv[1:])}\n")
sys.exit(code)
