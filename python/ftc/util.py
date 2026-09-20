from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

if TYPE_CHECKING:
    from ftc.hardware import Heartbeat, PeerDiscovery
    from ftc.internal import RobotControllerWebInfo, RobotCoreCommandList, RobotCoreException, WebHandler, WebObserver, WebSocketManager
    from ftc.telemetry import Predicate

E = TypeVar("E")
T = TypeVar("T")
X = TypeVar("X")
class AndroidSerialNumberNotFoundException(Exception):
    __java__ = "com.qualcomm.robotcore.util.AndroidSerialNumberNotFoundException"


class BatteryChecker:
    __java__ = "com.qualcomm.robotcore.util.BatteryChecker"
    class BatteryWatcher:
        __java__ = "com.qualcomm.robotcore.util.BatteryChecker.BatteryWatcher"
        def updateBatteryStatus(self, status: BatteryChecker.BatteryStatus) -> None:
            ...

    class BatteryStatus:
        __java__ = "com.qualcomm.robotcore.util.BatteryChecker.BatteryStatus"
        @overload
        def __init__(self, percent: float, isCharging: bool) -> None:
            ...
        @overload
        def __init__(self) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def serialize(self) -> str:
            ...

        @staticmethod
        def deserialize(serialized: str) -> BatteryChecker.BatteryStatus:
            ...

        percent: float
        isCharging: bool

    class Monitor:
        __java__ = "com.qualcomm.robotcore.util.BatteryChecker.Monitor"
        def onReceive(self, context: Any, intent: Any) -> None:
            ...

    def __init__(self, watcher: BatteryChecker.BatteryWatcher, delay: int) -> None:
        ...

    def startBatteryMonitoring(self) -> None:
        ...

    def close(self) -> None:
        ...

    def pollBatteryLevel(self, watcher: BatteryChecker.BatteryWatcher) -> None:
        ...

    def registerReceiver(self, receiver: Any) -> Any:
        ...

    def processBatteryChanged(self, intent: Any) -> None:
        ...

    def logBatteryInfo(self, percent: int, isCharging: bool) -> None:
        ...

    TAG: str
    scheduler: Any
    closed: bool
    monitor: BatteryChecker.Monitor
    debugBattery: bool
    BATTERY_WARN_THRESHOLD: int
    batteryLevelChecker: Any


class ClassUtil:
    __java__ = "com.qualcomm.robotcore.util.ClassUtil"
    class MappedByteBufferInfo:
        __java__ = "com.qualcomm.robotcore.util.ClassUtil.MappedByteBufferInfo"
        blockField: Any
        addressField: Any

    @staticmethod
    def getDeclaredConstructors(clazz: type[object]) -> list[Any]:
        ...

    @staticmethod
    def inheritsFrom(subclass: type[object], superClass: type[object]) -> bool:
        """Answers whether one class is or inherits from another"""
        ...

    @staticmethod
    def getDeclaredMethod(clazz: type[object], methodName: str, *types: type[object]) -> Any:
        """Finds a hidden (using @hide) or non-public method in the indicated class or one of its superclasses."""
        ...

    @staticmethod
    def getAllDeclaredMethods(clazz: type[object]) -> list[Any]:
        ...

    @staticmethod
    def getLocalDeclaredMethods(clazz: type[object]) -> list[Any]:
        ...

    @staticmethod
    def getDeclaredField(clazz: type[object], fieldName: str) -> Any:
        """Finds a hidden (using @hide) or non-public field in the indicated class or one of its superclasses."""
        ...

    @staticmethod
    def getAllDeclaredFields(clazz: type[object]) -> list[Any]:
        ...

    @staticmethod
    def getLocalDeclaredFields(clazz: type[object]) -> list[Any]:
        ...

    @staticmethod
    def invoke(receiver: object, method: Any, *args: object) -> object:
        ...

    @staticmethod
    def searchInheritance(clazz: type[object], predicate: Predicate[type[object]]) -> bool:
        """Searches the inheritance tree for the first class for which the predicate returns true"""
        ...

    @staticmethod
    def getStringResId(resName: str, c: type[object]) -> int:
        ...

    @staticmethod
    def decodeStringRes(string: str) -> str:
        """If string starts with \"@string/\", the remainder is a string resource we are to look up and return. Otherwise, we are just to return the string."""
        ...

    @staticmethod
    def findClass(className: str) -> type[object]:
        ...

    @staticmethod
    def memoryAddressFrom(buffer: Any) -> int:
        ...

    TAG: str


class GlobalWarningSource:
    """Instances of this interface can be registered with RobotLog as dynamic generators of robot warning messages."""
    __java__ = "com.qualcomm.robotcore.util.GlobalWarningSource"
    def getGlobalWarning(self) -> str:
        """Returns the current warning associated with this warning source. If the source currently has no warning to contribute, it should return null or an empty string."""
        ...

    def shouldTriggerWarningSound(self) -> bool:
        """Returns true if the current warning (if any) is severe enough to warrant playing a warning sound. If the source has no critical warning, this should return false. If getGlobalWarning() returns null or a blank string, the value returned here will be ignored."""
        ...

    def suppressGlobalWarning(self, suppress: bool) -> None:
        """Suppress or de-suppress the contributions of warnings by this source. If warnings are suppressed, #getGlobalWarning() will always return an empty string. Internally, a suppression count is maintained which is incremented if 'suppress' is true and decremented if it is false. The initial value of the count is zero; suppression is in effect if the count is greater than zero."""
        ...

    def setGlobalWarning(self, warning: str) -> None:
        """Sets the current warning associated with this warning source, if permitted to do so by the source. Sources may refuse for various reasons: perhaps they only ever produce their warnings from internal state, or perhaps they don't accept another warning if a first has already been set."""
        ...

    def clearGlobalWarning(self) -> None:
        """Clears any currently set warning (if permitted) for this source, and zeros the sources suppression count."""
        ...


class PeerStatusCallback:
    __java__ = "org.firstinspires.ftc.robotcore.internal.network.PeerStatusCallback"
    def onPeerConnected(self) -> None:
        """Notifies that a peer is newly connected (including if the peer just changed or the robot was restarted)."""
        ...

    def onPeerDisconnected(self) -> None:
        """Notifies that the peer is newly disconnected."""
        ...


class ClockWarningSource(GlobalWarningSource, PeerStatusCallback):
    """This class is only used on the Robot Controller"""
    __java__ = "com.qualcomm.robotcore.util.ClockWarningSource"
    @staticmethod
    def getInstance() -> ClockWarningSource:
        ...

    def onPossibleRcClockUpdate(self) -> None:
        ...

    def onDsHeartbeatReceived(self, dsHeartbeat: Heartbeat) -> None:
        ...

    def getGlobalWarning(self) -> str:
        ...

    def shouldTriggerWarningSound(self) -> bool:
        ...

    def onSharedPreferenceChanged(self, prefs: Any, key: str) -> None:
        ...

    def onPeerDisconnected(self) -> None:
        ...

    def suppressGlobalWarning(self, suppress: bool) -> None:
        ...

    def setGlobalWarning(self, warning: str) -> None:
        ...

    def clearGlobalWarning(self) -> None:
        ...

    def onPeerConnected(self) -> None:
        ...


class Device:
    """A few constants that help us detect which device we are running on"""
    __java__ = "com.qualcomm.robotcore.util.Device"
    class LinuxKernelVersion:
        __java__ = "com.qualcomm.robotcore.util.Device.LinuxKernelVersion"
        def toString(self) -> str:
            ...

        major: int
        minor: int
        patch: int
        TAG: str

    @staticmethod
    def getLinuxKernelVersion() -> Device.LinuxKernelVersion:
        ...

    @staticmethod
    def isMotorola() -> bool:
        ...

    @staticmethod
    def isRevDriverHub() -> bool:
        ...

    @staticmethod
    def deviceHasBackButton() -> bool:
        ...

    @staticmethod
    def phoneImplementsAggressiveWifiScanning() -> bool:
        ...

    @staticmethod
    def wifiP2pRemoteChannelChangeWorks() -> bool:
        """Is it possible to remote channel change from a driver station to this device?"""
        ...

    @staticmethod
    def isRevControlHub() -> bool:
        """Answers whether this is any sort of REV Control Hub"""
        ...

    @staticmethod
    def getSerialNumber() -> str:
        """Get the Android device's serial number, as defined by Build.SERIAL Uses a fallback method if that API fails"""
        ...

    @staticmethod
    def getSerialNumberOrUnknown() -> str:
        """Get the Android device's serial number, as defined by Build.SERIAL Returns \"unknown\" if the serial number cannot be determined."""
        ...

    TAG: str
    MANUFACTURER_REV: str
    MANUFACTURER_MOTOROLA: str
    MODEL_E5_PLAY: str
    MODEL_E5_XT1920DL: str
    MODEL_E4: str


class DifferentialControlLoopCoefficients:
    """Contains p, i, and d coefficients for control loops"""
    __java__ = "com.qualcomm.robotcore.util.DifferentialControlLoopCoefficients"
    @overload
    def __init__(self) -> None:
        """Constructor with coefficients set to 0.0"""
        ...
    @overload
    def __init__(self, p: float, i: float, d: float) -> None:
        """Constructor with coefficients supplied"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    p: float
    """p coefficient"""
    i: float
    """i coefficient"""
    d: float
    """d coefficient"""


class Dimmer:
    """A class that will dim the screen after a set amount of time."""
    __java__ = "com.qualcomm.robotcore.util.Dimmer"
    @overload
    def __init__(self, activity: Any) -> None:
        ...
    @overload
    def __init__(self, waitTime: int, activity: Any) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def handleDimTimer(self) -> None:
        ...

    def longBright(self) -> None:
        """Cancels all existing handler calls that are not already running, and sets up a new handler that will post in x milliseconds. I.e., leaves the screen bright for one full minute."""
        ...

    DEFAULT_DIM_TIME: int
    LONG_BRIGHT_TIME: int
    MAXIMUM_BRIGHTNESS: float
    MINIMUM_BRIGHTNESS: float
    handler: Any
    activity: Any
    layoutParams: Any
    waitTime: int
    userBrightness: float


class ElapsedTime:
    """The ElapsedTime class provides a simple handy timer to measure elapsed time intervals. The timer does not provide events or callbacks, as some other timers do. Rather, at an application- determined juncture, one can #reset() the timer. Thereafter, one can query the interval of wall-clock time that has subsequently elapsed by calling the #time(), #seconds(), or #milliseconds() methods. The timer has nanosecond internal accuracy. The precision reported by the #time() method is either seconds or milliseconds, depending on how the timer is initially constructed. This class is thread-safe."""
    __java__ = "com.qualcomm.robotcore.util.ElapsedTime"
    class Resolution(enum.Enum):
        """An indicator of the resolution of a timer."""
        __java__ = "com.qualcomm.robotcore.util.ElapsedTime.Resolution"
        SECONDS = enum.auto()
        MILLISECONDS = enum.auto()

    @overload
    def __init__(self) -> None:
        """Creates a timer with resolution com.qualcomm.robotcore.util.ElapsedTime.Resolution#SECONDS that is initialized with the now-current time."""
        ...
    @overload
    def __init__(self, startTime: int) -> None:
        """Creates a timer with resolution com.qualcomm.robotcore.util.ElapsedTime.Resolution#SECONDS. The timer is initialized with the provided start time. Zero is often a useful value to provide here: in common usage such timers will often be processed by application logic virtually immediately."""
        ...
    @overload
    def __init__(self, resolution: ElapsedTime.Resolution) -> None:
        """Creates a timer with a resolution of seconds or milliseconds. The resolution affects the units in which the #time() method reports. The timer is initialized with the current time."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def nsNow(self) -> int:
        ...

    def now(self, unit: Any) -> int:
        """Returns the current time on the clock used by the timer"""
        ...

    def reset(self) -> None:
        """Resets the internal state of the timer to reflect the current time. Instantaneously following this reset, #time() will report as zero."""
        ...

    def startTime(self) -> float:
        """Returns, in resolution-dependent units, the time at which this timer was last reset."""
        ...

    def startTimeNanoseconds(self) -> int:
        """Returns the time at which the timer was last reset, in units of nanoseconds"""
        ...

    @overload
    def time(self) -> float:
        """Returns the duration that has elapsed since the last reset of this timer. Units used are either seconds or milliseconds, depending on the resolution with which the timer was instantiated."""
        ...
    @overload
    def time(self, unit: Any) -> int:
        """Returns the duration that has elapsed since the last reset of this timer as an integer in the units requested."""
        ...
    def time(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def seconds(self) -> float:
        """Returns the duration that has elapsed since the last reset of this timer in seconds"""
        ...

    def milliseconds(self) -> float:
        """Returns the duration that has elapsed since the last reset of this timer in milliseconds"""
        ...

    def nanoseconds(self) -> int:
        """Returns the duration that has elapsed since the last reset of this timer in nanoseconds"""
        ...

    def getResolution(self) -> ElapsedTime.Resolution:
        """Returns the resolution with which the timer was instantiated."""
        ...

    def log(self, label: str) -> None:
        """Log a message stating how long the timer has been running"""
        ...

    def toString(self) -> str:
        """Returns a string indicating the current elapsed time of the timer."""
        ...

    SECOND_IN_NANO: int
    """the number of nanoseconds in a second"""
    MILLIS_IN_NANO: int
    """the number of nanoseconds in a millisecond"""
    nsStartTime: int
    resolution: float


class ImmersiveMode:
    """ImmersiveMode set up and maintain immersive mode for an Android app."""
    __java__ = "com.qualcomm.robotcore.util.ImmersiveMode"
    def __init__(self, decorView: Any) -> None:
        ...

    def hideSystemUI(self) -> None:
        ...

    decorView: Any


class IncludedFirmwareFileInfo:
    __java__ = "com.qualcomm.robotcore.util.IncludedFirmwareFileInfo"
    HUMAN_READABLE_FW_VERSION: str
    FW_IMAGE: RobotCoreCommandList.FWImage


class Intents:
    __java__ = "com.qualcomm.robotcore.util.Intents"
    INTENT_PREFIX: str
    """FTC related application specific intents."""
    ACTION_FTC_AP_NAME_CHANGE: str
    ACTION_FTC_AP_PASSWORD_CHANGE: str
    ACTION_FTC_AP_CHANNEL_CHANGE: str
    ACTION_FTC_AP_SETTINGS_CHANGE: str
    ACTION_FTC_WIFI_FACTORY_RESET: str
    ACTION_FTC_AP_GET_CURRENT_CHANNEL_INFO: str
    ACTION_FTC_AP_NOTIFY_BAND_CHANGE: str
    ACTION_FTC_NOTIFY_RC_ALIVE: str
    EXTRA_AP_PREF: str
    EXTRA_RC_ALIVE_NOTIFICATION_TIMEOUT_SECONDS: str
    EXTRA_AP_NAME: str
    """Extras that can be sent with the FTC_AP_SETTINGS_CHANGE action"""
    EXTRA_AP_PASSWORD: str
    EXTRA_AP_CHANNEL: str
    EXTRA_AP_BAND: str
    EXTRA_RESULT_RECEIVER: str
    """Extra to provide when we need to receive data back in response to a broadcast via a ResultReceiver"""
    BUNDLE_KEY_CURRENT_BAND: str
    """Key strings for Bundle data sent in response to Intents#ACTION_FTC_AP_GET_CURRENT_CHANNEL_INFO"""
    BUNDLE_KEY_CURRENT_CHANNEL: str
    ANDROID_ACTION_WIFI_AP_STATE_CHANGED: str
    """Android system intents."""


class LastKnown(Generic[T]):
    """Instances of LastKnown can keep track of a last known value for a certain datum, together with whether in fact any such last value is known at all. Values can become unknown either due to explicit invalidation, or by not being fresh enough. The requirement that values be 'fresh' helps guard against an error situation in which the underlying setting has actually been lost and the user's code is simply trying to apply it. Were we to not have this, such error situations might never be repaired. This class is NOT thread-safe."""
    __java__ = "com.qualcomm.robotcore.util.LastKnown"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, msFreshness: float) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def createArray(length: int) -> list[LastKnown[X]]:
        ...

    @staticmethod
    def invalidateArray(array: list[LastKnown[X]]) -> None:
        ...

    def invalidate(self) -> None:
        """Marks the last known value as invalid. However, the value internally stored is uneffected."""
        ...

    def isValid(self) -> bool:
        """Returns whether a last value is currently known and is fresh enough. Note that a value which is valid may spontaneously become invalid (because it expires) but a value which is invalid will never spontaneously become valid."""
        ...

    def getValue(self) -> T:
        """Returns the last known value, or null if not valid"""
        ...

    def getNonTimedValue(self) -> T:
        """Returns the stored value, w/o using a timer to invalidate"""
        ...

    def getRawValue(self) -> T:
        """Returns the stored value, whether or not it is valid"""
        ...

    def setValue(self, value: T) -> T:
        """If non-null, sets the current value to be the indicated (known) value and resets the freshness timer. If null, this is equivalent to #invalidate()."""
        ...

    def isValue(self, valueQ: T) -> bool:
        """Answers whether the last known value is both valid and equal to the value indicated. Note that the .equals() method is used to make the comparison."""
        ...

    def updateValue(self, valueQ: T) -> bool:
        """If the last known value is not both valid and equal to the indicated value, updates it to be same and returns true; otherwise, returns false."""
        ...

    value: T
    isValid_: bool
    timer: ElapsedTime
    msFreshness: float


class MovingStatistics:
    """MovingStatistics keeps statistics on the most recent samples in a data set, automatically removing old samples as the size of the data exceeds a fixed capacity. This class is *not* thread-safe."""
    __java__ = "com.qualcomm.robotcore.util.MovingStatistics"
    def __init__(self, capacity: int) -> None:
        ...

    def getCount(self) -> int:
        """Returns the current number of samples"""
        ...

    def getMean(self) -> float:
        """Returns the mean of the current set of samples"""
        ...

    def getVariance(self) -> float:
        """Returns the sample variance of the current set of samples"""
        ...

    def getStandardDeviation(self) -> float:
        """Returns the sample standard deviation of the current set of samples"""
        ...

    def clear(self) -> None:
        """Resets the statistics to an empty state"""
        ...

    def add(self, x: float) -> None:
        """Adds a new sample to the statistics, possibly also removing the oldest."""
        ...

    statistics: Statistics
    capacity: int
    samples: list[float]


class Network:
    """Utility class for performing network operations"""
    __java__ = "com.qualcomm.robotcore.util.Network"
    @staticmethod
    def getLoopbackAddress() -> Any:
        """Get the Loopback Address"""
        ...

    @staticmethod
    def getLocalIpAddresses() -> list[Any]:
        """Get local IP addresses"""
        ...

    @staticmethod
    def getLocalIpAddress(networkInterface: str) -> list[Any]:
        """Get local IP addresses of a given interface"""
        ...

    @staticmethod
    def removeIPv6Addresses(addresses: list[Any]) -> list[Any]:
        """Remove all IPv6 addresses from a collection"""
        ...

    @staticmethod
    def removeIPv4Addresses(addresses: list[Any]) -> list[Any]:
        """Remove all IPv4 addresses from a collection"""
        ...

    @staticmethod
    def removeLoopbackAddresses(addresses: list[Any]) -> list[Any]:
        """Remove all loopback addresses from a collection"""
        ...

    @staticmethod
    def getHostAddresses(addresses: list[Any]) -> list[str]:
        """Get the host address of each InetAddress in a collection"""
        ...


class NextLock:
    """A NextLock is a concurrency manager that allows one to await the next occurrence of an event in a (possibly infinite) sequence that follows after the juncture at which one chooses to pay attention."""
    __java__ = "com.qualcomm.robotcore.util.NextLock"
    class Waiter:
        """Waiter instances are returned from #getNextWaiter(), and can be used to await the next #advanceNext() call in lock from which they were retrieved."""
        __java__ = "com.qualcomm.robotcore.util.NextLock.Waiter"
        def __init__(self, nextCount: int) -> None:
            ...

        def awaitNext(self) -> None:
            """Awaits the next #advanceNext() call in the associated NextLock."""
            ...

        nextCount: int

    def __init__(self) -> None:
        ...

    def getNextWaiter(self) -> NextLock.Waiter:
        """Returns a Waiter that will await the next #advanceNext()."""
        ...

    def advanceNext(self) -> None:
        """Advances to the next event in the sequence."""
        ...

    lock: object
    count: int


class Range:
    """Utility class for performing range operations"""
    __java__ = "com.qualcomm.robotcore.util.Range"
    @staticmethod
    def scale(n: float, x1: float, x2: float, y1: float, y2: float) -> float:
        """Scale a number in the range of x1 to x2, to the range of y1 to y2"""
        ...

    @overload
    @staticmethod
    def clip(number: float, min: float, max: float) -> float:
        """clip 'number' if 'number' is less than 'min' or greater than 'max'"""
        ...
    @overload
    @staticmethod
    def clip(number: float, min: float, max: float) -> float:
        """clip 'number' if 'number' is less than 'min' or greater than 'max'"""
        ...
    @overload
    @staticmethod
    def clip(number: int, min: int, max: int) -> int:
        """clip 'number' if 'number' is less than 'min' or greater than 'max'"""
        ...
    @overload
    @staticmethod
    def clip(number: int, min: int, max: int) -> int:
        """clip 'number' if 'number' is less than 'min' or greater than 'max'"""
        ...
    @overload
    @staticmethod
    def clip(number: int, min: int, max: int) -> int:
        """clip 'number' if 'number' is less than 'min' or greater than 'max'"""
        ...
    @staticmethod
    def clip(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def throwIfRangeIsInvalid(number: float, min: float, max: float) -> None:
        """Throw an IllegalArgumentException if 'number' is less than 'min' or greater than 'max'"""
        ...
    @overload
    @staticmethod
    def throwIfRangeIsInvalid(number: int, min: int, max: int) -> None:
        """Throw an IllegalArgumentException if 'number' is less than 'min' or greater than 'max'"""
        ...
    @staticmethod
    def throwIfRangeIsInvalid(*args: Any, **kwargs: Any) -> Any:
        ...


class ReadWriteFile:
    __java__ = "com.qualcomm.robotcore.util.ReadWriteFile"
    @staticmethod
    def readFileOrThrow(file: Any) -> str:
        ...

    @staticmethod
    def readFile(file: Any) -> str:
        ...

    @staticmethod
    def readBytes(fwImage: RobotCoreCommandList.FWImage) -> list[int]:
        ...

    @staticmethod
    def readAssetBytes(assetFile: Any) -> list[int]:
        ...

    @staticmethod
    def readFileBytes(file: Any) -> list[int]:
        ...

    @staticmethod
    def readAssetBytesOrThrow(assetFile: Any) -> list[int]:
        ...

    @staticmethod
    def readRawResourceBytesOrThrow(id: int) -> list[int]:
        ...

    @staticmethod
    def readFileBytesOrThrow(file: Any) -> list[int]:
        ...

    @staticmethod
    def readBytesOrThrow(cbSizeHint: int, inputStream: Any) -> list[int]:
        ...

    @overload
    @staticmethod
    def writeFile(file: Any, fileContents: str) -> None:
        ...
    @overload
    @staticmethod
    def writeFile(directory: Any, fileName: str, fileContents: str) -> None:
        ...
    @staticmethod
    def writeFile(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def writeFileOrThrow(file: Any, fileContents: str) -> None:
        ...
    @overload
    @staticmethod
    def writeFileOrThrow(directory: Any, fileName: str, fileContents: str) -> None:
        ...
    @staticmethod
    def writeFileOrThrow(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def ensureAllChangesAreCommitted(folder: Any) -> None:
        ...

    @staticmethod
    def ensureChangesAreCommitted(file: Any) -> None:
        ...

    @staticmethod
    def updateFileRequiringCommit(file: Any, newContents: str) -> None:
        ...

    TAG: str
    charset: Any


class RobotLog:
    """Allows consistent logging across all RobotCore packages"""
    __java__ = "com.qualcomm.robotcore.util.RobotLog"
    class GlobalWarningMessage:
        __java__ = "com.qualcomm.robotcore.util.RobotLog.GlobalWarningMessage"
        def __init__(self, message: str, deservesWarningSound: bool) -> None:
            ...

        message: str
        deservesWarningSound: bool

    class LoggingThread:
        __java__ = "com.qualcomm.robotcore.util.RobotLog.LoggingThread"
        def __init__(self, name: str) -> None:
            ...

        def run(self, commandLine: str) -> None:
            ...

        def kill(self) -> None:
            ...

    @staticmethod
    def processTimeSynch(t0: int, t1: int, t2: int, t3: int) -> None:
        """Processes the reception of a set of NTP timestamps between this device (t0 and t3) and a remote device (t1 and t2) with whom it is trying to synchronize time. Our current implementation is very, very crude: we just calculate the instantaneous offset, and remember. But that's probably good enough for trying to coordinate timestamps in logs."""
        ...

    @staticmethod
    def setMsTimeOffset(offset: float) -> None:
        ...

    @overload
    @staticmethod
    def getRemoteTime() -> int:
        ...
    @overload
    @staticmethod
    def getRemoteTime(localTime: int) -> int:
        ...
    @staticmethod
    def getRemoteTime(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def getLocalTime(remoteTime: int) -> int:
        ...

    @overload
    @staticmethod
    def a(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def a(message: str) -> None:
        ...
    @staticmethod
    def a(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def aa(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def aa(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def aa(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def aa(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def aa(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def v(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def v(message: str) -> None:
        ...
    @staticmethod
    def v(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def vv(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def vv(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def vv(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def vv(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def vv(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def d(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def d(message: str) -> None:
        ...
    @staticmethod
    def d(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def dd(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def dd(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def dd(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def dd(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def dd(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def i(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def i(message: str) -> None:
        ...
    @staticmethod
    def i(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def ii(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ii(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def ii(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ii(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def ii(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def w(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def w(message: str) -> None:
        ...
    @staticmethod
    def w(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def ww(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ww(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def ww(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ww(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def ww(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def e(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def e(message: str) -> None:
        ...
    @staticmethod
    def e(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def ee(tag: str, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ee(tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def ee(tag: str, throwable: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def ee(tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def ee(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def internalLog(priority: int, tag: str, message: str) -> None:
        ...
    @overload
    @staticmethod
    def internalLog(priority: int, tag: str, throwable: Any, message: str) -> None:
        ...
    @staticmethod
    def internalLog(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def logExceptionHeader(e: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def logExceptionHeader(tag: str, e: Any, format: str, *args: object) -> None:
        ...
    @staticmethod
    def logExceptionHeader(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def logStacktrace(e: Any) -> None:
        ...

    @overload
    @staticmethod
    def logStackTrace(e: Any) -> None:
        ...
    @overload
    @staticmethod
    def logStackTrace(thread: Any, format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def logStackTrace(thread: Any, stackTrace: list[Any]) -> None:
        ...
    @overload
    @staticmethod
    def logStackTrace(tag: str, e: Any) -> None:
        ...
    @staticmethod
    def logStackTrace(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def logAndThrow(errMsg: str) -> None:
        ...

    @overload
    @staticmethod
    def setGlobalErrorMsg(message: str) -> bool:
        """NOT FOR USE BY TEAM SOFTWARE OR THIRD PARTY LIBRARIES PRIVATE INTERNAL SDK USAGE ONLY. If used in an OpMode or third party library and called when an OpMode is running, setGlobalErrorMsg will be ignored. Set a global error message This message stays set until clearGlobalErrorMsg is called. Additional calls to set the global error message will be silently ignored until the current error message is cleared. This is so that if multiple global error messages are raised, the first error message is captured. Presently, the global error is cleared only when the robot is restarted."""
        ...
    @overload
    @staticmethod
    def setGlobalErrorMsg(format: str, *args: object) -> None:
        ...
    @overload
    @staticmethod
    def setGlobalErrorMsg(e: RobotCoreException, message: str) -> None:
        ...
    @overload
    @staticmethod
    def setGlobalErrorMsg(e: Any, message: str) -> None:
        ...
    @staticmethod
    def setGlobalErrorMsg(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def addGlobalWarningMessage(msg: str) -> None:
        """Adds a global warning message. This stays set until clearGlobalWarningMsg is called."""
        ...
    @overload
    @staticmethod
    def addGlobalWarningMessage(format: str, *args: object) -> None:
        ...
    @staticmethod
    def addGlobalWarningMessage(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def registerGlobalWarningSource(globalWarningSource: GlobalWarningSource) -> None:
        """Adds (if not already present) a new source that can contribute the generation of warnings on the robot controller and driver station displays (if the source is already registered, the call has no effect). The source will periodically be polled for its contribution to the overall warning message; if the source has no warning to contribute, it should return an empty string. Note that weak references are used in this registration: the act of adding a global warning source will not of its own accord keep that source from being reclaimed by the system garbage collector."""
        ...

    @staticmethod
    def unregisterGlobalWarningSource(globalWarningSource: GlobalWarningSource) -> None:
        """Removes (if present) a source from the list of warning sources contributing to the overall system warning message (if the indicated source is not currently registered, this call has no effect). Note that explicit unregistration of a warning source is not required: due to the internal use of weak references, warning sources will be automatically unregistered if they are reclaimed by the garbage collector. However, explicit unregistration may be useful to the source itself so that it will stop being polled for its warning contribution."""
        ...

    @overload
    @staticmethod
    def setGlobalErrorMsgAndThrow(e: RobotCoreException, message: str) -> None:
        ...
    @overload
    @staticmethod
    def setGlobalErrorMsgAndThrow(e: Any, message: str) -> None:
        ...
    @staticmethod
    def setGlobalErrorMsgAndThrow(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def getGlobalErrorMsg() -> str:
        """Get the current global error message"""
        ...

    @staticmethod
    def setGlobalErrorMsgSticky(sticky: bool) -> None:
        """Causes all calls to clearGlobalErrorMsg() to be ignored. Use with caution."""
        ...

    @staticmethod
    def getGlobalWarningMessage() -> RobotLog.GlobalWarningMessage:
        """Returns the current global warning, or \"\" if there is none"""
        ...

    @staticmethod
    def setGlobalWarningMsgSticky(sticky: bool) -> None:
        """Causes all calls to clearGlobalWarningMsg() to be ignored. Use with caution."""
        ...

    @staticmethod
    def combineGlobalWarnings(warnings: list[str]) -> str:
        """Combines possibly multiple warnings together using an appropriate delimiter. If there is no actual warning in effect, then \"\" is returned."""
        ...

    @staticmethod
    def hasGlobalErrorMsg() -> bool:
        """Returns true if a global error message is set"""
        ...

    @staticmethod
    def hasGlobalWarningMsg() -> bool:
        """Returns whether a global warning currently exists"""
        ...

    @staticmethod
    def clearGlobalErrorMsg() -> None:
        """Clears the current global error message."""
        ...

    @staticmethod
    def clearGlobalWarningMsg() -> None:
        """Clears the current global warning message."""
        ...

    @staticmethod
    def onApplicationStart() -> None:
        """Write logcat logs to disk. Log data will continue to be written to disk until #cancelWriteLogcatToDisk() is called. #onApplicationStart() is idempotent: additional calls to this method will be a NOOP."""
        ...

    @staticmethod
    def writeLogcatToDisk(context: Any, kbFileSize: int) -> None:
        ...

    @staticmethod
    def startMatchLogging(context: Any, opModeName: str, matchNum: int) -> None:
        ...

    @staticmethod
    def stopMatchLogging() -> None:
        ...

    @overload
    @staticmethod
    def getLogFilename() -> str:
        ...
    @overload
    @staticmethod
    def getLogFilename(context: Any) -> str:
        ...
    @staticmethod
    def getLogFilename(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def pruneMatchLogsIfNecessary() -> None:
        ...

    @staticmethod
    def getMatchLogFilename(context: Any, opModeName: str, matchNum: int) -> str:
        ...

    @staticmethod
    def getExtantLogFiles(context: Any) -> list[Any]:
        ...

    @staticmethod
    def cancelWriteLogcatToDisk() -> None:
        """Cancels any logcat writing to disk that might currently be going on"""
        ...

    @staticmethod
    def logAppInfo() -> None:
        ...

    @staticmethod
    def logDeviceInfo() -> None:
        ...

    @overload
    @staticmethod
    def logBytes(tag: str, caption: str, data: list[int], cb: int) -> None:
        ...
    @overload
    @staticmethod
    def logBytes(tag: str, caption: str, data: list[int], ibStart: int, cb: int) -> None:
        ...
    @staticmethod
    def logBytes(*args: Any, **kwargs: Any) -> Any:
        ...

    OPMODE_START_TAG: str
    OPMODE_STOP_TAG: str
    TAG: str


class RollingAverage:
    """Calculate a rolling average from a stream of numbers. Only the last 'size' elements will be considered."""
    __java__ = "com.qualcomm.robotcore.util.RollingAverage"
    @overload
    def __init__(self) -> None:
        """Constructor, with default size"""
        ...
    @overload
    def __init__(self, size: int) -> None:
        """Constructor, with given size"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def size(self) -> int:
        """Get the size"""
        ...

    def resize(self, size: int) -> None:
        """Resize the rolling average"""
        ...

    def addNumber(self, number: int) -> None:
        """Add a number to the rolling average"""
        ...

    def getAverage(self) -> int:
        """Get the rolling average"""
        ...

    def reset(self) -> None:
        """Reset the rolling average"""
        ...

    DEFAULT_SIZE: int


class RunShellCommand:
    """Run shell commands"""
    __java__ = "com.qualcomm.robotcore.util.RunShellCommand"
    class ProcessResult:
        """The text output and return code of a completed process"""
        __java__ = "com.qualcomm.robotcore.util.RunShellCommand.ProcessResult"
        def getReturnCode(self) -> int:
            ...

        def getOutput(self) -> str:
            ...

        def equals(self, o: object) -> bool:
            ...

        def hashCode(self) -> int:
            ...

    def __init__(self) -> None:
        """Constructor"""
        ...

    def enableLogging(self, enable: bool) -> None:
        """If logging is enabled, all command will be logged"""
        ...

    def run(self, cmd: str) -> RunShellCommand.ProcessResult:
        """Run the given command"""
        ...

    def runAsRoot(self, cmd: str) -> RunShellCommand.ProcessResult:
        """Run the given command, as root"""
        ...

    def commitSeppuku(self) -> None:
        ...

    @staticmethod
    def killSpawnedProcess(processName: str, packageName: str) -> None:
        """Kill any spawn processes matching a given process name"""
        ...

    @staticmethod
    def getSpawnedProcessPid(processName: str, packageName: str) -> int:
        """return the PID of a given process name started a given package name"""
        ...


class SerialNumber:
    """Instances of SerialNumber represent serial number indentifiers of hardware devices. For USB-attached devices, these are usually the low-level USB serial number (see UsbDevice#getSerialNumber(), but that is not required. Rather, the notion of SerialNumber is a general purpose one representing a user-visible digital identity for a particular device instance. 'Fake' serial numbers are serial numbers that will *never* appear for a real device; they are useful, for example, as the serial number of a ControllerConfiguration that has not yet been associated with a actual controller device. Fake serial numbers are never shown to users. Note that *all* serial numbers loaded in memory at any given instant are guaranteed unique and different, even the fake ones; this allows code that processes USB-device-bound ControllerConfigurations to operate easily on unbound ones as well, a significant coding simplification. The technology used in fake serial numbers, UUIDs, in fact guarantees uniqueness across space and time, so fake serial numbers can be recorded persistently and still maintain uniqueness. Historically, non-unique 'fake' serial numbers were also used: these appeared int the form of \"-1\" or \"N/A\". When loaded from persistent storage, such legacy fake serial numbers are converted to unique ones to maintain the uniqueness guarantee."""
    __java__ = "com.qualcomm.robotcore.util.SerialNumber"
    class GsonTypeAdapter:
        __java__ = "com.qualcomm.robotcore.util.SerialNumber.GsonTypeAdapter"
        def write(self, writer: Any, serialNumber: SerialNumber) -> None:
            ...

        def read(self, reader: Any) -> SerialNumber:
            ...

    def __init__(self, serialNumberString: str) -> None:
        """Constructs a serial number using the supplied initialization string. If the initialization string is a legacy form of fake serial number, a unique fake serial number is created."""
        ...

    @staticmethod
    def createFake() -> SerialNumber:
        ...

    @staticmethod
    def createEmbedded() -> SerialNumber:
        ...

    @staticmethod
    def fromString(serialNumberString: str) -> SerialNumber:
        ...

    @staticmethod
    def fromStringOrNull(serialNumberString: str) -> SerialNumber:
        ...

    @staticmethod
    def fromUsbOrNull(serialNumberString: str) -> SerialNumber:
        ...

    @staticmethod
    def fromVidPid(vid: int, pid: int, connectionPath: str) -> SerialNumber:
        """Makes up a serial-number-like-thing for USB devices that internally lack a serial number."""
        ...

    def isVendorProduct(self) -> bool:
        ...

    def isFake(self) -> bool:
        """Returns whether the indicated serial number is one of the legacy fake serial number forms or not."""
        ...

    def isUsb(self) -> bool:
        """Returns whether the serial number is one of an actual USB device."""
        ...

    def isEmbedded(self) -> bool:
        """Returns whether the serial number is the one used for the embedded Expansion Hub inside a Rev Control Hub."""
        ...

    def getString(self) -> str:
        """Returns the string contents of the serial number. Result is not intended to be displayed to humans."""
        ...

    def getScannableDeviceSerialNumber(self) -> SerialNumber:
        """Returns the SerialNumber of the device associated with this one that would appear in a ScannedDevices."""
        ...

    def matches(self, pattern: object) -> bool:
        ...

    @overload
    def equals(self, object: object) -> bool:
        ...
    @overload
    def equals(self, string: str) -> bool:
        ...
    def equals(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def hashCode(self) -> int:
        ...

    @staticmethod
    def noteSerialNumberType(serialNumber: SerialNumber, typeName: str) -> None:
        ...

    @staticmethod
    def getDeviceDisplayName(serialNumber: SerialNumber) -> str:
        ...

    fakePrefix: str
    vendorProductPrefix: str
    lynxModulePrefix: str
    embedded: str
    ethernetOverUsbPrefix: str
    serialNumberString: str
    deviceDisplayNames: dict[str, str]


class ShortHash:
    """ShortHash, based heavily off of Hashids. This is a reimplementation of http://hashids.org v1.0.0 version. This implementation is immutable, thread-safe, no lock is necessary."""
    __java__ = "com.qualcomm.robotcore.util.ShortHash"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, salt: str) -> None:
        ...
    @overload
    def __init__(self, salt: str, minHashLength: int) -> None:
        ...
    @overload
    def __init__(self, salt: str, minHashLength: int, alphabet: str) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def encode(self, number: int) -> str:
        """Encrypt numbers to string"""
        ...

    def getAlphabetLength(self) -> int:
        ...

    def getVersion(self) -> str:
        """Get Hashid algorithm version."""
        ...

    MAX_NUMBER: int
    """Max number that can be encoded with Hashids."""


class SoftwareVersionWarningSource(GlobalWarningSource, PeerStatusCallback):
    """This class is only used on the Robot Controller"""
    __java__ = "com.qualcomm.robotcore.util.SoftwareVersionWarningSource"
    class MismatchedAppsDetail:
        __java__ = "com.qualcomm.robotcore.util.SoftwareVersionWarningSource.MismatchedAppsDetail"
        oldApp: str

    @staticmethod
    def getInstance() -> SoftwareVersionWarningSource:
        ...

    def onReceivedPeerDiscoveryFromCurrentPeer(self, peerDiscoveryData: PeerDiscovery) -> None:
        ...

    def onReceivedDriverHubOsVersionCode(self, dhOsVersionCode: int) -> None:
        ...

    def getGlobalWarning(self) -> str:
        ...

    def shouldTriggerWarningSound(self) -> bool:
        ...

    def onPeerDisconnected(self) -> None:
        ...

    def onSharedPreferenceChanged(self, prefs: Any, key: str) -> None:
        ...

    def suppressGlobalWarning(self, suppress: bool) -> None:
        ...

    def setGlobalWarning(self, warning: str) -> None:
        ...

    def clearGlobalWarning(self) -> None:
        ...

    def onPeerConnected(self) -> None:
        ...


class SortOrder(enum.Enum):
    __java__ = "com.qualcomm.robotcore.util.SortOrder"
    ASCENDING = enum.auto()
    DESCENDING = enum.auto()


class Statistics:
    """This handy utility class supports the ongoing calculation of mean and variance of a series of numbers. This class is *not* thread-safe."""
    __java__ = "com.qualcomm.robotcore.util.Statistics"
    def __init__(self) -> None:
        ...

    def getCount(self) -> int:
        """Returns the current number of samples"""
        ...

    def getMean(self) -> float:
        """Returns the mean of the current set of samples"""
        ...

    def getVariance(self) -> float:
        """Returns the sample variance of the current set of samples"""
        ...

    def getStandardDeviation(self) -> float:
        """Returns the sample standard deviation of the current set of samples"""
        ...

    def clear(self) -> None:
        """Resets the statistics to an empty state"""
        ...

    def add(self, x: float) -> None:
        """Adds a new sample to the statistics"""
        ...

    def remove(self, x: float) -> None:
        """Removes a sample from the statistics"""
        ...

    n: int
    mean: float
    m2: float


class ThreadPool:
    """The ThreadPool class manages thread creation and shutdown in the SDK. We centralize things here mostly so as to provide robust logging services that will aid in postmortem analysis of system issues."""
    __java__ = "com.qualcomm.robotcore.util.ThreadPool"
    class Singleton(Generic[T]):
        """Singletons are helpers that gatekeep execution of work on a service to a single runnable at a time. Submitting a runnable will return a SingletonResult, either from a newly started item or one that was previously running. That result can be waited upon for completion. Alternately, the Singleton itself can be waited upon to await the completion of the currently running item, if any."""
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.Singleton"
        def __init__(self) -> None:
            ...

        def setService(self, service: Any) -> None:
            ...

        def reset(self) -> None:
            ...

        @overload
        def submit(self, msAwaitDefault: int, runnable: Any) -> ThreadPool.SingletonResult[T]:
            """Submits a runnable to the service of this singleton, but only if there's not some other runnable currently submitted thereto."""
            ...
        @overload
        def submit(self, runnable: Any) -> ThreadPool.SingletonResult[T]:
            ...
        @overload
        def submit(self, msAwaitDefault: int, callable: Any) -> ThreadPool.SingletonResult[T]:
            ...
        @overload
        def submit(self, callable: Any) -> ThreadPool.SingletonResult[T]:
            ...
        def submit(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def getResult(self) -> ThreadPool.SingletonResult[T]:
            """Returns the result from the extant or previous work item, if any; otherwise, null."""
            ...

        @overload
        def await_(self, ms: int) -> T:
            """Awaits the completion of the extant work item, if one exists"""
            ...
        @overload
        def await_(self) -> T:
            ...
        def await_(self, *args: Any, **kwargs: Any) -> Any:
            ...

        INFINITE_TIMEOUT: int

    class SingletonResult(Generic[T]):
        """SingletonResults are returned from Singleton as a token that can be used to await the completion of submitted work."""
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.SingletonResult"
        def __init__(self, msAwaitDefault: int, singleton: ThreadPool.Singleton[T], future: Any) -> None:
            ...

        def setFuture(self, future: Any) -> None:
            ...

        @overload
        def await_(self, ms: int) -> T:
            """Awaits the completion of the work item associated with this result."""
            ...
        @overload
        def await_(self) -> T:
            """Awaits (until deadline, forever, or until interruption) the completion of the work item associated with this result."""
            ...
        def await_(self, *args: Any, **kwargs: Any) -> Any:
            ...

    class ContainerOfThreads:
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.ContainerOfThreads"
        def setNameRootForThreads(self, nameRootForThreads: str) -> None:
            ...

        def setPriorityForThreads(self, priorityForThreads: int) -> None:
            ...

        def noteNewThread(self, thread: Any) -> None:
            ...

        def noteFinishedThread(self, thread: Any) -> None:
            ...

    class ThreadFactoryImpl:
        """ThreadFactoryImpl notifies the container that it's passed on construction of all the threads that get made."""
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.ThreadFactoryImpl"
        def __init__(self, container: ThreadPool.ContainerOfThreads) -> None:
            ...

        def newThread(self, runUserCode: Any) -> Any:
            ...

        threadFactory: Any
        container: ThreadPool.ContainerOfThreads

    class ContainerOfThreadsRecorder(ContainerOfThreads):
        """ContainerOfThreadsImpl serves as base for our executors, and records the threads used in each."""
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.ContainerOfThreadsRecorder"
        def __init__(self) -> None:
            ...

        def setNameRootForThreads(self, nameRootForThreads: str) -> None:
            ...

        def setPriorityForThreads(self, priorityForThreads: int) -> None:
            ...

        def noteNewThread(self, thread: Any) -> None:
            ...

        def noteFinishedThread(self, thread: Any) -> None:
            ...

        def logThread(self, thread: Any, action: str) -> None:
            ...

        def iterator(self) -> Any:
            ...

        threads: list[Any]
        nameRootForThreads: str
        threadCount: Any
        priorityForThreads: int

    class ThreadBorrowable:
        """Indicates a thread pool that is at times capable of using guest worker threads"""
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.ThreadBorrowable"
        def canBorrowThread(self, thread: Any) -> bool:
            """Caller guarantees that thread is a typical utility 'worker' thread (in contrast to, for example, the dedicated UI thread, or other threads on which work is dispatched through a Handler). Answer whether we are ok to dispatch here instead of one of our own worker threads. Caller must additionally assure themselves from their contextual knowledge that taking advantage of this function will not lead to deadlocks that otherwise would not occur."""
            ...

    class RecordingThreadPool(ContainerOfThreadsRecorder):
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.RecordingThreadPool"
        def __init__(self, nThreadsCore: int, nThreadsMax: int, keepAliveTime: int, unit: Any, workQueue: Any) -> None:
            ...

        def execute(self, command: Any) -> None:
            ...

        def shutdown(self) -> None:
            ...

        def shutdownNow(self) -> list[Any]:
            ...

        def isShutdown(self) -> bool:
            ...

        def isTerminated(self) -> bool:
            ...

        def awaitTermination(self, timeout: int, unit: Any) -> bool:
            ...

        @overload
        def submit(self, task: Any) -> Any:
            ...
        @overload
        def submit(self, task: Any, result: T) -> Any:
            ...
        @overload
        def submit(self, task: Any) -> Any:
            ...
        def submit(self, *args: Any, **kwargs: Any) -> Any:
            ...

        @overload
        def invokeAll(self, tasks: list[Any]) -> list[Any]:
            ...
        @overload
        def invokeAll(self, tasks: list[Any], timeout: int, unit: Any) -> list[Any]:
            ...
        def invokeAll(self, *args: Any, **kwargs: Any) -> Any:
            ...

        @overload
        def invokeAny(self, tasks: list[Any]) -> T:
            ...
        @overload
        def invokeAny(self, tasks: list[Any], timeout: int, unit: Any) -> T:
            ...
        def invokeAny(self, *args: Any, **kwargs: Any) -> Any:
            ...

        executor: Any

    class RecordingScheduledExecutor(ContainerOfThreadsRecorder):
        __java__ = "com.qualcomm.robotcore.util.ThreadPool.RecordingScheduledExecutor"
        def __init__(self, numberOfThreads: int) -> None:
            ...

        def setKeepAliveTime(self, time: int, timeUnit: Any) -> None:
            ...

        def allowCoreThreadTimeOut(self, allow: bool) -> None:
            ...

        def execute(self, command: Any) -> None:
            ...

        def shutdown(self) -> None:
            ...

        def shutdownNow(self) -> list[Any]:
            ...

        def isShutdown(self) -> bool:
            ...

        def isTerminated(self) -> bool:
            ...

        def awaitTermination(self, timeout: int, unit: Any) -> bool:
            ...

        @overload
        def submit(self, task: Any) -> Any:
            ...
        @overload
        def submit(self, task: Any, result: T) -> Any:
            ...
        @overload
        def submit(self, task: Any) -> Any:
            ...
        def submit(self, *args: Any, **kwargs: Any) -> Any:
            ...

        @overload
        def invokeAll(self, tasks: list[Any]) -> list[Any]:
            ...
        @overload
        def invokeAll(self, tasks: list[Any], timeout: int, unit: Any) -> list[Any]:
            ...
        def invokeAll(self, *args: Any, **kwargs: Any) -> Any:
            ...

        @overload
        def invokeAny(self, tasks: list[Any]) -> T:
            ...
        @overload
        def invokeAny(self, tasks: list[Any], timeout: int, unit: Any) -> T:
            ...
        def invokeAny(self, *args: Any, **kwargs: Any) -> Any:
            ...

        @overload
        def schedule(self, command: Any, delay: int, unit: Any) -> Any:
            ...
        @overload
        def schedule(self, callable: Any, delay: int, unit: Any) -> Any:
            ...
        def schedule(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def scheduleAtFixedRate(self, command: Any, initialDelay: int, period: int, unit: Any) -> Any:
            ...

        def scheduleWithFixedDelay(self, command: Any, initialDelay: int, delay: int, unit: Any) -> Any:
            ...

        executor: Any

    @staticmethod
    def getDefault() -> Any:
        ...

    @staticmethod
    def getDefaultSerial() -> Any:
        ...

    @staticmethod
    def getDefaultScheduler() -> Any:
        ...

    @staticmethod
    def newSingleThreadExecutor(nameRoot: str) -> Any:
        """Creates an Executor that uses a single worker thread operating off an unbounded queue."""
        ...

    @staticmethod
    def newFixedThreadPool(numberOfThreads: int, nameRoot: str) -> Any:
        """Creates a thread pool that reuses a fixed number of threads operating off a shared unbounded queue. At any point, at most numberOfThreads threads will be active processing tasks."""
        ...

    @staticmethod
    def newCachedThreadPool(nameRoot: str) -> Any:
        """Creates a thread pool that creates new threads as needed, but will reuse previously constructed threads when they are available."""
        ...

    @staticmethod
    def newScheduledExecutor(maxWorkerThreadCount: int, nameRoot: str) -> ThreadPool.RecordingScheduledExecutor:
        """Creates an executor that can schedule commands to run after a given delay, or to execute periodically. The pool has a minimum size of 1, but will expand as necessary to accommodate its workload."""
        ...

    @overload
    @staticmethod
    def getTID(thread: Any) -> int:
        """Returns the OS-level thread id for the given thread"""
        ...
    @overload
    @staticmethod
    def getTID(threadId: int) -> int:
        """Returns the OS-level thread id for the indicated Android-level thread id"""
        ...
    @staticmethod
    def getTID(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def awaitTermination(executorService: Any, timeout: int, unit: Any, serviceName: str) -> bool:
        """Waits for the indicated timeout for the indicated executor service to shutdown. Will return early if an interrupt occurs. If the shutdown is particularly lengthy, then at periodic intervals (on the order of seconds) messages are recorded to the log to aid in postmortem analyses."""
        ...

    @staticmethod
    def awaitTerminationOrExitApplication(executorService: Any, timeout: int, unit: Any, serviceName: str, message: str) -> None:
        """Awaits the termination of the indicated service for the indicated timeout. If the service terminates, then the function returns. If the service does not terminate within the alloted time, then a bold message is written to the log and the application is terminated."""
        ...

    @staticmethod
    def awaitFuture(future: Any, timeout: int, unit: Any) -> bool:
        ...

    @staticmethod
    def cancelFutureOrExitApplication(future: Any, timeout: int, unit: Any, serviceName: str, message: str) -> None:
        ...

    @staticmethod
    def exitApplication(serviceName: str, message: str) -> None:
        ...

    @staticmethod
    def logThreadLifeCycle(name: str, runnable: Any) -> None:
        """Robustly log thread startup and shutdown"""
        ...

    @staticmethod
    def retrieveUserException(r: Any, t: Any) -> Any:
        """See ThreadPoolExecutor#afterExecute(Runnable, Throwable), after which this logic is modelled"""
        ...

    TAG: str


class TypeConversion:
    """Utility class for performing type conversions"""
    __java__ = "com.qualcomm.robotcore.util.TypeConversion"
    @overload
    @staticmethod
    def shortToByteArray(shortInt: int) -> list[int]:
        """convert a short into a byte array; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def shortToByteArray(shortInt: int, byteOrder: Any) -> list[int]:
        """convert a short into a byte array"""
        ...
    @staticmethod
    def shortToByteArray(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def intToByteArray(integer: int) -> list[int]:
        """convert an int into a byte array; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def intToByteArray(integer: int, byteOrder: Any) -> list[int]:
        """convert an int into a byte array"""
        ...
    @staticmethod
    def intToByteArray(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def longToByteArray(longInt: int) -> list[int]:
        """convert a long into a byte array; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def longToByteArray(longInt: int, byteOrder: Any) -> list[int]:
        """convert a long into a byte array"""
        ...
    @staticmethod
    def longToByteArray(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def byteArrayToShort(byteArray: list[int]) -> int:
        """convert a byte array into a short; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def byteArrayToShort(byteArray: list[int], byteOrder: Any) -> int:
        """convert a byte array into a short"""
        ...
    @overload
    @staticmethod
    def byteArrayToShort(byteArray: list[int], ibFirst: int, byteOrder: Any) -> int:
        ...
    @staticmethod
    def byteArrayToShort(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def byteArrayToInt(byteArray: list[int]) -> int:
        """convert a byte array into an int; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def byteArrayToInt(byteArray: list[int], byteOrder: Any) -> int:
        """convert a byte array into an int"""
        ...
    @staticmethod
    def byteArrayToInt(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def byteArrayToLong(byteArray: list[int]) -> int:
        """convert a byte array into a long; big endian is assumed"""
        ...
    @overload
    @staticmethod
    def byteArrayToLong(byteArray: list[int], byteOrder: Any) -> int:
        """convert a byte array into a long"""
        ...
    @staticmethod
    def byteArrayToLong(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def unsignedByteToInt(b: int) -> int:
        """Accept a byte, treat that byte as an unsigned byte, then covert it to the return type"""
        ...

    @staticmethod
    def unsignedShortToInt(s: int) -> int:
        """Treats a short as an unsigned value and returns that value as a int"""
        ...

    @staticmethod
    def unsignedByteToDouble(b: int) -> float:
        """Accept a byte, treat that byte as an unsigned byte, then covert it to the return type"""
        ...

    @staticmethod
    def unsignedIntToLong(i: int) -> int:
        """Accept an int, treat that int as an unsigned int, then covert it to the return type"""
        ...

    @staticmethod
    def stringToUtf8(javaString: str) -> list[int]:
        """Convert a Java String into a UTF-8 byte array"""
        ...

    @staticmethod
    def doubleToFixedInt(value: float, fractionBits: int) -> int:
        ...

    @overload
    @staticmethod
    def doubleFromFixed(value: int, fractionBits: int) -> float:
        ...
    @overload
    @staticmethod
    def doubleFromFixed(value: int, fractionBits: int) -> float:
        ...
    @staticmethod
    def doubleFromFixed(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def doubleToFixedLong(value: float, fractionBits: int) -> int:
        ...

    @staticmethod
    def utf8ToString(utf8String: list[int]) -> str:
        ...

    @overload
    @staticmethod
    def toBoolean(value: bool) -> bool:
        ...
    @overload
    @staticmethod
    def toBoolean(value: bool, defaultValue: bool) -> bool:
        ...
    @staticmethod
    def toBoolean(*args: Any, **kwargs: Any) -> Any:
        ...


class Util:
    """Various utility methods"""
    __java__ = "com.qualcomm.robotcore.util.Util"
    @staticmethod
    def getRandomString(stringLength: int, charSet: str) -> str:
        """Get a random string of characters of specified length from a specified character set."""
        ...

    @staticmethod
    def sortFilesByName(files: list[Any]) -> None:
        """Sort an array of File objects, by filename"""
        ...

    @staticmethod
    def updateTextView(textView: Any, msg: str) -> None:
        ...

    @overload
    @staticmethod
    def concatenateByteArrays(first: list[int], second: list[int]) -> list[int]:
        """Creates a new byte array long enough to hold both byte arrays, then fills them."""
        ...
    @overload
    @staticmethod
    def concatenateByteArrays(first: list[int], second: list[int], third: list[int]) -> list[int]:
        ...
    @staticmethod
    def concatenateByteArrays(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def isPrefixOf(prefix: str, target: str) -> bool:
        """Is 'prefix' an initial substring of 'target'?"""
        ...

    @staticmethod
    def isGoodString(string: str) -> bool:
        ...

    @staticmethod
    def forEachInFolder(folder: Any, recursive: bool, action: Predicate[Any]) -> None:
        ...

    @staticmethod
    def teamNumberMatch(first: str, second: str) -> bool:
        ...

    ASCII_RECORD_SEPARATOR: str
    LOWERCASE_ALPHA_NUM_CHARACTERS: str


class Version:
    __java__ = "com.qualcomm.robotcore.util.Version"
    @staticmethod
    def getLibraryVersion() -> str:
        ...

    LIBRARY_VERSION: str
    """BUILD_VERSION for library"""


class WeakReferenceSet(Generic[E]):
    """WeakReferenceSet has set behaviour but contains weak references, not strong ones. WeakReferenceSet is thread-safe. It's designed primarily for relatively small sets, as the implementation employed is inefficient on large sets."""
    __java__ = "com.qualcomm.robotcore.util.WeakReferenceSet"
    def add(self, o: E) -> bool:
        ...

    def remove(self, o: object) -> bool:
        ...

    def contains(self, o: object) -> bool:
        ...

    def addAll(self, collection: list[E]) -> bool:
        ...

    def clear(self) -> None:
        ...

    def containsAll(self, collection: list[object]) -> bool:
        ...

    def isEmpty(self) -> bool:
        ...

    def size(self) -> int:
        ...

    @overload
    def toArray(self) -> list[object]:
        ...
    @overload
    def toArray(self, array: list[object]) -> list[object]:
        ...
    def toArray(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def iterator(self) -> Any:
        ...

    def removeAll(self, collection: list[object]) -> bool:
        ...

    def retainAll(self, collection: list[object]) -> bool:
        ...

    members: Any


class WebHandlerManager:
    __java__ = "com.qualcomm.robotcore.util.WebHandlerManager"
    def getWebServer(self) -> WebServer:
        ...

    def register(self, command: str, webHandler: WebHandler) -> None:
        """Register a key, value pair. Associate a String command with a WebHandler."""
        ...

    def getRegistered(self, command: str) -> WebHandler:
        """Returns if a web handler is already associated with a command."""
        ...

    def registerObserver(self, key: str, webObserver: WebObserver) -> None:
        """Registers a observer as WebObserver for client requests into the robot web server. This allows for the detection of some client requests, but this method does not allow for WebObservers to return a server response. Successive calls with the same key use the last WebObserver that was used in a call. Therefore, different instances of active WebObserver require different keys."""
        ...


class WebServer:
    __java__ = "com.qualcomm.robotcore.util.WebServer"
    def getWebHandlerManager(self) -> WebHandlerManager:
        ...

    def wasStarted(self) -> bool:
        """Check if the WebServer has been started."""
        ...

    def start(self) -> None:
        """start the WebServer."""
        ...

    def stop(self) -> None:
        """stop the WebServer."""
        ...

    def getConnectionInformation(self) -> RobotControllerWebInfo:
        """Get RobotControllerWebInfo"""
        ...

    def getWebSocketManager(self) -> WebSocketManager:
        """Get the manager for the WebSockets associated with this WebServer"""
        ...


class VendorProductSerialNumber(SerialNumber):
    """A VendorProductSerialNumber is a made-up USB serial number derived from vendor and product identifiers together with the USB connection path (concatenation of USB port numbers through possibly various USB hubs). The general rule we have for devices with this kind of serial number is that if there's only one of them attached with a given (vid,pid) pair, then we allow that to move around from USB port to USB port, but if there's more than one with the same (vid,pid) identification then we require that all of them only be used on the USB phyical ports / connection paths on which they were originally configured / detected."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.usb.VendorProductSerialNumber"
    @overload
    def __init__(self, initializer: str) -> None:
        ...
    @overload
    def __init__(self, vid: int, pid: int, connectionPath: str) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def matches(self, oPattern: object) -> bool:
        ...

    def toString(self) -> str:
        ...

    def isVendorProduct(self) -> bool:
        ...

    def getVendorId(self) -> int:
        ...

    def getProductId(self) -> int:
        ...

    def getConnectionPath(self) -> str:
        ...

    vendorId: int
    productId: int
    connectionPath: str


class Deadline(ElapsedTime):
    """Deadline enhances ElapsedTime with an explicit duration. A Deadline can also be cancelled, causing it to expire earlier than it originally would have."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.system.Deadline"
    def __init__(self, duration: int, unit: Any) -> None:
        ...

    def reset(self) -> None:
        ...

    def cancel(self) -> None:
        ...

    def expire(self) -> None:
        ...

    def getDuration(self, unit: Any) -> int:
        ...

    def getDeadline(self, unit: Any) -> int:
        ...

    def timeRemaining(self, unit: Any) -> int:
        ...

    def hasExpired(self) -> bool:
        ...

    def await_(self, latch: Any) -> bool:
        ...

    def tryLock(self, lock: Any) -> bool:
        ...

    def tryAcquire(self, semaphore: Any) -> bool:
        ...

    nsDuration: int
    nsDeadline: int
    awaitUnit: Any
    msPollInterval: int
