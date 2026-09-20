"""Types pulled in only so a stubbed signature elsewhere (e.g. DcMotor.getMotorType() -> MotorConfigurationType) resolves to a real class instead of Any. None of these have a Contract-2 package mapping of their own; users don't normally import from here directly."""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

if TYPE_CHECKING:
    from ftc.hardware import AnalogInputController, CameraName, Command, ControlSystem, DcMotor, DeviceManager, DigitalChannelController, EventLoopManager, HardwareDevice, I2cDeviceSynchSimple, LynxModule, LynxModuleImuType, LynxModuleIntf, LynxModuleMetaList, LynxUnsupportedCommandException, MotorControlAlgorithm, PIDFCoefficients, RobocolParsable, RobotUsbModule, ServoControllerEx, SwitchableCameraName, TelemetryMessage, WebcamName
    from ftc.navigation import AngleUnit, AxesOrder, AxesReference, Rotation
    from ftc.opmode import OpMode, OpModeManagerImpl
    from ftc.telemetry import Func
    from ftc.util import Deadline, SerialNumber

A = TypeVar("A")
E = TypeVar("E")
EXCEPTION = TypeVar("EXCEPTION", bound="Any")
ITEM_T = TypeVar("ITEM_T", bound="DeviceConfiguration")
NewType = TypeVar("NewType")
OldType = TypeVar("OldType")
R = TypeVar("R")
RESPONSE = TypeVar("RESPONSE", bound="LynxMessage")
S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
VALUE = TypeVar("VALUE")
class BuiltinCameraDirection(enum.Enum):
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.BuiltinCameraDirection"
    BACK = enum.auto()
    FRONT = enum.auto()


class DeviceConfiguration:
    __java__ = "com.qualcomm.robotcore.hardware.configuration.DeviceConfiguration"
    class I2cChannel:
        """A separate class to allow the compiler to help us find all the place this should be used"""
        __java__ = "com.qualcomm.robotcore.hardware.configuration.DeviceConfiguration.I2cChannel"
        def __init__(self, channel: int) -> None:
            ...

        def toString(self) -> str:
            ...

        channel: int

    @overload
    def __init__(self, port: int, type: ConfigurationType, name: str, enabled: bool) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, port: int) -> None:
        ...
    @overload
    def __init__(self, type: ConfigurationType) -> None:
        ...
    @overload
    def __init__(self, port: int, type: ConfigurationType) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def isEnabled(self) -> bool:
        ...

    def setEnabled(self, enabled: bool) -> None:
        ...

    def getName(self) -> str:
        ...

    def setName(self, newName: str) -> None:
        ...

    def setConfigurationType(self, type: ConfigurationType) -> None:
        ...

    @staticmethod
    def sortByName(configurations: list[DeviceConfiguration]) -> None:
        ...

    def getConfigurationType(self) -> ConfigurationType:
        ...

    def getSpinnerChoiceType(self) -> ConfigurationType:
        ...

    def getPort(self) -> int:
        ...

    def setPort(self, port: int) -> None:
        ...

    def getI2cChannel(self) -> DeviceConfiguration.I2cChannel:
        """This device is an I2c device. Returns information as to how to connect to same"""
        ...

    def compareTo(self, another: DeviceConfiguration) -> int:
        ...

    def serializeXmlAttributes(self, serializer: Any) -> None:
        ...

    def deserialize(self, parser: Any, xmlReader: ReadXMLFileHandler) -> None:
        """Initialize this DeviceConfiguration from XML"""
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        """This gets called while the parser is pointed at the open tag for this device configuration. Override this to deserialize additional attributes of the open tag, or to do additional initialization Do NOT advance the parser from this method."""
        ...

    def deserializeChildElement(self, configurationType: ConfigurationType, parser: Any, xmlReader: ReadXMLFileHandler) -> None:
        """This gets called while the parser is pointed at the open tag for a child device configuration. This method MUST be overridden by any subclass that needs to access XML child elements. When this method returns, the parser can be advanced only as far as the child's end tag. Do not parse multiple child elements."""
        ...

    def onDeserializationComplete(self, xmlReader: ReadXMLFileHandler) -> None:
        """This gets called when the serialization process has been completed."""
        ...

    TAG: str
    XMLATTR_NAME: str
    XMLATTR_PORT: str
    DISABLED_DEVICE_NAME: str
    name: str


class ControllerConfiguration(DeviceConfiguration, Generic[ITEM_T]):
    """ControllerConfiguration represents container of DeviceConfigurations. It may or may not be USB attached; in the latter case, the serial number will be an instance of FakeSerialNumber."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ControllerConfiguration"
    @overload
    def __init__(self, name: str, serialNumber: SerialNumber, type: ConfigurationType) -> None:
        ...
    @overload
    def __init__(self, name: str, devices: list[ITEM_T], serialNumber: SerialNumber, type: ConfigurationType) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def forType(name: str, serialNumber: SerialNumber, type: ConfigurationType) -> ControllerConfiguration:
        ...

    def getDevices(self) -> list[ITEM_T]:
        ...

    def getConfigurationType(self) -> ConfigurationType:
        ...

    def setSerialNumber(self, serialNumber: SerialNumber) -> None:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def isKnownToBeAttached(self) -> bool:
        ...

    def setKnownToBeAttached(self, knownToBeAttached: bool) -> None:
        ...

    def isSystemSynthetic(self) -> bool:
        ...

    def setSystemSynthetic(self, systemSynthetic: bool) -> None:
        ...

    def setDevices(self, devices: list[ITEM_T]) -> None:
        ...

    def toUSBDeviceType(self) -> DeviceManager.UsbDeviceType:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    XMLATTR_SERIAL_NUMBER: str


class LynxMessage:
    """LynxMessage is the root base class from which all lynx messaging related classes derive."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxMessage"
    def __init__(self, module: LynxModuleIntf) -> None:
        ...

    @staticmethod
    def invokeStaticNullaryMethod(clazz: type[object], methodName: str) -> object:
        ...

    def getDestModuleAddress(self) -> int:
        ...

    def noteHasBeenTransmitted(self) -> None:
        ...

    def hasBeenTransmitted(self) -> bool:
        ...

    def getNanotimeLastTransmit(self) -> int:
        ...

    def setNanotimeLastTransmit(self, value: int) -> None:
        ...

    def acquireNetworkLock(self) -> None:
        ...

    def releaseNetworkLock(self) -> None:
        ...

    def onPretendTransmit(self) -> None:
        ...

    def resetModulePingTimer(self) -> None:
        ...

    def getModule(self) -> LynxModuleIntf:
        ...

    def setModule(self, module: LynxModule) -> None:
        ...

    def getModuleAddress(self) -> int:
        ...

    def getMessageNumber(self) -> int:
        ...

    def setMessageNumber(self, value: int) -> None:
        ...

    def getReferenceNumber(self) -> int:
        ...

    def setReferenceNumber(self, value: int) -> None:
        ...

    def getPayloadTimeWindow(self) -> TimeWindow:
        ...

    def setPayloadTimeWindow(self, payloadTimeWindow: TimeWindow) -> None:
        ...

    def getSerialization(self) -> LynxDatagram:
        ...

    def forgetSerialization(self) -> None:
        ...

    def setSerialization(self, datagram: LynxDatagram) -> None:
        ...

    def loadFromSerialization(self) -> None:
        ...

    def getCommandNumber(self) -> int:
        ...

    def toPayloadByteArray(self) -> list[int]:
        ...

    def fromPayloadByteArray(self, rgb: list[int]) -> None:
        ...

    def isAckable(self) -> bool:
        ...

    def isAck(self) -> bool:
        ...

    def isNack(self) -> bool:
        ...

    def isResponseExpected(self) -> bool:
        """Returns whether this message will generate a response message in return. Ackables which do *not* generate a response will generate an ack instead."""
        ...

    def isResponse(self) -> bool:
        ...

    def isDangerous(self) -> bool:
        ...

    module: LynxModuleIntf
    messageNumber: int
    referenceNumber: int
    serialization: LynxDatagram
    hasBeenTransmitted_: bool
    nanotimeLastTransmit: int
    payloadTimeWindow: TimeWindow


class LynxRespondable(LynxMessage, Generic[RESPONSE]):
    """A LynxRespondable is a message that will generate a response from the module to which it is transmitted. A positive response is either a full-fledged response message (if the message expects a response) or a LynxAck if not; a negative response is in the form of a LynxNack."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxRespondable"
    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        """Constructor for any messages that do not expect a response (other than ACK or NACK)"""
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, defaultResponse: RESPONSE) -> None:
        """Constructor for commands that expect a response (not just an ACK)"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def onPretendTransmit(self) -> None:
        ...

    def hasBeenAcknowledged(self) -> bool:
        ...

    def isAckOrResponseReceived(self) -> bool:
        ...

    def isNackReceived(self) -> bool:
        ...

    def getNackReceived(self) -> LynxNack:
        ...

    def isAckable(self) -> bool:
        ...

    def isResponseExpected(self) -> bool:
        ...

    def pretendFinish(self) -> None:
        ...

    def onAckReceived(self, ack: LynxAck) -> None:
        ...

    def setAttentionRequired(self, attentionRequired: bool) -> None:
        ...

    def onResponseReceived(self, response: LynxMessage) -> None:
        ...

    def onNackReceived(self, nack: LynxNack) -> None:
        ...

    def send(self) -> None:
        ...

    def sendReceive(self) -> RESPONSE:
        ...

    def usePretendResponseIfRealModuleDoesntSupport(self) -> bool:
        """Command normally pre-create responses that get used when the usb device is in pretend mode. Normally, those responses are *only* used in pretend mode. However, on a case-by-case basis those pretend responses can *also* be used when armed in the situation where the module in question doesn't in fact support the command (perhaps it has an older, shorter notion of a particular interface, for example)."""
        ...

    def throwNackForUnsupportedCommand(self, e: LynxUnsupportedCommandException) -> None:
        ...

    def responseOrThrow(self) -> RESPONSE:
        ...

    def throwIfNack(self) -> None:
        ...

    def getMsAwaitInterval(self) -> int:
        ...

    def getMsRetransmissionInterval(self) -> int:
        ...

    def awaitAndRetransmit(self, latch: Any, nackCode: LynxNack.ReasonCode, message: str) -> None:
        ...

    def awaitAckResponseOrNack(self) -> None:
        ...


class LynxCommand(LynxRespondable[RESPONSE], Generic[RESPONSE]):
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxCommand"
    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        """Constructor for commands that do not expect a response (other than ACK or NACK)"""
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, defaultResponse: RESPONSE) -> None:
        """Constructor for commands that expect a response (not just an ACK)"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def getResponseClass(clazz: type[object]) -> type[LynxResponse]:
        """Returns the LynxResponse that goes with this class"""
        ...


class LynxResponse(LynxRespondable[RESPONSE], Generic[RESPONSE]):
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxResponse"
    def __init__(self, module: LynxModuleIntf) -> None:
        ...

    def isResponse(self) -> bool:
        ...

    def isDangerous(self) -> bool:
        ...

    RESPONSE_BIT: int


class LynxNack(LynxMessage):
    """Created by bob on 2016-03-04."""
    __java__ = "com.qualcomm.hardware.lynx.commands.standard.LynxNack"
    class ReasonCode:
        __java__ = "com.qualcomm.hardware.lynx.commands.standard.LynxNack.ReasonCode"
        def toString(self) -> str:
            ...

        def getValue(self) -> int:
            ...

        def isUnsupportedReason(self) -> bool:
            ...

    class StandardReasonCode(ReasonCode, enum.Enum):
        __java__ = "com.qualcomm.hardware.lynx.commands.standard.LynxNack.StandardReasonCode"
        PARAM0 = enum.auto()
        PARAM1 = enum.auto()
        PARAM2 = enum.auto()
        PARAM3 = enum.auto()
        PARAM4 = enum.auto()
        PARAM5 = enum.auto()
        PARAM6 = enum.auto()
        PARAM7 = enum.auto()
        PARAM8 = enum.auto()
        PARAM9 = enum.auto()
        GPIO_OUT0 = enum.auto()
        GPIO_OUT1 = enum.auto()
        GPIO_OUT2 = enum.auto()
        GPIO_OUT3 = enum.auto()
        GPIO_OUT4 = enum.auto()
        GPIO_OUT5 = enum.auto()
        GPIO_OUT6 = enum.auto()
        GPIO_OUT7 = enum.auto()
        GPIO_NO_OUTPUT = enum.auto()
        GPIO_IN0 = enum.auto()
        GPIO_IN1 = enum.auto()
        GPIO_IN2 = enum.auto()
        GPIO_IN3 = enum.auto()
        GPIO_IN4 = enum.auto()
        GPIO_IN5 = enum.auto()
        GPIO_IN6 = enum.auto()
        GPIO_IN7 = enum.auto()
        GPIO_NO_INPUT = enum.auto()
        SERVO_NOT_CONFIG_BEFORE_ENABLED = enum.auto()
        BATTERY_TOO_LOW_TO_RUN_SERVO = enum.auto()
        I2C_MASTER_BUSY = enum.auto()
        I2C_OPERATION_IN_PROGRESS = enum.auto()
        I2C_NO_RESULTS_PENDING = enum.auto()
        I2C_QUERY_MISMATCH = enum.auto()
        I2C_TIMEOUT_SDA_STUCK = enum.auto()
        I2C_TIMEOUT_SCK_STUCK = enum.auto()
        I2C_TIMEOUT_UNKNOWN_CAUSE = enum.auto()
        MOTOR_NOT_CONFIG_BEFORE_ENABLED = enum.auto()
        COMMAND_INVALID_FOR_MOTOR_MODE = enum.auto()
        BATTERY_TOO_LOW_TO_RUN_MOTOR = enum.auto()
        COMMAND_IMPL_PENDING = enum.auto()
        COMMAND_ROUTING_ERROR = enum.auto()
        PACKET_TYPE_ID_UNKNOWN = enum.auto()
        ABANDONED_WAITING_FOR_RESPONSE = enum.auto()
        ABANDONED_WAITING_FOR_ACK = enum.auto()
        UNRECOGNIZED_REASON_CODE = enum.auto()
        CANCELLED_FOR_SAFETY = enum.auto()
        def getValue(self) -> int:
            ...

        def isUnsupportedReason(self) -> bool:
            ...

    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, nackReasonCode: int) -> None:
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, reasonCode: LynxNack.ReasonCode) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getNackReasonCode(self) -> LynxNack.ReasonCode:
        ...

    def getNackReasonCodeAsEnum(self) -> LynxNack.StandardReasonCode:
        """Use this method to easily check for certain reason codes in a switch statement (as StandardReasonCode is an enum). Do not use it for logging, as the result may not contain the true reason code sent by the hub."""
        ...

    @staticmethod
    def getStandardCommandNumber() -> int:
        ...

    def getCommandNumber(self) -> int:
        ...

    def toPayloadByteArray(self) -> list[int]:
        ...

    def fromPayloadByteArray(self, rgb: list[int]) -> None:
        ...

    def isNack(self) -> bool:
        ...

    def isDangerous(self) -> bool:
        ...


class ConfigurationType:
    """ConfigurationType instances represent the type of various kinds of hardware device configurations that might exist within the SDK."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ConfigurationType"
    class DeviceFlavor(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.configuration.ConfigurationType.DeviceFlavor"
        BUILT_IN = enum.auto()
        I2C = enum.auto()
        MOTOR = enum.auto()
        ANALOG_SENSOR = enum.auto()
        SERVO = enum.auto()
        DIGITAL_IO = enum.auto()
        ANALOG_OUTPUT = enum.auto()
        ETHERNET_OVER_USB = enum.auto()

    def getName(self) -> str:
        ...

    def isDeprecated(self) -> bool:
        ...

    def getClassSource(self) -> ConfigurationTypeManager.ClassSource:
        ...

    def annotatedClassIsInstantiable(self) -> bool:
        ...

    def getXmlTag(self) -> str:
        ...

    def toUSBDeviceType(self) -> DeviceManager.UsbDeviceType:
        """If this configuration type has a corresponding USB device configuration type, returns same; otherwise, returns DeviceManager.UsbDeviceType#FTDI_USB_UNKNOWN_DEVICE."""
        ...

    def isDeviceFlavor(self, flavor: ConfigurationType.DeviceFlavor) -> bool:
        ...

    def isCompatibleWith(self, controlSystem: ControlSystem) -> bool:
        ...

    def getDeviceFlavor(self) -> ConfigurationType.DeviceFlavor:
        """Returns the configuration type's most specific flavor."""
        ...


class UserConfigurationType(ConfigurationType):
    """UserConfigurationType contains metadata regarding classes which have been declared as user-defined sensor implementations. Subclasses should be either abstract or final."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.UserConfigurationType"
    @overload
    def __init__(self, clazz: type[object], flavor: Any, xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self, flavor: Any) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def processAnnotation(self, deviceProperties: DeviceProperties) -> None:
        ...

    def finishedAnnotations(self, clazz: type[object]) -> None:
        ...

    def isCompatibleWith(self, controlSystem: ControlSystem) -> bool:
        ...

    def getDeviceFlavor(self) -> Any:
        ...

    def getName(self) -> str:
        ...

    def getDescription(self) -> str:
        ...

    def getClassSource(self) -> ConfigurationTypeManager.ClassSource:
        ...

    def isBuiltIn(self) -> bool:
        """This is about whether the type \"comes with\" the SDK, not whether it lives in BuiltInConfigurationType"""
        ...

    def annotatedClassIsInstantiable(self) -> bool:
        """Only InstantiableUserConfigurationType subclasses can have this return true"""
        ...

    def getXmlTag(self) -> str:
        ...

    def toUSBDeviceType(self) -> DeviceManager.UsbDeviceType:
        ...

    def isDeviceFlavor(self, flavor: Any) -> bool:
        ...

    def isDeprecated(self) -> bool:
        ...

    name: str
    description: str


class InstantiableUserConfigurationType(UserConfigurationType):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.InstantiableUserConfigurationType"
    class ClearTypesFromSourceResult:
        __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.InstantiableUserConfigurationType.ClearTypesFromSourceResult"
        def __init__(self, newTopLevelType: InstantiableUserConfigurationType, freedDisplayNames: set[str]) -> None:
            ...

        newTopLevelType: InstantiableUserConfigurationType
        freedDisplayNames: set[str]

    @overload
    def __init__(self, clazz: type[object], flavor: Any, xmlTag: str, allowableConstructorPrototypes: list[ConstructorPrototype], classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self, flavor: Any) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def processAnnotation(self, deviceProperties: DeviceProperties) -> None:
        ...

    def findMatch(self, prototype: ConstructorPrototype) -> Any:
        """Finds a constructor of the underlying class that matches a given prototype"""
        ...

    def forThisAndAllAdditionalTypes(self, consumer: Consumer[InstantiableUserConfigurationType]) -> None:
        ...

    def checkThisAndAllAdditionalTypes(self, checker: Function[InstantiableUserConfigurationType, bool]) -> bool:
        ...

    def hasConstructors(self) -> bool:
        ...

    def getClazz(self) -> type[HardwareDevice]:
        ...

    def annotatedClassIsInstantiable(self) -> bool:
        ...

    def addAdditionalTypeToInstantiate(self, newAdditionalType: InstantiableUserConfigurationType) -> None:
        ...

    def clearTypesFromSource(self, classSource: ConfigurationTypeManager.ClassSource) -> InstantiableUserConfigurationType.ClearTypesFromSourceResult:
        ...

    def handleConstructorExceptions(self, e: Any, clazz: type[object]) -> None:
        ...

    additionalTypesToInstantiate: set[InstantiableUserConfigurationType]


class DigitalIoDeviceConfigurationType(InstantiableUserConfigurationType):
    """DigitalIoDeviceConfigurationType contains the meta-data for a user-defined digital device driver."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.DigitalIoDeviceConfigurationType"
    @overload
    def __init__(self, clazz: type[HardwareDevice], xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def createInstances(self, controller: DigitalChannelController, port: int) -> list[HardwareDevice]:
        ...


class RobotUsbManager:
    """USB Manager Interface"""
    __java__ = "com.qualcomm.robotcore.hardware.usb.RobotUsbManager"
    def scanForDevices(self) -> list[SerialNumber]:
        """Scan for USB devices; return serial numbers of those found"""
        ...

    def openBySerialNumber(self, serialNumber: SerialNumber) -> RobotUsbDevice:
        """Open device by serial number"""
        ...


class CameraManager:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. CameraManager is the main entrypoint for accessing USB Video Class (UVC) webcams. Modelled after android.hardware.camera2.CameraManager"""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraManager"
    def getAllWebcams(self) -> list[WebcamName]:
        """Return the list of currently connected camera devices which are USB webcams. Note: this list may contain duplicates if more than once instance of a serialnumberless webcam is attached."""
        ...

    def nameFromCameraDirection(self, cameraDirection: BuiltinCameraDirection) -> CameraName:
        """Returns a camera name indicating a particular BuiltinCameraDirection. Using this method, both camera directions and webcam names can be indicated with a uniform name representation."""
        ...

    def nameForUnknownCamera(self) -> CameraName:
        """Returns a CameraName which is guaranteed never to represent that of an actual camera. This can be useful in situations where a value distinguished from null and actual camera names is desired."""
        ...

    def nameForSwitchableCamera(self, *cameraNames: CameraName) -> SwitchableCameraName:
        """Returns a name of a virtual camera comprised of a sequence of other camera. Only one of the member cameras is opened at a time, but which one is in use can be switched on the fly."""
        ...

    def requestPermissionAndOpenCamera(self, deadline: Deadline, cameraName: CameraName, continuation: Continuation[Camera.StateCallback]) -> Camera:
        """Synchronously requests permission to opens the camera of the indicated name, then opens that camera. The calling thread blocks until the open attempt is complete. If successful, the newly opened Camera is returned. It is the caller's responsibility to ultimately call Camera#close() when they are done using the camera. If unsuccessful, then null is returned. If a Camera.StateCallback continuation is provided, that callback is notified of life-cycle events of the camera. In particular, it is guaranteed that one of Camera.StateCallback#onOpened(Camera) or Camera.StateCallback#onOpenFailed will be called."""
        ...

    def asyncOpenCameraAssumingPermission(self, cameraName: CameraName, continuation: Continuation[Camera.StateCallback], reopenDuration: int, reopenTimeUnit: Any) -> None:
        """Asynchronously opens a connection to a camera with the given name. Assumes that permissions have already been obtained to do so. If the camera is successfully opened, Camera.StateCallback#onOpened will be invoked with the newly opened Camera. The camera device can then be set up for operation by calling Camera#createCaptureSession If the camera fails to open, then Camera.StateCallback#onOpenFailed is called."""
        ...


class ThrowingSupplier(Generic[VALUE, EXCEPTION]):
    """An interface for workers that has a specialized exception set"""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.ThrowingSupplier"
    def get(self) -> VALUE:
        ...


class VectorF:
    """A VectorF represents a single-dimensional vector of floats. It is not a matrix, but can easily be converted into either a RowMatrixF or a ColumnMatrixF should that be desired. That said, vectors can be multiplied by matrices to their left (or right); this is commonly used to transform a set of coordinates (in the vector) by a transformation matrix."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.VectorF"
    @overload
    def __init__(self, data: list[float]) -> None:
        ...
    @overload
    def __init__(self, x: float) -> None:
        ...
    @overload
    def __init__(self, x: float, y: float) -> None:
        ...
    @overload
    def __init__(self, x: float, y: float, z: float) -> None:
        ...
    @overload
    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @overload
    @staticmethod
    def length(length: int) -> VectorF:
        """Creates a new vector of the indicated length. The vector will contain zeros."""
        ...
    @overload
    def length(self) -> int:
        ...
    def length(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getData(self) -> list[float]:
        ...

    def get(self, index: int) -> float:
        ...

    def put(self, index: int, value: float) -> None:
        ...

    def toString(self) -> str:
        ...

    def normalized3D(self) -> VectorF:
        """Consider this vector as a 3D coordinate or 3D homogeneous coordinate, and, if the latter, return its normalized form. In either case, the result is of length three, and contains coordinate values for x, y, and z at indices 0, 1, and 2 respectively."""
        ...

    def magnitude(self) -> float:
        ...

    def dotProduct(self, him: VectorF) -> float:
        """Returns the dot product of this vector and another."""
        ...

    @overload
    def multiplied(self, him: MatrixF) -> MatrixF:
        """Multiplies this vector, taken as a row vector, against the indicated matrix."""
        ...
    @overload
    def multiplied(self, scale: float) -> VectorF:
        """Returns a new vector containing the elements of this vector scaled by the indicated factor."""
        ...
    def multiplied(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def added(self, addend: MatrixF) -> MatrixF:
        """Adds this vector, taken as a row vector against, to the indicated matrix."""
        ...
    @overload
    def added(self, addend: VectorF) -> VectorF:
        ...
    def added(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def add(self, addend: VectorF) -> None:
        ...

    @overload
    def subtracted(self, subtrahend: MatrixF) -> MatrixF:
        """Subtracts the indicated matrix from this vector, taken as a row vector."""
        ...
    @overload
    def subtracted(self, subtrahend: VectorF) -> VectorF:
        ...
    def subtracted(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def subtract(self, subtrahend: VectorF) -> None:
        ...

    def multiply(self, scale: float) -> None:
        ...

    @overload
    def dimensionsError(self) -> Any:
        ...
    @overload
    @staticmethod
    def dimensionsError(length: int) -> Any:
        ...
    def dimensionsError(self, *args: Any, **kwargs: Any) -> Any:
        ...

    data: list[float]


class LynxInterface:
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxInterface"
    def __init__(self, interfaceName: str, *commands: type[LynxInterfaceCommand]) -> None:
        ...

    def getInterfaceName(self) -> str:
        ...

    def getCommandCount(self) -> int:
        ...

    def setBaseCommandNumber(self, baseCommandNumber: int) -> None:
        ...

    def setWasNacked(self, nacked: bool) -> None:
        ...

    def wasNacked(self) -> bool:
        ...

    def getBaseCommandNumber(self) -> int:
        ...

    def getCommandIndex(self, clazz: type[LynxInterfaceCommand]) -> int:
        """Returns the index of this command class within the interface"""
        ...

    def getResponseIndex(self, clazz: type[LynxInterfaceResponse]) -> int:
        """Returns the index of this response class within the interface"""
        ...

    def getCommandClasses(self) -> list[type[LynxInterfaceCommand]]:
        ...

    ERRONEOUS_COMMAND_NUMBER: int
    ERRONEOUS_INDEX: int


class LynxInterfaceResponse(LynxResponse):
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxInterfaceResponse"
    def __init__(self, module: LynxModuleIntf) -> None:
        ...

    def getInterface(self) -> LynxInterface:
        ...

    def getCommandNumber(self) -> int:
        ...


class EvictingBlockingQueue(Generic[E]):
    """EvictingBlockingQueue is a BlockingQueue that evicts old elements rather than failing when new data is added to the queue."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.collections.EvictingBlockingQueue"
    def __init__(self, targetQueue: Any) -> None:
        """Constructs an EvictingBlockingQueue using the target queue as an implementation. The target queue must have a capacity of at least one."""
        ...

    def setEvictAction(self, evictAction: Consumer[E]) -> None:
        ...

    def iterator(self) -> Any:
        ...

    def size(self) -> int:
        ...

    @overload
    def offer(self, e: E) -> bool:
        ...
    @overload
    def offer(self, e: E, timeout: int, unit: Any) -> bool:
        ...
    def offer(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def take(self) -> E:
        ...

    @overload
    def poll(self, timeout: int, unit: Any) -> E:
        ...
    @overload
    def poll(self) -> E:
        ...
    def poll(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def peek(self) -> E:
        ...

    def put(self, e: E) -> None:
        ...

    def remainingCapacity(self) -> int:
        ...

    @overload
    def drainTo(self, c: list[E]) -> int:
        ...
    @overload
    def drainTo(self, c: list[E], maxElements: int) -> int:
        ...
    def drainTo(self, *args: Any, **kwargs: Any) -> Any:
        ...

    theLock: object
    targetQueue: Any
    evictAction: Consumer[E]


class MemberwiseCloneable(Generic[T]):
    """MemberwiseCloneable tries to make it easier to use Java's botched 'cloneable' mechanism. Sigh. Such a mess. So unnecessary."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.system.MemberwiseCloneable"
    def memberwiseClone(self) -> T:
        ...


class Continuation(Generic[T]):
    """Continuation provides mechanisms for continuing subsequent, later work on a different thread (either a handler thread or a worker thread) along with a contextual object that will be present at such time. The latter is usually a consumer of some type, that will thus receive the result of some computation with threading all taken care of neat and tidy."""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.Continuation"
    class Dispatcher(MemberwiseCloneable, Generic[S]):
        __java__ = "org.firstinspires.ftc.robotcore.external.function.Continuation.Dispatcher"
        def __init__(self, continuation: Continuation[S]) -> None:
            ...

        def isTrivial(self) -> bool:
            ...

        def isHandler(self) -> bool:
            ...

        def isExecutor(self) -> bool:
            ...

        def setContinuation(self, continuation: Continuation[S]) -> None:
            ...

        def dispatch(self, consumer: ContinuationResult[S]) -> None:
            ...

        def copyAndCast(self) -> Continuation.Dispatcher[U]:
            """Returns a copy of this object (duh). Note that we use 'clone' as in practice we've maybe got anonymous subclasses whose names we don't even know. The alternative would have been to use reflection, but that's slower."""
            ...

        continuation: Continuation[S]

    def __init__(self, target: T) -> None:
        ...

    def getTarget(self) -> T:
        ...

    def getDispatcher(self) -> Continuation.Dispatcher[T]:
        ...

    @staticmethod
    def createTrivial(t: T) -> Continuation[T]:
        ...

    @overload
    @staticmethod
    def create(executor: Any, t: T) -> Continuation[T]:
        ...
    @overload
    @staticmethod
    def create(handler: Any, t: T) -> Continuation[T]:
        ...
    @staticmethod
    def create(*args: Any, **kwargs: Any) -> Any:
        ...

    def createForNewTarget(self, newTarget: U) -> Continuation[U]:
        """Return a new continuation that dispatches to the same location but operates on a new target instance of a possibly different target type."""
        ...

    def dispatch(self, consumer: ContinuationResult[T]) -> None:
        ...

    def dispatchHere(self, consumer: ContinuationResult[T]) -> None:
        """Note: be very careful in the use of #dispatchHere(ContinuationResult), as it can easily lead to unexpected deadlocks."""
        ...

    def isHandler(self) -> bool:
        ...

    def getHandler(self) -> Any:
        ...

    def isTrivial(self) -> bool:
        ...

    def isDispatchSynchronous(self) -> bool:
        """When we dispatch this continuation, is it a synchronous, blocking call, one that will be fully executed before the dispatch returns?"""
        ...

    def canBorrowThread(self, thread: Any) -> bool:
        """Caller guarantees that they're on a typical utility 'worker' thread (in contrast to, for example, the dedicated UI thread, or other threads on which work is dispatched through a Handler). Answer whether we are ok to dispatch here instead of wherever we might usually dispatch. Caller must additionally assure themselves from their contextual knowledge that taking advantage of this function will not lead to deadlocks that otherwise would not occur."""
        ...

    def createTrivialDispatcher(self) -> Continuation[T]:
        ...

    def createHandlerDispatcher(self, handler: Any) -> Continuation[T]:
        ...

    def createExecutorDispatcher(self, threadPool: Any) -> Continuation[T]:
        ...

    def setDispatcher(self, dispatcher: Continuation.Dispatcher[T]) -> Continuation[T]:
        ...

    TAG: str
    target: T
    dispatcher: Continuation.Dispatcher[T]


class CameraControls:
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraControls"
    def getControl(self, controlType: type[T]) -> T:
        ...


class Camera(CameraControls):
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. Camera provides access to a camera that has been opened. Modelled after android.hardware.camera2.CameraDevice, but somewhat simplified."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.Camera"
    class StateCallback:
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.Camera.StateCallback"
        def onOpened(self, camera: Camera) -> None:
            """The method called when a camera device has finished successfully opening. At this point, the camera device is ready to use, and Camera#createCaptureSession can be called to set up a capture session. Important: once this method is invoked, callee is responsible for calling Camera#close() when they are finished using the camera device."""
            ...

        def onOpenFailed(self, cameraName: CameraName, reason: Camera.OpenFailure) -> None:
            """A request to open a camera has failed."""
            ...

        def onClosed(self, camera: Camera) -> None:
            """The method called when a camera device has been closed with Camera#close. Any attempt to call methods on this Camera in the future will likely throw a RuntimeException."""
            ...

        def onError(self, camera: Camera, error: Camera.Error) -> None:
            """The method called when a camera device has encountered a serious error. This indicates a failure of the camera device or camera service in some way. Any attempt to call methods on this Camera in the future will likely throw a CameraException There may still be capture completion or camera stream callbacks that will be called after this error is received. You should clean up the camera with Camera#close after this happens. Further attempts at recovery are error-code specific."""
            ...

    class Error(enum.Enum):
        """Reasons for which a Camera might have failed after opening. Note: this list might get extended and elaborated in the future; do not assume that the present set of errors is exhaustive. Rather, treat any errors you do not recognize as you do #OtherError."""
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.Camera.Error"
        None_ = enum.auto()
        OtherError = enum.auto()
        Disconnected = enum.auto()
        Connected = enum.auto()
        StreamingRequestNotSupported = enum.auto()
        Timeout = enum.auto()
        InternalError = enum.auto()

    class OpenFailure(enum.Enum):
        """Reasons for which a Camera might have failed to open. Note: this list might get extended and elaborated in the future; do not assume that the present set of errors is exhaustive. Rather, treat any errors you do not recognize as you do #OtherFailure."""
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.Camera.OpenFailure"
        None_ = enum.auto()
        OtherFailure = enum.auto()
        CameraTypeNotSupported = enum.auto()
        InUseOrAccessDenied = enum.auto()
        Disconnected = enum.auto()
        InternalError = enum.auto()

    def getCameraName(self) -> CameraName:
        """Returns the name of this camera device. This method can be called even if the device has been closed or has encountered a serious error."""
        ...

    def createCaptureRequest(self, androidFormat: int, size: Size, fps: int) -> CameraCaptureRequest:
        """Create a capture request. Capture requests contain the set of parameters used to configure a given capture operations."""
        ...

    def createCaptureSession(self, continuation: Continuation[CameraCaptureSession.StateCallback]) -> CameraCaptureSession:
        """Creates a capture session for this device. Only one capture session may be extant at any given time: any extant session is closed if a new one is created. If the creation of the capture session is successful, then CameraCaptureSession.StateCallback#onConfigured(CameraCaptureSession) is called. If the creation fails, then an exception is thrown."""
        ...

    def close(self) -> None:
        """Close the connection to this camera device as quickly as possible. Immediately after this call, all calls to the camera device or active session interface will throw a IllegalStateException, except for calls to close(). Once the device has fully shut down, the StateCallback#onClosed callback will be called. Immediately after this call, besides the final StateCallback#onClosed calls, no further callbacks from the device or the active session will occur, and any remaining submitted capture requests will be discarded, and no success or failure callbacks will be invoked."""
        ...

    def dup(self) -> Camera:
        """Returns another Camera on the same underlying device with an independent close() effect. The analogy is that of dup()ing open file descriptors in Linux / Unix."""
        ...


class Size:
    """Immutable class for describing width and height dimensions in integer valued units. Backported from API21, where it was introduced, to here, where we need to support API19."""
    __java__ = "org.firstinspires.ftc.robotcore.external.android.util.Size"
    def __init__(self, width: int, height: int) -> None:
        """Create a new immutable Size instance."""
        ...

    def getWidth(self) -> int:
        """Get the width of the size (in pixels)."""
        ...

    def getHeight(self) -> int:
        """Get the height of the size (in pixels)."""
        ...

    def equals(self, obj: object) -> bool:
        """Check if this size is equal to another size."""
        ...

    def toString(self) -> str:
        """Return the size represented as a string with the format \"WxH\""""
        ...

    @staticmethod
    def parseSize(string: str) -> Size:
        """Parses the specified string as a size value."""
        ...

    def hashCode(self) -> int:
        """{@inheritDoc}"""
        ...


class CameraCaptureSession:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. CameraCaptureSession provides the means by which streaming data can be captured from the camera."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureSession"
    class StateCallback:
        """A callback object for receiving updates about the state of a camera capture session."""
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureSession.StateCallback"
        def onConfigured(self, session: CameraCaptureSession) -> None:
            """This method is called when the camera device has finished configuring itself, and the session can start processing capture requests."""
            ...

        def onClosed(self, session: CameraCaptureSession) -> None:
            """This method is called when the session is closed. A session is closed when a new session is created by the parent camera device, or when the parent camera device is closed (either by the user closing the device, or due to a camera device disconnection or fatal error). This method will not be called unless #onConfigured is called first."""
            ...

    class CaptureCallback:
        """A callback object for tracking the progress of a CameraCaptureRequest submitted to the camera device."""
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureSession.CaptureCallback"
        def onNewFrame(self, session: CameraCaptureSession, request: CameraCaptureRequest, cameraFrame: CameraFrame) -> None:
            """This method is called when an image capture has fully completed and a newly captured frame is available."""
            ...

    class StatusCallback:
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureSession.StatusCallback"
        def onCaptureSequenceCompleted(self, session: CameraCaptureSession, cameraCaptureSequenceId: CameraCaptureSequenceId, lastFrameNumber: int) -> None:
            """This method is called when a capture sequence is completed. Once this is invoked, no further calls to CaptureCallback#onNewFrame will be made."""
            ...

    def getCamera(self) -> Camera:
        """Get the camera device that this session is created for."""
        ...

    def close(self) -> None:
        """Close this capture session"""
        ...

    @overload
    def startCapture(self, cameraCaptureRequest: CameraCaptureRequest, captureCallback: CameraCaptureSession.CaptureCallback, statusContinuation: Continuation[CameraCaptureSession.StatusCallback]) -> CameraCaptureSequenceId:
        """Stream data from the camera: request endlessly repeating capture of images by this capture session. CameraFrames are provided through CaptureCallback#onNewFrame as they become available. With this method, the camera device will continually capture images using the settings in the provided CameraCaptureRequest, at the maximum rate possible. If the capture fails to start, then an exception is thrown. To stop the repeating capture, call #stopCapture Calling this method will replace any earlier repeating request or burst set up by this method."""
        ...
    @overload
    def startCapture(self, cameraCaptureRequest: CameraCaptureRequest, captureContinuation: Continuation[CameraCaptureSession.CaptureCallback], statusContinuation: Continuation[CameraCaptureSession.StatusCallback]) -> CameraCaptureSequenceId:
        """As in #startCapture(CameraCaptureRequest,, but supports the generality of a Continuation to handle the capture. Note that unless this continuation synchronously dispatches, or indicates that it can run on a guest worker thread, a copy of each frame will be made before invoking CaptureCallback#onNewFrame."""
        ...
    def startCapture(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def stopCapture(self) -> None:
        """Cancel any ongoing repeating capture set by #startCapture. This method is idempotent. Any currently in-flight captures will still complete."""
        ...


class MotorConfigurationType(UserConfigurationType):
    """MotorConfigurationType contains the amalgamated set of information that is known about a given type of motor."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType"
    @overload
    def __init__(self, clazz: type[object], xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getTicksPerRev(self) -> float:
        ...

    def getAchieveableMaxTicksPerSecond(self) -> float:
        ...

    def getAchieveableMaxTicksPerSecondRounded(self) -> int:
        ...

    def setTicksPerRev(self, ticksPerRev: float) -> None:
        ...

    def getGearing(self) -> float:
        ...

    def setGearing(self, gearing: float) -> None:
        ...

    def getMaxRPM(self) -> float:
        ...

    def setMaxRPM(self, maxRPM: float) -> None:
        ...

    def getAchieveableMaxRPMFraction(self) -> float:
        ...

    def setAchieveableMaxRPMFraction(self, achieveableMaxRPMFraction: float) -> None:
        ...

    def getOrientation(self) -> Rotation:
        ...

    def setOrientation(self, orientation: Rotation) -> None:
        ...

    def hasExpansionHubVelocityParams(self) -> bool:
        ...

    def getHubVelocityParams(self) -> ExpansionHubMotorControllerParamsState:
        ...

    def hasExpansionHubPositionParams(self) -> bool:
        ...

    def getHubPositionParams(self) -> ExpansionHubMotorControllerParamsState:
        ...

    def getDistributorInfo(self) -> DistributorInfoState:
        ...

    @staticmethod
    def getUnspecifiedMotorType() -> MotorConfigurationType:
        ...

    @staticmethod
    def getMotorType(clazz: type[object]) -> MotorConfigurationType:
        ...

    def clone(self) -> MotorConfigurationType:
        ...

    @overload
    def processAnnotation(self, params: object) -> bool:
        ...
    @overload
    def processAnnotation(self, motorType: MotorType) -> bool:
        ...
    @overload
    def processAnnotation(self, motorType: MotorType) -> bool:
        ...
    @overload
    def processAnnotation(self, params: ExpansionHubPIDFVelocityParams) -> bool:
        ...
    @overload
    def processAnnotation(self, params: ExpansionHubMotorControllerVelocityParams) -> bool:
        ...
    @overload
    def processAnnotation(self, params: ExpansionHubPIDFPositionParams) -> bool:
        ...
    @overload
    def processAnnotation(self, params: ExpansionHubMotorControllerPositionParams) -> bool:
        ...
    @overload
    def processAnnotation(self, info: DistributorInfo) -> bool:
        ...
    def processAnnotation(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def finishedAnnotations(self, clazz: type[object]) -> None:
        ...


def ExpansionHubPIDFVelocityParams(*, P: float, I: float = 0, D: float = 0, F: float = 0, algorithm: MotorControlAlgorithm) -> Callable[[type], type]:
    """When ExpansionHubPIDFVelocityParams annotations are placed on a motor type, the indicated PIDF coefficients are automatically initialized when instances of that motor are used."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


def ExpansionHubMotorControllerPositionParams(*, P: float, I: float, D: float) -> Callable[[type], type]:
    """When ExpansionHubMotorControllerVelocityParams annotations are placed on a motor type, the indicated PID coefficients are automatically initialized when instances of that motor are used."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


def MotorType(*, xmlTag: str, name: str, ticksPerRev: float, gearing: float, maxRPM: float, achieveableMaxRPMFraction: float = 0.85, orientation: Rotation) -> Callable[[type], type]:
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class LynxInterfaceCommand(LynxCommand[RESPONSE], Generic[RESPONSE]):
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxInterfaceCommand"
    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        """Constructor for commands that do not expect a response (other than ACK or NACK)"""
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, defaultResponse: RESPONSE) -> None:
        """Constructor for commands that expect a response (not just an ACK)"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getInterface(self) -> LynxInterface:
        ...

    def getCommandNumber(self) -> int:
        ...


class LynxDekaInterfaceCommand(LynxInterfaceCommand[RESPONSE], Generic[RESPONSE]):
    """Created by bob on 2016-03-06."""
    __java__ = "com.qualcomm.hardware.lynx.commands.core.LynxDekaInterfaceCommand"
    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        """Constructor for commands that do not expect a response (other than ACK or NACK)"""
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, defaultResponse: RESPONSE) -> None:
        """Constructor for commands that expect a response (not just an ACK)"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def createDekaInterface() -> LynxInterface:
        ...

    def getInterface(self) -> LynxInterface:
        ...

    dekaInterfaceName: str


class ContinuationResult(Generic[T]):
    """ContinuationResult is used as the mechanism by which a Continuation delivers its dispatched target."""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.ContinuationResult"
    def handle(self, t: T) -> None:
        ...


class Function(Generic[T, R]):
    """If we were running Java8, we'd just use the built-in interface"""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.Function"
    def apply(self, arg: T) -> R:
        ...


class CameraFrame:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. CameraFrame represents one frame of captured video."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraFrame"
    def getRequest(self) -> CameraCaptureRequest:
        """Returns the request associated with this result."""
        ...

    def getFrameNumber(self) -> int:
        """Get the frame number associated with this result. Whenever a request has been processed, regardless of failure or success, it gets a unique frame number assigned to its future result/failure. For the same type of request (capturing from the camera device or reprocessing), this value monotonically increments, starting with 0, for every new result or failure and the scope is the lifetime of the Camera. Between different types of requests, the frame number may not monotonically increment. For example, the frame number of a newer reprocess result may be smaller than the frame number of an older result of capturing new images from the camera device, but the frame number of a newer reprocess result will never be smaller than the frame number of an older reprocess result."""
        ...

    def getSize(self) -> Size:
        """Returns the dimensions of the image"""
        ...

    def getImageSize(self) -> int:
        """Returns the number of bytes in the image"""
        ...

    @overload
    def getImageData(self) -> list[int]:
        ...
    @overload
    def getImageData(self, buf: list[int]) -> list[int]:
        """Copies the raw image data into the byte array supplied as the parameter. Supplied array must be &gt;= size reported by #getImageSize()"""
        ...
    def getImageData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getImageBuffer(self) -> int:
        """Returns access to the data of the image. This will be #getImageSize() in length."""
        ...

    def getCaptureTime(self) -> int:
        """Returns the time on the System.nanoTime() clock at which this frame was captured."""
        ...

    def getUvcFrameFormat(self) -> UvcFrameFormat:
        """Returns the format of this frame using the UvcFrameFormat enumeration."""
        ...

    def getStride(self) -> int:
        """Number of bytes per horizontal line (undefined/zero for compressed format)"""
        ...

    def getCaptureSequenceId(self) -> CameraCaptureSequenceId:
        """The sequence ID for this frame that was returned by the CameraCaptureSession#startCapture family of functions. The sequence ID is a unique monotonically-increasing value starting from 0, incremented every time a new group of requests is submitted to the Camera."""
        ...

    def copyToBitmap(self, bitmap: Any) -> None:
        """Copies the contents of the CameraFrame into the indicated bitmap. The size of the bitmap must be compatible with this result."""
        ...

    def copy(self) -> CameraFrame:
        """Returns a copy of this frame, one whose data is guaranteed to be accessible as long as the instance is extant. It is recommended that a copied frame be #releaseRef()'d when no longer needed in order to help improve memory usage (this is not required)."""
        ...

    def addRef(self) -> None:
        """Adds a counted reference to the camera frame to facilitate it's deterministic reclamation when no longer needed."""
        ...

    def releaseRef(self) -> int:
        ...

    UnknownFrameNumber: int
    """A frame number that never appears in a real camera frame."""


class UvcFrameFormat(enum.Enum):
    """Java representation of uvc_frame_format (in libuvc.h)"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.camera.libuvc.constants.UvcFrameFormat"
    UNKNOWN = enum.auto()
    ANY = enum.auto()
    UNCOMPRESSED = enum.auto()
    COMPRESSED = enum.auto()
    YUY2 = enum.auto()
    UYVY = enum.auto()
    RGB = enum.auto()
    BGR = enum.auto()
    MJPEG = enum.auto()
    GRAY8 = enum.auto()
    BY8 = enum.auto()
    @staticmethod
    def from_(value: int) -> UvcFrameFormat:
        ...

    def getValue(self) -> int:
        ...

    value: int


class DistributorInfoState:
    """DistributorInfoState contains metadata transcribed from DistributorInfo"""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.DistributorInfoState"
    def __init__(self) -> None:
        ...

    @staticmethod
    def from_(info: DistributorInfo) -> DistributorInfoState:
        ...

    def clone(self) -> DistributorInfoState:
        ...

    def getDistributor(self) -> str:
        ...

    def setDistributor(self, distributor: str) -> None:
        ...

    def getModel(self) -> str:
        ...

    def setModel(self, model: str) -> None:
        ...

    def getUrl(self) -> str:
        ...

    def setUrl(self, url: str) -> None:
        ...


class TargetPositionNotSetException(Exception):
    __java__ = "com.qualcomm.robotcore.exception.TargetPositionNotSetException"
    def __init__(self) -> None:
        ...


def DeviceProperties(*, xmlTag: str, name: str, description: str = '', builtIn: bool = False, defaultDevice: bool = True, compatibleControlSystems: list[ControlSystem], xmlTagAliases: list[str]) -> Callable[[type], type]:
    """DeviceProperties annotations must accompany annotations like AnalogSensorType or ServoType."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class RobotControllerWebInfo:
    """A class that contains various information about the robot controller's web server that is useful to javascript."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.RobotControllerWebInfo"
    def __init__(self, networkName: str, passphrase: str, serverUrl: str, serverIsAlive: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getNetworkName(self) -> str:
        ...

    def getPassphrase(self) -> str:
        ...

    def getServerUrl(self) -> str:
        ...

    def isServerAlive(self) -> bool:
        ...

    def getFtcUserAgentCategory(self) -> FtcUserAgentCategory:
        ...

    def isREVControlHub(self) -> bool:
        ...

    def is5GhzApSupported(self) -> bool:
        ...

    def doesAppUpdateRequireReboot(self) -> bool:
        ...

    def isOtaUpdateSupported(self) -> bool:
        ...

    def getWebSocketApiVersion(self) -> int:
        ...

    def setFtcUserAgentCategory(self, session: dict[str, str]) -> None:
        ...

    @staticmethod
    def setActiveConfigName(newActiveConfig: str) -> None:
        ...

    def toJson(self) -> str:
        ...

    @staticmethod
    def fromJson(json: str) -> RobotControllerWebInfo:
        ...

    TAG: str


class RobotCoreException(Exception):
    __java__ = "com.qualcomm.robotcore.exception.RobotCoreException"
    @overload
    def __init__(self, message: str) -> None:
        ...
    @overload
    def __init__(self, message: str, cause: Any) -> None:
        ...
    @overload
    def __init__(self, format: str, *args: object) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def createChained(e: Any, format: str, *args: object) -> RobotCoreException:
        ...


class RobotState(enum.Enum):
    __java__ = "com.qualcomm.robotcore.robot.RobotState"
    UNKNOWN = enum.auto()
    NOT_STARTED = enum.auto()
    INIT = enum.auto()
    RUNNING = enum.auto()
    STOPPED = enum.auto()
    EMERGENCY_STOP = enum.auto()
    def asByte(self) -> int:
        ...

    @staticmethod
    def fromByte(b: int) -> RobotState:
        ...

    def toString(self, context: Any) -> str:
        ...


def MotorType(*, ticksPerRev: float, gearing: float, maxRPM: float, achieveableMaxRPMFraction: float = 0.85, orientation: Rotation) -> Callable[[type], type]:
    """MotorType is an annotation with which a class or interface can be decorated in order to define a new kind of motor that can be configured in the robot configuration user interface."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class FtcUserAgentCategory(enum.Enum):
    """For the js code, FtcUserAgentCategory distinguishes the RC and DS embedded clients from others"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.FtcUserAgentCategory"
    DRIVER_STATION = enum.auto()
    ROBOT_CONTROLLER = enum.auto()
    OTHER = enum.auto()
    @staticmethod
    def fromUserAgent(userAgent: str) -> FtcUserAgentCategory:
        ...

    @staticmethod
    def addToUserAgent(existingUserAgent: str) -> str:
        ...

    TAG: str


class I2cDeviceConfigurationType(InstantiableUserConfigurationType):
    """I2cDeviceConfigurationType contains the meta-data for a user-defined I2c sensor driver."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.I2cDeviceConfigurationType"
    @overload
    def __init__(self, clazz: type[HardwareDevice], xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def getLynxEmbeddedBNO055ImuType() -> I2cDeviceConfigurationType:
        ...

    @staticmethod
    def getLynxEmbeddedBHI260APImuType() -> I2cDeviceConfigurationType:
        ...

    def processAnnotation(self, i2cSensor: I2cSensor) -> None:
        ...

    def createInstances(self, simpleSynchFunc: Func[I2cDeviceSynchSimple]) -> list[HardwareDevice]:
        ...


def I2cSensor(*, xmlTag: str = '', name: str = '', description: str = 'an I2c sensor') -> Callable[[type], type]:
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class OpModeMeta:
    """OpModeMeta provides information about an OpMode."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.OpModeMeta"
    class Source(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.OpModeMeta.Source"
        ANDROID_STUDIO = enum.auto()
        BLOCKLY = enum.auto()
        ONBOTJAVA = enum.auto()
        EXTERNAL_LIBRARY = enum.auto()
        BUILTIN = enum.auto()

    class Flavor(enum.Enum):
        __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.OpModeMeta.Flavor"
        AUTONOMOUS = enum.auto()
        TELEOP = enum.auto()
        UTILITY = enum.auto()
        SYSTEM = enum.auto()

    @staticmethod
    def nameIsLegalForOpMode(name: str, isSystem: bool) -> bool:
        ...

    @staticmethod
    def isSystemName(name: str) -> bool:
        ...

    def getDisplayName(self) -> str:
        ...

    def toString(self) -> str:
        ...

    def equals(self, o: object) -> bool:
        ...

    def hashCode(self) -> int:
        ...

    DefaultGroup: str
    flavor: OpModeMeta.Flavor
    group: str
    name: str
    systemOpModeBaseDisplayName: str
    autoTransition: str
    source: OpModeMeta.Source
    description: str


class OnBotJavaHelper:
    __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.OnBotJavaHelper"
    def createOnBotJavaClassLoader(self) -> Any:
        """Create a ClassLoader for the current OnBotJava output .dex files."""
        ...

    def getOnBotJavaClassNames(self) -> list[str]:
        """Returns a Collection of the names of classes in OnBotJava."""
        ...

    def getExternalLibrariesClassNames(self) -> list[str]:
        """Returns a Collection of the names of classes in external libraries."""
        ...

    def isExternalLibrariesError(self, e: Any) -> bool:
        """Returns true if the given NoClassDefFoundError (or one of its causes) is due to a class from an external library not being found; false otherwise."""
        ...

    javaRoot: Any
    srcDir: Any
    statusDir: Any
    buildSuccessfulFile: Any
    controlDir: Any


class ClassFilter:
    """Classes that want to iterate over the list of all classes in the APK should implement this interface and register themselves with the ClassManager via the ClassManagerFactory."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.opmode.ClassFilter"
    def filterAllClassesStart(self) -> None:
        """Clears the result of any previous filtering in preparation for further filtering"""
        ...

    def filterOnBotJavaClassesStart(self) -> None:
        ...

    def filterExternalLibrariesClassesStart(self) -> None:
        ...

    def filterClass(self, clazz: type[object]) -> None:
        """Don't call me, I'll call you."""
        ...

    def filterOnBotJavaClass(self, clazz: type[object]) -> None:
        ...

    def filterExternalLibrariesClass(self, clazz: type[object]) -> None:
        ...

    def filterAllClassesComplete(self) -> None:
        """Called when a filtering cycle is complete"""
        ...

    def filterOnBotJavaClassesComplete(self) -> None:
        ...

    def filterExternalLibrariesClassesComplete(self) -> None:
        ...


class ConfigurationTypeManager(ClassFilter):
    """ConfigurationTypeManager is responsible for managing configuration types."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ConfigurationTypeManager"
    class ClassSource(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.configuration.ConfigurationTypeManager.ClassSource"
        APK = enum.auto()
        ONBOTJAVA = enum.auto()
        EXTERNAL_LIB = enum.auto()

    def __init__(self) -> None:
        ...

    @staticmethod
    def getInstance() -> ConfigurationTypeManager:
        ...

    def getUnspecifiedMotorType(self) -> MotorConfigurationType:
        ...

    def getStandardServoType(self) -> ServoConfigurationType:
        ...

    def configurationTypeFromTag(self, xmlTag: str) -> ConfigurationType:
        ...

    def userTypeFromClass(self, flavor: ConfigurationType.DeviceFlavor, clazz: type[object]) -> UserConfigurationType:
        ...

    @overload
    def getApplicableConfigTypes(self, deviceFlavor: ConfigurationType.DeviceFlavor, controlSystem: ControlSystem, configuringControlHubParent: bool, i2cBus: int) -> set[ConfigurationType]:
        """Get the applicable configuration types to populate dropdowns with"""
        ...
    @overload
    def getApplicableConfigTypes(self, deviceFlavor: ConfigurationType.DeviceFlavor, controlSystem: ControlSystem, configuringControlHubParent: bool) -> set[ConfigurationType]:
        """Get the applicable configuration types to populate dropdowns with (don't use this variant for REV I2C)"""
        ...
    def getApplicableConfigTypes(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getGson(self) -> Any:
        ...

    def sendUserDeviceTypes(self) -> None:
        ...

    def deserializeUserDeviceTypes(self, serialization: str) -> None:
        ...

    def filterAllClassesStart(self) -> None:
        ...

    def filterOnBotJavaClassesStart(self) -> None:
        ...

    def filterExternalLibrariesClassesStart(self) -> None:
        ...

    def filterClass(self, clazz: type[object]) -> None:
        ...

    def filterOnBotJavaClass(self, clazz: type[object]) -> None:
        ...

    def filterExternalLibrariesClass(self, clazz: type[object]) -> None:
        ...

    def filterAllClassesComplete(self) -> None:
        ...

    def filterOnBotJavaClassesComplete(self) -> None:
        ...

    def filterExternalLibrariesClassesComplete(self) -> None:
        ...

    def processNewOldAnnotations(self, motorConfigurationType: MotorConfigurationType, clazz: type[object], newType: type[NewType], oldType: type[OldType]) -> None:
        ...

    def processAnnotationIfPresent(self, motorConfigurationType: MotorConfigurationType, clazz: type[object], annotationType: type[A]) -> bool:
        ...

    @staticmethod
    def getXmlTag(clazz: type[object]) -> str:
        ...

    TAG: str
    DEBUG: bool
    LEGACY_HD_HEX_MOTOR_TAG: str
    NEW_HD_HEX_MOTOR_40_TAG: str


class CameraIntrinsics:
    """Provides basic information regarding some characteristics which are built-in to / intrinsic to a particular camera model. https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html https://docs.opencv.org/3.0-beta/doc/tutorials/calib3d/camera_calibration/camera_calibration.html https://www.mathworks.com/help/vision/camera-calibration.html"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.camera.calibration.CameraIntrinsics"
    def __init__(self, focalLengthX: float, focalLengthY: float, principalPointX: float, principalPointY: float, distortionCoefficients: list[float]) -> None:
        ...

    def toArray(self) -> list[float]:
        ...

    def isDegenerate(self) -> bool:
        ...

    focalLengthX: float
    """Focal length x-component. 0.f if not available."""
    focalLengthY: float
    """Focal length y-component. 0.f if not available."""
    principalPointX: float
    """Principal point x-component. 0.f if not available."""
    principalPointY: float
    """Principal point y-component. 0.f if not available."""
    distortionCoefficients: list[float]
    """An 8 element array of distortion coefficients. Array should be filled in the following order (r: radial, t:tangential): [r0, r1, t0, t1, r2, r3, r4, r5] Values that are not available should be set to 0.f. Yes, the parameter order seems odd, but it is correct."""


class CameraCalibration(CameraIntrinsics):
    """An augmentation to CameraIntrinsics that helps support debugging and parsing from XML."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.camera.calibration.CameraCalibration"
    @overload
    def __init__(self, identity: CameraCalibrationIdentity, size: Size, focalLengthX: float, focalLengthY: float, principalPointX: float, principalPointY: float, distortionCoefficients: list[float], remove: bool, isFake: bool) -> None:
        ...
    @overload
    def __init__(self, identity: CameraCalibrationIdentity, size: list[int], focalLength: list[float], principalPoint: list[float], distortionCoefficients: list[float], remove: bool, isFake: bool) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toString(self) -> str:
        ...

    def getIdentity(self) -> CameraCalibrationIdentity:
        ...

    def getSize(self) -> Size:
        ...

    def getRemove(self) -> bool:
        ...

    def isFake(self) -> bool:
        ...

    @staticmethod
    def forUnavailable(calibrationIdentity: CameraCalibrationIdentity, size: Size) -> CameraCalibration:
        ...

    def memberwiseClone(self) -> CameraCalibration:
        ...

    def scaledTo(self, newSize: Size) -> CameraCalibration:
        ...

    @overload
    def getAspectRatio(self) -> float:
        ...
    @overload
    @staticmethod
    def getAspectRatio(size: Size) -> float:
        ...
    def getAspectRatio(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getDiagonal(self) -> float:
        ...
    @overload
    @staticmethod
    def getDiagonal(size: Size) -> float:
        ...
    def getDiagonal(self, *args: Any, **kwargs: Any) -> Any:
        ...

    identity: CameraCalibrationIdentity
    """These are not passed to native code"""
    size: Size
    remove: bool
    isFake_: bool
    resolutionScaledFrom: Size


class MatrixF:
    """MatrixF represents a matrix of floats of a defined dimensionality but abstracts the means by which a particular element of the matrix is retrieved or updated. MatrixF is an abstract class: it is never instantiated; rather, only instances of its subclasses are made."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.MatrixF"
    def __init__(self, numRows: int, numCols: int) -> None:
        """Creates a matrix containing the indicated number of rows and columns."""
        ...

    @overload
    def slice(self, row: int, col: int, numRows: int, numCols: int) -> SliceMatrixF:
        """Returns a matrix which a submatrix of the receiver."""
        ...
    @overload
    def slice(self, numRows: int, numCols: int) -> SliceMatrixF:
        """Returns a matrix which is a submatrix of the receiver starting at (0,0)"""
        ...
    def slice(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def identityMatrix(dim: int) -> MatrixF:
        """Returns an identity matrix of the indicated dimension. An identity matrix is zero everywhere except on the diagonal, where it is one."""
        ...

    @overload
    @staticmethod
    def diagonalMatrix(dim: int, scale: float) -> MatrixF:
        """Returns a new matrix which is zero everywhere except on the diagonal, where it has an indicated value."""
        ...
    @overload
    @staticmethod
    def diagonalMatrix(vector: VectorF) -> MatrixF:
        """Returns a new matrix which is zero everywhere, except on the diagonal, where its values are taken from an indicated vector"""
        ...
    @staticmethod
    def diagonalMatrix(*args: Any, **kwargs: Any) -> Any:
        ...

    def emptyMatrix(self, numRows: int, numCols: int) -> MatrixF:
        """Returns a new empty matrix of the indicated dimensions. If a specific implementation associated with the receiver can be used with these dimensions, then such is used; otherwise a general matrix implementation will be used."""
        ...

    def numRows(self) -> int:
        """Returns the number of rows in this matrix"""
        ...

    def numCols(self) -> int:
        """Returns the number of columns in this matrix"""
        ...

    def get(self, row: int, col: int) -> float:
        """Returns a particular element of this matrix"""
        ...

    def put(self, row: int, col: int, value: float) -> None:
        """Updates a particular element of this matrix"""
        ...

    def getRow(self, row: int) -> VectorF:
        """Returns a vector containing data of a particular row of the receiver."""
        ...

    def getColumn(self, col: int) -> VectorF:
        """Returns a vector containing data of a particular column of the receiver."""
        ...

    def toString(self) -> str:
        ...

    def transform(self, him: VectorF) -> VectorF:
        """Transforms the vector according to this matrix interpreted as a transformation matrix. Conversion to homogeneous coordinates is automatically provided."""
        ...

    def adaptHomogeneous(self, him: VectorF) -> VectorF:
        """Automatically adapts vectors to and from homogeneous coordinates according to the size of the receiver matrix."""
        ...

    @overload
    def formatAsTransform(self) -> str:
        """A simple utility that extracts positioning information from a transformation matrix and formats it in a form palatable to a human being. This should only be invoked on a matrix which is a transformation matrix. We report here using an extrinsic angle reference, meaning that all three angles are rotations in the (fixed) field coordinate system, as this is perhaps easiest to conceptually understand. And we use an angle order of XYZ, which results in the Z angle, being applied last (after X and Y rotations) and so representing the robot's heading on the field, which is often what is of most interest in robot navigation."""
        ...
    @overload
    def formatAsTransform(self, axesReference: AxesReference, axesOrder: AxesOrder, unit: AngleUnit) -> str:
        """A simple utility that extracts positioning information from a transformation matrix and formats it in a form palatable to a human being. This should only be invoked on a matrix which is a transformation matrix."""
        ...
    def formatAsTransform(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def transposed(self) -> MatrixF:
        """Returns a matrix which is the transposition of the receiver matrix."""
        ...

    @overload
    def multiply(self, him: MatrixF) -> None:
        """Updates the receiver to be the product of itself and another matrix."""
        ...
    @overload
    def multiply(self, scale: float) -> None:
        ...
    @overload
    def multiply(self, him: VectorF) -> None:
        ...
    @overload
    def multiply(self, him: list[float]) -> None:
        ...
    def multiply(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def multiplied(self, him: MatrixF) -> MatrixF:
        """Returns a matrix which is the multiplication of the recevier with another matrix."""
        ...
    @overload
    def multiplied(self, scale: float) -> MatrixF:
        """Returns a new matrix in which all the entries of the receiver have been scaled by an indicated value."""
        ...
    @overload
    def multiplied(self, him: VectorF) -> VectorF:
        """Multiplies the receiver by the indicated vector, considered as a column matrix."""
        ...
    @overload
    def multiplied(self, him: list[float]) -> VectorF:
        """Multiplies the receiver by the indicated vector, considered as a column matrix."""
        ...
    def multiplied(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def toVector(self) -> VectorF:
        """If the receiver is one-dimensional in one of its dimensions, returns a vector containing the data of the receiver; otherwise, an exception is thrown."""
        ...

    @overload
    def added(self, addend: MatrixF) -> MatrixF:
        """Returns a new matrix whose elements are the sum of the corresponding elements of the receiver and the addend"""
        ...
    @overload
    def added(self, him: VectorF) -> MatrixF:
        ...
    @overload
    def added(self, him: list[float]) -> MatrixF:
        ...
    def added(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def add(self, addend: MatrixF) -> None:
        """Adds a matrix, in place, to the receiver"""
        ...
    @overload
    def add(self, him: VectorF) -> None:
        ...
    @overload
    def add(self, him: list[float]) -> None:
        ...
    def add(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def subtracted(self, subtrahend: MatrixF) -> MatrixF:
        """Returns a new matrix whose elements are the difference of the corresponding elements of the receiver and the subtrahend"""
        ...
    @overload
    def subtracted(self, him: VectorF) -> MatrixF:
        ...
    @overload
    def subtracted(self, him: list[float]) -> MatrixF:
        ...
    def subtracted(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def subtract(self, subtrahend: MatrixF) -> None:
        """Subtracts a matrix, in place, from the receiver."""
        ...
    @overload
    def subtract(self, him: VectorF) -> None:
        ...
    @overload
    def subtract(self, him: list[float]) -> None:
        ...
    def subtract(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getTranslation(self) -> VectorF:
        """Assumes that the receiver is non-perspective transformation matrix. Returns the translation component of the transformation."""
        ...

    @overload
    def dimensionsError(self) -> Any:
        ...
    @overload
    @staticmethod
    def dimensionsError(numRows: int, numCols: int) -> Any:
        ...
    def dimensionsError(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def inverted(self) -> MatrixF:
        """Returns a matrix which is the matrix-multiplication inverse of the receiver."""
        ...

    numRows_: int
    numCols_: int


class SliceMatrixF(MatrixF):
    """A SliceMatrixF is a matrix whose implementation is a submatrix of some other matrix."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.SliceMatrixF"
    def __init__(self, matrix: MatrixF, row: int, col: int, numRows: int, numCols: int) -> None:
        """Creates a SliceMatrixF based on the indicated matrix whose upper left corner is at (row, col) of that matrix and whose size is numRows x numCols."""
        ...

    def get(self, row: int, col: int) -> float:
        ...

    def put(self, row: int, col: int, value: float) -> None:
        ...

    def emptyMatrix(self, numRows: int, numCols: int) -> MatrixF:
        ...

    matrix: MatrixF
    row: int
    col: int


class WebObserver:
    """WebObserver instances like to observe (rather than handle) web traffic as it goes buy"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.WebObserver"
    def observe(self, session: NanoHTTPD.IHTTPSession) -> None:
        ...


class NanoHTTPD:
    """A simple, tiny, nicely embeddable HTTP server in Java"""
    __java__ = "fi.iki.elonen.NanoHTTPD"
    class TempFileManagerFactory:
        """Factory to create temp file managers."""
        __java__ = "fi.iki.elonen.NanoHTTPD.TempFileManagerFactory"
        def create(self) -> NanoHTTPD.TempFileManager:
            ...

    class IHTTPSession:
        """Handles one session, i.e. parses the HTTP request and returns the response."""
        __java__ = "fi.iki.elonen.NanoHTTPD.IHTTPSession"
        def execute(self) -> None:
            ...

        def getCookies(self) -> NanoHTTPD.CookieHandler:
            ...

        def getHeaders(self) -> dict[str, str]:
            ...

        def getInputStream(self) -> Any:
            ...

        def getMethod(self) -> NanoHTTPD.Method:
            ...

        def getParms(self) -> dict[str, str]:
            """This method will only return the first value for a given parameter. You will want to use getParameters if you expect multiple values for a given key."""
            ...

        def getParameters(self) -> dict[str, list[str]]:
            ...

        def getQueryParameterString(self) -> str:
            ...

        def getUri(self) -> str:
            ...

        def parseBody(self, files: dict[str, str]) -> None:
            """Adds the files in the request body to the files map."""
            ...

        def getRemoteIpAddress(self) -> str:
            """Get the remote ip address of the requester."""
            ...

        def getRemoteHostName(self) -> str:
            """Get the remote hostname of the requester."""
            ...

    class ServerSocketFactory:
        """Factory to create ServerSocketFactories."""
        __java__ = "fi.iki.elonen.NanoHTTPD.ServerSocketFactory"
        def create(self) -> Any:
            ...

    class AsyncRunner:
        """Pluggable strategy for asynchronously executing requests."""
        __java__ = "fi.iki.elonen.NanoHTTPD.AsyncRunner"
        def closeAll(self) -> None:
            ...

        def closed(self, clientHandler: NanoHTTPD.ClientHandler) -> None:
            ...

        def exec(self, code: NanoHTTPD.ClientHandler) -> None:
            ...

    class Response:
        """HTTP response. Return one of these from serve()."""
        __java__ = "fi.iki.elonen.NanoHTTPD.Response"
        class IStatus:
            __java__ = "fi.iki.elonen.NanoHTTPD.Response.IStatus"
            def getDescription(self) -> str:
                ...

            def getRequestStatus(self) -> int:
                ...

        def __init__(self, status: NanoHTTPD.Response.IStatus, mimeType: str, data: Any, totalBytes: int) -> None:
            """Creates a fixed length response if totalBytes&gt;=0, otherwise chunked."""
            ...

        def close(self) -> None:
            ...

        def addHeader(self, name: str, value: str) -> None:
            """Adds given line to the header."""
            ...

        def closeConnection(self, close: bool) -> None:
            """Indicate to close the connection after the Response has been sent."""
            ...

        def isCloseConnection(self) -> bool:
            ...

        def getData(self) -> Any:
            ...

        def getHeader(self, name: str) -> str:
            ...

        def getMimeType(self) -> str:
            ...

        def getRequestMethod(self) -> NanoHTTPD.Method:
            ...

        def getStatus(self) -> NanoHTTPD.Response.IStatus:
            ...

        def setGzipEncoding(self, encodeAsGzip: bool) -> None:
            ...

        def setKeepAlive(self, useKeepAlive: bool) -> None:
            ...

        def send(self, outputStream: Any) -> None:
            """Sends given response to the socket."""
            ...

        def printHeader(self, pw: Any, key: str, value: str) -> None:
            ...

        def sendContentLengthHeaderIfNotAlreadyPresent(self, pw: Any, defaultSize: int) -> int:
            ...

        def setChunkedTransfer(self, chunkedTransfer: bool) -> None:
            ...

        def setData(self, data: Any) -> None:
            ...

        def setMimeType(self, mimeType: str) -> None:
            ...

        def setRequestMethod(self, requestMethod: NanoHTTPD.Method) -> None:
            ...

        def setStatus(self, status: NanoHTTPD.Response.IStatus) -> None:
            ...

    class CookieHandler:
        """Provides rudimentary support for cookies. Doesn't support 'path', 'secure' nor 'httpOnly'. Feel free to improve it and/or add unsupported features."""
        __java__ = "fi.iki.elonen.NanoHTTPD.CookieHandler"
        def __init__(self, httpHeaders: dict[str, str]) -> None:
            ...

        def delete(self, name: str) -> None:
            """Set a cookie with an expiration date from a month ago, effectively deleting it on the client side."""
            ...

        def iterator(self) -> Any:
            ...

        def read(self, name: str) -> str:
            """Read a cookie from the HTTP Headers."""
            ...

        @overload
        def set(self, cookie: NanoHTTPD.Cookie) -> None:
            ...
        @overload
        def set(self, name: str, value: str, expires: int) -> None:
            """Sets a cookie."""
            ...
        def set(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def unloadQueue(self, response: NanoHTTPD.Response) -> None:
            """Internally used by the webserver to add all queued cookies into the Response's HTTP Headers."""
            ...

    class Cookie:
        __java__ = "fi.iki.elonen.NanoHTTPD.Cookie"
        @overload
        def __init__(self, name: str, value: str) -> None:
            ...
        @overload
        def __init__(self, name: str, value: str, numDays: int) -> None:
            ...
        @overload
        def __init__(self, name: str, value: str, expires: str) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        @staticmethod
        def getHTTPTime(days: int) -> str:
            ...

        def getHTTPHeader(self) -> str:
            ...

        n: str
        v: str
        e: str

    class TempFileManager:
        """Temp file manager."""
        __java__ = "fi.iki.elonen.NanoHTTPD.TempFileManager"
        def clear(self) -> None:
            ...

        def createTempFile(self, filename_hint: str) -> NanoHTTPD.TempFile:
            ...

    class TempFile:
        """A temp file."""
        __java__ = "fi.iki.elonen.NanoHTTPD.TempFile"
        def delete(self) -> None:
            ...

        def getName(self) -> str:
            ...

        def open(self) -> Any:
            ...

    class ClientHandler:
        """The runnable that will be used for every new client connection."""
        __java__ = "fi.iki.elonen.NanoHTTPD.ClientHandler"
        def __init__(self, inputStream: Any, acceptSocket: Any) -> None:
            ...

        def close(self) -> None:
            ...

        def run(self) -> None:
            ...

    class Method(enum.Enum):
        """HTTP Request methods, with the ability to decode a String back to its enum value."""
        __java__ = "fi.iki.elonen.NanoHTTPD.Method"
        GET = enum.auto()
        PUT = enum.auto()
        POST = enum.auto()
        DELETE = enum.auto()
        HEAD = enum.auto()
        OPTIONS = enum.auto()
        TRACE = enum.auto()
        CONNECT = enum.auto()
        PATCH = enum.auto()
        PROPFIND = enum.auto()
        PROPPATCH = enum.auto()
        MKCOL = enum.auto()
        MOVE = enum.auto()
        COPY = enum.auto()
        LOCK = enum.auto()
        UNLOCK = enum.auto()
        @staticmethod
        def lookup(method: str) -> NanoHTTPD.Method:
            ...

    class ServerRunnable:
        """The runnable that will be used for the main listening thread."""
        __java__ = "fi.iki.elonen.NanoHTTPD.ServerRunnable"
        def __init__(self, timeout: int) -> None:
            ...

        def run(self) -> None:
            ...

    @overload
    def __init__(self, port: int) -> None:
        """Constructs an HTTP server on given port."""
        ...
    @overload
    def __init__(self, hostname: str, port: int) -> None:
        """Constructs an HTTP server on given hostname and port."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def mimeTypes() -> dict[str, str]:
        ...

    @overload
    @staticmethod
    def makeSSLSocketFactory(loadedKeyStore: Any, keyManagers: list[Any]) -> Any:
        """Creates an SSLSocketFactory for HTTPS. Pass a loaded KeyStore and an array of loaded KeyManagers. These objects must properly loaded/initialized by the caller."""
        ...
    @overload
    @staticmethod
    def makeSSLSocketFactory(loadedKeyStore: Any, loadedKeyFactory: Any) -> Any:
        """Creates an SSLSocketFactory for HTTPS. Pass a loaded KeyStore and a loaded KeyManagerFactory. These objects must properly loaded/initialized by the caller."""
        ...
    @overload
    @staticmethod
    def makeSSLSocketFactory(keyAndTrustStoreClasspathPath: str, passphrase: list[str]) -> Any:
        """Creates an SSLSocketFactory for HTTPS. Pass a KeyStore resource with your certificate and passphrase"""
        ...
    @staticmethod
    def makeSSLSocketFactory(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def getMimeTypeForFile(uri: str) -> str:
        """Get MIME type from file name extension, if possible"""
        ...

    def closeAllConnections(self) -> None:
        """Forcibly closes all connections that are open."""
        ...

    def createClientHandler(self, finalAccept: Any, inputStream: Any) -> NanoHTTPD.ClientHandler:
        """create a instance of the client handler, subclasses can return a subclass of the ClientHandler."""
        ...

    def createServerRunnable(self, timeout: int) -> NanoHTTPD.ServerRunnable:
        """Instantiate the server runnable, can be overwritten by subclasses to provide a subclass of the ServerRunnable."""
        ...

    @overload
    @staticmethod
    def decodeParameters(parms: dict[str, str]) -> dict[str, list[str]]:
        """Decode parameters from a URL, handing the case where a single parameter name might have been supplied several times, by return lists of values. In general these lists will contain a single element."""
        ...
    @overload
    @staticmethod
    def decodeParameters(queryString: str) -> dict[str, list[str]]:
        """Decode parameters from a URL, handing the case where a single parameter name might have been supplied several times, by return lists of values. In general these lists will contain a single element."""
        ...
    @staticmethod
    def decodeParameters(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def decodePercent(str: str) -> str:
        """Decode percent encoded String values."""
        ...

    def useGzipWhenAccepted(self, r: NanoHTTPD.Response) -> bool:
        ...

    def getListeningPort(self) -> int:
        ...

    def isAlive(self) -> bool:
        ...

    def getServerSocketFactory(self) -> NanoHTTPD.ServerSocketFactory:
        ...

    def setServerSocketFactory(self, serverSocketFactory: NanoHTTPD.ServerSocketFactory) -> None:
        ...

    def getHostname(self) -> str:
        ...

    def getTempFileManagerFactory(self) -> NanoHTTPD.TempFileManagerFactory:
        ...

    def makeSecure(self, sslServerSocketFactory: Any, sslProtocols: list[str]) -> None:
        """Call before start() to serve over HTTPS instead of HTTP"""
        ...

    @staticmethod
    def newChunkedResponse(status: NanoHTTPD.Response.IStatus, mimeType: str, data: Any) -> NanoHTTPD.Response:
        """Create a response with unknown length (using HTTP 1.1 chunking)."""
        ...

    @overload
    @staticmethod
    def newFixedLengthResponse(status: NanoHTTPD.Response.IStatus, mimeType: str, data: Any, totalBytes: int) -> NanoHTTPD.Response:
        """Create a response with known length."""
        ...
    @overload
    @staticmethod
    def newFixedLengthResponse(status: NanoHTTPD.Response.IStatus, mimeType: str, txt: str) -> NanoHTTPD.Response:
        """Create a text response with known length."""
        ...
    @overload
    @staticmethod
    def newFixedLengthResponse(msg: str) -> NanoHTTPD.Response:
        """Create a text response with known length."""
        ...
    @staticmethod
    def newFixedLengthResponse(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def serve(self, session: NanoHTTPD.IHTTPSession) -> NanoHTTPD.Response:
        """Override this to customize the server. (By default, this returns a 404 \"Not Found\" plain text error response.)"""
        ...
    @overload
    def serve(self, uri: str, method: NanoHTTPD.Method, headers: dict[str, str], parms: dict[str, str], files: dict[str, str]) -> NanoHTTPD.Response:
        """Override this to customize the server. (By default, this returns a 404 \"Not Found\" plain text error response.)"""
        ...
    def serve(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setAsyncRunner(self, asyncRunner: NanoHTTPD.AsyncRunner) -> None:
        """Pluggable strategy for asynchronously executing requests."""
        ...

    def setTempFileManagerFactory(self, tempFileManagerFactory: NanoHTTPD.TempFileManagerFactory) -> None:
        """Pluggable strategy for creating and cleaning up temporary files."""
        ...

    @overload
    def start(self) -> None:
        """Start the server."""
        ...
    @overload
    def start(self, timeout: int) -> None:
        """Starts the server (in setDaemon(true) mode)."""
        ...
    @overload
    def start(self, timeout: int, daemon: bool) -> None:
        """Start the server."""
        ...
    def start(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def stop(self) -> None:
        """Stop the server."""
        ...

    def wasStarted(self) -> bool:
        ...

    SOCKET_READ_TIMEOUT: int
    """Maximum time to wait on Socket.getInputStream().read() (in milliseconds) This is required as the Keep-Alive HTTP connections would otherwise block the socket reading thread forever (or as long the browser is open)."""
    MIME_PLAINTEXT: str
    """Common MIME type for dynamic content: plain text"""
    MIME_HTML: str
    """Common MIME type for dynamic content: html"""
    MIME_TYPES: dict[str, str]
    """Hashtable mapping (String)FILENAME_EXTENSION -&gt; (String)MIME_TYPE"""
    asyncRunner: NanoHTTPD.AsyncRunner
    """Pluggable strategy for asynchronously executing requests."""


def ExpansionHubPIDFPositionParams(*, P: float, algorithm: MotorControlAlgorithm) -> Callable[[type], type]:
    """When ExpansionHubPIDFPositionParams annotations are placed on a motor type, the indicated PIDF coefficients are automatically initialized when instances of that motor are used."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class GamepadUser(enum.Enum):
    """A *typed* integer so that we can more easily keep track of things"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.ui.GamepadUser"
    ONE = enum.auto()
    TWO = enum.auto()
    @staticmethod
    def from_(user: int) -> GamepadUser:
        ...

    id: int


class Consumer(Generic[T]):
    """Instances of Consumer are functions that act on an instance of a indicated type"""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.Consumer"
    def accept(self, value: T) -> None:
        """Performs this operation on the given argument."""
        ...


class AnalogSensorConfigurationType(InstantiableUserConfigurationType):
    """AnalogSensorConfigurationType contains the meta-data for a user-defined analog sensor driver."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.AnalogSensorConfigurationType"
    @overload
    def __init__(self, clazz: type[HardwareDevice], xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def createInstances(self, controller: AnalogInputController, port: int) -> list[HardwareDevice]:
        ...


class TimeWindow:
    """TimeWindow represents an interval in time on the System nanotime clock"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.hardware.TimeWindow"
    def __init__(self) -> None:
        ...

    def clear(self) -> None:
        ...

    def isCleared(self) -> bool:
        ...

    def setNanosecondsFirst(self, nsFirst: int) -> None:
        ...

    def setNanosecondsLast(self, nsLast: int) -> None:
        ...

    def getNanosecondsFirst(self) -> int:
        ...

    def getNanosecondsLast(self) -> int:
        ...

    nsFirst: int
    nsLast: int


class LynxDatagram:
    """A LynxDatagram represents the quantum of transmission of Lynx data between host and controller module."""
    __java__ = "com.qualcomm.hardware.lynx.commands.LynxDatagram"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, command: LynxMessage) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @overload
    @staticmethod
    def beginsWithFraming(data: list[int]) -> bool:
        """Does the indicated data begin with the framing bytes?"""
        ...
    @overload
    @staticmethod
    def beginsWithFraming(buffer: Any) -> bool:
        ...
    @staticmethod
    def beginsWithFraming(*args: Any, **kwargs: Any) -> Any:
        ...

    def setPayloadTimeWindow(self, payloadTimeWindow: TimeWindow) -> None:
        ...

    def getPayloadTimeWindow(self) -> TimeWindow:
        ...

    def getPacketLength(self) -> int:
        ...

    def setPacketLength(self, value: int) -> None:
        ...

    @staticmethod
    def getFixedPacketLength() -> int:
        ...

    def updatePacketLength(self) -> int:
        ...

    def getDestModuleAddress(self) -> int:
        ...

    def setDestModuleAddress(self, value: int) -> None:
        ...

    def getSourceModuleAddress(self) -> int:
        ...

    def setSourceModuleAddress(self, value: int) -> None:
        ...

    def getMessageNumber(self) -> int:
        ...

    def setMessageNumber(self, value: int) -> None:
        ...

    def getReferenceNumber(self) -> int:
        ...

    def setReferenceNumber(self, value: int) -> None:
        ...

    def getPacketId(self) -> int:
        ...

    def setPacketId(self, value: int) -> None:
        ...

    def isResponse(self) -> bool:
        ...

    def getCommandNumber(self) -> int:
        """Note that we clear the response bit."""
        ...

    def getPayloadData(self) -> list[int]:
        ...

    def setPayloadData(self, data: list[int]) -> None:
        ...

    def getChecksum(self) -> int:
        ...

    def setChecksum(self, value: int) -> None:
        ...

    def computeChecksum(self) -> int:
        ...

    def isChecksumValid(self) -> bool:
        ...

    def toByteArray(self) -> list[int]:
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        ...

    LYNX_ENDIAN: Any
    """All integral data is exchanged in 'little endian' format, least significant byte first (at lowest address/offset."""
    cbFrameBytesAndPacketLength: int
    """How much are the frame bytes and packet length accounted for in the overall packet length?"""
    frameBytes: list[int]
    """Two particular bytes identify the start of a valid Controller Module data packet"""


class LynxAck(LynxMessage):
    """Created by bob on 2016-02-26. Example: 44 4B 0C 00 00 01 07 6B 01 7F 01 8F D K len=12 to from # ref# ack attn chksum"""
    __java__ = "com.qualcomm.hardware.lynx.commands.standard.LynxAck"
    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, isAttentionRequired: bool) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def isAttentionRequired(self) -> bool:
        ...

    @staticmethod
    def getStandardCommandNumber() -> int:
        ...

    def getCommandNumber(self) -> int:
        ...

    def toPayloadByteArray(self) -> list[int]:
        ...

    def fromPayloadByteArray(self, rgb: list[int]) -> None:
        ...

    def isAck(self) -> bool:
        ...

    def isDangerous(self) -> bool:
        ...


class CameraCaptureRequest:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. CameraCaptureRequest represents a block of specified parameters that can be used for capturing frames of images."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureRequest"
    def getAndroidFormat(self) -> int:
        """Returns Android android.graphics.ImageFormat or android.graphics.PixelFormat associated with this request."""
        ...

    def getSize(self) -> Size:
        """Returns the dimensions of the data retrieved by this request"""
        ...

    def getNsFrameDuration(self) -> int:
        """Returns the duration of frames returned by this request, in nanoseconds."""
        ...

    def getFramesPerSecond(self) -> int:
        """Returns the number of frames per second desired by this request"""
        ...

    def createEmptyBitmap(self) -> Any:
        """Returns an empty bitmap which is compatible with this capture request. The contents of a CameraFrame can be transferred to this bitmap using CameraFrame#copyToBitmap(Bitmap)."""
        ...


class ConstructorPrototype:
    """Class that represents a constructor's form"""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ConstructorPrototype"
    def __init__(self, *prototypeParameterTypes: type[object]) -> None:
        """Constructor"""
        ...

    def matches(self, constructor: Any) -> bool:
        """Returns true if the constructor matches this prototype"""
        ...

    prototypeParameterTypes: list[type[object]]


class WebSocketManager:
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.WebSocketManager"
    def registerNamespaceHandler(self, handler: WebSocketNamespaceHandler) -> None:
        """Register a namespace handler. All received messages with a namespace matching handler.getNamespace() will be forwarded to the handler."""
        ...

    def registerNamespaceAsBroadcastOnly(self, namespace: str) -> None:
        """Register a namespace as broadcast-only. You can broadcast to it from Java, and js clients can subscribe to it, but any messages that the client sends will be logged and ignored."""
        ...

    def broadcastToNamespace(self, namespace: str, message: FtcWebSocketMessage) -> int:
        """Send a message to all WebSockets subscribed to a particular namespace"""
        ...

    def webSocketIsSubscribedToNamespace(self, namespace: str, webSocket: FtcWebSocket) -> bool:
        """Determine if a particular WebSocket is subscribed to a given namespace"""
        ...

    SYSTEM_NAMESPACE: str
    WEBSOCKET_API_VERSION: int
    """Version of the WebSocket core implementation. This value should be incremented any time a breaking change is made to the core functionality of our websockets (commands and messages). Clients will read this value from rcInfo.json to determine if they are compatible with WebSocket commands and messages."""


class FtcWebSocketMessage:
    """A WebSocket message that conforms to our sub-protocol. Transmitted over the wire as JSON. The payload is transparently converted to and from Base64 during serialization and deserialization, respectively. This ensures that there are no parsing issues when the payload is itself JSON."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.FtcWebSocketMessage"
    @overload
    def __init__(self, namespace: str, type: str) -> None:
        """Create an FtcWebSocketMessage that does not include a payload"""
        ...
    @overload
    def __init__(self, namespace: str, type: str, payload: str) -> None:
        """Create an FtcWebSocketMessage that optionally includes a payload"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def fromJson(json: str) -> FtcWebSocketMessage:
        """Convert a JSON string into an FtcWebSocketMessage"""
        ...

    def toJson(self) -> str:
        """Serialize into a JSON string for network transmission"""
        ...

    def getPayload(self) -> str:
        """Get the payload (may be JSON)"""
        ...

    def getNamespace(self) -> str:
        """Get the namespace"""
        ...

    def getType(self) -> str:
        """Get the message type"""
        ...

    def hasPayload(self) -> bool:
        """Check if the message has a payload"""
        ...

    def toString(self) -> str:
        ...


def ExpansionHubMotorControllerVelocityParams(*, P: float, I: float, D: float) -> Callable[[type], type]:
    """When ExpansionHubMotorControllerVelocityParams annotations are placed on a motor type, the indicated PID coefficients are automatically initialized when instances of that motor are used."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class CameraCaptureSequenceId:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. Identifies a unique capture request."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCaptureSequenceId"
    def getIdValue(self) -> int:
        """Returns the value of the id associated with this sequence. Note that capture sequences from different capture sessions may in fact have overlapping id values."""
        ...


class CameraCharacteristics:
    """THIS INTERFACE IS EXPERIMENTAL. Its form and function may change in whole or in part before being finalized for production use. Caveat emptor. Metadata regarding the configuration of video streams that a camera might produce. Modelled after android.hardware.camera2.params.StreamConfigurationMap, though significantly simplified here."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCharacteristics"
    class CameraMode:
        __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraCharacteristics.CameraMode"
        def __init__(self, androidFormat: int, size: Size, nsFrameDuration: int, isDefaultSize: bool) -> None:
            ...

        def toString(self) -> str:
            ...

        def equals(self, o: object) -> bool:
            ...

        def hashCode(self) -> int:
            ...

        androidFormat: int
        size: Size
        nsFrameDuration: int
        fps: int
        isDefaultSize: bool

    def getAndroidFormats(self) -> list[int]:
        """Get the image format output formats in this camera All image formats returned by this function will be defined in either ImageFormat or in PixelFormat (and there is no possibility of collision)."""
        ...

    def getSizes(self, androidFormat: int) -> list[Size]:
        """Get a list of sizes compatible with the requested image format. The format should be a supported format (one of the formats returned by #getAndroidFormats)."""
        ...

    def getDefaultSize(self, androidFormat: int) -> Size:
        """Gets the device-recommended optimum size for the indicated format"""
        ...

    def getMinFrameDuration(self, androidFormat: int, size: Size) -> int:
        """Get the minimum frame duration for the format/size combination (in nanoseconds). format should be one of the ones returned by #getAndroidFormats(). size should be one of the ones returned by #getSizes(int)."""
        ...

    def getMaxFramesPerSecond(self, androidFormat: int, size: Size) -> int:
        """Returns the maximum fps rate supported for the given format."""
        ...

    def getAllCameraModes(self) -> list[CameraCharacteristics.CameraMode]:
        """Returns all the combinatorial format, size, and fps camera modes supported."""
        ...


class ProgressParameters:
    """ProgressParameters is a utility class for passing information regarding progress towards completing a task."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.ui.ProgressParameters"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, cur: int, max: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def fractionComplete(self) -> float:
        ...

    @overload
    @staticmethod
    def fromFraction(fractionComplete: float, max: int) -> ProgressParameters:
        ...
    @overload
    @staticmethod
    def fromFraction(fractionComplete: float) -> ProgressParameters:
        ...
    @staticmethod
    def fromFraction(*args: Any, **kwargs: Any) -> Any:
        ...

    cur: int
    max: int


class CameraCalibrationIdentity:
    __java__ = "org.firstinspires.ftc.robotcore.internal.camera.calibration.CameraCalibrationIdentity"
    def isDegenerate(self) -> bool:
        ...


class FtcWebSocket:
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.FtcWebSocket"
    def send(self, message: FtcWebSocketMessage) -> None:
        """Send a message to this WebSocket"""
        ...

    def sendCommandResponse(self, response: WebSocketCommandResponse) -> None:
        """Send a command result to this WebSocket."""
        ...

    def getRemoteIpAddress(self) -> Any:
        ...

    def getRemoteHostname(self) -> str:
        ...

    def getPort(self) -> int:
        ...

    def isOpen(self) -> bool:
        ...

    def close(self, closeCode: CloseCode, reason: str) -> None:
        """Close the WebSocket connection"""
        ...


class CloseCode(enum.Enum):
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.CloseCode"
    NORMAL_CLOSURE = enum.auto()
    GOING_AWAY = enum.auto()
    PROTOCOL_ERROR = enum.auto()
    UNSUPPORTED_DATA = enum.auto()
    NO_STATUS_RCVD = enum.auto()
    ABNORMAL_CLOSURE = enum.auto()
    INVALID_FRAME_PAYLOAD_DATA = enum.auto()
    POLICY_VIOLATION = enum.auto()
    MESSAGE_TOO_BIG = enum.auto()
    MANDATORY_EXT = enum.auto()
    INTERNAL_SERVER_ERROR = enum.auto()
    TLS_HANDSHAKE = enum.auto()
    PING_TIMEOUT = enum.auto()
    @staticmethod
    def find(value: int) -> CloseCode:
        ...

    def getValue(self) -> int:
        ...

    def toString(self) -> str:
        ...


class WebSocketCommandResponse:
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.WebSocketCommandResponse"
    @staticmethod
    def createSuccess(commandKey: object, response: str) -> WebSocketCommandResponse:
        """Create a success response to send"""
        ...

    @staticmethod
    def createError(commandKey: object, exception: WebSocketCommandException) -> WebSocketCommandResponse:
        """Create an error response to send"""
        ...

    def getCommandKey(self) -> object:
        ...

    def getResponse(self) -> str:
        ...

    def getError(self) -> str:
        ...

    commandKey: object
    response: str
    error: str


class WebSocketCommandException(Exception):
    """Base class for failures of WebSocket commands. Specify a type that the consumer can use to determine the Exception type."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.WebSocketCommandException"
    def __init__(self, type: str, message: str) -> None:
        ...

    def getType(self) -> str:
        ...

    type: str
    """Type identifier for this exception."""


class EventLoop:
    """Event loop interface"""
    __java__ = "com.qualcomm.robotcore.eventloop.EventLoop"
    def init(self, eventLoopManager: EventLoopManager) -> None:
        """Init method, this will be called before the first call to loop. You should set up your hardware in this method. Threading: called on the RobotSetupRunnable.run() thread, before the EventLoopRunnable.run() thread is created."""
        ...

    def loop(self) -> None:
        """This method will be repeatedly called by the event loop manager. Threading: called on the EventLoopRunnable.run() thread. If an Exception is thrown, it will be handled by the event loop manager. The manager may decide to either stop processing this iteration of the loop, or it may decide to shut down the robot."""
        ...

    def refreshUserTelemetry(self, telemetry: TelemetryMessage, sInterval: float) -> None:
        """Update's the user portion of the driver station screen with the contents of the telemetry object here provided if a sufficiently long duration has passed since the last update."""
        ...

    def teardown(self) -> None:
        """Teardown method, this will be called after the last call to loop. You should place your robot into a safe state before this method exits, since there will be no more changes to communicate with your robot. Threading: called on the EventLoopRunnable.run() thread."""
        ...

    def onUsbDeviceAttached(self, usbDevice: Any) -> None:
        """Notifies the event loop that a UsbDevice has just been attached to the system. User interface activities that receive UsbManager.ACTION_USB_DEVICE_ATTACHED notifications should retrieve the UsbDevice using intent.getParcelableExtra(UsbManager.EXTRA_DEVICE) then pass that along to this method in their event loop for processing."""
        ...

    def pendUsbDeviceAttachment(self, serialNumber: SerialNumber, time: int, unit: Any) -> None:
        ...

    def processedRecentlyAttachedUsbDevices(self) -> None:
        """Process the batch of newly arrived USB devices. This is called on the EventLoop thread by the EventLoopManager; there is sufficient time and correct context to, e.g., fully arm the associated module software to make the device operational within the app."""
        ...

    def handleUsbModuleDetach(self, module: RobotUsbModule) -> None:
        """Process the fact that a usb module has now become detached from the system. This is called on the EventLoop thread by the EventLoopManager; there is sufficient time and correct context to, e.g., fully disarm and 'pretend' the associated module."""
        ...

    def handleUsbModuleAttach(self, module: RobotUsbModule) -> None:
        """Process the fact that (we believe) that the indicated module has now reappeared after a previously observed detachment."""
        ...

    def processCommand(self, command: Command) -> CallbackResult:
        """Process command method, this will be called if the event loop manager receives a user defined command. How this command is handled is up to the event loop implementation. Threading: called on the RecvRunnable.run() thread."""
        ...

    def getOpModeManager(self) -> OpModeManagerImpl:
        """Returns the OpModeManager associated with this event loop"""
        ...

    def requestOpModeStop(self, opModeToStopIfActive: OpMode) -> None:
        """Requests that an OpMode be stopped if it's the currently active one"""
        ...

    TELEMETRY_DEFAULT_INTERVAL: float
    """The value to pass to #refreshUserTelemetry(TelemetryMessage, as the time interval parameter in order to cause a system default interval to be used."""


class CallbackResult(enum.Enum):
    """CallbackResult is typically returned by members of an event handling chain to indicate whether the function processed the result (and so chain propagation should cease) or not."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.network.CallbackResult"
    NOT_HANDLED = enum.auto()
    HANDLED = enum.auto()
    HANDLED_CONTINUE = enum.auto()
    def isHandled(self) -> bool:
        ...

    def stopDispatch(self) -> bool:
        ...


class RobocolDatagramSocket:
    """Multi-threaded datagram socket with non-blocking IO."""
    __java__ = "com.qualcomm.robotcore.robocol.RobocolDatagramSocket"
    class State(enum.Enum):
        __java__ = "com.qualcomm.robotcore.robocol.RobocolDatagramSocket.State"
        LISTENING = enum.auto()
        CLOSED = enum.auto()
        ERROR = enum.auto()

    def __init__(self) -> None:
        ...

    def listenUsingDestination(self, destAddress: Any) -> None:
        ...

    def bind(self, bindAddress: Any) -> None:
        ...

    def close(self) -> None:
        ...

    def send(self, message: RobocolDatagram) -> None:
        ...

    def recv(self) -> RobocolDatagram:
        """Receive a RobocolDatagram packet"""
        ...

    def gatherTrafficData(self, enable: bool) -> None:
        ...

    def getRxDataSample(self) -> int:
        ...

    def getTxDataSample(self) -> int:
        ...

    def getRxDataCount(self) -> int:
        ...

    def getTxDataCount(self) -> int:
        ...

    def resetDataSample(self) -> None:
        ...

    def getState(self) -> RobocolDatagramSocket.State:
        ...

    def getInetAddress(self) -> Any:
        ...

    def getLocalAddress(self) -> Any:
        ...

    def isRunning(self) -> bool:
        ...

    def isClosed(self) -> bool:
        ...

    TAG: str


class RobocolDatagram:
    """RobocolDatagram Used by RobocolServer and RobocolClient to pass messages."""
    __java__ = "com.qualcomm.robotcore.robocol.RobocolDatagram"
    def __init__(self, message: RobocolParsable, destination: Any) -> None:
        """Construct a RobocolDatagram from a RobocolParsable"""
        ...

    @staticmethod
    def forReceive(receiveBufferSize: int) -> RobocolDatagram:
        """Returns a RobocolDatagram suitable for use in socket receives. We pay particular attention here to avoiding allocating too many buffers, fearing an impact on the GC, as the buffers are relatively large-ish."""
        ...

    def close(self) -> None:
        """Clients are done with this message. If it has a socket receive buffer, then scavenge that."""
        ...

    def getMsgType(self) -> RobocolParsable.MsgType:
        """Get the message type"""
        ...

    def getLength(self) -> int:
        """Get the size of this RobocolDatagram, in bytes"""
        ...

    def getPayloadLength(self) -> int:
        """Get the size of the payload, in bytes"""
        ...

    def getData(self) -> list[int]:
        """Gets the payload of this datagram packet"""
        ...

    def getAddress(self) -> Any:
        ...

    def getPort(self) -> int:
        ...

    def getWallClockTimeMsReceived(self) -> int:
        ...

    def getNanoTimeReceived(self) -> int:
        ...

    def setAddress(self, address: Any) -> None:
        ...

    def toString(self) -> str:
        ...

    def getPacket(self) -> Any:
        ...

    def setPacket(self, packet: Any) -> None:
        ...

    def markReceivedNow(self) -> None:
        ...

    TAG: str
    receiveBuffers: list[list[int]]
    """the place we put old receive buffers"""


class NetworkType(enum.Enum):
    __java__ = "com.qualcomm.robotcore.wifi.NetworkType"
    WIFIDIRECT = enum.auto()
    LOOPBACK = enum.auto()
    SOFTAP = enum.auto()
    WIRELESSAP = enum.auto()
    RCWIRELESSAP = enum.auto()
    UNKNOWN_NETWORK_TYPE = enum.auto()
    @staticmethod
    def fromString(type: str) -> NetworkType:
        ...

    @staticmethod
    def globalDefault() -> NetworkType:
        ...

    @staticmethod
    def globalDefaultAsString() -> str:
        ...


class ApChannel(enum.Enum):
    __java__ = "org.firstinspires.ftc.robotcore.internal.network.ApChannel"
    UNKNOWN = enum.auto()
    AUTO_2_4_GHZ = enum.auto()
    AUTO_5_GHZ = enum.auto()
    CHAN_1 = enum.auto()
    CHAN_2 = enum.auto()
    CHAN_3 = enum.auto()
    CHAN_4 = enum.auto()
    CHAN_5 = enum.auto()
    CHAN_6 = enum.auto()
    CHAN_7 = enum.auto()
    CHAN_8 = enum.auto()
    CHAN_9 = enum.auto()
    CHAN_10 = enum.auto()
    CHAN_11 = enum.auto()
    CHAN_36 = enum.auto()
    CHAN_40 = enum.auto()
    CHAN_44 = enum.auto()
    CHAN_48 = enum.auto()
    CHAN_149 = enum.auto()
    CHAN_153 = enum.auto()
    CHAN_157 = enum.auto()
    CHAN_161 = enum.auto()
    CHAN_165 = enum.auto()
    CHAN_52 = enum.auto()
    CHAN_56 = enum.auto()
    CHAN_60 = enum.auto()
    CHAN_64 = enum.auto()
    CHAN_100 = enum.auto()
    CHAN_104 = enum.auto()
    CHAN_108 = enum.auto()
    CHAN_112 = enum.auto()
    CHAN_116 = enum.auto()
    CHAN_120 = enum.auto()
    CHAN_124 = enum.auto()
    CHAN_128 = enum.auto()
    CHAN_132 = enum.auto()
    CHAN_136 = enum.auto()
    CHAN_140 = enum.auto()
    def getDisplayName(self) -> str:
        ...

    @staticmethod
    def fromName(name: str) -> ApChannel:
        """Gets an ApChannel instance from an ApChannel enum value name"""
        ...

    @staticmethod
    def fromBandAndChannel(band: int, channelNum: int) -> ApChannel:
        """Gets an ApChannel instance from a band and channel"""
        ...

    ALL_2_4_GHZ_CHANNELS: Any
    NON_DFS_5_GHZ_CHANNELS: Any
    AP_BAND_2GHZ: int
    AP_BAND_5GHZ: int
    overlapsWithOtherChannels: bool
    channelNum: int
    band: Any


class RobotCoreCommandList:
    """RobotCoreCommandList contains network commands that are accessible in the RobotCore module"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.network.RobotCoreCommandList"
    class LynxFirmwareUpdateResp:
        __java__ = "org.firstinspires.ftc.robotcore.internal.network.RobotCoreCommandList.LynxFirmwareUpdateResp"
        def serialize(self) -> str:
            ...

        @staticmethod
        def deserialize(serialized: str) -> RobotCoreCommandList.LynxFirmwareUpdateResp:
            ...

        success: bool
        errorMessage: str
        originatorId: str

    class FWImage:
        """For the moment (perhaps forever), firmware images can only either be files or assets"""
        __java__ = "org.firstinspires.ftc.robotcore.internal.network.RobotCoreCommandList.FWImage"
        def __init__(self, file: Any, isAsset: bool) -> None:
            ...

        def getName(self) -> str:
            ...

        file: Any
        isAsset: bool

    CMD_SHOW_TOAST: str
    CMD_SHOW_PROGRESS: str
    CMD_DISMISS_PROGRESS: str
    CMD_SHOW_STACKTRACE: str
    CMD_SHOW_DIALOG: str
    CMD_DISMISS_ALL_DIALOGS: str
    CMD_DISMISS_DIALOG: str
    CMD_REQUEST_INSPECTION_REPORT: str
    CMD_REQUEST_INSPECTION_REPORT_RESP: str
    CMD_REQUEST_PARTICULAR_CONFIGURATION: str
    CMD_REQUEST_PARTICULAR_CONFIGURATION_RESP: str
    CMD_DISABLE_BLUETOOTH: str
    CMD_REQUEST_ABOUT_INFO: str
    CMD_REQUEST_ABOUT_INFO_RESP: str
    CMD_NOTIFY_INIT_OP_MODE: str
    CMD_NOTIFY_RUN_OP_MODE: str
    CMD_REQUEST_ACTIVE_CONFIG: str
    CMD_REQUEST_USER_DEVICE_TYPES: str
    CMD_REQUEST_OP_MODE_LIST: str
    CMD_NOTIFY_ACTIVE_CONFIGURATION: str
    CMD_NOTIFY_OP_MODE_LIST: str
    CMD_NOTIFY_USER_DEVICE_LIST: str
    CMD_NOTIFY_ROBOT_STATE: str
    CMD_ROBOT_CONTROLLER_PREFERENCE: str
    CMD_CLEAR_REMEMBERED_GROUPS: str
    CMD_NOTIFY_WIFI_DIRECT_REMEMBERED_GROUPS_CHANGED: str
    CMD_DISCONNECT_FROM_WIFI_DIRECT: str
    CMD_VISUALLY_CONFIRM_WIFI_RESET: str
    CMD_VISUALLY_CONFIRM_WIFI_BAND_SWITCH: str
    CMD_GET_CANDIDATE_LYNX_FIRMWARE_IMAGES: str
    CMD_GET_CANDIDATE_LYNX_FIRMWARE_IMAGES_RESP: str
    CMD_GET_USB_ACCESSIBLE_LYNX_MODULES: str
    CMD_GET_USB_ACCESSIBLE_LYNX_MODULES_RESP: str
    CMD_LYNX_FIRMWARE_UPDATE: str
    CMD_LYNX_FIRMWARE_UPDATE_RESP: str
    """This class should be considered a part of the public JSON API exposed via the webserver"""
    CMD_STREAM_CHANGE: str
    CMD_REQUEST_FRAME: str
    CMD_RECEIVE_FRAME_BEGIN: str
    CMD_RECEIVE_FRAME_CHUNK: str
    CMD_SET_TELEMETRY_DISPLAY_FORMAT: str
    CMD_RUMBLE_GAMEPAD: str
    CMD_GAMEPAD_LED_EFFECT: str
    CMD_TEXT_TO_SPEECH: str


class LynxI2cConfigureChannelCommand(LynxDekaInterfaceCommand[LynxAck]):
    """Created by bob on 2016-09-01."""
    __java__ = "com.qualcomm.hardware.lynx.commands.core.LynxI2cConfigureChannelCommand"
    class SpeedCode(enum.Enum):
        __java__ = "com.qualcomm.hardware.lynx.commands.core.LynxI2cConfigureChannelCommand.SpeedCode"
        UNKNOWN = enum.auto()
        STANDARD_100K = enum.auto()
        FAST_400K = enum.auto()
        FASTPLUS_1M = enum.auto()
        HIGH_3_4M = enum.auto()
        @staticmethod
        def fromByte(bVal: int) -> LynxI2cConfigureChannelCommand.SpeedCode:
            ...

        bVal: int

    @overload
    def __init__(self, module: LynxModuleIntf) -> None:
        ...
    @overload
    def __init__(self, module: LynxModuleIntf, busZ: int, speedCode: LynxI2cConfigureChannelCommand.SpeedCode) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getSpeedCode(self) -> LynxI2cConfigureChannelCommand.SpeedCode:
        ...

    def toPayloadByteArray(self) -> list[int]:
        ...

    def fromPayloadByteArray(self, rgb: list[int]) -> None:
        ...

    def isDangerous(self) -> bool:
        ...

    cbPayload: int


def DistributorInfo(*, distributor: str = '', model: str = '', url: str = '') -> Callable[[type], type]:
    """DistributorInfo is an annotation by which the distribution source of a class representing a commercial product can be annotated."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class WebSocketNamespaceHandler:
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.WebSocketNamespaceHandler"
    @overload
    def __init__(self, namespace: str) -> None:
        """Simple constructor"""
        ...
    @overload
    def __init__(self, namespace: str, prepopulatedMessageTypeHandlerMap: dict[str, WebSocketMessageTypeHandler]) -> None:
        """Constructor with parameter for a map of message type handlers. Can be used as an alternative to overriding #registerMessageTypeHandlers(Map)"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def registerMessageTypeHandlers(self, messageTypeHandlerMap: dict[str, WebSocketMessageTypeHandler]) -> None:
        """Register handlers for particular method types by overriding this method and adding to messageTypeHandlerMap. Use the message type as the key, and the handler as the value. This should be called ONLY from the WebSocketNamespaceHandler constructor."""
        ...

    def onMessage(self, message: FtcWebSocketMessage, webSocket: FtcWebSocket) -> bool:
        """This will be called when a client sends a message with the registered namespace. It may be called from any thread."""
        ...

    def onSubscribe(self, webSocket: FtcWebSocket) -> None:
        """This will be called when a client subscribes to the registered namespace. It may be called from any thread."""
        ...

    def onUnsubscribe(self, webSocket: FtcWebSocket) -> None:
        """This will be called when a client unsubscribes from the registered namespace. This includes when the WebSocket connected to a subscribed client closes. This may be called from any thread."""
        ...

    def getNamespace(self) -> str:
        """Specifies the namespace that this handler will handle the messages of"""
        ...


class WebSocketMessageTypeHandler:
    """Instances of WebSocketMessageTypeHandler can handle a WebSocketMessage of a particular namespace and type"""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.websockets.WebSocketMessageTypeHandler"
    def handleMessage(self, message: FtcWebSocketMessage, webSocket: FtcWebSocket) -> None:
        ...


class WebHandler:
    """Interface for implementing how a request is handled, and subsequently what response is returned."""
    __java__ = "org.firstinspires.ftc.robotcore.internal.webserver.WebHandler"
    def getResponse(self, session: NanoHTTPD.IHTTPSession) -> NanoHTTPD.Response:
        """Return a Response from a request."""
        ...


class ConfigurationUtility:
    """ConfigurationUtility is a utility class containing methods for construction and initializing various types of DeviceConfiguration. This is used in two contexts: constructing entirely new XML configurations in the configuration UI, and during reading of an existing XML configuration, where it's used to reconstitute fully flushed out configurations, since we only *store* the parts of a configuration which are actually populated."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ConfigurationUtility"
    def __init__(self) -> None:
        ...

    def resetNameUniquifiers(self) -> None:
        ...

    def getExistingNames(self, configurationType: ConfigurationType) -> set[str]:
        """Historical policy is that all names are in a single flat name space. We could perhaps change that, and it might be an improvement, but that hasn't yet been done."""
        ...

    def noteExistingName(self, configurationType: ConfigurationType, name: str) -> None:
        ...

    @overload
    def createUniqueName(self, configurationType: ConfigurationType, resId: int) -> str:
        ...
    @overload
    def createUniqueName(self, configurationType: ConfigurationType, resId: int, preferredParam: int) -> str:
        ...
    @overload
    def createUniqueName(self, configurationType: ConfigurationType, format: str, preferredParam: int) -> str:
        ...
    @overload
    def createUniqueName(self, configurationType: ConfigurationType, firstChoiceId: int, formatId: int, preferredParam: int) -> str:
        ...
    def createUniqueName(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def buildNewControllerConfiguration(self, serialNumber: SerialNumber, deviceType: DeviceManager.UsbDeviceType, lynxModuleSupplier: Supplier[LynxModuleMetaList]) -> ControllerConfiguration:
        ...

    def buildNewEthernetOverUsbControllerConfiguration(self, serialNumber: SerialNumber) -> ControllerConfiguration:
        ...

    def buildNewWebcam(self, serialNumber: SerialNumber) -> WebcamConfiguration:
        ...

    @overload
    def buildNewLynxUsbDevice(self, serialNumber: SerialNumber, lynxModuleMetaListSupplier: Supplier[LynxModuleMetaList]) -> LynxUsbDeviceConfiguration:
        ...
    @overload
    def buildNewLynxUsbDevice(self, serialNumber: SerialNumber, metas: LynxModuleMetaList) -> LynxUsbDeviceConfiguration:
        ...
    def buildNewLynxUsbDevice(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def buildNewLynxModule(self, moduleAddress: int, parentModuleAddress: int, syntheticImuType: LynxModuleImuType, isEnabled: bool, isEmbeddedControlHubModule: bool) -> LynxModuleConfiguration:
        """To build a parent lynx module, pass the same number to both moduleAddress and parentModuleAddress"""
        ...

    def buildNewServoHub(self, moduleAddress: int, parentModuleAddress: int, isEnabled: bool) -> ServoHubConfiguration:
        ...

    def buildNewEmbeddedLynxUsbDevice(self, deviceManager: DeviceManager) -> LynxUsbDeviceConfiguration:
        """The distinguishing feature of the 'embedded' Lynx USB device is that it is labelled as 'system synthetic', in that we make it up, making sure it's there independent of whether it's been configured in the hardware map or not. We do this so that we can ALWAYS access the functionality of that embedded module, such as its LEDs."""
        ...

    @staticmethod
    def buildEmptyDevices(initialPort: int, size: int, type: ConfigurationType) -> list[DeviceConfiguration]:
        ...

    @staticmethod
    def buildEmptyMotors(initialPort: int, size: int) -> list[DeviceConfiguration]:
        ...

    @staticmethod
    def buildEmptyServos(initialPort: int, size: int) -> list[DeviceConfiguration]:
        ...

    def buildEmptyLynxModule(self, name: str, moduleAddress: int, parentModuleAddress: int, isEnabled: bool) -> LynxModuleConfiguration:
        """To build a parent lynx module, pass the same number to both moduleAddress and parentModuleAddress"""
        ...

    def buildEmptyServoHub(self, name: str, moduleAddress: int, parentModuleAddress: int, isEnabled: bool) -> ServoHubConfiguration:
        ...

    TAG: str
    firstNamedDeviceNumber: int
    existingNames: set[str]


class ReadXMLFileHandler(ConfigurationUtility):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ReadXMLFileHandler"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, deviceManager: DeviceManager) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def xmlPullParserFromReader(reader: Any) -> Any:
        ...

    @overload
    def parse(self, reader: Any) -> list[ControllerConfiguration]:
        ...
    @overload
    def parse(self, parser: Any) -> list[ControllerConfiguration]:
        ...
    @overload
    def parse(self, is_: Any) -> list[ControllerConfiguration]:
        ...
    def parse(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def onDeviceParsed(self, device: DeviceConfiguration) -> None:
        ...

    @staticmethod
    def deform(xmlTag: str) -> ConfigurationType:
        ...

    TAG: str


class LynxUsbDeviceConfiguration(ControllerConfiguration):
    """A Lynx USB Device contains one or more Lynx modules linked together over an RS485 bus. The one of these which is connected externally to USB is termed the 'parent'; the others are called 'children'."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.LynxUsbDeviceConfiguration"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, name: str, modules: list[RhspModuleConfiguration], serialNumber: SerialNumber) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def setSerialNumber(self, serialNumber: SerialNumber) -> None:
        ...

    def getParentModuleAddress(self) -> int:
        """Returns the module address of the Lynx module which is directly USB connected"""
        ...

    def setParentModuleAddress(self, moduleAddress: int) -> None:
        ...

    def getModules(self) -> list[RhspModuleConfiguration]:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    def deserializeChildElement(self, configurationType: ConfigurationType, parser: Any, xmlReader: ReadXMLFileHandler) -> None:
        ...

    def onDeserializationComplete(self, xmlReader: ReadXMLFileHandler) -> None:
        ...

    XMLATTR_PARENT_MODULE_ADDRESS: str
    parentModuleAddress: int


class RhspModuleConfiguration(ControllerConfiguration[DeviceConfiguration]):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.RhspModuleConfiguration"
    def __init__(self, name: str, devices: list[DeviceConfiguration], serialNumber: SerialNumber, type: ConfigurationType) -> None:
        ...

    def isParent(self) -> bool:
        """A Control Hub or a USB-connected Expansion Hub is considered a \"Parent\", and an RS485-connected Expansion Hub is a \"Child\"."""
        ...

    def setModuleAddress(self, moduleAddress: int) -> None:
        ...

    def getModuleAddress(self) -> int:
        ...

    def setParentModuleAddress(self, parentModuleAddress: int) -> None:
        """Set the address of the parent module that this module is connected through."""
        ...

    def getParentModuleAddress(self) -> int:
        """If this module is a parent, this will return its own address"""
        ...

    def setPort(self, port: int) -> None:
        ...

    def setUsbDeviceSerialNumber(self, usbDeviceSerialNumber: SerialNumber) -> None:
        ...

    def setSerialNumber(self, serialNumber: SerialNumber) -> None:
        ...

    def getUsbDeviceSerialNumber(self) -> SerialNumber:
        ...

    def getModuleSerialNumber(self) -> SerialNumber:
        """separate method just to reinforce whose serial number we're retreiving"""
        ...


class ServoHubConfiguration(RhspModuleConfiguration):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ServoHubConfiguration"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, name: str) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def isParent(self) -> bool:
        ...

    def getServos(self) -> list[DeviceConfiguration]:
        ...

    def setServos(self, servos: list[DeviceConfiguration]) -> None:
        ...

    def deserializeChildElement(self, configurationType: ConfigurationType, parser: Any, xmlReader: ReadXMLFileHandler) -> None:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    TAG: str


class Supplier(Generic[T]):
    """Represents a supplier of results. There is no requirement that a new or distinct result be returned each time the supplier is invoked. This is a functional interface whose functional method is get()."""
    __java__ = "org.firstinspires.ftc.robotcore.external.function.Supplier"
    def get(self) -> T:
        ...


class LynxModuleConfiguration(RhspModuleConfiguration):
    """Created by bob on 2016-03-11."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.LynxModuleConfiguration"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, name: str) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def isParent(self) -> bool:
        """A Control Hub or a USB-connected Expansion Hub is considered a \"Parent\", and an RS485-connected Expansion Hub is a \"Child\"."""
        ...

    def getServos(self) -> list[DeviceConfiguration]:
        ...

    def setServos(self, servos: list[DeviceConfiguration]) -> None:
        ...

    def getMotors(self) -> list[DeviceConfiguration]:
        ...

    def setMotors(self, motors: list[DeviceConfiguration]) -> None:
        ...

    def getAnalogInputs(self) -> list[DeviceConfiguration]:
        ...

    def setAnalogInputs(self, inputs: list[DeviceConfiguration]) -> None:
        ...

    def getPwmOutputs(self) -> list[DeviceConfiguration]:
        ...

    def setPwmOutputs(self, pwmOutputs: list[DeviceConfiguration]) -> None:
        ...

    @overload
    def getI2cDevices(self) -> list[LynxI2cDeviceConfiguration]:
        ...
    @overload
    def getI2cDevices(self, busZ: int) -> list[LynxI2cDeviceConfiguration]:
        ...
    def getI2cDevices(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def setI2cDevices(self, i2cDevices: list[LynxI2cDeviceConfiguration]) -> None:
        ...
    @overload
    def setI2cDevices(self, busZ: int, devices: list[LynxI2cDeviceConfiguration]) -> None:
        ...
    def setI2cDevices(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getDigitalDevices(self) -> list[DeviceConfiguration]:
        ...

    def setDigitalDevices(self, digitalDevices: list[DeviceConfiguration]) -> None:
        ...

    def deserializeChildElement(self, configurationType: ConfigurationType, parser: Any, xmlReader: ReadXMLFileHandler) -> None:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    TAG: str


class LynxI2cDeviceConfiguration(DeviceConfiguration):
    """LynxI2cDeviceConfiguration need to specify the bus number in addition to the port. On Lynx, the latter is only used in the configuration UI to maintain the sort order."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.LynxI2cDeviceConfiguration"
    def __init__(self) -> None:
        ...

    def getBus(self) -> int:
        ...

    def setBus(self, bus: int) -> None:
        ...

    def getI2cChannel(self) -> Any:
        ...

    def serializeXmlAttributes(self, serializer: Any) -> None:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    TAG: str
    XMLATTR_BUS: str
    bus: int


class WebcamConfiguration(ControllerConfiguration[DeviceConfiguration]):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.WebcamConfiguration"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, name: str, serialNumber: SerialNumber) -> None:
        ...
    @overload
    def __init__(self, name: str, serialNumber: SerialNumber, autoOpen: bool) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getAutoOpen(self) -> bool:
        ...

    def deserializeAttributes(self, parser: Any) -> None:
        ...

    XMLATTR_AUTO_OPEN_CAMERA: str
    autoOpen: bool
    """Whether we are to open the camera automatically on robot restart. Not currently implemented; parsing support here is future-proofing."""


class RobotUsbDevice:
    """RobotUsbDevice is an interface to USB devices that are commuicated with using a serial communication stream. This is in contrast to more other USB devices that use the full capabilities of USB. See http://www.usb.org/developers/defined_class. Note that this is not to be confused with RobotUsbDeviceTty."""
    __java__ = "com.qualcomm.robotcore.hardware.usb.RobotUsbDevice"
    class FirmwareVersion:
        __java__ = "com.qualcomm.robotcore.hardware.usb.RobotUsbDevice.FirmwareVersion"
        @overload
        def __init__(self, majorVersion: int, minorVersion: int) -> None:
            ...
        @overload
        def __init__(self, bVersion: int) -> None:
            ...
        @overload
        def __init__(self) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def toString(self) -> str:
            ...

        majorVersion: int
        minorVersion: int

    class USBIdentifiers:
        __java__ = "com.qualcomm.robotcore.hardware.usb.RobotUsbDevice.USBIdentifiers"
        def isLynxDevice(self) -> bool:
            ...

        @staticmethod
        def createLynxIdentifiers() -> RobotUsbDevice.USBIdentifiers:
            ...

        @staticmethod
        def first(set: set[T]) -> T:
            ...

        vendorId: int
        productId: int
        bcdDevice: int

    def setDebugRetainBuffers(self, retain: bool) -> None:
        ...

    def getDebugRetainBuffers(self) -> bool:
        ...

    def logRetainedBuffers(self, nsOrigin: int, nsTimerExpire: int, tag: str, format: str, *args: object) -> None:
        ...

    def setBaudRate(self, rate: int) -> None:
        """Sets the rate of data transmission used to communicate with the device."""
        ...

    def setDataCharacteristics(self, dataBits: int, stopBits: int, parity: int) -> None:
        """Set the Data Characteristics"""
        ...

    def setLatencyTimer(self, latencyTimer: int) -> None:
        """Set the latency timer"""
        ...

    def setBreak(self, enable: bool) -> None:
        """Sets or unsets a break state on the communication line"""
        ...

    def resetAndFlushBuffers(self) -> None:
        """Resets the remote USB device comm-layer as best we can. Additionally, flushes any incoming or outgoing data buffers on this end of the line."""
        ...

    def write(self, data: list[int]) -> None:
        """Write to device"""
        ...

    def skipToLikelyUsbPacketStart(self) -> None:
        """Skips to the beginning of a USB packet, if not already there. It is safe to err on the side of saying we're at the start when in fact we may not be. The point of this is that the packet start can have significance for resynchronization."""
        ...

    def mightBeAtUsbPacketStart(self) -> bool:
        """Answers as to whether we're it's probably the case we're at the start of a Usb packet. No is definitive; yes is uncertain."""
        ...

    def read(self, data: list[int], ibFirst: int, cbToRead: int, msTimeout: int, timeWindow: TimeWindow) -> int:
        """Reads a requested number of bytes from the device."""
        ...

    def requestReadInterrupt(self, interruptRequested: bool) -> None:
        """Interrupts any reads that are currently pending inside the device, possibly waiting on a perhaps lengthy timeout."""
        ...

    def close(self) -> None:
        """Closes the device"""
        ...

    def isOpen(self) -> bool:
        """Returns whether the device is open or not"""
        ...

    def isAttached(self) -> bool:
        """Returns whether or not this USB device is known to be physically attached"""
        ...

    def getFirmwareVersion(self) -> RobotUsbDevice.FirmwareVersion:
        """Returns the firmware version of this USB device, or null if no such version is known."""
        ...

    def setFirmwareVersion(self, version: RobotUsbDevice.FirmwareVersion) -> None:
        """Sets the firmware version of this USB device. Note that this does not actually change the persistent firmware version inside the device, only our local copy of it here."""
        ...

    def getUsbIdentifiers(self) -> RobotUsbDevice.USBIdentifiers:
        """Returns the USB-level vendor and product id of this device. All the devices we are interested in use FTDI chips (2018.06.01: no longer true: webcams!), which report as vendor 0x0403. Modern Robotics modules (currently?) use a product id of 0x6001 and bcdDevice of 0x0600. Lynx modules use a product id of 0x6015 and bcdDevice of 0x1000. Note that for FTDI, only the upper byte of the two-byte bcdDevice seems to be of significance. \"Every Universal Serial Bus (USB) device must be able to provide a single device descriptor that contains relevant information about the device. The USB_DEVICE_DESCRIPTOR structure describes a device descriptor. Windows uses that information to derive various sets of information. For example, the idVendor and idProduct fields specify vendor and product identifiers, respectively. Windows uses those field values to construct a hardware ID for the device. To view the hardware ID of a particular device, open Device Manager and view device properties. In the Details tab, the Hardware Ids property value indicates the hardware ID (\"USB\\XXX\") that is generated by Windows. The bcdUSB field indicates the version of the USB specification to which the device conforms. For example, 0x0200 indicates that the device is designed as per the USB 2.0 specification. The bcdDevice value indicates the device-defined revision number. The USB driver stack uses bcdDevice, along with idVendor and idProduct, to generate hardware and compatible IDs for the device. You can view the those identifiers in Device Manager. The device descriptor also indicates the total number of configurations that the device supports\""""
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getProductName(self) -> str:
        ...

    def setDeviceType(self, deviceType: DeviceManager.UsbDeviceType) -> None:
        ...

    def getDeviceType(self) -> DeviceManager.UsbDeviceType:
        ...


class ServoConfigurationType(InstantiableUserConfigurationType):
    """ServoConfigurationType contains the meta-data for a user-defined servo type."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.typecontainers.ServoConfigurationType"
    @overload
    def __init__(self, clazz: type[HardwareDevice], xmlTag: str, classSource: ConfigurationTypeManager.ClassSource) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def getStandardServoType() -> ServoConfigurationType:
        ...

    def processAnnotation(self, servoType: ServoType) -> None:
        ...

    def getServoFlavor(self) -> ServoFlavor:
        ...

    def getUsPulseLower(self) -> float:
        ...

    def getUsPulseUpper(self) -> float:
        ...

    def getUsFrame(self) -> float:
        ...

    def annotatedClassIsInstantiable(self) -> bool:
        ...

    def createInstances(self, controller: ServoControllerEx, port: int) -> list[HardwareDevice]:
        ...


class ServoFlavor(enum.Enum):
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ServoFlavor"
    STANDARD = enum.auto()
    CONTINUOUS = enum.auto()
    CUSTOM = enum.auto()


def ServoType(*, flavor: ServoFlavor, usPulseLower: float, usPulseUpper: float, usPulseFrameRate: float, xmlTag: str = 'Servo') -> Callable[[type], type]:
    """ServoType is an annotation with which a class or interface can be decorated in order to define a new kind of servo that can be configured in the robot configuration user interface."""
    def _decorator(cls: type) -> type:
        return cls
    return _decorator


class ExpansionHubMotorControllerParamsState:
    """ExpansionHubMotorControllerParamsState captures state that is declared in Expansion Hub Motor Controller parameter attributes."""
    __java__ = "com.qualcomm.robotcore.hardware.configuration.ExpansionHubMotorControllerParamsState"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> None:
        ...
    @overload
    def __init__(self, params: ExpansionHubMotorControllerPositionParams) -> None:
        ...
    @overload
    def __init__(self, params: ExpansionHubPIDFPositionParams) -> None:
        ...
    @overload
    def __init__(self, params: ExpansionHubMotorControllerVelocityParams) -> None:
        ...
    @overload
    def __init__(self, params: ExpansionHubPIDFVelocityParams) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getPidfCoefficients(self) -> PIDFCoefficients:
        ...

    def clone(self) -> ExpansionHubMotorControllerParamsState:
        ...

    def isDefault(self) -> bool:
        ...

    def equals(self, o: object) -> bool:
        ...

    def hashCode(self) -> int:
        ...

    def hash(self, d: float) -> int:
        ...

    def toString(self) -> str:
        ...

    mode: DcMotor.RunMode
    """Only DcMotor.RunMode#RUN_USING_ENCODER and DcMotor.RunMode#RUN_TO_POSITION are legal for #mode."""
    p: float
    i: float
    d: float
    f: float
    algorithm: MotorControlAlgorithm


class DenseMatrixF(MatrixF):
    """A DenseMatrixF is a matrix of floats whose storage is a contiguous float[] array. It may logically be ranged arranged either in row or column major order."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.DenseMatrixF"
    def __init__(self, nRows: int, nCols: int) -> None:
        ...

    def get(self, row: int, col: int) -> float:
        ...

    def put(self, row: int, col: int, value: float) -> None:
        ...

    def getData(self) -> list[float]:
        """Returns the contiguous array of floats which is the storage for this matrix"""
        ...

    def indexFromRowCol(self, row: int, col: int) -> int:
        """Given a row and column index into the matrix, returns the corresponding index into the underlying float[] array."""
        ...


class ColumnMajorMatrixF(DenseMatrixF):
    """A ColumnMajorMatrixF is a dense matrix whose entries are arranged in column-major order."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.ColumnMajorMatrixF"
    def __init__(self, nRows: int, nCols: int) -> None:
        ...

    def indexFromRowCol(self, row: int, col: int) -> int:
        ...

    def toVector(self) -> VectorF:
        ...


class OpenGLMatrix(ColumnMajorMatrixF):
    """An OpenGLMatrix is a 4x4 matrix commonly used as a transformation matrix for 3D homogeneous coordinates. The data layout of an OpenGLMatrix is used heavily in the OpenGL high performance graphics standard."""
    __java__ = "org.firstinspires.ftc.robotcore.external.matrices.OpenGLMatrix"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, data: list[float]) -> None:
        ...
    @overload
    def __init__(self, him: MatrixF) -> None:
        """Constructs an OpenGL matrix whose values are initialized from the other matrix. The other matrix must have dimensions at most 4x4."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def emptyMatrix(self, numRows: int, numCols: int) -> MatrixF:
        ...

    @overload
    @staticmethod
    def rotation(angleUnit: AngleUnit, angle: float, dx: float, dy: float, dz: float) -> OpenGLMatrix:
        """Creates a matrix for rotation by the indicated angle around the indicated vector."""
        ...
    @overload
    @staticmethod
    def rotation(axesReference: AxesReference, axesOrder: AxesOrder, angleUnit: AngleUnit, first: float, second: float, third: float) -> OpenGLMatrix:
        """Creates a matrix for a rotation specified by three successive rotation angles."""
        ...
    @staticmethod
    def rotation(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def translation(dx: float, dy: float, dz: float) -> OpenGLMatrix:
        ...

    @staticmethod
    def identityMatrix() -> OpenGLMatrix:
        ...

    def getData(self) -> list[float]:
        ...

    @overload
    def scale(self, scaleX: float, scaleY: float, scaleZ: float) -> None:
        ...
    @overload
    def scale(self, scale: float) -> None:
        ...
    def scale(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def translate(self, dx: float, dy: float, dz: float) -> None:
        ...

    @overload
    def rotate(self, angleUnit: AngleUnit, angle: float, dx: float, dy: float, dz: float) -> None:
        ...
    @overload
    def rotate(self, axesReference: AxesReference, axesOrder: AxesOrder, angleUnit: AngleUnit, first: float, second: float, third: float) -> None:
        ...
    def rotate(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def scaled(self, scaleX: float, scaleY: float, scaleZ: float) -> OpenGLMatrix:
        ...
    @overload
    def scaled(self, scale: float) -> OpenGLMatrix:
        ...
    def scaled(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def translated(self, dx: float, dy: float, dz: float) -> OpenGLMatrix:
        ...

    @overload
    def rotated(self, angleUnit: AngleUnit, angle: float, dx: float, dy: float, dz: float) -> OpenGLMatrix:
        ...
    @overload
    def rotated(self, axesReference: AxesReference, axesOrder: AxesOrder, angleUnit: AngleUnit, first: float, second: float, third: float) -> OpenGLMatrix:
        ...
    def rotated(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def inverted(self) -> OpenGLMatrix:
        ...

    def transposed(self) -> OpenGLMatrix:
        ...

    @overload
    def multiplied(self, him: OpenGLMatrix) -> OpenGLMatrix:
        ...
    @overload
    def multiplied(self, him: MatrixF) -> MatrixF:
        ...
    def multiplied(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def multiply(self, him: OpenGLMatrix) -> None:
        """Updates the receiver to be the product of itself and another matrix."""
        ...
    @overload
    def multiply(self, him: MatrixF) -> None:
        """Updates the receiver to be the product of itself and another matrix."""
        ...
    def multiply(self, *args: Any, **kwargs: Any) -> Any:
        ...

    data: list[float]


# Referenced from a stubbed signature somewhere in ftc.*, but not
# extractable: no declaration for these exists in any FTC SDK
# *-sources.jar artifact (Android framework, OpenCV, org.json, the
# JDK itself, or a couple of third-party libraries the SDK depends
# on without shipping sources for). A signature naming one of these
# still renders `Any` for that parameter/return/field -- this list
# exists so that's a documented gap, not a silent one.
UNSTUBBABLE_JAVA_TYPES = [
    "android.app.Activity",
    "android.content.BroadcastReceiver",
    "android.content.Context",
    "android.content.Intent",
    "android.content.SharedPreferences",
    "android.content.SharedPreferences.OnSharedPreferenceChangeListener",
    "android.graphics.Bitmap",
    "android.graphics.Canvas",
    "android.graphics.Paint",
    "android.hardware.Sensor",
    "android.hardware.SensorEvent",
    "android.hardware.SensorEventListener",
    "android.hardware.TriggerEvent",
    "android.hardware.TriggerEventListener",
    "android.hardware.usb.UsbDevice",
    "android.net.wifi.WifiManager",
    "android.net.wifi.p2p.WifiP2pDevice",
    "android.os.Handler",
    "android.util.Pair",
    "android.util.Size",
    "android.view.View",
    "android.view.WindowManager.LayoutParams",
    "android.widget.TextView",
    "com.google.gson.Gson",
    "com.google.gson.TypeAdapter",
    "com.google.gson.stream.JsonReader",
    "com.google.gson.stream.JsonWriter",
    "com.qualcomm.robotcore.hardware.DcMotor.Direction",
    "com.qualcomm.robotcore.hardware.usb.RobotUsbModule.ARMINGSTATE",
    "com.qualcomm.robotcore.wifi.WifiDirectAssistant.ConnectStatus",
    "java.io.Closeable",
    "java.io.File",
    "java.io.InputStream",
    "java.io.OutputStream",
    "java.io.PrintWriter",
    "java.io.Reader",
    "java.io.Serializable",
    "java.lang.ARMINGSTATE",
    "java.lang.AccelerationIntegrator",
    "java.lang.Band",
    "java.lang.Blob",
    "java.lang.BlobFilter",
    "java.lang.BlobSort",
    "java.lang.CachingMode",
    "java.lang.CalibrationData",
    "java.lang.CalibrationStatus",
    "java.lang.Callback",
    "java.lang.CameraState",
    "java.lang.ChannelBankConfig",
    "java.lang.ChannelPulseWidthParams",
    "java.lang.ClassLoader",
    "java.lang.Cloneable",
    "java.lang.Comparable",
    "java.lang.CompassMode",
    "java.lang.ConnectStatus",
    "java.lang.ContourMode",
    "java.lang.DeviceFlavor",
    "java.lang.Direction",
    "java.lang.Enable",
    "java.lang.EncoderDataBlock",
    "java.lang.EncoderDirection",
    "java.lang.Exception",
    "java.lang.FirmwareVersion",
    "java.lang.Gain",
    "java.lang.HealthStatus",
    "java.lang.HeartbeatAction",
    "java.lang.I2cChannel",
    "java.lang.I2cRecoveryMode",
    "java.lang.InterruptedException",
    "java.lang.IrSeekerIndividualSensor",
    "java.lang.Iterable",
    "java.lang.LEDCurrent",
    "java.lang.LEDDrive",
    "java.lang.LEDPulseModulation",
    "java.lang.LSMeasurementRate",
    "java.lang.LSResolution",
    "java.lang.LocalizerDataBlock",
    "java.lang.LocalizerStatus",
    "java.lang.LocalizerYawAxis",
    "java.lang.LynxUsbDeviceImpl",
    "java.lang.Manufacturer",
    "java.lang.Mode",
    "java.lang.MorphOperationType",
    "java.lang.MsgType",
    "java.lang.NetworkEvent",
    "java.lang.NoClassDefFoundError",
    "java.lang.PSMeasurementRate",
    "java.lang.PSResolution",
    "java.lang.Parameters",
    "java.lang.PoseSolver",
    "java.lang.PwmRange",
    "java.lang.PwmStatus",
    "java.lang.ReadWindow",
    "java.lang.Register",
    "java.lang.Result",
    "java.lang.RunMode",
    "java.lang.Runnable",
    "java.lang.RuntimeException",
    "java.lang.SensorMode",
    "java.lang.ShutdownReason",
    "java.lang.StackTraceElement",
    "java.lang.Step",
    "java.lang.StreamFormat",
    "java.lang.StringBuilder",
    "java.lang.Swatch",
    "java.lang.SystemError",
    "java.lang.SystemOperationHandle",
    "java.lang.SystemStatus",
    "java.lang.TagFamily",
    "java.lang.Thread",
    "java.lang.Throwable",
    "java.lang.UsbDeviceType",
    "java.lang.ZeroPowerBehavior",
    "java.lang.reflect.Constructor",
    "java.lang.reflect.Field",
    "java.lang.reflect.Method",
    "java.net.DatagramPacket",
    "java.net.InetAddress",
    "java.net.InetSocketAddress",
    "java.net.ServerSocket",
    "java.net.Socket",
    "java.nio.ByteBuffer",
    "java.nio.ByteOrder",
    "java.nio.MappedByteBuffer",
    "java.nio.charset.Charset",
    "java.security.KeyStore",
    "java.util.AbstractQueue",
    "java.util.Comparator",
    "java.util.EnumSet",
    "java.util.Iterator",
    "java.util.Map.Entry",
    "java.util.WeakHashMap",
    "java.util.concurrent.BlockingQueue",
    "java.util.concurrent.Callable",
    "java.util.concurrent.ConcurrentHashMap",
    "java.util.concurrent.CountDownLatch",
    "java.util.concurrent.Executor",
    "java.util.concurrent.ExecutorService",
    "java.util.concurrent.Future",
    "java.util.concurrent.LinkedBlockingDeque",
    "java.util.concurrent.ScheduledExecutorService",
    "java.util.concurrent.ScheduledFuture",
    "java.util.concurrent.ScheduledThreadPoolExecutor",
    "java.util.concurrent.Semaphore",
    "java.util.concurrent.ThreadFactory",
    "java.util.concurrent.ThreadPoolExecutor",
    "java.util.concurrent.TimeUnit",
    "java.util.concurrent.atomic.AtomicInteger",
    "java.util.concurrent.atomic.AtomicReference",
    "java.util.concurrent.locks.Lock",
    "javax.net.ssl.KeyManager",
    "javax.net.ssl.KeyManagerFactory",
    "javax.net.ssl.SSLServerSocketFactory",
    "org.json.JSONObject",
    "org.opencv.core.Mat",
    "org.opencv.core.MatOfPoint",
    "org.opencv.core.MatOfPoint2f",
    "org.opencv.core.Point",
    "org.opencv.core.Rect",
    "org.opencv.core.RotatedRect",
    "org.opencv.core.Scalar",
    "org.openftc.apriltag.AprilTagDetectorJNI.TagFamily",
    "org.openftc.easyopencv.OpenCvCamera",
    "org.openftc.easyopencv.OpenCvCameraRotation",
    "org.openftc.easyopencv.OpenCvWebcam.StreamFormat",
    "org.openftc.easyopencv.TimestampedOpenCvPipeline",
    "org.threeten.bp.YearMonth",
    "org.xmlpull.v1.XmlPullParser",
    "org.xmlpull.v1.XmlSerializer",
]
