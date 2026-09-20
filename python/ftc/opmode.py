from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

if TYPE_CHECKING:
    from ftc.hardware import EventLoopManager, Gamepad, HardwareMap, TelemetryMessage
    from ftc.internal import OnBotJavaHelper, OpModeMeta, RobotState
    from ftc.telemetry import Telemetry
    from ftc.util import WeakReferenceSet, WebServer

_AnnotationTargetT = TypeVar("_AnnotationTargetT")
class OpModeManager:
    """OpModeManager instances are used to register OpModes for use."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManager"
    @overload
    def register(self, name: str, opModeClass: type[OpMode]) -> None:
        """Registers a class for display on the driver station and availability for game play. New instances of this class will be created as needed."""
        ...
    @overload
    def register(self, name: OpModeMeta, opModeClass: type[OpMode]) -> None:
        """Registers a class for display on the driver station and availability for game play. New instances of this class will be created as needed."""
        ...
    @overload
    def register(self, name: str, opModeInstance: OpMode) -> None:
        """Register an *instance* of a class for display on the driver station and availability for game play. You won't likely use this method very often."""
        ...
    @overload
    def register(self, name: OpModeMeta, opModeInstance: OpMode) -> None:
        """Register an *instance* of a class for display on the driver station and availability for game play. You won't likely use this method very often."""
        ...
    def register(self, *args: Any, **kwargs: Any) -> Any:
        ...

    DEFAULT_OP_MODE_NAME: str
    """DEFAULT_OP_MODE_NAME is the (non-localized) name of the default OpMode, the one that automatically runs whenever no user OpMode is running."""


class AnnotatedOpModeManager(OpModeManager):
    """OpModeManager instances are used as part of a decentralized OpMode registration mechanism."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.AnnotatedOpModeManager"
    def register(self, opModeClass: type[object]) -> None:
        """Register a class for display on the driver station and availability for game play. New instances of this class will be created as needed. The name used on the driver station menu is taken from a TeleOp or Autonomous annotation on the class itself (any Disabled attribute which may also be present is ignored). If the class lacks both a TeleOp and a Autonomous annotation, then no registration takes place."""
        ...


class AnnotatedOpModeRegistrar:
    """Call AnnotatedOpModeRegistrar#register(OpModeManager) from FtcOpModeRegister.register() in order to automatically register OpMode classes that you have annotated with @Autonomous or @TeleOp."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.AnnotatedOpModeRegistrar"
    @staticmethod
    def register(manager: OpModeManager) -> None:
        ...


class Autonomous:
    """Provides an easy and non-centralized way of determining the OpMode list shown on an FTC Driver Station. Put an Autonomous annotation on your autonomous OpModes that you want to show up in the driver station display. If you want to temporarily disable an OpMode, then set then also add a Disabled annotation to it."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.Autonomous"
    def __init__(self, *, name: str = '', group: str = '', preselectTeleOp: str = '') -> None:
        ...
    def __call__(self, target: type[_AnnotationTargetT]) -> type[_AnnotationTargetT]:
        return target


class Disabled:
    """Provides a way to temporarily disable an OpMode annotated with Autonomous or TeleOp from showing up on the driver station OpMode list."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.Disabled"
    def __new__(cls, target: type[_AnnotationTargetT]) -> type[_AnnotationTargetT]:
        return target


class EventLoopManagerClient:
    """Provides certain functionality to the EventLoopManager from its client"""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.EventLoopManagerClient"
    def getWebServer(self) -> WebServer:
        ...

    def getOnBotJavaHelper(self) -> OnBotJavaHelper:
        ...


class FtcRobotControllerServiceState(EventLoopManagerClient):
    """Created by David on 7/7/2017."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.FtcRobotControllerServiceState"
    def getEventLoopManager(self) -> EventLoopManager:
        ...


class OpModeInternal:
    """This class is package-private, and has many package-private members. Do NOT mark them as protected, since we do not want to make them available to the user's subclasses (we don't want to make the API surface huge), only the OpMode and LinearOpMode subclasses."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeInternal"
    def requestOpModeStop(self) -> None:
        """Requests that this OpMode be shut down if it is the currently active OpMode, much as if the stop button had been pressed on the driver station."""
        ...

    def internalRunOpMode(self) -> None:
        """Called on the OpModeThread when the OpMode is initialized"""
        ...

    def internalOnStart(self) -> None:
        """Called on the main event loop thread when the OpMode is started."""
        ...

    def internalOnEventLoopIteration(self) -> None:
        """Called on the main event loop thread periodically."""
        ...

    def internalOnStopRequested(self) -> None:
        """Called on the main event loop thread when the OpMode is requested to stop."""
        ...

    def newGamepadDataAvailable(self, latestGamepad1Data: Gamepad, latestGamepad2Data: Gamepad) -> None:
        """Called on the main event loop thread when new gamepad data is available."""
        ...

    def internalInit(self) -> None:
        ...

    def internalStart(self) -> None:
        ...

    def internalThrowOpModeExceptionIfPresent(self) -> None:
        ...

    def internalStop(self) -> None:
        ...

    MS_BEFORE_FORCE_STOP_AFTER_STOP_REQUESTED: int
    """The approximate duration in milliseconds that the OpMode is allowed to run after a stop has been requested before it is considered stuck and is forcefully stopped."""
    gamepad1: Gamepad
    """Gamepad 1"""
    gamepad2: Gamepad
    """Gamepad 2"""
    telemetry: Telemetry
    """Allows text and numerical data to be transmitted for display on the Driver Station. This data is automatically transmitted on a regular, periodic basis."""
    hardwareMap: HardwareMap
    """Mapping of configured device names to Java objects that can be used to access them"""
    msStuckDetectStop: int
    executorService: Any
    internalOpModeServices: OpModeServices
    isStarted: bool
    stopRequested: bool
    opModeThreadFinished: bool
    exception: Any
    noClassDefFoundError: Any
    previousGamepad1Data: Gamepad
    previousGamepad2Data: Gamepad


class OpMode(OpModeInternal):
    """Base class for user-defined iterative operation modes (OpModes)."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpMode"
    def __init__(self) -> None:
        """OpMode constructor"""
        ...

    def init(self) -> None:
        """User-defined init method"""
        ...

    def init_loop(self) -> None:
        """User-defined init_loop method"""
        ...

    def start(self) -> None:
        """User-defined start method"""
        ...

    def loop(self) -> None:
        """User-defined loop method"""
        ...

    def stop(self) -> None:
        """User-defined stop method"""
        ...

    def terminateOpModeNow(self) -> None:
        """Immediately stops execution of the calling OpMode and transitions to the STOP state. No further code in the OpMode will execute once this has been called."""
        ...

    def getRuntime(self) -> float:
        """Gets the number of seconds this OpMode has been running."""
        ...

    def resetRuntime(self) -> None:
        """Resets the runtime to zero."""
        ...

    def updateTelemetry(self, telemetry: Telemetry) -> None:
        """Refreshes the user's telemetry on the driver station with the contents of the provided telemetry object if a nominal amount of time has passed since the last telemetry transmission. Once transmitted, the contents of the telemetry object are (by default) cleared."""
        ...

    def internalRunOpMode(self) -> None:
        ...

    def newGamepadDataAvailable(self, latestGamepad1Data: Gamepad, latestGamepad2Data: Gamepad) -> None:
        ...

    def internalUpdateTelemetryNow(self, telemetry: TelemetryMessage) -> None:
        """This is an internal SDK method, not intended for use by user opmodes."""
        ...

    def internalPreInit(self) -> None:
        ...

    def internalPostInitLoop(self) -> None:
        ...

    def internalPostLoop(self) -> None:
        ...

    blackboard: dict[str, object]
    """this is to store information in between opmodes"""
    time: float
    """The number of seconds this OpMode has been running. This is updated before every call to loop()."""
    msStuckDetectInit: int
    """OpModes no longer have a time limit for init()"""
    msStuckDetectInitLoop: int
    """OpModes no longer have a time limit for init_loop()"""
    msStuckDetectStart: int
    """OpModes no longer have a time limit for start()"""
    msStuckDetectLoop: int
    """OpModes no longer have a time limit for loop()"""


class LinearOpMode(OpMode):
    """Base class for user defined linear operation modes (linear OpModes)."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.LinearOpMode"
    def __init__(self) -> None:
        """LinearOpMode constructor"""
        ...

    def runOpMode(self) -> None:
        """Override this method and place your code here."""
        ...

    def waitForStart(self) -> None:
        """Pauses until the play button has been pressed (or until the current thread gets interrupted, which typically indicates that the OpMode has been stopped)."""
        ...

    def idle(self) -> None:
        """Puts the current thread to sleep for a bit as it has nothing better to do. This allows other threads in the system to run. One can use this method when you have nothing better to do in your code as you await state managed by other threads to change. Calling idle() is entirely optional: it just helps make the system a little more responsive and a little more efficient."""
        ...

    def sleep(self, milliseconds: int) -> None:
        """Sleeps for the given amount of milliseconds, or until the thread is interrupted (which usually indicates that the OpMode has been stopped). This is simple shorthand for Thread#sleep(long), but it does not throw InterruptedException."""
        ...

    def opModeIsActive(self) -> bool:
        """Determine whether this OpMode is in the Run phase (meaning it has been started and not yet told to stop). For safety reasons, the Run phase is the only time that the robot should move freely, so if this method returns false, the robot should not make any significant movements. If this method returns false after #waitForStart() has previously been called, you should break out of any loops and allow the OpMode to exit at its earliest convenience. Note that this method calls #idle() internally."""
        ...

    def opModeInInit(self) -> bool:
        """Determine whether this OpMode is still in the Init phase (indicating that the play button has not been pressed and the OpMode has not been stopped)."""
        ...

    def isStarted(self) -> bool:
        """Determine if the OpMode has been started (the play button has been pressed). To avoid difficult-to-debug deadlocks, this method will also return true if the current thread has been interrupted (which typically indicates that the OpMode has been told to stop), even if the play button has not been pressed."""
        ...

    def isStopRequested(self) -> bool:
        """Determine whether the OpMode has been asked to stop. If this method returns false, you should break out of any loops and allow the OpMode to exit at its earliest convenience."""
        ...

    def init(self) -> None:
        """This method may not be overridden by linear OpModes"""
        ...

    def init_loop(self) -> None:
        """This method may not be overridden by linear OpModes"""
        ...

    def start(self) -> None:
        """This method may not be overridden by linear OpModes"""
        ...

    def loop(self) -> None:
        """This method may not be overridden by linear OpModes"""
        ...

    def stop(self) -> None:
        """This method may not be overridden by linear OpModes"""
        ...

    def internalRunOpMode(self) -> None:
        ...

    def internalOnStart(self) -> None:
        ...

    def internalOnEventLoopIteration(self) -> None:
        ...

    def internalOnStopRequested(self) -> None:
        ...

    def newGamepadDataAvailable(self, latestGamepad1Data: Gamepad, latestGamepad2Data: Gamepad) -> None:
        ...


class OpModeManagerNotifier:
    """OpModeManagerNotifier.Notifications is an interface by which interested parties can receive notification of the coming and going of OpModes."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerNotifier"
    class Notifications:
        """Notifications can be used to receive notifications of the comings and goings of OpModes in the system. These notifications are sent to any HardwareDevice in the hardware map that additional implements the Notifications interface. Notifications may also be received by objects that register themselves with the OpMode manager."""
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerNotifier.Notifications"
        def onOpModePreInit(self, opMode: OpMode) -> None:
            """The indicated OpMode is just about to be initialized."""
            ...

        def onOpModePreStart(self, opMode: OpMode) -> None:
            """The indicated OpMode is just about to be started."""
            ...

        def onOpModePostStop(self, opMode: OpMode) -> None:
            """The indicated OpMode has just been stopped."""
            ...

    def registerListener(self, listener: OpModeManagerNotifier.Notifications) -> OpMode:
        """Registers an object as explicitly interested in receiving notifications as to the coming and going of OpModes."""
        ...

    def unregisterListener(self, listener: OpModeManagerNotifier.Notifications) -> None:
        """Unregisters a previously registered listener. If the provided listener is in fact not currently registered, the call has no effect."""
        ...


class OpModeServices:
    __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.OpModeServices"
    def refreshUserTelemetry(self, telemetry: TelemetryMessage, sInterval: float) -> None:
        """Update's the user portion of the driver station screen with the contents of the telemetry object here provided if a sufficiently long duration has passed since the last update."""
        ...

    def requestOpModeStop(self, opModeToStopIfActive: OpMode) -> None:
        """If the indicated OpMode is the currently active OpMode, cause that OpMode to stop as if the stop button had been pressed on the driver station"""
        ...


class OpModeManagerImpl(OpModeServices, OpModeManagerNotifier):
    """OpModeManagerImpl is the owner of the concept of a 'current' OpMode."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl"
    class OpModeStateTransition:
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.OpModeStateTransition"
        def apply(self) -> None:
            ...

        def copy(self) -> OpModeManagerImpl.OpModeStateTransition:
            ...

        queuedOpModeMetadata: OpModeMeta
        opModeSwapNeeded: bool
        callToInitNeeded: bool
        gamepadResetNeeded: bool
        telemetryClearNeeded: bool
        callToStartNeeded: bool
        onlyTransitionIfDefaultOpModeIsRunning: bool

    class OpModeState(enum.Enum):
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.OpModeState"
        INIT = enum.auto()
        LOOPING = enum.auto()

    class ForceStopException(Exception):
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.ForceStopException"

    class OpModeStuckCodeMonitor:
        """A utility class that detects infinite loops in user code"""
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.OpModeStuckCodeMonitor"
        class Runner:
            __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.OpModeStuckCodeMonitor.Runner"
            def run(self) -> None:
                ...

            msgForceStoppedCommon: str
            msgForceStoppedPopupIterative: str
            msgForceStoppedPopupLinear: str

        def startMonitoring(self, msTimeout: int, method: str, resetDebuggerCheck: bool) -> None:
            ...

        def stopMonitoring(self) -> None:
            ...

        def shutdown(self) -> None:
            ...

        def checkForDebugger(self) -> bool:
            ...

        executorService: Any
        stopped: Any
        acquired: Any
        debuggerDetected: bool
        msTimeout: int
        method: str

    class DefaultOpMode(OpMode):
        """DefaultOpMode is the OpMode that the system runs when no user OpMode is active. Note that it's not necessarily the case that this OpMode runs when a user OpMode stops: there are situations in which we can transition directly for one user OpMode to another."""
        __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl.DefaultOpMode"
        def __init__(self) -> None:
            ...

        def init(self) -> None:
            ...

        def init_loop(self) -> None:
            ...

        def loop(self) -> None:
            ...

        def stop(self) -> None:
            ...

    def __init__(self, activity: Any, hardwareMap: HardwareMap) -> None:
        ...

    @staticmethod
    def shouldPreventDangerousHardwareAccess() -> bool:
        ...

    @staticmethod
    def getOpModeManagerOfActivity(activity: Any) -> OpModeManagerImpl:
        ...

    def init(self, eventLoopManager: EventLoopManager) -> None:
        ...

    def teardown(self) -> None:
        ...

    def registerListener(self, listener: OpModeManagerNotifier.Notifications) -> OpMode:
        ...

    def unregisterListener(self, listener: OpModeManagerNotifier.Notifications) -> None:
        ...

    def setActiveOpMode(self, opMode: OpMode, activeOpModeName: str) -> None:
        ...

    def setHardwareMap(self, hardwareMap: HardwareMap) -> None:
        ...

    def getHardwareMap(self) -> HardwareMap:
        ...

    def getRobotState(self) -> RobotState:
        ...

    def getActiveOpModeName(self) -> str:
        ...

    def getActiveOpMode(self) -> OpMode:
        ...

    def doMatchLoggingWork(self, opModeName: str, isSystemOpMode: bool) -> None:
        ...

    def setMatchNumber(self, matchNumber: int) -> None:
        ...

    @overload
    def initOpMode(self, opModeName: str) -> None:
        ...
    @overload
    def initOpMode(self, opModeName: str, onlyInitIfDefaultIsRunning: bool) -> None:
        ...
    def initOpMode(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def startActiveOpMode(self) -> None:
        ...

    def stopActiveOpMode(self) -> None:
        ...

    def runActiveOpMode(self, opModeGamepads: list[Gamepad], latestGamepad1Data: Gamepad, latestGamepad2Data: Gamepad) -> None:
        ...

    def resetHardwareForOpMode(self) -> None:
        ...

    def callActiveOpModeStop(self) -> None:
        ...

    @overload
    def detectStuck(self, msTimeout: int, method: str, runnable: Any) -> None:
        ...
    @overload
    def detectStuck(self, msTimeout: int, method: str, runnable: Any, resetDebuggerCheck: bool) -> None:
        ...
    def detectStuck(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def callActiveOpModeInit(self) -> None:
        ...

    def callActiveOpModeStart(self) -> None:
        ...

    def checkOnActiveOpMode(self) -> None:
        ...

    def handleUserCodeException(self, e: Any) -> None:
        ...

    def handleSendStacktrace(self, e: Any) -> None:
        ...

    @staticmethod
    def updateTelemetryNow(opMode: OpMode, telemetry: TelemetryMessage) -> None:
        """For the use of TelemetryImpl."""
        ...

    def refreshUserTelemetry(self, telemetry: TelemetryMessage, sInterval: float) -> None:
        ...

    def requestOpModeStop(self, opModeToStopIfActive: OpMode) -> None:
        """Requests that an OpMode be stopped."""
        ...

    matchNumber: int
    preventDangerousHardwareAccess: bool
    TAG: str
    DEFAULT_OP_MODE_NAME: str
    context: Any
    activeOpModeName: str
    activeOpMode: OpModeInternal
    queuedOpModeMetadata: OpModeMeta
    hardwareMap: HardwareMap
    eventLoopManager: EventLoopManager
    listeners: WeakReferenceSet[OpModeManagerNotifier.Notifications]
    stuckMonitor: OpModeManagerImpl.OpModeStuckCodeMonitor
    peerWasConnected: bool
    opModeState: OpModeManagerImpl.OpModeState
    opModeSwapNeeded: bool
    callToInitNeeded: bool
    callToStartNeeded: bool
    gamepadResetNeeded: bool
    telemetryClearNeeded: bool
    nextOpModeState: Any
    mapActivityToOpModeManager: Any


class OpModeRegister:
    """Register OpModes"""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeRegister"
    def register(self, manager: OpModeManager) -> None:
        """The OpMode Manager will call this method when it wants a list of all available OpModes. Add you OpMode to the list to enable it."""
        ...


class OpModeRegistrar:
    """Provides an easy and non-centralized way of contributing to the OpMode list shown on an FTC Driver Station. While Autonomous and TeleOp annotations can be placed on your *own* classes to register them, to register classes found in libraries *other* than your own it is best to use a mechanism that does not require that you modify source code in that other library. OpModeRegistrar provides such a mechanism. Place an OpModeRegistrar annotation on a static method in your code that accepts a parameter of type OpModeManager or AnnotatedOpModeManager, and that method will be automatically called at the right time to register OpModes. You can use any of the register() methods that exist on the AnnotatedOpModeManager to register OpModes."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.OpModeRegistrar"
    def __new__(cls, target: type[_AnnotationTargetT]) -> type[_AnnotationTargetT]:
        return target


class TeleOp:
    """Provides an easy and non-centralized way of determining the OpMode list shown on an FTC Driver Station. Put an TeleOp annotation on your teleop OpModes that you want to show up in the driver station display. If you want to temporarily disable an OpMode from showing up, then set then also add a Disabled annotation to it."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.TeleOp"
    def __init__(self, *, name: str = '', group: str = '') -> None:
        ...
    def __call__(self, target: type[_AnnotationTargetT]) -> type[_AnnotationTargetT]:
        return target


class Utility:
    """Provides an easy and non-centralized way of determining the OpMode list shown on an FTC Driver Station. Put a Utility annotation on your utility OpModes that you want to show up in the driver station display."""
    __java__ = "com.qualcomm.robotcore.eventloop.opmode.Utility"
    def __init__(self, *, name: str = '', description: str = '') -> None:
        ...
    def __call__(self, target: type[_AnnotationTargetT]) -> type[_AnnotationTargetT]:
        return target
