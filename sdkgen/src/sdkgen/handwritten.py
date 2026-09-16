"""Static file content for the few python/ftc files that aren't derived from
Java sources. Kept here (not typed directly into python/ftc/) so a clean
generator run reproduces the whole package, per ARCHITECTURE.md."""

LANG_PY = '''"""Java-primitive spellings with no direct Python equivalent (or a
different width than Python's own `int`/`str`). These exist only so
generated/hand-written pyftc code can be explicit about which Java type the
translator should choose -- `long`, `short` and `byte` are otherwise all just
Python `int`, and `char` is a one-character `str`. They carry no runtime
behavior of their own.
"""

long = int
short = int
byte = int
char = str
float32 = float
'''

INIT_PY = '''"""Generated FTC SDK stub package.

Everything under ftc/ (except this file, lang.py and gamepad.py) is produced
by sdkgen from the FTC SDK sources -- see sdkgen/README or ARCHITECTURE.md.
It exists purely so Pylance/pyright can offer autocomplete, parameter names
and hover docs while writing OpMode code in this workspace; the translator
(python/pyftc) does not import it and trusts python/pyftc/data/sdk-<ver>.json
instead, so a mismatch here is a DX regression, not a build break.
"""
'''

GAMEPAD_PY = '''"""Gamepad lives in com.qualcomm.robotcore.hardware in the real SDK, so its
generated stub is in ftc.hardware; this module just re-exports it under the
name Contract 2 promises (`ftc.gamepad`)."""
from __future__ import annotations

from ftc.hardware import Gamepad

__all__ = ["Gamepad"]
'''
