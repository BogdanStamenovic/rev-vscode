from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

from ftc.opmode import LinearOpMode, OpModeManagerNotifier
from ftc.util import GlobalWarningSource, PeerStatusCallback
if TYPE_CHECKING:
    from ftc.internal import AnalogSensorConfigurationType, ApChannel, CallbackResult, CameraCharacteristics, Consumer, Continuation, ControllerConfiguration, DeviceConfiguration, DigitalIoDeviceConfigurationType, EventLoop, EvictingBlockingQueue, ExpansionHubMotorControllerParamsState, GamepadUser, I2cDeviceConfigurationType, LynxCommand, LynxDatagram, LynxDekaInterfaceCommand, LynxI2cConfigureChannelCommand, LynxInterface, LynxMessage, LynxNack, LynxRespondable, LynxResponse, MotorConfigurationType, NetworkType, ProgressParameters, RobocolDatagram, RobocolDatagramSocket, RobotCoreCommandList, RobotCoreException, RobotState, RobotUsbDevice, RobotUsbManager, ServoConfigurationType, TargetPositionNotSetException, ThrowingSupplier, TimeWindow
    from ftc.navigation import Acceleration, AngleUnit, AngularVelocity, AxesOrder, AxesReference, Axis, CurrentUnit, DistanceUnit, MagneticFlux, Orientation, Pose2D, Pose3D, Position, Quaternion, TempUnit, Temperature, UnnormalizedAngleUnit, Velocity, VoltageUnit, YawPitchRollAngles
    from ftc.opmode import EventLoopManagerClient, OpMode, OpModeManagerImpl
    from ftc.telemetry import Consumer, Func
    from ftc.util import Deadline, ElapsedTime, LastKnown, SerialNumber, VendorProductSerialNumber, WeakReferenceSet, WebServer

DEVICE_CLIENT = TypeVar("DEVICE_CLIENT", bound="I2cDeviceSynchSimple")
DEVICE_TYPE = TypeVar("DEVICE_TYPE", bound="HardwareDevice")
PARAMETERS = TypeVar("PARAMETERS")
T = TypeVar("T")
class HardwareDevice:
    """Interface used by Hardware Devices"""
    __java__ = "com.qualcomm.robotcore.hardware.HardwareDevice"
    class Manufacturer(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.HardwareDevice.Manufacturer"
        Unknown = enum.auto()
        Other = enum.auto()
        Lego = enum.auto()
        HiTechnic = enum.auto()
        ModernRobotics = enum.auto()
        Adafruit = enum.auto()
        Matrix = enum.auto()
        Lynx = enum.auto()
        AMS = enum.auto()
        STMicroelectronics = enum.auto()
        Broadcom = enum.auto()
        DFRobot = enum.auto()
        DigitalChickenLabs = enum.auto()
        SparkFun = enum.auto()
        MaxBotix = enum.auto()
        LimelightVision = enum.auto()
        GoBilda = enum.auto()

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        """Returns an indication of the manufacturer of this device."""
        ...

    def getDeviceName(self) -> str:
        """Returns a string suitable for display to the user as to the type of device. Note that this is a device-type-specific name; it has nothing to do with the name by which a user might have configured the device in a robot configuration."""
        ...

    def getConnectionInfo(self) -> str:
        """Get connection information about this device in a human readable format"""
        ...

    def getVersion(self) -> int:
        """Version"""
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        """Resets the device's configuration to that which is expected at the beginning of an OpMode. For example, motors will reset the their direction to 'forward'."""
        ...

    def close(self) -> None:
        """Closes this device"""
        ...


class AccelerationSensor(HardwareDevice):
    """Acceleration Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.AccelerationSensor"
    def getAcceleration(self) -> Acceleration:
        """Acceleration, measured in g's"""
        ...

    def status(self) -> str:
        """Status of this sensor, in string form"""
        ...


class AnalogInput(HardwareDevice):
    """Control a single analog device"""
    __java__ = "com.qualcomm.robotcore.hardware.AnalogInput"
    def __init__(self, controller: AnalogInputController, channel: int) -> None:
        """Constructor"""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getVoltage(self) -> float:
        """Returns the current voltage of this input."""
        ...

    def getMaxVoltage(self) -> float:
        """Returns the maximum value that getVoltage() is capable of reading"""
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...


class AnalogInputController(HardwareDevice):
    """Interface for working with Analog Controllers"""
    __java__ = "com.qualcomm.robotcore.hardware.AnalogInputController"
    def getAnalogInputVoltage(self, channel: int) -> float:
        """Get the value of this analog input Return the current ADC results from the A0-A7 channel input pins."""
        ...

    def getMaxAnalogInputVoltage(self) -> float:
        """Returns the maximum value that getAnalogInputVoltage() is capable of reading"""
        ...

    def getSerialNumber(self) -> SerialNumber:
        """Serial Number"""
        ...


class AnalogSensor:
    """Instances of this interface are sensors whose input is reported as a voltage level to an analog to digital converter."""
    __java__ = "com.qualcomm.robotcore.hardware.AnalogSensor"
    def readRawVoltage(self) -> float:
        """Returns the sensor's current value as a raw voltage level. Note that for Returns the light level voltage as reported by the sensor. Note that returned values INCREASE as the light energy INCREASES."""
        ...


class Blinker:
    """Blinker provides the means to control an LED or a light that can be illuminated in a sequenced pattern of colors and durations."""
    __java__ = "com.qualcomm.robotcore.hardware.Blinker"
    class Step:
        """Step represents a particular color held for a particular length of time."""
        __java__ = "com.qualcomm.robotcore.hardware.Blinker.Step"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, color: int, duration: int, unit: Any) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        @staticmethod
        def nullStep() -> Blinker.Step:
            ...

        @overload
        def equals(self, them: object) -> bool:
            ...
        @overload
        def equals(self, step: Blinker.Step) -> bool:
            ...
        def equals(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def hashCode(self) -> int:
            ...

        def isLit(self) -> bool:
            ...

        def setLit(self, isEnabled: bool) -> None:
            ...

        def getColor(self) -> int:
            ...

        def setColor(self, color: int) -> None:
            ...

        def getDurationMs(self) -> int:
            ...

        def setDuration(self, duration: int, unit: Any) -> None:
            ...

        def toString(self) -> str:
            ...

        color: int
        msDuration: int

    def setPattern(self, steps: list[Blinker.Step]) -> None:
        """Sets the pattern with which this LED or light should illuminate. If the list of steps is longer than the maximum number supported, then the pattern is truncated."""
        ...

    def getPattern(self) -> list[Blinker.Step]:
        """Returns the current blinking pattern"""
        ...

    def pushPattern(self, steps: list[Blinker.Step]) -> None:
        """Saves the existing pattern such that it can be later restored, then calls setPattern()."""
        ...

    def patternStackNotEmpty(self) -> bool:
        """Returns whether the pattern stack is currently nonempty."""
        ...

    def popPattern(self) -> bool:
        """Pops the next pattern off of the stack of saved patterns, if any. If the stack is empty, then this sets the blinker to a constant black."""
        ...

    def setConstant(self, color: int) -> None:
        """Sets the blinker pattern to be a single, unchanging color"""
        ...

    def stopBlinking(self) -> None:
        """Sets the blinker to constant black and frees any internal resources"""
        ...

    def getBlinkerPatternMaxLength(self) -> int:
        """Returns the maximum number of Steps that can be present in a pattern"""
        ...


class DcMotorSimple(HardwareDevice):
    """Instances of DcMotorSimple interface provide a most basic motor-like functionality"""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorSimple"
    class Direction(enum.Enum):
        """DcMotors can be configured to internally reverse the values to which, e.g., their motor power is set. This makes it easy to have drive train motors on two sides of a robot: during initialization, one would be set at at forward, the other at reverse, and the difference between the two in that respect could be thereafter ignored. At the start of an OpMode, motors are guaranteed to be in the forward direction."""
        __java__ = "com.qualcomm.robotcore.hardware.DcMotorSimple.Direction"
        FORWARD = enum.auto()
        REVERSE = enum.auto()
        def inverted(self) -> DcMotorSimple.Direction:
            ...

    def setDirection(self, direction: DcMotorSimple.Direction) -> None:
        """Sets the logical direction in which this motor operates."""
        ...

    def getDirection(self) -> DcMotorSimple.Direction:
        """Returns the current logical direction in which this motor is set as operating."""
        ...

    def setPower(self, power: float) -> None:
        """Sets the power level of the motor, expressed as a fraction of the maximum possible power / speed supported according to the run mode in which the motor is operating. Setting a power level of zero will brake the motor"""
        ...

    def getPower(self) -> float:
        """Returns the current configured power level of the motor."""
        ...


class CRServo(DcMotorSimple):
    """CRServo is the central interface supported by continuous rotation servos"""
    __java__ = "com.qualcomm.robotcore.hardware.CRServo"
    def getController(self) -> ServoController:
        """Returns the underlying servo controller on which this servo is situated."""
        ...

    def getPortNumber(self) -> int:
        """Returns the port number on the underlying servo controller on which this motor is situated."""
        ...


class CRServoImpl(CRServo):
    """ContinuousRotationServoImpl provides an implementation of continuous rotation servo functionality."""
    __java__ = "com.qualcomm.robotcore.hardware.CRServoImpl"
    @overload
    def __init__(self, controller: ServoController, portNumber: int) -> None:
        """Constructor"""
        ...
    @overload
    def __init__(self, controller: ServoController, portNumber: int, direction: DcMotorSimple.Direction) -> None:
        """Constructor"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def getController(self) -> ServoController:
        ...

    def getPortNumber(self) -> int:
        ...

    def setDirection(self, direction: DcMotorSimple.Direction) -> None:
        ...

    def getDirection(self) -> DcMotorSimple.Direction:
        ...

    def setPower(self, power: float) -> None:
        ...

    def getPower(self) -> float:
        ...

    controller: ServoController
    portNumber: int
    direction: DcMotorSimple.Direction
    apiPowerMin: float
    apiPowerMax: float
    apiServoPositionMin: float
    apiServoPositionMax: float


class PwmControl:
    """For hardware devices which are manipulated using a pulse width modulation (PWM) signal, the PwmControl interface provides control of the width of pulses used and whether the PWM is enabled or disabled. PWM is commonly used to control servos. PwmControl is thus found as a second interface on servo objects whose primary interface is Servo or CRServo when the underlying servo controller hardware supports this fine-grained control (not all servo controllers provide such control). To access the PwmControl interface, cast your Servo or CRServo object to PwmControl; however, it is usually prudent to first test whether the cast will succeed by testing using instanceof."""
    __java__ = "com.qualcomm.robotcore.hardware.PwmControl"
    class PwmRange:
        """PwmRange instances are used to specify the upper and lower pulse widths and overall framing rate for a servo."""
        __java__ = "com.qualcomm.robotcore.hardware.PwmControl.PwmRange"
        @overload
        def __init__(self, usPulseLower: float, usPulseUpper: float) -> None:
            """Creates a new PwmRange with the indicated lower and upper bounds and the default framing rate."""
            ...
        @overload
        def __init__(self, usPulseLower: float, usPulseUpper: float, usFrame: float) -> None:
            """Creates a new PwmRange with the indicated lower and upper bounds and the specified framing rate."""
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def equals(self, o: object) -> bool:
            ...

        def hashCode(self) -> int:
            ...

        usFrameDefault: float
        """usFrameDefault is the default frame rate used, in microseconds"""
        usPulseUpperDefault: float
        usPulseLowerDefault: float
        defaultRange: PwmControl.PwmRange
        """defaultRange is the default PWM range used"""
        usPulseLower: float
        """usPulseLower is the minimum PWM rate used, in microseconds. This corresponds to a servo position of 0.0."""
        usPulseUpper: float
        """usPulseLower is the maximum PWM rate used, in microseconds. This corresponds to a servo position of 1.0."""
        usFrame: float
        """usFrame is the rate, in microseconds, at which the PWM is transmitted."""

    def setPwmRange(self, range: PwmControl.PwmRange) -> None:
        """Sets the PWM range limits for the servo"""
        ...

    def getPwmRange(self) -> PwmControl.PwmRange:
        """Returns the current PWM range limits for the servo"""
        ...

    def setPwmEnable(self) -> None:
        """Individually energizes the PWM for this particular servo."""
        ...

    def setPwmDisable(self) -> None:
        """Individually denergizes the PWM for this particular servo"""
        ...

    def isPwmEnabled(self) -> bool:
        """Returns whether the PWM is energized for this particular servo"""
        ...

    def setPulseWidth(self, usWidth: float) -> None:
        """Sets the pulse width for this particular servo (in microseconds)"""
        ...

    def getPulseWidth(self) -> float:
        """Gets the pulse width for this particular servo (in microseconds)"""
        ...


class CRServoImplEx(CRServoImpl, PwmControl):
    """CRServoEx provides access to extended functionality on continuous rotation servos. Implementations support both the CRServo and PwmControl interfaces."""
    __java__ = "com.qualcomm.robotcore.hardware.CRServoImplEx"
    @overload
    def __init__(self, controller: ServoControllerEx, portNumber: int, servoType: ServoConfigurationType) -> None:
        ...
    @overload
    def __init__(self, controller: ServoControllerEx, portNumber: int, direction: DcMotorSimple.Direction, servoType: ServoConfigurationType) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def setPwmRange(self, range: PwmControl.PwmRange) -> None:
        ...

    def getPwmRange(self) -> PwmControl.PwmRange:
        ...

    def setPwmEnable(self) -> None:
        ...

    def setPwmDisable(self) -> None:
        ...

    def isPwmEnabled(self) -> bool:
        ...

    def getPulseWidth(self) -> float:
        ...

    def setPulseWidth(self, usPulseWidth: float) -> None:
        ...

    controllerEx: ServoControllerEx


class DistanceSensor(HardwareDevice):
    """The DistanceSensor may be found on hardware sensors which measure distance by one means or another."""
    __java__ = "com.qualcomm.robotcore.hardware.DistanceSensor"
    def getDistance(self, unit: DistanceUnit) -> float:
        """Returns the current distance in the indicated distance units"""
        ...

    distanceOutOfRange: float
    """The value returned when a distance reading is not in fact available."""


class LightSensor(HardwareDevice):
    """Light Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.LightSensor"
    def getLightDetected(self) -> float:
        """Get the amount of light detected by the sensor, scaled and cliped to a range which is a pragmatically useful sensitivity. Note that returned values INCREASE as the light energy INCREASES."""
        ...

    def getRawLightDetected(self) -> float:
        """Returns a signal whose strength is proportional to the intensity of the light measured. Note that returned values INCREASE as the light energy INCREASES. The units in which this signal is returned are unspecified."""
        ...

    def getRawLightDetectedMax(self) -> float:
        """Returns the maximum value that can be returned by #getRawLightDetected."""
        ...

    def enableLed(self, enable: bool) -> None:
        """Enable the LED light"""
        ...

    def status(self) -> str:
        """Status of this sensor, in string form"""
        ...


class NormalizedColorSensor(HardwareDevice):
    """NormalizedColorSensor returns color sensor data in standardized units, which provides a measure of absolute color color intensity beyond the relative intensities available using ColorSensor."""
    __java__ = "com.qualcomm.robotcore.hardware.NormalizedColorSensor"
    def getNormalizedColors(self) -> NormalizedRGBA:
        """Reads the colors from the sensor"""
        ...

    def getGain(self) -> float:
        ...

    def setGain(self, newGain: float) -> None:
        ...


class OpticalDistanceSensor(LightSensor):
    """OpticalDistanceSensor is a LightSensor whose reported light intensities reflect (pun intended) a relationship to distance. Both raw readings and normalized readings can be obtained; however, these both (usually) have an inverse-square relationship to distance, and thus can be cumbersome to use. For an easier-to-use, linear relationship, see DistanceSensor."""
    __java__ = "com.qualcomm.robotcore.hardware.OpticalDistanceSensor"


class ColorSensor(HardwareDevice):
    """Color Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.ColorSensor"
    def red(self) -> int:
        """Get the Red values detected by the sensor as an int."""
        ...

    def green(self) -> int:
        """Get the Green values detected by the sensor as an int."""
        ...

    def blue(self) -> int:
        """Get the Blue values detected by the sensor as an int."""
        ...

    def alpha(self) -> int:
        """Get the amount of light detected by the sensor as an int."""
        ...

    def argb(self) -> int:
        """Get the sensed ARGB color value from the sensor."""
        ...

    def enableLed(self, enable: bool) -> None:
        """Enable the LED light"""
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        """Set the I2C address to a new value."""
        ...

    def getI2cAddress(self) -> I2cAddr:
        """Get the current I2C Address of this object. Not necessarily the same as the I2C address of the actual device. Return the current I2C address."""
        ...


class ColorRangeSensor(ColorSensor, NormalizedColorSensor, DistanceSensor, OpticalDistanceSensor):
    """Color Range Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.ColorRangeSensor"


class CompassSensor(HardwareDevice):
    """Compass Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.CompassSensor"
    class CompassMode(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.CompassSensor.CompassMode"
        MEASUREMENT_MODE = enum.auto()
        CALIBRATION_MODE = enum.auto()

    def getDirection(self) -> float:
        """Get the current direction, in degrees, in the range [0, 360). North is zero, East is 90, South is 180, and West is 270."""
        ...

    def status(self) -> str:
        """Status of this sensor, in string form"""
        ...

    def setMode(self, mode: CompassSensor.CompassMode) -> None:
        """Change to calibration or measurement mode"""
        ...

    def calibrationFailed(self) -> bool:
        """Check to see whether calibration was successful. After attempting a calibration, the hardware will (eventually) indicate whether or not it was unsuccessful. The default is \"success\", even when the calibration is not guaranteed to have completed successfully. A user should monitor this field for (at least) several seconds to determine success."""
        ...


class ControlSystem(enum.Enum):
    """Used to specify what type of control system a particular piece of hardware is connected to"""
    __java__ = "com.qualcomm.robotcore.hardware.ControlSystem"
    REV_HUB = enum.auto()


class DcMotor(DcMotorSimple):
    """DcMotor interface provides access to full-featured motor functionality."""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotor"
    class ZeroPowerBehavior(enum.Enum):
        """ZeroPowerBehavior provides an indication as to a motor's behavior when a power level of zero is applied."""
        __java__ = "com.qualcomm.robotcore.hardware.DcMotor.ZeroPowerBehavior"
        UNKNOWN = enum.auto()
        BRAKE = enum.auto()
        FLOAT = enum.auto()

    class RunMode(enum.Enum):
        """The run mode of a motor RunMode controls how the motor interprets the it's parameter settings passed through power- and encoder-related methods. Some of these modes internally use PID control to achieve their function, while others do not. Those that do are referred to as \"PID modes\"."""
        __java__ = "com.qualcomm.robotcore.hardware.DcMotor.RunMode"
        RUN_WITHOUT_ENCODER = enum.auto()
        RUN_USING_ENCODER = enum.auto()
        RUN_TO_POSITION = enum.auto()
        STOP_AND_RESET_ENCODER = enum.auto()
        RUN_WITHOUT_ENCODERS = enum.auto()
        RUN_USING_ENCODERS = enum.auto()
        RESET_ENCODERS = enum.auto()
        def migrate(self) -> DcMotor.RunMode:
            """Returns the new new constant corresponding to old constant names."""
            ...

        def isPIDMode(self) -> bool:
            """Returns whether this RunMode is a PID-controlled mode or not"""
            ...

    def getMotorType(self) -> MotorConfigurationType:
        """Returns the assigned type for this motor. If no particular motor type has been configured, then MotorConfigurationType#getUnspecifiedMotorType() will be returned. Note that the motor type for a given motor is initially assigned in the robot configuration user interface, though it may subsequently be modified using methods herein."""
        ...

    def setMotorType(self, motorType: MotorConfigurationType) -> None:
        """Sets the assigned type of this motor. Usage of this method is very rare."""
        ...

    def getController(self) -> DcMotorController:
        """Returns the underlying motor controller on which this motor is situated."""
        ...

    def getPortNumber(self) -> int:
        """Returns the port number on the underlying motor controller on which this motor is situated."""
        ...

    def setZeroPowerBehavior(self, zeroPowerBehavior: DcMotor.ZeroPowerBehavior) -> None:
        """Sets the behavior of the motor when a power level of zero is applied."""
        ...

    def getZeroPowerBehavior(self) -> DcMotor.ZeroPowerBehavior:
        """Returns the current behavior of the motor were a power level of zero to be applied."""
        ...

    def setPowerFloat(self) -> None:
        """Sets the zero power behavior of the motor to ZeroPowerBehavior#FLOAT, then applies zero power to that motor. Note that the change of the zero power behavior to ZeroPowerBehavior#FLOAT remains in effect even following the return of this method. This is a breaking change in behavior from previous releases of the SDK. Consider, for example, the following code sequence:"""
        ...

    def getPowerFloat(self) -> bool:
        """Returns whether the motor is currently in a float power level."""
        ...

    def setTargetPosition(self, position: int) -> None:
        """Sets the desired encoder target position to which the motor should advance or retreat and then actively hold thereat. This behavior is similar to the operation of a servo. The maximum speed at which this advance or retreat occurs is governed by the power level currently set on the motor. While the motor is advancing or retreating to the desired taget position, #isBusy() will return true. Note that adjustment to a target position is only effective when the motor is in RunMode#RUN_TO_POSITION RunMode. Note further that, clearly, the motor must be equipped with an encoder in order for this mode to function properly."""
        ...

    def getTargetPosition(self) -> int:
        """Returns the current target encoder position for this motor."""
        ...

    def isBusy(self) -> bool:
        """Returns true if the motor is currently advancing or retreating to a target position."""
        ...

    def getCurrentPosition(self) -> int:
        """Returns the current reading of the encoder for this motor. The units for this reading, that is, the number of ticks per revolution, are specific to the motor/encoder in question, and thus are not specified here."""
        ...

    def setMode(self, mode: DcMotor.RunMode) -> None:
        """Sets the current run mode for this motor"""
        ...

    def getMode(self) -> DcMotor.RunMode:
        """Returns the current run mode for this motor"""
        ...


class DcMotorController(HardwareDevice):
    """Interface for working with DC Motor Controllers"""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorController"
    def setMotorType(self, motor: int, motorType: MotorConfigurationType) -> None:
        """Informs the motor controller of the type of a particular motor. This is normally used only as part of the initialization of a motor."""
        ...

    def getMotorType(self, motor: int) -> MotorConfigurationType:
        """Retrieves the motor type configured for this motor"""
        ...

    def setMotorMode(self, motor: int, mode: DcMotor.RunMode) -> None:
        """Set the current motor mode. DcMotor.RunMode"""
        ...

    def getMotorMode(self, motor: int) -> DcMotor.RunMode:
        """Get the current motor mode. Returns the current \"run mode\"."""
        ...

    def setMotorPower(self, motor: int, power: float) -> None:
        """Set the current motor power"""
        ...

    def getMotorPower(self, motor: int) -> float:
        """Get the current motor power"""
        ...

    def isBusy(self, motor: int) -> bool:
        """Is the motor busy?"""
        ...

    def setMotorZeroPowerBehavior(self, motor: int, zeroPowerBehavior: DcMotor.ZeroPowerBehavior) -> None:
        """Sets the behavior of the motor when zero power is applied."""
        ...

    def getMotorZeroPowerBehavior(self, motor: int) -> DcMotor.ZeroPowerBehavior:
        """Returns the current zero power behavior of the motor."""
        ...

    def getMotorPowerFloat(self, motor: int) -> bool:
        """Is motor power set to float?"""
        ...

    def setMotorTargetPosition(self, motor: int, position: int) -> None:
        """Set the motor target position. This takes in an integer, which is not scaled. Motor power should be positive if using run to position"""
        ...

    def getMotorTargetPosition(self, motor: int) -> int:
        """Get the current motor target position"""
        ...

    def getMotorCurrentPosition(self, motor: int) -> int:
        """Get the current motor position"""
        ...

    def resetDeviceConfigurationForOpMode(self, motor: int) -> None:
        """Reset the state we hold for the given motor so that it's clean at the start of an OpMode"""
        ...


class DcMotorControllerEx(DcMotorController):
    """DcMotorControllerEx is an optional motor controller interface supported by some hardware that provides enhanced motor functionality."""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorControllerEx"
    def setMotorEnable(self, motor: int) -> None:
        """Individually energizes a particular motor"""
        ...

    def setMotorDisable(self, motor: int) -> None:
        """Individually denergizes a particular motor"""
        ...

    def isMotorEnabled(self, motor: int) -> bool:
        """Returns whether a particular motor on the controller is energized"""
        ...

    @overload
    def setMotorVelocity(self, motor: int, ticksPerSecond: float) -> None:
        """Sets the target velocity of the indicated motor."""
        ...
    @overload
    def setMotorVelocity(self, motor: int, angularRate: float, unit: AngleUnit) -> None:
        """Sets the target velocity of the indicated motor."""
        ...
    def setMotorVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getMotorVelocity(self, motor: int) -> float:
        """Returns the velocity of the indicated motor in ticks per second."""
        ...
    @overload
    def getMotorVelocity(self, motor: int, unit: AngleUnit) -> float:
        """Returns the velocity of the indicated motor."""
        ...
    def getMotorVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setPIDCoefficients(self, motor: int, mode: DcMotor.RunMode, pidCoefficients: PIDCoefficients) -> None:
        """Sets the coefficients used for PID control on the indicated motor when in the indicated mode"""
        ...

    def setPIDFCoefficients(self, motor: int, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> None:
        """Sets the coefficients used for PIDF control on the indicated motor when in the indicated mode"""
        ...

    def getPIDCoefficients(self, motor: int, mode: DcMotor.RunMode) -> PIDCoefficients:
        """Returns the coefficients used for PID control on the indicated motor when in the indicated mode"""
        ...

    def getPIDFCoefficients(self, motor: int, mode: DcMotor.RunMode) -> PIDFCoefficients:
        """Returns the coefficients used for PIDF control on the indicated motor when in the indicated mode"""
        ...

    def setMotorTargetPosition(self, motor: int, position: int, tolerance: int) -> None:
        """Sets the target position and tolerance for a 'run to position' operation."""
        ...

    def getMotorCurrent(self, motor: int, unit: CurrentUnit) -> float:
        """Returns the current consumed by the indicated motor."""
        ...

    def getMotorCurrentAlert(self, motor: int, unit: CurrentUnit) -> float:
        """Returns the current alert for the indicated motor."""
        ...

    def setMotorCurrentAlert(self, motor: int, current: float, unit: CurrentUnit) -> None:
        """Sets the current alert for the indicated motor"""
        ...

    def isMotorOverCurrent(self, motor: int) -> bool:
        """Returns whether the indicated motor current consumption has exceeded the alert threshold."""
        ...


class DcMotorEx(DcMotor):
    """The DcMotorEx interface provides enhanced motor functionality which is available with some hardware devices. The DcMotorEx interface is typically used as a second interface on an object whose primary interface is DcMotor. To access it, cast your DcMotor object to DcMotorEx. However, it is perhaps prudent to first test whether the cast will succeed by testing using 'instanceof'."""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorEx"
    def setMotorEnable(self) -> None:
        """Individually energizes this particular motor"""
        ...

    def setMotorDisable(self) -> None:
        """Individually de-energizes this particular motor"""
        ...

    def isMotorEnabled(self) -> bool:
        """Returns whether this motor is energized"""
        ...

    @overload
    def setVelocity(self, angularRate: float) -> None:
        """Sets the velocity of the motor"""
        ...
    @overload
    def setVelocity(self, angularRate: float, unit: AngleUnit) -> None:
        """Sets the velocity of the motor"""
        ...
    def setVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getVelocity(self) -> float:
        """Returns the current velocity of the motor, in ticks per second"""
        ...
    @overload
    def getVelocity(self, unit: AngleUnit) -> float:
        """Returns the current velocity of the motor, in angular units per second"""
        ...
    def getVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setPIDCoefficients(self, mode: DcMotor.RunMode, pidCoefficients: PIDCoefficients) -> None:
        """Sets the PID control coefficients for one of the PID modes of this motor. Note that in some controller implementations, setting the PID coefficients for one mode on a motor might affect other modes on that motor, or might affect the PID coefficients used by other motors on the same controller (this is not true on the REV Expansion Hub)."""
        ...

    def setPIDFCoefficients(self, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> None:
        """#setPIDFCoefficients is a superset enhancement to #setPIDCoefficients. In addition to the proportional, integral, and derivative coefficients previously supported, a feed-forward coefficient may also be specified. Further, a selection of motor control algorithms is offered: the originally-shipped Legacy PID algorithm, and a PIDF algorithm which avails itself of the feed-forward coefficient. Note that the feed-forward coefficient is not used by the Legacy PID algorithm; thus, the feed-forward coefficient must be indicated as zero if the Legacy PID algorithm is used. Also: the internal implementation of these algorithms may be different: it is not the case that the use of PIDF with the F term as zero necessarily exhibits exactly the same behavior as the use of the LegacyPID algorithm, though in practice they will be quite close. Readers are reminded that DcMotor.RunMode#RUN_TO_POSITION mode makes use of both the coefficients set for RUN_TO_POSITION and the coefficients set for RUN_WITH_ENCODER, due to the fact that internally the RUN_TO_POSITION logic calculates an on-the-fly velocity goal on each control cycle, then (logically) runs the RUN_WITH_ENCODER logic. Because of that double- layering, only the proportional ('p') coefficient makes logical sense for use in the RUN_TO_POSITION coefficients."""
        ...

    def setVelocityPIDFCoefficients(self, p: float, i: float, d: float, f: float) -> None:
        """A shorthand for setting the PIDF coefficients for the DcMotor.RunMode#RUN_USING_ENCODER mode. MotorControlAlgorithm#PIDF is used."""
        ...

    def setPositionPIDFCoefficients(self, p: float) -> None:
        """A shorthand for setting the PIDF coefficients for the DcMotor.RunMode#RUN_TO_POSITION mode. MotorControlAlgorithm#PIDF is used. Readers are reminded that DcMotor.RunMode#RUN_TO_POSITION mode makes use of both the coefficients set for RUN_TO_POSITION and the coefficients set for RUN_WITH_ENCODER, due to the fact that internally the RUN_TO_POSITION logic calculates an on-the-fly velocity goal on each control cycle, then (logically) runs the RUN_WITH_ENCODER logic. Because of that double- layering, only the proportional ('p') coefficient makes logical sense for use in the RUN_TO_POSITION coefficients."""
        ...

    def getPIDCoefficients(self, mode: DcMotor.RunMode) -> PIDCoefficients:
        """Returns the PID control coefficients used when running in the indicated mode on this motor."""
        ...

    def getPIDFCoefficients(self, mode: DcMotor.RunMode) -> PIDFCoefficients:
        """Returns the PIDF control coefficients used when running in the indicated mode on this motor."""
        ...

    def setTargetPositionTolerance(self, tolerance: int) -> None:
        """Sets the target positioning tolerance of this motor"""
        ...

    def getTargetPositionTolerance(self) -> int:
        """Returns the current target positioning tolerance of this motor"""
        ...

    def getCurrent(self, unit: CurrentUnit) -> float:
        """Returns the current consumed by this motor."""
        ...

    def getCurrentAlert(self, unit: CurrentUnit) -> float:
        """Returns the current alert for this motor."""
        ...

    def setCurrentAlert(self, current: float, unit: CurrentUnit) -> None:
        """Sets the current alert for this motor"""
        ...

    def isOverCurrent(self) -> bool:
        """Returns whether the current consumption of this motor exceeds the alert threshold."""
        ...


class DcMotorImpl(DcMotor):
    """Control a DC Motor attached to a DC Motor Controller"""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorImpl"
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int) -> None:
        """Constructor"""
        ...
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int, direction: DcMotorSimple.Direction) -> None:
        """Constructor"""
        ...
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int, direction: DcMotorSimple.Direction, motorType: MotorConfigurationType) -> None:
        """Constructor"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def getMotorType(self) -> MotorConfigurationType:
        ...

    def setMotorType(self, motorType: MotorConfigurationType) -> None:
        ...

    def getController(self) -> DcMotorController:
        """Get DC motor controller"""
        ...

    def setDirection(self, direction: DcMotorSimple.Direction) -> None:
        """Set the direction"""
        ...

    def getDirection(self) -> DcMotorSimple.Direction:
        """Get the direction"""
        ...

    def getPortNumber(self) -> int:
        """Get port number"""
        ...

    def setPower(self, power: float) -> None:
        """Set the current motor power"""
        ...

    def internalSetPower(self, power: float) -> None:
        ...

    def getPower(self) -> float:
        """Get the current motor power"""
        ...

    def isBusy(self) -> bool:
        """Is the motor busy?"""
        ...

    def setZeroPowerBehavior(self, zeroPowerBehavior: DcMotor.ZeroPowerBehavior) -> None:
        ...

    def getZeroPowerBehavior(self) -> DcMotor.ZeroPowerBehavior:
        ...

    def setPowerFloat(self) -> None:
        """Allow motor to float"""
        ...

    def getPowerFloat(self) -> bool:
        """Is motor power set to float?"""
        ...

    def setTargetPosition(self, position: int) -> None:
        """Set the motor target position, using an integer. If this motor has been set to REVERSE, the passed-in \"position\" value will be multiplied by -1."""
        ...

    def internalSetTargetPosition(self, position: int) -> None:
        ...

    def getTargetPosition(self) -> int:
        """Get the current motor target position. If this motor has been set to REVERSE, the returned \"position\" will be multiplied by -1."""
        ...

    def getCurrentPosition(self) -> int:
        """Get the current encoder value, accommodating the configured directionality of the motor."""
        ...

    def adjustPosition(self, position: int) -> int:
        ...

    def adjustPower(self, power: float) -> float:
        ...

    def getOperationalDirection(self) -> DcMotorSimple.Direction:
        ...

    def setMode(self, mode: DcMotor.RunMode) -> None:
        """Set the current mode"""
        ...

    def internalSetMode(self, mode: DcMotor.RunMode) -> None:
        ...

    def getMode(self) -> DcMotor.RunMode:
        """Get the current mode"""
        ...

    controller: DcMotorController
    portNumber: int
    direction: DcMotorSimple.Direction
    motorType: MotorConfigurationType


class DcMotorImplEx(DcMotorImpl, DcMotorEx):
    """DcMotorImplEx is a motor that supports the DcMotorEx interface in addition to simply DcMotor."""
    __java__ = "com.qualcomm.robotcore.hardware.DcMotorImplEx"
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int) -> None:
        ...
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int, direction: DcMotorSimple.Direction) -> None:
        ...
    @overload
    def __init__(self, controller: DcMotorController, portNumber: int, direction: DcMotorSimple.Direction, motorType: MotorConfigurationType) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def setMotorEnable(self) -> None:
        ...

    def setMotorDisable(self) -> None:
        ...

    def isMotorEnabled(self) -> bool:
        ...

    @overload
    def setVelocity(self, angularRate: float) -> None:
        ...
    @overload
    def setVelocity(self, angularRate: float, unit: AngleUnit) -> None:
        ...
    def setVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getVelocity(self) -> float:
        ...
    @overload
    def getVelocity(self, unit: AngleUnit) -> float:
        ...
    def getVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def adjustAngularRate(self, angularRate: float) -> float:
        ...

    def setPIDCoefficients(self, mode: DcMotor.RunMode, pidCoefficients: PIDCoefficients) -> None:
        ...

    def setPIDFCoefficients(self, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> None:
        ...

    def setVelocityPIDFCoefficients(self, p: float, i: float, d: float, f: float) -> None:
        ...

    def setPositionPIDFCoefficients(self, p: float) -> None:
        ...

    def getPIDCoefficients(self, mode: DcMotor.RunMode) -> PIDCoefficients:
        ...

    def getPIDFCoefficients(self, mode: DcMotor.RunMode) -> PIDFCoefficients:
        ...

    def getTargetPositionTolerance(self) -> int:
        ...

    def setTargetPositionTolerance(self, tolerance: int) -> None:
        ...

    def internalSetTargetPosition(self, position: int) -> None:
        ...

    def getCurrent(self, unit: CurrentUnit) -> float:
        ...

    def getCurrentAlert(self, unit: CurrentUnit) -> float:
        ...

    def setCurrentAlert(self, current: float, unit: CurrentUnit) -> None:
        ...

    def isOverCurrent(self) -> bool:
        ...

    controllerEx: DcMotorControllerEx
    targetPositionTolerance: int


class DeviceManager:
    __java__ = "com.qualcomm.robotcore.hardware.DeviceManager"
    class UsbDeviceType(enum.Enum):
        """Enum of known USB Device Types"""
        __java__ = "com.qualcomm.robotcore.hardware.DeviceManager.UsbDeviceType"
        FTDI_USB_UNKNOWN_DEVICE = enum.auto()
        LYNX_USB_DEVICE = enum.auto()
        WEBCAM = enum.auto()
        ETHERNET_DEVICE = enum.auto()
        UNKNOWN_DEVICE = enum.auto()
        @staticmethod
        def from_(string: str) -> DeviceManager.UsbDeviceType:
            ...

    def scanForUsbDevices(self) -> ScannedDevices:
        """Get a listing of currently connected USB devices"""
        ...

    def createDcMotor(self, controller: DcMotorController, portNumber: int, motorType: MotorConfigurationType, name: str) -> DcMotor:
        """Create an instance of a DcMotor"""
        ...

    def createDcMotorEx(self, controller: DcMotorController, portNumber: int, motorType: MotorConfigurationType, name: str) -> DcMotor:
        ...

    def createServoEx(self, controller: ServoControllerEx, portNumber: int, name: str, servoType: ServoConfigurationType) -> Servo:
        """Create an instance of a Servo"""
        ...

    def createCRServoEx(self, controller: ServoControllerEx, portNumber: int, name: str, servoType: ServoConfigurationType) -> CRServo:
        ...

    def createCustomServoDeviceInstances(self, controller: ServoControllerEx, portNumber: int, servoConfigurationType: ServoConfigurationType) -> list[HardwareDevice]:
        ...

    def createAnalogSensorInstances(self, controller: AnalogInputController, channel: int, type: AnalogSensorConfigurationType) -> list[HardwareDevice]:
        ...

    def createDigitalDeviceInstances(self, controller: DigitalChannelController, channel: int, type: DigitalIoDeviceConfigurationType) -> list[HardwareDevice]:
        ...

    def createPwmOutputDevice(self, controller: PWMOutputController, channel: int, name: str) -> PWMOutput:
        ...

    def createI2cDeviceSynch(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> I2cDeviceSynch:
        ...

    def createI2cDeviceInstances(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, type: I2cDeviceConfigurationType, name: str) -> list[HardwareDevice]:
        ...

    def createLimelight3A(self, serialNumber: SerialNumber, name: str, ipAddress: Any) -> HardwareDevice:
        """Creates a Limelight3A."""
        ...

    def createLynxUsbDevice(self, serialNumber: SerialNumber, name: str) -> RobotCoreLynxUsbDevice:
        """Creates an instance of a Lynx USB device"""
        ...

    def createWebcamName(self, serialNumber: SerialNumber, name: str) -> WebcamName:
        """Creates a WebcamName from the indicated serialized contents"""
        ...

    def createMRDigitalTouchSensor(self, digitalController: DigitalChannelController, physicalPort: int, name: str) -> TouchSensor:
        """Create an instance of a Modern Robotics TouchSensor on a digital controller"""
        ...

    def createMRI2cIrSeekerSensorV3(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> IrSeekerSensor:
        """Create an instance of a IrSeekerSensorV3"""
        ...

    def createModernRoboticsI2cGyroSensor(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> GyroSensor:
        """Create an instance of a GyroSensor"""
        ...

    def createAdafruitI2cColorSensor(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        """Create an instance of a ColorSensor"""
        ...

    def createLynxColorRangeSensor(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        ...

    def createModernRoboticsI2cColorSensor(self, module: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        """Create an instance of a ColorSensor"""
        ...

    def createLED(self, controller: DigitalChannelController, channel: int, name: str) -> LED:
        """Create an instance of an LED"""
        ...


class DigitalChannel(HardwareDevice):
    """DigitalChannel is an interface by which digital channels can be controlled. Such channels have a boolean state, and are modal as to direction, being either input channels or output channels."""
    __java__ = "com.qualcomm.robotcore.hardware.DigitalChannel"
    class Mode(enum.Enum):
        """Digital channel mode - input or output"""
        __java__ = "com.qualcomm.robotcore.hardware.DigitalChannel.Mode"
        INPUT = enum.auto()
        OUTPUT = enum.auto()

    def getMode(self) -> DigitalChannel.Mode:
        """Returns whether the channel is in input or output mode"""
        ...

    @overload
    def setMode(self, mode: DigitalChannel.Mode) -> None:
        """Changes whether the channel is in input or output mode"""
        ...
    @overload
    def setMode(self, mode: DigitalChannelController.Mode) -> None:
        ...
    def setMode(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getState(self) -> bool:
        """Returns the current state of the channel"""
        ...

    def setState(self, state: bool) -> None:
        """Sets the current state of the channel"""
        ...


class DigitalChannelController(HardwareDevice):
    """Interface for working with Digital Channel Controllers"""
    __java__ = "com.qualcomm.robotcore.hardware.DigitalChannelController"
    class Mode(enum.Enum):
        """Digital channel mode - input or output"""
        __java__ = "com.qualcomm.robotcore.hardware.DigitalChannelController.Mode"
        INPUT = enum.auto()
        OUTPUT = enum.auto()
        def migrate(self) -> DigitalChannel.Mode:
            ...

    def getSerialNumber(self) -> SerialNumber:
        """Serial Number"""
        ...

    def getDigitalChannelMode(self, channel: int) -> DigitalChannel.Mode:
        """Get the mode of a digital channel"""
        ...

    @overload
    def setDigitalChannelMode(self, channel: int, mode: DigitalChannel.Mode) -> None:
        """Set the mode of a digital channel"""
        ...
    @overload
    def setDigitalChannelMode(self, channel: int, mode: DigitalChannelController.Mode) -> None:
        ...
    def setDigitalChannelMode(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getDigitalChannelState(self, channel: int) -> bool:
        """Get the state of a digital channel If it's in OUTPUT mode, this will return the output bit. If the channel is in INPUT mode, this will return the input bit."""
        ...

    def setDigitalChannelState(self, channel: int, state: bool) -> None:
        """Set the state of a digital channel"""
        ...


class DigitalChannelImpl(DigitalChannel):
    """Control a single digital channel"""
    __java__ = "com.qualcomm.robotcore.hardware.DigitalChannelImpl"
    def __init__(self, controller: DigitalChannelController, channel: int) -> None:
        """Constructor"""
        ...

    def getMode(self) -> DigitalChannel.Mode:
        """Get the channel mode"""
        ...

    @overload
    def setMode(self, mode: DigitalChannel.Mode) -> None:
        """Set the channel mode"""
        ...
    @overload
    def setMode(self, mode: DigitalChannelController.Mode) -> None:
        ...
    def setMode(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getState(self) -> bool:
        """Get the channel state"""
        ...

    def setState(self, state: bool) -> None:
        """Set the channel state"""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...


class EmbeddedControlHubModule:
    """EmbeddedControlHubModule provides easy access to the Lynx module embedded in the Control Hub via a singleton"""
    __java__ = "com.qualcomm.robotcore.hardware.EmbeddedControlHubModule"
    @staticmethod
    def get() -> RobotCoreLynxModule:
        ...

    @staticmethod
    def set(lynxModule: RobotCoreLynxModule) -> None:
        ...

    @staticmethod
    def getImuType() -> LynxModuleImuType:
        ...

    @staticmethod
    def setImuType(imuType: LynxModuleImuType) -> None:
        ...

    @staticmethod
    def clear() -> None:
        ...

    TAG: str
    embeddedLynxModule: RobotCoreLynxModule
    embeddedImuType: LynxModuleImuType


class Engagable:
    """The engageable interface can be used to temporarily disengage higher-level hardware objects from the services they manipulate, then later be able to re-engage them. Objects which implement this interface include legacy motor and servo controllers."""
    __java__ = "com.qualcomm.robotcore.hardware.Engagable"
    def disengage(self) -> None:
        """Disengage the object from underlying services it uses to render its function. If the object is presently disenaged, this method has no effect."""
        ...

    def engage(self) -> None:
        """(Re)enage the object with its underlying services. If the object is presently engaged, this method has no effect."""
        ...

    def isEngaged(self) -> bool:
        """Returns whether the object is currently in the engaged state."""
        ...


class RobocolParsable:
    """Interface implemented by objects that want to be sendable via a RobocolDatagram."""
    __java__ = "com.qualcomm.robotcore.robocol.RobocolParsable"
    class MsgType(enum.Enum):
        """Message Type"""
        __java__ = "com.qualcomm.robotcore.robocol.RobocolParsable.MsgType"
        EMPTY = enum.auto()
        HEARTBEAT = enum.auto()
        GAMEPAD = enum.auto()
        PEER_DISCOVERY = enum.auto()
        COMMAND = enum.auto()
        TELEMETRY = enum.auto()
        KEEPALIVE = enum.auto()
        @staticmethod
        def fromByte(b: int) -> RobocolParsable.MsgType:
            """Create a MsgType from a byte"""
            ...

        def asByte(self) -> int:
            """Return this message type as a byte"""
            ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        """Get the Robocol MsgType of this RobocolParsable"""
        ...

    def getSequenceNumber(self) -> int:
        """Returns the sequence number of this packet. Newly-created packets are numbered in a monotonically increasing fashion, independently, on both driver station and robot controller; there are thus two numbering spaces. Note that though the value here reports as an int, only two bytes are used to transmit the sequence number. Reported values will thus be in the range of 0..65535."""
        ...

    def setSequenceNumber(self) -> None:
        """Sets/updates the sequence number of the parsable to be the next available value"""
        ...

    def shouldTransmit(self, nanotimeNow: int) -> bool:
        """Returns whether or not this parsable is due for a (re)transmisison"""
        ...

    def toByteArrayForTransmission(self) -> list[int]:
        """Serializes the object for the purposes of network transmission, which is assumed will take place virtually immediately. Internal state regarding the time of last transmission may thus be updated during this method."""
        ...

    def toByteArray(self) -> list[int]:
        """Serializes the object for the purposes other than network transmission, such as creating a local copy by a subsequent invocation of fromByteArray() into another instance."""
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        """Populate the fields of this object based on values of this byte array."""
        ...

    HEADER_LENGTH: int


class RobocolParsableBase(RobocolParsable):
    """RobocolParsableBase is an implementation base class for Robocol elements, providing functionality that is common to all such elements."""
    __java__ = "com.qualcomm.robotcore.robocol.RobocolParsableBase"
    def __init__(self) -> None:
        ...

    @staticmethod
    def initializeSequenceNumber(sequenceNumber: int) -> None:
        """A utility function that helps us separate driver station from robot controller packets"""
        ...

    def getSequenceNumber(self) -> int:
        ...

    @overload
    def setSequenceNumber(self, sequenceNumber: int) -> None:
        ...
    @overload
    def setSequenceNumber(self) -> None:
        ...
    def setSequenceNumber(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def toByteArrayForTransmission(self) -> list[int]:
        """Serialize, but also record timestamp if for transmission"""
        ...

    def shouldTransmit(self, nanotimeNow: int) -> bool:
        ...

    def allocateWholeWriteBuffer(self, overallSize: int) -> Any:
        ...

    def getWholeReadBuffer(self, byteArray: list[int]) -> Any:
        ...

    def getWriteBuffer(self, payloadSize: int) -> Any:
        ...

    def getReadBuffer(self, byteArray: list[int]) -> Any:
        ...

    sequenceNumber: int
    nanotimeTransmit: int
    nanotimeTransmitInterval: int
    nextSequenceNumber: Any


class Gamepad(RobocolParsableBase):
    """Monitor a hardware gamepad."""
    __java__ = "com.qualcomm.robotcore.hardware.Gamepad"
    class Type(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.Gamepad.Type"
        UNKNOWN = enum.auto()
        LOGITECH_F310 = enum.auto()
        XBOX_360 = enum.auto()
        SONY_PS4 = enum.auto()
        SONY_PS4_SUPPORTED_BY_KERNEL = enum.auto()

    class LegacyType(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.Gamepad.LegacyType"
        UNKNOWN = enum.auto()
        LOGITECH_F310 = enum.auto()
        XBOX_360 = enum.auto()
        SONY_PS4 = enum.auto()

    class LedEffect:
        __java__ = "com.qualcomm.robotcore.hardware.Gamepad.LedEffect"
        class Step:
            __java__ = "com.qualcomm.robotcore.hardware.Gamepad.LedEffect.Step"
            r: int
            g: int
            b: int
            duration: int

        class Builder:
            __java__ = "com.qualcomm.robotcore.hardware.Gamepad.LedEffect.Builder"
            def addStep(self, r: float, g: float, b: float, durationMs: int) -> Gamepad.LedEffect.Builder:
                """Add a \"step\" to this LED effect. A step basically just means to set the LED to a certain color (r,g,b) for a certain duration. By creating a chain of steps, you can create unique effects."""
                ...

            def setRepeating(self, repeating: bool) -> Gamepad.LedEffect.Builder:
                """Set whether this LED effect should loop after finishing, unless the LED is otherwise commanded differently."""
                ...

            def build(self) -> Gamepad.LedEffect:
                """After you've added your steps, call this to get an LedEffect object that you can then pass to #runLedEffect(LedEffect)"""
                ...

        def serialize(self) -> str:
            ...

        @staticmethod
        def deserialize(serialized: str) -> Gamepad.LedEffect:
            ...

        steps: list[Gamepad.LedEffect.Step]
        repeating: bool
        user: int

    class RumbleEffect:
        __java__ = "com.qualcomm.robotcore.hardware.Gamepad.RumbleEffect"
        class Step:
            __java__ = "com.qualcomm.robotcore.hardware.Gamepad.RumbleEffect.Step"
            large: int
            small: int
            duration: int

        class Builder:
            __java__ = "com.qualcomm.robotcore.hardware.Gamepad.RumbleEffect.Builder"
            def addStep(self, rumble1: float, rumble2: float, durationMs: int) -> Gamepad.RumbleEffect.Builder:
                """Add a \"step\" to this rumble effect. A step basically just means to rumble at a certain power level for a certain duration. By creating a chain of steps, you can create unique effects. See #rumbleBlips(int) for a a simple example."""
                ...

            def build(self) -> Gamepad.RumbleEffect:
                """After you've added your steps, call this to get a RumbleEffect object that you can then pass to #runRumbleEffect(RumbleEffect)"""
                ...

        def serialize(self) -> str:
            ...

        @staticmethod
        def deserialize(serialized: str) -> Gamepad.RumbleEffect:
            ...

        user: int
        steps: list[Gamepad.RumbleEffect.Step]

    def __init__(self) -> None:
        ...

    def setTriggerThreshold(self, threshold: float) -> None:
        """Set the threshold for determining if a trigger is pressed"""
        ...

    def getTriggerThreshold(self) -> float:
        """Get the threshold for determining if a trigger is pressed"""
        ...

    def getUser(self) -> GamepadUser:
        ...

    def setUser(self, user: GamepadUser) -> None:
        ...

    def setUserForEffects(self, userForEffects: int) -> None:
        ...

    def setGamepadId(self, id: int) -> None:
        ...

    def getGamepadId(self) -> int:
        ...

    def setTimestamp(self, timestamp: int) -> None:
        """Sets the time at which this Gamepad last changed its state, in the android.os.SystemClock#uptimeMillis time base."""
        ...

    def refreshTimestamp(self) -> None:
        """Refreshes the Gamepad's timestamp to be the current time."""
        ...

    def copy(self, gamepad: Gamepad) -> None:
        """Copy the state of a gamepad into this gamepad"""
        ...

    def reset(self) -> None:
        """Reset this gamepad into its initial state"""
        ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        ...

    def toByteArray(self) -> list[int]:
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        ...

    def atRest(self) -> bool:
        """Are all analog sticks and triggers in their rest position?"""
        ...

    def type(self) -> Gamepad.Type:
        """Get the type of gamepad as a Type. This method defaults to \"UNKNOWN\"."""
        ...

    def toString(self) -> str:
        """Display a summary of this gamepad, including the state of all buttons, analog sticks, and triggers"""
        ...

    def ps4ToString(self) -> str:
        ...

    def genericToString(self) -> str:
        ...

    def setLedColor(self, r: float, g: float, b: float, durationMs: int) -> None:
        ...

    def runLedEffect(self, effect: Gamepad.LedEffect) -> None:
        """Run an LED effect built using LedEffect.Builder The LED effect will be run asynchronously; your OpMode will not halt execution while the effect is running. Calling this will displace any currently running LED effect"""
        ...

    def runRumbleEffect(self, effect: Gamepad.RumbleEffect) -> None:
        """Run a rumble effect built using RumbleEffect.Builder The rumble effect will be run asynchronously; your OpMode will not halt execution while the effect is running. Calling this will displace any currently running rumble effect"""
        ...

    @overload
    def rumble(self, durationMs: int) -> None:
        """Rumble the gamepad's first rumble motor at maximum power for a certain duration. Calling this will displace any currently running rumble effect."""
        ...
    @overload
    def rumble(self, rumble1: float, rumble2: float, durationMs: int) -> None:
        """Rumble the gamepad at a fixed rumble power for a certain duration Calling this will displace any currently running rumble effect"""
        ...
    def rumble(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def stopRumble(self) -> None:
        """Cancel the currently running rumble effect, if any"""
        ...

    def rumbleBlips(self, count: int) -> None:
        """Rumble the gamepad for a certain number of \"blips\" using predetermined blip timing This will displace any currently running rumble effect."""
        ...

    def isRumbling(self) -> bool:
        """Returns an educated guess about whether there is a rumble action ongoing on this gamepad"""
        ...

    def updateButtonAliases(self) -> None:
        """Alias buttons so that XBOX &amp; PS4 native button labels can be used in use code. Should allow a team to program with whatever controllers they prefer, but be able to swap controllers easily without changing code."""
        ...

    def resetEdgeDetection(self) -> None:
        """Clears any remembered presses and releases of buttons"""
        ...

    def dpadUpWasPressed(self) -> bool:
        """Checks if dpad_up was pressed since the last call of this method"""
        ...

    def dpadUpWasReleased(self) -> bool:
        """Checks if dpad_up was released since the last call of this method"""
        ...

    def dpadDownWasPressed(self) -> bool:
        """Checks if dpad_down was pressed since the last call of this method"""
        ...

    def dpadDownWasReleased(self) -> bool:
        """Checks if dpad_down was released since the last call of this method"""
        ...

    def dpadLeftWasPressed(self) -> bool:
        """Checks if dpad_left was pressed since the last call of this method"""
        ...

    def dpadLeftWasReleased(self) -> bool:
        """Checks if dpad_left was released since the last call of this method"""
        ...

    def dpadRightWasPressed(self) -> bool:
        """Checks if dpad_right was pressed since the last call of this method"""
        ...

    def dpadRightWasReleased(self) -> bool:
        """Checks if dpad_right was released since the last call of this methmethodod"""
        ...

    def aWasPressed(self) -> bool:
        """Checks if a was pressed since the last call of this method"""
        ...

    def aWasReleased(self) -> bool:
        """Checks if a was released since the last call of this method"""
        ...

    def bWasPressed(self) -> bool:
        """Checks if b was pressed since the last call of this method"""
        ...

    def bWasReleased(self) -> bool:
        """Checks if b was released since the last call of this method"""
        ...

    def xWasPressed(self) -> bool:
        """Checks if x was pressed since the last call of this method"""
        ...

    def xWasReleased(self) -> bool:
        """Checks if x was released since the last call of this method"""
        ...

    def yWasPressed(self) -> bool:
        """Checks if y was pressed since the last call of this method"""
        ...

    def yWasReleased(self) -> bool:
        """Checks if y was released since the last call of this method"""
        ...

    def guideWasPressed(self) -> bool:
        """Checks if guide was pressed since the last call of this method"""
        ...

    def guideWasReleased(self) -> bool:
        """Checks if guide was released since the last call of this method"""
        ...

    def startWasPressed(self) -> bool:
        """Checks if start was pressed since the last call of this method"""
        ...

    def startWasReleased(self) -> bool:
        """Checks if start was released since the last call of this method"""
        ...

    def backWasPressed(self) -> bool:
        """Checks if back was pressed since the last call of this method"""
        ...

    def backWasReleased(self) -> bool:
        """Checks if back was released since the last call of this method"""
        ...

    def leftBumperWasPressed(self) -> bool:
        """Checks if left_bumper was pressed since the last call of this method"""
        ...

    def leftBumperWasReleased(self) -> bool:
        """Checks if left_bumper was released since the last call of this method"""
        ...

    def rightBumperWasPressed(self) -> bool:
        """Checks if right_bumper was pressed since the last call of this method"""
        ...

    def rightBumperWasReleased(self) -> bool:
        """Checks if right_bumper was released since the last call of this method"""
        ...

    def leftStickButtonWasPressed(self) -> bool:
        """Checks if left_stick_button was pressed since the last call of this method"""
        ...

    def leftStickButtonWasReleased(self) -> bool:
        """Checks if left_stick_button was released since the last call of this method"""
        ...

    def rightStickButtonWasPressed(self) -> bool:
        """Checks if right_stick_button was pressed since the last call of this method"""
        ...

    def rightStickButtonWasReleased(self) -> bool:
        """Checks if right_stick_button was released since the last call of this method"""
        ...

    def circleWasPressed(self) -> bool:
        """Checks if circle was pressed since the last call of this method"""
        ...

    def circleWasReleased(self) -> bool:
        """Checks if circle was released since the last call of this method"""
        ...

    def crossWasPressed(self) -> bool:
        """Checks if cross was pressed since the last call of this method"""
        ...

    def crossWasReleased(self) -> bool:
        """Checks if cross was released since the last call of this method"""
        ...

    def triangleWasPressed(self) -> bool:
        """Checks if triangle was pressed since the last call of this method"""
        ...

    def triangleWasReleased(self) -> bool:
        """Checks if triangle was released since the last call of this method"""
        ...

    def squareWasPressed(self) -> bool:
        """Checks if square was pressed since the last call of this method"""
        ...

    def squareWasReleased(self) -> bool:
        """Checks if square was released since the last call of this method"""
        ...

    def shareWasPressed(self) -> bool:
        """Checks if share was pressed since the last call of this method"""
        ...

    def shareWasReleased(self) -> bool:
        """Checks if share was released since the last call of this method"""
        ...

    def optionsWasPressed(self) -> bool:
        """Checks if options was pressed since the last call of this method"""
        ...

    def optionsWasReleased(self) -> bool:
        """Checks if options was released since the last call of this method"""
        ...

    def touchpadWasPressed(self) -> bool:
        """Checks if touchpad was pressed since the last call of this method"""
        ...

    def touchpadWasReleased(self) -> bool:
        """Checks if touchpad was released since the last call of this method"""
        ...

    def psWasPressed(self) -> bool:
        """Checks if ps was pressed since the last call of this method"""
        ...

    def psWasReleased(self) -> bool:
        """Checks if ps was released since the last call of this method"""
        ...

    def leftTriggerWasPressed(self) -> bool:
        """Checks if left_trigger was pressed since the last call of this method"""
        ...

    def leftTriggerWasReleased(self) -> bool:
        """Checks if left_trigger was released since the last call of this method"""
        ...

    def rightTriggerWasPressed(self) -> bool:
        """Checks if right_trigger was pressed since the last call of this method"""
        ...

    def rightTriggerWasReleased(self) -> bool:
        """Checks if right_trigger was released since the last call of this method"""
        ...

    ID_UNASSOCIATED: int
    """A gamepad with an ID equal to ID_UNASSOCIATED has not been associated with any device."""
    ID_SYNTHETIC: int
    """A gamepad with a phantom id a synthetic one made up by the system"""
    type_: Gamepad.Type
    left_stick_x: float
    """left analog stick horizontal axis"""
    left_stick_y: float
    """left analog stick vertical axis"""
    right_stick_x: float
    """right analog stick horizontal axis"""
    right_stick_y: float
    """right analog stick vertical axis"""
    dpad_up: bool
    """dpad up"""
    dpad_down: bool
    """dpad down"""
    dpad_left: bool
    """dpad left"""
    dpad_right: bool
    """dpad right"""
    a: bool
    """button a"""
    b: bool
    """button b"""
    x: bool
    """button x"""
    y: bool
    """button y"""
    guide: bool
    """button guide - often the large button in the middle of the controller. The OS may capture this button before it is sent to the app; in which case you'll never receive it."""
    start: bool
    """button start"""
    back: bool
    """button back"""
    left_bumper: bool
    """button left bumper"""
    right_bumper: bool
    """button right bumper"""
    left_stick_button: bool
    """left stick button"""
    right_stick_button: bool
    """right stick button"""
    left_trigger: float
    """left trigger"""
    right_trigger: float
    """right trigger"""
    DEFAULT_TRIGGER_THRESHOLD: float
    """default threshold for triggers being pressed"""
    left_trigger_pressed: bool
    """left trigger past threshold"""
    right_trigger_pressed: bool
    """right trigger past threshold"""
    circle: bool
    """PS4 Support - Circle"""
    cross: bool
    """PS4 Support - cross"""
    triangle: bool
    """PS4 Support - triangle"""
    square: bool
    """PS4 Support - square"""
    share: bool
    """PS4 Support - share"""
    options: bool
    """PS4 Support - options"""
    touchpad: bool
    """PS4 Support - touchpad"""
    touchpad_finger_1: bool
    touchpad_finger_2: bool
    touchpad_finger_1_x: float
    touchpad_finger_1_y: float
    touchpad_finger_2_x: float
    touchpad_finger_2_y: float
    ps: bool
    """PS4 Support - PS Button"""
    user: int
    """Which user is this gamepad used by"""
    userForEffects: int
    """See OpModeManagerImpl#runActiveOpMode(Gamepad[])"""
    id: int
    """ID assigned to this gamepad by the OS. This value can change each time the device is plugged in."""
    timestamp: int
    """Relative timestamp of the last time an event was detected"""
    ledQueue: EvictingBlockingQueue[Gamepad.LedEffect]
    LED_DURATION_CONTINUOUS: int
    rumbleQueue: EvictingBlockingQueue[Gamepad.RumbleEffect]
    nextRumbleApproxFinishTime: int
    RUMBLE_DURATION_CONTINUOUS: int


class GamepadStateChanges:
    """Monitors changes to buttons on a Gamepad."""
    __java__ = "com.qualcomm.robotcore.hardware.GamepadStateChanges"
    class ButtonStateMonitor:
        __java__ = "com.qualcomm.robotcore.hardware.GamepadStateChanges.ButtonStateMonitor"
        def wasPressed(self) -> bool:
            ...

        def wasReleased(self) -> bool:
            ...

    def updateAllButtons(self, gamepad: Gamepad) -> None:
        ...

    dpadUp: GamepadStateChanges.ButtonStateMonitor
    dpadDown: GamepadStateChanges.ButtonStateMonitor
    dpadLeft: GamepadStateChanges.ButtonStateMonitor
    dpadRight: GamepadStateChanges.ButtonStateMonitor
    a: GamepadStateChanges.ButtonStateMonitor
    b: GamepadStateChanges.ButtonStateMonitor
    x: GamepadStateChanges.ButtonStateMonitor
    y: GamepadStateChanges.ButtonStateMonitor
    guide: GamepadStateChanges.ButtonStateMonitor
    start: GamepadStateChanges.ButtonStateMonitor
    back: GamepadStateChanges.ButtonStateMonitor
    leftBumper: GamepadStateChanges.ButtonStateMonitor
    rightBumper: GamepadStateChanges.ButtonStateMonitor
    leftStickButton: GamepadStateChanges.ButtonStateMonitor
    rightStickButton: GamepadStateChanges.ButtonStateMonitor
    circle: GamepadStateChanges.ButtonStateMonitor
    cross: GamepadStateChanges.ButtonStateMonitor
    triangle: GamepadStateChanges.ButtonStateMonitor
    square: GamepadStateChanges.ButtonStateMonitor
    share: GamepadStateChanges.ButtonStateMonitor
    options: GamepadStateChanges.ButtonStateMonitor
    touchpad: GamepadStateChanges.ButtonStateMonitor
    ps: GamepadStateChanges.ButtonStateMonitor
    leftTrigger: GamepadStateChanges.ButtonStateMonitor
    rightTrigger: GamepadStateChanges.ButtonStateMonitor


class GyroSensor(HardwareDevice):
    """Gyro Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.GyroSensor"
    def calibrate(self) -> None:
        """Calibrate the gyro. For the Modern Robotics device this will null, or reset, the Z axis heading."""
        ...

    def isCalibrating(self) -> bool:
        """Is the gyro performing a calibration operation?"""
        ...

    def getHeading(self) -> int:
        """Return the integrated Z axis as a cartesian heading."""
        ...

    def getRotationFraction(self) -> float:
        """Return the rotation of this sensor expressed as a fraction of the maximum possible reportable rotation"""
        ...

    def rawX(self) -> int:
        """Return the gyro's raw X value."""
        ...

    def rawY(self) -> int:
        """Return the gyro's raw Y value."""
        ...

    def rawZ(self) -> int:
        """Return the gyro's raw Z value."""
        ...

    def resetZAxisIntegrator(self) -> None:
        """Set the integrated Z axis to zero."""
        ...

    def status(self) -> str:
        """Status of this sensor, in string form"""
        ...


class Gyroscope:
    """The Gyroscope interface exposes core, fundamental functionality that is applicable to all gyroscopes: that of reporting angular rotation rate."""
    __java__ = "com.qualcomm.robotcore.hardware.Gyroscope"
    def getAngularVelocityAxes(self) -> set[Axis]:
        """Returns the axes on which the gyroscope measures angular velocity. Some gyroscopes measure angular velocity on all three axes (X, Y, &amp; Z) while others measure on only a subset, typically the Z axis. This method allows you to determine what information is usefully returned through #getAngularVelocity(AngleUnit)."""
        ...

    def getAngularVelocity(self, unit: AngleUnit) -> AngularVelocity:
        """Returns the angular rotation rate across all the axes measured by the gyro. Axes on which angular velocity is not measured are reported as zero."""
        ...


class HardwareDeviceCloseOnTearDown:
    """Instances of HardwareDeviceCloseOnTearDown are those which should be automatically closed when we we 'teardown' a robot"""
    __java__ = "com.qualcomm.robotcore.hardware.HardwareDeviceCloseOnTearDown"
    def close(self) -> None:
        ...


class HardwareDeviceHealth:
    """HardwareDeviceHealth provides an indication of the perceived health of a hardware device"""
    __java__ = "com.qualcomm.robotcore.hardware.HardwareDeviceHealth"
    class HealthStatus(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.HardwareDeviceHealth.HealthStatus"
        UNKNOWN = enum.auto()
        HEALTHY = enum.auto()
        UNHEALTHY = enum.auto()
        CLOSED = enum.auto()

    def setHealthStatus(self, status: HardwareDeviceHealth.HealthStatus) -> None:
        ...

    def getHealthStatus(self) -> HardwareDeviceHealth.HealthStatus:
        ...


class HardwareDeviceHealthImpl(HardwareDeviceHealth):
    """HardwareDeviceHealthImpl provides a delegatable-to implemenatation of HardwareDeviceHealth"""
    __java__ = "com.qualcomm.robotcore.hardware.HardwareDeviceHealthImpl"
    @overload
    def __init__(self, tag: str) -> None:
        ...
    @overload
    def __init__(self, tag: str, override: Any) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def close(self) -> None:
        ...

    def setHealthStatus(self, status: HardwareDeviceHealth.HealthStatus) -> None:
        ...

    def getHealthStatus(self) -> HardwareDeviceHealth.HealthStatus:
        ...

    tag: str
    healthStatus: HardwareDeviceHealth.HealthStatus
    override: Any


class HardwareMap:
    """HardwareMap provides a means of retrieving runtime HardwareDevice instances according to the names with which the corresponding physical devices were associated during robot configuration. A HardwareMap also contains an associated application context in which it was instantiated. Through their com.qualcomm.robotcore.eventloop.opmode.OpMode#hardwareMap, this provides access to a Context for OpModes, as such an appropriate instance is needed by various system APIs. Retrieving devices from a HardwareMap will initialize them if they have not already been initialized, which may take some time. As a result, you should ONLY access a HardwareMap from the Init phase of your OpMode."""
    __java__ = "com.qualcomm.robotcore.hardware.HardwareMap"
    class DeviceMapping(Generic[DEVICE_TYPE]):
        """A DeviceMapping contains a subcollection of the devices registered in a HardwareMap comprised of all the devices of a particular device type."""
        __java__ = "com.qualcomm.robotcore.hardware.HardwareMap.DeviceMapping"
        def __init__(self, deviceTypeClass: type[DEVICE_TYPE]) -> None:
            ...

        def getDeviceTypeClass(self) -> type[DEVICE_TYPE]:
            """Returns the runtime device type for this mapping"""
            ...

        def cast(self, obj: object) -> DEVICE_TYPE:
            """A small utility that assists in keeping the Java generics type system happy"""
            ...

        def get(self, deviceName: str) -> DEVICE_TYPE:
            """Retrieves the device in this DeviceMapping with the indicated name. If no such device is found, an exception is thrown."""
            ...

        @overload
        def put(self, deviceName: str, device: DEVICE_TYPE) -> None:
            """Registers a new device in this DeviceMapping under the indicated name. Any existing device with this name in this DeviceMapping is removed. The new device is also added to the overall collection in the overall map itself. Note that this method is normally called only by code in the SDK itself, not by user code."""
            ...
        @overload
        def put(self, serialNumber: SerialNumber, deviceName: str, device: DEVICE_TYPE) -> None:
            """(Advanced) Registers a new device in this DeviceMapping under the indicated name. Any existing device with this name in this DeviceMapping is removed. The new device is also added to the overall collection in the overall map itself. Note that this method is normally called only by code in the SDK itself, not by user code."""
            ...
        def put(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def internalPut(self, serialNumber: SerialNumber, deviceName: str, device: DEVICE_TYPE) -> None:
            ...

        def putLocal(self, deviceName: str, device: DEVICE_TYPE) -> None:
            ...

        def contains(self, deviceName: str) -> bool:
            """Returns whether a device of the indicated name is contained within this mapping"""
            ...

        @overload
        def remove(self, deviceName: str) -> bool:
            """(Advanced) Removes the device with the indicated name (if any) from this DeviceMapping. The device is also removed under that name in the overall map itself. Note that this method is normally called only by code in the SDK itself, not by user code."""
            ...
        @overload
        def remove(self, serialNumber: SerialNumber, deviceName: str) -> bool:
            """(Advanced) Removes the device with the indicated name (if any) from this DeviceMapping. The device is also removed under that name in the overall map itself. Note that this method is normally called only by code in the SDK itself, not by user code."""
            ...
        def remove(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def iterator(self) -> Any:
            """Returns an iterator over all the devices in this DeviceMapping. This will initialize any un-initialized devices in the DeviceMapping, so you should ONLY call it during the Init phase of your OpMode."""
            ...

        def entrySet(self) -> set[Any]:
            """Returns a collection of all the (name, device) pairs in this DeviceMapping. This will initialize any un-initialized devices in the DeviceMapping, so you should ONLY call it during the Init phase of your OpMode."""
            ...

        def size(self) -> int:
            ...

    class DeviceInstanceHolder:
        __java__ = "com.qualcomm.robotcore.hardware.HardwareMap.DeviceInstanceHolder"
        def __init__(self, instance: HardwareDevice) -> None:
            ...

        hasBeenRetrieved: bool
        instance: HardwareDevice

    class DeviceInstancesFromSingleConfigEntry:
        """ALL device instances in this data structure come from the SAME configuration entry. Each instance was created from a different driver class."""
        __java__ = "com.qualcomm.robotcore.hardware.HardwareMap.DeviceInstancesFromSingleConfigEntry"
        def __init__(self, driverInstances: list[HardwareDevice]) -> None:
            ...

        def warnIfOtherDriverHasBeenRetrieved(self, hardwareDevice: HardwareDevice, name: str) -> bool:
            ...

        deviceInstanceHolders: list[HardwareMap.DeviceInstanceHolder]

    def __init__(self, appContext: Any, notifier: OpModeManagerNotifier) -> None:
        ...

    @overload
    def get(self, classOrInterface: type[T], deviceName: str) -> T:
        """Retrieves the (first) device with the indicated name which is also an instance of the indicated class or interface. If no such device is found, an exception is thrown. Example:"""
        ...
    @overload
    def get(self, classOrInterface: type[T], serialNumber: SerialNumber) -> T:
        """(Advanced) Returns the device with the indicated SerialNumber, if it exists, cast to the indicated class or interface; otherwise, null."""
        ...
    @overload
    def get(self, deviceName: str) -> HardwareDevice:
        """Returns the (first) device with the indicated name. If no such device is found, an exception is thrown. If the found device is an I2C device, it will be initialized at this time if it has not already been initialized, which for some devices may take a second or more."""
        ...
    def get(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def tryGet(self, classOrInterface: type[T], deviceName: str) -> T:
        """Retrieves the (first) device with the indicated name which is also an instance of the indicated class or interface. If no such device is found, null is returned."""
        ...

    def getAll(self, classOrInterface: type[T]) -> list[T]:
        """Returns all the devices which are instances of the indicated class or interface. Any I2C devices that are found will be initialized at this time if they have not already been initialized, which for some devices may take a second or more."""
        ...

    def getAllNames(self, classOrInterface: type[HardwareDevice]) -> set[str]:
        """Returns all the names of all the devices which are instances of the indicated class or interface."""
        ...

    @overload
    def put(self, deviceName: str, device: HardwareDevice) -> None:
        """Puts a device in the overall map without having it also reside in a type-specific DeviceMapping."""
        ...
    @overload
    def put(self, deviceName: str, deviceInstances: list[HardwareDevice]) -> None:
        """(Advanced) Puts multiple HardwareDevice instances for the same configuration entry in the overall map without having them also reside in a type-specific DeviceMapping."""
        ...
    @overload
    def put(self, serialNumber: SerialNumber, deviceName: str, device: HardwareDevice) -> None:
        """(Advanced) Puts a device in the overall map without having it also reside in a type-specific DeviceMapping."""
        ...
    def put(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def internalPut(self, serialNumber: SerialNumber, deviceName: str, device: HardwareDevice) -> None:
        ...

    @overload
    def remove(self, deviceName: str, device: HardwareDevice) -> bool:
        """(Advanced) Removes a device from the overall map, if present. If the device is also present in a DeviceMapping, then the device should be removed using DeviceMapping#remove instead of calling this method. This is normally called only by code in the SDK itself, not by user code."""
        ...
    @overload
    def remove(self, serialNumber: SerialNumber, deviceName: str, device: HardwareDevice) -> bool:
        """(Advanced) Removes a device from the overall map, if present. If the device is also present in a DeviceMapping, then the device should be removed using DeviceMapping#remove instead of calling this method. This is normally called only by code in the SDK itself, not by user code."""
        ...
    def remove(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getNamesOf(self, device: HardwareDevice) -> set[str]:
        """Returns all the names by which the device is known. Virtually always, there is but a single name."""
        ...

    def recordDeviceName(self, deviceName: str, device: HardwareDevice) -> None:
        ...

    def rebuildDeviceNamesIfNecessary(self) -> None:
        ...

    def size(self) -> int:
        ...

    def iterator(self) -> Any:
        """Returns an iterator of all the devices in the HardwareMap. This function will initialize ALL devices in the HardwareMap if they are not initialized already, so try to avoid using it (whether directly or indirectly by treating HardwareMap as an Iterable)."""
        ...

    def unsafeIterable(self) -> Any:
        """Returns an Iterable for all the devices in the HardwareMap. This function will NOT ensure that all devices have been initialized, so this is NOT recommended for use by end users."""
        ...

    def logDevices(self) -> None:
        ...

    dcMotorController: HardwareMap.DeviceMapping[DcMotorController]
    dcMotor: HardwareMap.DeviceMapping[DcMotor]
    servoController: HardwareMap.DeviceMapping[ServoController]
    servo: HardwareMap.DeviceMapping[Servo]
    crservo: HardwareMap.DeviceMapping[CRServo]
    touchSensorMultiplexer: HardwareMap.DeviceMapping[TouchSensorMultiplexer]
    analogInput: HardwareMap.DeviceMapping[AnalogInput]
    digitalChannel: HardwareMap.DeviceMapping[DigitalChannel]
    opticalDistanceSensor: HardwareMap.DeviceMapping[OpticalDistanceSensor]
    touchSensor: HardwareMap.DeviceMapping[TouchSensor]
    pwmOutput: HardwareMap.DeviceMapping[PWMOutput]
    i2cDevice: HardwareMap.DeviceMapping[I2cDevice]
    i2cDeviceSynch: HardwareMap.DeviceMapping[I2cDeviceSynch]
    colorSensor: HardwareMap.DeviceMapping[ColorSensor]
    led: HardwareMap.DeviceMapping[LED]
    accelerationSensor: HardwareMap.DeviceMapping[AccelerationSensor]
    compassSensor: HardwareMap.DeviceMapping[CompassSensor]
    gyroSensor: HardwareMap.DeviceMapping[GyroSensor]
    irSeekerSensor: HardwareMap.DeviceMapping[IrSeekerSensor]
    lightSensor: HardwareMap.DeviceMapping[LightSensor]
    ultrasonicSensor: HardwareMap.DeviceMapping[UltrasonicSensor]
    voltageSensor: HardwareMap.DeviceMapping[VoltageSensor]
    allDevicesMap: dict[str, list[HardwareDevice]]
    allDevicesList: list[HardwareDevice]
    deviceNames: dict[HardwareDevice, set[str]]
    serialNumberMap: dict[SerialNumber, HardwareDevice]
    devicesWithMultipleDriversMap: dict[str, list[HardwareMap.DeviceInstancesFromSingleConfigEntry]]
    allDeviceMappings: list[HardwareMap.DeviceMapping[HardwareDevice]]
    appContext: Any
    lock: object


class I2cAddr:
    """I2cAddr represents an address on an I2C bus."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cAddr"
    def __init__(self, i2cAddr7Bit: int) -> None:
        ...

    @staticmethod
    def zero() -> I2cAddr:
        ...

    @staticmethod
    def create7bit(i2cAddr7Bit: int) -> I2cAddr:
        ...

    @staticmethod
    def create8bit(i2cAddr8Bit: int) -> I2cAddr:
        ...

    def get8Bit(self) -> int:
        ...

    def get7Bit(self) -> int:
        ...


class I2cAddressableDevice:
    """I2cAddressableDevice provides a means by which the address of a device living on an I2C bus can be retrieved."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cAddressableDevice"
    def getI2cAddress(self) -> I2cAddr:
        """Returns the I2C address currently in use to communicate with an I2C hardware device"""
        ...


class I2cAddrConfig(I2cAddressableDevice):
    """I2cAddrConfig allows the runtime I2C address used with a sensor to be changed or queried. Note that this does not affect the address that the actual hardware sensor responds to on the I2C bus; rather, it configures software to interact with a a hardware sensor living at a different I2C address than the one at which the software is configured to use by default."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cAddrConfig"
    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        """Configures a new I2C address to use"""
        ...


class I2cDevice(HardwareDevice):
    """The I2cDevice interface abstracts the engine used to interact on with a specific I2c device"""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDevice"
    def enableI2cReadMode(self, i2cAddr: I2cAddr, register: int, count: int) -> None:
        """Enable read mode for this I2C device. This simply sets bytes in the header of the write-cache; it does not enqueue or transmit any data."""
        ...

    def enableI2cWriteMode(self, i2cAddr: I2cAddr, register: int, count: int) -> None:
        """Enable write mode for this I2C device. This simply sets bytes in the header of the write-cache; it does not enqueue or transmit any data."""
        ...

    def isI2cPortInReadMode(self) -> bool:
        """Queries whether or not the controller has reported that it is in read mode."""
        ...

    def isI2cPortInWriteMode(self) -> bool:
        """Queries whether or not the controller has reported that it is in write mode."""
        ...

    def readI2cCacheFromController(self) -> None:
        """Enqueue a request to the controller to read the range of data from the HW device that was previously indicated in #enableI2cReadMode(I2cAddr, and subsequently written to the controller."""
        ...

    def writeI2cCacheToController(self) -> None:
        """Enqueue a request to the controller to write the current contents of the write cache to the HW device."""
        ...

    def writeI2cPortFlagOnlyToController(self) -> None:
        """Enqueue a request to the controller to reissue the previous i2c transaction to the HW device."""
        ...

    def setI2cPortActionFlag(self) -> None:
        """Set the flag in the write cache that indicates that when the write cache is next transferred to the controller an i2c transaction should take place. This will be either a read transaction or a write transaction according to whether the #enableI2cReadMode(I2cAddr, or #enableI2cWriteMode(I2cAddr, has most recently been called."""
        ...

    def isI2cPortActionFlagSet(self) -> bool:
        """Returns whether the action flag is set in the read cache. This is rarely what is actually desired by the I2cDevice client; it's use generally should be avoided."""
        ...

    def clearI2cPortActionFlag(self) -> None:
        """Clears the flag that #setI2cPortActionFlag() sets"""
        ...

    def getI2cReadCache(self) -> list[int]:
        """Returns access to the read-cache into which data from the controller is read. The returned byte array may be retained for repeated use; #getI2cReadCache() need not be repeatedly called. The lock returned by #getI2cReadCacheLock() must be held whenever the data in the returned byte array is accessed. Note that the returned byte array contains an initial header section, four bytes in size, which contains the information manipulated by #enableI2cReadMode(I2cAddr, and #enableI2cWriteMode(I2cAddr,."""
        ...

    def getI2cReadCacheTimeWindow(self) -> TimeWindow:
        """Returns the time window object into which time stamps are written when the read cache is updated"""
        ...

    def getI2cReadCacheLock(self) -> Any:
        """Returns access to the lock controlling the read-cache. This lock must be held a while the data accessible from #getI2cReadCache() is accessed."""
        ...

    def getI2cWriteCache(self) -> list[int]:
        """Returns access to the write-cache from which data is written to the controller. The returned byte array may be retained for repeated use; #getI2cWriteCache() need not be repeatedly called. The lock returned by #getI2cWriteCacheLock() must be held whenever the data in the returned byte array is accessed or written. Note that the returned byte array contains an inital header section, four bytes in size, which contains the information manipulated by #enableI2cReadMode(I2cAddr, and #enableI2cWriteMode(I2cAddr,."""
        ...

    def getI2cWriteCacheLock(self) -> Any:
        """Returns access to the lock controlling the write-cache. This lock must be held a while the data accessible from #getI2cWriteCache() is accessed"""
        ...

    def getCopyOfReadBuffer(self) -> list[int]:
        """Atomically returns a copy of that portion of the read-cache which does not include the initial four-byte header section: that contains the read payload most recently read from the controller. The read-cache lock need not be held while executing this method."""
        ...

    def getCopyOfWriteBuffer(self) -> list[int]:
        """Atomically returns a copy that portion of the write-cache which does not include the initial four-byte header section. The write-cache lock need not be held to execute this method."""
        ...

    def copyBufferIntoWriteBuffer(self, buffer: list[int]) -> None:
        """Atomically copies the provided buffer into the user portion of the write cache, beginning immediately following the four-byte header. The write-cache lock need not be held to execute this method."""
        ...

    def getMaxI2cWriteLatency(self) -> int:
        """Returns the maximum interval, in milliseconds, from when the controller receives an I2c write transmission over USB to when that write is actually issued to the I2c device."""
        ...

    def isArmed(self) -> bool:
        """Returns whether, as of this instant, this I2cDevice is alive and operational in its normally expected mode; that is, whether it is currently in communication with its underlying hardware or whether it is in some other state"""
        ...

    def readI2cCacheFromModule(self) -> None:
        ...

    def writeI2cCacheToModule(self) -> None:
        ...

    def writeI2cPortFlagOnlyToModule(self) -> None:
        ...


class RobotConfigNameable(HardwareDevice):
    """RobotConfigNameable provides access to the name by which a device has been configured within a robot configuration"""
    __java__ = "com.qualcomm.robotcore.hardware.RobotConfigNameable"
    def setUserConfiguredName(self, name: str) -> None:
        """Informs the device of a name by which it would be recognized by the user. Note that the provided name may be null, in which case no such user-recognizable name is provided"""
        ...

    def getUserConfiguredName(self) -> str:
        """Returns the human-recognizable name of this device, if same has been set."""
        ...


class I2cDeviceSynchSimple(HardwareDeviceHealth, I2cAddrConfig, RobotConfigNameable):
    """I2cDeviceSyncSimple is an interface that provides simple synchronous read and write functionality to an I2c device."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchSimple"
    @overload
    def read8(self) -> int:
        """Read a single byte from the device. See #readTimeStamped(int) for a complete description."""
        ...
    @overload
    def read8(self, ireg: int) -> int:
        """Read the byte at the indicated register. See #readTimeStamped(int, for a complete description."""
        ...
    def read8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def read(self, creg: int) -> list[int]:
        """Read a block of bytes from the device. See #readTimeStamped(int) for a complete description."""
        ...
    @overload
    def read(self, ireg: int, creg: int) -> list[int]:
        """Read a contiguous set of device I2C registers. See #readTimeStamped(int, for a complete description."""
        ...
    def read(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def readTimeStamped(self, creg: int) -> TimestampedData:
        """Read a block of bytes from the device, together with a best-available timestamp of when the actual I2C read occurred. Note that this can take many tens of milliseconds to execute, and thus should not be called from the loop() thread. You can always just call this method without worrying at all about I2cDeviceSynch.ReadWindow, that will work, but usually it is more efficient to take some thought and care as to what set of registers the I2C device controller is being set up to read, as adjusting that window of registers incurs significant extra time. If the current read window can't be used to read the requested registers, then a new read window will automatically be created as follows. If the current read window is non null and wholly contains the registers to read but can't be read because it is a used-up com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadMode#ONLY_ONCE window, a new read fresh window will be created with the same set of registers. Otherwise, a window that exactly covers the requested set of registers will be created."""
        ...
    @overload
    def readTimeStamped(self, ireg: int, creg: int) -> TimestampedData:
        """Reads and returns a contiguous set of device I2C registers, together with a best-available timestamp of when the actual I2C read occurred. Note that this can take many tens of milliseconds to execute, and thus should not be called from the loop() thread. You can always just call this method without worrying at all about I2cDeviceSynch.ReadWindow, that will work, but usually it is more efficient to take some thought and care as to what set of registers the I2C device controller is being set up to read, as adjusting that window of registers incurs significant extra time. If the current read window can't be used to read the requested registers, then a new read window will automatically be created as follows. If the current read window is non null and wholly contains the registers to read but can't be read because it is a used-up com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadMode#ONLY_ONCE window, a new read fresh window will be created with the same set of registers. Otherwise, a window that exactly covers the requested set of registers will be created."""
        ...
    def readTimeStamped(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write8(self, bVal: int) -> None:
        """Writes a byte to the device using I2cWaitControl#ATOMIC semantics."""
        ...
    @overload
    def write8(self, ireg: int, bVal: int) -> None:
        """Writes a byte to the indicated register using I2cWaitControl#ATOMIC semantics."""
        ...
    @overload
    def write8(self, bVal: int, waitControl: I2cWaitControl) -> None:
        """Writes a single byte to the device. See also #write(byte[],."""
        ...
    @overload
    def write8(self, ireg: int, bVal: int, waitControl: I2cWaitControl) -> None:
        """Writes a byte to the indicated register. See also #write(int,."""
        ...
    def write8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write(self, data: list[int]) -> None:
        """Writes block of bytes to the I2C device, using I2cWaitControl#ATOMIC semantics."""
        ...
    @overload
    def write(self, ireg: int, data: list[int]) -> None:
        """Writes data to a set of registers, beginning with the one indicated, using I2cWaitControl#ATOMIC semantics."""
        ...
    @overload
    def write(self, data: list[int], waitControl: I2cWaitControl) -> None:
        """Writes a block of bytes to the I2C device. The data will be written to the I2C device in an expeditious manner. Once data is accepted by this API, it is guaranteed that (barring catastrophic failure) the data will be transmitted to the USB controller module before the I2cDeviceSync is closed. The call itself may or may block until the data has been transmitted to the USB controller module according to a caller-provided parameter."""
        ...
    @overload
    def write(self, ireg: int, data: list[int], waitControl: I2cWaitControl) -> None:
        """Writes data to a set of registers, beginning with the one indicated. The data will be written to the I2C device in an expeditious manner. Once data is accepted by this API, it is guaranteed that (barring catastrophic failure) the data will be transmitted to the USB controller module before the I2cDeviceSync is closed. The call itself may or may block until the data has been transmitted to the USB controller module according to a caller-provided parameter."""
        ...
    def write(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def waitForWriteCompletions(self, waitControl: I2cWaitControl) -> None:
        """Waits for the most recent write to complete according to the behavior specified in writeControl."""
        ...

    def enableWriteCoalescing(self, enable: bool) -> None:
        """Enables or disables an optimization wherein writes to two sets of adjacent register ranges may be coalesced into a single I2c transaction if the second write comes along while the first is still queued for writing. By default, write coalescing is disabled."""
        ...

    def isWriteCoalescingEnabled(self) -> bool:
        """Answers as to whether write coalescing is currently enabled on this device."""
        ...

    def isArmed(self) -> bool:
        """Returns whether, as of this instant, this device client is alive and operational in its normally expected mode; that is, whether it is currently in communication with its underlying hardware or whether it is in some other state. Note that a device client which is not engaged will never report as armed."""
        ...

    def setI2cAddr(self, i2cAddr: I2cAddr) -> None:
        """Sets the I2C address of the underlying client. If necessary, the client may be briefly disengaged (and then automatically reengaged) in the process."""
        ...

    def getI2cAddr(self) -> I2cAddr:
        """Returns the I2C address currently being used by this device client"""
        ...

    def setLogging(self, enabled: bool) -> None:
        """Turn logging on or off. Logging output can be viewed using the Android Logcat tools."""
        ...

    def getLogging(self) -> bool:
        ...

    def setLoggingTag(self, loggingTag: str) -> None:
        """Set the tag to use when logging is on."""
        ...

    def getLoggingTag(self) -> str:
        ...


class I2cDeviceSynch(I2cDeviceSynchSimple, Engagable):
    """I2cDeviceSynch is an interface that exposes functionality for interacting with I2c devices. Its methods are synchronous, in that they complete their action before returning to the caller. Methods are provided to read and write data simply and straightforwardly. Singleton bytes or larger quantities of data can be read or written using #read8(int) and #write8(int, or #read(int, and #write(int, respectively. No attention to 'read mode' or 'write mode' is required. Simply call reads and writes as you need them, and the right thing happens. For devices that automatically shutdown if no communication is received within a certain duration, a heartbeat facility is optionally provided. On causality: regarding the sequencing of reads and writes, two important points are worthy of mention. First, reads and writes are ultimately issued to the controller in the same chronological order they were received by the device client instance. Second, even more importantly, reads *always* see the effect of preceding writes on the controller. That is, a read that follows a write will ensure that, first, the write gets issued to the controller, and then, second, a read from the controller is subsequently issued. By contrast, absent such constraints, a read might quickly return freshly-read data already present without having to interact with the controller. Which brings us to... Reading data. The simplest way to read data is to call one of the variations of the #read(int, method. This is always correct, and will return data as accessed from the I2c device. However, in many situations, reads can be significantly optimized by use of a read window. With a read window, a larger chunk of the device's I2c register space can be automatically read even if only a portion of it is needed to service a particular read() call; this can make subsequent read()s significantly faster. Further, depending on the mode of com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadWindow used, read operations will occur in the background, and read()s will be serviced (subject to causality) out of cached data updated and maintained by the background processing without any synchronous communication with the I2c device itself. For sensors in particular, this mode of operation can be particularly advantageous. Three modes of com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadWindow are available:"""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynch"
    class HeartbeatAction:
        """Instances of HeartBeatAction indicate what action to carry out to perform a heartbeat should that become necessary. The actual action to take is indicated by one of several prioritized possibilities. When a heartbeat is needed, these are considered in order, and the first one applicable given the state of the I2C device at the time will be applied."""
        __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynch.HeartbeatAction"
        def __init__(self, rereadLastRead: bool, rewriteLastWritten: bool, readWindow: I2cDeviceSynch.ReadWindow) -> None:
            """instantiates a new HeartbeatAction."""
            ...

        rereadLastRead: bool
        """Priority #1: re-issue the last I2C read operation, if possible."""
        rewriteLastWritten: bool
        """Priority #2: re-issue the last I2C write operation, if possible."""
        heartbeatReadWindow: I2cDeviceSynch.ReadWindow
        """Priority #3: explicitly read a given register window"""

    class ReadMode(enum.Enum):
        """ReadMode controls whether when asked to read we read only once or read multiple times. In all modes, it is guaranteed that a read() which follows a write() operation will see the state of the device after the write has had effect."""
        __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadMode"
        REPEAT = enum.auto()
        BALANCED = enum.auto()
        ONLY_ONCE = enum.auto()

    class ReadWindow:
        """RegWindow is a utility class for managing the window of I2C register bytes that are read from our I2C device on every hardware cycle"""
        __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynch.ReadWindow"
        def __init__(self, iregFirst: int, creg: int, readMode: I2cDeviceSynch.ReadMode) -> None:
            """Create a new register window with the indicated starting register and register count"""
            ...

        def getRegisterFirst(self) -> int:
            """Returns the first register in the window"""
            ...

        def getRegisterMax(self) -> int:
            """Returns the first register NOT in the window"""
            ...

        def getRegisterCount(self) -> int:
            """Returns the number of registers in the window"""
            ...

        def getReadMode(self) -> I2cDeviceSynch.ReadMode:
            """Returns the mode of the window"""
            ...

        def hasWindowBeenUsedForRead(self) -> bool:
            """Returns whether a read has ever been issued for this window or not"""
            ...

        def noteWindowUsedForRead(self) -> None:
            """Sets that a read has in fact been issued for this window"""
            ...

        def canBeUsedToRead(self) -> bool:
            """Answers as to whether we're allowed to read using this window. This will return false for ONLY_ONCE windows after #noteWindowUsedForRead() has been called on them."""
            ...

        def mayInitiateSwitchToReadMode(self) -> bool:
            """Answers as to whether this window in its present state ought to cause a transition to read-mode when there's nothing else for the device to be doing."""
            ...

        def readableCopy(self) -> I2cDeviceSynch.ReadWindow:
            """Returns a copy of this window but with the #usedForRead flag clear"""
            ...

        def sameAsIncludingMode(self, him: I2cDeviceSynch.ReadWindow) -> bool:
            """Do the receiver and the indicated register window cover exactly the same set of registers and have the same modality?"""
            ...

        @overload
        def contains(self, him: I2cDeviceSynch.ReadWindow) -> bool:
            """Answers as to whether the receiver wholly contains the indicated window."""
            ...
        @overload
        def contains(self, ireg: int, creg: int) -> bool:
            """Answers as to whether the receiver wholly contains the indicated set of registers."""
            ...
        def contains(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def containsWithSameMode(self, him: I2cDeviceSynch.ReadWindow) -> bool:
            """Answers as to whether the receiver wholly contains the indicated window and also has the same modality."""
            ...

        READ_REGISTER_COUNT_MAX: int
        """enableI2cReadMode and enableI2cWriteMode both impose a maximum length on the size of data that can be read or written at one time. #READ_REGISTER_COUNT_MAX and #WRITE_REGISTER_COUNT_MAX indicate those maximum sizes."""
        WRITE_REGISTER_COUNT_MAX: int

    def setReadWindow(self, window: I2cDeviceSynch.ReadWindow) -> None:
        """Set the set of registers that we will read and read and read again on every hardware cycle"""
        ...

    def getReadWindow(self) -> I2cDeviceSynch.ReadWindow:
        """Returns the current register window used for reading."""
        ...

    def ensureReadWindow(self, windowNeeded: I2cDeviceSynch.ReadWindow, windowToSet: I2cDeviceSynch.ReadWindow) -> None:
        """Ensure that the current register window covers the indicated set of registers. If there is currently a non-null register window, and windowNeeded is non-null, and the current register window entirely contains windowNeeded, then do nothing. Otherwise, set the current register window to windowToSet."""
        ...

    def readTimeStamped(self, ireg: int, creg: int, readWindowNeeded: I2cDeviceSynch.ReadWindow, readWindowSet: I2cDeviceSynch.ReadWindow) -> TimestampedData:
        """Advanced: Atomically calls ensureReadWindow() with the last two parameters and then readTimeStamped() with the first two without the possibility of a concurrent client interrupting in the middle."""
        ...

    def setHeartbeatInterval(self, ms: int) -> None:
        """Sets the interval within which communication must be received by the I2C device lest a timeout may occur. The default heartbeat interval is zero, signifying that no heartbeat is maintained."""
        ...

    def getHeartbeatInterval(self) -> int:
        """Returns the interval within which communication must be received by the I2C device lest a timeout occur."""
        ...

    def setHeartbeatAction(self, action: I2cDeviceSynch.HeartbeatAction) -> None:
        """Sets the action to take when the current heartbeat interval expires. The default action is null; thus, to be useful, an action must always be explicitly specified."""
        ...

    def getHeartbeatAction(self) -> I2cDeviceSynch.HeartbeatAction:
        """Returns the current action, if any, to take upon expiration of the heartbeat interval."""
        ...


class RobotArmingStateNotifier:
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.robotcore.hardware.usb.RobotArmingStateNotifier"
    class Callback:
        """The Callback interface can be used to receive notifications when a module changes its arming state."""
        __java__ = "com.qualcomm.robotcore.hardware.usb.RobotArmingStateNotifier.Callback"
        def onModuleStateChange(self, module: RobotArmingStateNotifier, state: RobotArmingStateNotifier.ARMINGSTATE) -> None:
            """Notifies the callback that a module with which it has registered for notifications has undergone a change of state."""
            ...

    class ARMINGSTATE(enum.Enum):
        __java__ = "com.qualcomm.robotcore.hardware.usb.RobotArmingStateNotifier.ARMINGSTATE"
        ARMED = enum.auto()
        PRETENDING = enum.auto()
        DISARMED = enum.auto()
        CLOSED = enum.auto()
        TO_ARMED = enum.auto()
        TO_PRETENDING = enum.auto()
        TO_DISARMED = enum.auto()

    def getSerialNumber(self) -> SerialNumber:
        """Returns the serial number of this USB module"""
        ...

    def getArmingState(self) -> RobotArmingStateNotifier.ARMINGSTATE:
        """Returns the current arming state of the object."""
        ...

    def registerCallback(self, callback: RobotArmingStateNotifier.Callback, doInitialCallback: bool) -> None:
        """Registers a callback for arming state notifications from this module. If this callback is already registered for notifications from this module, this method has no effect. Note that multiple callbacks may be simultaneously registered with a given one module: they all receive state-change notifications, in an arbitrary order."""
        ...

    def unregisterCallback(self, callback: RobotArmingStateNotifier.Callback) -> None:
        """Unregister a callback which has been registered for notifications with this module. If the callback was not previously registered, this method has no effect."""
        ...


class I2cDeviceSynchDevice(RobotArmingStateNotifier.Callback, HardwareDevice, Generic[DEVICE_CLIENT]):
    """I2cDeviceSynchDevice instances are I2c devices which are built on top of I2cDeviceSynchSimple instances or subclasses thereof. The class provides common and handy utility services for such devices."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchDevice"
    def __init__(self, deviceClient: DEVICE_CLIENT, deviceClientIsOwned: bool) -> None:
        ...

    def registerArmingStateCallback(self, doInitialCallback: bool) -> None:
        ...

    def engage(self) -> None:
        ...

    def disengage(self) -> None:
        ...

    def getDeviceClient(self) -> DEVICE_CLIENT:
        ...

    def onModuleStateChange(self, module: RobotArmingStateNotifier, state: RobotArmingStateNotifier.ARMINGSTATE) -> None:
        ...

    def initializeIfNecessary(self) -> None:
        ...

    def initialize(self) -> bool:
        ...

    def doInitialize(self) -> bool:
        """Actually carries out the initialization of the instance."""
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def getVersion(self) -> int:
        ...

    def getConnectionInfo(self) -> str:
        ...

    deviceClient: DEVICE_CLIENT
    deviceClientIsOwned: bool
    isInitialized: bool


class I2cDeviceSynchDeviceWithParameters(I2cDeviceSynchDevice[DEVICE_CLIENT], Generic[DEVICE_CLIENT, PARAMETERS]):
    """I2cDeviceSynchDeviceWithParameters adds to I2cDeviceSynchDevice support for sensors that can be publicly initialized with a particular parameters class."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchDeviceWithParameters"
    def __init__(self, deviceClient: DEVICE_CLIENT, deviceClientIsOwned: bool, defaultParameters: PARAMETERS) -> None:
        ...

    def getParameters(self) -> PARAMETERS:
        """Returns the parameter block currently in use for this sensor"""
        ...

    def doInitialize(self) -> bool:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def initialize(self, parameters: PARAMETERS) -> bool:
        """Allows for external initialization with non-default parameters"""
        ...

    def internalInitialize(self, parameters: PARAMETERS) -> bool:
        """Actually attempts to carry out initialization with the indicated parameter block. If successful, said parameter block should be stored in the #parameters member variable."""
        ...

    parameters: PARAMETERS
    defaultParameters: PARAMETERS


class I2cDeviceSynchReadHistory:
    """I2cDeviceSynchReadHistory provides a means by which one can be guaranteed to be informed of all data read by through an I2cDeviceSynch. This is provided by means of a queue into which all data retrieved is (optionally) be stored."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchReadHistory"
    def setHistoryQueueCapacity(self, capacity: int) -> None:
        """Sets the maximum number of TimestampedI2cDatas that will simultaneously be stored in the history queue. If the queue is full and new TimestampedI2cDatas become available, older data will be discarded. The history queue initially has a capacity of zero. Note that calling this method invalidates any history queue retrieved previously through #getHistoryQueue()."""
        ...

    def getHistoryQueueCapacity(self) -> int:
        """Returns the current capacity of the history queue."""
        ...

    def getHistoryQueue(self) -> Any:
        """(Advanced) Returns a queue into which, if requested, TimestampedI2cDatas are (optionally) placed as they become available. To access these TimestampedI2cDatas, call #setHistoryQueueCapacity(int) to enable the history queue. Once enabled, the history queue can be accessed using #getHistoryQueue() and the methods thereon used to access TimestampedI2cDatas as they become available. When #setHistoryQueueCapacity(int) is called, any history queue returned previously by #getHistoryQueue() becomes invalid and must be re-fetched."""
        ...


class I2cDeviceSynchReadHistoryImpl(I2cDeviceSynchReadHistory):
    """I2cDeviceSynchReadHistoryImpl is a helper class providing an implementation of the I2c read history queue"""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchReadHistoryImpl"
    def __init__(self) -> None:
        ...

    def getHistoryQueue(self) -> Any:
        ...

    def setHistoryQueueCapacity(self, capacity: int) -> None:
        ...

    def getHistoryQueueCapacity(self) -> int:
        ...

    def addToHistoryQueue(self, data: TimestampedI2cData) -> None:
        ...

    historyQueueLock: object
    historyQueue: Any
    historyQueueCapacity: int


class I2cDeviceSynchImplOnSimple(I2cDeviceSynchReadHistoryImpl, I2cDeviceSynch):
    """I2cDeviceSynchImplOnSimple takes an I2cDeviceSynchSimple and adds to it heartbeat and readwindow functionality."""
    __java__ = "com.qualcomm.robotcore.hardware.I2cDeviceSynchImplOnSimple"
    def __init__(self, simple: I2cDeviceSynchSimple, isSimpleOwned: bool) -> None:
        ...

    def setUserConfiguredName(self, name: str) -> None:
        ...

    def getUserConfiguredName(self) -> str:
        ...

    def setLogging(self, enabled: bool) -> None:
        ...

    def getLogging(self) -> bool:
        ...

    def setLoggingTag(self, loggingTag: str) -> None:
        ...

    def getLoggingTag(self) -> str:
        ...

    def engage(self) -> None:
        ...

    def hook(self) -> None:
        ...

    def adjustHooking(self) -> None:
        ...

    def isEngaged(self) -> bool:
        ...

    def isArmed(self) -> bool:
        ...

    def disengage(self) -> None:
        ...

    def unhook(self) -> None:
        ...

    def setHeartbeatInterval(self, ms: int) -> None:
        ...

    def getHeartbeatInterval(self) -> int:
        ...

    def setHeartbeatAction(self, action: I2cDeviceSynch.HeartbeatAction) -> None:
        ...

    def getHeartbeatAction(self) -> I2cDeviceSynch.HeartbeatAction:
        ...

    def startHeartBeat(self) -> None:
        ...

    def stopHeartBeat(self) -> None:
        ...

    def setReadWindow(self, window: I2cDeviceSynch.ReadWindow) -> None:
        ...

    def getReadWindow(self) -> I2cDeviceSynch.ReadWindow:
        ...

    def ensureReadWindow(self, windowNeeded: I2cDeviceSynch.ReadWindow, windowToSet: I2cDeviceSynch.ReadWindow) -> None:
        ...

    @overload
    def readTimeStamped(self, ireg: int, creg: int, readWindowNeeded: I2cDeviceSynch.ReadWindow, readWindowSet: I2cDeviceSynch.ReadWindow) -> TimestampedData:
        ...
    @overload
    def readTimeStamped(self, creg: int) -> TimestampedData:
        ...
    @overload
    def readTimeStamped(self, ireg: int, creg: int) -> TimestampedData:
        ...
    def readTimeStamped(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def setHealthStatus(self, status: HardwareDeviceHealth.HealthStatus) -> None:
        ...

    def getHealthStatus(self) -> HardwareDeviceHealth.HealthStatus:
        ...

    def getHistoryQueue(self) -> Any:
        ...

    def setHistoryQueueCapacity(self, capacity: int) -> None:
        ...

    def getHistoryQueueCapacity(self) -> int:
        ...

    def addToHistoryQueue(self, data: TimestampedI2cData) -> None:
        ...

    def isOpenForReading(self) -> bool:
        ...

    def isOpenForWriting(self) -> bool:
        ...

    def newReadsAndWritesAllowed(self) -> bool:
        ...

    def getSimple(self) -> I2cDeviceSynchSimple:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def setI2cAddr(self, i2cAddr: I2cAddr) -> None:
        ...

    def getI2cAddr(self) -> I2cAddr:
        ...

    @overload
    def read8(self) -> int:
        ...
    @overload
    def read8(self, ireg: int) -> int:
        ...
    def read8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def read(self, creg: int) -> list[int]:
        ...
    @overload
    def read(self, ireg: int, creg: int) -> list[int]:
        ...
    def read(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write8(self, bVal: int) -> None:
        ...
    @overload
    def write8(self, ireg: int, bVal: int) -> None:
        ...
    @overload
    def write8(self, ireg: int, bVal: int, waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def write8(self, bVal: int, waitControl: I2cWaitControl) -> None:
        ...
    def write8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write(self, ireg: int, data: list[int]) -> None:
        ...
    @overload
    def write(self, data: list[int]) -> None:
        ...
    @overload
    def write(self, ireg: int, data: list[int], waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def write(self, data: list[int], waitControl: I2cWaitControl) -> None:
        ...
    def write(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def waitForWriteCompletions(self, waitControl: I2cWaitControl) -> None:
        ...

    def enableWriteCoalescing(self, enable: bool) -> None:
        ...

    def isWriteCoalescingEnabled(self) -> bool:
        ...

    i2cDeviceSynchSimple: I2cDeviceSynchSimple
    i2cDeviceSynchSimpleHistory: I2cDeviceSynchReadHistory
    isSimpleOwned: bool
    iregReadLast: int
    cregReadLast: int
    iregWriteLast: int
    rgbWriteLast: list[int]
    isHooked: bool
    isEngaged_: bool
    isClosing: bool
    msHeartbeatInterval: int
    heartbeatAction: I2cDeviceSynch.HeartbeatAction
    heartbeatExecutor: Any
    engagementLock: object
    concurrentClientLock: object


class I2cWaitControl(enum.Enum):
    """Values in I2cWaitControl control the semantics of waiting on I2c writes"""
    __java__ = "com.qualcomm.robotcore.hardware.I2cWaitControl"
    NONE = enum.auto()
    ATOMIC = enum.auto()
    WRITTEN = enum.auto()


class I2cWarningManager(GlobalWarningSource):
    __java__ = "com.qualcomm.robotcore.hardware.I2cWarningManager"
    @staticmethod
    def notifyProblemI2cDevice(dev: I2cDeviceSynchSimple) -> None:
        ...

    @staticmethod
    def removeProblemI2cDevice(dev: I2cDeviceSynchSimple) -> None:
        ...

    @staticmethod
    def suppressNewProblemDeviceWarningsWhile(runnable: Any) -> None:
        ...

    @staticmethod
    def suppressNewProblemDeviceWarnings(suppress: bool) -> None:
        ...

    @staticmethod
    def clearI2cWarnings() -> None:
        ...

    def getGlobalWarning(self) -> str:
        ...

    def shouldTriggerWarningSound(self) -> bool:
        ...

    def suppressGlobalWarning(self, suppress: bool) -> None:
        ...

    def setGlobalWarning(self, warning: str) -> None:
        ...

    def clearGlobalWarning(self) -> None:
        ...


class IMU(HardwareDevice):
    """An Inertial Measurement Unit that provides robot-centric orientation and angular velocity."""
    __java__ = "com.qualcomm.robotcore.hardware.IMU"
    class Parameters:
        """Settings to change the IMU's behavior. Used as the parameter of #initialize(Parameters)."""
        __java__ = "com.qualcomm.robotcore.hardware.IMU.Parameters"
        def __init__(self, imuOrientationOnRobot: ImuOrientationOnRobot) -> None:
            ...

        def copy(self) -> IMU.Parameters:
            ...

        imuOrientationOnRobot: ImuOrientationOnRobot

    def initialize(self, parameters: IMU.Parameters) -> bool:
        """Initializes the IMU with non-default settings."""
        ...

    def resetYaw(self) -> None:
        """Resets the robot's yaw angle to 0. After calling this method, the reported orientation will be relative to the robot's position when this method was called, as if the robot was perfectly level right then. That is to say, the pitch and yaw will be ignored when this method is called."""
        ...

    def getRobotYawPitchRollAngles(self) -> YawPitchRollAngles:
        ...

    def getRobotOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def getRobotOrientationAsQuaternion(self) -> Quaternion:
        ...

    def getRobotAngularVelocity(self, angleUnit: AngleUnit) -> AngularVelocity:
        ...


class ImuOrientationOnRobot:
    """Defines how an IMU is oriented relative to the robot. See com.qualcomm.hardware.rev.RevHubOrientationOnRobot (from the Hardware module) for an easy-to-use implementation for the REV Control and Expansion Hub."""
    __java__ = "com.qualcomm.robotcore.hardware.ImuOrientationOnRobot"
    def imuCoordinateSystemOrientationFromPerspectiveOfRobot(self) -> Quaternion:
        ...

    def imuRotationOffset(self) -> Quaternion:
        ...

    def angularVelocityTransform(self) -> Quaternion:
        ...


class OrientationSensor:
    """OrientationSensor provides access to sensors which measure absolute orientation"""
    __java__ = "com.qualcomm.robotcore.hardware.OrientationSensor"
    def getAngularOrientationAxes(self) -> set[Axis]:
        """Returns the axes on which the sensor measures angular orientation."""
        ...

    def getAngularOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        """Returns the absolute orientation of the sensor as a set three angles. Axes on which absolute orientation is not measured are reported as zero."""
        ...


class IntegratingGyroscope(Gyroscope, OrientationSensor):
    """For gyroscopes which perform angular rotation rate integration inside the sensor, IntegratingGyroscope provides a means by which the integrated rotation can be easily retrieved."""
    __java__ = "com.qualcomm.robotcore.hardware.IntegratingGyroscope"


class IrSeekerSensor(HardwareDevice):
    """IR Seeker Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.IrSeekerSensor"
    class Mode(enum.Enum):
        """Enumeration of device modes"""
        __java__ = "com.qualcomm.robotcore.hardware.IrSeekerSensor.Mode"
        MODE_600HZ = enum.auto()
        MODE_1200HZ = enum.auto()

    class IrSeekerIndividualSensor:
        """IR Sensor attached to an IR Seeker"""
        __java__ = "com.qualcomm.robotcore.hardware.IrSeekerSensor.IrSeekerIndividualSensor"
        @overload
        def __init__(self) -> None:
            """Constructor"""
            ...
        @overload
        def __init__(self, angle: float, strength: float) -> None:
            """Constructor"""
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def getSensorAngle(self) -> float:
            """Get the angle at which this sensor is mounted"""
            ...

        def getSensorStrength(self) -> float:
            """Get the strength of the IR signal detected by this sensor"""
            ...

        def toString(self) -> str:
            ...

    def setSignalDetectedThreshold(self, threshold: float) -> None:
        """Set the minimum threshold for a signal to be considered detected"""
        ...

    def getSignalDetectedThreshold(self) -> float:
        """Get the minimum threshold for a signal to be considered detected"""
        ...

    def setMode(self, mode: IrSeekerSensor.Mode) -> None:
        """Set the device mode"""
        ...

    def getMode(self) -> IrSeekerSensor.Mode:
        """Get the device mode"""
        ...

    def signalDetected(self) -> bool:
        """Returns true if an IR signal is detected"""
        ...

    def getAngle(self) -> float:
        """Estimated angle in which the signal is coming from"""
        ...

    def getStrength(self) -> float:
        """IR Signal strength"""
        ...

    def getIndividualSensors(self) -> list[IrSeekerSensor.IrSeekerIndividualSensor]:
        """Get a list of all IR sensors attached to this seeker. The list will include the angle at which the sensor is mounted, and the signal strength."""
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        """Set the I2C address to a new value."""
        ...

    def getI2cAddress(self) -> I2cAddr:
        """Get the current I2C Address of this object. Not necessarily the same as the I2C address of the actual device. Return the current I2C address."""
        ...


class Light:
    """Light instances are sources of illumination. They can inform as to whether they are on or off."""
    __java__ = "com.qualcomm.robotcore.hardware.Light"
    def isLightOn(self) -> bool:
        """Answers whether the light is on or off"""
        ...


class SwitchableLight(Light):
    """SwitchableLight instances are Lights whose on/off status can be programmatically manipulated."""
    __java__ = "com.qualcomm.robotcore.hardware.SwitchableLight"
    def enableLight(self, enable: bool) -> None:
        """Turns the light on or off."""
        ...


class LED(HardwareDevice, SwitchableLight):
    __java__ = "com.qualcomm.robotcore.hardware.LED"
    def __init__(self, controller: DigitalChannelController, physicalPort: int) -> None:
        """Constructor"""
        ...

    def enable(self, enableLed: bool) -> None:
        """A method to turn on or turn off the LED"""
        ...

    def isLightOn(self) -> bool:
        ...

    def enableLight(self, enable: bool) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def on(self) -> None:
        """Turns the light on"""
        ...

    def off(self) -> None:
        """Turns the light off"""
        ...


class LightBlinker(Blinker):
    """A LightBlinker is a handy utility that will flash a com.qualcomm.robotcore.hardware.SwitchableLight in a pattern of timed durations, and, optionally, colors, if the light supports same (NYI)"""
    __java__ = "com.qualcomm.robotcore.hardware.LightBlinker"
    def __init__(self, light: SwitchableLight) -> None:
        ...

    def setConstant(self, color: int) -> None:
        ...

    def stopBlinking(self) -> None:
        ...

    def getBlinkerPatternMaxLength(self) -> int:
        ...

    def pushPattern(self, steps: list[Blinker.Step]) -> None:
        ...

    def patternStackNotEmpty(self) -> bool:
        ...

    def popPattern(self) -> bool:
        ...

    def setPattern(self, steps: list[Blinker.Step]) -> None:
        ...

    def isCurrentPattern(self, steps: list[Blinker.Step]) -> bool:
        ...

    def getPattern(self) -> list[Blinker.Step]:
        ...

    def scheduleNext(self) -> None:
        ...

    def stop(self) -> None:
        ...

    TAG: str
    light: SwitchableLight
    currentSteps: list[Blinker.Step]
    previousSteps: list[list[Blinker.Step]]
    future: Any
    nextStep: int


class LightMultiplexor(SwitchableLight):
    """A LightMultiplexor adapts a second SwitchableLight by adding reference counting to SwitchableLight#enableLight(boolean): the light will be lit if the net number of enables is greater than zero."""
    __java__ = "com.qualcomm.robotcore.hardware.LightMultiplexor"
    def __init__(self, target: SwitchableLight) -> None:
        ...

    @staticmethod
    def forLight(target: SwitchableLight) -> LightMultiplexor:
        ...

    def isLightOn(self) -> bool:
        ...

    def enableLight(self, enable: bool) -> None:
        ...

    extantMultiplexors: set[LightMultiplexor]
    target: SwitchableLight
    enableCount: int


class LynxModuleDescription:
    """A description of the properties that you'd like the LynxModule instance returned by LynxUsbDevice#getOrAddModule() to have"""
    __java__ = "com.qualcomm.robotcore.hardware.LynxModuleDescription"
    class Builder:
        __java__ = "com.qualcomm.robotcore.hardware.LynxModuleDescription.Builder"
        def __init__(self, address: int, isParent: bool) -> None:
            ...

        def setUserModule(self) -> LynxModuleDescription.Builder:
            ...

        def setSystemSynthetic(self) -> LynxModuleDescription.Builder:
            ...

        def build(self) -> LynxModuleDescription:
            ...

    address: int
    isParent: bool
    isUserModule: bool
    isSystemSynthetic: bool


class LynxModuleImuType(enum.Enum):
    __java__ = "com.qualcomm.robotcore.hardware.LynxModuleImuType"
    UNKNOWN = enum.auto()
    NONE = enum.auto()
    BNO055 = enum.auto()
    BHI260 = enum.auto()
    def toString(self) -> str:
        ...


class LynxModuleMeta:
    """LynxModuleMeta has simple lynx module meta information for transmission from RC to DS"""
    __java__ = "com.qualcomm.robotcore.hardware.LynxModuleMeta"
    @overload
    def __init__(self, moduleAddress: int, isParent: bool) -> None:
        ...
    @overload
    def __init__(self, him: LynxModuleMeta) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getModuleAddress(self) -> int:
        ...

    def isParent(self) -> bool:
        ...

    def imuType(self) -> LynxModuleImuType:
        ...

    def setImuType(self, imuType: LynxModuleImuType) -> None:
        ...

    def revProductNumber(self) -> int:
        ...

    def setRevProductNumber(self, productNumber: int) -> None:
        ...

    def toString(self) -> str:
        ...

    moduleAddress: int
    isParent_: bool
    imuType_: LynxModuleImuType
    revProductNumber_: int


class LynxModuleMetaList:
    """LynxModuleMetaList is a container of RobotCoreLynxModules. Its primary use is for transmission of module information from RC to DS."""
    __java__ = "com.qualcomm.robotcore.hardware.LynxModuleMetaList"
    @overload
    def __init__(self, serialNumber: SerialNumber) -> None:
        ...
    @overload
    def __init__(self, serialNumber: SerialNumber, modules: list[LynxModuleMeta]) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def iterator(self) -> Any:
        ...

    def getParent(self) -> LynxModuleMeta:
        ...

    def flatten(self) -> LynxModuleMetaList:
        ...

    def toSerializationString(self) -> str:
        ...

    @staticmethod
    def fromSerializationString(serialization: str) -> LynxModuleMetaList:
        ...

    def toString(self) -> str:
        ...

    serialNumber: SerialNumber
    modules: list[LynxModuleMeta]


class MotorControlAlgorithm(enum.Enum):
    """MotorControlAlgorithm indicates the control algorithm variant to use with DcMotor.RunMode#RUN_TO_POSITION and DcMotor.RunMode#RUN_USING_ENCODER."""
    __java__ = "com.qualcomm.robotcore.hardware.MotorControlAlgorithm"
    Unknown = enum.auto()
    LegacyPID = enum.auto()
    PIDF = enum.auto()


class NormalizedRGBA:
    """NormalizedRGBA instances represent a set of normalized color values."""
    __java__ = "com.qualcomm.robotcore.hardware.NormalizedRGBA"
    def toColor(self) -> int:
        """Converts the normalized colors into an Android color integer"""
        ...

    red: float
    """normalized red value, in range [0,1)"""
    green: float
    """normalized green value, in range [0,1)"""
    blue: float
    """normalized blue value, in range [0,1)"""
    alpha: float
    """normalized alpha value, in range [0,1)"""


class PIDCoefficients:
    """PIDCoefficients conveys a set of configuration parameters for a PID algorithm."""
    __java__ = "com.qualcomm.robotcore.hardware.PIDCoefficients"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, p: float, i: float, d: float) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toString(self) -> str:
        ...

    p: float
    i: float
    d: float


class PIDFCoefficients:
    """PIDFCoefficients conveys a set of configuration parameters for a PIDF algorithm, a PID algorithm which includes an additional feed-forward term. Optionally, coefficients for the original Expansion Hub \"Legacy PID\" alogrithm may also be indicated."""
    __java__ = "com.qualcomm.robotcore.hardware.PIDFCoefficients"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, p: float, i: float, d: float, f: float, algorithm: MotorControlAlgorithm) -> None:
        ...
    @overload
    def __init__(self, p: float, i: float, d: float, f: float) -> None:
        ...
    @overload
    def __init__(self, them: PIDFCoefficients) -> None:
        ...
    @overload
    def __init__(self, them: PIDCoefficients) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toString(self) -> str:
        ...

    p: float
    i: float
    d: float
    f: float
    algorithm: MotorControlAlgorithm


class PWMOutput(HardwareDevice):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutput"
    def setPulseWidthOutputTime(self, usDuration: int) -> None:
        ...

    def getPulseWidthOutputTime(self) -> int:
        ...

    def setPulseWidthPeriod(self, usFrame: int) -> None:
        ...

    def getPulseWidthPeriod(self) -> int:
        ...


class PWMOutputController(HardwareDevice):
    """Interface for working with PWM Input Controllers"""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutputController"
    def getSerialNumber(self) -> SerialNumber:
        """Serial Number"""
        ...

    def setPulseWidthOutputTime(self, port: int, usDuration: int) -> None:
        """Set the pulse width output time for this channel. Typically set to a value between 750 and 2,250 to control a servo."""
        ...

    def setPulseWidthPeriod(self, port: int, usPeriod: int) -> None:
        """Set the pulse width output period. Typically set to 20,000 to control servo."""
        ...

    def getPulseWidthOutputTime(self, port: int) -> int:
        """Gets the pulse width for the channel output in units of 1 microsecond."""
        ...

    def getPulseWidthPeriod(self, port: int) -> int:
        """Gets the pulse repetition period for the channel output in units of 1 microsecond."""
        ...


class PWMOutputControllerEx:
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutputControllerEx"
    def setPwmEnable(self, port: int) -> None:
        ...

    def setPwmDisable(self, port: int) -> None:
        ...

    def isPwmEnabled(self, port: int) -> bool:
        ...


class PWMOutputEx:
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutputEx"
    def setPwmEnable(self) -> None:
        ...

    def setPwmDisable(self) -> None:
        ...

    def isPwmEnabled(self) -> bool:
        ...


class PWMOutputImpl(PWMOutput):
    """Control a single digital port"""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutputImpl"
    def __init__(self, controller: PWMOutputController, port: int) -> None:
        """Constructor"""
        ...

    def setPulseWidthOutputTime(self, time: int) -> None:
        """Set the pulse width output time for this port. Typically set to a value between 750 and 2,250 to control a servo."""
        ...

    def getPulseWidthOutputTime(self) -> int:
        """Get the pulse width output time for this port"""
        ...

    def setPulseWidthPeriod(self, period: int) -> None:
        """Set the pulse width output period. Typically set to 20,000 to control servo."""
        ...

    def getPulseWidthPeriod(self) -> int:
        """Get the pulse width output"""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    controller: PWMOutputController
    port: int


class PWMOutputImplEx(PWMOutputImpl, PWMOutputEx):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.robotcore.hardware.PWMOutputImplEx"
    def __init__(self, controller: PWMOutputController, port: int) -> None:
        ...

    def setPwmEnable(self) -> None:
        ...

    def setPwmDisable(self) -> None:
        ...

    def isPwmEnabled(self) -> bool:
        ...

    controllerEx: PWMOutputControllerEx


class QuaternionBasedImuHelper:
    __java__ = "com.qualcomm.robotcore.hardware.QuaternionBasedImuHelper"
    class FailedToRetrieveQuaternionException(Exception):
        __java__ = "com.qualcomm.robotcore.hardware.QuaternionBasedImuHelper.FailedToRetrieveQuaternionException"

    def __init__(self, imuOrientationOnRobot: ImuOrientationOnRobot) -> None:
        ...

    @staticmethod
    def quaternionFromZAxisRotation(rotation: float, angleUnit: AngleUnit) -> Quaternion:
        ...

    def resetYaw(self, tag: str, imuCentricOrientationSupplier: ThrowingSupplier[Quaternion, QuaternionBasedImuHelper.FailedToRetrieveQuaternionException], timeoutMs: int) -> None:
        ...

    def getRobotOrientationAsQuaternionOrThrow(self, imuCentricOrientationSupplier: ThrowingSupplier[Quaternion, QuaternionBasedImuHelper.FailedToRetrieveQuaternionException], applyYawOffset: bool) -> Quaternion:
        ...

    def getRobotOrientationAsQuaternion(self, tag: str, imuCentricOrientationSupplier: ThrowingSupplier[Quaternion, QuaternionBasedImuHelper.FailedToRetrieveQuaternionException], applyYawOffset: bool) -> Quaternion:
        ...

    def getRobotYawPitchRollAngles(self, tag: str, imuCentricOrientationSupplier: ThrowingSupplier[Quaternion, QuaternionBasedImuHelper.FailedToRetrieveQuaternionException]) -> YawPitchRollAngles:
        ...

    def getRobotOrientation(self, tag: str, imuCentricOrientationSupplier: ThrowingSupplier[Quaternion, QuaternionBasedImuHelper.FailedToRetrieveQuaternionException], reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def getRobotAngularVelocity(self, rawAngularVelocity: AngularVelocity, angleUnit: AngleUnit) -> AngularVelocity:
        ...

    def setImuOrientationOnRobot(self, imuOrientationOnRobot: ImuOrientationOnRobot) -> None:
        ...


class RobotCoreLynxController(HardwareDevice):
    """RobotCoreLynxController is the view of a LynxController available at the RobotCore layer."""
    __java__ = "com.qualcomm.robotcore.hardware.RobotCoreLynxController"


class RobotCoreLynxModule(HardwareDevice):
    """RobotCoreLynxModule is the view of a Lynx Module available at the RobotCore layer."""
    __java__ = "com.qualcomm.robotcore.hardware.RobotCoreLynxModule"
    def getModuleAddress(self) -> int:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getFirmwareVersionString(self) -> str:
        ...

    def getNullableFirmwareVersionString(self) -> str:
        ...

    def isParent(self) -> bool:
        ...

    def attemptFailSafeAndIgnoreErrors(self) -> None:
        ...


class RobotCoreLynxUsbDevice:
    """RobotCoreLynxUsbDevice is the subset of the functionality of the LynxUsbDevice which is accessible from the RobotCore subsystem."""
    __java__ = "com.qualcomm.robotcore.hardware.RobotCoreLynxUsbDevice"
    def failSafe(self) -> None:
        ...

    def lockNetworkLockAcquisitions(self) -> None:
        ...

    def setThrowOnNetworkLockAcquisition(self, shouldThrow: bool) -> None:
        ...

    def discoverModules(self, checkForImus: bool) -> LynxModuleMetaList:
        ...

    def close(self) -> None:
        ...


class ScannedDevices:
    """ScannedDevices is a simple distinguished kind of map of serial numbers to device types. Simple serialization and deserialization logic is provided."""
    __java__ = "com.qualcomm.robotcore.hardware.ScannedDevices"
    class MapAdapter:
        """There *has* to be an easier way here, somehow."""
        __java__ = "com.qualcomm.robotcore.hardware.ScannedDevices.MapAdapter"
        def write(self, writer: Any, map: dict[SerialNumber, DeviceManager.UsbDeviceType]) -> None:
            ...

        def read(self, reader: Any) -> dict[SerialNumber, DeviceManager.UsbDeviceType]:
            ...

    @overload
    def __init__(self, them: ScannedDevices) -> None:
        ...
    @overload
    def __init__(self) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def setErrorMessage(self, errorMessage: str) -> None:
        ...

    def getErrorMessage(self) -> str:
        ...

    def size(self) -> int:
        ...

    def put(self, serialNumber: SerialNumber, deviceType: DeviceManager.UsbDeviceType) -> DeviceManager.UsbDeviceType:
        ...

    def get(self, serialNumber: SerialNumber) -> DeviceManager.UsbDeviceType:
        ...

    def containsKey(self, serialNumber: SerialNumber) -> bool:
        ...

    def keySet(self) -> set[SerialNumber]:
        ...

    def entrySet(self) -> set[Any]:
        ...

    def remove(self, serialNumber: SerialNumber) -> DeviceManager.UsbDeviceType:
        ...

    @staticmethod
    def newGson() -> Any:
        ...

    def toSerializationString(self) -> str:
        ...

    @staticmethod
    def fromSerializationString(string: str) -> ScannedDevices:
        ...

    TAG: str
    lock: object
    errorMessage: str
    map: dict[SerialNumber, DeviceManager.UsbDeviceType]


class Servo(HardwareDevice):
    """Instances of Servo interface provide access to servo hardware devices."""
    __java__ = "com.qualcomm.robotcore.hardware.Servo"
    class Direction(enum.Enum):
        """Servos can be configured to internally reverse the values to which their positioning power is set. This makes it easy, e.g., to have cooperating servos on two sides of a robot arm: one would be set at at forward, the other at reverse, and the difference between the two in that respect could be thereafter ignored. At the start of an OpMode, servos are guaranteed to be in the forward direction."""
        __java__ = "com.qualcomm.robotcore.hardware.Servo.Direction"
        FORWARD = enum.auto()
        REVERSE = enum.auto()

    def getController(self) -> ServoController:
        """Returns the underlying servo controller on which this servo is situated."""
        ...

    def getPortNumber(self) -> int:
        """Returns the port number on the underlying servo controller on which this motor is situated."""
        ...

    def setDirection(self, direction: Servo.Direction) -> None:
        """Sets the logical direction in which this servo operates."""
        ...

    def getDirection(self) -> Servo.Direction:
        """Returns the current logical direction in which this servo is set as operating."""
        ...

    def setPosition(self, position: float) -> None:
        """Sets the current position of the servo, expressed as a fraction of its available range. If PWM power is enabled for the servo, the servo will attempt to move to the indicated position."""
        ...

    def getPosition(self) -> float:
        """Returns the position to which the servo was last commanded to move. Note that this method does NOT read a position from the servo through any electrical means, as no such electrical mechanism is, generally, available."""
        ...

    def scaleRange(self, min: float, max: float) -> None:
        """Scales the available movement range of the servo to be a subset of its maximum range. Subsequent positioning calls will operate within that subset range. This is useful if your servo has only a limited useful range of movement due to the physical hardware that it is manipulating (as is often the case) but you don't want to have to manually scale and adjust the input to #setPosition(double) each time. For example, if scaleRange(0.2, 0.8) is set; then servo positions will be scaled to fit in that range: setPosition(0.0) scales to 0.2 setPosition(1.0) scales to 0.8 setPosition(0.5) scales to 0.5 setPosition(0.25) scales to 0.35 setPosition(0.75) scales to 0.65"""
        ...

    MIN_POSITION: float
    """The minimum allowable position to which a servo can be moved"""
    MAX_POSITION: float
    """The maximum allowable position to which a servo can be moved"""


class ServoController(HardwareDevice):
    """Interface for working with Servo Controllers"""
    __java__ = "com.qualcomm.robotcore.hardware.ServoController"
    class PwmStatus(enum.Enum):
        """PWM Status - is pwm enabled?"""
        __java__ = "com.qualcomm.robotcore.hardware.ServoController.PwmStatus"
        ENABLED = enum.auto()
        DISABLED = enum.auto()
        MIXED = enum.auto()

    def pwmEnable(self) -> None:
        """Enables all of the servos connected to this controller"""
        ...

    def pwmDisable(self) -> None:
        """Disables all of the servos connected to this controller"""
        ...

    def getPwmStatus(self) -> ServoController.PwmStatus:
        """Returns the enablement status of the collective set of servos connected to this controller"""
        ...

    def setServoPosition(self, servo: int, position: float) -> None:
        """Set the position of a servo at the given channel"""
        ...

    def getServoPosition(self, servo: int) -> float:
        """Get the position of a servo at a given channel"""
        ...

    def forgetLastKnownPosition(self, servo: int) -> None:
        """This gets rid of last known position so setting the position will send to the servo even if it is the same as the last known position"""
        ...


class ServoControllerEx(ServoController):
    """ServoControllerEx is an optional servo controller interface supported by some hardware that provides enhanced servo functionality."""
    __java__ = "com.qualcomm.robotcore.hardware.ServoControllerEx"
    def setServoPwmRange(self, servo: int, range: PwmControl.PwmRange) -> None:
        """Sets the PWM range of the indicated servo."""
        ...

    def getServoPwmRange(self, servo: int) -> PwmControl.PwmRange:
        """Returns the PWM range of the indicated servo on this controller."""
        ...

    def setServoPwmEnable(self, servo: int) -> None:
        """Individually energizes the PWM for a particular servo"""
        ...

    def setServoPwmDisable(self, servo: int) -> None:
        """Individually de-energizes the PWM for a particular servo"""
        ...

    def isServoPwmEnabled(self, servo: int) -> bool:
        """Returns whether the PWM is energized for this particular servo"""
        ...

    def setServoType(self, servo: int, servoType: ServoConfigurationType) -> None:
        """Sets the servo type for a particular servo"""
        ...

    def setPulseWidth(self, servo: int, usWidth: float) -> None:
        """Sets the pulse width for this particular servo (in microseconds)"""
        ...

    def getPulseWidth(self, servo: int) -> float:
        """Gets the pulse width for this particular servo (in microseconds)"""
        ...


class ServoImpl(Servo):
    """ServoImpl provides an implementation of the Servo interface that operates on top of an instance of the ServoController interface."""
    __java__ = "com.qualcomm.robotcore.hardware.ServoImpl"
    @overload
    def __init__(self, controller: ServoController, portNumber: int) -> None:
        """Constructor"""
        ...
    @overload
    def __init__(self, controller: ServoController, portNumber: int, direction: Servo.Direction) -> None:
        """COnstructor"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def getController(self) -> ServoController:
        """Get Servo Controller"""
        ...

    def setDirection(self, direction: Servo.Direction) -> None:
        """Set the direction"""
        ...

    def getDirection(self) -> Servo.Direction:
        """Get the direction"""
        ...

    def getPortNumber(self) -> int:
        """Get Channel"""
        ...

    def setPosition(self, position: float) -> None:
        """Commands the servo to move to a designated position. This method initiates the movement; the servo will arrive at the commanded position at some later time."""
        ...

    def internalSetPosition(self, position: float) -> None:
        ...

    def getPosition(self) -> float:
        """Returns the position to which the servo was last commanded, or Double.NaN if that is unavailable."""
        ...

    def scaleRange(self, min: float, max: float) -> None:
        """Automatically scales the position of the servo irrespective of whether or not reverse() is called. For example, if you set the scale range to [0.0, 0.5] and the servo is reversed, it will be from 0.5 to 0.0, NOT 1.0 to 0.5"""
        ...

    controller: ServoController
    portNumber: int
    direction: Servo.Direction
    limitPositionMin: float
    limitPositionMax: float


class ServoImplEx(ServoImpl, PwmControl):
    """ServoImplEx provides access to extended functionality on servos. Instances support both the Servo and the PwmControl interfaces."""
    __java__ = "com.qualcomm.robotcore.hardware.ServoImplEx"
    @overload
    def __init__(self, controller: ServoControllerEx, portNumber: int, servoType: ServoConfigurationType) -> None:
        ...
    @overload
    def __init__(self, controller: ServoControllerEx, portNumber: int, direction: Servo.Direction, servoType: ServoConfigurationType) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def setPwmRange(self, range: PwmControl.PwmRange) -> None:
        ...

    def getPwmRange(self) -> PwmControl.PwmRange:
        ...

    def setPwmEnable(self) -> None:
        ...

    def setPwmDisable(self) -> None:
        ...

    def isPwmEnabled(self) -> bool:
        ...

    def setPulseWidth(self, usWidth: float) -> None:
        ...

    def getPulseWidth(self) -> float:
        ...

    controllerEx: ServoControllerEx


class TimestampedData:
    """TimestampedData pairs together data which has been read with the timestamp at which the read occurred, as best that can be determined"""
    __java__ = "com.qualcomm.robotcore.hardware.TimestampedData"
    data: list[int]
    """the data in question"""
    nanoTime: int
    """the timestamp on the System.nanoTime() clock associated with that data"""


class TimestampedI2cData(TimestampedData):
    """TimestampedI2cData extends TimestampedData so as to provide an indication of the I2c source from which the data was retrieved."""
    __java__ = "com.qualcomm.robotcore.hardware.TimestampedI2cData"
    @staticmethod
    def makeFakeData(i2cAddr: I2cAddr, ireg: int, creg: int) -> TimestampedI2cData:
        """Creates and returns fake I2C data for use in situations where data must be returned but actual data is unavailable. Optionally, records that the device in question is having difficulties."""
        ...

    i2cAddr: I2cAddr
    """the I2c address from which the data was read"""
    register: int
    """the starting register address from which the data was retrieved"""


class TouchSensor(HardwareDevice):
    """TouchSensor models a button."""
    __java__ = "com.qualcomm.robotcore.hardware.TouchSensor"
    def getValue(self) -> float:
        """Represents how much force is applied to the touch sensor; for some touch sensors this value will only ever be 0 or 1."""
        ...

    def isPressed(self) -> bool:
        """Return true if the touch sensor is being pressed"""
        ...


class TouchSensorMultiplexer(HardwareDevice):
    """NXT Touch Sensor Multiplexer."""
    __java__ = "com.qualcomm.robotcore.hardware.TouchSensorMultiplexer"
    def isTouchSensorPressed(self, channel: int) -> bool:
        ...

    def getSwitches(self) -> int:
        ...


class USBAccessibleLynxModule:
    """A simple utility class holding the serial number of a USB accessible lynx module and (optionally) its module address This class should be considered a part of the public JSON API exposed via the webserver"""
    __java__ = "com.qualcomm.robotcore.hardware.USBAccessibleLynxModule"
    def __init__(self, serialNumber: SerialNumber) -> None:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def setSerialNumber(self, serialNumber: SerialNumber) -> None:
        ...

    def getModuleAddress(self) -> int:
        ...

    def setModuleAddress(self, moduleAddress: int) -> None:
        ...

    def getFirmwareVersionString(self) -> str:
        ...

    def getFinishedFirmwareVersionString(self) -> str:
        ...

    def setFirmwareVersionString(self, firmwareVersionString: str) -> None:
        ...

    serialNumber: SerialNumber
    moduleAddress: int
    firmwareVersionString: str
    formattedFirmwareVersionString: str


class UltrasonicSensor(HardwareDevice):
    __java__ = "com.qualcomm.robotcore.hardware.UltrasonicSensor"
    def getUltrasonicLevel(self) -> float:
        """Get the Ultrasonic levels from this sensor"""
        ...

    def status(self) -> str:
        """Status of this sensor, in string form"""
        ...


class VisuallyIdentifiableHardwareDevice:
    __java__ = "com.qualcomm.robotcore.hardware.VisuallyIdentifiableHardwareDevice"
    def visuallyIdentify(self, shouldIdentify: bool) -> None:
        """idempotent"""
        ...


class VoltageSensor(HardwareDevice):
    """Voltage Sensor"""
    __java__ = "com.qualcomm.robotcore.hardware.VoltageSensor"
    def getVoltage(self) -> float:
        """Get the current voltage"""
        ...


class HardwareDeviceManager(DeviceManager):
    """Scan for, and create instances of, hardware devices"""
    __java__ = "com.qualcomm.hardware.HardwareDeviceManager"
    def __init__(self, context: Any, manager: SyncdDevice.Manager) -> None:
        """HardwareDeviceManager constructor"""
        ...

    @staticmethod
    def createUsbManager() -> RobotUsbManager:
        ...

    def scanForUsbDevices(self) -> ScannedDevices:
        """Returns a map from serial number to UsbDeviceType"""
        ...

    def countVidPid(self, map: dict[Any, int], vendorProduct: VendorProductSerialNumber) -> int:
        ...

    def addVidPid(self, map: dict[Any, int], vendorProduct: VendorProductSerialNumber, delta: int) -> None:
        ...

    def scanForEthernetOverUsbDevices(self, scannedDevices: ScannedDevices) -> None:
        ...

    def scanForWebcams(self, scannedDevices: ScannedDevices) -> None:
        ...

    def determineDeviceType(self, dev: RobotUsbDevice, serialNumber: SerialNumber, deviceMap: ScannedDevices) -> None:
        ...

    def getLynxDeviceType(self, dev: RobotUsbDevice) -> DeviceManager.UsbDeviceType:
        ...

    def createLynxUsbDevice(self, serialNumber: SerialNumber, name: str) -> RobotCoreLynxUsbDevice:
        """Note: unlike other creation methods, creating a Lynx USB device will succeed even if the device is already open (in which case it will return a new delegate to the existing instance)."""
        ...

    def createDcMotor(self, controller: DcMotorController, portNumber: int, motorType: MotorConfigurationType, name: str) -> DcMotor:
        ...

    def createDcMotorEx(self, controller: DcMotorController, portNumber: int, motorType: MotorConfigurationType, name: str) -> DcMotor:
        ...

    def createServoEx(self, controller: ServoControllerEx, portNumber: int, name: str, servoType: ServoConfigurationType) -> Servo:
        ...

    def createCRServoEx(self, controller: ServoControllerEx, portNumber: int, name: str, servoType: ServoConfigurationType) -> CRServo:
        ...

    def createCustomServoDeviceInstances(self, controller: ServoControllerEx, portNumber: int, servoConfigurationType: ServoConfigurationType) -> list[HardwareDevice]:
        ...

    def createWebcamName(self, serialNumber: SerialNumber, name: str) -> WebcamName:
        ...

    def createMRDigitalTouchSensor(self, digitalChannelController: DigitalChannelController, physicalPort: int, name: str) -> TouchSensor:
        ...

    def createMRI2cIrSeekerSensorV3(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> IrSeekerSensor:
        ...

    def createAnalogSensorInstances(self, controller: AnalogInputController, channel: int, type: AnalogSensorConfigurationType) -> list[HardwareDevice]:
        ...

    def createDigitalDeviceInstances(self, controller: DigitalChannelController, channel: int, type: DigitalIoDeviceConfigurationType) -> list[HardwareDevice]:
        ...

    def createPwmOutputDevice(self, controller: PWMOutputController, channel: int, name: str) -> PWMOutput:
        ...

    def createI2cDeviceInstances(self, lynxModule: RobotCoreLynxModule, bus: DeviceConfiguration.I2cChannel, type: I2cDeviceConfigurationType, name: str) -> list[HardwareDevice]:
        ...

    def createLimelight3A(self, serialNumber: SerialNumber, name: str, ipAddress: Any) -> HardwareDevice:
        ...

    def createAdafruitI2cColorSensor(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        ...

    def createLynxColorRangeSensor(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        ...

    def createModernRoboticsI2cColorSensor(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> ColorSensor:
        ...

    def createModernRoboticsI2cGyroSensor(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> GyroSensor:
        ...

    def createLED(self, controller: DigitalChannelController, channel: int, name: str) -> LED:
        ...

    def createI2cDeviceSynch(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> I2cDeviceSynch:
        ...

    def createI2cDeviceSynchSimple(self, lynxModule: RobotCoreLynxModule, channel: DeviceConfiguration.I2cChannel, name: str) -> I2cDeviceSynchSimple:
        ...

    TAG: str
    TAG_USB_SCAN: str
    scanDevicesLock: object


class HardwareFactory:
    """Populates the hardware map."""
    __java__ = "com.qualcomm.hardware.HardwareFactory"
    def __init__(self, context: Any) -> None:
        ...

    def createHardwareMap(self, manager: SyncdDevice.Manager, opModeNotifier: OpModeManagerNotifier) -> HardwareMap:
        """Create a hardware map"""
        ...

    def mapControllerConfiguration(self, map: HardwareMap, deviceMgr: DeviceManager, ctrlConf: ControllerConfiguration) -> None:
        ...

    def setXmlPullParser(self, xmlPullParser: Any) -> None:
        ...

    def getXmlPullParser(self) -> Any:
        ...

    @staticmethod
    def noteSerialNumberType(context: Any, serialNumber: SerialNumber, typeName: str) -> None:
        ...

    @staticmethod
    def getDeviceDisplayName(context: Any, serialNumber: SerialNumber) -> str:
        ...

    TAG: str


class HardwareManualControlOpMode(LinearOpMode):
    """A view of ManualControlOpMode that's accessible from the Hardware module"""
    __java__ = "com.qualcomm.hardware.HardwareManualControlOpMode"
    @staticmethod
    def getInstance() -> HardwareManualControlOpMode:
        ...

    @staticmethod
    def setInstance(newInstance: HardwareManualControlOpMode) -> None:
        ...

    def onLynxModuleAddressChanged(self, module: LynxModule, oldAddress: int, newAddress: int) -> None:
        ...

    def onLynxModuleStatusChanged(self, module: LynxModule, statusWord: int, motorAlerts: int) -> None:
        ...


class BNO055IMU:
    """BNO055IMU interface abstracts the functionality of the Bosch/Sensortec BNO055 Intelligent 9-axis absolute orientation sensor. The BNO055 can output the following sensor data (as described in AdaFruit Absolute Orientation Sensor)."""
    __java__ = "com.qualcomm.hardware.bosch.BNO055IMU"
    class Parameters:
        """Instances of Parameters contain data indicating how a BNO055 absolute orientation sensor is to be initialized."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.Parameters"
        def clone(self) -> BNO055IMU.Parameters:
            ...

        i2cAddr: I2cAddr
        """the address at which the sensor resides on the I2C bus."""
        mode: BNO055IMU.SensorMode
        """the mode we wish to use the sensor in"""
        useExternalCrystal: bool
        """whether to use the external or internal 32.768khz crystal. External crystal use is recommended by the BNO055 specification."""
        temperatureUnit: BNO055IMU.TempUnit
        """units in which temperature are measured. See Section 3.6.1 of the BNO055 specification"""
        angleUnit: BNO055IMU.AngleUnit
        """units in which angles and angular rates are measured. See Section 3.6.1 of the BNO055 specification"""
        accelUnit: BNO055IMU.AccelUnit
        """units in which accelerations are measured. See Section 3.6.1 of the BNO055 specification"""
        pitchMode: BNO055IMU.PitchMode
        """directional convention for measuring pitch angles. See Section 3.6.1 of the BNO055 specification"""
        accelRange: BNO055IMU.AccelRange
        """accelerometer range. See Section 3.5.2 and Table 3-4 of the BNO055 specification"""
        accelBandwidth: BNO055IMU.AccelBandwidth
        """accelerometer bandwidth. See Section 3.5.2 and Table 3-4 of the BNO055 specification"""
        accelPowerMode: BNO055IMU.AccelPowerMode
        """accelerometer power mode. See Section 3.5.2 and Section 4.2.2 of the BNO055 specification"""
        gyroRange: BNO055IMU.GyroRange
        """gyroscope range. See Section 3.5.2 and Table 3-4 of the BNO055 specification"""
        gyroBandwidth: BNO055IMU.GyroBandwidth
        """gyroscope bandwidth. See Section 3.5.2 and Table 3-4 of the BNO055 specification"""
        gyroPowerMode: BNO055IMU.GyroPowerMode
        """gyroscope power mode. See Section 3.5.2 and Section 4.4.4 of the BNO055 specification"""
        magRate: BNO055IMU.MagRate
        """magnetometer data rate. See Section 3.5.3 and Section 4.4.3 of the BNO055 specification"""
        magOpMode: BNO055IMU.MagOpMode
        """magnetometer op mode. See Section 3.5.3 and Section 4.4.3 of the BNO055 specification"""
        magPowerMode: BNO055IMU.MagPowerMode
        """magnetometer power mode. See Section 3.5.3 and Section 4.4.3 of the BNO055 specification"""
        calibrationData: BNO055IMU.CalibrationData
        """Calibration data with which the BNO055 should be initialized. If calibrationData is non-null, it is used. Otherwise, if calibrationDataFile is non-null, it is used. Otherwise, only the default automatic calibration of the IMU is used"""
        calibrationDataFile: str
        accelerationIntegrationAlgorithm: BNO055IMU.AccelerationIntegrator
        """the algorithm to use for integrating acceleration to produce velocity and position. If not specified, a simple but not especially effective internal algorithm will be used."""
        loggingEnabled: bool
        """debugging aid: enable logging for this device?"""
        loggingTag: str
        """debugging aid: the logging tag to use when logging"""

    class AccelerationIntegrator:
        """AccelerationIntegrator encapsulates an algorithm for integrating acceleration information over time to produce velocity and position."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AccelerationIntegrator"
        def initialize(self, parameters: BNO055IMU.Parameters, initialPosition: Position, initialVelocity: Velocity) -> None:
            """(Re)initializes the algorithm with a starting position and velocity. Any timestamps that are present in these data are not to be considered as significant. The initial acceleration should be taken as undefined; you should set it to null when this method is called."""
            ...

        def getPosition(self) -> Position:
            """Returns the current position as calculated by the algorithm"""
            ...

        def getVelocity(self) -> Velocity:
            """Returns the current velocity as calculated by the algorithm"""
            ...

        def getAcceleration(self) -> Acceleration:
            """Returns the current acceleration as understood by the algorithm. This is typically just the value provided in the most recent call to #update(Acceleration), if any."""
            ...

        def update(self, linearAcceleration: Acceleration) -> None:
            """Step the algorithm as a result of the stimulus of new acceleration data."""
            ...

    class CalibrationData:
        """See Section 3.6.4 of the BNO055 Specification."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.CalibrationData"
        def serialize(self) -> str:
            ...

        @staticmethod
        def deserialize(data: str) -> BNO055IMU.CalibrationData:
            ...

        def clone(self) -> BNO055IMU.CalibrationData:
            ...

        dxAccel: int
        dyAccel: int
        dzAccel: int
        dxMag: int
        dyMag: int
        dzMag: int
        dxGyro: int
        dyGyro: int
        dzGyro: int
        radiusAccel: int
        radiusMag: int

    class TempUnit(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.TempUnit"
        CELSIUS = enum.auto()
        FARENHEIT = enum.auto()
        def toTempUnit(self) -> TempUnit:
            ...

        @staticmethod
        def fromTempUnit(tempUnit: TempUnit) -> BNO055IMU.TempUnit:
            ...

        bVal: int

    class AngleUnit(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AngleUnit"
        DEGREES = enum.auto()
        RADIANS = enum.auto()
        def toAngleUnit(self) -> AngleUnit:
            ...

        @staticmethod
        def fromAngleUnit(angleUnit: AngleUnit) -> BNO055IMU.AngleUnit:
            ...

        bVal: int

    class AccelUnit(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AccelUnit"
        METERS_PERSEC_PERSEC = enum.auto()
        MILLI_EARTH_GRAVITY = enum.auto()
        bVal: int

    class PitchMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.PitchMode"
        WINDOWS = enum.auto()
        ANDROID = enum.auto()
        bVal: int

    class GyroRange(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.GyroRange"
        DPS2000 = enum.auto()
        DPS1000 = enum.auto()
        DPS500 = enum.auto()
        DPS250 = enum.auto()
        DPS125 = enum.auto()
        bVal: int

    class GyroBandwidth(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.GyroBandwidth"
        HZ523 = enum.auto()
        HZ230 = enum.auto()
        HZ116 = enum.auto()
        HZ47 = enum.auto()
        HZ23 = enum.auto()
        HZ12 = enum.auto()
        HZ64 = enum.auto()
        HZ32 = enum.auto()
        bVal: int

    class GyroPowerMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.GyroPowerMode"
        NORMAL = enum.auto()
        FAST = enum.auto()
        DEEP = enum.auto()
        SUSPEND = enum.auto()
        ADVANCED = enum.auto()
        bVal: int

    class AccelRange(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AccelRange"
        G2 = enum.auto()
        G4 = enum.auto()
        G8 = enum.auto()
        G16 = enum.auto()
        bVal: int

    class AccelBandwidth(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AccelBandwidth"
        HZ7_81 = enum.auto()
        HZ15_63 = enum.auto()
        HZ31_25 = enum.auto()
        HZ62_5 = enum.auto()
        HZ125 = enum.auto()
        HZ250 = enum.auto()
        HZ500 = enum.auto()
        HZ1000 = enum.auto()
        bVal: int

    class AccelPowerMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.AccelPowerMode"
        NORMAL = enum.auto()
        SUSPEND = enum.auto()
        LOW1 = enum.auto()
        STANDBY = enum.auto()
        LOW2 = enum.auto()
        DEEP = enum.auto()
        bVal: int

    class MagRate(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.MagRate"
        HZ2 = enum.auto()
        HZ6 = enum.auto()
        HZ8 = enum.auto()
        HZ10 = enum.auto()
        HZ15 = enum.auto()
        HZ20 = enum.auto()
        HZ25 = enum.auto()
        HZ30 = enum.auto()
        bVal: int

    class MagOpMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.MagOpMode"
        LOW = enum.auto()
        REGULAR = enum.auto()
        ENHANCED = enum.auto()
        HIGH = enum.auto()
        bVal: int

    class MagPowerMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.MagPowerMode"
        NORMAL = enum.auto()
        SLEEP = enum.auto()
        SUSPEND = enum.auto()
        FORCE = enum.auto()
        bVal: int

    class SystemStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.SystemStatus"
        UNKNOWN = enum.auto()
        IDLE = enum.auto()
        SYSTEM_ERROR = enum.auto()
        INITIALIZING_PERIPHERALS = enum.auto()
        SYSTEM_INITIALIZATION = enum.auto()
        SELF_TEST = enum.auto()
        RUNNING_FUSION = enum.auto()
        RUNNING_NO_FUSION = enum.auto()
        @staticmethod
        def from_(value: int) -> BNO055IMU.SystemStatus:
            ...

        def toShortString(self) -> str:
            ...

        bVal: int

    class SystemError(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.SystemError"
        UNKNOWN = enum.auto()
        NO_ERROR = enum.auto()
        PERIPHERAL_INITIALIZATION_ERROR = enum.auto()
        SYSTEM_INITIALIZATION_ERROR = enum.auto()
        SELF_TEST_FAILED = enum.auto()
        REGISTER_MAP_OUT_OF_RANGE = enum.auto()
        REGISTER_MAP_ADDRESS_OUT_OF_RANGE = enum.auto()
        REGISTER_MAP_WRITE_ERROR = enum.auto()
        LOW_POWER_MODE_NOT_AVAILABLE = enum.auto()
        ACCELEROMETER_POWER_MODE_NOT_AVAILABLE = enum.auto()
        FUSION_CONFIGURATION_ERROR = enum.auto()
        SENSOR_CONFIGURATION_ERROR = enum.auto()
        @staticmethod
        def from_(value: int) -> BNO055IMU.SystemError:
            ...

        bVal: int

    class CalibrationStatus:
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.CalibrationStatus"
        def __init__(self, calibrationStatus: int) -> None:
            ...

        def toString(self) -> str:
            ...

        calibrationStatus: int

    class SensorMode(enum.Enum):
        """Sensor modes are described in Table 3-5 of the BNO055 specification, where they are termed \"operation modes\"."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.SensorMode"
        CONFIG = enum.auto()
        ACCONLY = enum.auto()
        MAGONLY = enum.auto()
        GYRONLY = enum.auto()
        ACCMAG = enum.auto()
        ACCGYRO = enum.auto()
        MAGGYRO = enum.auto()
        AMG = enum.auto()
        IMU = enum.auto()
        COMPASS = enum.auto()
        M4G = enum.auto()
        NDOF_FMC_OFF = enum.auto()
        NDOF = enum.auto()
        DISABLED = enum.auto()
        def isFusionMode(self) -> bool:
            """Is this SensorMode one of the fusion modes in which the BNO055 operates?"""
            ...

        @staticmethod
        def fromByte(b: int) -> BNO055IMU.SensorMode:
            ...

        bVal: int

    class Register(enum.Enum):
        """Register provides symbolic names for each of the BNO055 device registers."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMU.Register"
        PAGE_ID = enum.auto()
        CHIP_ID = enum.auto()
        ACC_ID = enum.auto()
        MAG_ID = enum.auto()
        GYR_ID = enum.auto()
        SW_REV_ID_LSB = enum.auto()
        SW_REV_ID_MSB = enum.auto()
        BL_REV_ID = enum.auto()
        ACC_DATA_X_LSB = enum.auto()
        ACC_DATA_X_MSB = enum.auto()
        ACC_DATA_Y_LSB = enum.auto()
        ACC_DATA_Y_MSB = enum.auto()
        ACC_DATA_Z_LSB = enum.auto()
        ACC_DATA_Z_MSB = enum.auto()
        MAG_DATA_X_LSB = enum.auto()
        MAG_DATA_X_MSB = enum.auto()
        MAG_DATA_Y_LSB = enum.auto()
        MAG_DATA_Y_MSB = enum.auto()
        MAG_DATA_Z_LSB = enum.auto()
        MAG_DATA_Z_MSB = enum.auto()
        GYR_DATA_X_LSB = enum.auto()
        GYR_DATA_X_MSB = enum.auto()
        GYR_DATA_Y_LSB = enum.auto()
        GYR_DATA_Y_MSB = enum.auto()
        GYR_DATA_Z_LSB = enum.auto()
        GYR_DATA_Z_MSB = enum.auto()
        EUL_H_LSB = enum.auto()
        EUL_H_MSB = enum.auto()
        EUL_R_LSB = enum.auto()
        EUL_R_MSB = enum.auto()
        EUL_P_LSB = enum.auto()
        EUL_P_MSB = enum.auto()
        QUA_DATA_W_LSB = enum.auto()
        QUA_DATA_W_MSB = enum.auto()
        QUA_DATA_X_LSB = enum.auto()
        QUA_DATA_X_MSB = enum.auto()
        QUA_DATA_Y_LSB = enum.auto()
        QUA_DATA_Y_MSB = enum.auto()
        QUA_DATA_Z_LSB = enum.auto()
        QUA_DATA_Z_MSB = enum.auto()
        LIA_DATA_X_LSB = enum.auto()
        LIA_DATA_X_MSB = enum.auto()
        LIA_DATA_Y_LSB = enum.auto()
        LIA_DATA_Y_MSB = enum.auto()
        LIA_DATA_Z_LSB = enum.auto()
        LIA_DATA_Z_MSB = enum.auto()
        GRV_DATA_X_LSB = enum.auto()
        GRV_DATA_X_MSB = enum.auto()
        GRV_DATA_Y_LSB = enum.auto()
        GRV_DATA_Y_MSB = enum.auto()
        GRV_DATA_Z_LSB = enum.auto()
        GRV_DATA_Z_MSB = enum.auto()
        TEMP = enum.auto()
        CALIB_STAT = enum.auto()
        SELFTEST_RESULT = enum.auto()
        INTR_STAT = enum.auto()
        SYS_CLK_STAT = enum.auto()
        SYS_STAT = enum.auto()
        SYS_ERR = enum.auto()
        UNIT_SEL = enum.auto()
        DATA_SELECT = enum.auto()
        OPR_MODE = enum.auto()
        PWR_MODE = enum.auto()
        SYS_TRIGGER = enum.auto()
        TEMP_SOURCE = enum.auto()
        AXIS_MAP_CONFIG = enum.auto()
        AXIS_MAP_SIGN = enum.auto()
        SIC_MATRIX_0_LSB = enum.auto()
        SIC_MATRIX_0_MSB = enum.auto()
        SIC_MATRIX_1_LSB = enum.auto()
        SIC_MATRIX_1_MSB = enum.auto()
        SIC_MATRIX_2_LSB = enum.auto()
        SIC_MATRIX_2_MSB = enum.auto()
        SIC_MATRIX_3_LSB = enum.auto()
        SIC_MATRIX_3_MSB = enum.auto()
        SIC_MATRIX_4_LSB = enum.auto()
        SIC_MATRIX_4_MSB = enum.auto()
        SIC_MATRIX_5_LSB = enum.auto()
        SIC_MATRIX_5_MSB = enum.auto()
        SIC_MATRIX_6_LSB = enum.auto()
        SIC_MATRIX_6_MSB = enum.auto()
        SIC_MATRIX_7_LSB = enum.auto()
        SIC_MATRIX_7_MSB = enum.auto()
        SIC_MATRIX_8_LSB = enum.auto()
        SIC_MATRIX_8_MSB = enum.auto()
        ACC_OFFSET_X_LSB = enum.auto()
        ACC_OFFSET_X_MSB = enum.auto()
        ACC_OFFSET_Y_LSB = enum.auto()
        ACC_OFFSET_Y_MSB = enum.auto()
        ACC_OFFSET_Z_LSB = enum.auto()
        ACC_OFFSET_Z_MSB = enum.auto()
        MAG_OFFSET_X_LSB = enum.auto()
        MAG_OFFSET_X_MSB = enum.auto()
        MAG_OFFSET_Y_LSB = enum.auto()
        MAG_OFFSET_Y_MSB = enum.auto()
        MAG_OFFSET_Z_LSB = enum.auto()
        MAG_OFFSET_Z_MSB = enum.auto()
        GYR_OFFSET_X_LSB = enum.auto()
        GYR_OFFSET_X_MSB = enum.auto()
        GYR_OFFSET_Y_LSB = enum.auto()
        GYR_OFFSET_Y_MSB = enum.auto()
        GYR_OFFSET_Z_LSB = enum.auto()
        GYR_OFFSET_Z_MSB = enum.auto()
        ACC_RADIUS_LSB = enum.auto()
        ACC_RADIUS_MSB = enum.auto()
        MAG_RADIUS_LSB = enum.auto()
        MAG_RADIUS_MSB = enum.auto()
        ACC_CONFIG = enum.auto()
        MAG_CONFIG = enum.auto()
        GYR_CONFIG_0 = enum.auto()
        GYR_CONFIG_1 = enum.auto()
        ACC_SLEEP_CONFIG = enum.auto()
        GYR_SLEEP_CONFIG = enum.auto()
        INT_MSK = enum.auto()
        INT_EN = enum.auto()
        ACC_AM_THRES = enum.auto()
        ACC_INT_SETTINGS = enum.auto()
        ACC_HG_DURATION = enum.auto()
        ACC_HG_THRES = enum.auto()
        ACC_NM_THRES = enum.auto()
        ACC_NM_SET = enum.auto()
        GRYO_INT_SETTING = enum.auto()
        GRYO_HR_X_SET = enum.auto()
        GRYO_DUR_X = enum.auto()
        GRYO_HR_Y_SET = enum.auto()
        GRYO_DUR_Y = enum.auto()
        GRYO_HR_Z_SET = enum.auto()
        GRYO_DUR_Z = enum.auto()
        GRYO_AM_THRES = enum.auto()
        GRYO_AM_SET = enum.auto()
        UNIQUE_ID_FIRST = enum.auto()
        UNIQUE_ID_LAST = enum.auto()
        bVal: int

    def initialize(self, parameters: BNO055IMU.Parameters) -> bool:
        """Initialize the sensor using the indicated set of parameters. Note that the execution of this method can take a fairly long while, possibly several tens of milliseconds."""
        ...

    def getParameters(self) -> BNO055IMU.Parameters:
        """Returns the parameters which which initialization was last attempted, if any"""
        ...

    def close(self) -> None:
        """Shut down the sensor. This doesn't do anything in the hardware device itself, but rather shuts down any resources (threads, etc) that we use to communicate with it. It is rare that user code has a need to call this method."""
        ...

    @overload
    def getAngularOrientation(self) -> Orientation:
        """Returns the absolute orientation of the sensor as a set three angles"""
        ...
    @overload
    def getAngularOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        """Returns the absolute orientation of the sensor as a set three angles with indicated parameters."""
        ...
    def getAngularOrientation(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getOverallAcceleration(self) -> Acceleration:
        """Returns the overall acceleration experienced by the sensor. This is composed of a component due to the movement of the sensor and a component due to the force of gravity."""
        ...

    def getAngularVelocity(self) -> AngularVelocity:
        """Returns the rate of change of the absolute orientation of the sensor."""
        ...

    def getLinearAcceleration(self) -> Acceleration:
        """Returns the acceleration experienced by the sensor due to the movement of the sensor."""
        ...

    def getGravity(self) -> Acceleration:
        """Returns the direction of the force of gravity relative to the sensor."""
        ...

    def getTemperature(self) -> Temperature:
        """Returns the current temperature."""
        ...

    def getMagneticFieldStrength(self) -> MagneticFlux:
        """Returns the magnetic field strength experienced by the sensor. See Section 3.6.5.2 of the BNO055 specification."""
        ...

    def getQuaternionOrientation(self) -> Quaternion:
        """Returns the absolute orientation of the sensor as a quaternion."""
        ...

    def getPosition(self) -> Position:
        """Returns the current position of the sensor as calculated by doubly integrating the observed sensor accelerations."""
        ...

    def getVelocity(self) -> Velocity:
        """Returns the current velocity of the sensor as calculated by integrating the observed sensor accelerations."""
        ...

    def getAcceleration(self) -> Acceleration:
        """Returns the last observed acceleration of the sensor. Note that this does not communicate with the sensor, but rather returns the most recent value reported to the acceleration integration algorithm."""
        ...

    def startAccelerationIntegration(self, initialPosition: Position, initialVelocity: Velocity, msPollInterval: int) -> None:
        """Start (or re-start) a thread that continuously at intervals polls the current linear acceleration of the sensor and integrates it to provide velocity and position information."""
        ...

    def stopAccelerationIntegration(self) -> None:
        """Stop the integration thread if it is currently running."""
        ...

    def getSystemStatus(self) -> BNO055IMU.SystemStatus:
        """Returns the current status of the system."""
        ...

    def getSystemError(self) -> BNO055IMU.SystemError:
        """If #getSystemStatus() is 'system error' (1), returns particulars regarding that error. See section 4.3.58 of the BNO055 specification."""
        ...

    def getCalibrationStatus(self) -> BNO055IMU.CalibrationStatus:
        """Returns the calibration status of the IMU"""
        ...

    def isSystemCalibrated(self) -> bool:
        """Answers as to whether the system is fully calibrated. The system is fully calibrated if the gyro, accelerometer, and magnetometer are fully calibrated."""
        ...

    def isGyroCalibrated(self) -> bool:
        """Answers as to whether the gyro is fully calibrated."""
        ...

    def isAccelerometerCalibrated(self) -> bool:
        """Answers as to whether the accelerometer is fully calibrated."""
        ...

    def isMagnetometerCalibrated(self) -> bool:
        """Answers as to whether the magnetometer is fully calibrated."""
        ...

    def readCalibrationData(self) -> BNO055IMU.CalibrationData:
        """Read calibration data from the IMU which later can be restored with writeCalibrationData(). This might be persistently stored, and reapplied at a later power-on. For greatest utility, full calibration should be achieved before reading the calibration data."""
        ...

    def writeCalibrationData(self, data: BNO055IMU.CalibrationData) -> None:
        """Write calibration data previously retrieved."""
        ...

    def read8(self, register: BNO055IMU.Register) -> int:
        """Low level: read the byte starting at the indicated register"""
        ...

    def read(self, register: BNO055IMU.Register, cb: int) -> list[int]:
        """Low level: read data starting at the indicated register"""
        ...

    def write8(self, register: BNO055IMU.Register, bVal: int) -> None:
        """Low level: write a byte to the indicated register"""
        ...

    def write(self, register: BNO055IMU.Register, data: list[int]) -> None:
        """Low level: write data starting at the indicated register"""
        ...

    I2CADDR_UNSPECIFIED: I2cAddr
    I2CADDR_DEFAULT: I2cAddr
    I2CADDR_ALTERNATE: I2cAddr


class BNO055IMUImpl(I2cDeviceSynchDeviceWithParameters[I2cDeviceSynch, BNO055IMU.Parameters], BNO055IMU, IntegratingGyroscope, I2cAddrConfig, OpModeManagerNotifier.Notifications):
    """BNO055IMUImpl provides support for communicating with a BNO055 inertial motion unit. Sensors using this integrated circuit are available from several manufacturers."""
    __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl"
    class ImuNotInitializedException(Exception):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl.ImuNotInitializedException"
        def __init__(self) -> None:
            ...

    class VectorData:
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl.VectorData"
        def __init__(self, data: TimestampedData, scale: float) -> None:
            ...

        def next(self) -> float:
            ...

        data: TimestampedData
        scale: float
        buffer: Any

    class AccelerationManager:
        """Maintains current velocity and position by integrating acceleration"""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl.AccelerationManager"
        def __init__(self, msPollInterval: int) -> None:
            ...

        def run(self) -> None:
            ...

        msPollInterval: int
        nsPerMs: int

    class VECTOR(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl.VECTOR"
        ACCELEROMETER = enum.auto()
        MAGNETOMETER = enum.auto()
        GYROSCOPE = enum.auto()
        EULER = enum.auto()
        LINEARACCEL = enum.auto()
        GRAVITY = enum.auto()
        def getValue(self) -> int:
            ...

        value: int

    class POWER_MODE(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUImpl.POWER_MODE"
        NORMAL = enum.auto()
        LOWPOWER = enum.auto()
        SUSPEND = enum.auto()
        def getValue(self) -> int:
            ...

        value: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    @staticmethod
    def imuIsPresent(deviceClient: I2cDeviceSynchSimple, retryAfterWaiting: bool) -> bool:
        """The deviceClient parameter needs to already have its I2C address set."""
        ...

    @staticmethod
    def newWindow(regFirst: BNO055IMU.Register, regMax: BNO055IMU.Register) -> I2cDeviceSynch.ReadWindow:
        ...

    def throwIfNotInitialized(self) -> None:
        ...

    @staticmethod
    def disabledParameters() -> BNO055IMU.Parameters:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def onOpModePreInit(self, opMode: OpMode) -> None:
        ...

    def onOpModePreStart(self, opMode: OpMode) -> None:
        ...

    def onOpModePostStop(self, opMode: OpMode) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def internalInitialize(self, parameters: BNO055IMU.Parameters) -> bool:
        """Initialize the device to be running in the indicated operation mode"""
        ...

    def internalInitializeOnce(self, expectedStatus: BNO055IMU.SystemStatus) -> bool:
        """Do one attempt at initializing the device to be running in the indicated operation mode"""
        ...

    def setSensorMode(self, mode: BNO055IMU.SensorMode) -> None:
        ...

    def getSystemStatus(self) -> BNO055IMU.SystemStatus:
        ...

    def getSystemError(self) -> BNO055IMU.SystemError:
        ...

    def getCalibrationStatus(self) -> BNO055IMU.CalibrationStatus:
        ...

    def close(self) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getAngularVelocityAxes(self) -> set[Axis]:
        ...

    def getAngularOrientationAxes(self) -> set[Axis]:
        ...

    @overload
    def getAngularVelocity(self, unit: AngleUnit) -> AngularVelocity:
        ...
    @overload
    def getAngularVelocity(self) -> AngularVelocity:
        ...
    def getAngularVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getAngularOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...
    @overload
    def getAngularOrientation(self) -> Orientation:
        ...
    def getAngularOrientation(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def isSystemCalibrated(self) -> bool:
        ...

    def isGyroCalibrated(self) -> bool:
        ...

    def isAccelerometerCalibrated(self) -> bool:
        ...

    def isMagnetometerCalibrated(self) -> bool:
        ...

    def readCalibrationData(self) -> BNO055IMU.CalibrationData:
        ...

    def writeCalibrationData(self, data: BNO055IMU.CalibrationData) -> None:
        ...

    def getTemperature(self) -> Temperature:
        ...

    def getMagneticFieldStrength(self) -> MagneticFlux:
        ...

    def getOverallAcceleration(self) -> Acceleration:
        ...

    def getLinearAcceleration(self) -> Acceleration:
        ...

    def getGravity(self) -> Acceleration:
        ...

    def getQuaternionOrientation(self) -> Quaternion:
        ...

    def getAngularScale(self) -> float:
        """Return the number by which we need to divide a raw angle as read from the device in order to convert it to our current angular units. See Table 3-22 of the BNO055 spec"""
        ...

    def getAccelerationScale(self) -> float:
        """Return the number by which we need to divide a raw acceleration as read from the device in order to convert it to our current acceleration units. See Table 3-17 of the BNO055 spec."""
        ...

    def getMetersAccelerationScale(self) -> float:
        ...

    def getFluxScale(self) -> float:
        """Return the number by which we need to divide a raw acceleration as read from the device in order to convert it to our current angular units. See Table 3-19 of the BNO055 spec. Note that the BNO055 natively uses micro Teslas; we instead use Teslas."""
        ...

    def getVector(self, vector: BNO055IMUImpl.VECTOR, scale: float) -> BNO055IMUImpl.VectorData:
        ...

    def getAcceleration(self) -> Acceleration:
        ...

    def getVelocity(self) -> Velocity:
        ...

    def getPosition(self) -> Position:
        ...

    def startAccelerationIntegration(self, initalPosition: Position, initialVelocity: Velocity, msPollInterval: int) -> None:
        ...

    def stopAccelerationIntegration(self) -> None:
        ...

    def isStopRequested(self) -> bool:
        ...

    def read8(self, reg: BNO055IMU.Register) -> int:
        ...

    def read(self, reg: BNO055IMU.Register, cb: int) -> list[int]:
        ...

    def readShort(self, reg: BNO055IMU.Register) -> int:
        ...

    @overload
    def write8(self, reg: BNO055IMU.Register, data: int) -> None:
        ...
    @overload
    def write8(self, reg: BNO055IMU.Register, data: int, waitControl: I2cWaitControl) -> None:
        ...
    def write8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write(self, reg: BNO055IMU.Register, data: list[int]) -> None:
        ...
    @overload
    def write(self, reg: BNO055IMU.Register, data: list[int], waitControl: I2cWaitControl) -> None:
        ...
    def write(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def writeShort(self, reg: BNO055IMU.Register, value: int) -> None:
        ...

    def waitForWriteCompletions(self) -> None:
        ...

    def getLoggingTag(self) -> str:
        ...

    def log_v(self, format: str, *args: object) -> None:
        ...

    def log_d(self, format: str, *args: object) -> None:
        ...

    def log_w(self, format: str, *args: object) -> None:
        ...

    def log_e(self, format: str, *args: object) -> None:
        ...

    def ensureReadWindow(self, needed: I2cDeviceSynch.ReadWindow) -> None:
        ...

    def delayExtra(self, ms: int) -> None:
        ...

    def delayLoreExtra(self, ms: int) -> None:
        ...

    def delayLore(self, ms: int) -> None:
        """delayLore() implements a delay that only known by lore and mythology to be necessary."""
        ...

    def delay(self, ms: int) -> None:
        """delay() implements delays which are known to be necessary according to the BNO055 specification"""
        ...

    @overload
    def enterConfigModeFor(self, action: Any) -> None:
        ...
    @overload
    def enterConfigModeFor(self, lambda_: Func[T]) -> T:
        ...
    def enterConfigModeFor(self, *args: Any, **kwargs: Any) -> Any:
        ...

    dataLock: object
    accelerationAlgorithm: BNO055IMU.AccelerationIntegrator
    startStopLock: object
    accelerationMananger: Any
    delayScale: float
    msAwaitChipId: int
    msAwaitSelfTest: int
    readMode: I2cDeviceSynch.ReadMode
    lowerWindow: I2cDeviceSynch.ReadWindow
    """One of two primary register windows we use for reading from the BNO055. Given the maximum allowable size of a register window, the set of registers on a BNO055 can be usefully divided into two windows, which we here call lowerWindow and upperWindow. When we find the need to change register windows depending on what data is being requested from the sensor, we try to use these two windows so as to reduce the number of register window switching that might be required as other data is read in the future."""
    upperWindow: I2cDeviceSynch.ReadWindow
    """A second of two primary register windows we use for reading from the BNO055. We'd like to include the temperature register, too, but that would make a 27-byte window, and those don't (currently) work in the CDIM."""
    msExtra: int
    bCHIP_ID_VALUE: int


class AdafruitBNO055IMU(BNO055IMUImpl):
    """Instances of AdafruitBNO055IMU provide API access to an Adafruit Absolute Orientation Sensor."""
    __java__ = "com.qualcomm.hardware.adafruit.AdafruitBNO055IMU"
    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class BNO055IMUNew(I2cDeviceSynchDeviceWithParameters[I2cDeviceSynchSimple, IMU.Parameters], IMU):
    """BNO055 IMU driver that implements the new com.qualcomm.robotcore.hardware.IMU interface"""
    __java__ = "com.qualcomm.hardware.bosch.BNO055IMUNew"
    class Parameters(IMU.Parameters):
        """A version of the IMU.Parameters class that adds additional parameters specific to the BNO055 IMU."""
        __java__ = "com.qualcomm.hardware.bosch.BNO055IMUNew.Parameters"
        def __init__(self, imuOrientationOnRobot: ImuOrientationOnRobot) -> None:
            ...

        def copy(self) -> BNO055IMUNew.Parameters:
            ...

        i2cAddr: I2cAddr
        """The I2C address of the BNO055"""
        calibrationData: BNO055IMU.CalibrationData
        """Calibration data with which the BNO055 should be initialized."""
        calibrationDataFile: str
        """The path of a file containing calibration data with which the BNO055 should be initialized. If #calibrationData is not null, that will be used instead."""

    @overload
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        """Use this constructor for BNO055-based sensors that allow the I2C address to be changed"""
        ...
    @overload
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool, guaranteedAddress: I2cAddr) -> None:
        """Use this constructor for BNO055-based sensors that do NOT allow the I2C address to be changed"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def internalInitialize(self, genericParameters: IMU.Parameters) -> bool:
        ...

    def resetYaw(self) -> None:
        ...

    def getRobotYawPitchRollAngles(self) -> YawPitchRollAngles:
        ...

    def getRobotOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def getRobotOrientationAsQuaternion(self) -> Quaternion:
        ...

    def getRobotAngularVelocity(self, angleUnit: AngleUnit) -> AngularVelocity:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class AdafruitBNO055IMUNew(BNO055IMUNew):
    __java__ = "com.qualcomm.hardware.adafruit.AdafruitBNO055IMUNew"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class AMSColorSensor(ColorSensor, NormalizedColorSensor):
    """AMSColorSensor is an extension of ColorSensor that provides additional functionality supported by a family of color sensor chips from AMS."""
    __java__ = "com.qualcomm.hardware.ams.AMSColorSensor"
    class Parameters:
        """Instances of Parameters contain data indicating how the sensor is to be initialized."""
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Parameters"
        def __init__(self, i2cAddr: I2cAddr, deviceId: int) -> None:
            ...

        @staticmethod
        def atimeFromMs(msAccumulationInterval: float) -> int:
            """Returns the minimum integration register value ('atime') for which the accumulation interval is at least the indicated duration in length."""
            ...

        def integrationCycles(self) -> int:
            """Returns the number of 2.4ms integration cycles currently configured for each accumulation time interval"""
            ...

        def getMaximumReading(self) -> int:
            """Returns the maximum intensity count that can be reached in the currently configured accumulation time interval"""
            ...

        def msAccumulationInterval(self) -> float:
            """Returns the duration of the accumulation interval"""
            ...

        @staticmethod
        def createForTCS34725() -> AMSColorSensor.Parameters:
            ...

        @staticmethod
        def createForTMD37821() -> AMSColorSensor.Parameters:
            ...

        def clone(self) -> AMSColorSensor.Parameters:
            ...

        deviceId: int
        """the device id expected to be reported by the color sensor chip"""
        i2cAddr: I2cAddr
        """the address at which the sensor resides on the I2C bus."""
        gain: AMSColorSensor.Gain
        """the gain level to use for color sensing"""
        atime: int
        """the integration time to use for color sensing"""
        useProximityIfAvailable: bool
        """whether we should turn on the proximity functionality if it is available on the chip in question"""
        proximityPulseCount: int
        """when using the proximity functionality, controls the number of times the proximity LED is pulsed each cycle."""
        ledDrive: AMSColorSensor.LEDDrive
        """when using proximity, controls the nominal proximity LED drive current"""
        proximitySaturation: int
        """the maximum possible raw proximity value read. is sensitive to ledDrive and proximityPulseCount."""
        loggingEnabled: bool
        """debugging aid: enable logging for this device?"""
        loggingTag: str
        """debugging aid: the logging tag to use when logging"""
        readWindow: I2cDeviceSynch.ReadWindow
        """set of registers to read in background, if supported by underlying I2cDeviceSynch"""

    class Register(enum.Enum):
        """Register provides symbolic names for interesting device registers"""
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Register"
        ENABLE = enum.auto()
        ATIME = enum.auto()
        REGISTER2 = enum.auto()
        WTIME = enum.auto()
        AILT = enum.auto()
        AIHT = enum.auto()
        PERS = enum.auto()
        CONFIGURATION = enum.auto()
        PPLUSE = enum.auto()
        CONTROL = enum.auto()
        DEVICE_ID = enum.auto()
        STATUS = enum.auto()
        ALPHA = enum.auto()
        RED = enum.auto()
        GREEN = enum.auto()
        BLUE = enum.auto()
        PDATA = enum.auto()
        READ_WINDOW_FIRST = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        bVal: int

    class Enable(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Enable"
        RES7 = enum.auto()
        RES6 = enum.auto()
        PIEN = enum.auto()
        AIEN = enum.auto()
        WEN = enum.auto()
        PEN = enum.auto()
        AEN = enum.auto()
        PON = enum.auto()
        OFF = enum.auto()
        UNKNOWN = enum.auto()
        @overload
        def bitOr(self, him: AMSColorSensor.Enable) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class Wait(enum.Enum):
        """Wait time is set 2.4 ms increments unless the WLONG bit is asserted, in which case the wait times are 12× longer. WTIME is programmed as a 2’s complement number."""
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Wait"
        MS_2_4 = enum.auto()
        MS_204 = enum.auto()
        MS_614 = enum.auto()
        UNKNOWN = enum.auto()
        bVal: int

    class Pers(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Pers"
        CYCLE_NONE = enum.auto()
        CYCLE_1 = enum.auto()
        CYCLE_2 = enum.auto()
        CYCLE_3 = enum.auto()
        CYCLE_5 = enum.auto()
        CYCLE_10 = enum.auto()
        CYCLE_15 = enum.auto()
        CYCLE_20 = enum.auto()
        CYCLE_25 = enum.auto()
        CYCLE_30 = enum.auto()
        CYCLE_35 = enum.auto()
        CYCLE_40 = enum.auto()
        CYCLE_45 = enum.auto()
        CYCLE_50 = enum.auto()
        CYCLE_55 = enum.auto()
        CYCLE_60 = enum.auto()
        UNKNOWN = enum.auto()
        bVal: int

    class Config(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Config"
        NORMAL = enum.auto()
        LONG_WAIT = enum.auto()
        bVal: int

    class Gain(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Gain"
        UNKNOWN = enum.auto()
        GAIN_1 = enum.auto()
        GAIN_4 = enum.auto()
        GAIN_16 = enum.auto()
        GAIN_64 = enum.auto()
        MASK = enum.auto()
        @staticmethod
        def fromByte(byteVal: int) -> AMSColorSensor.Gain:
            ...

        bVal: int

    class LEDDrive(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.LEDDrive"
        Percent100 = enum.auto()
        Percent50 = enum.auto()
        Percent25 = enum.auto()
        Percent12_5 = enum.auto()
        MASK = enum.auto()
        bVal: int

    class Status(enum.Enum):
        __java__ = "com.qualcomm.hardware.ams.AMSColorSensor.Status"
        PINT = enum.auto()
        AINT = enum.auto()
        PVALID = enum.auto()
        AVALID = enum.auto()
        bVal: int

    def initialize(self, parameters: AMSColorSensor.Parameters) -> bool:
        """Initialize the sensor using the indicated set of parameters."""
        ...

    def getParameters(self) -> AMSColorSensor.Parameters:
        """Returns the parameters which which initialization was last attempted, if any"""
        ...

    def getDeviceID(self) -> int:
        """Returns the flavor of the AMS color sensor as reported by the chip itself"""
        ...

    def read8(self, register: AMSColorSensor.Register) -> int:
        """Low level: read the byte starting at the indicated register"""
        ...

    def read(self, register: AMSColorSensor.Register, cb: int) -> list[int]:
        """Low level: read data starting at the indicated register"""
        ...

    def write8(self, register: AMSColorSensor.Register, bVal: int) -> None:
        """Low level: write a byte to the indicated register"""
        ...

    def write(self, register: AMSColorSensor.Register, data: list[int]) -> None:
        """Low level: write data starting at the indicated register"""
        ...

    AMS_TCS34725_ADDRESS: I2cAddr
    AMS_TMD37821_ADDRESS: I2cAddr
    AMS_TCS34725_ID: int
    AMS_TMD37821_ID: int
    AMS_TMD37823_ID: int
    AMS_COLOR_COMMAND_BIT: int
    AMS_COLOR_COMMAND_TYPE_REPEATED_BYTE: int
    AMS_COLOR_COMMAND_TYPE_AUTO_INCREMENT: int
    AMS_COLOR_COMMAND_TYPE_RESERVED: int
    AMS_COLOR_COMMAND_TYPE_SPECIAL: int


class AMSColorSensorImpl(I2cDeviceSynchDeviceWithParameters[I2cDeviceSynchSimple, AMSColorSensor.Parameters], AMSColorSensor, I2cAddrConfig, Light):
    """AMSColorSensorImpl is used to support the Adafruit color sensor: http://adafru.it/1334 https://www.adafruit.com/products/1334?&amp;main_page=product_info&amp;products_id=1334 https://github.com/adafruit/Adafruit_TCS34725 More generally, there is a family of color sensors from AMS which this could support http://ams.com/eng/Support/Demoboards/Light-Sensors/(show)/145298 This implementation sits on top of I2cDeviceSynchSimple instead of I2cDevice. That said, if an I2cDeviceSynch is provided instead, advantage will be taken thereof. This class is declared abstract. Subclasses in user code should add @I2cSensor annotations to allow proper registration and life cycle management."""
    __java__ = "com.qualcomm.hardware.ams.AMSColorSensorImpl"
    def __init__(self, params: AMSColorSensor.Parameters, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def internalInitialize(self, parameters: AMSColorSensor.Parameters) -> bool:
        ...

    def dumpState(self) -> None:
        ...

    def enable(self) -> None:
        ...

    def disable(self) -> None:
        ...

    def isConnectedAndEnabled(self) -> bool:
        """Return whether we know we are enabled and still actively able to talk to the device"""
        ...

    @overload
    def testBits(self, value: int, desired: int) -> bool:
        ...
    @overload
    def testBits(self, value: int, mask: int, desired: int) -> bool:
        ...
    @overload
    def testBits(self, value: int, desired: AMSColorSensor.Enable) -> bool:
        ...
    @overload
    def testBits(self, value: int, mask: AMSColorSensor.Enable, desired: AMSColorSensor.Enable) -> bool:
        ...
    def testBits(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def writeEnable(self, value: int) -> None:
        ...

    def readEnable(self) -> int:
        ...

    def readEnableAfterWrite(self) -> int:
        ...

    def setIntegrationTime(self, atime: int) -> None:
        ...

    def setProximityPulseCount(self, proximityPulseCount: int) -> None:
        """From the TMD3782 datasheet: \"When the proximity detection feature is enabled (PEN), the state machine transitions through the Prox Accum, Prox Wait, and Prox ADC states. The Prox Wait time is a fixed 2.4 ms, whereas the Prox Accum time is determined by the number of proximity LED pulses (PPULSE) and the Prox ADC time is determined by the integration time (PTIME). The formulas to determine the Prox Accum and Prox ADC times are given in the associated boxes in Figure 25. If an interrupt is generated as a result of the proximity cycle, it will be asserted at the end of the Prox ADC state.\" Note: the reference to PTIME in the above seems to be an error, as there is no such register. Though there MIGHT be, but the documentation has been pulled for some reason: mysteriously, register=x02 is missing. Perhaps it was there, and is now undocumented? If PTIME is in fact register two, then it's reset value seems to be 0xff. Which should be the shortest possible integration time."""
        ...

    def is3782(self) -> bool:
        ...

    def setHardwareGain(self, gain: AMSColorSensor.Gain) -> None:
        ...

    def setPDrive(self, ledDrive: AMSColorSensor.LEDDrive) -> None:
        ...

    def updateControl(self, mask: int, value: int) -> None:
        ...

    def getDeviceID(self) -> int:
        ...

    def getGain(self) -> float:
        ...

    def setGain(self, newGain: float) -> None:
        ...

    def red(self) -> int:
        """In this implementation, the Color methods return 16 bit unsigned values."""
        ...

    def green(self) -> int:
        ...

    def blue(self) -> int:
        ...

    def alpha(self) -> int:
        ...

    def normalToUnsignedShort(self, normal: float) -> int:
        ...

    def argb(self) -> int:
        ...

    def getNormalizedColors(self) -> NormalizedRGBA:
        ...

    def enableLed(self, enable: bool) -> None:
        ...

    def isLightOn(self) -> bool:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def setI2cAddress(self, i2cAddr: I2cAddr) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def readUnsignedByte(self, reg: AMSColorSensor.Register) -> int:
        ...

    def readUnsignedShort(self, reg: AMSColorSensor.Register, byteOrder: Any) -> int:
        ...

    def read8(self, reg: AMSColorSensor.Register) -> int:
        ...

    def read(self, reg: AMSColorSensor.Register, cb: int) -> list[int]:
        ...

    def write8(self, reg: AMSColorSensor.Register, data: int) -> None:
        ...

    def write(self, reg: AMSColorSensor.Register, data: list[int]) -> None:
        ...

    def delay(self, ms: int) -> None:
        ...

    TAG: str


class AdafruitI2cColorSensor(AMSColorSensorImpl):
    """AdafruitI2cColorSensor provides an implementation of color sensor functionality for the AdaFruit color sensor"""
    __java__ = "com.qualcomm.hardware.adafruit.AdafruitI2cColorSensor"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class AndyMarkColorSensor(I2cDeviceSynchDevice[I2cDeviceSynch], ColorRangeSensor):
    """AndyMark Proximity and Color Sensor Driver Author: Jonathan Lane Organization: AndyMark, Inc. Description: Driver for the AndyMark Proximity and Color Sensor It enables measurements of Proximity, Ambient Light, Red, Green, Blue Values"""
    __java__ = "com.qualcomm.hardware.andymark.AndyMarkColorSensor"
    class ProximityGain(enum.Enum):
        __java__ = "com.qualcomm.hardware.andymark.AndyMarkColorSensor.ProximityGain"
        GAIN_1X = enum.auto()
        GAIN_2X = enum.auto()
        GAIN_4X = enum.auto()
        GAIN_8X = enum.auto()
        bits: int

    class ProximityPulseLength(enum.Enum):
        __java__ = "com.qualcomm.hardware.andymark.AndyMarkColorSensor.ProximityPulseLength"
        LENGTH_4US = enum.auto()
        LENGTH_8US = enum.auto()
        LENGTH_16US = enum.auto()
        LENGTH_32US = enum.auto()
        bits: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        """Returns the name of the device."""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        """Returns the manufacturer of the sensor."""
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        """Sets a new I2C address for the sensor."""
        ...

    def getI2cAddress(self) -> I2cAddr:
        """Returns the I2C address currently assigned to the sensor."""
        ...

    def doInitialize(self) -> bool:
        """Performs internal initialization and status check."""
        ...

    def classifyColor(self) -> str:
        """Classifies the perceived color using raw RGB sensor values with calibrated thresholds."""
        ...

    def argb(self) -> int:
        """Returns a packed 32-bit Android-style ARGB color value."""
        ...

    def getNormalizedColors(self) -> NormalizedRGBA:
        """Returns the color sensor readings normalized to a range of [0, 1]. Normalization allows color values to be compared independent of ambient light intensity."""
        ...

    def alpha(self) -> int:
        """Reads the ambient (clear) light level from the sensor."""
        ...

    def getRawLightDetected(self) -> float:
        """Returns the raw light detected by the sensor, normalized to a [0.0, 1.0] range. This is typically based on the clear (ambient) light channel."""
        ...

    def getLightDetected(self) -> float:
        """Returns the normalized light detection value. Typically identical to #getRawLightDetected() for sensors without built-in filtering."""
        ...

    def getRawLightDetectedMax(self) -> float:
        """Returns the maximum possible value for raw light detection."""
        ...

    def red(self) -> int:
        """Reads the red color component from the sensor."""
        ...

    def green(self) -> int:
        """Reads the green color component from the sensor."""
        ...

    def blue(self) -> int:
        """Reads the blue color component from the sensor."""
        ...

    def enableLed(self, enable: bool) -> None:
        """Enables or disables the sensor's LED, if available."""
        ...

    def setGain(self, gain: float) -> None:
        """Sets the gain for the color sensor."""
        ...

    def getGain(self) -> float:
        """Returns the gain setting currently applied to the color sensor."""
        ...

    def getDistance(self, unit: DistanceUnit) -> float:
        """Returns a calibrated, linear sense of distance as read by the infrared proximity part of the TMD3725 sensor. Distance is measured to the plastic housing at the front of the sensor. Natively, the raw optical signal follows an inverse relationship. Here, parameters have been fitted to turn that into a linear measure of distance. The function fitted was of the form: RawProximity = a * distance^b + c Calibration is based on the default settings from the TMD3725 datasheet using 6 pulses at 90mA with default gain and pulse length. Reflectivity and surface angle will affect results and user should validate calibration for specific applications."""
        ...

    def getProximity(self) -> int:
        """Reads the proximity measurement from the sensor."""
        ...

    def setProximityGain(self, gain: AndyMarkColorSensor.ProximityGain) -> None:
        """Sets the proximity gain used by the TMD3725 sensor during proximity measurements."""
        ...

    def setProximityLedPulses(self, pulses: int) -> None:
        """Sets the number of IR LED pulses emitted during a single proximity measurement."""
        ...

    def setProximityLedPulseLength(self, pulseLength: AndyMarkColorSensor.ProximityPulseLength) -> None:
        """Sets the IR LED pulse duration used during proximity measurements."""
        ...

    def configureProximitySettings(self, gain: AndyMarkColorSensor.ProximityGain, pulses: int, pulseLength: AndyMarkColorSensor.ProximityPulseLength) -> None:
        """Configures proximity sensor settings in one call: gain, number of pulses, and pulse length."""
        ...

    def status(self) -> str:
        """Returns a status string indicating the connection status of the device. Useful for telemetry or debugging output."""
        ...


class AndyMarkIMU(BNO055IMUNew):
    """AndyMark 9-Axis IMU Driver Author: Jonathan Lane Organization: AndyMark, Inc. Description: This class provides a hardware abstraction layer for the AndyMark 9-Axis IMU, which is based on the Bosch BNO055 sensor. It extends the `BNO055IMUNew` class from the FTC SDK and registers as a built-in I2C device for automatic configuration."""
    __java__ = "com.qualcomm.hardware.andymark.AndyMarkIMU"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    def getDeviceName(self) -> str:
        """Returns the name of this device for display in the Driver Station and SDK internals."""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        """Returns the manufacturer of this device. Although AndyMark distributes the hardware, the internal BNO055 chip is manufactured by Bosch and this device is represented internally as a Lynx component."""
        ...


class AndyMarkIMUOrientationOnRobot(ImuOrientationOnRobot):
    """The orientation at which an AndyMark IMU is mounted to a robot."""
    __java__ = "com.qualcomm.hardware.andymark.AndyMarkIMUOrientationOnRobot"
    class LogoFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.andymark.AndyMarkIMUOrientationOnRobot.LogoFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    class I2cPortFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.andymark.AndyMarkIMUOrientationOnRobot.I2cPortFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    @overload
    def __init__(self, logoFacingDirection: AndyMarkIMUOrientationOnRobot.LogoFacingDirection, i2cPortFacingDirection: AndyMarkIMUOrientationOnRobot.I2cPortFacingDirection) -> None:
        """Constructs an AndyMarkIMUOrientationOnRobot for an AndyMark IMU that is mounted orthogonally to a robot. This is the easiest constructor to use. Simply specify which direction on the robot that the AndyMark logo on the IMU is facing, and the direction that the I2C port on the IMU is facing."""
        ...
    @overload
    def __init__(self, rotation: Orientation) -> None:
        """Constructs an AndyMarkIMUOrientationOnRobot for an AndyMark IMU that is mounted at any arbitrary angle on a robot using an Orientation object."""
        ...
    @overload
    def __init__(self, rotation: Quaternion) -> None:
        """Constructs an AndyMarkIMUOrientationOnRobot for an AndyMark IMU that is mounted at any arbitrary angle on a robot using a Quaternion object."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def imuCoordinateSystemOrientationFromPerspectiveOfRobot(self) -> Quaternion:
        ...

    def imuRotationOffset(self) -> Quaternion:
        ...

    def angularVelocityTransform(self) -> Quaternion:
        ...

    @staticmethod
    def friendlyApiToOrientation(logoFacingDirection: AndyMarkIMUOrientationOnRobot.LogoFacingDirection, i2cPortFacingDirection: AndyMarkIMUOrientationOnRobot.I2cPortFacingDirection) -> Orientation:
        ...

    @staticmethod
    def zyxOrientation(z: float, y: float, x: float) -> Orientation:
        ...

    @staticmethod
    def xyzOrientation(x: float, y: float, z: float) -> Orientation:
        ...


class VL53L0X(I2cDeviceSynchDevice[I2cDeviceSynch], DistanceSensor):
    """VL53L0X implements support for the STMicroelectronics VL53L0x time-of-flight distance sensor."""
    __java__ = "com.qualcomm.hardware.stmicroelectronics.VL53L0X"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.stmicroelectronics.VL53L0X.Register"
        SYSRANGE_START = enum.auto()
        SYSTEM_THRESH_HIGH = enum.auto()
        SYSTEM_THRESH_LOW = enum.auto()
        SYSTEM_SEQUENCE_CONFIG = enum.auto()
        SYSTEM_RANGE_CONFIG = enum.auto()
        SYSTEM_INTERMEASUREMENT_PERIOD = enum.auto()
        SYSTEM_INTERRUPT_CONFIG_GPIO = enum.auto()
        GPIO_HV_MUX_ACTIVE_HIGH = enum.auto()
        SYSTEM_INTERRUPT_CLEAR = enum.auto()
        RESULT_INTERRUPT_STATUS = enum.auto()
        RESULT_RANGE_STATUS = enum.auto()
        RESULT_CORE_AMBIENT_WINDOW_EVENTS_RTN = enum.auto()
        RESULT_CORE_RANGING_TOTAL_EVENTS_RTN = enum.auto()
        RESULT_CORE_AMBIENT_WINDOW_EVENTS_REF = enum.auto()
        RESULT_CORE_RANGING_TOTAL_EVENTS_REF = enum.auto()
        RESULT_PEAK_SIGNAL_RATE_REF = enum.auto()
        ALGO_PART_TO_PART_RANGE_OFFSET_MM = enum.auto()
        I2C_SLAVE_DEVICE_ADDRESS = enum.auto()
        MSRC_CONFIG_CONTROL = enum.auto()
        PRE_RANGE_CONFIG_MIN_SNR = enum.auto()
        PRE_RANGE_CONFIG_VALID_PHASE_LOW = enum.auto()
        PRE_RANGE_CONFIG_VALID_PHASE_HIGH = enum.auto()
        PRE_RANGE_MIN_COUNT_RATE_RTN_LIMIT = enum.auto()
        FINAL_RANGE_CONFIG_MIN_SNR = enum.auto()
        FINAL_RANGE_CONFIG_VALID_PHASE_LOW = enum.auto()
        FINAL_RANGE_CONFIG_VALID_PHASE_HIGH = enum.auto()
        FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = enum.auto()
        PRE_RANGE_CONFIG_SIGMA_THRESH_HI = enum.auto()
        PRE_RANGE_CONFIG_SIGMA_THRESH_LO = enum.auto()
        PRE_RANGE_CONFIG_VCSEL_PERIOD = enum.auto()
        PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI = enum.auto()
        PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO = enum.auto()
        SYSTEM_HISTOGRAM_BIN = enum.auto()
        HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT = enum.auto()
        HISTOGRAM_CONFIG_READOUT_CTRL = enum.auto()
        FINAL_RANGE_CONFIG_VCSEL_PERIOD = enum.auto()
        FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI = enum.auto()
        FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO = enum.auto()
        CROSSTALK_COMPENSATION_PEAK_RATE_MCPS = enum.auto()
        MSRC_CONFIG_TIMEOUT_MACROP = enum.auto()
        SOFT_RESET_GO2_SOFT_RESET_N = enum.auto()
        IDENTIFICATION_MODEL_ID = enum.auto()
        IDENTIFICATION_REVISION_ID = enum.auto()
        OSC_CALIBRATE_VAL = enum.auto()
        GLOBAL_CONFIG_VCSEL_WIDTH = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_0 = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_1 = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_2 = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_3 = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_4 = enum.auto()
        GLOBAL_CONFIG_SPAD_ENABLES_REF_5 = enum.auto()
        GLOBAL_CONFIG_REF_EN_START_SELECT = enum.auto()
        DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD = enum.auto()
        DYNAMIC_SPAD_REF_EN_START_OFFSET = enum.auto()
        POWER_MANAGEMENT_GO1_POWER_FORCE = enum.auto()
        VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV = enum.auto()
        ALGO_PHASECAL_LIM = enum.auto()
        ALGO_PHASECAL_CONFIG_TIMEOUT = enum.auto()
        bVal: int

    class vcselPeriodType(enum.Enum):
        __java__ = "com.qualcomm.hardware.stmicroelectronics.VL53L0X.vcselPeriodType"
        VcselPeriodPreRange = enum.auto()
        VcselPeriodFinalRange = enum.auto()

    class SequenceStepEnables:
        __java__ = "com.qualcomm.hardware.stmicroelectronics.VL53L0X.SequenceStepEnables"
        tcc: bool
        msrc: bool
        dss: bool
        pre_range: bool
        final_range: bool

    class SequenceStepTimeouts:
        __java__ = "com.qualcomm.hardware.stmicroelectronics.VL53L0X.SequenceStepTimeouts"
        pre_range_vcsel_period_pclks: int
        final_range_vcsel_period_pclks: int
        msrc_dss_tcc_mclks: int
        pre_range_mclks: int
        final_range_mclks: int
        msrc_dss_tcc_us: int
        pre_range_us: int
        final_range_us: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getModelID(self) -> int:
        ...

    def getDistance(self, unit: DistanceUnit) -> float:
        ...

    def didTimeoutOccur(self) -> bool:
        """Did a timeout occur?"""
        ...

    def doInitialize(self) -> bool:
        ...

    def getMeasurementTimingBudget(self) -> int:
        ...

    def getSequenceStepEnables(self, enables: VL53L0X.SequenceStepEnables) -> None:
        ...

    def getSequenceStepTimeouts(self, enables: VL53L0X.SequenceStepEnables, timeouts: VL53L0X.SequenceStepTimeouts) -> None:
        ...

    def decodeTimeout(self, reg_val: int) -> int:
        ...

    def getVcselPulsePeriod(self, type: VL53L0X.vcselPeriodType) -> int:
        ...

    def decodeVcselPeriod(self, reg_val: int) -> int:
        ...

    def timeoutMclksToMicroseconds(self, timeout_period_mclks: int, vcsel_period_pclks: int) -> int:
        ...

    def calcMacroPeriod(self, vcsel_period_pclks: int) -> int:
        ...

    def setMeasurementTimingBudget(self, budget_us: int) -> bool:
        ...

    def timeoutMicrosecondsToMclks(self, timeout_period_us: int, vcsel_period_pclks: int) -> int:
        ...

    def encodeTimeout(self, timeout_mclks: int) -> int:
        ...

    def performSingleRefCalibration(self, vhv_init_byte: int) -> bool:
        ...

    @overload
    def startContinuous(self) -> None:
        ...
    @overload
    def startContinuous(self, period_ms: int) -> None:
        ...
    def startContinuous(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def stopContinuous(self) -> None:
        ...

    def setTimeout(self, timeout: int) -> None:
        ...

    def getTimeout(self) -> int:
        ...

    def readRangeContinuousMillimeters(self) -> int:
        ...

    @overload
    def readReg(self, reg: VL53L0X.Register) -> int:
        ...
    @overload
    def readReg(self, bVal: int) -> int:
        ...
    @overload
    def readReg(self, iVal: int) -> int:
        ...
    def readReg(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def writeReg(self, reg: VL53L0X.Register, value: int) -> None:
        ...
    @overload
    def writeReg(self, addr: int, value: int) -> None:
        ...
    @overload
    def writeReg(self, addr: int, value: int) -> None:
        ...
    @overload
    def writeReg(self, reg: VL53L0X.Register, value: int, waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def writeReg(self, addr: int, value: int, waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def writeReg(self, addr: int, value: int, waitControl: I2cWaitControl) -> None:
        ...
    def writeReg(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readUnsignedByte(self, reg: VL53L0X.Register) -> int:
        ...

    def writeShort(self, reg: VL53L0X.Register, value: int) -> None:
        ...

    def readShort(self, reg: VL53L0X.Register) -> int:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr
    FAKE_DISTANCE_MM: int
    MYTAG: str
    measurement_timing_budget_us: int
    io_timeout: int
    ioElapsedTime: ElapsedTime
    did_timeout: bool
    assume_uninitialized: bool


class AndyMarkTOF(VL53L0X):
    """AndyMark 2m TOF Lidar Driver Author: Jonathan Lane Organization: AndyMark, Inc. Description: This class provides a hardware abstraction layer for the AndyMark 2-meter Time-of-Flight (TOF) Lidar sensor, which is based on the STMicroelectronics VL53L0X. It extends the `VL53L0X` class from the FTC SDK and registers as a built-in I2C device for automatic recognition in configuration files. Features: - Provides distance measurements up to 2 meters using laser-based time-of-flight technology. - Fully integrates with FTC SDK I2C device handling. Note: Ensure the I2C address and wiring match your configuration. Performance may vary depending on lighting conditions and surface reflectivity."""
    __java__ = "com.qualcomm.hardware.andymark.AndyMarkTOF"
    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        """Returns the name of this device for display in the Driver Station and SDK internals."""
        ...


class BHI260IMU(I2cDeviceSynchDeviceWithParameters[I2cDeviceSynchSimple, IMU.Parameters], IMU):
    __java__ = "com.qualcomm.hardware.bosch.BHI260IMU"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.Register"
        COMMAND_INPUT = enum.auto()
        WAKE_UP_FIFO_OUTPUT = enum.auto()
        NON_WAKE_UP_FIFO_OUTPUT = enum.auto()
        STATUS_AND_DEBUG_FIFO_OUTPUT = enum.auto()
        CHIP_CONTROL = enum.auto()
        HOST_INTERFACE_CONTROL = enum.auto()
        HOST_INTERRUPT_CONTROL = enum.auto()
        RESET_REQUEST = enum.auto()
        TIMESTAMP_EVENT_REQUEST = enum.auto()
        HOST_CONTROL = enum.auto()
        HOST_STATUS = enum.auto()
        PRODUCT_IDENTIFIER = enum.auto()
        REVISION_IDENTIFIER = enum.auto()
        ROM_VERSION = enum.auto()
        KERNEL_VERSION = enum.auto()
        USER_VERSION = enum.auto()
        FEATURE_STATUS = enum.auto()
        BOOT_STATUS = enum.auto()
        CHIP_ID = enum.auto()
        INTERRUPT_STATUS = enum.auto()
        ERROR_VALUE = enum.auto()
        GEN_PURPOSE_READ = enum.auto()

    class Fifo(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.Fifo"
        WAKE_UP = enum.auto()
        NON_WAKE_UP = enum.auto()
        STATUS_AND_DEBUG = enum.auto()

    class StatusAndDebugFifoMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.StatusAndDebugFifoMode"
        SYNCHRONOUS = enum.auto()
        ASYNCHRONOUS = enum.auto()

    class NonSensorEventType(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.NonSensorEventType"
        DEBUG_DATA = enum.auto()
        TIMESTAMP_SMALL_DELTA = enum.auto()
        TIMESTAMP_LARGE_DELTA = enum.auto()
        TIMESTAMP_FULL = enum.auto()
        META_EVENT = enum.auto()
        FILLER = enum.auto()
        PADDING = enum.auto()
        @staticmethod
        def findById(id: int) -> BHI260IMU.NonSensorEventType:
            ...

        nonWakeUpId: int
        wakeUpId: int

    class CommandType(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.CommandType"
        ERASE_FLASH = enum.auto()
        WRITE_FLASH = enum.auto()
        BOOT_FLASH = enum.auto()
        FIFO_FLUSH = enum.auto()
        CONFIGURE_SENSOR = enum.auto()
        CHANGE_SENSOR_DYNAMIC_RANGE = enum.auto()
        CONTROL_FIFO_FORMAT = enum.auto()
        @staticmethod
        def findById(id: int) -> BHI260IMU.CommandType:
            ...

    class CommandError(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.CommandError"
        INCORRECT_LENGTH = enum.auto()
        TOO_LONG = enum.auto()
        PARAM_WRITE_ERROR = enum.auto()
        PARAM_READ_ERROR = enum.auto()
        INVALID_COMMAND = enum.auto()
        INVALID_PARAM = enum.auto()
        COMMAND_FAILED = enum.auto()
        @staticmethod
        def fromInt(intValue: int) -> BHI260IMU.CommandError:
            ...

    class Sensor(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.Sensor"
        GAME_ROTATION_VECTOR_WAKE_UP = enum.auto()
        GAME_ROTATION_VECTOR_DATA_HOLDER = enum.auto()
        GAME_ROTATION_VECTOR_GPIO_HANDLER = enum.auto()
        GYROSCOPE_CORRECTED_DATA_HOLDER = enum.auto()
        GYROSCOPE_CORRECTED_GPIO_HANDLER = enum.auto()

    class BootStatusFlag(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.BootStatusFlag"
        FLASH_DETECTED = enum.auto()
        FLASH_VERIFY_DONE = enum.auto()
        FLASH_VERIFY_ERROR = enum.auto()
        NO_FLASH = enum.auto()
        HOST_INTERFACE_READY = enum.auto()
        FIRMWARE_VERIFY_DONE = enum.auto()
        FIRMWARE_VERIFY_ERROR = enum.auto()
        FIRMWARE_HALTED = enum.auto()

    class InterruptStatusFlag(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.InterruptStatusFlag"
        HOST_INTERRUPT_ASSERTED = enum.auto()
        WAKE_UP_FIFO_STATUS_1 = enum.auto()
        WAKE_UP_FIFO_STATUS_2 = enum.auto()
        NON_WAKE_UP_FIFO_STATUS_1 = enum.auto()
        NON_WAKE_UP_FIFO_STATUS_2 = enum.auto()
        STATUS_STATUS = enum.auto()
        DEBUG_STATUS = enum.auto()
        RESET_OR_FAULT = enum.auto()

    class HostInterfaceControlFlag(enum.Enum):
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.HostInterfaceControlFlag"
        ABORT_TRANSFER_CHANNEL_0 = enum.auto()
        ABORT_TRANSFER_CHANNEL_1 = enum.auto()
        ABORT_TRANSFER_CHANNEL_2 = enum.auto()
        ABORT_TRANSFER_CHANNEL_3 = enum.auto()
        APPLICATION_PROCESSOR_SUSPENDED = enum.auto()
        RESERVED = enum.auto()
        TIMESTAMP_EVENT_REQUEST = enum.auto()
        ASYNC_STATUS_CHANNEL = enum.auto()

    class InitException(Exception):
        """Public-facing methods should not throw this exception."""
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.InitException"

    class CommandFailureException(Exception):
        """Public-facing methods should not throw this exception."""
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.CommandFailureException"
        def __init__(self, message: str) -> None:
            ...

    class StatusPacket:
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.StatusPacket"
        statusCode: int
        payload: list[int]

    class StatusAndDebugFifoModeManager:
        __java__ = "com.qualcomm.hardware.bosch.BHI260IMU.StatusAndDebugFifoModeManager"
        def lockStatusAndDebugFifoMode(self, deviceClient: I2cDeviceSynchSimple, mode: BHI260IMU.StatusAndDebugFifoMode) -> None:
            """Set the Status and Debug FIFO mode, and prevent other threads from changing it until this thread calls #unlockStatusAndDebugFifoMode()"""
            ...

        def unlockStatusAndDebugFifoMode(self) -> None:
            """Allow other threads to change the Status and Debug FIFO mode"""
            ...

    def __init__(self, i2cDeviceSynchSimple: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    @staticmethod
    def imuIsPresent(deviceClient: I2cDeviceSynchSimple) -> bool:
        ...

    @staticmethod
    def flashFirmwareIfNecessary(deviceClient: I2cDeviceSynchSimple) -> None:
        ...

    def internalInitialize(self, parameters: IMU.Parameters) -> bool:
        ...

    def resetYaw(self) -> None:
        ...

    def getRobotYawPitchRollAngles(self) -> YawPitchRollAngles:
        ...

    def getRobotOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def getRobotOrientationAsQuaternion(self) -> Quaternion:
        ...

    def getRobotAngularVelocity(self, angleUnit: AngleUnit) -> AngularVelocity:
        ...

    def getRawQuaternion(self) -> Quaternion:
        ...

    def getRawAngularVelocity(self) -> AngularVelocity:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getFirmwareVersion(self) -> int:
        ...

    DIAGNOSTIC_MODE: bool
    DIAGNOSTIC_MODE_FIFO_PARSING: bool


class BNO055Util:
    __java__ = "com.qualcomm.hardware.bosch.BNO055Util"
    class InitException(Exception):
        __java__ = "com.qualcomm.hardware.bosch.BNO055Util.InitException"
        def __init__(self, message: str) -> None:
            ...

    @staticmethod
    def sharedInit(deviceClient: I2cDeviceSynchSimple, parameters: BNO055IMU.Parameters) -> None:
        """The deviceClient parameter needs to already have its I2C address set."""
        ...

    @staticmethod
    def imuIsPresent(deviceClient: I2cDeviceSynchSimple, retryAfterWaiting: bool) -> bool:
        """The deviceClient parameter needs to already have its I2C address set."""
        ...

    @staticmethod
    def getSystemStatus(deviceClient: I2cDeviceSynchSimple, tag: str) -> BNO055IMU.SystemStatus:
        ...

    @staticmethod
    def writeCalibrationData(deviceClient: I2cDeviceSynchSimple, data: BNO055IMU.CalibrationData) -> None:
        ...

    @staticmethod
    def setSensorMode(deviceClient: I2cDeviceSynchSimple, mode: BNO055IMU.SensorMode) -> None:
        ...

    @staticmethod
    def getSensorMode(deviceClient: I2cDeviceSynchSimple) -> BNO055IMU.SensorMode:
        ...

    @staticmethod
    def getRawQuaternion(deviceClient: I2cDeviceSynchSimple) -> Quaternion:
        ...

    @staticmethod
    def getRawAngularVelocity(deviceClient: I2cDeviceSynchSimple, angleUnitConfiguredOnImu: BNO055IMU.AngleUnit, desiredAngleUnit: AngleUnit) -> AngularVelocity:
        ...

    @staticmethod
    def getAngularScale(angleUnit: BNO055IMU.AngleUnit) -> float:
        ...

    @staticmethod
    def read8(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register) -> int:
        ...

    @staticmethod
    def read(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register, cb: int) -> list[int]:
        ...

    @overload
    @staticmethod
    def write8(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register, data: int) -> None:
        ...
    @overload
    @staticmethod
    def write8(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register, data: int, waitControl: I2cWaitControl) -> None:
        ...
    @staticmethod
    def write8(*args: Any, **kwargs: Any) -> Any:
        ...

    @staticmethod
    def write(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register, data: list[int]) -> None:
        ...

    @staticmethod
    def writeShort(deviceClient: I2cDeviceSynchSimple, reg: BNO055IMU.Register, value: int) -> None:
        ...


class JustLoggingAccelerationIntegrator(BNO055IMU.AccelerationIntegrator):
    """JustLoggingAccelerationIntegrator is an integrator that doesn't actually integrate accelerations, but merely reports them in the logcat log. This is a debugging and demonstration tool, little more."""
    __java__ = "com.qualcomm.hardware.bosch.JustLoggingAccelerationIntegrator"
    def initialize(self, parameters: BNO055IMU.Parameters, initialPosition: Position, initialVelocity: Velocity) -> None:
        ...

    def getPosition(self) -> Position:
        ...

    def getVelocity(self) -> Velocity:
        ...

    def getAcceleration(self) -> Acceleration:
        ...

    def update(self, linearAcceleration: Acceleration) -> None:
        ...

    parameters: BNO055IMU.Parameters
    acceleration: Acceleration


class NaiveAccelerationIntegrator(BNO055IMU.AccelerationIntegrator):
    """NaiveAccelerationIntegrator provides a very naive implementation of an acceleration integration algorithm. It just does the basic physics. One you would actually want to use in a robot would, for example, likely filter noise out the acceleration data or more sophisticated processing."""
    __java__ = "com.qualcomm.hardware.bosch.NaiveAccelerationIntegrator"
    def __init__(self) -> None:
        ...

    def getPosition(self) -> Position:
        ...

    def getVelocity(self) -> Velocity:
        ...

    def getAcceleration(self) -> Acceleration:
        ...

    def initialize(self, parameters: BNO055IMU.Parameters, initialPosition: Position, initialVelocity: Velocity) -> None:
        ...

    def update(self, linearAcceleration: Acceleration) -> None:
        ...

    parameters: BNO055IMU.Parameters
    position: Position
    velocity: Velocity
    acceleration: Acceleration


class BroadcomColorSensor(ColorSensor, NormalizedColorSensor):
    """BroadcomColorSensor is an extension of ColorSensor that provides additional functionality supported by a family of color sensor chips from Broadcom."""
    __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor"
    class Parameters:
        """Instances of Parameters contain data indicating how the sensor is to be initialized."""
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.Parameters"
        def __init__(self, i2cAddr: I2cAddr, deviceId: int) -> None:
            ...

        @staticmethod
        def createForAPDS9151() -> BroadcomColorSensor.Parameters:
            ...

        def clone(self) -> BroadcomColorSensor.Parameters:
            ...

        deviceId: int
        """the device id expected to be reported by the color sensor chip"""
        i2cAddr: I2cAddr
        """the address at which the sensor resides on the I2C bus."""
        gain: BroadcomColorSensor.Gain
        """the gain level to use for color sensing"""
        proximityPulseCount: int
        """controls the number of times the proximity LED is pulsed each cycle."""
        proximityResolution: BroadcomColorSensor.PSResolution
        """number of bits used for proximity sensing"""
        proximityMeasRate: BroadcomColorSensor.PSMeasurementRate
        """periodic measurement rate for the proximity sensor"""
        lightSensorResolution: BroadcomColorSensor.LSResolution
        """number of bits used for light sensing"""
        lightSensorMeasRate: BroadcomColorSensor.LSMeasurementRate
        """periodic measurement rate for the light sensor"""
        ledCurrent: BroadcomColorSensor.LEDCurrent
        """when using proximity, controls the nominal proximity LED drive current"""
        proximitySaturation: int
        """the maximum possible raw proximity value read. is sensitive to ledDrive and proximityPulseCount."""
        colorSaturation: int
        """the maximum possible color value."""
        pulseModulation: BroadcomColorSensor.LEDPulseModulation
        """LED pulse modulation frequency."""
        loggingEnabled: bool
        """debugging aid: enable logging for this device?"""
        loggingTag: str
        """debugging aid: the logging tag to use when logging"""
        readWindow: I2cDeviceSynch.ReadWindow
        """set of registers to read in background, if supported by underlying I2cDeviceSynch"""

    class Register(enum.Enum):
        """Register provides symbolic names for interesting device registers"""
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.Register"
        MAIN_CTRL = enum.auto()
        PS_LED = enum.auto()
        PS_PULSES = enum.auto()
        PS_MEAS_RATE = enum.auto()
        LS_MEAS_RATE = enum.auto()
        LS_GAIN = enum.auto()
        PART_ID = enum.auto()
        MAIN_STATUS = enum.auto()
        PS_DATA = enum.auto()
        LS_DATA_IR = enum.auto()
        LS_DATA_GREEN = enum.auto()
        LS_DATA_BLUE = enum.auto()
        LS_DATA_RED = enum.auto()
        INT_CFG = enum.auto()
        INT_PST = enum.auto()
        PS_THRES_UP = enum.auto()
        PS_THRES_LOW = enum.auto()
        PS_CAN = enum.auto()
        LS_THRES_UP = enum.auto()
        LS_THRES_LOW = enum.auto()
        LS_THRES_VAR = enum.auto()
        READ_WINDOW_FIRST = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        bVal: int

    class MainControl(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.MainControl"
        RES7 = enum.auto()
        SAI_PS = enum.auto()
        SAI_LS = enum.auto()
        SW_RESET = enum.auto()
        RES3 = enum.auto()
        RGB_MODE = enum.auto()
        LS_EN = enum.auto()
        PS_EN = enum.auto()
        OFF = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.MainControl) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class MainStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.MainStatus"
        POWER_ON_STATUS = enum.auto()
        LS_INT_STAT = enum.auto()
        LS_DATA_STATUS = enum.auto()
        PS_LOGIC_SIG_STAT = enum.auto()
        PS_INT_STAT = enum.auto()
        PS_DATA_STAT = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.MainStatus) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class Gain(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.Gain"
        UNKNOWN = enum.auto()
        GAIN_1 = enum.auto()
        GAIN_3 = enum.auto()
        GAIN_6 = enum.auto()
        GAIN_9 = enum.auto()
        GAIN_18 = enum.auto()
        @staticmethod
        def fromByte(byteVal: int) -> BroadcomColorSensor.Gain:
            ...

        bVal: int

    class LEDCurrent(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.LEDCurrent"
        CURRENT_2_5mA = enum.auto()
        CURRENT_5mA = enum.auto()
        CURRENT_10mA = enum.auto()
        CURRENT_25mA = enum.auto()
        CURRENT_50mA = enum.auto()
        CURRENT_75mA = enum.auto()
        CURRENT_100mA = enum.auto()
        CURRENT_125mA = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.LEDCurrent) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class LEDPulseModulation(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.LEDPulseModulation"
        RES0 = enum.auto()
        RES1 = enum.auto()
        RES2 = enum.auto()
        LED_PULSE_60kHz = enum.auto()
        LED_PULSE_70kHz = enum.auto()
        LED_PULSE_80kHz = enum.auto()
        LED_PULSE_90kHz = enum.auto()
        LED_PULSE_100kHz = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.LEDPulseModulation) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class PSResolution(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.PSResolution"
        R8BIT = enum.auto()
        R9BIT = enum.auto()
        R10BIT = enum.auto()
        R11BIT = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.PSResolution) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class PSMeasurementRate(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.PSMeasurementRate"
        RES = enum.auto()
        R6_25ms = enum.auto()
        R12_5ms = enum.auto()
        R25ms = enum.auto()
        R50ms = enum.auto()
        R100ms = enum.auto()
        R200ms = enum.auto()
        R400ms = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.PSMeasurementRate) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class LSResolution(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.LSResolution"
        R20BIT = enum.auto()
        R19BIT = enum.auto()
        R18BIT = enum.auto()
        R17BIT = enum.auto()
        R16BIT = enum.auto()
        R13BIT = enum.auto()
        RES_1 = enum.auto()
        RES_2 = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.LSResolution) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    class LSMeasurementRate(enum.Enum):
        __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensor.LSMeasurementRate"
        R25ms = enum.auto()
        R50ms = enum.auto()
        R100ms = enum.auto()
        R200ms = enum.auto()
        R500ms = enum.auto()
        R1000ms = enum.auto()
        R2000ms_1 = enum.auto()
        R2000ms_2 = enum.auto()
        @overload
        def bitOr(self, him: BroadcomColorSensor.PSMeasurementRate) -> int:
            ...
        @overload
        def bitOr(self, him: int) -> int:
            ...
        def bitOr(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    def initialize(self, parameters: BroadcomColorSensor.Parameters) -> bool:
        """Initialize the sensor using the indicated set of parameters."""
        ...

    def getParameters(self) -> BroadcomColorSensor.Parameters:
        """Returns the parameters which which initialization was last attempted, if any"""
        ...

    def getDeviceID(self) -> int:
        """Returns the flavor of the Broadcom color sensor as reported by the chip itself"""
        ...

    def read8(self, register: BroadcomColorSensor.Register) -> int:
        """Low level: read the byte starting at the indicated register"""
        ...

    def read(self, register: BroadcomColorSensor.Register, cb: int) -> list[int]:
        """Low level: read data starting at the indicated register"""
        ...

    def write8(self, register: BroadcomColorSensor.Register, bVal: int) -> None:
        """Low level: write a byte to the indicated register"""
        ...

    def write(self, register: BroadcomColorSensor.Register, data: list[int]) -> None:
        """Low level: write data starting at the indicated register"""
        ...

    BROADCOM_APDS9151_ADDRESS: I2cAddr
    BROADCOM_APDS9151_ID: int


class BroadcomColorSensorImpl(I2cDeviceSynchDeviceWithParameters[I2cDeviceSynchSimple, BroadcomColorSensor.Parameters], BroadcomColorSensor, I2cAddrConfig, Light):
    """BroadcomColorSensorImpl is used to support the Rev Robotics V3 color sensor"""
    __java__ = "com.qualcomm.hardware.broadcom.BroadcomColorSensorImpl"
    def __init__(self, params: BroadcomColorSensor.Parameters, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def internalInitialize(self, parameters: BroadcomColorSensor.Parameters) -> bool:
        ...

    def dumpState(self) -> None:
        ...

    def enable(self) -> None:
        ...

    def disable(self) -> None:
        ...

    @overload
    def testBits(self, value: int, desired: int) -> bool:
        ...
    @overload
    def testBits(self, value: int, mask: int, desired: int) -> bool:
        ...
    def testBits(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readMainCtrl(self) -> int:
        ...

    def setProximityPulseCount(self, proximityPulseCount: int) -> None:
        ...

    def setHardwareGain(self, gain: BroadcomColorSensor.Gain) -> None:
        ...

    def setPDrive(self, ledDrive: BroadcomColorSensor.LEDCurrent) -> None:
        ...

    def getDeviceID(self) -> int:
        ...

    def setLEDParameters(self, pulseMod: BroadcomColorSensor.LEDPulseModulation, curr: BroadcomColorSensor.LEDCurrent) -> None:
        ...

    def setPSRateAndRes(self, res: BroadcomColorSensor.PSResolution, rate: BroadcomColorSensor.PSMeasurementRate) -> None:
        ...

    def setLSRateAndRes(self, res: BroadcomColorSensor.LSResolution, rate: BroadcomColorSensor.LSMeasurementRate) -> None:
        ...

    def red(self) -> int:
        """In this implementation, the Color methods return 16 bit unsigned values."""
        ...

    def green(self) -> int:
        ...

    def blue(self) -> int:
        ...

    def alpha(self) -> int:
        ...

    def argb(self) -> int:
        ...

    def setGain(self, newGain: float) -> None:
        ...

    def getGain(self) -> float:
        ...

    def getNormalizedColors(self) -> NormalizedRGBA:
        ...

    def enableLed(self, enable: bool) -> None:
        ...

    def isLightOn(self) -> bool:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def setI2cAddress(self, i2cAddr: I2cAddr) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def readUnsignedByte(self, reg: BroadcomColorSensor.Register) -> int:
        ...

    def readUnsignedShort(self, reg: BroadcomColorSensor.Register, byteOrder: Any) -> int:
        ...

    def read8(self, reg: BroadcomColorSensor.Register) -> int:
        ...

    def read(self, reg: BroadcomColorSensor.Register, cb: int) -> list[int]:
        ...

    def write8(self, reg: BroadcomColorSensor.Register, data: int) -> None:
        ...

    def write(self, reg: BroadcomColorSensor.Register, data: list[int]) -> None:
        ...

    def delay(self, ms: int) -> None:
        ...

    TAG: str
    colors: NormalizedRGBA
    red_: int
    green_: int
    blue_: int
    alpha_: int
    softwareGain: float


class HuskyLens(I2cDeviceSynchDevice[I2cDeviceSynch]):
    """Driver for HuskyLens Vision Sensor. HuskyLens provides support for the DFRobot HuskyLens Vision Sensor."""
    __java__ = "com.qualcomm.hardware.dfrobot.HuskyLens"
    class Algorithm(enum.Enum):
        """Algorithms to be used with selectAlgorithm()"""
        __java__ = "com.qualcomm.hardware.dfrobot.HuskyLens.Algorithm"
        FACE_RECOGNITION = enum.auto()
        OBJECT_TRACKING = enum.auto()
        OBJECT_RECOGNITION = enum.auto()
        LINE_TRACKING = enum.auto()
        COLOR_RECOGNITION = enum.auto()
        TAG_RECOGNITION = enum.auto()
        OBJECT_CLASSIFICATION = enum.auto()
        NONE = enum.auto()
        bVal: int

    class Block:
        """A Block is a fundamental unit of recognition for all recognized kinds except Arrows and describes the recognized entity's location center, width, height, top left corner, and id. Units are pixels, except for the id. The device's resolution is 320x240."""
        __java__ = "com.qualcomm.hardware.dfrobot.HuskyLens.Block"
        def __init__(self, buf: list[int]) -> None:
            ...

        def toString(self) -> str:
            ...

        x: int
        y: int
        width: int
        height: int
        top: int
        left: int
        id: int

    class Arrow:
        """An Arrow is returned when the algorithm is set to LINE_TRACKING and represents the direction the line faces. Units are pixels, except for the id. The device's resolution is 320x240."""
        __java__ = "com.qualcomm.hardware.dfrobot.HuskyLens.Arrow"
        def __init__(self, buf: list[int]) -> None:
            ...

        def toString(self) -> str:
            ...

        x_origin: int
        y_origin: int
        x_target: int
        y_target: int
        id: int

    def __init__(self, deviceClient: I2cDeviceSynch) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def doInitialize(self) -> bool:
        ...

    def getDeviceName(self) -> str:
        ...

    def knock(self) -> bool:
        """Proof of life check."""
        ...

    def selectAlgorithm(self, algorithm: HuskyLens.Algorithm) -> None:
        """Select the algorithm that the HuskyLens should use. This should be called upon startup to ensure that the device is returning what you expect it to return."""
        ...

    @overload
    def blocks(self) -> list[HuskyLens.Block]:
        """Returns an array of blocks or the empty array if no blocks are seen."""
        ...
    @overload
    def blocks(self, id: int) -> list[HuskyLens.Block]:
        """Returns an array of blocks with the given id or the empty array if no blocks are seen."""
        ...
    def blocks(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def arrows(self) -> list[HuskyLens.Arrow]:
        """Returns an array of arrows or the empty array if no arrows are seen."""
        ...
    @overload
    def arrows(self, id: int) -> list[HuskyLens.Arrow]:
        """Returns an array of arrows with the given id or the empty array if no arrows are seen."""
        ...
    def arrows(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readInfo(self) -> list[int]:
        ...

    def readBlocksResponse(self) -> list[HuskyLens.Block]:
        ...

    def readArrowsResponse(self) -> list[HuskyLens.Arrow]:
        ...

    def sendCommand(self, cmd: int) -> None:
        ...

    def sendCommandWithData(self, cmd: int, d1: int, d2: int) -> None:
        ...

    DEFAULT_I2C_ADDR: int


class OctoQuad(HardwareDevice):
    __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad"
    class FirmwareVersion:
        """Class to represent an OctoQuad firmware version"""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.FirmwareVersion"
        def __init__(self, maj: int, min: int, eng: int) -> None:
            ...

        def toString(self) -> str:
            ...

        maj: int
        min: int
        eng: int

    class EncoderDirection(enum.Enum):
        """Allows reversing an encoder channel internally on the OctoQuad. This has basically the same effect as negating pos/vel in user code, except for when using the absolute localizer, in which case this must be used to inform the firmware of the tracking wheel directions"""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.EncoderDirection"
        FORWARD = enum.auto()
        REVERSE = enum.auto()

    class ChannelBankConfig(enum.Enum):
        """Switch which mode a channel bank operates in"""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.ChannelBankConfig"
        ALL_QUADRATURE = enum.auto()
        ALL_PULSE_WIDTH = enum.auto()
        BANK1_QUADRATURE_BANK2_PULSE_WIDTH = enum.auto()
        bVal: int

    class EncoderDataBlock:
        """A data block holding all encoder data; this block may be bulk read in one I2C operation. You should check if the CRC is OK before using the data."""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.EncoderDataBlock"
        def isDataValid(self) -> bool:
            """Check whether it is likely that this data is valid by checking if the CRC on the returned is bad. For example, if there is an I2C bus stall or bit flip, you could avoid acting on corrupted data."""
            ...

        def copyTo(self, target: OctoQuad.EncoderDataBlock) -> None:
            ...

        positions: list[int]
        velocities: list[int]
        crcOk: bool

    class CachingMode(enum.Enum):
        """Controls how data is cached to reduce the number of Lynx transactions needed to read the encoder data"""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.CachingMode"
        MANUAL = enum.auto()
        AUTO = enum.auto()

    class ChannelPulseWidthParams:
        """A data block containing minimum and maximum pulse widths to be applied to a channel using #setSingleChannelPulseWidthParams(int,"""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.ChannelPulseWidthParams"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, min_length_us: int, max_length_us: int) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        min_length_us: int
        max_length_us: int

    class LocalizerDataBlock:
        """A data block holding all localizer data needed for navigation; this block may be bulk read in one I2C read operation."""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.LocalizerDataBlock"
        def isDataValid(self) -> bool:
            """Check whether it is likely that this data is valid. The localizer status is read along with the data, and if the status is not RUNNING, then the data invalid. Additionally, if the CRC on the returned is bad, (e.g. if there is an I2C bus stall or bit flip), you could avoid acting on that corrupted data."""
            ...

        localizerStatus: OctoQuad.LocalizerStatus
        crcOk: bool
        heading_rad: float
        posX_mm: int
        posY_mm: int
        velX_mmS: int
        velY_mmS: int
        velHeading_radS: float

    class LocalizerStatus(enum.Enum):
        """Enum representing the status of the absolute localizer algorithm You can poll this to determine when IMU calibration has finished."""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.LocalizerStatus"
        INVALID = enum.auto()
        NOT_INITIALIZED = enum.auto()
        WARMING_UP_IMU = enum.auto()
        CALIBRATING_IMU = enum.auto()
        RUNNING = enum.auto()
        FAULT_NO_IMU = enum.auto()
        code: int

    class LocalizerYawAxis(enum.Enum):
        """The absolute localizer automagically selects the appropriate axis on the IMU to use for yaw, regardless of physical mounting orientation. (However, you must mount in one of the 6 axis-orthogonal orientations). You can poll this status to determine which axis was chosen."""
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.LocalizerYawAxis"
        UNDECIDED = enum.auto()
        X = enum.auto()
        X_INV = enum.auto()
        Y = enum.auto()
        Y_INV = enum.auto()
        Z = enum.auto()
        Z_INV = enum.auto()
        code: int

    class I2cRecoveryMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuad.I2cRecoveryMode"
        NONE = enum.auto()
        MODE_1_PERIPH_RST_ON_FRAME_ERR = enum.auto()
        MODE_2_M1_PLUS_SCL_IDLE_ONESHOT_TGL = enum.auto()
        bVal: int

    def getChipId(self) -> int:
        """Reads the CHIP_ID register of the OctoQuad"""
        ...

    def getFirmwareVersion(self) -> OctoQuad.FirmwareVersion:
        """Get the firmware version running on the OctoQuad"""
        ...

    def getFirmwareVersionString(self) -> str:
        """Get the firmware version running on the OctoQuad"""
        ...

    def setSingleEncoderDirection(self, idx: int, dir: OctoQuad.EncoderDirection) -> None:
        """Set the direction for a single encoder This has basically the same effect as negating pos/vel in user code, except for when using the absolute localizer, in which case this must be used to inform the firmware of the tracking wheel directions. This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...

    def getSingleEncoderDirection(self, idx: int) -> OctoQuad.EncoderDirection:
        """Get the direction for a single encoder"""
        ...

    def setAllEncoderDirections(self, reverse: list[bool]) -> None:
        """Set the direction for all encoders This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()} See #setSingleEncoderDirection(int,"""
        ...

    def setChannelBankConfig(self, config: OctoQuad.ChannelBankConfig) -> None:
        """Configures the OctoQuad's channel banks This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...

    def getChannelBankConfig(self) -> OctoQuad.ChannelBankConfig:
        """Queries the OctoQuad to determine the current channel bank configuration"""
        ...

    @overload
    def readAllEncoderData(self, out: OctoQuad.EncoderDataBlock) -> None:
        """Reads all encoder data from the OctoQuad, writing the data into an existing EncoderDataBlock object. The previous values are destroyed."""
        ...
    @overload
    def readAllEncoderData(self) -> OctoQuad.EncoderDataBlock:
        """Reads all encoder data from the OctoQuad"""
        ...
    def readAllEncoderData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setCachingMode(self, mode: OctoQuad.CachingMode) -> None:
        """Set the data caching mode for the OctoQuad. Applies to xxx_Caching() calls."""
        ...

    def refreshCache(self) -> None:
        """Manually refresh the position and velocity data cache"""
        ...

    def readSinglePosition_Caching(self, idx: int) -> int:
        """Read a single position from the data cache Depending on the channel bank configuration, this may either be quadrature step count, or pulse width. See #setCachingMode(CachingMode for more details about caching."""
        ...

    def readSingleVelocity_Caching(self, idx: int) -> int:
        """Read a single velocity from the data cache NOTE: if using an absolute pulse width encoder, in order to get sane velocity data, you must set the channel min/max pulse width parameter."""
        ...

    def readSingleVelocity(self, idx: int) -> int:
        """Deprecated - delegates to #readSingleVelocity_Caching(int)"""
        ...

    def readSinglePosition(self, idx: int) -> int:
        """Deprecated - delegates to #readSinglePosition_Caching(int)"""
        ...

    def resetSinglePosition(self, idx: int) -> None:
        """Reset a single encoder in the OctoQuad firmware"""
        ...

    def resetAllPositions(self) -> None:
        """Reset all encoder counts in the OctoQuad firmware"""
        ...

    @overload
    def resetMultiplePositions(self, resets: list[bool]) -> None:
        """Reset multiple encoders in the OctoQuad firmware in one command"""
        ...
    @overload
    def resetMultiplePositions(self, *indices: int) -> None:
        """Reset multiple encoders in the OctoQuad firmware in one command"""
        ...
    def resetMultiplePositions(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setSingleVelocitySampleInterval(self, idx: int, intvlms: int) -> None:
        """Set the velocity sample interval for a single encoder This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...

    def getSingleVelocitySampleInterval(self, idx: int) -> int:
        """Read a single velocity sample interval"""
        ...

    def setAllVelocitySampleIntervals(self, intvlms: int) -> None:
        """Set the velocity sample intervals for all encoders This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...

    @overload
    def setSingleChannelPulseWidthParams(self, idx: int, min_length_us: int, max_length_us: int) -> None:
        """Configure the minimum/maximum pulse width reported by an absolute encoder which is connected to a given channel, to allow the ability to provide accurate velocity data. These parameters will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...
    @overload
    def setSingleChannelPulseWidthParams(self, idx: int, params: OctoQuad.ChannelPulseWidthParams) -> None:
        """Configure the minimum/maximum pulse width reported by an absolute encoder which is connected to a given channel, to allow the ability to provide accurate velocity data. These parameters will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...
    def setSingleChannelPulseWidthParams(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getSingleChannelPulseWidthParams(self, idx: int) -> OctoQuad.ChannelPulseWidthParams:
        """Queries the OctoQuad to determine the currently set minimum/maxiumum pulse width for an encoder channel, to allow sane velocity data."""
        ...

    def setSingleChannelPulseWidthTracksWrap(self, idx: int, trackWrap: bool) -> None:
        """Configure whether in PWM mode, a channel will report the raw PWM length in microseconds, or whether it will perform \"wrap tracking\" for use with an absolute encoder to turn the absolute position into a continuous value."""
        ...

    def getSingleChannelPulseWidthTracksWrap(self, idx: int) -> bool:
        """Get whether PWM wrap tracking is enabled for a single channel"""
        ...

    def setAllChannelsPulseWidthTracksWrap(self, trackWrap: list[bool]) -> None:
        """Configure whether in PWM mode, a channel will report the raw PWM length in microseconds, or whether it will perform \"wrap tracking\" for use with an absolute encoder to turn the absolute position into a continuous value"""
        ...

    def setLocalizerPortX(self, port: int) -> None:
        """Set the port index to be used by the absolute localizer routine for measuring X movement"""
        ...

    def setLocalizerPortY(self, port: int) -> None:
        """Set the port index to be used by the absolute localizer routine for measuring Y movement"""
        ...

    def setLocalizerCountsPerMM_X(self, ticksPerMM_x: float) -> None:
        """Set the scalar for converting encoder counts on the X port to millimeters of travel You SHOULD NOT calculate this - this is a real world not a theoretical one - you should measure this by pushing your robot N meters and dividing the counts by (N*1000)"""
        ...

    def setLocalizerCountsPerMM_Y(self, ticksPerMM_y: float) -> None:
        """Set the scalar for converting encoder counts on the Y port to millimeters of travel You SHOULD NOT calculate this - this is a real world not a theoretical one - you should measure this by pushing your robot N meters and dividing the counts by (N*1000)"""
        ...

    def setLocalizerTcpOffsetMM_X(self, tcpOffsetMM_X: float) -> None:
        """The real TCP (Tracking Center Point) of your robot is the point on the robot, where, if the robot rotates about that point, neither the X nor Y tracking wheels will rotate. This point can be determined by drawing imaginary lines parallel to, and through the middle of, your tracking wheels, and finding where those lines intersect."""
        ...

    def setLocalizerTcpOffsetMM_Y(self, tcpOffsetMM_Y: float) -> None:
        """The real TCP (Tracking Center Point) of your robot is the point on the robot, where, if the robot rotates about that point, neither the X nor Y tracking wheels will rotate. This point can be determined by drawing imaginary lines parallel to, and through the middle of, your tracking wheels, and finding where those lines intersect."""
        ...

    def setLocalizerImuHeadingScalar(self, headingScalar: float) -> None:
        """Set a scale factor to apply to the IMU heading to improve accuracy The recommended way to tune this is to set the scalar to 1.0, place the robot against a hard surface, rotate the robot 10 times (3600 degrees) and see how far off the reported heading is from what it should be."""
        ...

    def setLocalizerVelocityIntervalMS(self, ms: int) -> None:
        """Set the period of translational velocity calculation. Longer periods give higher resolution with more latency, shorter periods give lower resolution with less latency."""
        ...

    def setAllLocalizerParameters(self, portX: int, portY: int, ticksPerMM_x: float, ticksPerMM_y: float, tcpOffsetMM_X: float, tcpOffsetMM_Y: float, headingScalar: float, velocityIntervalMs: int) -> None:
        """Set all localizer parameters with one function call"""
        ...

    @overload
    def readLocalizerData(self, out: OctoQuad.LocalizerDataBlock) -> None:
        """Bulk read all localizer data in one operation for maximum efficiency, writing the data into an existing LocalizerDataBlock object. The previous values are destroyed."""
        ...
    @overload
    def readLocalizerData(self) -> OctoQuad.LocalizerDataBlock:
        """Bulk read all localizer data in one operation for maximum efficiency"""
        ...
    def readLocalizerData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readLocalizerDataAndAllEncoderData(self, localizerOut: OctoQuad.LocalizerDataBlock, encoderOut: OctoQuad.EncoderDataBlock) -> None:
        """Bulk read all localizer data and encoder data in one operation for maximum efficiency, writing the data into existing objects. The previous values are destroyed."""
        ...

    def setLocalizerPose(self, posX_mm: int, posY_mm: int, heading_rad: float) -> None:
        """\"Teleport\" the localizer to a new location. This may be useful, for instance, for updating your position based on vision targeting."""
        ...

    def setLocalizerHeading(self, heading_rad: float) -> None:
        """Teleport the localizer heading to a new orientation. This may be useful, for instance, for updating heading based on vision targeting."""
        ...

    def getLocalizerStatus(self) -> OctoQuad.LocalizerStatus:
        """Get the current status of the localizer algorithm"""
        ...

    def getLocalizerHeadingAxisChoice(self) -> OctoQuad.LocalizerYawAxis:
        """Query which IMU axis the localizer decided to use for heading"""
        ...

    def resetLocalizerAndCalibrateIMU(self) -> None:
        """Reset the localizer pose to (0,0,0) and recalibrate the IMU. Poll #getLocalizerStatus() for LocalizerStatus#RUNNING to determine when the reset is complete."""
        ...

    def setI2cRecoveryMode(self, mode: OctoQuad.I2cRecoveryMode) -> None:
        """Configures the OctoQuad to use the specified I2C recovery mode. This parameter will NOT be retained across power cycles, unless you call #saveParametersToFlash() ()}"""
        ...

    def getI2cRecoveryMode(self) -> OctoQuad.I2cRecoveryMode:
        """Queries the OctoQuad to determine the currently configured I2C recovery mode"""
        ...

    def saveParametersToFlash(self) -> None:
        """Stores the current state of parameters to flash, to be applied at next boot"""
        ...

    def resetEverything(self) -> None:
        """Run the firmware's internal reset routine"""
        ...

    OCTOQUAD_CHIP_ID: int
    SUPPORTED_FW_VERSION_MAJ: int
    ENCODER_FIRST: int
    ENCODER_LAST: int
    NUM_ENCODERS: int
    MIN_VELOCITY_MEASUREMENT_INTERVAL_MS: int
    MAX_VELOCITY_MEASUREMENT_INTERVAL_MS: int
    MIN_PULSE_WIDTH_US: int
    MAX_PULSE_WIDTH_US: int


class OctoQuadImpl(I2cDeviceSynchDevice[I2cDeviceSynchSimple], OctoQuad):
    __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuadImpl"
    class RegisterType(enum.Enum):
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuadImpl.RegisterType"
        uint8_t = enum.auto()
        int32_t = enum.auto()
        int16_t = enum.auto()
        uint16_t = enum.auto()
        float32 = enum.auto()
        length: int

    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.digitalchickenlabs.OctoQuadImpl.Register"
        CHIP_ID = enum.auto()
        FIRMWARE_VERSION_MAJOR = enum.auto()
        FIRMWARE_VERSION_MINOR = enum.auto()
        FIRMWARE_VERSION_ENGINEERING = enum.auto()
        COMMAND = enum.auto()
        COMMAND_DAT_0 = enum.auto()
        COMMAND_DAT_1 = enum.auto()
        COMMAND_DAT_2 = enum.auto()
        COMMAND_DAT_3 = enum.auto()
        COMMAND_DAT_4 = enum.auto()
        COMMAND_DAT_5 = enum.auto()
        COMMAND_DAT_6 = enum.auto()
        LOCALIZER_YAW_AXIS = enum.auto()
        LOCALIZER_STATUS = enum.auto()
        LOCALIZER_VX = enum.auto()
        LOCALIZER_VY = enum.auto()
        LOCALIZER_VH = enum.auto()
        LOCALIZER_X = enum.auto()
        LOCALIZER_Y = enum.auto()
        LOCALIZER_H = enum.auto()
        LOCALIZER_CRC16 = enum.auto()
        ENCODER_0_POSITION = enum.auto()
        ENCODER_1_POSITION = enum.auto()
        ENCODER_2_POSITION = enum.auto()
        ENCODER_3_POSITION = enum.auto()
        ENCODER_4_POSITION = enum.auto()
        ENCODER_5_POSITION = enum.auto()
        ENCODER_6_POSITION = enum.auto()
        ENCODER_7_POSITION = enum.auto()
        ENCODER_0_VELOCITY = enum.auto()
        ENCODER_1_VELOCITY = enum.auto()
        ENCODER_2_VELOCITY = enum.auto()
        ENCODER_3_VELOCITY = enum.auto()
        ENCODER_4_VELOCITY = enum.auto()
        ENCODER_5_VELOCITY = enum.auto()
        ENCODER_6_VELOCITY = enum.auto()
        ENCODER_7_VELOCITY = enum.auto()
        ENCODER_DATA_CRC16 = enum.auto()
        addr: int
        length: int

    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getChipId(self) -> int:
        ...

    def getFirmwareVersion(self) -> OctoQuad.FirmwareVersion:
        ...

    def getFirmwareVersionString(self) -> str:
        ...

    def readSinglePosition(self, idx: int) -> int:
        ...

    def resetSinglePosition(self, idx: int) -> None:
        ...

    def resetAllPositions(self) -> None:
        ...

    @overload
    def resetMultiplePositions(self, resets: list[bool]) -> None:
        ...
    @overload
    def resetMultiplePositions(self, *indices: int) -> None:
        ...
    def resetMultiplePositions(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setSingleEncoderDirection(self, idx: int, direction: OctoQuad.EncoderDirection) -> None:
        ...

    def getSingleEncoderDirection(self, idx: int) -> OctoQuad.EncoderDirection:
        ...

    def setAllEncoderDirections(self, reverse: list[bool]) -> None:
        ...

    def readSingleVelocity(self, idx: int) -> int:
        ...

    @overload
    def readAllEncoderData(self, out: OctoQuad.EncoderDataBlock) -> None:
        ...
    @overload
    def readAllEncoderData(self) -> OctoQuad.EncoderDataBlock:
        ...
    def readAllEncoderData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setSingleVelocitySampleInterval(self, idx: int, intvlms: int) -> None:
        ...

    def getSingleVelocitySampleInterval(self, idx: int) -> int:
        ...

    def setAllVelocitySampleIntervals(self, intvlms: int) -> None:
        ...

    @overload
    def setSingleChannelPulseWidthParams(self, idx: int, min: int, max: int) -> None:
        ...
    @overload
    def setSingleChannelPulseWidthParams(self, idx: int, params: OctoQuad.ChannelPulseWidthParams) -> None:
        ...
    def setSingleChannelPulseWidthParams(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getSingleChannelPulseWidthParams(self, idx: int) -> OctoQuad.ChannelPulseWidthParams:
        ...

    def setSingleChannelPulseWidthTracksWrap(self, idx: int, trackWrap: bool) -> None:
        ...

    def getSingleChannelPulseWidthTracksWrap(self, idx: int) -> bool:
        ...

    def setAllChannelsPulseWidthTracksWrap(self, trackWrap: list[bool]) -> None:
        ...

    def setLocalizerCountsPerMM_X(self, ticksPerMM_x: float) -> None:
        ...

    def setLocalizerCountsPerMM_Y(self, ticksPerMM_y: float) -> None:
        ...

    def setLocalizerTcpOffsetMM_X(self, tcpOffsetMM_X: float) -> None:
        ...

    def setLocalizerTcpOffsetMM_Y(self, tcpOffsetMM_Y: float) -> None:
        ...

    def setLocalizerImuHeadingScalar(self, headingScalar: float) -> None:
        ...

    def setLocalizerPortX(self, port: int) -> None:
        ...

    def setLocalizerPortY(self, port: int) -> None:
        ...

    def setLocalizerVelocityIntervalMS(self, ms: int) -> None:
        ...

    def getLocalizerStatus(self) -> OctoQuad.LocalizerStatus:
        ...

    def getLocalizerHeadingAxisChoice(self) -> OctoQuad.LocalizerYawAxis:
        ...

    def resetLocalizerAndCalibrateIMU(self) -> None:
        ...

    @overload
    def readLocalizerData(self, out: OctoQuad.LocalizerDataBlock) -> None:
        ...
    @overload
    def readLocalizerData(self) -> OctoQuad.LocalizerDataBlock:
        ...
    def readLocalizerData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readLocalizerDataAndAllEncoderData(self, localizerOut: OctoQuad.LocalizerDataBlock, encoderOut: OctoQuad.EncoderDataBlock) -> None:
        ...

    def setAllLocalizerParameters(self, portX: int, portY: int, ticksPerMM_x: float, ticksPerMM_y: float, tcpOffsetMM_X: float, tcpOffsetMM_Y: float, headingScalar: float, velocityIntervalMs: int) -> None:
        ...

    def setLocalizerPose(self, posX_mm: int, posY_mm: int, heading_rad: float) -> None:
        ...

    def setLocalizerHeading(self, headingRad: float) -> None:
        ...

    def resetEverything(self) -> None:
        ...

    def setChannelBankConfig(self, config: OctoQuad.ChannelBankConfig) -> None:
        ...

    def getChannelBankConfig(self) -> OctoQuad.ChannelBankConfig:
        ...

    def setI2cRecoveryMode(self, mode: OctoQuad.I2cRecoveryMode) -> None:
        ...

    def getI2cRecoveryMode(self) -> OctoQuad.I2cRecoveryMode:
        ...

    def saveParametersToFlash(self) -> None:
        ...

    def setCachingMode(self, mode: OctoQuad.CachingMode) -> None:
        ...

    def refreshCache(self) -> None:
        ...

    def readSinglePosition_Caching(self, idx: int) -> int:
        ...

    def readSingleVelocity_Caching(self, idx: int) -> int:
        ...

    cachingMode: OctoQuad.CachingMode
    cachedData: OctoQuad.EncoderDataBlock
    posHasBeenRead: list[bool]
    velHasBeenRead: list[bool]


class GoBildaPinpointDriver(I2cDeviceSynchDevice[I2cDeviceSynchSimple]):
    __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver"
    class ErrorDetectionType(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.ErrorDetectionType"
        NONE = enum.auto()
        CRC = enum.auto()
        LOCAL_TEST = enum.auto()

    class RegisterType(enum.Enum):
        """Captures the length of each type of register used on the device. Aside from BULK_READ all registers are 4 bytes long"""
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.RegisterType"
        INT32 = enum.auto()
        FLOAT = enum.auto()
        GENERIC = enum.auto()
        BULK = enum.auto()

    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.Register"
        DEVICE_ID = enum.auto()
        DEVICE_VERSION = enum.auto()
        DEVICE_STATUS = enum.auto()
        DEVICE_CONTROL = enum.auto()
        LOOP_TIME = enum.auto()
        X_ENCODER_VALUE = enum.auto()
        Y_ENCODER_VALUE = enum.auto()
        X_POSITION = enum.auto()
        Y_POSITION = enum.auto()
        H_ORIENTATION = enum.auto()
        X_VELOCITY = enum.auto()
        Y_VELOCITY = enum.auto()
        H_VELOCITY = enum.auto()
        MM_PER_TICK = enum.auto()
        X_POD_OFFSET = enum.auto()
        Y_POD_OFFSET = enum.auto()
        YAW_SCALAR = enum.auto()
        BULK_READ = enum.auto()
        QUATERNION_W = enum.auto()
        QUATERNION_X = enum.auto()
        QUATERNION_Y = enum.auto()
        QUATERNION_Z = enum.auto()
        PITCH = enum.auto()
        ROLL = enum.auto()
        SET_BULK_READ = enum.auto()

    class DeviceStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.DeviceStatus"
        NOT_READY = enum.auto()
        READY = enum.auto()
        CALIBRATING = enum.auto()
        FAULT_X_POD_NOT_DETECTED = enum.auto()
        FAULT_Y_POD_NOT_DETECTED = enum.auto()
        FAULT_NO_PODS_DETECTED = enum.auto()
        FAULT_IMU_RUNAWAY = enum.auto()
        FAULT_BAD_READ = enum.auto()

    class EncoderDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.EncoderDirection"
        FORWARD = enum.auto()
        REVERSED = enum.auto()

    class GoBildaOdometryPods(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.GoBildaOdometryPods"
        goBILDA_SWINGARM_POD = enum.auto()
        goBILDA_4_BAR_POD = enum.auto()

    class ReadData(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.ReadData"
        ONLY_UPDATE_HEADING = enum.auto()

    class DeviceControl(enum.Enum):
        __java__ = "com.qualcomm.hardware.gobilda.GoBildaPinpointDriver.DeviceControl"
        RECALIBRATE_IMU = enum.auto()
        RESET_POS_AND_IMU = enum.auto()
        SET_X_ENCODER_REVERSED = enum.auto()
        SET_X_ENCODER_FORWARD = enum.auto()
        SET_Y_ENCODER_REVERSED = enum.auto()
        SET_Y_ENCODER_FORWARD = enum.auto()
        value: int

    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def doInitialize(self) -> bool:
        ...

    def getDeviceName(self) -> str:
        ...

    @overload
    def update(self) -> None:
        """Call this once per loop to read new data from the Odometry Computer. Data will only update once this is called."""
        ...
    @overload
    def update(self, data: GoBildaPinpointDriver.ReadData) -> None:
        """Call this once per loop to read new data from the Odometry Computer. This is an override of the update() function which allows a narrower range of data to be read from the device for faster read times. Currently ONLY_UPDATE_HEADING is supported."""
        ...
    def update(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setBulkReadScope(self, *registers: GoBildaPinpointDriver.Register) -> None:
        """Only supported on V3 firmware and above. This configures the registers that are read in bulk when .update() is called. Use this to minimize read times based on your unique application."""
        ...

    def setErrorDetectionType(self, e: GoBildaPinpointDriver.ErrorDetectionType) -> None:
        """The kind of error correction used on the I²C communication from the device. NONE: This does not check the data, and passes it directly to the user. CRC: This uses CRC8 error detection to catch incorrect reads. - Only supported by devices with V3 firmware or newer. LOCAL_TEST: \"Controller only\" validation that ensures that the data is !NAN, is not all zeros, and is a reasonable number. This is faster than CRC but may not catch every erroneous read."""
        ...

    def setOffsets(self, xOffset: float, yOffset: float, distanceUnit: DistanceUnit) -> None:
        """Sets the odometry pod positions relative to the point that the odometry computer tracks around. The most common tracking position is the center of the robot. The X pod offset refers to how far sideways from the tracking point the X (forward) odometry pod is. Left of the center is a positive number, right of center is a negative number. the Y pod offset refers to how far forwards from the tracking point the Y (strafe) odometry pod is. forward of center is a positive number, backwards is a negative number."""
        ...

    def recalibrateIMU(self) -> None:
        """Recalibrates the Odometry Computer's internal IMU. Robot MUST be stationary Device takes a large number of samples, and uses those as the gyroscope zero-offset. This takes approximately 0.25 seconds."""
        ...

    def resetPosAndIMU(self) -> None:
        """Resets the current position to 0,0,0 and recalibrates the Odometry Computer's internal IMU. Robot MUST be stationary Device takes a large number of samples, and uses those as the gyroscope zero-offset. This takes approximately 0.25 seconds."""
        ...

    def setEncoderDirections(self, xEncoder: GoBildaPinpointDriver.EncoderDirection, yEncoder: GoBildaPinpointDriver.EncoderDirection) -> None:
        """Can reverse the direction of each encoder."""
        ...

    @overload
    def setEncoderResolution(self, pods: GoBildaPinpointDriver.GoBildaOdometryPods) -> None:
        """This allows you to set the encoder resolution by the type of GoBilda pod you are using. If you aren't using a GoBilda pod, use setEncoderResolution(double) instead."""
        ...
    @overload
    def setEncoderResolution(self, ticksPerUnit: float, distanceUnit: DistanceUnit) -> None:
        """Sets the encoder resolution in ticks per mm of the odometry pods. You can find this number by dividing the counts-per-revolution of your encoder by the circumference of the wheel."""
        ...
    def setEncoderResolution(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setYawScalar(self, yawScalar: float) -> None:
        """Tuning this value should be unnecessary. The goBILDA Odometry Computer has a per-device tuned yaw offset already applied when you receive it. This is a scalar that is applied to the gyro's yaw value. Increasing it will mean it will report more than one degree for every degree the sensor fusion algorithm measures. You can tune this variable by rotating the robot a large amount (10 full turns is a good starting place) and comparing the amount that the robot rotated to the amount measured. Rotating the robot exactly 10 times should measure 3600°. If it measures more or less, divide moved amount by the measured amount and apply that value to the Yaw Offset. If you find that to get an accurate heading number you need to apply a scalar of more than 1.05, or less than 0.95, your device may be bad. Please reach out to tech@gobilda.com"""
        ...

    def setPosition(self, pos: Pose2D) -> None:
        """Send a position that the Pinpoint should use to track your robot relative to. You can use this to update the estimated position of your robot with new external sensor data, or to run a robot in field coordinates. This overrides the current position. Using this feature to track your robot's position in field coordinates: When you start your code, send a Pose2D that describes the starting position on the field of your robot. Say you're on the red alliance, your robot is against the wall and closer to the audience side, and the front of your robot is pointing towards the center of the field. You can send a setPosition with something like -600mm x, -1200mm Y, and 90 degrees. The pinpoint would then always keep track of how far away from the center of the field you are. Using this feature to update your position with additional sensors: Some robots have a secondary way to locate their robot on the field. This is commonly Apriltag localization in FTC, but it can also be something like a distance sensor. Often these external sensors are absolute (meaning they measure something about the field) so their data is very accurate. But they can be slower to read, or you may need to be in a very specific position on the field to use them. In that case, spend most of your time relying on the Pinpoint to determine your location. Then when you pull a new position from your secondary sensor, send a setPosition command with the new position. The Pinpoint will then track your movement relative to that new, more accurate position."""
        ...

    def setPosX(self, posX: float, distanceUnit: DistanceUnit) -> None:
        """Send a X position that the Pinpoint should use to track your robot relative to. You can use this to update the estimated position of your robot with new external sensor data, or to run a robot in field coordinates."""
        ...

    def setPosY(self, posY: float, distanceUnit: DistanceUnit) -> None:
        """Send a Y position that the Pinpoint should use to track your robot relative to. You can use this to update the estimated position of your robot with new external sensor data, or to run a robot in field coordinates."""
        ...

    def setHeading(self, heading: float, angleUnit: AngleUnit) -> None:
        """Send a heading that the Pinpoint should use to track your robot relative to. You can use this to update the estimated position of your robot with new external sensor data, or to run a robot in field coordinates."""
        ...

    def getDeviceID(self) -> int:
        """Checks the deviceID of the Odometry Computer. Should return 1."""
        ...

    def getDeviceVersion(self) -> int:
        ...

    def getYawScalar(self) -> float:
        ...

    def getDeviceStatus(self) -> GoBildaPinpointDriver.DeviceStatus:
        """Device Status stores any faults the Odometry Computer may be experiencing. These faults include:"""
        ...

    def getLoopTime(self) -> int:
        """Checks the Odometry Computer's most recent loop time. If values less than 500, or more than 1100 are commonly seen here, there may be something wrong with your device. Please reach out to tech@gobilda.com"""
        ...

    def getFrequency(self) -> float:
        """Checks the Odometry Computer's most recent loop frequency. If values less than 900, or more than 2000 are commonly seen here, there may be something wrong with your device. Please reach out to tech@gobilda.com"""
        ...

    def getEncoderX(self) -> int:
        ...

    def getEncoderY(self) -> int:
        ...

    def getPosX(self, distanceUnit: DistanceUnit) -> float:
        ...

    def getPosY(self, distanceUnit: DistanceUnit) -> float:
        ...

    @overload
    def getHeading(self, angleUnit: AngleUnit) -> float:
        ...
    @overload
    def getHeading(self, unnormalizedAngleUnit: UnnormalizedAngleUnit) -> float:
        ...
    def getHeading(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getVelX(self, distanceUnit: DistanceUnit) -> float:
        ...

    def getVelY(self, distanceUnit: DistanceUnit) -> float:
        ...

    def getHeadingVelocity(self, unnormalizedAngleUnit: UnnormalizedAngleUnit) -> float:
        ...

    def getXOffset(self, distanceUnit: DistanceUnit) -> float:
        """This uses its own I2C read, avoid calling this every loop."""
        ...

    def getYOffset(self, distanceUnit: DistanceUnit) -> float:
        """This uses its own I2C read, avoid calling this every loop."""
        ...

    def getPosition(self) -> Pose2D:
        ...

    def getQuaternion(self) -> Quaternion:
        ...

    def getPitch(self, angleUnit: AngleUnit) -> float:
        ...

    def getRoll(self, angleUnit: AngleUnit) -> float:
        ...


class NavxMicroNavigationSensor(I2cDeviceSynchDeviceWithParameters, IntegratingGyroscope, I2cAddrConfig):
    """NavxMicroNavigationSensor provides support for the Kauai Labs navX-Micro Robotics Navigation Sensor. This sensor contains an Invensense MPU-9250 integrated circuit."""
    __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor"
    class Parameters:
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.Parameters"
        def realizedUpdateRate(self) -> int:
            """Returns the update rate actually used with these parameters. The only update rates that can actually be realized are those evenly divisible by the internal sample clock, which is 200Hz. Thus, the actual rate may be higher than the requested rate. For example, a request of 58Hz will result in 200 / (200 / 58) = 200/3 == 66Hz."""
            ...

        def clone(self) -> NavxMicroNavigationSensor.Parameters:
            ...

        updateRate: int
        """The desired update rate for the sensor, in Hz"""

    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.Register"
        FIRST = enum.auto()
        WHOAMI = enum.auto()
        HW_REV = enum.auto()
        FW_VER_MAJOR = enum.auto()
        FW_VER_MINOR = enum.auto()
        UPDATE_RATE_HZ = enum.auto()
        ACCEL_FSR_G = enum.auto()
        GYRO_FSR_DPS_L = enum.auto()
        GYRO_FSR_DPS_H = enum.auto()
        OP_STATUS = enum.auto()
        CAL_STATUS = enum.auto()
        SELFTEST_STATUS = enum.auto()
        CAPABILITY_FLAGS_L = enum.auto()
        CAPABILITY_FLAGS_H = enum.auto()
        SENSOR_STATUS_L = enum.auto()
        SENSOR_STATUS_H = enum.auto()
        TIMESTAMP_L_L = enum.auto()
        TIMESTAMP_L_H = enum.auto()
        TIMESTAMP_H_L = enum.auto()
        TIMESTAMP_H_H = enum.auto()
        YAW_L = enum.auto()
        YAW_H = enum.auto()
        ROLL_L = enum.auto()
        ROLL_H = enum.auto()
        PITCH_L = enum.auto()
        PITCH_H = enum.auto()
        HEADING_L = enum.auto()
        HEADING_H = enum.auto()
        FUSED_HEADING_L = enum.auto()
        FUSED_HEADING_H = enum.auto()
        ALTITUDE_I_L = enum.auto()
        ALTITUDE_I_H = enum.auto()
        ALTITUDE_D_L = enum.auto()
        ALTITUDE_D_H = enum.auto()
        LINEAR_ACC_X_L = enum.auto()
        LINEAR_ACC_X_H = enum.auto()
        LINEAR_ACC_Y_L = enum.auto()
        LINEAR_ACC_Y_H = enum.auto()
        LINEAR_ACC_Z_L = enum.auto()
        LINEAR_ACC_Z_H = enum.auto()
        QUAT_W_L = enum.auto()
        QUAT_W_H = enum.auto()
        QUAT_X_L = enum.auto()
        QUAT_X_H = enum.auto()
        QUAT_Y_L = enum.auto()
        QUAT_Y_H = enum.auto()
        QUAT_Z_L = enum.auto()
        QUAT_Z_H = enum.auto()
        MPU_TEMP_C_L = enum.auto()
        MPU_TEMP_C_H = enum.auto()
        GYRO_X_L = enum.auto()
        GYRO_X_H = enum.auto()
        GYRO_Y_L = enum.auto()
        GYRO_Y_H = enum.auto()
        GYRO_Z_L = enum.auto()
        GYRO_Z_H = enum.auto()
        ACC_X_L = enum.auto()
        ACC_X_H = enum.auto()
        ACC_Y_L = enum.auto()
        ACC_Y_H = enum.auto()
        ACC_Z_L = enum.auto()
        ACC_Z_H = enum.auto()
        MAG_X_L = enum.auto()
        MAG_X_H = enum.auto()
        MAG_Y_L = enum.auto()
        MAG_Y_H = enum.auto()
        MAG_Z_L = enum.auto()
        MAG_Z_H = enum.auto()
        PRESSURE_IL = enum.auto()
        PRESSURE_IH = enum.auto()
        PRESSURE_DL = enum.auto()
        PRESSURE_DH = enum.auto()
        PRESSURE_TEMP_L = enum.auto()
        PRESSURE_TEMP_H = enum.auto()
        YAW_OFFSET_L = enum.auto()
        YAW_OFFSET_H = enum.auto()
        QUAT_OFFSET_W_L = enum.auto()
        QUAT_OFFSET_W_H = enum.auto()
        QUAT_OFFSET_X_L = enum.auto()
        QUAT_OFFSET_X_H = enum.auto()
        QUAT_OFFSET_Y_L = enum.auto()
        QUAT_OFFSET_Y_H = enum.auto()
        QUAT_OFFSET_Z_L = enum.auto()
        QUAT_OFFSET_Z_H = enum.auto()
        INTEGRATION_CTL = enum.auto()
        PAD_UNUSED = enum.auto()
        VEL_X_I_L = enum.auto()
        VEL_X_I_H = enum.auto()
        VEL_X_D_L = enum.auto()
        VEL_X_D_H = enum.auto()
        VEL_Y_I_L = enum.auto()
        VEL_Y_I_H = enum.auto()
        VEL_Y_D_L = enum.auto()
        VEL_Y_D_H = enum.auto()
        VEL_Z_I_L = enum.auto()
        VEL_Z_I_H = enum.auto()
        VEL_Z_D_L = enum.auto()
        VEL_Z_D_H = enum.auto()
        DISP_X_I_L = enum.auto()
        DISP_X_I_H = enum.auto()
        DISP_X_D_L = enum.auto()
        DISP_X_D_H = enum.auto()
        DISP_Y_I_L = enum.auto()
        DISP_Y_I_H = enum.auto()
        DISP_Y_D_L = enum.auto()
        DISP_Y_D_H = enum.auto()
        DISP_Z_I_L = enum.auto()
        DISP_Z_I_H = enum.auto()
        DISP_Z_D_L = enum.auto()
        DISP_Z_D_H = enum.auto()
        LAST = enum.auto()
        UNKNOWN = enum.auto()
        @staticmethod
        def fromByte(bVal: int) -> NavxMicroNavigationSensor.Register:
            ...

        bVal: int

    class OpStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.OpStatus"
        INITIALIZING = enum.auto()
        SELFTEST_IN_PROGRESS = enum.auto()
        ERROR = enum.auto()
        IMU_AUTOCAL_IN_PROGRESS = enum.auto()
        NORMAL = enum.auto()
        bVal: int

    class SensorStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.SensorStatus"
        MOVING = enum.auto()
        YAW_STABLE = enum.auto()
        MAG_DISTURBANCE = enum.auto()
        ALTITUDE_VALID = enum.auto()
        SEALEVEL_PRESS_SET = enum.auto()
        FUSED_HEADING_VALID = enum.auto()
        bVal: int

    class CalibrationStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.CalibrationStatus"
        IMU_CAL_INPROGRESS = enum.auto()
        IMU_CAL_ACCUMULATE = enum.auto()
        IMU_CAL_COMPLETE = enum.auto()
        IMU_CAL_MASK = enum.auto()
        MAG_CAL_COMPLETE = enum.auto()
        BARO_CAL_COMPLETE = enum.auto()
        bVal: int

    class SelfTestStatus(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.SelfTestStatus"
        COMPLETE = enum.auto()
        RESULT_GYRO_PASSED = enum.auto()
        RESULT_ACCEL_PASSED = enum.auto()
        RESULT_MAG_PASSED = enum.auto()
        RESULT_BARO_PASSED = enum.auto()
        bVal: int

    class IntegrationControl(enum.Enum):
        __java__ = "com.qualcomm.hardware.kauailabs.NavxMicroNavigationSensor.IntegrationControl"
        RESET_VEL_X = enum.auto()
        RESET_VEL_Y = enum.auto()
        RESET_VEL_Z = enum.auto()
        RESET_DISP_X = enum.auto()
        RESET_DISP_Y = enum.auto()
        RESET_DISP_Z = enum.auto()
        RESET_YAW = enum.auto()
        RESET_ALL = enum.auto()
        @overload
        def bitor(self, integrationControl: NavxMicroNavigationSensor.IntegrationControl) -> int:
            ...
        @overload
        def bitor(self, bVal: int) -> int:
            ...
        def bitor(self, *args: Any, **kwargs: Any) -> Any:
            ...

        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    @staticmethod
    def newWindow(regFirst: NavxMicroNavigationSensor.Register, regMax: NavxMicroNavigationSensor.Register) -> I2cDeviceSynch.ReadWindow:
        ...

    def setReadWindow(self) -> None:
        ...

    def internalInitialize(self, parameters: NavxMicroNavigationSensor.Parameters) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getFirmwareVersion(self) -> RobotUsbDevice.FirmwareVersion:
        ...

    def ensureReadWindow(self, needed: I2cDeviceSynch.ReadWindow) -> None:
        ...

    def readTimeStamped(self, reg: NavxMicroNavigationSensor.Register, creg: int) -> TimestampedData:
        ...

    def read8(self, reg: NavxMicroNavigationSensor.Register) -> int:
        ...

    def readShort(self, reg: NavxMicroNavigationSensor.Register) -> int:
        ...

    def readSignedHundredthsFloat(self, reg: NavxMicroNavigationSensor.Register) -> float:
        ...

    def shortToSignedHundredths(self, value: int) -> float:
        ...

    def write8(self, reg: NavxMicroNavigationSensor.Register, value: int) -> None:
        ...

    def writeShort(self, reg: NavxMicroNavigationSensor.Register, value: int) -> None:
        ...

    def isCalibrating(self) -> bool:
        """Returns true if the sensor is currently performing automatic gyro/accelerometer calibration. Automatic calibration occurs when the sensor is initially powered on, during which time the sensor should be held still, with the Z-axis pointing up (perpendicular to the earth). NOTE: During this automatic calibration, the angular orientation data may not be accurate."""
        ...

    def getAngularVelocityAxes(self) -> set[Axis]:
        ...

    def getAngularOrientationAxes(self) -> set[Axis]:
        ...

    def getAngularOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def getAngularVelocity(self, unit: AngleUnit) -> AngularVelocity:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    NAVX_WRITE_COMMAND_BIT: int
    readMode: I2cDeviceSynch.ReadMode
    lowerWindow: I2cDeviceSynch.ReadWindow
    upperWindow: I2cDeviceSynch.ReadWindow
    gyroScaleFactor: float
    ADDRESS_I2C_DEFAULT: I2cAddr


class LLFieldMap:
    """Represents a field map containing fiducial markers / AprilTags."""
    __java__ = "com.qualcomm.hardware.limelightvision.LLFieldMap"
    class Fiducial:
        """Represents a fiducial marker / AprilTag in the field map."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLFieldMap.Fiducial"
        @overload
        def __init__(self) -> None:
            """Constructs a Fiducial with default values."""
            ...
        @overload
        def __init__(self, id: int, size: float, family: str, transform: list[float], isUnique: bool) -> None:
            """Constructs a Fiducial with specified values."""
            ...
        @overload
        def __init__(self, json: Any) -> None:
            """Constructs a Fiducial from JSON data. Returns a default Fidcial if JSON is null or malformed"""
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def getId(self) -> int:
            """Gets the ID / index of the fiducial."""
            ...

        def getSize(self) -> float:
            """Gets the size of the fiducial in millimeters"""
            ...

        def getFamily(self) -> str:
            """Gets the family of the fiducial. eg \"apriltag3_36h11_classic\""""
            ...

        def getTransform(self) -> list[float]:
            """Gets the 4x4 transforms matrix of the fiducial."""
            ...

        def isUnique(self) -> bool:
            """Checks if the fiducial is marked as unique."""
            ...

        def toJson(self) -> Any:
            """Converts the Fiducial to a JSONObject."""
            ...

    @overload
    def __init__(self) -> None:
        """Constructs an empty LLFieldMap."""
        ...
    @overload
    def __init__(self, fiducials: list[LLFieldMap.Fiducial], type: str) -> None:
        """Constructs an LLFieldMap with specified fiducials and type."""
        ...
    @overload
    def __init__(self, json: Any) -> None:
        """Constructs an LLFieldMap from JSON data. Returns an empty map if json is null or malformed"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getFiducials(self) -> list[LLFieldMap.Fiducial]:
        """Gets the list of fiducials in the field map."""
        ...

    def getType(self) -> str:
        """Gets the type of the field map. (eg \"ftc\" or \"frc\")"""
        ...

    def getNumberOfTags(self) -> int:
        """Gets the number of tags (fiducials) in the field map."""
        ...

    def isValid(self) -> bool:
        """Get validity of map. Maps are valid if they have more than zero tags and have a specified type"""
        ...

    def toJson(self) -> Any:
        """Converts the LLFieldMap to a JSONObject."""
        ...


class LLResult:
    """Represents the result of a Limelight Pipeline. This class parses JSON data from a Limelight in the constructor and provides easy access to the results data."""
    __java__ = "com.qualcomm.hardware.limelightvision.LLResult"
    def __init__(self, json: Any) -> None:
        """Constructs an LLResult object from a JSONObject."""
        ...

    def setControlHubTimeStamp(self, timestamp: int) -> None:
        """Sets the timestamp from the control hub in milliseconds."""
        ...

    def getControlHubTimeStamp(self) -> int:
        """Gets the control hub timestamp in milliseconds."""
        ...

    def getControlHubTimeStampNanos(self) -> int:
        """Gets the control hub timestamp in nanoseconds."""
        ...

    def getStaleness(self) -> int:
        """Calculates the staleness of the data."""
        ...

    def getBarcodeResults(self) -> list[LLResultTypes.BarcodeResult]:
        """Gets the list of barcode results."""
        ...

    def getClassifierResults(self) -> list[LLResultTypes.ClassifierResult]:
        """Gets the list of classifier results."""
        ...

    def getDetectorResults(self) -> list[LLResultTypes.DetectorResult]:
        """Gets the list of detector results."""
        ...

    def getFiducialResults(self) -> list[LLResultTypes.FiducialResult]:
        """Gets the list of fiducial/apriltag results."""
        ...

    def getColorResults(self) -> list[LLResultTypes.ColorResult]:
        """Gets the list of color results."""
        ...

    def getFocusMetric(self) -> float:
        """Gets the focus metric of the image. This is only valid if the focus pipeline is enabled"""
        ...

    def getBotpose(self) -> Pose3D:
        """Gets the 3D botpose."""
        ...

    def getBotpose_MT2(self) -> Pose3D:
        """Gets the 3D botpose using MegaTag2. You must set the orientation of the robot with your imu for this to work."""
        ...

    def getStddevMt1(self) -> list[float]:
        """Gets the standard deviation metrics for MegaTag1 (x,y,z,roll,pitch,yaw)"""
        ...

    def getStddevMt2(self) -> list[float]:
        """Gets the standard deviation metrics for MegaTag2 (x,y,z,roll,pitch,yaw)"""
        ...

    def getBotposeTagCount(self) -> int:
        """Gets the number of tags used in the botpose calculation."""
        ...

    def getBotposeSpan(self) -> float:
        """Gets the span of tags used in the botpose calculation in meters."""
        ...

    def getBotposeAvgDist(self) -> float:
        """Gets the average distance of tags used in the botpose calculation in meters."""
        ...

    def getBotposeAvgArea(self) -> float:
        """Gets the average area of tags used in the botpose calculation."""
        ...

    def getPythonOutput(self) -> list[float]:
        """Gets the user-specified python snapscript output data"""
        ...

    def getCaptureLatency(self) -> float:
        """Gets the current capture latency in milliseconds"""
        ...

    def getPipelineType(self) -> str:
        """Gets the type of the current pipeline."""
        ...

    def getTx(self) -> float:
        """Gets the current tx in degrees from the crosshair"""
        ...

    def getTy(self) -> float:
        """Gets the current ty in degrees from the crosshair"""
        ...

    def getTxNC(self) -> float:
        """Gets the current tx in degrees from the principal pixel instead of the crosshair"""
        ...

    def getTyNC(self) -> float:
        """Gets the current ty in degrees from the principal pixel instead of the crosshair"""
        ...

    def getTa(self) -> float:
        """Gets the area of the target as a percentage of the image area"""
        ...

    def getPipelineIndex(self) -> int:
        """Gets the index of the currently active pipeline"""
        ...

    def getTargetingLatency(self) -> float:
        """Gets the targeting/pipeline latency in milliseconds."""
        ...

    def getTimestamp(self) -> float:
        """Gets the Limelight-local monotonic timestamp of the result."""
        ...

    def isValid(self) -> bool:
        """Gets the validity of the result."""
        ...

    def getParseLatency(self) -> float:
        """Gets the json parse latency."""
        ...

    @staticmethod
    def createPose3DRobot(pose: list[float]) -> Pose3D:
        """Helper method to create an Pose3D instance from a pose array."""
        ...

    @staticmethod
    def parse(json: Any) -> LLResult:
        """Parses a JSONObject into an LLResult object."""
        ...

    def toString(self) -> str:
        """Returns a string representation of the LLResult."""
        ...


class LLResultTypes:
    """Parent class for all Limelight Result Types"""
    __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes"
    class BarcodeResult:
        """Represents a barcode pipeline result. A barcode pipeline may generate multiple valid results."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.BarcodeResult"
        def __init__(self, data: Any) -> None:
            """Constructs a BarcodeResult from JSON data."""
            ...

        def getFamily(self) -> str:
            """Gets the family of the barcode."""
            ...

        def getData(self) -> str:
            """Gets the data contained in the barcode."""
            ...

        def getTargetXPixels(self) -> float:
            """Gets the horizontal offset of the barcode from the crosshair in pixels."""
            ...

        def getTargetYPixels(self) -> float:
            """Gets the vertical offset of the barcode from the crosshair in pixels."""
            ...

        def getTargetXDegrees(self) -> float:
            """Gets the horizontal offset of the barcode from the crosshair in degrees."""
            ...

        def getTargetYDegrees(self) -> float:
            """Gets the vertical offset of the barcode from the crosshair in degrees."""
            ...

        def getTargetXDegreesNoCrosshair(self) -> float:
            """Gets the horizontal offset of the barcode from the principal pixel in degrees."""
            ...

        def getTargetYDegreesNoCrosshair(self) -> float:
            """Gets the vertical offset of the barcode from the principal pixel in degrees."""
            ...

        def getTargetArea(self) -> float:
            """Gets the area of the detected barcode as a percentage of the image."""
            ...

        def getTargetCorners(self) -> list[list[float]]:
            """Gets the four corner points of the detected barcode."""
            ...

    class ClassifierResult:
        """Represents a classifier pipeline result."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.ClassifierResult"
        def __init__(self, data: Any) -> None:
            """Constructs a ClassifierResult from JSON data."""
            ...

        def getClassName(self) -> str:
            """Gets the class name of the classifier result (eg book, car, gamepiece)."""
            ...

        def getClassId(self) -> int:
            """Gets the class index of the classifier result."""
            ...

        def getConfidence(self) -> float:
            """Gets the confidence score of the classification."""
            ...

    class DetectorResult:
        """Represents a detector pipeline result. A detector pipeline may generate multiple valid results."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.DetectorResult"
        def __init__(self, data: Any) -> None:
            """Constructs a DetectorResult from JSON data."""
            ...

        def getClassName(self) -> str:
            """Gets the class name of the detector result (eg book, car, gamepiece)."""
            ...

        def getClassId(self) -> int:
            """Gets the class index of the detector result."""
            ...

        def getConfidence(self) -> float:
            """Gets the confidence score of the classification."""
            ...

        def getTargetCorners(self) -> list[list[float]]:
            """Gets the four corner points of the detected result."""
            ...

        def getTargetArea(self) -> float:
            """Gets the undistorted area of the target as a percentage of the image area"""
            ...

        def getTargetXPixels(self) -> float:
            """Gets the current tx in pixels from the crosshair"""
            ...

        def getTargetYPixels(self) -> float:
            """Gets the current ty in pixels from the crosshair"""
            ...

        def getTargetXDegrees(self) -> float:
            """Gets the current tx in degrees from the crosshair"""
            ...

        def getTargetYDegrees(self) -> float:
            """Gets the current ty in degrees from the crosshair"""
            ...

        def getTargetXDegreesNoCrosshair(self) -> float:
            """Gets the current tx in degrees from the principal pixel"""
            ...

        def getTargetYDegreesNoCrosshair(self) -> float:
            """Gets the current ty in degrees from the principal pixel"""
            ...

    class FiducialResult:
        """Represents a Fiducial/AprilTag pipeline result. A fiducial/apriltag pipeline may generate multiple valid results."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.FiducialResult"
        def __init__(self, data: Any) -> None:
            """Constructs a FiducialResult from JSON data."""
            ...

        def getFiducialId(self) -> int:
            """Gets the ID of the fiducial."""
            ...

        def getFamily(self) -> str:
            """Gets the family of the fiducial (eg 36h11)."""
            ...

        def getTargetCorners(self) -> list[list[float]]:
            """Gets the four corner points of the detected fiducial/apriltag."""
            ...

        def getSkew(self) -> float:
            """Gets the skew of the detected fiducial. Not recommended."""
            ...

        def getCameraPoseTargetSpace(self) -> Pose3D:
            """Gets the camera pose in target space."""
            ...

        def getRobotPoseFieldSpace(self) -> Pose3D:
            """Gets the robot pose in field based on this fiducial/apriltag alone."""
            ...

        def getRobotPoseTargetSpace(self) -> Pose3D:
            """Gets the robot pose in target space."""
            ...

        def getTargetPoseCameraSpace(self) -> Pose3D:
            """Gets the target pose in camera space."""
            ...

        def getTargetPoseRobotSpace(self) -> Pose3D:
            """Gets the target pose in robot space."""
            ...

        def getTargetArea(self) -> float:
            """Gets the area of the detected fiducial as a percentage of the image."""
            ...

        def getTargetXPixels(self) -> float:
            """Gets the current tx in pixels from the crosshair"""
            ...

        def getTargetYPixels(self) -> float:
            """Gets the current ty in pixels from the crosshair"""
            ...

        def getTargetXDegrees(self) -> float:
            """Gets the current tx in degrees from the crosshair"""
            ...

        def getTargetYDegrees(self) -> float:
            """Gets the current ty in degrees from the crosshair"""
            ...

        def getTargetXDegreesNoCrosshair(self) -> float:
            """Gets the current tx in degrees from the principal pixel"""
            ...

        def getTargetYDegreesNoCrosshair(self) -> float:
            """Gets the current ty in degrees from the principal pixel"""
            ...

    class ColorResult:
        """Represents a color pipeline result. A color pipeline may generate multiple valid results."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.ColorResult"
        def __init__(self, data: Any) -> None:
            """Constructs a Color/ColorResult from JSON data."""
            ...

        def getTargetCorners(self) -> list[list[float]]:
            """Gets the corner points of the detected target. The number of corners is not fixed."""
            ...

        def getCameraPoseTargetSpace(self) -> Pose3D:
            """Gets the camera pose in target space."""
            ...

        def getRobotPoseFieldSpace(self) -> Pose3D:
            """Gets the robot pose in field space based on this color target."""
            ...

        def getRobotPoseTargetSpace(self) -> Pose3D:
            """Gets the robot pose in target space."""
            ...

        def getTargetPoseCameraSpace(self) -> Pose3D:
            """Gets the target pose in camera space."""
            ...

        def getTargetPoseRobotSpace(self) -> Pose3D:
            """Gets the target pose in robot space."""
            ...

        def getTargetArea(self) -> float:
            """Gets the area of the detected color target as a percentage of the image."""
            ...

        def getTargetXPixels(self) -> float:
            """Gets the current tx in pixels from the crosshair"""
            ...

        def getTargetYPixels(self) -> float:
            """Gets the current ty in pixels from the crosshair"""
            ...

        def getTargetXDegrees(self) -> float:
            """Gets the current tx in degrees from the crosshair"""
            ...

        def getTargetYDegrees(self) -> float:
            """Gets the current ty in degrees from the crosshair"""
            ...

        def getTargetXDegreesNoCrosshair(self) -> float:
            """Gets the current tx in degrees from the principal pixel"""
            ...

        def getTargetYDegreesNoCrosshair(self) -> float:
            """Gets the current ty in degrees from the principal pixel"""
            ...

    class CalibrationResult:
        """Represents a calibration result. Calibration results are generated by the user in the UI's calibration tab."""
        __java__ = "com.qualcomm.hardware.limelightvision.LLResultTypes.CalibrationResult"
        @overload
        def __init__(self) -> None:
            """Constructs a CalibrationResult with default values."""
            ...
        @overload
        def __init__(self, displayName: str, resX: float, resY: float, reprojectionError: float, camMatVector: list[float], distortionCoefficients: list[float]) -> None:
            """Constructs a CalibrationResult with specified values."""
            ...
        @overload
        def __init__(self, json: Any) -> None:
            """Constructs a CalibrationResult from JSON data. (Package-private)"""
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def isValid(self) -> bool:
            """Checks if the calibration result is valid."""
            ...

        def getDisplayName(self) -> str:
            """Gets the display name of the calibration."""
            ...

        def getResX(self) -> float:
            """Gets the X resolution of the calibration."""
            ...

        def getResY(self) -> float:
            """Gets the Y resolution of the calibration."""
            ...

        def getReprojectionError(self) -> float:
            """Gets the reprojection error of the calibration."""
            ...

        def getCamMatVector(self) -> list[float]:
            """Gets the camera matrix vector."""
            ...

        def getDistortionCoefficients(self) -> list[float]:
            """Gets the distortion coefficients."""
            ...

        def toJson(self) -> Any:
            """Converts a CalibrationResult to a JSONObject."""
            ...


class LLStatus:
    """Represents the status of a Limelight."""
    __java__ = "com.qualcomm.hardware.limelightvision.LLStatus"
    @overload
    def __init__(self) -> None:
        """Constructs an LLStatus object with default values."""
        ...
    @overload
    def __init__(self, json: Any) -> None:
        """Constructs an LLStatus object from a JSON string."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getCameraQuat(self) -> Quaternion:
        ...

    def getCid(self) -> int:
        ...

    def getCpu(self) -> float:
        ...

    def getFinalYaw(self) -> float:
        ...

    def getFps(self) -> float:
        ...

    def getHwType(self) -> int:
        ...

    def getName(self) -> str:
        ...

    def getPipeImgCount(self) -> int:
        ...

    def getPipelineIndex(self) -> int:
        ...

    def getPipelineType(self) -> str:
        ...

    def getRam(self) -> float:
        ...

    def getSnapshotMode(self) -> int:
        ...

    def getTemp(self) -> float:
        ...

    def toString(self) -> str:
        """Returns a string representation of the LLStatus object."""
        ...


class Limelight3A(HardwareDevice):
    """Driver for Limelight3A Vision Sensor. Limelight3A provides support for the Limelight Vision Limelight3A Vision Sensor."""
    __java__ = "com.qualcomm.hardware.limelightvision.Limelight3A"
    def __init__(self, serialNumber: SerialNumber, name: str, ipAddress: Any) -> None:
        ...

    def start(self) -> None:
        """Starts or resumes periodic polling of Limelight data."""
        ...

    def pause(self) -> None:
        """Pauses polling of Limelight data."""
        ...

    def stop(self) -> None:
        """Stops polling of Limelight data."""
        ...

    def isRunning(self) -> bool:
        """Checks if the polling is enabled."""
        ...

    def setPollRateHz(self, rateHz: int) -> None:
        """Sets the poll rate in Hertz (Hz). Must be called before start() The rate is clamped between 1 and 250 Hz."""
        ...

    def getTimeSinceLastUpdate(self) -> int:
        """Gets the time elapsed since the last update."""
        ...

    def isConnected(self) -> bool:
        """Checks if the Limelight is currently connected."""
        ...

    def getLatestResult(self) -> LLResult:
        """Gets the latest result from the Limelight."""
        ...

    def getStatus(self) -> LLStatus:
        """Gets the current status of the Limelight."""
        ...

    def reloadPipeline(self) -> bool:
        """Reloads the current Limelight pipeline."""
        ...

    def pipelineSwitch(self, index: int) -> bool:
        """Switches to a pipeline at the specified index."""
        ...

    def captureSnapshot(self, snapname: str) -> bool:
        """Captures a snapshot with the given name."""
        ...

    def deleteSnapshots(self) -> bool:
        """Deletes all snapshots."""
        ...

    def deleteSnapshot(self, snapname: str) -> bool:
        """Deletes a specific snapshot."""
        ...

    @overload
    def updatePythonInputs(self, input1: float, input2: float, input3: float, input4: float, input5: float, input6: float, input7: float, input8: float) -> bool:
        """Updates the Python SnapScript inputs with 8 double values."""
        ...
    @overload
    def updatePythonInputs(self, inputs: list[float]) -> bool:
        """Updates the Python SnapScript inputs."""
        ...
    def updatePythonInputs(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def updateRobotOrientation(self, yaw: float) -> bool:
        """Updates the robot orientation for MegaTag2."""
        ...

    def uploadPipeline(self, jsonString: str, index: int) -> bool:
        """Uploads a pipeline to a specific slot."""
        ...

    def uploadFieldmap(self, fieldmap: LLFieldMap, index: int) -> bool:
        """Uploads a new fiducial field map. Early exits if map is empty or doesn't specify a type"""
        ...

    def uploadPython(self, pythonString: str, index: int) -> bool:
        """Uploads new Python code."""
        ...

    def getCalDefault(self) -> LLResultTypes.CalibrationResult:
        """Gets the default calibration data."""
        ...

    def getCalFile(self) -> LLResultTypes.CalibrationResult:
        """Gets calibration data from the user-generated calibration file."""
        ...

    def getCalEEPROM(self) -> LLResultTypes.CalibrationResult:
        """Gets the calibration data from the Limelight EEPROM."""
        ...

    def getCalLatest(self) -> LLResultTypes.CalibrationResult:
        """Gets the latest calibration result. This result is not necessarily used by the camera in any way"""
        ...

    def shutdown(self) -> None:
        """Shuts down the Limelight connection and stops all ongoing processes."""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...


class LynxModuleIntf(RobotCoreLynxModule, Engagable):
    """LynxModuleIntf is an interface to LynxModule so as to allow for an alternate substitution of PretendLynxModule when necessary."""
    __java__ = "com.qualcomm.hardware.lynx.LynxModuleIntf"
    def acquireI2cLockWhile(self, supplier: Supplier[T]) -> T:
        ...

    def acquireNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def releaseNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def validateCommand(self, lynxMessage: LynxMessage) -> None:
        ...

    def isCommandSupported(self, command: type[LynxCommand]) -> bool:
        ...

    def isOpen(self) -> bool:
        ...

    def sendCommand(self, message: LynxMessage) -> None:
        ...

    def resetPingTimer(self, message: LynxMessage) -> None:
        ...

    def retransmit(self, message: LynxMessage) -> None:
        ...

    def finishedWithMessage(self, message: LynxMessage) -> None:
        ...

    def setAttentionRequired(self, attentionRequired: bool) -> None:
        ...

    def noteNotResponding(self) -> None:
        ...

    def isNotResponding(self) -> bool:
        ...

    def getInterface(self, interfaceName: str) -> LynxInterface:
        ...


class LynxCommExceptionHandler:
    """Created by bob on 2016-12-11."""
    __java__ = "com.qualcomm.hardware.lynx.LynxCommExceptionHandler"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, tag: str) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getTag(self) -> str:
        ...

    def handleException(self, e: Any) -> bool:
        """Returns true if command was supported (so: exception was something else) or false if the exception indicated that the command wasn't supported"""
        ...

    @overload
    def handleSpecificException(self, e: Any) -> None:
        ...
    @overload
    def handleSpecificException(self, e: TargetPositionNotSetException) -> None:
        ...
    @overload
    def handleSpecificException(self, e: Any) -> None:
        ...
    @overload
    def handleSpecificException(self, nackException: LynxNackException) -> None:
        ...
    def handleSpecificException(self, *args: Any, **kwargs: Any) -> Any:
        ...

    tag: str


class LynxController(LynxCommExceptionHandler, RobotCoreLynxController, Engagable, HardwareDeviceHealth, RobotArmingStateNotifier.Callback, RobotArmingStateNotifier):
    """Created by bob on 2016-03-07."""
    __java__ = "com.qualcomm.hardware.lynx.LynxController"
    class PretendLynxModule(LynxModuleIntf):
        __java__ = "com.qualcomm.hardware.lynx.LynxController.PretendLynxModule"
        def getManufacturer(self) -> HardwareDevice.Manufacturer:
            ...

        def getFirmwareVersionString(self) -> str:
            ...

        def getNullableFirmwareVersionString(self) -> str:
            ...

        def getDeviceName(self) -> str:
            ...

        def getConnectionInfo(self) -> str:
            ...

        def getVersion(self) -> int:
            ...

        def resetDeviceConfigurationForOpMode(self) -> None:
            ...

        def close(self) -> None:
            ...

        def getSerialNumber(self) -> SerialNumber:
            ...

        def acquireI2cLockWhile(self, supplier: Supplier[T]) -> T:
            ...

        def acquireNetworkTransmissionLock(self, message: LynxMessage) -> None:
            ...

        def releaseNetworkTransmissionLock(self, message: LynxMessage) -> None:
            ...

        def sendCommand(self, command: LynxMessage) -> None:
            ...

        def retransmit(self, message: LynxMessage) -> None:
            ...

        def finishedWithMessage(self, message: LynxMessage) -> None:
            ...

        def resetPingTimer(self, message: LynxMessage) -> None:
            ...

        def getModuleAddress(self) -> int:
            ...

        def setAttentionRequired(self, attentionRequired: bool) -> None:
            ...

        def getInterface(self, interfaceName: str) -> LynxInterface:
            ...

        def isParent(self) -> bool:
            ...

        def validateCommand(self, lynxMessage: LynxMessage) -> None:
            ...

        def isCommandSupported(self, command: type[LynxCommand]) -> bool:
            ...

        def isOpen(self) -> bool:
            ...

        def isEngaged(self) -> bool:
            ...

        def engage(self) -> None:
            ...

        def disengage(self) -> None:
            ...

        def noteNotResponding(self) -> None:
            ...

        def isNotResponding(self) -> bool:
            ...

        def attemptFailSafeAndIgnoreErrors(self) -> None:
            ...

        isEngaged_: bool

    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def finishConstruction(self) -> None:
        ...

    def onModuleStateChange(self, module: RobotArmingStateNotifier, state: RobotArmingStateNotifier.ARMINGSTATE) -> None:
        ...

    def moduleNowArmedOrPretending(self) -> None:
        ...

    def moduleNowDisarmed(self) -> None:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getArmingState(self) -> RobotArmingStateNotifier.ARMINGSTATE:
        ...

    def registerCallback(self, callback: RobotArmingStateNotifier.Callback, doInitialCallback: bool) -> None:
        ...

    def unregisterCallback(self, callback: RobotArmingStateNotifier.Callback) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def close(self) -> None:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def getDeviceName(self) -> str:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def initializeHardwareIfNecessary(self) -> None:
        ...

    def initializeHardware(self) -> None:
        ...

    def floatHardware(self) -> None:
        ...

    def forgetLastKnown(self) -> None:
        ...

    def setHealthyIfArmed(self) -> None:
        ...

    def setHealthStatus(self, status: HardwareDeviceHealth.HealthStatus) -> None:
        ...

    def getHealthStatusOverride(self) -> Any:
        ...

    def getHealthStatus(self) -> HardwareDeviceHealth.HealthStatus:
        ...

    def engage(self) -> None:
        ...

    def disengage(self) -> None:
        ...

    def isEngaged(self) -> bool:
        ...

    def getModule(self) -> LynxModuleIntf:
        ...

    def adjustHookingToMatchEngagement(self) -> None:
        ...

    def hook(self) -> None:
        ...

    def unhook(self) -> None:
        ...

    def doHook(self) -> None:
        ...

    def doUnhook(self) -> None:
        ...

    def isArmed(self) -> bool:
        ...

    context: Any
    isHardwareInitialized: bool
    isEngaged_: bool
    isHooked: bool
    registeredCallbacks: WeakReferenceSet[RobotArmingStateNotifier.Callback]
    hardwareDeviceHealth: HardwareDeviceHealthImpl


class LynxAnalogInputController(LynxController, AnalogInputController):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.hardware.lynx.LynxAnalogInputController"
    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def getDeviceName(self) -> str:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getAnalogInputVoltage(self, port: int) -> float:
        ...

    def getMaxAnalogInputVoltage(self) -> float:
        ...

    TAG: str
    apiPortFirst: int
    apiPortLast: int


class LynxDcMotorController(LynxController, DcMotorControllerEx):
    """LynxDcMotorController implements motor controller semantics on Lynx module"""
    __java__ = "com.qualcomm.hardware.lynx.LynxDcMotorController"
    class MotorProperties:
        __java__ = "com.qualcomm.hardware.lynx.LynxDcMotorController.MotorProperties"
        lastKnownPower: LastKnown[float]
        lastKnownTargetPosition: LastKnown[int]
        lastKnownMode: LastKnown[DcMotor.RunMode]
        lastKnownZeroPowerBehavior: LastKnown[DcMotor.ZeroPowerBehavior]
        lastKnownEnable: LastKnown[bool]
        lastKnownCurrentAlert: LastKnown[float]
        motorType: MotorConfigurationType
        internalMotorType: MotorConfigurationType
        desiredPIDParams: dict[DcMotor.RunMode, ExpansionHubMotorControllerParamsState]
        originalPIDParams: dict[DcMotor.RunMode, ExpansionHubMotorControllerParamsState]

    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def initializeHardware(self) -> None:
        ...

    def doHook(self) -> None:
        ...

    def doUnhook(self) -> None:
        ...

    def forgetLastKnown(self) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def setMotorEnable(self, motor: int) -> None:
        ...

    def setMotorDisable(self, motor: int) -> None:
        ...

    def internalSetMotorEnable(self, motorZ: int, enable: bool) -> None:
        ...

    def isMotorEnabled(self, motor: int) -> bool:
        ...

    def resetDeviceConfigurationForOpMode(self, motor: int) -> None:
        ...

    def getMotorType(self, motor: int) -> MotorConfigurationType:
        ...

    def setMotorType(self, motor: int, motorType: MotorConfigurationType) -> None:
        ...

    def rememberPIDParams(self, motorZ: int, params: ExpansionHubMotorControllerParamsState) -> None:
        ...

    def updateMotorParams(self, motorZ: int) -> None:
        ...

    def getDefaultMaxMotorSpeed(self, motorZ: int) -> int:
        ...

    def setMotorMode(self, motor: int, mode: DcMotor.RunMode) -> None:
        ...

    def getMotorMode(self, motor: int) -> DcMotor.RunMode:
        ...

    def internalGetPublicMotorMode(self, motorZ: int) -> DcMotor.RunMode:
        ...

    def internalGetMotorChannelMode(self, motorZ: int) -> DcMotor.RunMode:
        """like #internalGetPublicMotorMode(int), but ALWAYS returns a value that can be set with LynxSetMotorChannelModeCommand. We also don't here update lastKnownMode."""
        ...

    def setMotorPower(self, motor: int, apiMotorPower: float) -> None:
        ...

    def getMotorPower(self, motor: int) -> float:
        ...

    def internalGetZeroPowerBehavior(self, motorZ: int) -> DcMotor.ZeroPowerBehavior:
        ...

    def internalSetZeroPowerBehavior(self, motorZ: int, behavior: DcMotor.ZeroPowerBehavior) -> None:
        ...

    @overload
    def internalSetMotorPower(self, motorZ: int, apiPower: float) -> None:
        ...
    @overload
    def internalSetMotorPower(self, motorZ: int, apiPower: float, forceUpdate: bool) -> None:
        ...
    def internalSetMotorPower(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def internalGetMotorPower(self, motorZ: int) -> float:
        ...

    def isBusy(self, motor: int) -> bool:
        ...

    def setMotorZeroPowerBehavior(self, motor: int, zeroPowerBehavior: DcMotor.ZeroPowerBehavior) -> None:
        ...

    def getMotorZeroPowerBehavior(self, motor: int) -> DcMotor.ZeroPowerBehavior:
        ...

    def setMotorPowerFloat(self, motor: int) -> None:
        ...

    def getMotorPowerFloat(self, motor: int) -> bool:
        ...

    @overload
    def setMotorTargetPosition(self, motor: int, position: int) -> None:
        ...
    @overload
    def setMotorTargetPosition(self, motor: int, position: int, tolerance: int) -> None:
        ...
    def setMotorTargetPosition(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getMotorTargetPosition(self, motor: int) -> int:
        ...

    def getMotorCurrentPosition(self, motor: int) -> int:
        ...

    @overload
    def setMotorVelocity(self, motor: int, ticksPerSecond: float) -> None:
        ...
    @overload
    def setMotorVelocity(self, motor: int, angularRate: float, unit: AngleUnit) -> None:
        ...
    def setMotorVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getMotorVelocity(self, motor: int) -> float:
        ...
    @overload
    def getMotorVelocity(self, motor: int, unit: AngleUnit) -> float:
        ...
    def getMotorVelocity(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def internalGetMotorTicksPerSecond(self, motorZ: int) -> int:
        ...

    def setPIDCoefficients(self, motor: int, mode: DcMotor.RunMode, pidCoefficients: PIDCoefficients) -> None:
        ...

    def setPIDFCoefficients(self, motor: int, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> None:
        ...

    def internalSetPIDFCoefficients(self, motorZ: int, mode: DcMotor.RunMode, pidfCoefficients: PIDFCoefficients) -> bool:
        ...

    def getPIDCoefficients(self, motor: int, mode: DcMotor.RunMode) -> PIDCoefficients:
        ...

    def getPIDFCoefficients(self, motor: int, mode: DcMotor.RunMode) -> PIDFCoefficients:
        ...

    def getMotorCurrent(self, motor: int, unit: CurrentUnit) -> float:
        ...

    def getMotorCurrentAlert(self, motor: int, unit: CurrentUnit) -> float:
        ...

    def setMotorCurrentAlert(self, motor: int, current: float, unit: CurrentUnit) -> None:
        ...

    def isMotorOverCurrent(self, motor: int) -> bool:
        ...

    def floatHardware(self) -> None:
        ...

    def getModuleAddress(self) -> int:
        ...

    apiMotorFirst: int
    apiMotorLast: int
    apiPowerFirst: float
    apiPowerLast: float
    TAG: str
    DEBUG: bool
    motors: list[LynxDcMotorController.MotorProperties]


class LynxDigitalChannelController(LynxController, DigitalChannelController):
    """LynxDigitalChannelController provides access to the digital IO pins on a Lynx module."""
    __java__ = "com.qualcomm.hardware.lynx.LynxDigitalChannelController"
    class PinProperties:
        __java__ = "com.qualcomm.hardware.lynx.LynxDigitalChannelController.PinProperties"
        lastKnownMode: LastKnown[DigitalChannel.Mode]
        lastKnownState: LastKnown[bool]

    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def initializeHardware(self) -> None:
        ...

    def forgetLastKnown(self) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getDigitalChannelMode(self, pin: int) -> DigitalChannel.Mode:
        ...

    @overload
    def setDigitalChannelMode(self, pin: int, mode: DigitalChannel.Mode) -> None:
        ...
    @overload
    def setDigitalChannelMode(self, pin: int, mode: DigitalChannelController.Mode) -> None:
        ...
    def setDigitalChannelMode(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def internalSetDigitalChannelMode(self, pinZ: int, mode: DigitalChannel.Mode) -> None:
        ...

    def getDigitalChannelState(self, pin: int) -> bool:
        ...

    def setDigitalChannelState(self, pin: int, state: bool) -> None:
        ...

    TAG: str
    apiPinFirst: int
    apiPinLast: int
    pins: list[LynxDigitalChannelController.PinProperties]


class LynxEmbeddedBNO055IMUNew(BNO055IMUNew):
    __java__ = "com.qualcomm.hardware.lynx.LynxEmbeddedBNO055IMUNew"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class LynxEmbeddedIMU(BNO055IMUImpl):
    """LynxEmbeddedIMU represents a BNO055 IMU embedded on the lynx board. It cannot be used for the BHI260AP IMU on newer Control Hubs."""
    __java__ = "com.qualcomm.hardware.lynx.LynxEmbeddedIMU"
    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        """This constructor is used internally by the FTC SDK"""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class LynxFirmwareUpdater:
    __java__ = "com.qualcomm.hardware.lynx.LynxFirmwareUpdater"
    def __init__(self, device: Any) -> None:
        ...

    def updateFirmware(self, image: RobotCoreCommandList.FWImage, requestId: str, progressConsumer: Consumer[ProgressParameters]) -> RobotCoreCommandList.LynxFirmwareUpdateResp:
        ...

    def enterFirmwareUpdateModeControlHub(self) -> bool:
        ...


class LynxI2cColorRangeSensor(AMSColorSensorImpl, ColorRangeSensor):
    """LynxI2cColorRangeSensor is both a color sensor and a distance sensor, supporting both DistanceSensor for calibrated readings and OpticalDistanceSensor (which is an historical name that could perhaps have been chosen better) for raw, uncalibrated readings."""
    __java__ = "com.qualcomm.hardware.lynx.LynxI2cColorRangeSensor"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def getDistance(self, unit: DistanceUnit) -> float:
        """Returns a calibrated, linear sense of distance as read by the infrared proximity part of the sensor. Distance is measured to the plastic housing at the front of the sensor. Natively, the raw optical signal follows an inverse square law. Here, parameters have been fitted to turn that into a linear measure of distance. The function fitted was of the form: rawOptical = a + b * (cm + c)^(-2) This fitted linearity is fairly accurate over a wide range of target surfaces, but is ultimately affected by the infrared reflectivity of the surface. However, even on surfaces where there is significantly different reflectivity, the linearity calculated here tends to be preserved, so distance accuracy can often be refined with a simple further multiplicative scaling. Note that readings are most accurate when perpendicular to the surface. For non-perpendicularity, a cosine correction factor is usually appropriate."""
        ...

    def cmFromOptical(self, rawOptical: int) -> float:
        """Converts a raw optical inverse-square reading into a fitted, calibrated linear reading in cm."""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getLightDetected(self) -> float:
        ...

    def getRawLightDetected(self) -> float:
        ...

    def getRawLightDetectedMax(self) -> float:
        ...

    def status(self) -> str:
        ...

    def rawOptical(self) -> int:
        ...

    apiLevelMin: float
    apiLevelMax: float
    aParam: float
    """Experimentally determined constants for converting optical measurements to distance."""
    bParam: float
    cParam: float


class LynxI2cDeviceSynch(LynxController):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.hardware.lynx.LynxI2cDeviceSynch"
    class BusSpeed(enum.Enum):
        """Lynx I2C bus speed."""
        __java__ = "com.qualcomm.hardware.lynx.LynxI2cDeviceSynch.BusSpeed"
        STANDARD_100K = enum.auto()
        FAST_400K = enum.auto()
        def toSpeedCode(self) -> LynxI2cConfigureChannelCommand.SpeedCode:
            ...

    def __init__(self, context: Any, module: LynxModule, bus: int) -> None:
        ...

    def getTag(self) -> str:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    def isArmed(self) -> bool:
        ...

    def setI2cAddress(self, i2cAddr: I2cAddr) -> None:
        ...

    def setI2cAddr(self, i2cAddr: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def getI2cAddr(self) -> I2cAddr:
        ...

    def setUserConfiguredName(self, name: str) -> None:
        ...

    def getUserConfiguredName(self) -> str:
        ...

    def setLogging(self, enabled: bool) -> None:
        ...

    def getLogging(self) -> bool:
        ...

    def setLoggingTag(self, loggingTag: str) -> None:
        ...

    def getLoggingTag(self) -> str:
        ...

    def setHistoryQueueCapacity(self, capacity: int) -> None:
        ...

    def getHistoryQueueCapacity(self) -> int:
        ...

    def getHistoryQueue(self) -> Any:
        ...

    @overload
    def read(self, ireg: int, creg: int) -> list[int]:
        ...
    @overload
    def read(self, creg: int) -> list[int]:
        ...
    def read(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def read8(self, ireg: int) -> int:
        ...
    @overload
    def read8(self) -> int:
        ...
    def read8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def readTimeStamped(self, ireg: int, creg: int) -> TimestampedData:
        ...
    @overload
    def readTimeStamped(self, creg: int) -> TimestampedData:
        ...
    def readTimeStamped(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write(self, ireg: int, data: list[int]) -> None:
        ...
    @overload
    def write(self, ireg: int, data: list[int], waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def write(self, data: list[int]) -> None:
        ...
    @overload
    def write(self, data: list[int], waitControl: I2cWaitControl) -> None:
        ...
    def write(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def write8(self, ireg: int, bVal: int) -> None:
        ...
    @overload
    def write8(self, ireg: int, bVal: int, waitControl: I2cWaitControl) -> None:
        ...
    @overload
    def write8(self, bVal: int) -> None:
        ...
    @overload
    def write8(self, bVal: int, waitControl: I2cWaitControl) -> None:
        ...
    def write8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def waitForWriteCompletions(self, waitControl: I2cWaitControl) -> None:
        ...

    def enableWriteCoalescing(self, enable: bool) -> None:
        ...

    def isWriteCoalescingEnabled(self) -> bool:
        ...

    def sendI2cTransaction(self, transactionSupplier: Supplier[LynxCommand[object]]) -> None:
        """Waits for the current I2C transaction to finish, then executes the supplied transaction."""
        ...

    def acquireI2cLockWhile(self, supplier: Supplier[T]) -> T:
        ...

    def internalWaitForWriteCompletions(self, waitControl: I2cWaitControl) -> None:
        ...

    def pollForReadResult(self, i2cAddr: I2cAddr, ireg: int, creg: int) -> TimestampedData:
        ...

    def setBusSpeed(self, speed: LynxI2cDeviceSynch.BusSpeed) -> None:
        """Sets the bus speed."""
        ...

    TAG: str
    i2cAddr: I2cAddr
    bus: int
    readTimeStampedPlaceholder: LynxUsbUtil.Placeholder[TimestampedData]


class LynxI2cDeviceSynchV1(LynxI2cDeviceSynch):
    __java__ = "com.qualcomm.hardware.lynx.LynxI2cDeviceSynchV1"
    def __init__(self, context: Any, module: LynxModule, bus: int) -> None:
        ...

    def readTimeStamped(self, ireg: int, creg: int) -> TimestampedData:
        ...


class LynxI2cDeviceSynchV2(LynxI2cDeviceSynch):
    __java__ = "com.qualcomm.hardware.lynx.LynxI2cDeviceSynchV2"
    def __init__(self, context: Any, module: LynxModule, bus: int) -> None:
        ...

    def readTimeStamped(self, ireg: int, creg: int) -> TimestampedData:
        ...


class LynxModule(LynxCommExceptionHandler, LynxModuleIntf, RobotArmingStateNotifier, RobotArmingStateNotifier.Callback, Blinker, VisuallyIdentifiableHardwareDevice):
    """LynxModule represents the connection between the host and a particular Lynx controller module. Multiple Lynx controller modules may be chained together over RS-485 and share a common USB connection."""
    __java__ = "com.qualcomm.hardware.lynx.LynxModule"
    class MessageClassAndCtor:
        """A Class for one of the Lynx messages together with a cached constructor thereto"""
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.MessageClassAndCtor"
        def assignCtor(self) -> None:
            ...

        clazz: type[LynxMessage]
        ctor: Any

    class BlinkerPolicy:
        """BlinkerPolicy embodies the various blinker patterns exhibited by LynxModules The policy can be changed, globally, by setting the variable #blinkerPolicy."""
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.BlinkerPolicy"
        def getIdlePattern(self, lynxModule: LynxModule) -> list[Blinker.Step]:
            ...

        def getVisuallyIdentifyPattern(self, lynxModule: LynxModule) -> list[Blinker.Step]:
            ...

    class BreathingBlinkerPolicy(BlinkerPolicy):
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.BreathingBlinkerPolicy"
        def getIdlePattern(self, lynxModule: LynxModule) -> list[Blinker.Step]:
            ...

        def getVisuallyIdentifyPattern(self, lynxModule: LynxModule) -> list[Blinker.Step]:
            ...

    class CountModuleAddressBlinkerPolicy(BreathingBlinkerPolicy):
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.CountModuleAddressBlinkerPolicy"
        def getIdlePattern(self, lynxModule: LynxModule) -> list[Blinker.Step]:
            ...

    class BulkData:
        """Container for the values retrieved with a bulk read."""
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.BulkData"
        def getDigitalChannelState(self, digitalInputZ: int) -> bool:
            ...

        def getMotorCurrentPosition(self, motorZ: int) -> int:
            ...

        def getMotorVelocity(self, motorZ: int) -> int:
            """Returns (signed) motor velocity in encoder counts per second"""
            ...

        def isMotorBusy(self, motorZ: int) -> bool:
            ...

        def isMotorOverCurrent(self, motorZ: int) -> bool:
            ...

        @overload
        def getAnalogInputVoltage(self, inputZ: int) -> float:
            """Returns the analog input in V"""
            ...
        @overload
        def getAnalogInputVoltage(self, inputZ: int, unit: VoltageUnit) -> float:
            ...
        def getAnalogInputVoltage(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def isFake(self) -> bool:
            ...

    class BulkCachingMode(enum.Enum):
        """Bulk caching mode that controls the behavior of certain read commands."""
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.BulkCachingMode"
        OFF = enum.auto()
        MANUAL = enum.auto()
        AUTO = enum.auto()

    class DebugGroup(enum.Enum):
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.DebugGroup"
        NONE = enum.auto()
        MAIN = enum.auto()
        TOHOST = enum.auto()
        FROMHOST = enum.auto()
        ADC = enum.auto()
        PWMSERVO = enum.auto()
        MODULELED = enum.auto()
        DIGITALIO = enum.auto()
        I2C = enum.auto()
        MOTOR0 = enum.auto()
        MOTOR1 = enum.auto()
        MOTOR2 = enum.auto()
        MOTOR3 = enum.auto()
        @staticmethod
        def fromInt(b: int) -> LynxModule.DebugGroup:
            ...

        bVal: int

    class DebugVerbosity(enum.Enum):
        __java__ = "com.qualcomm.hardware.lynx.LynxModule.DebugVerbosity"
        OFF = enum.auto()
        LOW = enum.auto()
        MEDIUM = enum.auto()
        HIGH = enum.auto()
        @staticmethod
        def fromInt(b: int) -> LynxModule.DebugVerbosity:
            ...

        bVal: int

    def __init__(self, lynxUsbDevice: LynxUsbDevice, moduleAddress: int, isParent: bool, isUserModule: bool) -> None:
        ...

    def getTag(self) -> str:
        ...

    @staticmethod
    def addStandardMessage(clazz: type[LynxMessage]) -> None:
        ...

    @staticmethod
    def correlateStandardResponse(commandClass: type[LynxCommand]) -> None:
        ...

    @staticmethod
    def correlateResponse(commandClass: type[LynxCommand], responseClass: type[LynxResponse]) -> None:
        ...

    def toString(self) -> str:
        ...

    def close(self) -> None:
        ...

    def isOpen(self) -> bool:
        ...

    def isUserModule(self) -> bool:
        ...

    def setUserModule(self, isUserModule: bool) -> None:
        ...

    def isSystemSynthetic(self) -> bool:
        ...

    def setSystemSynthetic(self, systemSynthetic: bool) -> None:
        ...

    def noteController(self, controller: LynxController) -> None:
        ...

    def getRevProductNumber(self) -> int:
        ...

    def getModuleAddress(self) -> int:
        ...

    def setNewModuleAddress(self, newModuleAddress: int) -> None:
        ...

    def getNewMessageNumber(self) -> int:
        ...

    def setAttentionRequired(self, attentionRequired: bool) -> None:
        ...

    def noteDatagramReceived(self) -> None:
        ...

    def noteNotResponding(self) -> None:
        ...

    def isNotResponding(self) -> bool:
        ...

    def warnIfClosed(self) -> None:
        ...

    def stopAttentionRequired(self) -> None:
        ...

    def sendGetModuleStatusAndProcessResponse(self, clearStatus: bool) -> None:
        ...

    def forgetLastKnown(self) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getFirmwareVersionString(self) -> str:
        ...

    def getNullableFirmwareVersionString(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def getGlobalWarnings(self) -> list[str]:
        """Returns any global warnings from this device. Currently, such warnings are culled from the health status of the controllers attached to this module. If no warnings are currently relevant, then an empty list is returned."""
        ...

    @staticmethod
    def getHealthStatusWarningMessage(hardwareDeviceHealth: HardwareDeviceHealth) -> str:
        """Returns a status warning message indicative of the health of the indicated device, or an empty string if no such message is currently applicable."""
        ...

    def getModuleSerialNumber(self) -> SerialNumber:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getArmingState(self) -> RobotArmingStateNotifier.ARMINGSTATE:
        ...

    def registerCallback(self, callback: RobotArmingStateNotifier.Callback, doInitialCallback: bool) -> None:
        ...

    def unregisterCallback(self, callback: RobotArmingStateNotifier.Callback) -> None:
        ...

    def onModuleStateChange(self, module: RobotArmingStateNotifier, state: RobotArmingStateNotifier.ARMINGSTATE) -> None:
        ...

    def engage(self) -> None:
        ...

    def disengage(self) -> None:
        ...

    def isEngaged(self) -> bool:
        ...

    def visuallyIdentify(self, shouldIdentify: bool) -> None:
        ...

    def getBlinkerPatternMaxLength(self) -> int:
        ...

    def setConstant(self, color: int) -> None:
        ...

    def stopBlinking(self) -> None:
        ...

    def setPattern(self, steps: list[Blinker.Step]) -> None:
        ...

    def getPattern(self) -> list[Blinker.Step]:
        ...

    def resendCurrentPattern(self) -> None:
        ...

    def pushPattern(self, steps: list[Blinker.Step]) -> None:
        ...

    def internalPushPattern(self, steps: list[Blinker.Step]) -> None:
        ...

    def patternStackNotEmpty(self) -> bool:
        ...

    def popPattern(self) -> bool:
        ...

    def sendLEDPatternSteps(self, steps: list[Blinker.Step]) -> None:
        ...

    def isParent(self) -> bool:
        ...

    def pingAndQueryKnownInterfacesAndEtc(self) -> None:
        """Do all the stuff we need to do when we've become aware that this module is in fact attached to its USB device. Throws a RobotCoreException if we were unable to communicate with the module."""
        ...

    def initializeLEDS(self) -> None:
        ...

    def initializeDebugLogging(self) -> None:
        ...

    def pingInitialContact(self) -> None:
        ...

    def validateCommand(self, lynxMessage: LynxMessage) -> None:
        ...

    def isCommandSupported(self, clazz: type[LynxCommand]) -> bool:
        """Answers as to whether the command is actively supported by the module, at least in SOME interface, or as a standard command"""
        ...

    def queryInterface(self, theInterface: LynxInterface) -> bool:
        """Issues a query interface for the indicated interface and processes the results. This method is idempotent, and copes with a module changing its mind about command numbering."""
        ...

    def getInterface(self, interfaceName: str) -> LynxInterface:
        """Returns null if the interface has not been queried or is not supported"""
        ...

    @overload
    def ping(self) -> None:
        ...
    @overload
    def ping(self, initialPing: bool) -> None:
        ...
    def ping(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getMsModulePingInterval(self) -> int:
        ...

    def resetPingTimer(self, message: LynxMessage) -> None:
        ...

    def startPingTimer(self) -> None:
        ...

    def stopPingTimer(self, wait: bool) -> None:
        ...

    def startFtdiResetWatchdog(self) -> None:
        ...

    @overload
    def stopFtdiResetWatchdog(self) -> None:
        ...
    @overload
    def stopFtdiResetWatchdog(self, disengaging: bool) -> None:
        ...
    def stopFtdiResetWatchdog(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setFtdiResetWatchdog(self, enabled: bool) -> None:
        ...

    def startExecutor(self) -> None:
        ...

    def stopExecutor(self) -> None:
        ...

    def getBulkData(self) -> LynxModule.BulkData:
        """Gets the bulk data for this module and clears the cache. A bulk read command is *always* issued regardless of the bulk caching mode."""
        ...

    def getBulkCachingMode(self) -> LynxModule.BulkCachingMode:
        """Returns the current bulk caching mode."""
        ...

    def setBulkCachingMode(self, mode: LynxModule.BulkCachingMode) -> None:
        """Sets the bulk caching mode. Cache is cleared if new mode is OFF."""
        ...

    def clearBulkCache(self) -> None:
        """Clears the bulk read cache."""
        ...

    @overload
    def recordBulkCachingCommandIntent(self, command: LynxDekaInterfaceCommand[object]) -> LynxModule.BulkData:
        ...
    @overload
    def recordBulkCachingCommandIntent(self, command: LynxDekaInterfaceCommand[object], tag: str) -> LynxModule.BulkData:
        ...
    def recordBulkCachingCommandIntent(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def failSafe(self) -> None:
        ...

    def attemptFailSafeAndIgnoreErrors(self) -> None:
        ...

    def enablePhoneCharging(self, enable: bool) -> None:
        ...

    def isPhoneChargingEnabled(self) -> bool:
        ...

    def getCurrent(self, unit: CurrentUnit) -> float:
        """Returns the current consumption of the whole module."""
        ...

    def getGpioBusCurrent(self, unit: CurrentUnit) -> float:
        """Returns the current consumption of the GPIO bus."""
        ...

    def getI2cBusCurrent(self, unit: CurrentUnit) -> float:
        """Returns the current consumption of the I2C bus."""
        ...

    def getInputVoltage(self, unit: VoltageUnit) -> float:
        """Returns the input (battery) voltage."""
        ...

    def getAuxiliaryVoltage(self, unit: VoltageUnit) -> float:
        """Returns the auxiliary (5V) voltage."""
        ...

    def getTemperature(self, unit: TempUnit) -> float:
        """Returns the module temperature."""
        ...

    def getImuType(self) -> LynxModuleImuType:
        ...

    def setDebug(self, group: LynxModule.DebugGroup, verbosity: LynxModule.DebugVerbosity) -> None:
        ...

    def acquireI2cLockWhile(self, supplier: Supplier[T]) -> T:
        ...

    def acquireNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def releaseNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def sendCommand(self, command: LynxMessage) -> None:
        """Sends a command to the module, scheduling retransmissions as necessary."""
        ...

    def retransmit(self, message: LynxMessage) -> None:
        ...

    def finishedWithMessage(self, message: LynxMessage) -> None:
        ...

    def pretendFinishExtantCommands(self) -> None:
        ...

    def onIncomingDatagramReceived(self, datagram: LynxDatagram) -> None:
        ...

    def abandonUnfinishedCommands(self) -> None:
        ...

    def nackUnfinishedCommands(self) -> None:
        ...

    TAG: str
    blinkerPolicy: LynxModule.BlinkerPolicy
    msInitialContact: int
    msKeepAliveTimeout: int
    moduleStatusPersistentBits: int
    standardMessages: dict[int, LynxModule.MessageClassAndCtor]
    responseClasses: dict[type[LynxCommand], LynxModule.MessageClassAndCtor]
    lynxUsbDevice: LynxUsbDevice
    controllers: list[LynxController]
    addrAndSerialLock: object
    moduleAddress: int
    moduleSerialNumber: SerialNumber
    nextMessageNumber: Any
    isParent_: bool
    isSystemSynthetic_: bool
    isUserModule_: bool
    systemOperationCounter: int
    isEngaged_: bool
    engagementLock: object
    isOpen_: bool
    isNotResponding_: bool
    startStopLock: object
    unfinishedCommands: Any
    """maps message number to command we've issued with said number"""
    commandClasses: Any
    """for all the commands we know about (standard + QueryInterface), maps command number to class which implements same. Only commands known to be supported by the module are populated"""
    supportedCommands: set[type[LynxCommand]]
    interfacesQueried: Any
    i2cLock: object
    """This lock prevents concurrency problems that would arrive from interleaving messages of the (asynchronous) i2c protocol. In particular it makes sure that once we issue a read, we can actually read that data before we get back in there and, say, issue a write on another bus."""
    currentSteps: list[Blinker.Step]
    """State for maintaining stack of blinker patterns"""
    previousSteps: list[list[Blinker.Step]]
    isVisuallyIdentifying: bool
    executor: Any
    pingFuture: Any
    pingFutureLock: object
    moduleStatusFuture: Any
    attentionRequiredPreviously: bool
    previousModuleStatus: int
    moduleStatusLock: object
    ftdiResetWatchdogActive: bool
    ftdiResetWatchdogActiveWhenEngaged: bool
    bulkCachingLock: object
    bulkCachingMode: LynxModule.BulkCachingMode
    bulkCachingHistory: dict[str, list[LynxDekaInterfaceCommand[object]]]
    lastBulkData: LynxModule.BulkData


class LynxModuleWarningManager:
    """Composes system telemetry warnings related to the status of the lynx modules, and logs persistent conditions with configurable throttling."""
    __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager"
    class ConditionStatus:
        """Used for conditions that persist past a singular event"""
        __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager.ConditionStatus"
        def __init__(self, lynxModule: LynxModuleIntf, moduleName: str, logFrequencySeconds: int) -> None:
            ...

        def conditionCurrentlyTrue(self) -> bool:
            ...

        def logCondition(self) -> None:
            ...

        def reportConditionAndLogWithThrottle(self, userOpModeRunning: bool) -> None:
            ...

        def hasChangedSinceLastCheck(self) -> bool:
            ...

        timeSinceConditionLastReported: ElapsedTime
        timeSinceConditionLogged: ElapsedTime
        lynxModule: LynxModuleIntf
        moduleName: str
        logFrequencySeconds: int
        conditionPreviouslyTrue: bool
        conditionTrueDuringOpModeRun: bool

    class UnresponsiveStatus(ConditionStatus):
        __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager.UnresponsiveStatus"
        def conditionCurrentlyTrue(self) -> bool:
            ...

        def logCondition(self) -> None:
            ...

    class LowBatteryStatus(ConditionStatus):
        __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager.LowBatteryStatus"
        def conditionCurrentlyTrue(self) -> bool:
            ...

        def logCondition(self) -> None:
            ...

    class LynxModuleWarningSource(GlobalWarningSource):
        __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager.LynxModuleWarningSource"
        def getGlobalWarning(self) -> str:
            ...

        def shouldTriggerWarningSound(self) -> bool:
            ...

        def composeModuleList(self, moduleNames: list[str], builder: Any) -> None:
            ...

        def suppressGlobalWarning(self, suppress: bool) -> None:
            ...

        def clearGlobalWarning(self) -> None:
            ...

        def setGlobalWarning(self, warning: str) -> None:
            ...

    class WarningManagerOpModeListener(OpModeManagerNotifier.Notifications):
        __java__ = "com.qualcomm.hardware.lynx.LynxModuleWarningManager.WarningManagerOpModeListener"
        def onOpModePreInit(self, opMode: OpMode) -> None:
            ...

        def onOpModePreStart(self, opMode: OpMode) -> None:
            ...

        def onOpModePostStop(self, opMode: OpMode) -> None:
            ...

    @staticmethod
    def getInstance() -> LynxModuleWarningManager:
        ...

    def init(self, opModeManager: OpModeManagerImpl, hardwareMap: HardwareMap) -> None:
        """Called on Robot startup"""
        ...

    def reportModuleUnresponsive(self, module: LynxModule) -> None:
        """Unlike LynxModule#noteNotResponding(), this method should be called repeatedly while the module is unresponsive. This is so that we can keep track of if the module was ever unresponsive while a user OpMode was running."""
        ...

    def reportModuleReset(self, module: LynxModule) -> None:
        ...

    def reportModuleLowBattery(self, module: LynxModule) -> None:
        ...


class LynxNackException(Exception):
    """LynxNackExceptions are thrown in response to the receipt by the host of a 'nack' packet from the module when a command is sent."""
    __java__ = "com.qualcomm.hardware.lynx.LynxNackException"
    @overload
    def __init__(self, command: LynxRespondable, message: str) -> None:
        ...
    @overload
    def __init__(self, command: LynxRespondable, format: str, *args: object) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def wrap(self) -> RobotCoreException:
        ...

    def getCommand(self) -> LynxRespondable:
        ...

    def getNack(self) -> LynxNack:
        ...


class LynxPwmOutputController(LynxController, PWMOutputController, PWMOutputControllerEx):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.hardware.lynx.LynxPwmOutputController"
    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def initializeHardware(self) -> None:
        ...

    def floatHardware(self) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def setPulseWidthOutputTime(self, port: int, usDuration: int) -> None:
        ...

    def internalSetPulseWidthOutputTime(self, portZ: int, usDuration: int) -> None:
        ...

    def setPulseWidthPeriod(self, port: int, usPeriod: int) -> None:
        ...

    def internalSetPulseWidthPeriod(self, portZ: int, usPeriod: int) -> None:
        ...

    def getPulseWidthOutputTime(self, port: int) -> int:
        ...

    def getPulseWidthPeriod(self, port: int) -> int:
        ...

    def setPwmEnable(self, port: int) -> None:
        ...

    def setPwmDisable(self, port: int) -> None:
        ...

    def isPwmEnabled(self, port: int) -> bool:
        ...

    TAG: str
    apiPortFirst: int
    apiPortLast: int
    lastKnownOutputTimes: list[LastKnown[int]]
    lastKnownPulseWidthPeriods: list[LastKnown[int]]


class LynxServoController(LynxController, ServoControllerEx):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.hardware.lynx.LynxServoController"
    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def initializeHardware(self) -> None:
        ...

    def floatHardware(self) -> None:
        ...

    def forgetLastKnown(self) -> None:
        ...

    def forgetLastKnownPosition(self, servo: int) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def pwmEnable(self) -> None:
        ...

    def pwmDisable(self) -> None:
        ...

    def getPwmStatus(self) -> ServoController.PwmStatus:
        ...

    def setServoPwmEnable(self, servo: int) -> None:
        ...

    def setServoPwmDisable(self, servo: int) -> None:
        ...

    def isServoPwmEnabled(self, servo: int) -> bool:
        ...

    def setServoType(self, servo: int, servoType: ServoConfigurationType) -> None:
        ...

    def setServoPosition(self, servo: int, position: float) -> None:
        ...

    def getServoPosition(self, servo: int) -> float:
        ...

    def setServoPwmRange(self, servo: int, range: PwmControl.PwmRange) -> None:
        ...

    def getServoPwmRange(self, servo: int) -> PwmControl.PwmRange:
        ...

    def setPulseWidth(self, servo: int, usWidth: float) -> None:
        ...

    def getPulseWidth(self, servo: int) -> float:
        ...

    def internalSetPulseWidth(self, servo: int, usWidth: int) -> None:
        ...

    def internalGetPulseWidth(self, servo: int) -> int:
        ...

    TAG: str
    apiServoFirst: int
    apiServoLast: int
    apiPositionFirst: float
    apiPositionLast: float
    lastKnownCommandedPosition: list[LastKnown[float]]
    lastKnownEnabled: list[LastKnown[bool]]
    pwmRanges: list[PwmControl.PwmRange]
    defaultPwmRanges: list[PwmControl.PwmRange]
    lastKnownPulseWidthMicroseconds: list[LastKnown[int]]


class LynxUnsupportedCommandException(Exception):
    """Created by bob on 2/6/2017."""
    __java__ = "com.qualcomm.hardware.lynx.LynxUnsupportedCommandException"
    def __init__(self, module: LynxModule, lynxMessage: LynxMessage) -> None:
        ...

    def getCommandNumber(self) -> int:
        ...

    def getClazz(self) -> type[LynxMessage]:
        ...

    def getLynxModule(self) -> LynxModuleIntf:
        ...


class SyncdDevice:
    """SyncdDevice is for a device that wants to be in sync with the event loop. If there is sync'd device registered with the event loop manager then the event loop manager will run the event loop in this manner:"""
    __java__ = "com.qualcomm.robotcore.eventloop.SyncdDevice"
    class ShutdownReason(enum.Enum):
        """ShutdownReason indicates the health of the shutdown of the device."""
        __java__ = "com.qualcomm.robotcore.eventloop.SyncdDevice.ShutdownReason"
        NORMAL = enum.auto()
        ABNORMAL = enum.auto()
        ABNORMAL_ATTEMPT_REOPEN = enum.auto()

    class Manager:
        __java__ = "com.qualcomm.robotcore.eventloop.SyncdDevice.Manager"
        def registerSyncdDevice(self, device: SyncdDevice) -> None:
            ...

        def unregisterSyncdDevice(self, device: SyncdDevice) -> None:
            ...

    def getShutdownReason(self) -> SyncdDevice.ShutdownReason:
        """Has this device shutdown abnormally? Note that even if this method returns true that a close() will still be necessary to fully clean up associated resources."""
        ...

    def setOwner(self, owner: RobotUsbModule) -> None:
        """Records the owning module of this sync'd device. The owner of the device is the party that is responsible for the device's lifetime management, and thus who should be involved if the device experiences problems and needs to be shutdown or restarted."""
        ...

    def getOwner(self) -> RobotUsbModule:
        """Retrieves the owning module of this sync'd device."""
        ...

    msAbnormalReopenInterval: int
    """When a device shuts down with ShutdownReason#ABNORMAL_ATTEMPT_REOPEN, this is the recommended duration of time to wait before attempting reopen. It was only heuristically determined, and might thus perhaps be shortened"""


class RobotUsbModule(RobotArmingStateNotifier):
    """This interface can be used to control the activeness or aliveness of an object that controls a piece of hardware such as a motor or servo controller. The object can be transitioned amongst a series of states in which various degrees of functionality are available. The states are as follows: armed: the object controlling the hardware is fully functional in its intended, usual way. In this state, the object 'owns' full control of the hardware it represents. disarmed: the object is quiescent, not manipulating or controlling the hardware. In this state, it is conceivable that some *other* object instance might be created and then be successfully armed on the same underlying hardware. In contrast, it is not expected that two object instances may be simultaneously armed against the same piece of hardware. pretending: the object pretends as best it can to act as if it were armed on an actual underlying piece of hardware, but in reality the object is just making it all up: writes may be sent to the bit-bucket, reads might always return zeros, and so on. Though this may sound odd, having a hardware-controlling object function in this mode might minimize impact on upper software layers in the event that the desired actual hardware is disconnected or otherwise unavailable. closed: this is much like disarmed, but more serious and permanent shutdown steps might be taken as an object transitions to the closed state. Transient 'toX' states are also present. The legal state transitions are as follows: disarmed -&gt; toArmed toArmed -&gt; armed disarmed -&gt; toPretending toPretending -&gt; pretending armed -&gt; toDisarmed toArmed -&gt; toDisarmed pretending -&gt; toDisarmed toPretending -&gt; toDisarmed toDisarmed -&gt; disarmed armed -&gt; closed toArmed -&gt; closed pretending -&gt; closed toPretending -&gt; closed toDisarmed -&gt; closed disarmed -&gt; closed Notice that once closed, no further state transitions are possible. Conversely, it is possible to close from any state and to disarm from any state except from closed. In particular, it is possible to close or disarm from the transitional toArmed and toPretending states: implementations *must* take care to ensure this is always possible. Typically, when first instantiated, an object is in the disarmed state. Objects should, generally, minimize the time they are in the disarmed state, as to many clients they will appear dysfunctional and error prone in that state, since those clients may not have been coded correctly to deal with an object that doesn't service read()s or write()s *at*all*."""
    __java__ = "com.qualcomm.robotcore.hardware.usb.RobotUsbModule"
    def arm(self) -> None:
        """Causes the module to attempt to enter the armed state. If the module is already armed, this method has no effect."""
        ...

    def pretend(self) -> None:
        """Causes the module to attempt to enter the pretending state. If the module is already pretending, this method has no effect."""
        ...

    def armOrPretend(self) -> None:
        """Causes the module to attempt to enter the armed state, but if that is not possible, to enter the pretending state."""
        ...

    def disarm(self) -> None:
        """Causes the module to attempt to enter the disarmed state. If the module is already disarmed, this method has no effect."""
        ...

    def close(self) -> None:
        """Causes the module to attempt to enter the closed state. If the module is already closed, this method has no effect."""
        ...


class LynxUsbDevice(RobotUsbModule, GlobalWarningSource, RobotCoreLynxUsbDevice, HardwareDevice, SyncdDevice, Engagable):
    """The working interface to Lynx USB Devices. Separating out the interface like this allows us to create delegators where we need to."""
    __java__ = "com.qualcomm.hardware.lynx.LynxUsbDevice"
    class SystemOperationHandle:
        __java__ = "com.qualcomm.hardware.lynx.LynxUsbDevice.SystemOperationHandle"
        def __init__(self, lynxUsb: Any, module: LynxModule, parentModule: LynxModule) -> None:
            """ONLY to be called by LynxUsbDeviceImpl#keepConnectedModuleAliveForSystemOperations(int,"""
            ...

        def performSystemOperation(self, operation: Consumer[LynxModule], timeout: int, timeoutUnit: Any) -> None:
            """The operation will run on a background thread, but this method will not return until the operation has completed."""
            ...

        def close(self) -> None:
            """Allow the module associated with this handle (and its parent) to close if there are no other users of it"""
            ...

        def getLynxModuleSerialNumber(self) -> SerialNumber:
            ...

        def wrapsModule(self, module: LynxModule) -> bool:
            ...

        def wrapsSameModule(self, otherHandle: LynxUsbDevice.SystemOperationHandle) -> bool:
            ...

        lynxUsb: Any
        module: LynxModule
        parentModule: LynxModule
        closed: bool

    def getRobotUsbDevice(self) -> RobotUsbDevice:
        ...

    def isSystemSynthetic(self) -> bool:
        ...

    def setSystemSynthetic(self, systemSynthetic: bool) -> None:
        ...

    def failSafe(self) -> None:
        ...

    def changeModuleAddress(self, module: LynxModule, oldAddress: int, runnable: Any) -> None:
        ...

    def getOrAddModule(self, moduleDescription: LynxModuleDescription) -> LynxModule:
        ...

    def removeConfiguredModule(self, module: LynxModule) -> None:
        """Should ONLY be called by LynxModule.close()"""
        ...

    def noteMissingModule(self, moduleAddress: int, moduleName: str) -> None:
        ...

    def performSystemOperationOnParentModule(self, parentAddress: int, operation: Consumer[LynxModule], timeout: int, timeoutUnit: Any) -> None:
        """The operation will run on a background thread, but this method will not return until the operation has completed."""
        ...

    def performSystemOperationOnConnectedModule(self, moduleAddress: int, parentAddress: int, operation: Consumer[LynxModule], timeout: int, timeoutUnit: Any) -> None:
        """The operation will run on a background thread, but this method will not return until the operation has completed."""
        ...

    def keepConnectedModuleAliveForSystemOperations(self, moduleAddress: int, parentAddress: int) -> LynxUsbDevice.SystemOperationHandle:
        """Open a SystemOperationHandle that will allow you to keep the LynxModule open for an unbounded length of time."""
        ...

    def discoverModules(self, checkForImus: bool) -> LynxModuleMetaList:
        ...

    def acquireNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def releaseNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def transmit(self, message: LynxMessage) -> None:
        ...

    def setupControlHubEmbeddedModule(self) -> bool:
        ...

    def getDelegationTarget(self) -> Any:
        ...

    def updateFirmware(self, image: RobotCoreCommandList.FWImage, requestId: str, progressConsumer: Consumer[ProgressParameters]) -> RobotCoreCommandList.LynxFirmwareUpdateResp:
        ...


class LynxUsbDeviceDelegate(LynxUsbDevice, HardwareDeviceCloseOnTearDown):
    """This delegation class simply forwards calls on, with the single exception that it turns a local close into a delegated reference count."""
    __java__ = "com.qualcomm.hardware.lynx.LynxUsbDeviceDelegate"
    def __init__(self, lynxUsbDevice: Any) -> None:
        ...

    def getDelegationTarget(self) -> Any:
        ...

    def close(self) -> None:
        ...

    def assertOpen(self) -> None:
        ...

    def disengage(self) -> None:
        ...

    def engage(self) -> None:
        ...

    def isEngaged(self) -> bool:
        ...

    def getRobotUsbDevice(self) -> RobotUsbDevice:
        ...

    def isSystemSynthetic(self) -> bool:
        ...

    def setSystemSynthetic(self, systemSynthetic: bool) -> None:
        ...

    def failSafe(self) -> None:
        ...

    def lockNetworkLockAcquisitions(self) -> None:
        ...

    def setThrowOnNetworkLockAcquisition(self, shouldThrow: bool) -> None:
        ...

    def changeModuleAddress(self, module: LynxModule, newAddress: int, runnable: Any) -> None:
        ...

    def noteMissingModule(self, moduleAddress: int, moduleName: str) -> None:
        ...

    def performSystemOperationOnParentModule(self, parentAddress: int, operation: Consumer[LynxModule], timeout: int, timeoutUnit: Any) -> None:
        ...

    def performSystemOperationOnConnectedModule(self, moduleAddress: int, parentAddress: int, operation: Consumer[LynxModule], timeout: int, timeoutUnit: Any) -> None:
        ...

    def keepConnectedModuleAliveForSystemOperations(self, moduleAddress: int, parentAddress: int) -> LynxUsbDevice.SystemOperationHandle:
        ...

    def getOrAddModule(self, moduleDescription: LynxModuleDescription) -> LynxModule:
        ...

    def removeConfiguredModule(self, module: LynxModule) -> None:
        ...

    def discoverModules(self, checkForImus: bool) -> LynxModuleMetaList:
        ...

    def acquireNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def releaseNetworkTransmissionLock(self, message: LynxMessage) -> None:
        ...

    def transmit(self, message: LynxMessage) -> None:
        ...

    def setupControlHubEmbeddedModule(self) -> bool:
        ...

    def updateFirmware(self, image: RobotCoreCommandList.FWImage, requestId: str, progressConsumer: Consumer[ProgressParameters]) -> RobotCoreCommandList.LynxFirmwareUpdateResp:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def getShutdownReason(self) -> SyncdDevice.ShutdownReason:
        ...

    def setOwner(self, owner: RobotUsbModule) -> None:
        ...

    def getOwner(self) -> RobotUsbModule:
        ...

    def getSerialNumber(self) -> SerialNumber:
        ...

    def getArmingState(self) -> RobotArmingStateNotifier.ARMINGSTATE:
        ...

    def registerCallback(self, callback: RobotArmingStateNotifier.Callback, doInitialCallback: bool) -> None:
        ...

    def unregisterCallback(self, callback: RobotArmingStateNotifier.Callback) -> None:
        ...

    def arm(self) -> None:
        ...

    def pretend(self) -> None:
        ...

    def armOrPretend(self) -> None:
        ...

    def disarm(self) -> None:
        ...

    def getGlobalWarning(self) -> str:
        ...

    def shouldTriggerWarningSound(self) -> bool:
        ...

    def suppressGlobalWarning(self, suppress: bool) -> None:
        ...

    def setGlobalWarning(self, warning: str) -> None:
        ...

    def clearGlobalWarning(self) -> None:
        ...

    TAG: str
    delegate: Any
    releaseOnClose: bool
    isOpen: bool


class LynxUsbUtil:
    """Created by bob on 2016-03-16."""
    __java__ = "com.qualcomm.hardware.lynx.LynxUsbUtil"
    class Placeholder(Generic[T]):
        """A simple utility that helps us understand when we're using placeholders. We don't log all the time for fear of swamping the log"""
        __java__ = "com.qualcomm.hardware.lynx.LynxUsbUtil.Placeholder"
        def __init__(self, tag: str, format: str, *args: object) -> None:
            ...

        def reset(self) -> None:
            ...

        def log(self, t: T) -> T:
            ...

    @staticmethod
    def openUsbDevice(doScan: bool, robotUsbManager: RobotUsbManager, serialNumber: SerialNumber) -> RobotUsbDevice:
        ...

    @staticmethod
    def makePlaceholderValue(t: T) -> T:
        """Documents that the value being passed is a dummy, placeholder value which is being returned from a function in lieu of something more reasonable actually being available."""
        ...


class LynxVoltageSensor(LynxController, VoltageSensor):
    """Created by bob on 2016-03-12."""
    __java__ = "com.qualcomm.hardware.lynx.LynxVoltageSensor"
    def __init__(self, context: Any, module: LynxModule) -> None:
        ...

    def getTag(self) -> str:
        ...

    def getDeviceName(self) -> str:
        ...

    def getVoltage(self) -> float:
        ...

    TAG: str


class MessageKeyedLock:
    """MessageKeyedLock is a recursively-acquirable lock that is keyed by a LynxMessage"""
    __java__ = "com.qualcomm.hardware.lynx.MessageKeyedLock"
    @overload
    def __init__(self, name: str) -> None:
        ...
    @overload
    def __init__(self, name: str, msAquisitionTimeout: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def reset(self) -> None:
        ...

    def acquire(self, message: LynxMessage) -> None:
        ...

    def release(self, message: LynxMessage) -> None:
        ...

    def lockAcquisitions(self) -> None:
        ...

    def throwOnLockAcquisitions(self, shouldthrow: bool) -> None:
        ...


class Supplier(Generic[T]):
    """Represents a supplier of results. There is no requirement that a new or distinct result be returned each time the supplier is invoked. This is a functional interface whose functional method is get()."""
    __java__ = "com.qualcomm.hardware.lynx.Supplier"
    def get(self) -> T:
        ...


class MaxSonarI2CXL(I2cDeviceSynchDevice[I2cDeviceSynch]):
    __java__ = "com.qualcomm.hardware.maxbotix.MaxSonarI2CXL"
    def __init__(self, deviceClient: I2cDeviceSynch) -> None:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def doInitialize(self) -> bool:
        ...

    def getDeviceName(self) -> str:
        ...

    def ping(self) -> None:
        """Commands the sensor to send out a ping"""
        ...

    def getRangingResult(self, units: DistanceUnit) -> float:
        """Reads the range of the last commanded measurement from the sensor"""
        ...

    @overload
    def getDistanceSync(self, units: DistanceUnit) -> float:
        """Commands the sensor to send out a ping, sleeps for the default sonar propagation delay, and then reads the result of the measurement just commanded"""
        ...
    @overload
    def getDistanceSync(self, sonarPropagationDelayMs: int, units: DistanceUnit) -> float:
        """Commands the sensor to send out a ping, sleeps for the time specified by the sonarPropagationDelay, and then reads the result of the measurement just commanded"""
        ...
    def getDistanceSync(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getDistanceAsync(self, units: DistanceUnit) -> float:
        """Commands the sensor to send out a ping if the default delay has expired, and then reads the result of the measurement just commanded. If the delay has NOT expired, then the last value read from the sensor will be returned instead."""
        ...
    @overload
    def getDistanceAsync(self, sonarPropagationDelayMs: int, units: DistanceUnit) -> float:
        """Commands the sensor to send out a ping if the delay specified has expired, and then reads the result of the measurement just commanded. If the delay has NOT expired, then the last value read from the sensor will be returned instead."""
        ...
    def getDistanceAsync(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setI2cAddress(self, i2cAddr: I2cAddr) -> None:
        """Sets the I2C address the SDK should use when attempting to communicate with the sensor. Note that this method will NOT actually change the address inside the sensor, for that see writeI2cAddrToSensorEEPROM(byte addr). If the aforementioned method is used to change the address inside the sensor, then you will need to call this method after getting the object from the hardwareMap, and pass in the same address as you wrote to the sensor's EEPROM. Note that you will need to call this method once at the beginning of each of your opmodes after you get the object from the hwMap, whereas you only need to call the method that writes to the sensor's EEPROM, once, ever. As in you only need to use that when you are initially wiring up the sensor."""
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def writeI2cAddrToSensorEEPROM(self, addr: int) -> None:
        """Tells the sensor that it should operate on an I2C address other than the default, and then writes that address to the internal EEPROM so that it is retained across a power cycle. You only need to call this method ONE TIME, EVER. (Unless you want to change the address again, that is) Note that the sensor will only accept even numbered address values. If an odd numbered address is sent, then the address will be set to the next lowest even number. Also, the following addresses are invalid, and if sent, the command will be ignored: 0x00 0x50 0xA4 0xAA"""
        ...

    DEFAULT_I2C_ADDR: int
    CHANGE_I2C_ADDR_UNLOCK_1: int
    CHANGE_I2C_ADDR_UNLOCK_2: int
    CMD_PING: int
    NUM_RANGE_BYTES: int
    DEFAULT_SONAR_PROPAGATION_DELAY_MS: int
    lastDistance: float
    lastPingTime: int


class ModernRoboticsAnalogOpticalDistanceSensor(OpticalDistanceSensor, AnalogSensor):
    """ModernRoboticsAnalogOpticalDistanceSensor supports the Modern Robotics Optical Distance Sensor."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsAnalogOpticalDistanceSensor"
    def __init__(self, analogInputController: AnalogInputController, physicalPort: int) -> None:
        ...

    def toString(self) -> str:
        ...

    def getLightDetected(self) -> float:
        ...

    def getMaxVoltage(self) -> float:
        ...

    def getRawLightDetected(self) -> float:
        ...

    def getRawLightDetectedMax(self) -> float:
        ...

    def readRawVoltage(self) -> float:
        ...

    def enableLed(self, enable: bool) -> None:
        ...

    def status(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    apiLevelMin: float
    apiLevelMax: float


class ModernRoboticsI2cColorSensor(I2cDeviceSynchDevice[I2cDeviceSynch], ColorSensor, NormalizedColorSensor, SwitchableLight, I2cAddrConfig):
    """ModernRoboticsI2cColorSensor provides support for the Modern Robotics Color Sensor."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cColorSensor"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cColorSensor.Register"
        FIRMWARE_REV = enum.auto()
        MANUFACTURE_CODE = enum.auto()
        SENSOR_ID = enum.auto()
        COMMAND = enum.auto()
        COLOR_NUMBER = enum.auto()
        RED = enum.auto()
        GREEN = enum.auto()
        BLUE = enum.auto()
        ALPHA = enum.auto()
        COLOR_INDEX = enum.auto()
        RED_INDEX = enum.auto()
        GREEN_INDEX = enum.auto()
        BLUE_INDEX = enum.auto()
        RED_READING = enum.auto()
        GREEN_READING = enum.auto()
        BLUE_READING = enum.auto()
        ALPHA_READING = enum.auto()
        NORMALIZED_RED_READING = enum.auto()
        NORMALIZED_GREEN_READING = enum.auto()
        NORMALIZED_BLUE_READING = enum.auto()
        NORMALIZED_ALPHA_READING = enum.auto()
        READ_WINDOW_FIRST = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        bVal: int

    class Command(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cColorSensor.Command"
        ACTIVE_LED = enum.auto()
        PASSIVE_LED = enum.auto()
        HZ50 = enum.auto()
        HZ60 = enum.auto()
        CALIBRATE_BLACK = enum.auto()
        CALIBRATE_WHITE = enum.auto()
        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def read8(self, reg: ModernRoboticsI2cColorSensor.Register) -> int:
        ...

    def write8(self, reg: ModernRoboticsI2cColorSensor.Register, value: int) -> None:
        ...

    def readUnsignedByte(self, register: ModernRoboticsI2cColorSensor.Register) -> int:
        ...

    def readUnsignedShort(self, register: ModernRoboticsI2cColorSensor.Register) -> int:
        ...

    def writeCommand(self, command: ModernRoboticsI2cColorSensor.Command) -> None:
        ...

    def toString(self) -> str:
        ...

    def red(self) -> int:
        ...

    def green(self) -> int:
        ...

    def blue(self) -> int:
        ...

    def alpha(self) -> int:
        ...

    def argb(self) -> int:
        ...

    def getNormalizedColors(self) -> NormalizedRGBA:
        ...

    def getGain(self) -> float:
        ...

    def setGain(self, newGain: float) -> None:
        ...

    def enableLed(self, enable: bool) -> None:
        ...

    def enableLight(self, enable: bool) -> None:
        ...

    def isLightOn(self) -> bool:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr
    colorNormalizationFactor: float
    """In NormalizedColorSensor we report the 16-bit sensor-normalized values, not the 8 bit colors reported through ColorSensor."""
    isLightOn_: bool


class ModernRoboticsI2cCompassSensor(I2cDeviceSynchDevice[I2cDeviceSynch], CompassSensor, I2cAddrConfig):
    """ModernRoboticsI2cCompassSensor implements support for the Modern Robotics compass sensor. \"During normal operation the LED will blink briefly at 1Hz. During Hard Iron Calibration the LED will blink at 1/2Hz. During tilt up and tilt down calibration the LED will be on during a period of calibration measurement.\""""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cCompassSensor"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cCompassSensor.Register"
        READ_WINDOW_FIRST = enum.auto()
        FIRMWARE_REV = enum.auto()
        MANUFACTURE_CODE = enum.auto()
        SENSOR_ID = enum.auto()
        COMMAND = enum.auto()
        HEADING = enum.auto()
        ACCELX = enum.auto()
        ACCELY = enum.auto()
        ACCELZ = enum.auto()
        MAGX = enum.auto()
        MAGY = enum.auto()
        MAGZ = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        ACCELX_OFFSET = enum.auto()
        ACCELY_OFFSET = enum.auto()
        ACCELZ_OFFSET = enum.auto()
        MAGX_OFFSET = enum.auto()
        MAGY_OFFSET = enum.auto()
        MAGZ_OFFSET = enum.auto()
        MAG_TILT_COEFF = enum.auto()
        ACCEL_SCALE_COEFF = enum.auto()
        MAG_SCALE_COEFF_X = enum.auto()
        MAG_SCALE_COEFF_Y = enum.auto()
        UNKNOWN = enum.auto()
        bVal: int

    class Command(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cCompassSensor.Command"
        NORMAL = enum.auto()
        CALIBRATE_IRON = enum.auto()
        ACCEL_NULL_X = enum.auto()
        ACCEL_NULL_Y = enum.auto()
        ACCEL_NULL_Z = enum.auto()
        ACCEL_GAIN_ADJUST = enum.auto()
        MEASURE_TILT_UP = enum.auto()
        MEASURE_TILT_DOWN = enum.auto()
        WRITE_EEPROM = enum.auto()
        CALIBRATION_FAILED = enum.auto()
        UNKNOWN = enum.auto()
        @staticmethod
        def fromByte(b: int) -> ModernRoboticsI2cCompassSensor.Command:
            ...

        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def setOptimalReadWindow(self) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def read8(self, reg: ModernRoboticsI2cCompassSensor.Register) -> int:
        ...

    def write8(self, reg: ModernRoboticsI2cCompassSensor.Register, value: int) -> None:
        ...

    def readShort(self, reg: ModernRoboticsI2cCompassSensor.Register) -> int:
        ...

    def writeShort(self, reg: ModernRoboticsI2cCompassSensor.Register, value: int) -> None:
        ...

    def writeCommand(self, command: ModernRoboticsI2cCompassSensor.Command) -> None:
        ...

    def readCommand(self) -> ModernRoboticsI2cCompassSensor.Command:
        ...

    def getAcceleration(self) -> Acceleration:
        ...

    def getMagneticFlux(self) -> MagneticFlux:
        ...

    def getDirection(self) -> float:
        ...

    def status(self) -> str:
        ...

    def isCalibrating(self) -> bool:
        ...

    def calibrationFailed(self) -> bool:
        ...

    def setMode(self, mode: CompassSensor.CompassMode) -> None:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr


class ModernRoboticsI2cGyro(I2cDeviceSynchDevice[I2cDeviceSynch], GyroSensor, IntegratingGyroscope, I2cAddrConfig):
    """ModernRoboticsI2cGyro supports the Modern Robotics integrating gyro. This sensor contains an L3GD20 MEMS three-axis digital output gyroscope. Internally, the chip is labelled (e.g.) \"AGD2 2437 JR4IJ\"."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cGyro"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cGyro.Register"
        READ_WINDOW_FIRST = enum.auto()
        FIRMWARE_REV = enum.auto()
        MANUFACTURE_CODE = enum.auto()
        SENSOR_ID = enum.auto()
        COMMAND = enum.auto()
        HEADING_DATA = enum.auto()
        INTEGRATED_Z_VALUE = enum.auto()
        RAW_X_VAL = enum.auto()
        RAW_Y_VAL = enum.auto()
        RAW_Z_VAL = enum.auto()
        Z_AXIS_OFFSET = enum.auto()
        Z_AXIS_SCALE_COEF = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        UNKNOWN = enum.auto()
        @staticmethod
        def fromByte(bVal: int) -> ModernRoboticsI2cGyro.Register:
            ...

        bVal: int

    class Command(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cGyro.Command"
        NORMAL = enum.auto()
        CALIBRATE = enum.auto()
        RESET_Z_AXIS = enum.auto()
        WRITE_EEPROM = enum.auto()
        UNKNOWN = enum.auto()
        @staticmethod
        def fromByte(bVal: int) -> ModernRoboticsI2cGyro.Command:
            ...

        bVal: int

    class HeadingMode(enum.Enum):
        """HeadingMode can be used to configure the software to return either cartesian or cardinal headings."""
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cGyro.HeadingMode"
        HEADING_CARTESIAN = enum.auto()
        HEADING_CARDINAL = enum.auto()

    class MeasurementMode(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cGyro.MeasurementMode"
        GYRO_CALIBRATION_PENDING = enum.auto()
        GYRO_CALIBRATING = enum.auto()
        GYRO_NORMAL = enum.auto()

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def setOptimalReadWindow(self) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def read8(self, reg: ModernRoboticsI2cGyro.Register) -> int:
        ...

    def write8(self, reg: ModernRoboticsI2cGyro.Register, value: int) -> None:
        ...

    def readShort(self, reg: ModernRoboticsI2cGyro.Register) -> int:
        ...

    def writeShort(self, reg: ModernRoboticsI2cGyro.Register, value: int) -> None:
        ...

    def writeCommand(self, command: ModernRoboticsI2cGyro.Command) -> None:
        ...

    def readCommand(self) -> ModernRoboticsI2cGyro.Command:
        ...

    def getAngularVelocityAxes(self) -> set[Axis]:
        ...

    def getAngularOrientationAxes(self) -> set[Axis]:
        ...

    def getAngularVelocity(self, unit: AngleUnit) -> AngularVelocity:
        ...

    def getAngularOrientation(self, reference: AxesReference, order: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def setHeadingMode(self, headingMode: ModernRoboticsI2cGyro.HeadingMode) -> None:
        ...

    def getHeadingMode(self) -> ModernRoboticsI2cGyro.HeadingMode:
        ...

    def rawX(self) -> int:
        """\"Gyro Raw Values: The three fields X, Y and Z are the unprocessed values being obtained from the sensor element. These values are updated at approximately 760Hz.\""""
        ...

    def rawY(self) -> int:
        ...

    def rawZ(self) -> int:
        ...

    def getZAxisOffset(self) -> int:
        ...

    def setZAxisOffset(self, offset: int) -> None:
        ...

    def getZAxisScalingCoefficient(self) -> int:
        ...

    def setZAxisScalingCoefficient(self, zAxisScalingCoefficient: int) -> None:
        ...

    def getIntegratedZValue(self) -> int:
        ...

    def getHeading(self) -> int:
        ...

    def truncate(self, angle: float) -> int:
        ...

    def normalize0359(self, degrees: float) -> float:
        ...

    def degreesZFromIntegratedZ(self, integratedZ: int) -> float:
        ...

    def resetZAxisIntegrator(self) -> None:
        ...

    def status(self) -> str:
        ...

    def calibrate(self) -> None:
        ...

    def isCalibrating(self) -> bool:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def getRotationFraction(self) -> float:
        ...

    def getMeasurementMode(self) -> ModernRoboticsI2cGyro.MeasurementMode:
        """This provides little useful utility beyond #isCalibrating()"""
        ...

    def notSupported(self) -> None:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr
    degreesPerSecondPerDigit: float
    headingMode: ModernRoboticsI2cGyro.HeadingMode
    degreesPerZAxisTick: float


class ModernRoboticsI2cIrSeekerSensorV3(I2cDeviceSynchDevice[I2cDeviceSynch], IrSeekerSensor, I2cAddrConfig):
    """ModernRoboticsI2cIrSeekerSensorV3 supports the Modern Robotics IR Seeker V3."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cIrSeekerSensorV3"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cIrSeekerSensorV3.Register"
        READ_WINDOW_FIRST = enum.auto()
        FIRMWARE_REV = enum.auto()
        MANUFACTURE_CODE = enum.auto()
        SENSOR_ID = enum.auto()
        UNUSED = enum.auto()
        DIR_DATA_1200 = enum.auto()
        SIGNAL_STRENTH_1200 = enum.auto()
        DIR_DATA_600 = enum.auto()
        SIGNAL_STRENTH_600 = enum.auto()
        LEFT_SIDE_DATA_1200 = enum.auto()
        RIGHT_SIDE_DATA_1200 = enum.auto()
        LEFT_SIDE_DATA_600 = enum.auto()
        RIGHT_SIDE_DATA_600 = enum.auto()
        READ_WINDOW_LAST = enum.auto()
        UNKNOWN = enum.auto()
        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def setOptimalReadWindow(self) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def read8(self, reg: ModernRoboticsI2cIrSeekerSensorV3.Register) -> int:
        ...

    def write8(self, reg: ModernRoboticsI2cIrSeekerSensorV3.Register, value: int) -> None:
        ...

    def readShort(self, reg: ModernRoboticsI2cIrSeekerSensorV3.Register) -> int:
        ...

    def toString(self) -> str:
        ...

    def setSignalDetectedThreshold(self, threshold: float) -> None:
        ...

    def getSignalDetectedThreshold(self) -> float:
        ...

    def setMode(self, mode: IrSeekerSensor.Mode) -> None:
        ...

    def getMode(self) -> IrSeekerSensor.Mode:
        ...

    def signalDetected(self) -> bool:
        ...

    def getAngle(self) -> float:
        ...

    def getStrength(self) -> float:
        ...

    def getIndividualSensors(self) -> list[IrSeekerSensor.IrSeekerIndividualSensor]:
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr
    MAX_SENSOR_STRENGTH: float
    mode: IrSeekerSensor.Mode
    signalDetectedThreshold: float


class ModernRoboticsI2cRangeSensor(I2cDeviceSynchDevice[I2cDeviceSynch], DistanceSensor, OpticalDistanceSensor, I2cAddrConfig):
    """ModernRoboticsI2cRangeSensor implements support for the MR ultrasonic/optical combo range sensor."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cRangeSensor"
    class Register(enum.Enum):
        __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsI2cRangeSensor.Register"
        FIRST = enum.auto()
        FIRMWARE_REV = enum.auto()
        MANUFACTURE_CODE = enum.auto()
        SENSOR_ID = enum.auto()
        ULTRASONIC = enum.auto()
        OPTICAL = enum.auto()
        LAST = enum.auto()
        UNKNOWN = enum.auto()
        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def setOptimalReadWindow(self) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getDistance(self, unit: DistanceUnit) -> float:
        """Returns a calibrated, linear sense of distance as read by the infrared proximity part of the sensor. Distance is measured to the plastic housing at the front of the sensor. The manufacturer states that the optical readings decay exponentially. This was a surprise, as optical sensors usually decay with an inverse square law. However, both forms were fitted, and the the exponential form produced better results. Accordingly, exponential parameters have been fitted to turn the reported reading into a linear measure of distance. The function fitted was of the form: rawOptical == a + b exp(c cm - d) This fitted linearity is fairly accurate over a range of target surfaces, but is ultimately affected by the reflectivity of the surface. However, even on surfaces where there is significantly different reflectivity, the linearity calculated here tends to be preserved, so distance accuracy can often be refined with a simple further multiplicative scaling. Note that readings are most accurate when perpendicular to the surface. For non-perpendicularity, a cosine correction factor is usually appropriate."""
        ...

    def cmFromOptical(self, rawOptical: int) -> float:
        """Converts a raw optical inverse-square reading into a fitted, calibrated linear reading in cm."""
        ...

    def cmUltrasonic(self) -> float:
        ...

    def cmOptical(self) -> float:
        ...

    def getLightDetected(self) -> float:
        ...

    def getRawLightDetected(self) -> float:
        ...

    def getRawLightDetectedMax(self) -> float:
        ...

    def enableLed(self, enable: bool) -> None:
        ...

    def status(self) -> str:
        ...

    def rawUltrasonic(self) -> int:
        """Returns the raw reading on the ultrasonic sensor"""
        ...

    def rawOptical(self) -> int:
        """Returns the raw reading on the optical sensor"""
        ...

    def setI2cAddress(self, newAddress: I2cAddr) -> None:
        ...

    def getI2cAddress(self) -> I2cAddr:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def read8(self, reg: ModernRoboticsI2cRangeSensor.Register) -> int:
        ...

    @overload
    def write8(self, reg: ModernRoboticsI2cRangeSensor.Register, value: int) -> None:
        ...
    @overload
    def write8(self, reg: ModernRoboticsI2cRangeSensor.Register, value: int, waitControl: I2cWaitControl) -> None:
        ...
    def write8(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def readUnsignedByte(self, reg: ModernRoboticsI2cRangeSensor.Register) -> int:
        ...

    ADDRESS_I2C_DEFAULT: I2cAddr
    apiLevelMin: float
    apiLevelMax: float
    aParam: float
    """Experimentally determined constants for converting optical measurements to distance."""
    bParam: float
    cParam: float
    dParam: float
    rawOpticalMinValid: int
    cmUltrasonicMax: int


class ModernRoboticsTouchSensor(TouchSensor):
    """ModernRoboticsTouchSensor is the driver for a Modern Robotics Touch Sensor. This can operate on either a DigitalChannelController or on an AnalogInputController."""
    __java__ = "com.qualcomm.hardware.modernrobotics.ModernRoboticsTouchSensor"
    @overload
    def __init__(self, digitalController: DigitalChannelController, physicalPort: int) -> None:
        ...
    @overload
    def __init__(self, analogController: AnalogInputController, physicalPort: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def isDigital(self) -> bool:
        ...

    def isAnalog(self) -> bool:
        ...

    def getAnalogVoltageThreshold(self) -> float:
        ...

    def setAnalogVoltageThreshold(self, threshold: float) -> None:
        ...

    def toString(self) -> str:
        ...

    def getValue(self) -> float:
        ...

    def isPressed(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...


class GoBILDA5201Series:
    __java__ = "com.qualcomm.hardware.motors.GoBILDA5201Series"


class GoBILDA5202Series:
    __java__ = "com.qualcomm.hardware.motors.GoBILDA5202Series"


class Matrix12vMotor:
    __java__ = "com.qualcomm.hardware.motors.Matrix12vMotor"


class NeveRest20Gearmotor:
    __java__ = "com.qualcomm.hardware.motors.NeveRest20Gearmotor"


class NeveRest3_7GearmotorV1:
    """NeveRest3_7GearmotorV1 represents the original v1 3-magnetic-pole version of the NeveRest 3.7-geared gearmotor."""
    __java__ = "com.qualcomm.hardware.motors.NeveRest3_7GearmotorV1"


class NeveRest40Gearmotor:
    __java__ = "com.qualcomm.hardware.motors.NeveRest40Gearmotor"


class NeveRest60Gearmotor:
    __java__ = "com.qualcomm.hardware.motors.NeveRest60Gearmotor"


class RevRobotics20HdHexMotor:
    __java__ = "com.qualcomm.hardware.motors.RevRobotics20HdHexMotor"


class RevRobotics40HdHexMotor:
    __java__ = "com.qualcomm.hardware.motors.RevRobotics40HdHexMotor"


class RevRoboticsCoreHexMotor:
    __java__ = "com.qualcomm.hardware.motors.RevRoboticsCoreHexMotor"


class RevRoboticsHdHexMotor(RevRobotics40HdHexMotor):
    __java__ = "com.qualcomm.hardware.motors.RevRoboticsHdHexMotor"


class RevRoboticsUltraPlanetaryHdHexMotor:
    __java__ = "com.qualcomm.hardware.motors.RevRoboticsUltraPlanetaryHdHexMotor"


class StudicaMaverickMotor:
    __java__ = "com.qualcomm.hardware.motors.StudicaMaverickMotor"


class TetrixMotor:
    __java__ = "com.qualcomm.hardware.motors.TetrixMotor"


class Rev2mDistanceSensor(VL53L0X):
    """Rev2mDistanceSensor implements support for the REV Robotics 2M (time-of-flight) distance sensor."""
    __java__ = "com.qualcomm.hardware.rev.Rev2mDistanceSensor"
    def __init__(self, deviceClient: I2cDeviceSynch, deviceClientIsOwned: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        ...


class Rev9AxisImu(BNO055IMUNew):
    __java__ = "com.qualcomm.hardware.rev.Rev9AxisImu"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        """This constructor is called internally by the FTC SDK."""
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...


class RevImuOrientationOnRobot(ImuOrientationOnRobot):
    __java__ = "com.qualcomm.hardware.rev.RevImuOrientationOnRobot"
    def __init__(self, rotation: Quaternion) -> None:
        ...

    def imuCoordinateSystemOrientationFromPerspectiveOfRobot(self) -> Quaternion:
        ...

    def imuRotationOffset(self) -> Quaternion:
        ...

    def angularVelocityTransform(self) -> Quaternion:
        ...

    @staticmethod
    def zyxOrientation(z: float, y: float, x: float) -> Orientation:
        ...

    @staticmethod
    def xyzOrientation(x: float, y: float, z: float) -> Orientation:
        ...


class Rev9AxisImuOrientationOnRobot(RevImuOrientationOnRobot):
    """The orientation at which a given REV External IMU is mounted to a robot."""
    __java__ = "com.qualcomm.hardware.rev.Rev9AxisImuOrientationOnRobot"
    class LogoFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.rev.Rev9AxisImuOrientationOnRobot.LogoFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    class I2cPortFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.rev.Rev9AxisImuOrientationOnRobot.I2cPortFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    @overload
    def __init__(self, logoFacingDirection: Rev9AxisImuOrientationOnRobot.LogoFacingDirection, i2cPortFacingDirection: Rev9AxisImuOrientationOnRobot.I2cPortFacingDirection) -> None:
        """Constructs a Rev9AxisImuOrientationOnRobot for a REV 9-Axis IMU that is mounted orthogonally to a robot. This is the easiest constructor to use. Simply specify which direction on the robot that the REV logo on the IMU is facing, and the direction that the I2C port on the IMU is facing."""
        ...
    @overload
    def __init__(self, rotation: Orientation) -> None:
        """Constructs a Rev9AxisImuOrientationOnRobot for a REV 9-Axis IMU that is mounted at any arbitrary angle on a robot using an Orientation object."""
        ...
    @overload
    def __init__(self, rotation: Quaternion) -> None:
        """Constructs a Rev9AxisImuOrientationOnRobot for a REV 9-Axis IMU that is mounted at any arbitrary angle on a robot using a Quaternion object."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def friendlyApiToOrientation(logoFacingDirection: Rev9AxisImuOrientationOnRobot.LogoFacingDirection, i2cPortFacingDirection: Rev9AxisImuOrientationOnRobot.I2cPortFacingDirection) -> Orientation:
        ...

    @staticmethod
    def zyxOrientation(z: float, y: float, x: float) -> Orientation:
        ...

    @staticmethod
    def xyzOrientation(x: float, y: float, z: float) -> Orientation:
        ...


class RevBlinkinLedDriver(HardwareDevice):
    """Support for the REV Robotics Blinkin LED Driver. For full details see: http://www.revrobotics.com/content/docs/REV-11-1105-UM.pdf To use a Blinkin, connect your Blinkin to a servo port, then on the Robot Controller or Driver Station, configure the port you connected the Blinkin to as a REV Blinkin LED Driver. See the SampleRevBlinkinLedDriver.java sample for an example of how to use this class."""
    __java__ = "com.qualcomm.hardware.rev.RevBlinkinLedDriver"
    class BlinkinPattern(enum.Enum):
        __java__ = "com.qualcomm.hardware.rev.RevBlinkinLedDriver.BlinkinPattern"
        RAINBOW_RAINBOW_PALETTE = enum.auto()
        RAINBOW_PARTY_PALETTE = enum.auto()
        RAINBOW_OCEAN_PALETTE = enum.auto()
        RAINBOW_LAVA_PALETTE = enum.auto()
        RAINBOW_FOREST_PALETTE = enum.auto()
        RAINBOW_WITH_GLITTER = enum.auto()
        CONFETTI = enum.auto()
        SHOT_RED = enum.auto()
        SHOT_BLUE = enum.auto()
        SHOT_WHITE = enum.auto()
        SINELON_RAINBOW_PALETTE = enum.auto()
        SINELON_PARTY_PALETTE = enum.auto()
        SINELON_OCEAN_PALETTE = enum.auto()
        SINELON_LAVA_PALETTE = enum.auto()
        SINELON_FOREST_PALETTE = enum.auto()
        BEATS_PER_MINUTE_RAINBOW_PALETTE = enum.auto()
        BEATS_PER_MINUTE_PARTY_PALETTE = enum.auto()
        BEATS_PER_MINUTE_OCEAN_PALETTE = enum.auto()
        BEATS_PER_MINUTE_LAVA_PALETTE = enum.auto()
        BEATS_PER_MINUTE_FOREST_PALETTE = enum.auto()
        FIRE_MEDIUM = enum.auto()
        FIRE_LARGE = enum.auto()
        TWINKLES_RAINBOW_PALETTE = enum.auto()
        TWINKLES_PARTY_PALETTE = enum.auto()
        TWINKLES_OCEAN_PALETTE = enum.auto()
        TWINKLES_LAVA_PALETTE = enum.auto()
        TWINKLES_FOREST_PALETTE = enum.auto()
        COLOR_WAVES_RAINBOW_PALETTE = enum.auto()
        COLOR_WAVES_PARTY_PALETTE = enum.auto()
        COLOR_WAVES_OCEAN_PALETTE = enum.auto()
        COLOR_WAVES_LAVA_PALETTE = enum.auto()
        COLOR_WAVES_FOREST_PALETTE = enum.auto()
        LARSON_SCANNER_RED = enum.auto()
        LARSON_SCANNER_GRAY = enum.auto()
        LIGHT_CHASE_RED = enum.auto()
        LIGHT_CHASE_BLUE = enum.auto()
        LIGHT_CHASE_GRAY = enum.auto()
        HEARTBEAT_RED = enum.auto()
        HEARTBEAT_BLUE = enum.auto()
        HEARTBEAT_WHITE = enum.auto()
        HEARTBEAT_GRAY = enum.auto()
        BREATH_RED = enum.auto()
        BREATH_BLUE = enum.auto()
        BREATH_GRAY = enum.auto()
        STROBE_RED = enum.auto()
        STROBE_BLUE = enum.auto()
        STROBE_GOLD = enum.auto()
        STROBE_WHITE = enum.auto()
        CP1_END_TO_END_BLEND_TO_BLACK = enum.auto()
        CP1_LARSON_SCANNER = enum.auto()
        CP1_LIGHT_CHASE = enum.auto()
        CP1_HEARTBEAT_SLOW = enum.auto()
        CP1_HEARTBEAT_MEDIUM = enum.auto()
        CP1_HEARTBEAT_FAST = enum.auto()
        CP1_BREATH_SLOW = enum.auto()
        CP1_BREATH_FAST = enum.auto()
        CP1_SHOT = enum.auto()
        CP1_STROBE = enum.auto()
        CP2_END_TO_END_BLEND_TO_BLACK = enum.auto()
        CP2_LARSON_SCANNER = enum.auto()
        CP2_LIGHT_CHASE = enum.auto()
        CP2_HEARTBEAT_SLOW = enum.auto()
        CP2_HEARTBEAT_MEDIUM = enum.auto()
        CP2_HEARTBEAT_FAST = enum.auto()
        CP2_BREATH_SLOW = enum.auto()
        CP2_BREATH_FAST = enum.auto()
        CP2_SHOT = enum.auto()
        CP2_STROBE = enum.auto()
        CP1_2_SPARKLE_1_ON_2 = enum.auto()
        CP1_2_SPARKLE_2_ON_1 = enum.auto()
        CP1_2_COLOR_GRADIENT = enum.auto()
        CP1_2_BEATS_PER_MINUTE = enum.auto()
        CP1_2_END_TO_END_BLEND_1_TO_2 = enum.auto()
        CP1_2_END_TO_END_BLEND = enum.auto()
        CP1_2_NO_BLENDING = enum.auto()
        CP1_2_TWINKLES = enum.auto()
        CP1_2_COLOR_WAVES = enum.auto()
        CP1_2_SINELON = enum.auto()
        HOT_PINK = enum.auto()
        DARK_RED = enum.auto()
        RED = enum.auto()
        RED_ORANGE = enum.auto()
        ORANGE = enum.auto()
        GOLD = enum.auto()
        YELLOW = enum.auto()
        LAWN_GREEN = enum.auto()
        LIME = enum.auto()
        DARK_GREEN = enum.auto()
        GREEN = enum.auto()
        BLUE_GREEN = enum.auto()
        AQUA = enum.auto()
        SKY_BLUE = enum.auto()
        DARK_BLUE = enum.auto()
        BLUE = enum.auto()
        BLUE_VIOLET = enum.auto()
        VIOLET = enum.auto()
        WHITE = enum.auto()
        GRAY = enum.auto()
        DARK_GRAY = enum.auto()
        BLACK = enum.auto()
        @staticmethod
        def fromNumber(number: int) -> RevBlinkinLedDriver.BlinkinPattern:
            ...

        def next(self) -> RevBlinkinLedDriver.BlinkinPattern:
            ...

        def previous(self) -> RevBlinkinLedDriver.BlinkinPattern:
            ...

    def __init__(self, controller: ServoControllerEx, port: int) -> None:
        """RevBlinkinLedDriver"""
        ...

    def setPattern(self, pattern: RevBlinkinLedDriver.BlinkinPattern) -> None:
        """setPattern"""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...

    TAG: str
    PULSE_WIDTH_INCREMENTOR: float
    BASE_SERVO_POSITION: float
    PATTERN_OFFSET: int
    controller: ServoControllerEx


class RevColorSensorV3(BroadcomColorSensorImpl, ColorRangeSensor):
    """RevColorSensorV3 implements support for the REV Robotics Color Sensor V3."""
    __java__ = "com.qualcomm.hardware.rev.RevColorSensorV3"
    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    def getDeviceName(self) -> str:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getLightDetected(self) -> float:
        ...

    def getRawLightDetected(self) -> float:
        ...

    def getRawLightDetectedMax(self) -> float:
        ...

    def status(self) -> str:
        ...

    def getDistance(self, unit: DistanceUnit) -> float:
        """Returns a calibrated, linear sense of distance as read by the infrared proximity part of the sensor. Distance is measured to the plastic housing at the front of the sensor. Natively, the raw optical signal follows an inverse square law. Here, parameters have been fitted to turn that into a linear measure of distance. The function fitted was of the form: RawOptical = a * distance^b + c The calibration was performed with proximity sensor pulses set to 32, LED driver current set to 125ma, and measurement rate set to 100ms. If the end user chooses to use different settings, the device will need to be recalibrated. Additionally, calibration was performed using card stock measured head on. Actual raw values measured will depend on reflectivity and angle of surface. End user should experimentally verify calibration is appropriate for their own application."""
        ...

    def inFromOptical(self, rawOptical: int) -> float:
        """Converts a raw optical inverse-square reading into a fitted, calibrated linear reading in INCHES."""
        ...

    def rawOptical(self) -> int:
        ...

    apiLevelMin: float
    apiLevelMax: float
    aParam: float
    """Experimentally determined constants for converting optical measurements to distance."""
    binvParam: float
    cParam: float
    maxDist: float


class RevHubOrientationOnRobot(RevImuOrientationOnRobot):
    """The orientation at which a given REV Robotics Control Hub or Expansion Hub is mounted to a robot."""
    __java__ = "com.qualcomm.hardware.rev.RevHubOrientationOnRobot"
    class LogoFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.rev.RevHubOrientationOnRobot.LogoFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    class UsbFacingDirection(enum.Enum):
        __java__ = "com.qualcomm.hardware.rev.RevHubOrientationOnRobot.UsbFacingDirection"
        UP = enum.auto()
        DOWN = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()
        LEFT = enum.auto()
        RIGHT = enum.auto()

    @overload
    def __init__(self, logoFacingDirection: RevHubOrientationOnRobot.LogoFacingDirection, usbFacingDirection: RevHubOrientationOnRobot.UsbFacingDirection) -> None:
        """Constructs a RevHubOrientationOnRobot for a REV Hub that is mounted orthogonally to a robot. This is the easiest constructor to use. Simply specify which direction on the robot that the REV Robotics logo on the Hub is facing, and the direction that the USB port(s) on the Hub are facing."""
        ...
    @overload
    def __init__(self, rotation: Orientation) -> None:
        """Constructs a RevHubOrientationOnRobot for a REV Hub that is mounted at any arbitrary angle on a robot using an Orientation object."""
        ...
    @overload
    def __init__(self, rotation: Quaternion) -> None:
        """Constructs a RevHubOrientationOnRobot for a REV Hub that is mounted at any arbitrary angle on a robot using a Quaternion object."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def friendlyApiToOrientation(logoFacingDirection: RevHubOrientationOnRobot.LogoFacingDirection, usbFacingDirection: RevHubOrientationOnRobot.UsbFacingDirection) -> Orientation:
        ...

    @staticmethod
    def zyxOrientation(z: float, y: float, x: float) -> Orientation:
        ...

    @staticmethod
    def xyzOrientation(x: float, y: float, z: float) -> Orientation:
        ...


class RevSPARKMini:
    """Support for the REV Robotics SPARKmini Motor Controller. For full details see: http://www.revrobotics.com/rev-31-1230/ To use a SPARKmini, connect your SPARKmini to a servo port, then on the Robot Controller or Driver Station, configure the port you connected the SPARKmini as a REV SPARKmini Motor Controller."""
    __java__ = "com.qualcomm.hardware.rev.RevSPARKMini"


class RevTouchSensor(TouchSensor):
    __java__ = "com.qualcomm.hardware.rev.RevTouchSensor"
    def __init__(self, digitalChannelController: DigitalChannelController, physicalPort: int) -> None:
        ...

    def getValue(self) -> float:
        ...

    def isPressed(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def getConnectionInfo(self) -> str:
        ...

    def getVersion(self) -> int:
        ...

    def resetDeviceConfigurationForOpMode(self) -> None:
        ...

    def close(self) -> None:
        ...


class SparkFunLEDStick(I2cDeviceSynchDevice[I2cDeviceSynchSimple]):
    """Support for the Sparkfun QWIIC LED Stick To connect it directly, you need this cable"""
    __java__ = "com.qualcomm.hardware.sparkfun.SparkFunLEDStick"
    class Commands(enum.Enum):
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunLEDStick.Commands"
        CHANGE_LED_LENGTH = enum.auto()
        WRITE_SINGLE_LED_COLOR = enum.auto()
        WRITE_ALL_LED_COLOR = enum.auto()
        WRITE_RED_ARRAY = enum.auto()
        WRITE_GREEN_ARRAY = enum.auto()
        WRITE_BLUE_ARRAY = enum.auto()
        WRITE_SINGLE_LED_BRIGHTNESS = enum.auto()
        WRITE_ALL_LED_BRIGHTNESS = enum.auto()
        WRITE_ALL_LED_OFF = enum.auto()
        bVal: int

    def __init__(self, deviceClient: I2cDeviceSynchSimple, deviceClientIsOwned: bool) -> None:
        ...

    @overload
    def setColor(self, position: int, color: int) -> None:
        """Change the color of a specific LED"""
        ...
    @overload
    def setColor(self, color: int) -> None:
        """Change the color of all LEDs to a single color"""
        ...
    def setColor(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def setColors(self, colors: list[int]) -> None:
        """Change the color of all LEDs using arrays"""
        ...

    @overload
    def setBrightness(self, position: int, brightness: int) -> None:
        """Set the brightness of an individual LED"""
        ...
    @overload
    def setBrightness(self, brightness: int) -> None:
        """Set the brightness of all LEDs"""
        ...
    def setBrightness(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def turnAllOff(self) -> None:
        """Turn all LEDS off..."""
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def doInitialize(self) -> bool:
        ...

    def getDeviceName(self) -> str:
        ...


class SparkFunOTOS(I2cDeviceSynchDevice[I2cDeviceSynch]):
    """SparkFunOTOS is the Java driver for the SparkFun Qwiic Optical Tracking Odometry Sensor (OTOS). This is a port of the Arduino library."""
    __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS"
    class Pose2D:
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS.Pose2D"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, x: float, y: float, h: float) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def set(self, pose: SparkFunOTOS.Pose2D) -> None:
            ...

        def toString(self) -> str:
            ...

        x: float
        y: float
        h: float

    class Version:
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS.Version"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, value: int) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def set(self, value: int) -> None:
            ...

        def get(self) -> int:
            ...

        minor: int
        major: int

    class SignalProcessConfig:
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS.SignalProcessConfig"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, value: int) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def set(self, value: int) -> None:
            ...

        def get(self) -> int:
            ...

        enLut: bool
        enAcc: bool
        enRot: bool
        enVar: bool

    class SelfTestConfig:
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS.SelfTestConfig"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, value: int) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def set(self, value: int) -> None:
            ...

        def get(self) -> int:
            ...

        start: bool
        inProgress: bool
        pass_: bool
        fail: bool

    class Status:
        __java__ = "com.qualcomm.hardware.sparkfun.SparkFunOTOS.Status"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, value: int) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        def set(self, value: int) -> None:
            ...

        def get(self) -> int:
            ...

        warnTiltAngle: bool
        warnOpticalTracking: bool
        errorPaa: bool
        errorLsm: bool

    def __init__(self, deviceClient: I2cDeviceSynch) -> None:
        ...

    def doInitialize(self) -> bool:
        ...

    def getManufacturer(self) -> HardwareDevice.Manufacturer:
        ...

    def getDeviceName(self) -> str:
        ...

    def begin(self) -> bool:
        """Begins the Qwiic OTOS and verifies it is connected"""
        ...

    def isConnected(self) -> bool:
        """Checks if the OTOS is connected to the I2C bus"""
        ...

    def getVersionInfo(self, hwVersion: SparkFunOTOS.Version, fwVersion: SparkFunOTOS.Version) -> None:
        """Gets the hardware and firmware version of the OTOS"""
        ...

    def selfTest(self) -> bool:
        """Performs a self-test on the OTOS"""
        ...

    @overload
    def calibrateImu(self) -> bool:
        """Calibrates the IMU on the OTOS, which removes the accelerometer and gyroscope offsets. This will do the full 255 samples and wait until the calibration is done, which takes about 612ms as of firmware v1.0"""
        ...
    @overload
    def calibrateImu(self, numSamples: int, waitUntilDone: bool) -> bool:
        """Calibrates the IMU on the OTOS, which removes the accelerometer and gyroscope offsets"""
        ...
    def calibrateImu(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getImuCalibrationProgress(self) -> int:
        """Gets the progress of the IMU calibration. Used for asynchronous calibration with calibrateImu()"""
        ...

    def getLinearUnit(self) -> DistanceUnit:
        """Gets the linear unit used by all methods using a pose"""
        ...

    def setLinearUnit(self, unit: DistanceUnit) -> None:
        """Sets the linear unit used by all methods using a pose"""
        ...

    def getAngularUnit(self) -> AngleUnit:
        """Gets the angular unit used by all methods using a pose"""
        ...

    def setAngularUnit(self, unit: AngleUnit) -> None:
        """Sets the angular unit used by all methods using a pose"""
        ...

    def getLinearScalar(self) -> float:
        """Gets the linear scalar used by the OTOS"""
        ...

    def setLinearScalar(self, scalar: float) -> bool:
        """Sets the linear scalar used by the OTOS. Can be used to compensate for scaling issues with the sensor measurements"""
        ...

    def getAngularScalar(self) -> float:
        """Gets the angular scalar used by the OTOS"""
        ...

    def setAngularScalar(self, scalar: float) -> bool:
        """Sets the angular scalar used by the OTOS. Can be used to compensate for scaling issues with the sensor measurements"""
        ...

    def resetTracking(self) -> None:
        """Resets the tracking algorithm, which resets the position to the origin, but can also be used to recover from some rare tracking errors"""
        ...

    def getSignalProcessConfig(self) -> SparkFunOTOS.SignalProcessConfig:
        """Gets the signal processing configuration from the OTOS"""
        ...

    def setSignalProcessConfig(self, config: SparkFunOTOS.SignalProcessConfig) -> None:
        """Sets the signal processing configuration on the OTOS. This is primarily useful for creating and testing a new lookup table calibration"""
        ...

    def getStatus(self) -> SparkFunOTOS.Status:
        """Gets the status register from the OTOS, which includes warnings and errors reported by the sensor"""
        ...

    def getOffset(self) -> SparkFunOTOS.Pose2D:
        """Gets the offset of the OTOS"""
        ...

    def setOffset(self, pose: SparkFunOTOS.Pose2D) -> None:
        """Sets the offset of the OTOS. This is useful if your sensor is mounted off-center from a robot. Rather than returning the position of the sensor, the OTOS will return the position of the robot"""
        ...

    def getPosition(self) -> SparkFunOTOS.Pose2D:
        """Gets the position measured by the OTOS"""
        ...

    def setPosition(self, pose: SparkFunOTOS.Pose2D) -> None:
        """Sets the position measured by the OTOS. This is useful if your robot does not start at the origin, or you have another source of location information (eg. vision odometry); the OTOS will continue tracking from this position"""
        ...

    def getVelocity(self) -> SparkFunOTOS.Pose2D:
        """Gets the velocity measured by the OTOS"""
        ...

    def getAcceleration(self) -> SparkFunOTOS.Pose2D:
        """Gets the acceleration measured by the OTOS"""
        ...

    def getPositionStdDev(self) -> SparkFunOTOS.Pose2D:
        """Gets the standard deviation of the measured position These values are just the square root of the diagonal elements of the covariance matrices of the Kalman filters used in the firmware, so they are just statistical quantities and do not represent actual error!"""
        ...

    def getVelocityStdDev(self) -> SparkFunOTOS.Pose2D:
        """Gets the standard deviation of the measured velocity These values are just the square root of the diagonal elements of the covariance matrices of the Kalman filters used in the firmware, so they are just statistical quantities and do not represent actual error!"""
        ...

    def getAccelerationStdDev(self) -> SparkFunOTOS.Pose2D:
        """Gets the standard deviation of the measured acceleration These values are just the square root of the diagonal elements of the covariance matrices of the Kalman filters used in the firmware, so they are just statistical quantities and do not represent actual error!"""
        ...

    def getPosVelAcc(self, pos: SparkFunOTOS.Pose2D, vel: SparkFunOTOS.Pose2D, acc: SparkFunOTOS.Pose2D) -> None:
        """Gets the position, velocity, and acceleration measured by the OTOS in a single burst read"""
        ...

    def getPosVelAccStdDev(self, pos: SparkFunOTOS.Pose2D, vel: SparkFunOTOS.Pose2D, acc: SparkFunOTOS.Pose2D) -> None:
        """Gets the standard deviation of the measured position, velocity, and acceleration in a single burst read"""
        ...

    def getPosVelAccAndStdDev(self, pos: SparkFunOTOS.Pose2D, vel: SparkFunOTOS.Pose2D, acc: SparkFunOTOS.Pose2D, posStdDev: SparkFunOTOS.Pose2D, velStdDev: SparkFunOTOS.Pose2D, accStdDev: SparkFunOTOS.Pose2D) -> None:
        """Gets the position, velocity, acceleration, and standard deviation of each in a single burst read"""
        ...

    def readPoseRegs(self, reg: int, rawToXY: float, rawToH: float) -> SparkFunOTOS.Pose2D:
        ...

    def writePoseRegs(self, reg: int, pose: SparkFunOTOS.Pose2D, xyToRaw: float, hToRaw: float) -> None:
        ...

    def regsToPose(self, rawData: list[int], rawToXY: float, rawToH: float) -> SparkFunOTOS.Pose2D:
        ...

    def poseToRegs(self, rawData: list[int], pose: SparkFunOTOS.Pose2D, xyToRaw: float, hToRaw: float) -> None:
        ...

    DEFAULT_ADDRESS: int
    MIN_SCALAR: float
    MAX_SCALAR: float
    REG_PRODUCT_ID: int
    REG_HW_VERSION: int
    REG_FW_VERSION: int
    REG_SCALAR_LINEAR: int
    REG_SCALAR_ANGULAR: int
    REG_IMU_CALIB: int
    REG_RESET: int
    REG_SIGNAL_PROCESS: int
    REG_SELF_TEST: int
    REG_OFF_XL: int
    REG_OFF_XH: int
    REG_OFF_YL: int
    REG_OFF_YH: int
    REG_OFF_HL: int
    REG_OFF_HH: int
    REG_STATUS: int
    REG_POS_XL: int
    REG_POS_XH: int
    REG_POS_YL: int
    REG_POS_YH: int
    REG_POS_HL: int
    REG_POS_HH: int
    REG_VEL_XL: int
    REG_VEL_XH: int
    REG_VEL_YL: int
    REG_VEL_YH: int
    REG_VEL_HL: int
    REG_VEL_HH: int
    REG_ACC_XL: int
    REG_ACC_XH: int
    REG_ACC_YL: int
    REG_ACC_YH: int
    REG_ACC_HL: int
    REG_ACC_HH: int
    REG_POS_STD_XL: int
    REG_POS_STD_XH: int
    REG_POS_STD_YL: int
    REG_POS_STD_YH: int
    REG_POS_STD_HL: int
    REG_POS_STD_HH: int
    REG_VEL_STD_XL: int
    REG_VEL_STD_XH: int
    REG_VEL_STD_YL: int
    REG_VEL_STD_YH: int
    REG_VEL_STD_HL: int
    REG_VEL_STD_HH: int
    REG_ACC_STD_XL: int
    REG_ACC_STD_XH: int
    REG_ACC_STD_YL: int
    REG_ACC_STD_YH: int
    REG_ACC_STD_HL: int
    REG_ACC_STD_HH: int
    PRODUCT_ID: int
    RADIAN_TO_DEGREE: float
    DEGREE_TO_RADIAN: float
    METER_TO_INT16: float
    INT16_TO_METER: float
    MPS_TO_INT16: float
    INT16_TO_MPS: float
    MPSS_TO_INT16: float
    INT16_TO_MPSS: float
    RAD_TO_INT16: float
    INT16_TO_RAD: float
    RPS_TO_INT16: float
    INT16_TO_RPS: float
    RPSS_TO_INT16: float
    INT16_TO_RPSS: float
    _distanceUnit: DistanceUnit
    _angularUnit: AngleUnit


class Heartbeat(RobocolParsableBase):
    """Heartbeat message"""
    __java__ = "com.qualcomm.robotcore.robocol.Heartbeat"
    def __init__(self) -> None:
        ...

    def cbPayload(self) -> int:
        ...

    def getTimeZoneId(self) -> str:
        ...

    def setTimeZoneId(self, timeZoneId: str) -> None:
        ...

    @staticmethod
    def createWithTimeStamp() -> Heartbeat:
        ...

    def getTimestamp(self) -> int:
        """Timestamp this Heartbeat was created at"""
        ...

    def getElapsedSeconds(self) -> float:
        """Number of seconds since Heartbeat was created"""
        ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        """Get Robocol message type"""
        ...

    def getRobotState(self) -> int:
        """Get RobotState"""
        ...

    def setRobotState(self, state: RobotState) -> None:
        """Set RobotState"""
        ...

    def toByteArray(self) -> list[int]:
        """Convert this Heartbeat into a byte array"""
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        """Populate this Heartbeat from a byte array"""
        ...

    def toString(self) -> str:
        """String containing sequence number and timestamp"""
        ...

    BASE_PAYLOAD_SIZE: int
    t0: int
    t1: int
    t2: int


class CameraName:
    """CameraName identifies a HardwareDevice which is a camera."""
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.CameraName"
    def isWebcam(self) -> bool:
        """Returns whether or not this name is that of a webcam. If true, then the CameraName can be cast to a WebcamName."""
        ...

    def isCameraDirection(self) -> bool:
        """Returns whether or not this name is that of a builtin phone camera. If true, then the CameraName can be cast to a BuiltinCameraName."""
        ...

    def isSwitchable(self) -> bool:
        """Returns whether this name is one representing the ability to switch amongst a series of member cameras. If true, then the receiver can be cast to a SwitchableCameraName."""
        ...

    def isUnknown(self) -> bool:
        """Returns whether or not this name represents that of an unknown or indeterminate camera."""
        ...

    def asyncRequestCameraPermission(self, context: Any, deadline: Deadline, continuation: Continuation[Consumer[bool]]) -> None:
        """Requests from the user permission to use the camera if same has not already been granted. This may take a long time, as interaction with the user may be necessary. When the outcome is known, the reportResult continuation is called with the result. The report may occur either before or after the call to #asyncRequestCameraPermission has itself returned. The report will be delivered using the indicated Continuation"""
        ...

    def requestCameraPermission(self, deadline: Deadline) -> bool:
        """Requests from the user permission to use the camera if same has not already been granted. This may take a long time, as interaction with the user may be necessary. The call is made synchronously: the calling thread blocks until an answer is obtained."""
        ...

    def getCameraCharacteristics(self) -> CameraCharacteristics:
        """Query the capabilities of a camera device. These capabilities are immutable for a given camera."""
        ...


class SwitchableCameraName(CameraName):
    __java__ = "org.firstinspires.ftc.robotcore.internal.camera.delegating.SwitchableCameraName"
    def getMembers(self) -> list[CameraName]:
        """Returns the ordered list of member CameraNames in this SwitchableCameraName."""
        ...

    def allMembersAreWebcams(self) -> bool:
        """Returns true if all members of this SwitchableCameraName are webcams."""
        ...


class NetworkConnection:
    __java__ = "com.qualcomm.robotcore.wifi.NetworkConnection"
    class NetworkEvent(enum.Enum):
        __java__ = "com.qualcomm.robotcore.wifi.NetworkConnection.NetworkEvent"
        DISCOVERING_PEERS = enum.auto()
        PEERS_AVAILABLE = enum.auto()
        GROUP_CREATED = enum.auto()
        CONNECTING = enum.auto()
        CONNECTED_AS_PEER = enum.auto()
        CONNECTED_AS_GROUP_OWNER = enum.auto()
        DISCONNECTED = enum.auto()
        CONNECTION_INFO_AVAILABLE = enum.auto()
        AP_CREATED = enum.auto()
        ERROR = enum.auto()
        UNKNOWN = enum.auto()

    class ConnectStatus(enum.Enum):
        __java__ = "com.qualcomm.robotcore.wifi.NetworkConnection.ConnectStatus"
        NOT_CONNECTED = enum.auto()
        CONNECTING = enum.auto()
        CONNECTED = enum.auto()
        GROUP_OWNER = enum.auto()
        ERROR = enum.auto()

    class NetworkConnectionCallback:
        __java__ = "com.qualcomm.robotcore.wifi.NetworkConnection.NetworkConnectionCallback"
        def onNetworkConnectionEvent(self, event: NetworkConnection.NetworkEvent) -> CallbackResult:
            ...

    def __init__(self, context: Any) -> None:
        ...

    def getNetworkType(self) -> NetworkType:
        ...

    def enable(self) -> None:
        ...

    def disable(self) -> None:
        ...

    def discoverPotentialConnections(self) -> None:
        ...

    def cancelPotentialConnections(self) -> None:
        ...

    def createConnection(self) -> None:
        ...

    @overload
    def connect(self, deviceAddress: str) -> None:
        ...
    @overload
    def connect(self, connectionName: str, connectionPassword: str) -> None:
        ...
    def connect(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def detectWifiReset(self) -> None:
        ...

    def getConnectionOwnerAddress(self) -> Any:
        ...

    def getConnectionOwnerName(self) -> str:
        ...

    def getConnectionOwnerMacAddress(self) -> str:
        ...

    def isConnected(self) -> bool:
        ...

    def getDeviceName(self) -> str:
        ...

    def getInfo(self) -> str:
        ...

    def getFailureReason(self) -> str:
        ...

    def getPassphrase(self) -> str:
        ...

    def getConnectStatus(self) -> NetworkConnection.ConnectStatus:
        ...

    def onWaitForConnection(self) -> None:
        ...

    def setNetworkSettings(self, deviceName: str, password: str, channel: ApChannel) -> None:
        """Should only be called on Robot Controller"""
        ...

    @staticmethod
    def isDeviceNameValid(deviceName: str) -> bool:
        """Return true if the device name is valid. A valid device name is greater than 0 characters and contains only alphanumeric or punctuation characters only."""
        ...

    def setCallback(self, callback: NetworkConnection.NetworkConnectionCallback) -> None:
        ...

    def getCallback(self) -> NetworkConnection.NetworkConnectionCallback:
        ...

    def getWifiChannel(self) -> int:
        ...

    def sendEvent(self, event: NetworkConnection.NetworkEvent) -> None:
        """sendEvent Unicast to a single listener. No support for multicast."""
        ...

    lastEvent: NetworkConnection.NetworkEvent
    callback: NetworkConnection.NetworkConnectionCallback
    callbackLock: object
    wifiManager: Any
    context: Any


class RecvLoopRunnable:
    __java__ = "org.firstinspires.ftc.robotcore.internal.network.RecvLoopRunnable"
    class RecvLoopCallback:
        __java__ = "org.firstinspires.ftc.robotcore.internal.network.RecvLoopRunnable.RecvLoopCallback"
        def packetReceived(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def peerDiscoveryEvent(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def heartbeatEvent(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def commandEvent(self, command: Command) -> CallbackResult:
            ...

        def telemetryEvent(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def gamepadEvent(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def emptyEvent(self, packet: RobocolDatagram) -> CallbackResult:
            ...

        def reportGlobalError(self, error: str, recoverable: bool) -> CallbackResult:
            ...

    def __init__(self, callback: RecvLoopRunnable.RecvLoopCallback, socket: RobocolDatagramSocket, lastRecvPacket: ElapsedTime) -> None:
        ...

    def setCallback(self, callback: RecvLoopRunnable.RecvLoopCallback) -> None:
        ...

    def injectReceivedCommand(self, cmd: Command) -> None:
        ...

    def getBytesPerSecond(self) -> int:
        ...

    def calculateBytesPerMilli(self) -> None:
        ...

    def run(self) -> None:
        ...

    TAG: str
    DEBUG: bool
    lastRecvPacket: ElapsedTime
    packetProcessingTimer: ElapsedTime
    commandProcessingTimer: ElapsedTime
    msCommandProcessingTimerReportingThreshold: float
    msPacketProcessingTimerReportingThreshold: float
    socket: RobocolDatagramSocket
    callback: RecvLoopRunnable.RecvLoopCallback
    packetsToProcess: Any
    commandsToProcess: Any


class EventLoopManager(RecvLoopRunnable.RecvLoopCallback, NetworkConnection.NetworkConnectionCallback, PeerStatusCallback, SyncdDevice.Manager):
    """Event Loop Manager"""
    __java__ = "com.qualcomm.robotcore.eventloop.EventLoopManager"
    class EventLoopMonitor:
        """Callback to monitor when event loop changes state"""
        __java__ = "com.qualcomm.robotcore.eventloop.EventLoopManager.EventLoopMonitor"
        def onStateChange(self, state: RobotState) -> None:
            ...

        def onTelemetryTransmitted(self) -> None:
            ...

        def onPeerConnected(self) -> None:
            ...

        def onPeerDisconnected(self) -> None:
            ...

    def __init__(self, context: Any, eventLoopManagerClient: EventLoopManagerClient, idleEventLoop: EventLoop) -> None:
        """Constructor"""
        ...

    def getWebServer(self) -> WebServer:
        ...

    def setMonitor(self, monitor: EventLoopManager.EventLoopMonitor) -> None:
        """Set a monitor for this event loop, which will immediately have the appropriate method called to indicate the current peer status."""
        ...

    def getMonitor(self) -> EventLoopManager.EventLoopMonitor:
        """return any event loop monitor previously set"""
        ...

    def getEventLoop(self) -> EventLoop:
        """Get the current event loop"""
        ...

    def getGamepad(self, port: int) -> Gamepad:
        """Get the gamepad connected to a particular user"""
        ...

    def getOpModeGamepads(self) -> list[Gamepad]:
        """Get the Gamepad instances used by user code"""
        ...

    def getLatestGamepad1Data(self) -> Gamepad:
        """Get a Gamepad instance with the latest gamepad data available for user 1"""
        ...

    def getLatestGamepad2Data(self) -> Gamepad:
        """Get a Gamepad instance with the latest gamepad data available for user 1"""
        ...

    def getHeartbeat(self) -> Heartbeat:
        """Get the current heartbeat state"""
        ...

    def telemetryEvent(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def reportGlobalError(self, error: str, recoverable: bool) -> CallbackResult:
        ...

    def packetReceived(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def refreshSystemTelemetryNow(self) -> None:
        """Forces an immediate refresh of the system telemetry"""
        ...

    def refreshSystemTelemetry(self) -> None:
        """Do our best to maintain synchrony of the system error / warning state between applications without incurring undo overhead."""
        ...

    def onNetworkConnectionEvent(self, event: NetworkConnection.NetworkEvent) -> CallbackResult:
        ...

    def start(self, eventLoop: EventLoop) -> None:
        """Starts up the EventLoopManager. This mostly involves setting up the network connections and listeners and senders, then getting the event loop thread going. Note that shutting down the EventLoopManager does not do a full complete inverse. Rather, it leaves the underlying network connection alive and running, as this, among other things, helps remote toasts to continue to function correctly. Thus, we must be aware of that possibility here as we start."""
        ...

    def shutdown(self) -> None:
        """Performs the logical inverse of #start(EventLoop)."""
        ...

    def close(self) -> None:
        ...

    def registerSyncdDevice(self, device: SyncdDevice) -> None:
        """Register a sync'd device"""
        ...

    def unregisterSyncdDevice(self, device: SyncdDevice) -> None:
        """Unregisters a device from this event loop. It is specifically permitted to unregister a device which is not currently registered; such an operation has no effect."""
        ...

    def setEventLoop(self, eventLoop: EventLoop) -> None:
        """Replace the current event loop with a new event loop"""
        ...

    def sendTelemetryData(self, telemetry: TelemetryMessage) -> None:
        """Send telemetry data"""
        ...

    def gamepadEvent(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def heartbeatEvent(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def onPeerConnected(self) -> None:
        ...

    def onPeerDisconnected(self) -> None:
        ...

    def peerDiscoveryEvent(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def commandEvent(self, command: Command) -> CallbackResult:
        ...

    def emptyEvent(self, packet: RobocolDatagram) -> CallbackResult:
        ...

    def buildAndSendTelemetry(self, tag: str, msg: str) -> None:
        ...

    TAG: str
    SYSTEM_NONE_KEY: str
    SYSTEM_ERROR_KEY: str
    SYSTEM_WARNING_KEY: str
    ROBOT_BATTERY_LEVEL_KEY: str
    RC_BATTERY_STATUS_KEY: str
    state: RobotState


class WebcamName(CameraName, HardwareDevice):
    __java__ = "org.firstinspires.ftc.robotcore.external.hardware.camera.WebcamName"
    def getSerialNumber(self) -> SerialNumber:
        """Returns the USB serial number of the webcam"""
        ...

    def getUsbDeviceNameIfAttached(self) -> str:
        """Returns the USB device path currently associated with this webcam. May be null if the webcam is not presently attached."""
        ...

    def isAttached(self) -> bool:
        """Returns whether this camera currently attached to the robot controller"""
        ...


class TelemetryMessage(RobocolParsableBase):
    """Hold telemtry data"""
    __java__ = "com.qualcomm.robotcore.robocol.TelemetryMessage"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, byteArray: list[int]) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getTimestamp(self) -> int:
        """Timestamp this message was sent. Timestamp is in wall time."""
        ...

    def isSorted(self) -> bool:
        """Returns whether this telemetry should be sorted by keys on the driver station or not. If not sorted, then data is displayed in the order in which it was added to the telemetry."""
        ...

    def setSorted(self, isSorted: bool) -> None:
        """Sets whether the telemetry should be sorted by its keys on the driver station or not."""
        ...

    def getRobotState(self) -> RobotState:
        ...

    def setRobotState(self, robotState: RobotState) -> None:
        ...

    def setTag(self, tag: str) -> None:
        """Set the optional tag value."""
        ...

    def getTag(self) -> str:
        """Get the optional tag value"""
        ...

    @overload
    def addData(self, key: str, msg: str) -> None:
        """Add a data point"""
        ...
    @overload
    def addData(self, key: str, msg: object) -> None:
        """Add a data point"""
        ...
    @overload
    def addData(self, key: str, msg: float) -> None:
        """Add a data point"""
        ...
    @overload
    def addData(self, key: str, msg: float) -> None:
        """Add a data point"""
        ...
    def addData(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getDataStrings(self) -> dict[str, str]:
        """Get a reference to the map of messages"""
        ...

    def getDataNumbers(self) -> dict[str, float]:
        ...

    def hasData(self) -> bool:
        """Return true if this telemetry object has data added to it"""
        ...

    def clearData(self) -> None:
        """Clear all messages"""
        ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        ...

    def toByteArray(self) -> list[int]:
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        ...

    @staticmethod
    def putCount(buffer: Any, count: int) -> None:
        ...

    @staticmethod
    def getCount(buffer: Any) -> int:
        ...

    @staticmethod
    def putTagLen(buffer: Any, cbTag: int) -> None:
        ...

    @staticmethod
    def getTagLen(buffer: Any) -> int:
        ...

    @staticmethod
    def putKeyLen(buffer: Any, cbKey: int) -> None:
        ...

    @staticmethod
    def getKeyLen(buffer: Any) -> int:
        ...

    @staticmethod
    def putValueLen(buffer: Any, cbValue: int) -> None:
        ...

    @staticmethod
    def getValueLen(buffer: Any) -> int:
        ...

    DEFAULT_TAG: str
    cbTimestamp: int
    cbSorted: int
    cbRobotState: int
    cbTagLen: int
    cbCountLen: int
    cbKeyLen: int
    cbValueLen: int
    cbFloat: int
    cbTagMax: int
    cCountMax: int
    cbKeyMax: int
    cbValueMax: int


class Command(RobocolParsableBase):
    """Class used to send and receive commands"""
    __java__ = "com.qualcomm.robotcore.robocol.Command"
    @overload
    def __init__(self, name: str) -> None:
        """Constructs a Command for transmission."""
        ...
    @overload
    def __init__(self, name: str, extra: str) -> None:
        """Constructs a Command for transmission."""
        ...
    @overload
    def __init__(self, packet: RobocolDatagram) -> None:
        """Constructs a Command from a received RobocolDatagram."""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def acknowledge(self) -> None:
        """The receiver should call this method before sending this command back to the sender"""
        ...

    def isAcknowledged(self) -> bool:
        """Check if this command has been acknowledged"""
        ...

    def getName(self) -> str:
        """Get the command name as a string"""
        ...

    def getExtra(self) -> str:
        """Get the extra data as a string"""
        ...

    def getAttempts(self) -> int:
        """Number of times this command was packaged into a byte array"""
        ...

    def hasExpired(self) -> bool:
        ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        ...

    def isInjected(self) -> bool:
        ...

    def setIsInjected(self, isInjected: bool) -> None:
        ...

    def setTransmissionDeadline(self, deadline: Deadline) -> None:
        ...

    def getSender(self) -> Any:
        ...

    def toByteArray(self) -> list[int]:
        ...

    def getPayloadSize(self, nameBytesLength: int, extraBytesLength: int) -> int:
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        ...

    def toString(self) -> str:
        ...

    def equals(self, o: object) -> bool:
        ...

    def hashCode(self) -> int:
        ...

    def compareTo(self, another: Command) -> int:
        ...

    def compare(self, c1: Command, c2: Command) -> int:
        ...

    @staticmethod
    def generateTimestamp() -> int:
        ...

    mName: str
    mExtra: str
    mTimestamp: int
    mAcknowledged: bool
    mAttempts: int
    mIsInjected: bool
    mTransmissionDeadline: Deadline
    mSender: Any


class PeerDiscovery(RobocolParsableBase):
    __java__ = "com.qualcomm.robotcore.robocol.PeerDiscovery"
    class PeerType(enum.Enum):
        """Peer type"""
        __java__ = "com.qualcomm.robotcore.robocol.PeerDiscovery.PeerType"
        NOT_SET = enum.auto()
        PEER = enum.auto()
        GROUP_OWNER = enum.auto()
        NOT_CONNECTED_DUE_TO_PREEXISTING_CONNECTION = enum.auto()
        @staticmethod
        def fromByte(b: int) -> PeerDiscovery.PeerType:
            """Create a PeerType from a byte"""
            ...

        def asByte(self) -> int:
            """Return this peer type as a byte"""
            ...

    @staticmethod
    def forReceive() -> PeerDiscovery:
        ...

    @staticmethod
    def forTransmission(peerType: PeerDiscovery.PeerType) -> PeerDiscovery:
        ...

    def getPeerType(self) -> PeerDiscovery.PeerType:
        ...

    def getSdkBuildMonth(self) -> Any:
        ...

    def isSdkBuildMonthValid(self) -> bool:
        """Checks if the build month was set correctly without allocating"""
        ...

    def getSdkMajorVersion(self) -> int:
        ...

    def getSdkMinorVersion(self) -> int:
        ...

    def getRobocolMsgType(self) -> RobocolParsable.MsgType:
        ...

    def toByteArray(self) -> list[int]:
        ...

    def fromByteArray(self, byteArray: list[int]) -> None:
        ...

    def toString(self) -> str:
        ...

    TAG: str
    cbBufferHistorical: int
    cbPayloadHistorical: int
