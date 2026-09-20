#!/usr/bin/env python3
"""Fake `adb` for the hardware-config-watch e2e suite (test/e2e/fakeSuite.js).

There is no real Control Hub in that suite - it exercises spawnStarterPack /
configWatch / updateFromConfig against `revFtc.hubUrl` pointing at
fakeHub.mjs (an HTTP server standing in for OnBot Java's rcInfo.json) and
`revFtc.adbPath` pointing at THIS script standing in for the one thing that
has no HTTP endpoint at all (ARCHITECTURE.md): reading the active hardware
config XML off /sdcard/FIRST. Only the handful of `adb` invocations
extension/src/hub/adb.ts actually makes are implemented; anything else exits
non-zero so a real bug (a new adb call we forgot to fake) fails loudly
instead of silently returning nothing.

The "current" config XML lives at $FAKE_HUB_CONFIG_XML, a plain file the
e2e suite rewrites between phases to simulate someone changing the robot's
hardware configuration on the Driver Hub and saving it - no HTTP endpoint to
poke, so a file swap is the fake-side equivalent of that.
"""
import os
import sys

SERIAL = os.environ.get("FAKE_HUB_SERIAL", "FAKEHUBSERIAL")
CONFIG_NAME = os.environ.get("FAKE_HUB_CONFIG_NAME", "TestConfig")


def main() -> int:
    args = sys.argv[1:]

    if args == ["devices"]:
        sys.stdout.write("List of devices attached\n")
        sys.stdout.write(f"{SERIAL}\tdevice\n")
        return 0

    if len(args) >= 2 and args[0] == "-s":
        serial, rest = args[1], args[2:]
        if serial != SERIAL:
            sys.stderr.write(f"fake_adb: unknown serial {serial}\n")
            return 1

        if rest[:2] == ["shell", "getprop"] and len(rest) == 3:
            value = "Control Hub" if rest[2] == "ro.product.model" else ""
            sys.stdout.write(value + "\n")
            return 0

        if rest[:2] == ["shell", "cat"] and len(rest) == 3:
            expected = f"/sdcard/FIRST/{CONFIG_NAME}.xml"
            xml_path = os.environ.get("FAKE_HUB_CONFIG_XML")
            if rest[2] != expected or not xml_path or not os.path.exists(xml_path):
                sys.stderr.write(f"cat: {rest[2]}: No such file or directory\n")
                return 1
            with open(xml_path, "r", encoding="utf-8") as f:
                sys.stdout.write(f.read())
            return 0

        if rest[:1] == ["forward"]:
            sys.stdout.write("9999\n")  # unused (revFtc.hubUrl bypasses adb forward)
            return 0

        if rest[:1] == ["connect"]:
            sys.stdout.write(f"connected to {serial}\n")
            return 0

    sys.stderr.write(f"fake_adb: unhandled invocation: {args}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
