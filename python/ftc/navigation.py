from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

if TYPE_CHECKING:
    from ftc.internal import MatrixF, OpenGLMatrix, VectorF

class Acceleration:
    """Instances of Acceleration represent the second derivative of Position over time. This is also to say that Position is a double integration of Acceleration with respect to time."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Acceleration"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, unit: DistanceUnit, xAccel: float, yAccel: float, zAccel: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def fromGravity(gx: float, gy: float, gz: float, acquisitionTime: int) -> Acceleration:
        """Returns an acceleration constructed from measures in units of earth's gravity rather than explicit distance units."""
        ...

    def toUnit(self, distanceUnit: DistanceUnit) -> Acceleration:
        ...

    def toString(self) -> str:
        ...

    earthGravity: float
    """The (nominal) acceleration due to Earth's gravity The units are in m/s^2"""
    unit: DistanceUnit
    """The distance units in which this acceleration is expressed. The time unit is always \"per second per second\"."""
    xAccel: float
    yAccel: float
    zAccel: float
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class AngleUnit(enum.Enum):
    """An AngleUnit represents angles in different units of measure and provides utility methods to convert across units. AngleUnit does not maintain angle information information internally, but only helps organize and use angle measures that may be maintained separately across various contexts."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.AngleUnit"
    DEGREES = enum.auto()
    RADIANS = enum.auto()
    @overload
    def fromDegrees(self, degrees: float) -> float:
        ...
    @overload
    def fromDegrees(self, degrees: float) -> float:
        ...
    def fromDegrees(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def fromRadians(self, radians: float) -> float:
        ...
    @overload
    def fromRadians(self, radians: float) -> float:
        ...
    def fromRadians(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def fromUnit(self, them: AngleUnit, theirs: float) -> float:
        ...
    @overload
    def fromUnit(self, them: AngleUnit, theirs: float) -> float:
        ...
    def fromUnit(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def toDegrees(self, inOurUnits: float) -> float:
        ...
    @overload
    def toDegrees(self, inOurUnits: float) -> float:
        ...
    def toDegrees(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def toRadians(self, inOurUnits: float) -> float:
        ...
    @overload
    def toRadians(self, inOurUnits: float) -> float:
        ...
    def toRadians(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def normalize(self, mine: float) -> float:
        ...
    @overload
    def normalize(self, mine: float) -> float:
        ...
    def normalize(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def normalizeDegrees(degrees: float) -> float:
        ...
    @overload
    @staticmethod
    def normalizeDegrees(degrees: float) -> float:
        ...
    @staticmethod
    def normalizeDegrees(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def normalizeRadians(radians: float) -> float:
        ...
    @overload
    @staticmethod
    def normalizeRadians(radians: float) -> float:
        ...
    @staticmethod
    def normalizeRadians(*args: Any, **kwargs: Any) -> Any:
        ...

    def getUnnormalized(self) -> UnnormalizedAngleUnit:
        ...

    bVal: int
    TwoPi: float
    Pif: float


class AngularVelocity:
    """Instances of AngularVelocity represent an instantaneous body-referenced 3D rotation rate. The instantaneous rate of change of an Orientation, which is what we are representing here, has unexpected subtleties. As described in Section 9.3 of the MIT Kinematics Lecture below, the instantaneous body-referenced rotation rate angles are decoupled (their order does not matter) but their conversion into a corresponding instantaneous rate of change of a set of related Euler angles (ie: Orientation involves a non-obvious transformation on two of the rotation rates."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.AngularVelocity"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, unit: UnnormalizedAngleUnit, xRotationRate: float, yRotationRate: float, zRotationRate: float, acquisitionTime: int) -> None:
        ...
    @overload
    def __init__(self, unit: AngleUnit, xRotationRate: float, yRotationRate: float, zRotationRate: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toAngleUnit(self, unit: AngleUnit) -> AngularVelocity:
        """Converts this AngularVelocity to one with the indicated angular units."""
        ...

    def toString(self) -> str:
        ...

    angleUnit: UnnormalizedAngleUnit
    """the angular unit in which angular rates are expressed. The time unit thereof is always \"per second\"."""
    xRotationRate: float
    """the instantaneous body-referenced rotation rate about the x-axis in units of \"#angleUnits per second\"."""
    yRotationRate: float
    """the instantaneous body-referenced rotation rate about the y-axis in units of \"#angleUnits per second\"."""
    zRotationRate: float
    """the instantaneous body-referenced rotation rate about the z-axis in units of \"#angleUnits per second\"."""
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class AxesOrder(enum.Enum):
    """AxesOrder indicates the chronological order of axes about which the three rotations of an Orientation take place. The geometry of three space is such that there are exactly twelve distinct rotational orders."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.AxesOrder"
    XZX = enum.auto()
    XYX = enum.auto()
    YXY = enum.auto()
    YZY = enum.auto()
    ZYZ = enum.auto()
    ZXZ = enum.auto()
    XZY = enum.auto()
    XYZ = enum.auto()
    YXZ = enum.auto()
    YZX = enum.auto()
    ZYX = enum.auto()
    ZXY = enum.auto()
    def indices(self) -> list[int]:
        """Returns the numerical axes indices associated with this AxesOrder."""
        ...

    def axes(self) -> list[Axis]:
        """Returns the Axis associated with this AxesOrder."""
        ...

    def reverse(self) -> AxesOrder:
        """Returns the AxesOrder which is the chronological reverse of the receiver."""
        ...


class AxesReference(enum.Enum):
    """AxesReference indicates whether we have intrinsic rotations, where the axes move with the object that is rotating, or extrinsic rotations, where they remain fixed in the world around the object."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.AxesReference"
    EXTRINSIC = enum.auto()
    INTRINSIC = enum.auto()
    def reverse(self) -> AxesReference:
        ...


class Axis(enum.Enum):
    """Axis enumerates the common X,Y,Z three-dimensional orthogonal axes."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Axis"
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()
    UNKNOWN = enum.auto()
    @staticmethod
    def fromIndex(index: int) -> Axis:
        ...

    index: int


class CurrentUnit(enum.Enum):
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.CurrentUnit"
    AMPS = enum.auto()
    MILLIAMPS = enum.auto()
    def toAmps(self, value: float) -> float:
        ...

    def toMilliAmps(self, value: float) -> float:
        ...

    def convert(self, value: float, unit: CurrentUnit) -> float:
        ...


class DistanceUnit(enum.Enum):
    """DistanceUnit represents a unit of measure of distance."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.DistanceUnit"
    METER = enum.auto()
    CM = enum.auto()
    MM = enum.auto()
    INCH = enum.auto()
    def fromMeters(self, meters: float) -> float:
        ...

    def fromInches(self, inches: float) -> float:
        ...

    def fromCm(self, cm: float) -> float:
        ...

    def fromMm(self, mm: float) -> float:
        ...

    def fromUnit(self, him: DistanceUnit, his: float) -> float:
        ...

    def toMeters(self, inOurUnits: float) -> float:
        ...

    def toInches(self, inOurUnits: float) -> float:
        ...

    def toCm(self, inOurUnits: float) -> float:
        ...

    def toMm(self, inOurUnits: float) -> float:
        ...

    @overload
    def toString(self, inOurUnits: float) -> str:
        ...
    @overload
    def toString(self) -> str:
        ...
    def toString(self, *args: Any, **kwargs: Any) -> Any:
        ...

    bVal: int
    infinity: float
    mmPerInch: float
    mPerInch: float


class MagneticFlux:
    """Instances of MagneticFlux represent a three-dimensional magnetic strength vector. Units are in tesla (NOT microtesla)."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.MagneticFlux"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, x: float, y: float, z: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toString(self) -> str:
        ...

    x: float
    """the flux in the X direction"""
    y: float
    """the flux in the Y direction"""
    z: float
    """the flux in the Z direction"""
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class MotionDetection:
    """A class that will notify listeners when a phone is in motion."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.MotionDetection"
    class MotionDetectionListener:
        __java__ = "org.firstinspires.ftc.robotcore.external.navigation.MotionDetection.MotionDetectionListener"
        def onMotionDetected(self, vector: float) -> None:
            ...

    class Vector:
        __java__ = "org.firstinspires.ftc.robotcore.external.navigation.MotionDetection.Vector"
        def magnitude(self) -> float:
            ...

        x: float
        y: float
        z: float

    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, detectionThreshold: float, rateLimitSeconds: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def filter(self, sensorEvent: Any) -> MotionDetection.Vector:
        """filter Taken straight from the google documentation for implementing a low pass filter for filtering out gravity. See https://developer.android.com/reference/android/hardware/SensorEvent#values"""
        ...

    def registerListener(self, listener: MotionDetection.MotionDetectionListener) -> None:
        """registerListener"""
        ...

    def purgeListeners(self) -> None:
        """purgeListeners"""
        ...

    def isAvailable(self) -> bool:
        """Is the required sensor available on this device?"""
        ...

    def startListening(self) -> None:
        """Start processing sensor data."""
        ...

    def stopListening(self) -> None:
        """Stop processing sensor data."""
        ...

    def notifyListeners(self, vector: float) -> None:
        ...

    def onSensorChanged(self, sensorEvent: Any) -> None:
        """********************************************************************************** Internal implementations of the SensorEventListener interface. ***********************************************************************************"""
        ...

    def onAccuracyChanged(self, sensor: Any, i: int) -> None:
        ...

    gravity: MotionDetection.Vector


class NavUtil:
    """NavUtil is a collection of utilities that provide useful manipulations of objects related to navigation."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.NavUtil"
    @overload
    @staticmethod
    def plus(a: Position, b: Position) -> Position:
        ...
    @overload
    @staticmethod
    def plus(a: Velocity, b: Velocity) -> Velocity:
        ...
    @overload
    @staticmethod
    def plus(a: Acceleration, b: Acceleration) -> Acceleration:
        ...
    @staticmethod
    def plus(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def minus(a: Position, b: Position) -> Position:
        ...
    @overload
    @staticmethod
    def minus(a: Velocity, b: Velocity) -> Velocity:
        ...
    @overload
    @staticmethod
    def minus(a: Acceleration, b: Acceleration) -> Acceleration:
        ...
    @staticmethod
    def minus(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def scale(p: Position, scale: float) -> Position:
        ...
    @overload
    @staticmethod
    def scale(v: Velocity, scale: float) -> Velocity:
        ...
    @overload
    @staticmethod
    def scale(a: Acceleration, scale: float) -> Acceleration:
        ...
    @staticmethod
    def scale(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def integrate(v: Velocity, dt: float) -> Position:
        ...
    @overload
    @staticmethod
    def integrate(a: Acceleration, dt: float) -> Velocity:
        ...
    @staticmethod
    def integrate(*args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def meanIntegrate(cur: Velocity, prev: Velocity) -> Position:
        """Integrate between two velocities to determine a change in position using an assumption that the mean of the velocities has been acting the entire interval."""
        ...
    @overload
    @staticmethod
    def meanIntegrate(cur: Acceleration, prev: Acceleration) -> Velocity:
        """Integrate between two accelerations to determine a change in velocity using an assumption that the mean of the accelerations has been acting the entire interval."""
        ...
    @staticmethod
    def meanIntegrate(*args: Any, **kwargs: Any) -> Any:
        ...


class Orientation:
    """Instances of Orientation represent a rotated stance in three-dimensional space by way of a set of three successive rotations. There are several ways that a particular orientation in three-space can be represented. One way is by specifying a (unit) directional vector about which the orientation is to occur, together with a rotation angle about that axis. This representation is unique up to the sign of the direction and angle; that is a rotation a about a vector v produces the same rotation as a rotation -a about the vector -v. While this manner of specifying a rotation is easy to visualize if the vector in question is one of the cardinal axes (ie: X,Y, or Z), many find it more difficult to visualize more complex rotations in this manner. An alternative, more common, way to represent a particular orientation in three-space is by means of indicating three angles of rotation about three successive axes. You might for example be familiar with the notions of heading, elevation, and bank angles for aircraft. Unfortunately, there are 24 different yet equivalent ways that a set of three rotational angles about three axes can represent the same effective rotation. As might be expected, this can be the source of much confusion. The 24 different representations break down as follows. First is the matter of the axes reference: is the coordinate system in which the referred-to rotational axes reside a coordinate system that moves with (and so remains fixed relative to) the object being rotated, or do the axes remain fixed relative to the world around the object and are unaffected by the object's rotational motion? The former situation is referred to as an AxesReference#INTRINSIC reference perspective while the latter is an AxesReference#EXTRINSIC perspective. Both points of view are equally valid methodologies, but one or the other may be more understandable or useful in a given application situation."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Orientation"
    class AngleSet(enum.Enum):
        """AngleSet is used to distinguish between the two sets of angles that will produce a given rotation in a given axes reference and a given axes order"""
        __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Orientation.AngleSet"
        THEONE = enum.auto()
        THEOTHER = enum.auto()

    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, axesReference: AxesReference, axesOrder: AxesOrder, angleUnit: AngleUnit, firstAngle: float, secondAngle: float, thirdAngle: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toAngleUnit(self, angleUnit: AngleUnit) -> Orientation:
        """Converts this Orientation to one with the indicated angular units."""
        ...

    def toAxesReference(self, axesReference: AxesReference) -> Orientation:
        """Converts the Orientation to an equivalent one with the indicted point of view."""
        ...

    def toAxesOrder(self, axesOrder: AxesOrder) -> Orientation:
        """Converts the Orientation to an equivalent one with the indicated ordering of axes"""
        ...

    def toString(self) -> str:
        ...

    @overload
    def getRotationMatrix(self) -> OpenGLMatrix:
        """Returns the rotation matrix associated with the receiver Orientation."""
        ...
    @overload
    @staticmethod
    def getRotationMatrix(axesReference: AxesReference, axesOrder: AxesOrder, unit: AngleUnit, firstAngle: float, secondAngle: float, thirdAngle: float) -> OpenGLMatrix:
        """Returns the rotation matrix associated with a particular set of three rotational angles."""
        ...
    def getRotationMatrix(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    @staticmethod
    def getOrientation(rot: MatrixF, axesReference: AxesReference, axesOrder: AxesOrder, unit: AngleUnit) -> Orientation:
        """Given a rotation matrix, and an AxesReference and AxesOrder, returns an orientation that would produce that rotation matrix."""
        ...
    @overload
    @staticmethod
    def getOrientation(rot: MatrixF, axesReference: AxesReference, axesOrder: AxesOrder, unit: AngleUnit, angleSet: Orientation.AngleSet) -> Orientation:
        """Given a rotation matrix, and an AxesReference and AxesOrder, returns an orientation that would produce that rotation matrix."""
        ...
    @staticmethod
    def getOrientation(*args: Any, **kwargs: Any) -> Any:
        ...

    axesReference: AxesReference
    """whether we have extrinsic or intrinsic rotations"""
    axesOrder: AxesOrder
    """the order of axes around which our three rotations occur"""
    angleUnit: AngleUnit
    """the unit in which the angles are expressed"""
    firstAngle: float
    """the chronologically first rotation made in the AxesOrder"""
    secondAngle: float
    """the chronologically second rotation made in the AxesOrder"""
    thirdAngle: float
    """the chronologically third rotation made in the AxesOrder"""
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class Pose2D:
    """Pose2D represents the position and heading of an object in 2D space."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Pose2D"
    def __init__(self, distanceUnit: DistanceUnit, x: float, y: float, headingUnit: AngleUnit, heading: float) -> None:
        """Creates a new Pose2D object."""
        ...

    def getX(self, unit: DistanceUnit) -> float:
        """This gets X in the desired distance unit"""
        ...

    def getY(self, unit: DistanceUnit) -> float:
        """This gets the Y in the desired distance unit"""
        ...

    def getHeading(self, unit: AngleUnit) -> float:
        """This gets the heading in the desired distance unit Be aware that this normalizes the angle to be between -PI and PI for RADIANS or between -180 and 180 for DEGREES"""
        ...

    def toString(self) -> str:
        """This returns a string representation of the object in a human readable format for debugging purposes."""
        ...

    x: float
    y: float
    distanceUnit: DistanceUnit
    heading: float
    headingUnit: AngleUnit


class Pose3D:
    """Pose3D represents the position and orientation of an object in 3D space."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Pose3D"
    def __init__(self, position: Position, orientation: YawPitchRollAngles) -> None:
        ...

    def toString(self) -> str:
        ...

    def getOrientation(self) -> YawPitchRollAngles:
        """A 3D orientation. The axis mapping is defined by the code that creates objects from this class. One should not assume that pitch, for example, is along the x axis. Consult the documentation of the API that returns a Pose3D for its axis mapping."""
        ...

    def getPosition(self) -> Position:
        """A 3D position."""
        ...

    position: Position
    orientation: YawPitchRollAngles


class Position:
    """Instances of Position represent a three-dimensional distance in a particular distance unit."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Position"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, unit: DistanceUnit, x: float, y: float, z: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toUnit(self, distanceUnit: DistanceUnit) -> Position:
        ...

    def toString(self) -> str:
        ...

    unit: DistanceUnit
    x: float
    y: float
    z: float
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class Quaternion:
    """A Quaternion can indicate an orientation in three-space without the trouble of possible gimbal-lock."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Quaternion"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, w: float, x: float, y: float, z: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    @staticmethod
    def identityQuaternion() -> Quaternion:
        ...

    @staticmethod
    def fromMatrix(m: MatrixF, acquisitionTime: int) -> Quaternion:
        ...

    def magnitude(self) -> float:
        ...

    def normalized(self) -> Quaternion:
        ...

    def conjugate(self) -> Quaternion:
        ...

    def congugate(self) -> Quaternion:
        ...

    def inverse(self) -> Quaternion:
        ...

    def multiply(self, q: Quaternion, acquisitionTime: int) -> Quaternion:
        ...

    def applyToVector(self, vector: VectorF) -> VectorF:
        """Apply this rotation to the given vector"""
        ...

    def toMatrix(self) -> MatrixF:
        ...

    def toOrientation(self, axesReference: AxesReference, axesOrder: AxesOrder, angleUnit: AngleUnit) -> Orientation:
        ...

    def toString(self) -> str:
        ...

    w: float
    x: float
    y: float
    z: float
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class Rotation(enum.Enum):
    """Rotation captures an angluar direction of movement"""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Rotation"
    CW = enum.auto()
    CCW = enum.auto()


class TempUnit(enum.Enum):
    """Instances of TempUnit enumerate a known different temperature scales"""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.TempUnit"
    CELSIUS = enum.auto()
    FARENHEIT = enum.auto()
    KELVIN = enum.auto()
    def fromCelsius(self, celsius: float) -> float:
        ...

    def fromKelvin(self, kelvin: float) -> float:
        ...

    def fromFarenheit(self, farenheit: float) -> float:
        ...

    def fromUnit(self, him: TempUnit, his: float) -> float:
        ...

    def toCelsius(self, inOurUnits: float) -> float:
        ...

    def toKelvin(self, inOurUnits: float) -> float:
        ...

    def toFarenheit(self, inOurUnits: float) -> float:
        ...

    bVal: int
    zeroCelsiusK: float
    zeroCelsiusF: float
    CperF: float


class Temperature:
    """Instances of Temperature represent a temperature in a particular temperature scale."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Temperature"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, unit: TempUnit, temperature: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toUnit(self, tempUnit: TempUnit) -> Temperature:
        ...

    unit: TempUnit
    temperature: float
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class UnnormalizedAngleUnit(enum.Enum):
    """An UnnormalizedAngleUnit represents angles in different units of measure and provides utility methods to convert across units. UnnormalizedAngleUnit does not maintain angle information internally, but only helps organize and use angle measures that may be maintained separately across various contexts."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.UnnormalizedAngleUnit"
    DEGREES = enum.auto()
    RADIANS = enum.auto()
    @overload
    def fromDegrees(self, degrees: float) -> float:
        ...
    @overload
    def fromDegrees(self, degrees: float) -> float:
        ...
    def fromDegrees(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def fromRadians(self, radians: float) -> float:
        ...
    @overload
    def fromRadians(self, radians: float) -> float:
        ...
    def fromRadians(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def fromUnit(self, them: UnnormalizedAngleUnit, theirs: float) -> float:
        ...
    @overload
    def fromUnit(self, them: UnnormalizedAngleUnit, theirs: float) -> float:
        ...
    @overload
    def fromUnit(self, them: AngleUnit, theirs: float) -> float:
        ...
    @overload
    def fromUnit(self, them: AngleUnit, theirs: float) -> float:
        ...
    def fromUnit(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def toDegrees(self, inOurUnits: float) -> float:
        ...
    @overload
    def toDegrees(self, inOurUnits: float) -> float:
        ...
    def toDegrees(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def toRadians(self, inOurUnits: float) -> float:
        ...
    @overload
    def toRadians(self, inOurUnits: float) -> float:
        ...
    def toRadians(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getNormalized(self) -> AngleUnit:
        ...

    bVal: int


class Velocity:
    """Instances of Velocity represent the derivative of Position over time."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.Velocity"
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, unit: DistanceUnit, xVeloc: float, yVeloc: float, zVeloc: float, acquisitionTime: int) -> None:
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def toUnit(self, distanceUnit: DistanceUnit) -> Velocity:
        ...

    def toString(self) -> str:
        ...

    unit: DistanceUnit
    """The distance units in which this velocity is expressed. The time unit is always \"per second\"."""
    xVeloc: float
    yVeloc: float
    zVeloc: float
    acquisitionTime: int
    """the time on the System.nanoTime() clock at which the data was acquired. If no timestamp is associated with this particular set of data, this value is zero."""


class VoltageUnit(enum.Enum):
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.VoltageUnit"
    VOLTS = enum.auto()
    MILLIVOLTS = enum.auto()
    def toVolts(self, value: float) -> float:
        ...

    def toMilliVolts(self, value: float) -> float:
        ...

    def convert(self, value: float, unit: VoltageUnit) -> float:
        ...


class YawPitchRollAngles:
    """A simplified view of the orientation of an object in 3D space."""
    __java__ = "org.firstinspires.ftc.robotcore.external.navigation.YawPitchRollAngles"
    def __init__(self, angleUnit: AngleUnit, yaw: float, pitch: float, roll: float, acquisitionTime: int) -> None:
        """See the top-level class Javadoc for the format that these angles need to be in."""
        ...

    @overload
    def getYaw(self) -> float:
        ...
    @overload
    def getYaw(self, angleUnit: AngleUnit) -> float:
        ...
    def getYaw(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getPitch(self) -> float:
        ...
    @overload
    def getPitch(self, angleUnit: AngleUnit) -> float:
        ...
    def getPitch(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @overload
    def getRoll(self) -> float:
        ...
    @overload
    def getRoll(self, angleUnit: AngleUnit) -> float:
        ...
    def getRoll(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def getAcquisitionTime(self) -> int:
        ...

    def toString(self) -> str:
        ...
