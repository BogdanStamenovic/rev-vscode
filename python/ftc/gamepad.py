"""Gamepad lives in com.qualcomm.robotcore.hardware in the real SDK, so its
generated stub is in ftc.hardware; this module just re-exports it under the
name Contract 2 promises (`ftc.gamepad`)."""
from __future__ import annotations

from ftc.hardware import Gamepad

__all__ = ["Gamepad"]
