from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, TYPE_CHECKING, overload
import enum

from ftc.opmode import OpModeManagerNotifier
if TYPE_CHECKING:
    from ftc.hardware import CameraName, WebcamName
    from ftc.internal import BuiltinCameraDirection, CameraCalibration, Consumer, Continuation, MatrixF, OpenGLMatrix, VectorF
    from ftc.navigation import AngleUnit, DistanceUnit, Pose3D, Position, Quaternion, YawPitchRollAngles
    from ftc.opmode import OpMode
    from ftc.util import SortOrder

T = TypeVar("T")
class CameraStreamSource:
    """Interface representing an on-demand source of frames (i.e., bitmaps)."""
    __java__ = "org.firstinspires.ftc.robotcore.external.stream.CameraStreamSource"
    def getFrameBitmap(self, continuation: Continuation[Consumer[Any]]) -> None:
        """Requests a single frame bitmap. Here's a brief example implementation using the now-removed VuforiaLocalizer class:"""
        ...


class VisionPortal(CameraStreamSource):
    __java__ = "org.firstinspires.ftc.vision.VisionPortal"
    class StreamFormat(enum.Enum):
        """StreamFormat is only applicable if using a webcam"""
        __java__ = "org.firstinspires.ftc.vision.VisionPortal.StreamFormat"
        YUY2 = enum.auto()
        MJPEG = enum.auto()
        eocvStreamFormat: Any

    class MultiPortalLayout(enum.Enum):
        """If you are using multiple vision portals with live previews concurrently, you need to split up the screen to make room for both portals"""
        __java__ = "org.firstinspires.ftc.vision.VisionPortal.MultiPortalLayout"
        VERTICAL = enum.auto()
        HORIZONTAL = enum.auto()

    class Builder:
        __java__ = "org.firstinspires.ftc.vision.VisionPortal.Builder"
        @overload
        def setCamera(self, camera: CameraName) -> VisionPortal.Builder:
            """Configure the portal to use a webcam"""
            ...
        @overload
        def setCamera(self, cameraDirection: BuiltinCameraDirection) -> VisionPortal.Builder:
            """Configure the portal to use an internal camera"""
            ...
        def setCamera(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def setStreamFormat(self, streamFormat: VisionPortal.StreamFormat) -> VisionPortal.Builder:
            """Configure the vision portal to stream from the camera in a certain image format THIS APPLIES TO WEBCAMS ONLY!"""
            ...

        def enableLiveView(self, enableLiveView: bool) -> VisionPortal.Builder:
            """Configure the vision portal to use (or not to use) a live camera preview NB: When using MultiPortal, you MUST use #setLiveViewContainerId(int) instead!"""
            ...

        def setAutoStopLiveView(self, autoPause: bool) -> VisionPortal.Builder:
            """Configure whether the portal should automatically pause the live camera view if all attached processors are disabled; this can save computational resources"""
            ...

        def setLiveViewContainerId(self, liveViewContainerId: int) -> VisionPortal.Builder:
            """A more advanced version of #enableLiveView(boolean); allows you to specify a specific view ID to use as a container, rather than just using the default one"""
            ...

        def setCameraResolution(self, cameraResolution: Any) -> VisionPortal.Builder:
            """Specify the resolution in which to stream images from the camera. To find out what resolutions your camera supports, simply call this with some random numbers (e.g. new Size(4634, 11115)) and the error message will provide a list of supported resolutions."""
            ...

        def addProcessor(self, processor: VisionProcessor) -> VisionPortal.Builder:
            """Send a VisionProcessor into this portal to allow it to process camera frames."""
            ...

        def addProcessors(self, *processors: VisionProcessor) -> VisionPortal.Builder:
            """Send multiple VisionProcessors into this portal to allow them to process camera frames."""
            ...

        def setAutoStartStreamOnBuild(self, autoStartStreamOnBuild: bool) -> VisionPortal.Builder:
            """Set whether the VisionPortal should automatically start streaming when you issue a .build() call on the Builder object."""
            ...

        def setShowStatsOverlay(self, showStatsOverlay: bool) -> VisionPortal.Builder:
            """Set whether the statistics overlay should be shown on the LiveView"""
            ...

        def build(self) -> VisionPortal:
            """Actually create the VisionPortal i.e. spool up the camera and LiveView and begin sending image data to any attached VisionProcessors"""
            ...

    class CameraState(enum.Enum):
        """The various states that the camera may be in at any given time"""
        __java__ = "org.firstinspires.ftc.vision.VisionPortal.CameraState"
        OPENING_CAMERA_DEVICE = enum.auto()
        CAMERA_DEVICE_READY = enum.auto()
        STARTING_STREAM = enum.auto()
        STREAMING = enum.auto()
        STOPPING_STREAM = enum.auto()
        CLOSING_CAMERA_DEVICE = enum.auto()
        CAMERA_DEVICE_CLOSED = enum.auto()
        ERROR = enum.auto()

    @staticmethod
    def makeMultiPortalView(numPortals: int, mpl: VisionPortal.MultiPortalLayout) -> list[int]:
        """Split up the screen for using multiple vision portals with LiveViews simultaneously"""
        ...

    @overload
    @staticmethod
    def easyCreateWithDefaults(cameraDirection: BuiltinCameraDirection, *processors: VisionProcessor) -> VisionPortal:
        """Create a VisionPortal for an internal camera using default configuration parameters, and skipping the use of the Builder pattern."""
        ...
    @overload
    @staticmethod
    def easyCreateWithDefaults(cameraName: CameraName, *processors: VisionProcessor) -> VisionPortal:
        """Create a VisionPortal for a webcam using default configuration parameters, and skipping the use of the Builder pattern."""
        ...
    @staticmethod
    def easyCreateWithDefaults(*args: Any, **kwargs: Any) -> Any:
        ...

    def setProcessorEnabled(self, processor: VisionProcessor, enabled: bool) -> None:
        """Enable or disable a VisionProcessor that is attached to this portal. Disabled processors are not passed new image data and do not consume any computational resources. Of course, they also don't give you any useful data when disabled. This takes effect immediately (on the next frame interval)"""
        ...

    def getProcessorEnabled(self, processor: VisionProcessor) -> bool:
        """Queries whether a given processor is enabled"""
        ...

    def getCameraState(self) -> VisionPortal.CameraState:
        """Query the current state of the camera (e.g. is a streaming session in flight?)"""
        ...

    def saveNextFrameRaw(self, filename: str) -> None:
        ...

    def stopStreaming(self) -> None:
        """Stop the streaming session. This is an asynchronous call which does not take effect immediately. You may use #getCameraState() to monitor for when this command has taken effect. If you call #resumeStreaming() before the operation is complete, it will SYNCHRONOUSLY await completion of the stop command Stopping the streaming session is a good way to save computational resources if there may be long (e.g. 10+ second) periods of match play in which vision processing is not required. When streaming is stopped, no new image data is acquired from the camera and any attached VisionProcessors will lie dormant until such time as #resumeStreaming() is called. Stopping and starting the stream can take a second or two, and thus is not advised for use cases where instantaneously enabling/disabling vision processing is required."""
        ...

    def resumeStreaming(self) -> None:
        """Resume the streaming session if previously stopped by #stopStreaming(). This is an asynchronous call which does not take effect immediately. If you call #stopStreaming() before the operation is complete, it will SYNCHRONOUSLY await completion of the resume command. See notes about use case on #stopStreaming()"""
        ...

    def stopLiveView(self) -> None:
        """Temporarily stop the LiveView on the RC screen. This DOES NOT affect the ability to get a camera frame on the Driver Station's \"Camera Stream\" feature. This has no effect if you didn't set up a LiveView. Stopping the LiveView is recommended during competition to save CPU resources when a LiveView is not required for debugging purposes."""
        ...

    def resumeLiveView(self) -> None:
        """Start the LiveView again, if it was previously stopped with #stopLiveView() This has no effect if you didn't set up a LiveView."""
        ...

    def getFps(self) -> float:
        """Get the current rate at which frames are passing through the vision portal (and all processors therein) per second - frames per second"""
        ...

    def getCameraControl(self, controlType: type[T]) -> T:
        """Get a camera control handle ONLY APPLICABLE TO WEBCAMS"""
        ...

    def setActiveCamera(self, webcamName: WebcamName) -> None:
        """Switches the active camera to the indicated camera. ONLY APPLICABLE IF USING A SWITCHABLE WEBCAM"""
        ...

    def getActiveCamera(self) -> WebcamName:
        """Returns the name of the currently active camera ONLY APPLIES IF USING A SWITCHABLE WEBCAM"""
        ...

    def close(self) -> None:
        """Teardown everything prior to the end of the OpMode (perhaps to save resources) at which point it will be torn down automagically anyway. This will stop all vision related processing, shut down the camera, and remove the LiveView. A closed portal may not be re-opened: if you wish to use the camera again, you must make a new portal"""
        ...

    DEFAULT_VIEW_CONTAINER_ID: int


class VisionPortalImpl(VisionPortal):
    __java__ = "org.firstinspires.ftc.vision.VisionPortalImpl"
    class OpModeNotificationsListener(OpModeManagerNotifier.Notifications):
        __java__ = "org.firstinspires.ftc.vision.VisionPortalImpl.OpModeNotificationsListener"
        def onOpModePreInit(self, opMode: OpMode) -> None:
            ...

        def onOpModePreStart(self, opMode: OpMode) -> None:
            ...

        def onOpModePostStop(self, opMode: OpMode) -> None:
            ...

    class ProcessingPipeline:
        __java__ = "org.firstinspires.ftc.vision.VisionPortalImpl.ProcessingPipeline"
        def __init__(self) -> None:
            ...

        def init(self, firstFrame: Any) -> None:
            ...

        def processFrame(self, input: Any, captureTimeNanos: int) -> Any:
            ...

        def onDrawFrame(self, canvas: Any, onscreenWidth: int, onscreenHeight: int, scaleBmpPxToCanvasPx: float, scaleCanvasDensity: float, userContext: object) -> None:
            ...

    def __init__(self, camera: CameraName, cameraMonitorViewId: int, autoPauseCameraMonitor: bool, cameraResolution: Any, webcamStreamFormat: VisionPortal.StreamFormat, autoStartStream: bool, showStats: bool, processors: list[VisionProcessor]) -> None:
        ...

    def startCamera(self) -> None:
        ...

    def createCamera(self, cameraName: CameraName, cameraMonitorViewId: int) -> None:
        ...

    def setProcessorEnabled(self, processor: VisionProcessor, enabled: bool) -> None:
        ...

    def getProcessorEnabled(self, processor: VisionProcessor) -> bool:
        ...

    def getCameraState(self) -> VisionPortal.CameraState:
        ...

    def setActiveCamera(self, webcamName: WebcamName) -> None:
        ...

    def getActiveCamera(self) -> WebcamName:
        ...

    def getCameraControl(self, controlType: type[T]) -> T:
        ...

    def getFrameBitmap(self, continuation: Continuation[Consumer[Any]]) -> None:
        ...

    def saveNextFrameRaw(self, filepath: str) -> None:
        ...

    def stopStreaming(self) -> None:
        ...

    def resumeStreaming(self) -> None:
        ...

    def stopLiveView(self) -> None:
        ...

    def resumeLiveView(self) -> None:
        ...

    def getFps(self) -> float:
        ...

    def close(self) -> None:
        ...

    camera: Any
    cameraMonitorViewId: int
    cameraState: VisionPortal.CameraState
    processors: list[VisionProcessor]
    processorsEnabled: list[bool]
    calibration: CameraCalibration
    autoPauseCameraMonitor: bool
    autoStartStream: bool
    showStats: bool
    userStateSemaphore: Any
    cameraResolution: Any
    webcamStreamFormat: VisionPortal.StreamFormat
    CAMERA_ROTATION: Any
    captureNextFrame: str
    captureFrameMtx: object
    opModeNotificationsListener: VisionPortalImpl.OpModeNotificationsListener
    viewUseMtx: object
    viewsInUse: list[int]


class VisionProcessorInternal:
    """Internal interface"""
    __java__ = "org.firstinspires.ftc.vision.VisionProcessorInternal"
    def init(self, width: int, height: int, calibration: CameraCalibration) -> None:
        ...

    def processFrame(self, frame: Any, captureTimeNanos: int) -> object:
        ...

    def onDrawFrame(self, canvas: Any, onscreenWidth: int, onscreenHeight: int, scaleBmpPxToCanvasPx: float, scaleCanvasDensity: float, userContext: object) -> None:
        ...


class VisionProcessor(VisionProcessorInternal):
    """May be attached to a VisionPortal to run image processing"""
    __java__ = "org.firstinspires.ftc.vision.VisionProcessor"


class AprilTagCanvasAnnotator:
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagCanvasAnnotator"
    class LinePaint:
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagCanvasAnnotator.LinePaint"
        def __init__(self, color: int) -> None:
            ...

    def __init__(self, cameraMatrix: Any) -> None:
        ...

    def noteDrawParams(self, bmpPxToCanvasPx: float, canvasDensityScale: float) -> None:
        ...

    def drawAxisMarker(self, detection: AprilTagDetection, canvas: Any, tagsize: float) -> None:
        """Draw a 3D axis marker on a detection. (Similar to what Vuforia does)"""
        ...

    def draw3dCubeMarker(self, detection: AprilTagDetection, canvas: Any, tagsize: float) -> None:
        """Draw a 3D cube marker on a detection"""
        ...

    def drawOutlineMarker(self, detection: AprilTagDetection, canvas: Any, tagsize: float) -> None:
        """Draw an outline marker on the detection"""
        ...

    def drawTagID(self, detection: AprilTagDetection, canvas: Any) -> None:
        """Draw the Tag's ID on the tag"""
        ...

    cameraMatrix: Any
    bmpPxToCanvasPx: float
    canvasDensityScale: float
    redAxisPaint: AprilTagCanvasAnnotator.LinePaint
    greenAxisPaint: AprilTagCanvasAnnotator.LinePaint
    blueAxisPaint: AprilTagCanvasAnnotator.LinePaint
    boxPillarPaint: AprilTagCanvasAnnotator.LinePaint
    boxTopPaint: AprilTagCanvasAnnotator.LinePaint
    textPaint: Any
    rectPaint: Any


class AprilTagDetection:
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagDetection"
    def __init__(self, id: int, hamming: int, decisionMargin: float, center: Any, corners: list[Any], metadata: AprilTagMetadata, ftcPose: AprilTagPoseFtc, rawPose: AprilTagPoseRaw, robotPose: Pose3D, frameAcquisitionNanoTime: int) -> None:
        ...

    id: int
    """The numerical ID of the detection"""
    hamming: int
    """The number of bits corrected when reading the tag ID payload"""
    decisionMargin: float
    center: Any
    corners: list[Any]
    metadata: AprilTagMetadata
    ftcPose: AprilTagPoseFtc
    rawPose: AprilTagPoseRaw
    robotPose: Pose3D
    frameAcquisitionNanoTime: int


class AprilTagGameDatabase:
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagGameDatabase"
    @staticmethod
    def getCurrentGameTagLibrary() -> AprilTagLibrary:
        """Get the AprilTagLibrary for the current season game, plus sample tags"""
        ...

    @staticmethod
    def getCenterStageTagLibrary() -> AprilTagLibrary:
        """Get the AprilTagLibrary for the Center Stage FTC game"""
        ...

    @staticmethod
    def getIntoTheDeepTagLibrary() -> AprilTagLibrary:
        """Get the AprilTagLibrary for the Into The Deep FTC game"""
        ...

    @staticmethod
    def getDecodeTagLibrary() -> AprilTagLibrary:
        """Get the AprilTagLibrary for the Decode FTC game"""
        ...

    @staticmethod
    def getSampleTagLibrary() -> AprilTagLibrary:
        """Get the AprilTagLibrary for the tags used in the sample OpModes"""
        ...


class AprilTagLibrary:
    """A tag library contains metadata about tags such as their ID, name, size, and 6DOF position on the field"""
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagLibrary"
    class Builder:
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagLibrary.Builder"
        def setAllowOverwrite(self, allowOverwrite: bool) -> AprilTagLibrary.Builder:
            """Set whether to allow overwriting an existing entry in the tag library with a new entry of the same ID"""
            ...

        @overload
        def addTag(self, aprilTagMetadata: AprilTagMetadata) -> AprilTagLibrary.Builder:
            """Add a tag to this tag library"""
            ...
        @overload
        def addTag(self, id: int, name: str, size: float, fieldPosition: VectorF, distanceUnit: DistanceUnit, fieldOrientation: Quaternion) -> AprilTagLibrary.Builder:
            """Add a tag to this tag library"""
            ...
        @overload
        def addTag(self, id: int, name: str, size: float, distanceUnit: DistanceUnit) -> AprilTagLibrary.Builder:
            """Add a tag to this tag library"""
            ...
        def addTag(self, *args: Any, **kwargs: Any) -> Any:
            ...

        def addTags(self, library: AprilTagLibrary) -> AprilTagLibrary.Builder:
            """Add multiple tags to this tag library"""
            ...

        def build(self) -> AprilTagLibrary:
            """Create an AprilTagLibrary object from the specified tags"""
            ...

    def getAllTags(self) -> list[AprilTagMetadata]:
        """Get the metadata of all tags in this library"""
        ...

    def lookupTag(self, id: int) -> AprilTagMetadata:
        """Get the metadata for a specific tag in this library"""
        ...


class AprilTagMetadata:
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagMetadata"
    @overload
    def __init__(self, id: int, name: str, tagsize: float, fieldPosition: VectorF, distanceUnit: DistanceUnit, fieldOrientation: Quaternion) -> None:
        """Add a tag to this tag library"""
        ...
    @overload
    def __init__(self, id: int, name: str, tagsize: float, distanceUnit: DistanceUnit) -> None:
        """Add a tag to this tag library"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    id: int
    tagsize: float
    name: str
    distanceUnit: DistanceUnit
    fieldPosition: VectorF
    fieldOrientation: Quaternion


class AprilTagPoseFtc:
    """AprilTagPoseFtc represents the AprilTag's position in space, relative to the camera. It is a realignment of the raw AprilTag Pose to be consistent with a forward-looking camera on an FTC robot. Also includes additional derived values to simplify driving towards any Tag. Note: These member definitions describe the camera Lens as the reference point for axis measurements. This measurement may be off by the distance from the lens to the image sensor itself. For most webcams this is a reasonable approximation."""
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagPoseFtc"
    def __init__(self, x: float, y: float, z: float, yaw: float, pitch: float, roll: float, range: float, bearing: float, elevation: float) -> None:
        ...

    x: float
    """X translation of AprilTag, relative to camera lens. Measured sideways (Horizontally in camera image) the positive X axis extends out to the right of the camera viewpoint. An x value of zero implies that the Tag is centered between the left and right sides of the Camera image."""
    y: float
    """Y translation of AprilTag, relative to camera lens. Measured forwards (Horizontally in camera image) the positive Y axis extends out in the direction the camera is pointing. A y value of zero implies that the Tag is touching (aligned with) the lens of the camera, which is physically unlikley. This value should always be positive."""
    z: float
    """Z translation of AprilTag, relative to camera lens. Measured upwards (Vertically in camera image) the positive Z axis extends Upwards in the camera viewpoint. A z value of zero implies that the Tag is centered between the top and bottom of the camera image."""
    yaw: float
    """Rotation of AprilTag around the Z axis. Right-Hand-Rule defines positive Yaw rotation as Counter-Clockwise when viewed from above. A yaw value of zero implies that the camera is directly in front of the Tag, as viewed from above."""
    pitch: float
    """Rotation of AprilTag around the X axis. Right-Hand-Rule defines positive Pitch rotation as the Tag Image face twisting down when viewed from the camera. A pitch value of zero implies that the camera is directly in front of the Tag, as viewed from the side."""
    roll: float
    """Rotation of AprilTag around the Y axis. Right-Hand-Rule defines positive Roll rotation as the Tag Image rotating Clockwise when viewed from the camera. A roll value of zero implies that the Tag image is alligned squarely and upright, when viewed in the camera image frame."""
    range: float
    """Range, (Distance), from the Camera lens to the center of the Tag, as measured along the X-Y plane (across the ground)."""
    bearing: float
    """Bearing, or Horizontal Angle, from the \"camera center-line\", to the \"line joining the Camera lens and the Center of the Tag\". This angle is measured across the X-Y plane (across the ground). A positive Bearing indicates that the robot must employ a positive Yaw (rotate counter clockwise) in order to point towards the target."""
    elevation: float
    """Elevation, (Vertical Angle), from \"the camera center-line\", to \"the line joining the Camera Lens and the Center of the Tag\". A positive Elevation indicates that the robot must employ a positive Pitch (tilt up) in order to point towards the target."""


class AprilTagPoseRaw:
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagPoseRaw"
    def __init__(self, x: float, y: float, z: float, R: MatrixF) -> None:
        ...

    x: float
    """X translation"""
    y: float
    """Y translation"""
    z: float
    """Z translation"""
    R: MatrixF
    """3x3 rotation matrix"""


class AprilTagProcessor(VisionProcessor):
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessor"
    class TagFamily(enum.Enum):
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessor.TagFamily"
        TAG_36h11 = enum.auto()
        TAG_25h9 = enum.auto()
        TAG_16h5 = enum.auto()
        TAG_standard41h12 = enum.auto()
        ATLibTF: Any

    class Builder:
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessor.Builder"
        def setCameraPose(self, position: Position, orientation: YawPitchRollAngles) -> AprilTagProcessor.Builder:
            """Set the camera pose relative to the robot origin."""
            ...

        def setLensIntrinsics(self, fx: float, fy: float, cx: float, cy: float) -> AprilTagProcessor.Builder:
            """Set the camera calibration parameters (needed for accurate 6DOF pose unless the SDK has a built in calibration for your camera)"""
            ...

        def setSuppressCalibrationWarnings(self, suppressCalibrationWarnings: bool) -> AprilTagProcessor.Builder:
            """Set whether any warnings about camera calibration should be suppressed"""
            ...

        def setTagFamily(self, tagFamily: AprilTagProcessor.TagFamily) -> AprilTagProcessor.Builder:
            """Set the tag family this detector will be used to detect (it can only be used for one tag family at a time)"""
            ...

        def setTagLibrary(self, tagLibrary: AprilTagLibrary) -> AprilTagProcessor.Builder:
            """Inform the detector about known tags. The tag library is used to allow solving for 6DOF pose, based on the physical size of the tag. Tags which are not in the library will not have their pose solved for"""
            ...

        def setOutputUnits(self, distanceUnit: DistanceUnit, angleUnit: AngleUnit) -> AprilTagProcessor.Builder:
            """Set the units you want translation and rotation data provided in, inside any AprilTagPoseRaw or AprilTagPoseFtc objects"""
            ...

        def setDrawAxes(self, drawAxes: bool) -> AprilTagProcessor.Builder:
            """Set whether to draw a 3D crosshair on the tag (what Vuforia did)"""
            ...

        def setDrawCubeProjection(self, drawCube: bool) -> AprilTagProcessor.Builder:
            """Set whether to draw a 3D cube projecting from the tag"""
            ...

        def setDrawTagOutline(self, drawOutline: bool) -> AprilTagProcessor.Builder:
            """Set whether to draw a 2D outline around the tag detection"""
            ...

        def setDrawTagID(self, drawTagId: bool) -> AprilTagProcessor.Builder:
            """Set whether to annotate the tag detection with its ID"""
            ...

        def setNumThreads(self, threads: int) -> AprilTagProcessor.Builder:
            """Set the number of threads the tag detector should use"""
            ...

        def build(self) -> AprilTagProcessor:
            """Create a VisionProcessor object which may be attached to a org.firstinspires.ftc.vision.VisionPortal using org.firstinspires.ftc.vision.VisionPortal.Builder#addProcessor(VisionProcessor)"""
            ...

    class PoseSolver(enum.Enum):
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessor.PoseSolver"
        APRILTAG_BUILTIN = enum.auto()
        OPENCV_ITERATIVE = enum.auto()
        OPENCV_SOLVEPNP_EPNP = enum.auto()
        OPENCV_IPPE = enum.auto()
        OPENCV_IPPE_SQUARE = enum.auto()
        OPENCV_SQPNP = enum.auto()
        code: int

    @staticmethod
    def easyCreateWithDefaults() -> AprilTagProcessor:
        ...

    def setDecimation(self, decimation: float) -> None:
        """Set the detector decimation Higher decimation increases frame rate at the expense of reduced range"""
        ...

    def setPoseSolver(self, poseSolver: AprilTagProcessor.PoseSolver) -> None:
        """Specify the method used to calculate 6DOF pose from the tag corner positions once found by the AprilTag algorithm"""
        ...

    def getPerTagAvgPoseSolveTime(self) -> int:
        """Get the average time in milliseconds the currently set pose solver is taking to converge on a solution PER TAG. Some pose solvers are much more expensive than others..."""
        ...

    def getDetections(self) -> list[AprilTagDetection]:
        """Get a list containing the latest detections, which may be stale i.e. the same as the last time you called this"""
        ...

    def getFreshDetections(self) -> list[AprilTagDetection]:
        """Get a list containing detections that were detected SINCE THE PREVIOUS CALL to this method, or NULL if no new detections are available. This is useful to avoid re-processing the same detections multiple times."""
        ...

    THREADS_DEFAULT: int


class AprilTagProcessorImpl(AprilTagProcessor):
    __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessorImpl"
    class Pose:
        __java__ = "org.firstinspires.ftc.vision.apriltag.AprilTagProcessorImpl.Pose"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, rvec: Any, tvec: Any) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        rvec: Any
        tvec: Any

    def __init__(self, robotInCameraFrame: OpenGLMatrix, fx: float, fy: float, cx: float, cy: float, outputUnitsLength: DistanceUnit, outputUnitsAngle: AngleUnit, tagLibrary: AprilTagLibrary, drawAxes: bool, drawCube: bool, drawOutline: bool, drawTagID: bool, tagFamily: AprilTagProcessor.TagFamily, threads: int, suppressCalibrationWarnings: bool) -> None:
        ...

    def finalize(self) -> None:
        ...

    def init(self, width: int, height: int, calibration: CameraCalibration) -> None:
        ...

    def processFrame(self, input: Any, captureTimeNanos: int) -> object:
        ...

    def runAprilTagDetectorForMultipleTagSizes(self, captureTimeNanos: int) -> list[AprilTagDetection]:
        ...

    def onDrawFrame(self, canvas: Any, onscreenWidth: int, onscreenHeight: int, scaleBmpPxToCanvasPx: float, scaleCanvasDensity: float, userContext: object) -> None:
        ...

    def setDecimation(self, decimation: float) -> None:
        ...

    def setPoseSolver(self, poseSolver: AprilTagProcessor.PoseSolver) -> None:
        ...

    def getPerTagAvgPoseSolveTime(self) -> int:
        ...

    def getDetections(self) -> list[AprilTagDetection]:
        ...

    def getFreshDetections(self) -> list[AprilTagDetection]:
        ...

    def constructMatrix(self) -> None:
        ...

    @staticmethod
    def aprilTagPoseToOpenCvPose(aprilTagPose: AprilTagPoseRaw) -> AprilTagProcessorImpl.Pose:
        """Converts an AprilTag pose to an OpenCV pose"""
        ...

    @staticmethod
    def poseFromTrapezoid(points: list[Any], cameraMatrix: Any, tagsize: float, solveMethod: int) -> AprilTagProcessorImpl.Pose:
        """Extracts 6DOF pose from a trapezoid, using a camera intrinsics matrix and the original size of the tag."""
        ...

    TAG: str


class Circle:
    """Stores the center Point and radius of a circle"""
    __java__ = "org.firstinspires.ftc.vision.opencv.Circle"
    @overload
    def __init__(self, center: Any, radius: float) -> None:
        """Create a new Circle"""
        ...
    @overload
    def __init__(self, x: float, y: float, radius: float) -> None:
        """Create a new Circle"""
        ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def getCenter(self) -> Any:
        """Get the center Point of the Circle"""
        ...

    def getRadius(self) -> float:
        """Get the radius of the Circle"""
        ...

    def getX(self) -> float:
        """Get the x position of the Circle"""
        ...

    def getY(self) -> float:
        """Get the y position of the Circle"""
        ...


class ColorBlobLocatorProcessor(VisionProcessor):
    """The ColorBlobLocatorProcessor finds \"blobs\" of a user-specified color in the image. You can restrict the search area to a specified Region of Interest (ROI)."""
    __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor"
    class Builder:
        """Class supporting construction of a ColorBlobLocatorProcessor"""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.Builder"
        def setDrawContours(self, drawContours: bool) -> ColorBlobLocatorProcessor.Builder:
            """Sets whether to draw the contour outline for the detected blobs on the camera preview. This can be helpful for debugging thresholding."""
            ...

        def setBoxFitColor(self, color: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the color used to draw the \"best fit\" bounding boxes for blobs"""
            ...

        def setCircleFitColor(self, color: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the color used to draw the enclosing circle around blobs"""
            ...

        def setRoiColor(self, color: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the color used to draw the ROI on the camera preview"""
            ...

        def setContourColor(self, color: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the color used to draw blob contours on the camera preview"""
            ...

        def setTargetColorRange(self, colorRange: ColorRange) -> ColorBlobLocatorProcessor.Builder:
            """Set the color range used to find blobs"""
            ...

        def setContourMode(self, contourMode: ColorBlobLocatorProcessor.ContourMode) -> ColorBlobLocatorProcessor.Builder:
            """Set the contour mode which will be used when generating the results provided by #getBlobs()"""
            ...

        def setRoi(self, roi: ImageRegion) -> ColorBlobLocatorProcessor.Builder:
            """Set the Region of Interest on which to perform blob detection"""
            ...

        def setBlurSize(self, blurSize: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the size of the blur kernel. Blurring can improve color thresholding results by smoothing color variation."""
            ...

        def setMorphOperationType(self, morphOperationType: ColorBlobLocatorProcessor.MorphOperationType) -> ColorBlobLocatorProcessor.Builder:
            """Set the type of morph operation to perform. Only relevant if using both erosion and dilation."""
            ...

        def setErodeSize(self, erodeSize: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the size of the Erosion operation performed after applying the color threshold. Erosion eats away at the mask, reducing noise by eliminating super small areas, but also reduces the contour areas of everything a little bit."""
            ...

        def setDilateSize(self, dilateSize: int) -> ColorBlobLocatorProcessor.Builder:
            """Set the size of the Dilation operation performed after applying the Erosion operation. Dilation expands mask areas, making up for shrinkage caused during erosion, and can also clean up results by closing small interior gaps in the mask."""
            ...

        def build(self) -> ColorBlobLocatorProcessor:
            """Construct a ColorBlobLocatorProcessor object using previously set parameters"""
            ...

    class ContourMode(enum.Enum):
        """Determines what you get in #getBlobs()"""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.ContourMode"
        EXTERNAL_ONLY = enum.auto()
        ALL_FLATTENED_HIERARCHY = enum.auto()

    class MorphOperationType(enum.Enum):
        """Determines which compound morphological operation to perform on blobs"""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.MorphOperationType"
        OPENING = enum.auto()
        CLOSING = enum.auto()

    class BlobCriteria(enum.Enum):
        """The criteria used for filtering and sorting."""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.BlobCriteria"
        BY_CONTOUR_AREA = enum.auto()
        BY_DENSITY = enum.auto()
        BY_ASPECT_RATIO = enum.auto()
        BY_ARC_LENGTH = enum.auto()
        BY_CIRCULARITY = enum.auto()

    class BlobFilter:
        """Class describing how to filter blobs."""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.BlobFilter"
        def __init__(self, criteria: ColorBlobLocatorProcessor.BlobCriteria, minValue: float, maxValue: float) -> None:
            ...

        criteria: ColorBlobLocatorProcessor.BlobCriteria
        minValue: float
        maxValue: float

    class BlobSort:
        """Class describing how to sort blobs."""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.BlobSort"
        def __init__(self, criteria: ColorBlobLocatorProcessor.BlobCriteria, sortOrder: SortOrder) -> None:
            ...

        criteria: ColorBlobLocatorProcessor.BlobCriteria
        sortOrder: SortOrder

    class Blob:
        """Class describing a Blob of color found inside the image"""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.Blob"
        def getContour(self) -> Any:
            """Get the OpenCV contour for this blob"""
            ...

        def getContourPoints(self) -> list[Any]:
            """Get the contour points for this blob"""
            ...

        def getContourAsFloat(self) -> Any:
            """Get this contour as a MatOfPoint2f"""
            ...

        def getContourArea(self) -> int:
            """Get the area enclosed by this blob's contour"""
            ...

        def getDensity(self) -> float:
            """Get the density of this blob, i.e. ratio of contour area to convex hull area"""
            ...

        def getAspectRatio(self) -> float:
            """Get the aspect ratio of this blob, i.e. the ratio of longer side of the bounding box to the shorter side"""
            ...

        def getBoxFit(self) -> Any:
            """Get a \"best fit\" bounding box for this blob"""
            ...

        def getArcLength(self) -> float:
            """Get the arc length of this blob"""
            ...

        def getCircularity(self) -> float:
            """Get the circularity of this blob"""
            ...

        def getCircle(self) -> Circle:
            """Get the center Point and radius of the circle enclosing this blob"""
            ...

    class Util:
        """Utility class for post-processing results from #getBlobs()"""
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessor.Util"
        @staticmethod
        def filterByCriteria(criteria: ColorBlobLocatorProcessor.BlobCriteria, minValue: float, maxValue: float, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Remove from a List of Blobs those which fail to meet a given criteria"""
            ...

        @staticmethod
        def sortByCriteria(criteria: ColorBlobLocatorProcessor.BlobCriteria, sortOrder: SortOrder, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            ...

        @staticmethod
        def filterByArea(minArea: float, maxArea: float, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Remove from a List of Blobs those which fail to meet an area criteria"""
            ...

        @staticmethod
        def sortByArea(sortOrder: SortOrder, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Sort a list of Blobs based on area"""
            ...

        @staticmethod
        def filterByDensity(minDensity: float, maxDensity: float, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Remove from a List of Blobs those which fail to meet a density criteria"""
            ...

        @staticmethod
        def sortByDensity(sortOrder: SortOrder, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Sort a list of Blobs based on density"""
            ...

        @staticmethod
        def filterByAspectRatio(minAspectRatio: float, maxAspectRatio: float, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Remove from a List of Blobs those which fail to meet an aspect ratio criteria"""
            ...

        @staticmethod
        def sortByAspectRatio(sortOrder: SortOrder, blobs: list[ColorBlobLocatorProcessor.Blob]) -> None:
            """Sort a list of Blobs based on aspect ratio"""
            ...

    def addFilter(self, filter: ColorBlobLocatorProcessor.BlobFilter) -> None:
        """Add a filter."""
        ...

    def removeFilter(self, filter: ColorBlobLocatorProcessor.BlobFilter) -> None:
        """Remove a filter."""
        ...

    def removeAllFilters(self) -> None:
        """Remove all filters."""
        ...

    def setSort(self, sort: ColorBlobLocatorProcessor.BlobSort) -> None:
        """Sets the sort."""
        ...

    def getBlobs(self) -> list[ColorBlobLocatorProcessor.Blob]:
        """Get the results of the most recent blob analysis"""
        ...


class ColorBlobLocatorProcessorImpl(ColorBlobLocatorProcessor):
    __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessorImpl"
    class BlobImpl(ColorBlobLocatorProcessor.Blob):
        __java__ = "org.firstinspires.ftc.vision.opencv.ColorBlobLocatorProcessorImpl.BlobImpl"
        def __init__(self, contour: Any) -> None:
            ...

        def getContour(self) -> Any:
            ...

        def getContourPoints(self) -> list[Any]:
            ...

        def getContourAsFloat(self) -> Any:
            ...

        def getContourArea(self) -> int:
            ...

        def getDensity(self) -> float:
            ...

        def getAspectRatio(self) -> float:
            ...

        def getBoxFit(self) -> Any:
            ...

        def getArcLength(self) -> float:
            ...

        def getCircularity(self) -> float:
            ...

        def getCircle(self) -> Circle:
            ...

    def __init__(self, colorRange: ColorRange, roiImg: ImageRegion, contourMode: ColorBlobLocatorProcessor.ContourMode, morphOperationType: ColorBlobLocatorProcessor.MorphOperationType, erodeSize: int, dilateSize: int, drawContours: bool, blurSize: int, boundingBoxColor: int, circleFitColor: int, roiColor: int, contourColor: int) -> None:
        ...

    def init(self, width: int, height: int, calibration: CameraCalibration) -> None:
        ...

    def processFrame(self, frame: Any, captureTimeNanos: int) -> object:
        ...

    def onDrawFrame(self, canvas: Any, onscreenWidth: int, onscreenHeight: int, scaleBmpPxToCanvasPx: float, scaleCanvasDensity: float, userContext: object) -> None:
        ...

    def addFilter(self, filter: ColorBlobLocatorProcessor.BlobFilter) -> None:
        ...

    def removeFilter(self, filter: ColorBlobLocatorProcessor.BlobFilter) -> None:
        ...

    def removeAllFilters(self) -> None:
        ...

    def setSort(self, sort: ColorBlobLocatorProcessor.BlobSort) -> None:
        ...

    def getBlobs(self) -> list[ColorBlobLocatorProcessor.Blob]:
        ...


class ColorRange:
    """An ColorRange"""
    __java__ = "org.firstinspires.ftc.vision.opencv.ColorRange"
    def __init__(self, colorSpace: ColorSpace, min: Any, max: Any) -> None:
        ...

    colorSpace: ColorSpace
    min: Any
    max: Any
    BLUE: ColorRange
    RED: ColorRange
    YELLOW: ColorRange
    GREEN: ColorRange
    ARTIFACT_GREEN: ColorRange
    ARTIFACT_PURPLE: ColorRange


class ColorSpace(enum.Enum):
    """A ColorSpace is a means to map a set of numerical values to colors"""
    __java__ = "org.firstinspires.ftc.vision.opencv.ColorSpace"
    YCrCb = enum.auto()
    HSV = enum.auto()
    RGB = enum.auto()


class ImageRegion:
    """An ImageRegion defines an area of an image buffer in terms of either a typical image processing coordinate system wherein the origin is in the top left corner and the domain of X and Y is dictated by the resolution of said image buffer; OR a \"unity center\" coordinate system wherein the origin is at the middle of the image and the domain of X and Y is {-1, 1} such that the region can be defined independent of the actual resolution of the image buffer."""
    __java__ = "org.firstinspires.ftc.vision.opencv.ImageRegion"
    @staticmethod
    def asImageCoordinates(left: int, top: int, right: int, bottom: int) -> ImageRegion:
        """Construct an ImageRegion using typical image processing coordinates -------------------------------------------- | (0,0)-------X | | | | | | | | Y | | | | (width,height) | --------------------------------------------"""
        ...

    @staticmethod
    def asUnityCenterCoordinates(left: float, top: float, right: float, bottom: float) -> ImageRegion:
        """Construct an ImageRegion using \"Unity Center\" coordinates -------------------------------------------- | (-1,1) Y (1,1) | | | | | | | | (0,0) ----- X | | | | (-1,-1) (1, -1) | --------------------------------------------"""
        ...

    @staticmethod
    def entireFrame() -> ImageRegion:
        """Construct an ImageRegion representing the entire frame"""
        ...

    def asOpenCvRect(self, imageWidth: int, imageHeight: int) -> Any:
        """Create an OpenCV Rect object which is representative of this ImageRegion for a specific image buffer size"""
        ...

    imageCoords: bool
    left: float
    top: float
    right: float
    bottom: float


class PredominantColorProcessor(VisionProcessor):
    """The PredominantColorProcessor acts like a \"Color Sensor\", allowing you to define a Region of Interest (ROI) of the camera stream inside of which the dominant color is found. Additionally, said color is matched to one of the Swatchs specified by the user as a \"best guess\" at the general shade of the color"""
    __java__ = "org.firstinspires.ftc.vision.opencv.PredominantColorProcessor"
    class Builder:
        """Class supporting construction of a PredominantColorProcessor"""
        __java__ = "org.firstinspires.ftc.vision.opencv.PredominantColorProcessor.Builder"
        def setRoi(self, roi: ImageRegion) -> PredominantColorProcessor.Builder:
            """Set the Region of Interest on which to perform color analysis"""
            ...

        def setSwatches(self, *swatches: PredominantColorProcessor.Swatch) -> PredominantColorProcessor.Builder:
            """Set the Swatches from which a \"best guess\" at the shade of the predominant color will be made"""
            ...

        def build(self) -> PredominantColorProcessor:
            """Construct a PredominantColorProcessor object using previously set parameters"""
            ...

        roi: ImageRegion
        swatches: list[PredominantColorProcessor.Swatch]

    class Result:
        """Class describing the result of color analysis on the ROI"""
        __java__ = "org.firstinspires.ftc.vision.opencv.PredominantColorProcessor.Result"
        @overload
        def __init__(self) -> None:
            ...
        @overload
        def __init__(self, closestSwatch: PredominantColorProcessor.Swatch, rgb: int) -> None:
            ...
        @overload
        def __init__(self, closestSwatch: PredominantColorProcessor.Swatch, rgb: int, RGB: list[int], HSV: list[int], YCrCb: list[int]) -> None:
            ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            ...

        closestSwatch: PredominantColorProcessor.Swatch
        """\"Best guess\" at the general shade of the dominant color in the ROI"""
        rgb: int
        """Exact numerical value of the dominant color in the ROI (24 bit)"""
        RGB: list[int]
        """Predominant color expressed as RGB int array. Red 0-255, Green 0-255, Blue 0-255"""
        HSV: list[int]
        """Predominant color expressed as HSV int array. Hue 0-180, Saturation 0-255, Value 0-255"""
        YCrCb: list[int]
        """Predominant color expressed as YCrCb int array. Luminance(Y) 0-255, Cr 0-255 (center 128), Cb 0-255 (center 128)"""

    class Swatch(enum.Enum):
        """Swatches from which you may choose from when invoking Builder#setSwatches(Swatch...)"""
        __java__ = "org.firstinspires.ftc.vision.opencv.PredominantColorProcessor.Swatch"
        RED = enum.auto()
        ORANGE = enum.auto()
        YELLOW = enum.auto()
        GREEN = enum.auto()
        ARTIFACT_GREEN = enum.auto()
        CYAN = enum.auto()
        BLUE = enum.auto()
        ARTIFACT_PURPLE = enum.auto()
        PURPLE = enum.auto()
        MAGENTA = enum.auto()
        BLACK = enum.auto()
        WHITE = enum.auto()
        @staticmethod
        def valueOf(swatch: int) -> PredominantColorProcessor.Swatch:
            ...

        hue: int

    def getAnalysis(self) -> PredominantColorProcessor.Result:
        """Get the result of the most recent color analysis"""
        ...


class PredominantColorProcessorImpl(PredominantColorProcessor):
    __java__ = "org.firstinspires.ftc.vision.opencv.PredominantColorProcessorImpl"
    def __init__(self, roi: ImageRegion, swatches: list[PredominantColorProcessor.Swatch]) -> None:
        ...

    def init(self, width: int, height: int, calibration: CameraCalibration) -> None:
        ...

    def processFrame(self, frame: Any, captureTimeNanos: int) -> object:
        ...

    def onDrawFrame(self, canvas: Any, onscreenWidth: int, onscreenHeight: int, scaleBmpPxToCanvasPx: float, scaleCanvasDensity: float, userContext: object) -> None:
        ...

    def getAnalysis(self) -> PredominantColorProcessor.Result:
        ...

    def yCrCb2Rgb(self, yCrCb: list[int]) -> list[int]:
        ...
