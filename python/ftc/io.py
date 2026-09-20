"""File I/O for saving data across a Robot Controller power cycle
(e.g. an `aftercare.py` OpMode that writes values a `Main` OpMode reads back
at INIT next match).

`java.io.File` is a plain JDK class -- no FTC SDK artifact ships a
*-sources.jar for the JDK itself, so sdkgen has no declaration to stub it
from -- hand-written here to match python/pyftc/typedb.py's hand-written
slice member-for-member.

`AppUtil` (org.firstinspires.ftc.robotcore.internal.system.AppUtil) IS in the
SDK sources, but stubbing the whole class (~120 public methods: dialogs,
websockets, progress UI, none of it reachable from a Python OpMode) for the
two members teams actually call was measured and rejected -- see the comment
above the type database entry in python/pyftc/typedb.py for the numbers.
Only `getInstance()` and `getSettingsFile(String)` are hand-written here,
matching the same narrow slice.

ReadWriteFile actually lives in ftc.util (it's a real, fully-stubbed
com.qualcomm.robotcore.util class); this just re-exports it under the name
Contract 2 promises (`ftc.io`), the same precedent as ftc.gamepad."""
from __future__ import annotations

from typing import overload

from ftc.util import ReadWriteFile

__all__ = ["File", "AppUtil", "ReadWriteFile"]


class File:
    __java__ = "java.io.File"

    @overload
    def __init__(self, pathname: str) -> None: ...
    @overload
    def __init__(self, parent: File, child: str) -> None: ...
    def __init__(self, *args, **kwargs) -> None:
        ...

    def getName(self) -> str: ...
    def getPath(self) -> str: ...
    def getAbsolutePath(self) -> str: ...
    def exists(self) -> bool: ...
    def delete(self) -> bool: ...
    def mkdirs(self) -> bool: ...
    def length(self) -> int: ...


class AppUtil:
    __java__ = "org.firstinspires.ftc.robotcore.internal.system.AppUtil"

    @staticmethod
    def getInstance() -> AppUtil: ...

    def getSettingsFile(self, filename: str) -> File: ...
