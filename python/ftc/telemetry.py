from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

if TYPE_CHECKING:
    from ftc.hardware import Gamepad, HardwareMap
    from ftc.opmode import LinearOpMode, OpMode

EXCEPTION = TypeVar("EXCEPTION", bound="Any")
R = TypeVar("R")
T = TypeVar("T")
VALUE = TypeVar("VALUE")
class BlocksOpModeCompanion:
    """An abstract base class that provides access to hardwareMap, telemetry, gamepad1, and gamepad2, in order to assist a novice Java coder who wants to implement some code in Java that can be called from a Blocks OpMode. The use of this class is not required for exporting a method to the Blocks programming environment. See ExportToBlocks for details on how to export a method to Blocks."""
    __java__ = "org.firstinspires.ftc.robotcore.external.BlocksOpModeCompanion"
    opMode: OpMode
    """The currently running Blocks OpMode, as an OpMode."""
    linearOpMode: LinearOpMode
    """The currently running Blocks OpMode, as an LinearOpMode."""
    hardwareMap: HardwareMap
    """Hardware mappings."""
    telemetry: Telemetry
    """The #telemetry field contains an object in which a user may accumulate data which is to be transmitted to the driver station. This data is automatically transmitted to the driver station on a regular, periodic basis."""
    gamepad1: Gamepad
    """Gamepad 1"""
    gamepad2: Gamepad
    """Gamepad 2"""


class ClassFactory:
    """ClassFactory provides a means by which various objects in the SDK may be logically instantiated without exposing their external class identities to user's programs."""
    __java__ = "org.firstinspires.ftc.robotcore.external.ClassFactory"
    class InstanceHolder:
        __java__ = "org.firstinspires.ftc.robotcore.external.ClassFactory.InstanceHolder"
        theInstance: ClassFactory

    @staticmethod
    def getInstance() -> ClassFactory:
        ...

    def getCameraManager(self) -> Any:
        """Returns a CameraManager which can be used to access the USB webcams attached to the robot controller."""
        ...

    @staticmethod
    def createSwitchableCameraNameForAllWebcams(hardwareMap: HardwareMap) -> Any:
        """Returns a name of a virtual camera comprised of all the webcams configured in the given hardware map."""
        ...


def Const(cls: type) -> type:
    """Const documents a method that promises not to change the internal state of the method receiver. Documenting methods in this way helps programmers understand which methods examine the object and return results based on that examination but don't change the internal object state and which methods, by contrast, perform their function but updating or changing internal object state."""
    return cls


class Consumer(Generic[T]):
    """Instances of Consumer are functions that act on an instance of a indicated type"""
    __java__ = "org.firstinspires.ftc.robotcore.external.Consumer"
    def accept(self, value: T) -> None:
        """Performs this operation on the given argument."""
        ...


class Event:
    """A state machine event. Implement this interface as an enumeration to define states for a given state machine."""
    __java__ = "org.firstinspires.ftc.robotcore.external.Event"
    def getName(self) -> str:
        ...


def ExportAprilTagLibraryToBlocks(*, color: int = 289, heading: str = 'call', comment: str = '', tooltip: str = '', parameterLabels: list[str], parameterDefaultValues: list[str]) -> Callable[[type], type]:
    """ExportAprilTagLibraryToBlocks indicates that a method that returns an AprilTagLibrary is exported to the Blocks programming environment. This annotation provides a way for the Java coder to specify some UI attributes of the \"call Java method\" block. The corresponding block will appear in the Blocks toolbox along with the built-in tag libraries. The method must satisfy all of these requirements:"""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


def ExportClassToBlocks(cls: type) -> type:
    """ExportClassToBlocks indicates that the class contains methods which are exported to blocks. Exported methods must be annotated with ExportToBlocks"""
    return cls


def ExportEnumToBlocks(*, color: int = 151) -> Callable[[type], type]:
    """ExportEnumToBlocks indicates that an enum is exported to the Blocks programming environment. This annotation provides a way for the Java coder to specify the color of the enum block. The enum must satisfy all of these requirements:"""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


def ExportToBlocks(*, color: int = 289, heading: str = 'call Java method', comment: str = '', tooltip: str = '', parameterLabels: list[str], parameterDefaultValues: list[str]) -> Callable[[type], type]:
    """ExportToBlocks indicates that a method is exported to the Blocks programming environment. This annotation provides a way for the Java coder to specify some UI attributes of the \"call Java method\" block. If the method is not in a hardware device class, it must satisfy all of these requirements:"""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class Func(Generic[T]):
    """Instances of Func are nullary producers of values. TODO: uses of this should probably be replaced with uses of Supplier."""
    __java__ = "org.firstinspires.ftc.robotcore.external.Func"
    def value(self) -> T:
        """Returns a value of the indicated type"""
        ...


class Function(Generic[T, R]):
    """If we were running Java8, we'd just use the built-in interface"""
    __java__ = "org.firstinspires.ftc.robotcore.external.Function"
    def apply(self, arg: T) -> R:
        ...


class JavaUtil:
    """A class that provides utility methods used in FTC Java code generated from blocks."""
    __java__ = "org.firstinspires.ftc.robotcore.external.JavaUtil"
    class AtMode(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.external.JavaUtil.AtMode"
        FIRST = enum.auto()
        LAST = enum.auto()
        FROM_START = enum.auto()
        FROM_END = enum.auto()
        RANDOM = enum.auto()

    class TrimMode(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.external.JavaUtil.TrimMode"
        LEFT = enum.auto()
        RIGHT = enum.auto()
        BOTH = enum.auto()

    class SortType(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.external.JavaUtil.SortType"
        NUMERIC = enum.auto()
        TEXT = enum.auto()
        IGNORE_CASE = enum.auto()

    class SortDirection(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.external.JavaUtil.SortDirection"
        ASCENDING = enum.auto()
        DESCENDING = enum.auto()

    @staticmethod
    def inTextGetLetter(str: str, atMode: JavaUtil.AtMode, i: int) -> str:
        ...

    @staticmethod
    def inTextGetSubstring(str: str, atMode1: JavaUtil.AtMode, i1: int, atMode2: JavaUtil.AtMode, i2: int) -> str:
        ...

    @staticmethod
    def toTitleCase(str: str) -> str:
        ...

    @staticmethod
    def textTrim(str: str, trimMode: JavaUtil.TrimMode) -> str:
        ...

    @overload
    @staticmethod
    def formatNumber(number: float, precision: int) -> str:
        ...
    @overload
    @staticmethod
    def formatNumber(number: float, width: int, precision: int) -> str:
        ...
    @staticmethod
    def formatNumber(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def isPrime(d: float) -> bool:
        ...

    @overload
    @staticmethod
    def sumOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def sumOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def sumOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def minOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def minOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def minOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def maxOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def maxOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def maxOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def averageOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def averageOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def averageOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def medianOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def medianOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def medianOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def modesOfList(list: list[object]) -> list[object]:
        ...
    @overload
    @staticmethod
    def modesOfList(list: list[object]) -> list[object]:
        ...
    @staticmethod
    def modesOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def standardDeviationOfList(list: list[object]) -> float:
        ...
    @overload
    @staticmethod
    def standardDeviationOfList(list: list[object]) -> float:
        ...
    @staticmethod
    def standardDeviationOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def randomItemOfList(list: list[object]) -> object:
        ...
    @overload
    @staticmethod
    def randomItemOfList(list: list[object]) -> object:
        ...
    @staticmethod
    def randomItemOfList(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def randomInt(a: float, b: float) -> int:
        ...

    @staticmethod
    def createListWith(*elements: object) -> list[object]:
        ...

    @staticmethod
    def createListWithItemRepeated(element: object, n: int) -> list[object]:
        ...

    @staticmethod
    def listLength(o: object) -> int:
        ...

    @staticmethod
    def listIsEmpty(o: object) -> bool:
        ...

    @overload
    @staticmethod
    def inListGet(list: list[object], atMode: JavaUtil.AtMode, i: int, remove: bool) -> object:
        ...
    @overload
    @staticmethod
    def inListGet(list: list[object], atMode: JavaUtil.AtMode, i: int, remove: bool) -> object:
        ...
    @staticmethod
    def inListGet(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def inListSet(list: list[object], atMode: JavaUtil.AtMode, i: int, insert: bool, value: object) -> None:
        ...
    @overload
    @staticmethod
    def inListSet(list: list[object], atMode: JavaUtil.AtMode, i: int, insert: bool, value: object) -> None:
        ...
    @staticmethod
    def inListSet(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def inListGetSublist(list: list[object], atMode1: JavaUtil.AtMode, i1: int, atMode2: JavaUtil.AtMode, i2: int) -> list[object]:
        ...
    @overload
    @staticmethod
    def inListGetSublist(list: list[object], atMode1: JavaUtil.AtMode, i1: int, atMode2: JavaUtil.AtMode, i2: int) -> list[object]:
        ...
    @staticmethod
    def inListGetSublist(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def sort(list: list[object], sortType: JavaUtil.SortType, sortDirection: JavaUtil.SortDirection) -> list[object]:
        ...
    @overload
    @staticmethod
    def sort(list: list[object], sortType: JavaUtil.SortType, sortDirection: JavaUtil.SortDirection) -> list[object]:
        ...
    @staticmethod
    def sort(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def makeTextFromList(list: list[object], delimiter: str) -> str:
        ...
    @overload
    @staticmethod
    def makeTextFromList(list: list[float], delimiter: str) -> str:
        ...
    @overload
    @staticmethod
    def makeTextFromList(list: list[object], delimiter: str) -> str:
        ...
    @staticmethod
    def makeTextFromList(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def makeListFromText(text: str, delimiter: str) -> list[object]:
        ...

    @staticmethod
    def colorToHue(color: int) -> float:
        ...

    @staticmethod
    def colorToSaturation(color: int) -> float:
        ...

    @staticmethod
    def colorToValue(color: int) -> float:
        ...

    @staticmethod
    def hsvToColor(hue: float, saturation: float, value: float) -> int:
        ...

    @staticmethod
    def ahsvToColor(alpha: int, hue: float, saturation: float, value: float) -> int:
        ...

    @staticmethod
    def rgbToHue(red: int, green: int, blue: int) -> float:
        ...

    @staticmethod
    def rgbToSaturation(red: int, green: int, blue: int) -> float:
        ...

    @staticmethod
    def rgbToValue(red: int, green: int, blue: int) -> float:
        ...

    @staticmethod
    def colorToText(color: int) -> str:
        ...

    @staticmethod
    def showColor(appContext: Any, color: int) -> None:
        ...

    @staticmethod
    def makeIntegerList(unboxed: list[int]) -> list[int]:
        ...

    @staticmethod
    def makeIntArray(list: list[int]) -> list[int]:
        ...

    @staticmethod
    def makeDoubleArray(list: list[float]) -> list[float]:
        ...


def NonConst(cls: type) -> type:
    """NonConst documents a method that performs its function by updating internal state of the method receiver. Documenting methods in this way helps programmers understand which methods examine the object and return results based on that examination but don't change the internal object state and which methods, by contrast, perform their function but updating or changing internal object state."""
    return cls


class Predicate(Generic[T]):
    __java__ = "org.firstinspires.ftc.robotcore.external.Predicate"
    def test(self, t: T) -> bool:
        ...


class SignificantMotionDetection:
    __java__ = "org.firstinspires.ftc.robotcore.external.SignificantMotionDetection"
    class SignificantMotionDetectionListener:
        __java__ = "org.firstinspires.ftc.robotcore.external.SignificantMotionDetection.SignificantMotionDetectionListener"
        def onSignificantMotion(self) -> None:
            ...

    class TriggerListener:
        __java__ = "org.firstinspires.ftc.robotcore.external.SignificantMotionDetection.TriggerListener"
        def onTrigger(self, triggerEvent: Any) -> None:
            ...

    def __init__(self) -> None:
        ...

    def startListening(self) -> None:
        """Start processing sensor data."""
        ...

    def stopListening(self) -> None:
        """Stop processing sensor data."""
        ...

    def registerListener(self, listener: SignificantMotionDetection.SignificantMotionDetectionListener) -> None:
        ...

    def notifyListeners(self) -> None:
        ...


class State:
    """A state for a given state machine. Implement this interface to define actions to happen upon transitions into and out of a given state."""
    __java__ = "org.firstinspires.ftc.robotcore.external.State"
    def onEnter(self, event: Event) -> None:
        """Called by the framework when a state is entered."""
        ...

    def onExit(self, event: Event) -> None:
        """Called by the framework when a state is exited."""
        ...


class StateMachine:
    """Infrastructure for a very simple generic state machine. Part of a collection of classes including State, Event, and StateTransition. All this class does is manage a directed graph and execute transitions on events. Create instances of a state machine by deriving from this class and defining states, events, and transitions. See usages of StateMachine for reference implementations."""
    __java__ = "org.firstinspires.ftc.robotcore.external.StateMachine"
    def __init__(self) -> None:
        ...

    def start(self, state: State) -> None:
        """start Define the start state of the state machine. Should be called from the start method of the feature's state machine."""
        ...

    def addTransition(self, transition: StateTransition) -> None:
        """addTransition Adds a transition to the state machine."""
        ...

    def consumeEvent(self, event: Event) -> State:
        """consumeEvent Executes a state transition and returns the new state. *"""
        ...

    def maskEvent(self, event: Event) -> None:
        ...

    def unMaskEvent(self, event: Event) -> None:
        ...

    def transition(self, event: Event) -> State:
        ...

    def toString(self) -> str:
        ...

    currentState: State
    stateGraph: dict[State, list[StateTransition]]
    maskList: list[Event]


class StateTransition:
    __java__ = "org.firstinspires.ftc.robotcore.external.StateTransition"
    def __init__(self, from_: State, event: Event, to: State) -> None:
        ...

    def toString(self) -> str:
        ...

    from_: State
    event: Event
    to: State


class Supplier(Generic[T]):
    """Represents a supplier of results. There is no requirement that a new or distinct result be returned each time the supplier is invoked. This is a functional interface whose functional method is get()."""
    __java__ = "org.firstinspires.ftc.robotcore.external.Supplier"
    def get(self) -> T:
        ...


class Telemetry:
    """Instances of Telemetry provide a means by which data can be transmitted from the robot controller to the driver station and displayed on the driver station screen. Simple use of Telemetry consists of a series of #addData(String, calls, followed by a call to #update(). For example:"""
    __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry"
    class Line:
        """Instances of Line build lines of data on the driver station telemetry display."""
        __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry.Line"
        @overload
        def addData(self, caption: str, format: str, *args: object) -> Telemetry.Item:
            """Adds a new data item at the end of the line which is the receiver."""
            ...
        @overload
        def addData(self, caption: str, value: object) -> Telemetry.Item:
            """Adds a new data item at the end of the line which is the receiver."""
            ...
        @overload
        def addData(self, caption: str, valueProducer: Func[T]) -> Telemetry.Item:
            """Adds a new data item at the end of the line which is the receiver."""
            ...
        @overload
        def addData(self, caption: str, format: str, valueProducer: Func[T]) -> Telemetry.Item:
            """Adds a new data item at the end of the line which is the receiver."""
            ...
        def addData(self, *args: Any, **kwargs: Any) -> Any:
            ...

    class Item:
        """Instances of Item represent an item of data on the drive station telemetry display."""
        __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry.Item"
        def getCaption(self) -> str:
            """Returns the caption associated with this item."""
            ...

        def setCaption(self, caption: str) -> Telemetry.Item:
            """Sets the caption associated with this item."""
            ...

        @overload
        def setValue(self, format: str, *args: object) -> Telemetry.Item:
            """Updates the value of this item to be the result of the indicated string formatting operation."""
            ...
        @overload
        def setValue(self, value: object) -> Telemetry.Item:
            """Updates the value of this item to be the result of applying Object#toString() to the indicated object."""
            ...
        @overload
        def setValue(self, valueProducer: Func[T]) -> Telemetry.Item:
            """Updates the value of this item to be the indicated value producer."""
            ...
        @overload
        def setValue(self, format: str, valueProducer: Func[T]) -> Telemetry.Item:
            """Updates the value of this item to be the indicated value producer."""
            ...
        def setValue(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def setRetained(self, retained: bool) -> Telemetry.Item:
            """Sets whether the item is to be retained in clear() operation or not. This is initially true for items that whose value is computed with a value producer; otherwise, it is initially false."""
            ...

        def isRetained(self) -> bool:
            """Returns whether the item is to be retained in a clear() operation."""
            ...

        @overload
        def addData(self, caption: str, format: str, *args: object) -> Telemetry.Item:
            """Adds a new data item in the associated Telemetry immediately following the receiver."""
            ...
        @overload
        def addData(self, caption: str, value: object) -> Telemetry.Item:
            """Adds a new data item in the associated Telemetry immediately following the receiver."""
            ...
        @overload
        def addData(self, caption: str, valueProducer: Func[T]) -> Telemetry.Item:
            """Adds a new data item in the associated Telemetry immediately following the receiver."""
            ...
        @overload
        def addData(self, caption: str, format: str, valueProducer: Func[T]) -> Telemetry.Item:
            """Adds a new data item in the associated Telemetry immediately following the receiver."""
            ...
        def addData(self, *args: Any, **kwargs: Any) -> Any:
            ...

    class DisplayFormat(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry.DisplayFormat"
        CLASSIC = enum.auto()
        MONOSPACE = enum.auto()
        HTML = enum.auto()

    class Log:
        """The Log in a Telemetry instance provides an append-only list of messages that appear on the driver station below the Items of the Telemetry."""
        __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry.Log"
        class DisplayOrder(enum.Enum):
            """DisplayOrder instances indicate the desired ordering of a #log()."""
            __java__ = "org.firstinspires.ftc.robotcore.external.Telemetry.Log.DisplayOrder"
            NEWEST_FIRST = enum.auto()
            OLDEST_FIRST = enum.auto()

        def getCapacity(self) -> int:
            """Returns the maximum number of lines which will be retained in a #log() and shown on the driver station display."""
            ...

        def setCapacity(self, capacity: int) -> None:
            ...

        def getDisplayOrder(self) -> Telemetry.Log.DisplayOrder:
            """Returns the order in which data in log is to be displayed on the driver station."""
            ...

        def setDisplayOrder(self, displayOrder: Telemetry.Log.DisplayOrder) -> None:
            ...

        @overload
        def add(self, entry: str) -> None:
            """Adds a new entry the the log. Transmits the updated log to the driver station at the earliest opportunity."""
            ...
        @overload
        def add(self, format: str, *args: object) -> None:
            """Adds a new entry to the log. Transmits the updated log to the driver station at the earliest opportunity."""
            ...
        def add(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def clear(self) -> None:
            """Removes all entries from this Log"""
            ...

    @overload
    def addData(self, caption: str, format: str, *args: object) -> Telemetry.Item:
        """Adds an item to the end of the telemetry being built for driver station display. The value shown will be the result of calling String#format(Locale, with the indicated format and arguments. The caption and value are shown on the driver station separated by the #getCaptionValueSeparator(). The item is removed if #clear() or #clearAll() is called."""
        ...
    @overload
    def addData(self, caption: str, value: object) -> Telemetry.Item:
        """Adds an item to the end if the telemetry being built for driver station display. The value shown will be the result of calling Object#toString() on the provided value object. The caption and value are shown on the driver station separated by the #getCaptionValueSeparator(). The item is removed if #clear() or #clearAll() is called."""
        ...
    @overload
    def addData(self, caption: str, valueProducer: Func[T]) -> Telemetry.Item:
        """Adds an item to the end of the telemetry being built for driver station display. The value shown will be the result of calling Object#toString() on the object which is returned from invoking valueProducer.Func#value() value()}. The caption and value are shown on the driver station separated by the #getCaptionValueSeparator(). The item is removed if #clearAll() is called, but not if #clear() is called. The valueProducer is evaluated only if actual transmission to the driver station is to occur. This is important, as it provides a means of displaying telemetry which is relatively expensive to evaluate while avoiding computation or delay on evaluations which won't be transmitted due to transmission interval throttling."""
        ...
    @overload
    def addData(self, caption: str, format: str, valueProducer: Func[T]) -> Telemetry.Item:
        """Adds an item to the end of the telemetry being built for driver station display. The value shown will be the result of calling String#format on the object which is returned from invoking valueProducer.Func#value() value()}. The caption and value are shown on the driver station separated by the #getCaptionValueSeparator(). The item is removed if #clearAll() is called, but not if #clear() is called. The valueProducer is evaluated only if actual transmission to the driver station is to occur. This is important, as it provides a means of displaying telemetry which is relatively expensive to evaluate while avoiding computation or delay on evaluations which won't be transmitted due to transmission interval throttling."""
        ...
    def addData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def removeItem(self, item: Telemetry.Item) -> bool:
        """Removes an item from the receiver telemetry, if present."""
        ...

    def clear(self) -> None:
        """Removes all items from the receiver whose value is not to be retained."""
        ...

    def clearAll(self) -> None:
        """Removes all items, lines, and actions from the receiver"""
        ...

    def addAction(self, action: Any) -> object:
        """In addition to items and lines, a telemetry may also contain a list of actions. When the telemetry is to be updated, these actions are evaluated before the telemetry lines are composed just prior to transmission. A typical use of such actions is to initialize some state variable, parts of which are subsequently displayed in items. This can help avoid needless re-evaluation. Actions are cleared with #clearAll(), and can be removed with #removeAction(Object)."""
        ...

    def removeAction(self, token: object) -> bool:
        """Removes a previously added action from the receiver."""
        ...

    @overload
    def speak(self, text: str) -> None:
        """Directs the Driver Station device to speak the given text using TextToSpeech functionality, with the same language and country codes that were previously used, or the default language and country."""
        ...
    @overload
    def speak(self, text: str, languageCode: str, countryCode: str) -> None:
        """Directs the Driver Station device to speak the given text using TextToSpeech functionality, with the given language and country codes."""
        ...
    def speak(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def update(self) -> bool:
        """Sends the receiver Telemetry to the driver station if more than the #getMsTransmissionInterval() has elapsed since the last transmission, or schedules the transmission of the receiver should no subsequent Telemetry state be scheduled for transmission before the #getMsTransmissionInterval() expires."""
        ...

    @overload
    def addLine(self) -> Telemetry.Line:
        """Creates and returns a new line in the receiver Telemetry."""
        ...
    @overload
    def addLine(self, lineCaption: str) -> Telemetry.Line:
        """Creates and returns a new line in the receiver Telemetry."""
        ...
    def addLine(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def removeLine(self, line: Telemetry.Line) -> bool:
        """Removes a line from the receiver telemetry, if present."""
        ...

    def isAutoClear(self) -> bool:
        """Answers whether #clear() is automatically called after each call to #update()."""
        ...

    def setAutoClear(self, autoClear: bool) -> None:
        """Sets whether #clear() is automatically called after each call to #update()."""
        ...

    def getMsTransmissionInterval(self) -> int:
        """Returns the minimum interval between Telemetry transmissions from the robot controller to the driver station"""
        ...

    def setMsTransmissionInterval(self, msTransmissionInterval: int) -> None:
        """Sets the minimum interval between Telemetry transmissions from the robot controller to the driver station."""
        ...

    def getItemSeparator(self) -> str:
        """Returns the string which is used to separate Items contained within a line. The default separator is \" | \"."""
        ...

    def setItemSeparator(self, itemSeparator: str) -> None:
        ...

    def getCaptionValueSeparator(self) -> str:
        """Returns the string which is used to separate caption from value within a Telemetry Item. The default separator is \" : \";"""
        ...

    def setCaptionValueSeparator(self, captionValueSeparator: str) -> None:
        ...

    def setDisplayFormat(self, displayFormat: Telemetry.DisplayFormat) -> None:
        """Sets the telemetry display format on the Driver Station. See the comments on DisplayFormat."""
        ...

    def setNumDecimalPlaces(self, minDecimalPlaces: int, maxDecimalPlaces: int) -> None:
        """Sets the number of decimal places for Double and Float"""
        ...

    def log(self) -> Telemetry.Log:
        """Returns the log of this Telemetry to which log entries may be appended."""
        ...


class ThrowingCallable(Generic[VALUE, EXCEPTION]):
    """An interface for workers that has a specialized exception set"""
    __java__ = "org.firstinspires.ftc.robotcore.external.ThrowingCallable"
    def call(self) -> VALUE:
        ...
