"""Maps Java packages to Contract-2 python modules (the module table in
ARCHITECTURE.md). Subpackages of com.qualcomm.hardware are discovered from
the registry rather than hardcoded, so a new hardware vendor package in a
future SDK bump is picked up automatically.
"""
from __future__ import annotations

from .registry import Registry

# Packages excluded even though they sit under a wildcard root: registration/
# annotation machinery and low-level transports, not user-facing device APIs.
_HARDWARE_EXCLUDE_SUBPACKAGES = {"configuration"}

FIXED_PACKAGE_MODULE = {
    "com.qualcomm.robotcore.eventloop.opmode": "ftc.opmode",
    "com.qualcomm.robotcore.hardware": "ftc.hardware",
    "com.qualcomm.hardware.rev": "ftc.hardware",
    "com.qualcomm.hardware.lynx": "ftc.hardware",
    "org.firstinspires.ftc.robotcore.external": "ftc.telemetry",
    "org.firstinspires.ftc.robotcore.external.navigation": "ftc.navigation",
    "com.qualcomm.robotcore.util": "ftc.util",
    "org.firstinspires.ftc.vision": "ftc.vision",
    "org.firstinspires.ftc.vision.apriltag": "ftc.vision",
    "org.firstinspires.ftc.vision.opencv": "ftc.vision",
}


def build_package_module_map(registry: Registry) -> dict[str, str]:
    mapping = dict(FIXED_PACKAGE_MODULE)
    mapping.setdefault("com.qualcomm.hardware", "ftc.hardware")
    for pkg in registry.by_package:
        if pkg == "com.qualcomm.hardware" or pkg.startswith("com.qualcomm.hardware."):
            rest = pkg[len("com.qualcomm.hardware."):] if pkg != "com.qualcomm.hardware" else ""
            top_sub = rest.split(".")[0] if rest else ""
            if top_sub in _HARDWARE_EXCLUDE_SUBPACKAGES:
                continue
            if "." in rest:
                continue  # only one level deep, per contract table
            mapping[pkg] = "ftc.hardware"
    return mapping
