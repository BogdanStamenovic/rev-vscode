package org.pyftc.sim.hw;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.qualcomm.hardware.rev.Rev2mDistanceSensor;
import com.qualcomm.hardware.rev.RevColorSensorV3;
import com.qualcomm.hardware.rev.RevTouchSensor;
import com.qualcomm.robotcore.hardware.AnalogInput;
import com.qualcomm.robotcore.hardware.CRServo;
import com.qualcomm.robotcore.hardware.CRServoImplEx;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorImplEx;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.DigitalChannelImpl;
import com.qualcomm.robotcore.hardware.HardwareDevice;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.hardware.Servo;
import com.qualcomm.robotcore.hardware.ServoImplEx;
import com.qualcomm.robotcore.hardware.configuration.ConfigurationTypeManager;
import com.qualcomm.robotcore.hardware.configuration.annotations.DeviceProperties;
import com.qualcomm.robotcore.hardware.configuration.annotations.MotorType;
import com.qualcomm.robotcore.hardware.configuration.annotations.ServoType;
import com.qualcomm.robotcore.hardware.configuration.ExpansionHubMotorControllerPositionParams;
import com.qualcomm.robotcore.hardware.configuration.ExpansionHubMotorControllerVelocityParams;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.ServoConfigurationType;

import org.pyftc.sim.Constants;
import org.pyftc.sim.SimLog;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The simulated robot: hubs, the devices from the hardware configuration, and
 * the real SDK HardwareMap they are registered in exactly as the Robot
 * Controller's HardwareFactory registers them (typed DeviceMappings, which also
 * feed hardwareMap.get(Class, name)). Motors, servos, CR servos, digital
 * channels and analog inputs are the REAL SDK device classes (DcMotorImplEx,
 * ServoImplEx, CRServoImplEx, DigitalChannelImpl, AnalogInput, RevTouchSensor)
 * on top of the simulated Lynx controllers.
 */
public final class Robot {
    private static Robot instance;

    public static Robot get() {
        return instance;
    }

    public final Map<String, Hub> hubs = new LinkedHashMap<String, Hub>();
    public final List<DeviceInfo> devices = new ArrayList<DeviceInfo>();
    private final HardwareMap hardwareMap = new HardwareMap(null, null);
    public final List<String> notSimulated = new ArrayList<String>();

    public static final class DeviceInfo {
        public String name;
        public String tag;
        public String kind;
        public String displayName;
        public String javaType;
        public Hub hub;
        public int port;
        public int bus = -1;
        public HardwareDevice device;
        public MotorChannel motor;
        public ServoChannel servo;
        public SensorState sensor;
        public MotorConfigurationType motorType;
    }

    public HardwareMap hardwareMap() {
        return hardwareMap;
    }

    public static Robot build(JsonObject config, JsonObject layout) {
        registerDefaultTypes();
        Robot r = new Robot();
        instance = r;
        JsonObject layoutDevices = layout != null && layout.has("devices") ? layout.getAsJsonObject("devices") : new JsonObject();
        for (JsonElement he : config.getAsJsonArray("hubs")) {
            JsonObject h = he.getAsJsonObject();
            String name = h.get("name").getAsString();
            int address = h.has("address") && !h.get("address").isJsonNull() ? h.get("address").getAsInt() : 0;
            boolean ch = h.has("kind") ? "ControlHub".equals(h.get("kind").getAsString()) : address == 173;
            Hub hub = new Hub(name, address, ch);
            r.hubs.put(name, hub);
            r.hardwareMap.dcMotorController.put(name, hub.motorController);
            r.hardwareMap.servoController.put(name, hub.servoController);
            r.hardwareMap.voltageSensor.put(name, hub.voltageSensor);
        }
        for (JsonElement de : config.getAsJsonArray("devices")) {
            JsonObject d = de.getAsJsonObject();
            try {
                r.addDevice(d, layoutDevices.has(str(d, "name")) ? layoutDevices.getAsJsonObject(str(d, "name")) : null);
            } catch (RuntimeException e) {
                SimLog.error("sim", "could not simulate device '" + str(d, "name") + "' (" + str(d, "tag") + "): " + e, e);
            }
        }
        r.applyLayout(layout);
        return r;
    }

    private static String str(JsonObject o, String key) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsString() : null;
    }

    private static int num(JsonObject o, String key, int dflt) {
        if (!o.has(key) || o.get(key).isJsonNull()) return dflt;
        try {
            return Integer.parseInt(o.get(key).getAsString());
        } catch (NumberFormatException e) {
            return dflt;
        }
    }

    private void addDevice(JsonObject d, JsonObject layoutDevice) {
        DeviceInfo info = new DeviceInfo();
        info.name = str(d, "name");
        info.tag = str(d, "tag");
        info.displayName = str(d, "displayName");
        info.javaType = str(d, "javaType");
        String category = str(d, "category");
        String hubName = str(d, "hub");
        info.hub = hubName == null ? null : hubs.get(hubName);
        info.port = num(d, "port", -1);
        info.bus = num(d, "bus", -1);
        JsonObject props = d.has("props") && d.get("props").isJsonObject() ? d.getAsJsonObject("props") : new JsonObject();
        if (info.hub == null && !"imu".equals(category)) {
            info.kind = "unsupported";
            notSimulated.add(info.name + " (" + info.tag + "): not attached to a hub");
            devices.add(info);
            return;
        }
        Hub hub = info.hub;
        if ("motor".equals(category)) {
            info.kind = "motor";
            MotorChannel ch = hub.motors[info.port];
            MotorConfigurationType type = motorType(info.tag);
            info.motorType = type;
            JsonObject layoutMotor = layoutDevice != null && layoutDevice.has("motor") ? layoutDevice.getAsJsonObject("motor") : null;
            ch.spec = MotorSpec.forTag(info.tag, props, layoutMotor);
            ch.deviceName = info.name;
            ch.orientationCW = type.getOrientation() == org.firstinspires.ftc.robotcore.external.navigation.Rotation.CW;
            ch.loadInertia = loadInertia(layoutMotor);
            DcMotorImplEx motor = new DcMotorImplEx(hub.motorController, info.port, DcMotorSimple.Direction.FORWARD, type);
            info.device = motor;
            info.motor = ch;
            ch.device = motor;
            hardwareMap.dcMotor.put(info.name, motor);
        } else if ("servo".equals(category) || "crservo".equals(category)) {
            boolean cr = "crservo".equals(category);
            if (!"Servo".equals(info.tag) && !"ServoFullRange".equals(info.tag) && !"ContinuousRotationServo".equals(info.tag)) {
                info.kind = "unsupported";
                notSimulated.add(info.name + " (" + info.tag + "): only standard servos, full-range servos and CR servos are simulated");
                devices.add(info);
                return;
            }
            info.kind = cr ? "crservo" : "servo";
            ServoChannel ch = hub.servos[info.port];
            ch.deviceName = info.name;
            ch.continuous = cr;
            ServoConfigurationType type = servoType(cr ? CRServo.class : Servo.class, info.tag);
            if (cr) {
                CRServoImplEx s = new CRServoImplEx(hub.servoController, info.port, DcMotorSimple.Direction.FORWARD, type);
                info.device = s;
                hardwareMap.crservo.put(info.name, s);
            } else {
                ServoImplEx s = new ServoImplEx(hub.servoController, info.port, Servo.Direction.FORWARD, type);
                info.device = s;
                hardwareMap.servo.put(info.name, s);
            }
            info.servo = ch;
        } else if ("RevTouchSensor".equals(info.tag)) {
            info.kind = "touch";
            RevTouchSensor t = new RevTouchSensor(hub.digitalController, info.port);
            info.device = t;
            info.sensor = new SensorState();
            hardwareMap.touchSensor.put(info.name, t);
        } else if ("DigitalDevice".equals(info.tag)) {
            info.kind = "digital";
            DigitalChannelImpl c = new DigitalChannelImpl(hub.digitalController, info.port);
            info.device = c;
            info.sensor = new SensorState();
            hardwareMap.digitalChannel.put(info.name, c);
        } else if ("AnalogInput".equals(info.tag)) {
            boolean pot = layoutDevice != null && layoutDevice.has("sensor") && layoutDevice.getAsJsonObject("sensor").has("potentiometer")
                    && layoutDevice.getAsJsonObject("sensor").get("potentiometer").getAsBoolean();
            info.kind = pot ? "potentiometer" : "analog";
            AnalogInput a = new AnalogInput(hub.analogController, info.port);
            info.device = a;
            info.sensor = new SensorState();
            hardwareMap.analogInput.put(info.name, a);
        } else if ("REV_VL53L0X_RANGE_SENSOR".equals(info.tag)) {
            info.kind = "distance";
            info.sensor = new SensorState();
            Rev2mDistanceSensor s = new Rev2mDistanceSensor(hub, info.sensor, info.bus);
            info.device = s;
            hardwareMap.put(info.name, s);
        } else if ("RevColorSensorV3".equals(info.tag)) {
            info.kind = "color";
            info.sensor = new SensorState();
            RevColorSensorV3 s = new RevColorSensorV3(hub, info.sensor, info.bus);
            info.device = s;
            hardwareMap.colorSensor.put(info.name, s);
        } else if ("ControlHubImuBHI260AP".equals(info.tag) || "LynxEmbeddedIMU".equals(info.tag)) {
            info.kind = "imu";
            HardwareDevice imu = SimImu.create(info.tag, hub, info.name);
            info.device = imu;
            hardwareMap.put(info.name, imu);
        } else {
            info.kind = "unsupported";
            notSimulated.add(info.name + " (" + info.tag + "): this device type is not simulated");
        }
        devices.add(info);
    }

    private static double loadInertia(JsonObject layoutMotor) {
        String load = layoutMotor != null && layoutMotor.has("load") ? layoutMotor.get("load").getAsString() : "free";
        if ("arm".equals(load)) return Constants.num("loads.armInertia");
        if ("wheel".equals(load)) {
            double r = 0.045;
            return Constants.num("loads.robotMass") / 4.0 * r * r;
        }
        return Constants.num("loads.freeShaftInertia");
    }

    // ------------------------------------------------------------------ SDK configuration types

    private static final String[] MOTOR_TYPE_CLASSES = {
        "com.qualcomm.hardware.motors.GoBILDA5201Series", "com.qualcomm.hardware.motors.GoBILDA5202Series",
        "com.qualcomm.hardware.motors.Matrix12vMotor", "com.qualcomm.hardware.motors.NeveRest3_7GearmotorV1",
        "com.qualcomm.hardware.motors.NeveRest20Gearmotor", "com.qualcomm.hardware.motors.NeveRest40Gearmotor",
        "com.qualcomm.hardware.motors.NeveRest60Gearmotor", "com.qualcomm.hardware.motors.RevRobotics20HdHexMotor",
        "com.qualcomm.hardware.motors.RevRobotics40HdHexMotor", "com.qualcomm.hardware.motors.RevRoboticsCoreHexMotor",
        "com.qualcomm.hardware.motors.RevRoboticsHdHexMotor", "com.qualcomm.hardware.motors.RevRoboticsUltraPlanetaryHdHexMotor",
        "com.qualcomm.hardware.motors.StudicaMaverickMotor", "com.qualcomm.hardware.motors.TetrixMotor",
        "com.qualcomm.robotcore.hardware.configuration.UnspecifiedMotor",
    };

    /**
     * The MotorConfigurationType the Robot Controller would build for this XML tag,
     * from the same @MotorType / @DeviceProperties / PIDF annotations its
     * ConfigurationTypeManager reads (it cannot be used directly: it needs Android).
     */
    static MotorConfigurationType motorType(String tag) {
        Class<?> found = null;
        for (String cn : MOTOR_TYPE_CLASSES) {
            try {
                Class<?> c = Class.forName(cn);
                DeviceProperties p = c.getAnnotation(DeviceProperties.class);
                if (p != null && p.xmlTag().equals(tag)) {
                    found = c;
                    break;
                }
            } catch (ClassNotFoundException ignored) {
            }
        }
        if (found == null) {
            try {
                found = Class.forName("com.qualcomm.robotcore.hardware.configuration.UnspecifiedMotor");
            } catch (ClassNotFoundException e) {
                throw new IllegalStateException(e);
            }
        }
        DeviceProperties props = found.getAnnotation(DeviceProperties.class);
        MotorConfigurationType t = new MotorConfigurationType(found, props.xmlTag(), ConfigurationTypeManager.ClassSource.APK);
        MotorType m = found.getAnnotation(MotorType.class);
        t.setTicksPerRev(m.ticksPerRev());
        t.setGearing(m.gearing());
        t.setMaxRPM(m.maxRPM());
        t.setAchieveableMaxRPMFraction(m.achieveableMaxRPMFraction());
        t.setOrientation(m.orientation());
        t.processAnnotation(found.getAnnotation(ExpansionHubMotorControllerVelocityParams.class));
        t.processAnnotation(found.getAnnotation(ExpansionHubMotorControllerPositionParams.class));
        ConfigurationTypeManager.getInstance().register(t);
        return t;
    }

    /** Types the SDK looks up by tag (MotorConfigurationType.getUnspecifiedMotorType(), ...). */
    static void registerDefaultTypes() {
        motorType("Motor");
        servoType(Servo.class, "Servo");
        servoType(Servo.class, "ServoFullRange");
        servoType(CRServo.class, "ContinuousRotationServo");
    }

    static ServoConfigurationType servoType(Class<? extends HardwareDevice> clazz, String tag) {
        ServoConfigurationType t = new ServoConfigurationType(clazz, tag, ConfigurationTypeManager.ClassSource.APK);
        for (ServoType st : clazz.getAnnotationsByType(ServoType.class)) {
            if (st.xmlTag().equals(tag) || ("ContinuousRotationServo".equals(tag) && clazz == CRServo.class)) {
                t.processAnnotation(st);
                ConfigurationTypeManager.getInstance().register(t);
                return t;
            }
        }
        throw new IllegalArgumentException("no @ServoType for tag " + tag + " on " + clazz.getName());
    }

    // ------------------------------------------------------------------ layout

    public void applyLayout(JsonObject layout) {
        if (layout == null) return;
        JsonObject ld = layout.has("devices") ? layout.getAsJsonObject("devices") : new JsonObject();
        for (DeviceInfo info : devices) {
            JsonObject d = ld.has(info.name) ? ld.getAsJsonObject(info.name) : null;
            if (info.servo != null && d != null && d.has("servo") && d.getAsJsonObject("servo").has("rangeDeg")) {
                info.servo.rangeDeg = d.getAsJsonObject("servo").get("rangeDeg").getAsDouble();
            }
            if (info.motor != null && d != null && d.has("motor")) {
                JsonObject lm = d.getAsJsonObject("motor");
                JsonObject props = new JsonObject();
                if (info.motorType != null) {
                    props.addProperty("gearing", info.motorType.getGearing());
                    props.addProperty("maxRPM", info.motorType.getMaxRPM());
                    props.addProperty("ticksPerRev", info.motorType.getTicksPerRev());
                }
                // Changing the cartridge stack keeps the shaft angle and speed at the output.
                info.motor.spec = MotorSpec.forTag(info.tag, props, lm);
                info.motor.loadInertia = loadInertia(lm);
            }
            if (info.sensor != null && d != null && d.has("sensor") && d.getAsJsonObject("sensor").has("override")) {
                JsonElement ov = d.getAsJsonObject("sensor").get("override");
                if (ov != null && ov.isJsonObject()) {
                    info.sensor.apply(ov.getAsJsonObject());
                    applySensor(info);
                }
            }
        }
        JsonObject hubsLayout = layout.has("hubs") ? layout.getAsJsonObject("hubs") : new JsonObject();
        for (Hub hub : hubs.values()) {
            if (hubsLayout.has(hub.name)) {
                JsonObject h = hubsLayout.getAsJsonObject(hub.name);
                if (h.has("rotation")) {
                    JsonArray rot = h.getAsJsonArray("rotation");
                    SimImu.setHubRotation(hub, rot.get(0).getAsDouble(), rot.get(1).getAsDouble(), rot.get(2).getAsDouble());
                }
            }
        }
    }

    public DeviceInfo find(String name) {
        for (DeviceInfo d : devices) if (d.name.equals(name)) return d;
        return null;
    }

    public void setSensor(String name, JsonObject value) {
        DeviceInfo info = find(name);
        if (info == null || info.sensor == null) {
            SimLog.warn("sim", "sensor input for unknown device '" + name + "'", null);
            return;
        }
        info.sensor.apply(value);
        applySensor(info);
    }

    private void applySensor(DeviceInfo info) {
        SensorState s = info.sensor;
        if ("touch".equals(info.kind)) {
            // REV touch sensor is active-low: pressed pulls the channel to 0 V (reads false).
            info.hub.digitalInput[info.port] = !s.pressed;
        } else if ("digital".equals(info.kind)) {
            info.hub.digitalInput[info.port] = s.digitalState;
        } else if ("analog".equals(info.kind) || "potentiometer".equals(info.kind)) {
            info.hub.analogVolts[info.port] = s.volts;
        }
    }

    // ------------------------------------------------------------------ OpMode lifecycle hooks

    /** What the RC does to the hardware when an OpMode is initialised. */
    public void prepareForOpMode() {
        for (Hub hub : hubs.values()) {
            hub.motorController.forgetLastKnown();
            hub.servoController.forgetLastKnown();
            hub.digitalController.forgetLastKnown();
        }
        for (DeviceInfo info : devices) {
            if (info.device != null) {
                try {
                    info.device.resetDeviceConfigurationForOpMode();
                } catch (RuntimeException e) {
                    SimLog.warn("sim", "resetDeviceConfigurationForOpMode failed for " + info.name + ": " + e, e);
                }
            }
        }
    }

    /** DefaultOpMode.startSafe(): every DcMotorSimple (motors and CR servos) with power != 0 gets setPower(0). */
    public void stopRobot() {
        for (DeviceInfo info : devices) {
            if (info.device instanceof DcMotorSimple) {
                DcMotorSimple m = (DcMotorSimple) info.device;
                try {
                    if (m.getPower() != 0) m.setPower(0);
                } catch (RuntimeException e) {
                    SimLog.warn("sim", "stopping " + info.name + " failed: " + e, e);
                }
            }
        }
    }

    /** Hub failsafe, 100 ms after the OpMode ends: every motor channel disabled, every servo PWM off. */
    public void failsafe() {
        for (Hub hub : hubs.values()) {
            hub.motorController.failsafe();
            hub.servoController.failsafe();
        }
    }

    public void step(double dt) {
        double volts = Constants.num("battery.nominalVoltage");
        for (Hub hub : hubs.values()) hub.step(dt, volts);
        SimImu.step(dt);
    }

    // ------------------------------------------------------------------ protocol

    public JsonArray describeDevices() {
        JsonArray arr = new JsonArray();
        for (DeviceInfo info : devices) {
            JsonObject o = new JsonObject();
            o.addProperty("name", info.name);
            o.addProperty("kind", info.kind);
            o.addProperty("tag", info.tag);
            if (info.displayName != null) o.addProperty("displayName", info.displayName);
            if (info.javaType != null) o.addProperty("javaType", info.javaType);
            if (info.hub != null) o.addProperty("hub", info.hub.name);
            if (info.port >= 0) o.addProperty("port", info.port);
            if (info.bus >= 0) o.addProperty("bus", info.bus);
            if (info.motor != null) {
                MotorSpec s = info.motor.spec;
                JsonObject m = new JsonObject();
                m.addProperty("orientation", info.motor.orientationCW ? "CW" : "CCW");
                m.addProperty("sdkTicksPerRev", info.motorType.getTicksPerRev());
                m.addProperty("sdkMaxRPM", info.motorType.getMaxRPM());
                m.addProperty("ticksPerRev", s.countsPerOutputRev());
                m.addProperty("gearRatio", s.ratio);
                m.addProperty("freeSpeedRpm", s.freeSpeedOutputRpm());
                JsonArray carts = new JsonArray();
                for (String c : s.cartridges) carts.add(c);
                m.add("cartridges", carts);
                m.addProperty("specVerified", s.verified);
                m.addProperty("note", s.note);
                o.add("motor", m);
            }
            if (info.servo != null) {
                JsonObject sv = new JsonObject();
                sv.addProperty("rangeDeg", info.servo.rangeDeg);
                sv.addProperty("continuous", info.servo.continuous);
                o.add("servo", sv);
            }
            arr.add(o);
        }
        return arr;
    }

    public JsonArray describeHubs() {
        JsonArray arr = new JsonArray();
        for (Hub hub : hubs.values()) {
            JsonObject o = new JsonObject();
            o.addProperty("name", hub.name);
            o.addProperty("address", hub.address);
            o.addProperty("kind", hub.controlHub ? "ControlHub" : "ExpansionHub");
            arr.add(o);
        }
        return arr;
    }

    public JsonObject stateJson() {
        JsonObject out = new JsonObject();
        for (DeviceInfo info : devices) {
            JsonObject o = new JsonObject();
            o.addProperty("kind", info.kind);
            if (info.motor != null) {
                MotorChannel c = info.motor;
                DcMotorImplEx m = (DcMotorImplEx) info.device;
                o.addProperty("power", DeviceState.userPower(m, c));
                o.addProperty("direction", DeviceState.motorDirection(m).toString());
                o.addProperty("orientation", c.orientationCW ? "CW" : "CCW");
                o.addProperty("reversed", DeviceState.operationallyReversed(m, info.motorType));
                o.addProperty("applied", c.appliedFraction);
                double w = c.physicalOmega();
                o.addProperty("spin", Math.abs(w) < 0.05 ? "stopped" : (w > 0 ? "CCW" : "CW"));
                o.addProperty("omegaRadS", w);
                o.addProperty("rpm", Math.abs(c.omega) * 60.0 / (2 * Math.PI));
                o.addProperty("angleRad", c.physicalAngle());
                o.addProperty("mode", c.mode.toString());
                o.addProperty("zeroPower", c.zeroPower.toString());
                o.addProperty("enabled", c.enabled);
                o.addProperty("position", DeviceState.userPosition(m, c));
                o.addProperty("target", c.targetPosition);
                o.addProperty("busy", c.mode == DcMotor.RunMode.RUN_TO_POSITION && Math.abs(c.targetPosition - c.encoderPosition()) > c.tolerance);
                o.addProperty("velocity", c.velocityTicksPerSec());
                o.addProperty("currentA", Math.abs(c.current));
            } else if (info.servo != null) {
                ServoChannel s = info.servo;
                o.addProperty("pwmUs", s.pulseUs);
                o.addProperty("enabled", s.pwmEnabled);
                if (s.continuous) {
                    CRServoImplEx cr = (CRServoImplEx) info.device;
                    DcMotorSimple.Direction dir = DeviceState.crDirection(cr);
                    o.addProperty("direction", dir.toString());
                    o.addProperty("reversed", dir == DcMotorSimple.Direction.REVERSE);
                    o.addProperty("power", DeviceState.crPower(s, cr));
                    o.addProperty("spin", Math.abs(s.omega) < 0.05 ? "stopped" : (s.omega > 0 ? "CCW" : "CW"));
                    o.addProperty("omegaRadS", s.omega);
                    o.addProperty("angleRad", s.spinRad);
                    o.addProperty("rpm", Math.abs(s.omega) * 60.0 / (2 * Math.PI));
                } else {
                    ServoImplEx sv = (ServoImplEx) info.device;
                    Servo.Direction dir = DeviceState.servoDirection(sv);
                    o.addProperty("direction", dir.toString());
                    o.addProperty("reversed", dir == Servo.Direction.REVERSE);
                    double pos = DeviceState.servoPosition(s, sv);
                    if (!Double.isNaN(pos)) o.addProperty("position", pos);
                    o.addProperty("angleDeg", s.angleDeg);
                    double target = s.targetAngleDeg();
                    if (!Double.isNaN(target)) o.addProperty("targetAngleDeg", target);
                    o.addProperty("rangeDeg", s.rangeDeg);
                }
            } else if (info.sensor != null) {
                info.sensor.describe(info.kind, info.hub, info.port, o);
            } else if ("imu".equals(info.kind)) {
                SimImu.describe(info.device, o);
            }
            out.add(info.name, o);
        }
        for (Hub hub : hubs.values()) {
            JsonObject v = new JsonObject();
            v.addProperty("kind", "voltage");
            v.addProperty("volts", hub.voltageSensor.volts());
            if (!out.has(hub.name)) out.add(hub.name, v);
        }
        return out;
    }
}
