package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.CRServoImpl;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorImpl;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.Servo;
import com.qualcomm.robotcore.hardware.ServoImpl;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType;

import org.firstinspires.ftc.robotcore.external.navigation.Rotation;

import java.lang.reflect.Field;

/**
 * Reads what the real SDK device objects would report, for the UI, WITHOUT
 * calling their methods: those are synchronized (the OpMode thread may be
 * parked inside one) and go through the Lynx caches (reading would change what
 * the next real call sends). Fields are read by reflection instead, and the
 * values are derived from the simulated hub state with the SDK's own formulas.
 */
final class DeviceState {
    private static final Field MOTOR_DIRECTION = field(DcMotorImpl.class, "direction");
    private static final Field SERVO_DIRECTION = field(ServoImpl.class, "direction");
    private static final Field SERVO_MIN = field(ServoImpl.class, "limitPositionMin");
    private static final Field SERVO_MAX = field(ServoImpl.class, "limitPositionMax");
    private static final Field CR_DIRECTION = field(CRServoImpl.class, "direction");

    private DeviceState() {}

    private static Field field(Class<?> c, String name) {
        try {
            Field f = c.getDeclaredField(name);
            f.setAccessible(true);
            return f;
        } catch (NoSuchFieldException e) {
            throw new IllegalStateException(e);
        }
    }

    private static Object get(Field f, Object o) {
        try {
            return f.get(o);
        } catch (IllegalAccessException e) {
            throw new IllegalStateException(e);
        }
    }

    static DcMotorSimple.Direction motorDirection(DcMotorImpl m) {
        return (DcMotorSimple.Direction) get(MOTOR_DIRECTION, m);
    }

    /** DcMotorImpl.getOperationalDirection(): the motor type's CCW orientation flips the user's direction. */
    static boolean operationallyReversed(DcMotorImpl m, MotorConfigurationType type) {
        DcMotorSimple.Direction d = motorDirection(m);
        DcMotorSimple.Direction op = type.getOrientation() == Rotation.CCW ? d.inverted() : d;
        return op == DcMotorSimple.Direction.REVERSE;
    }

    /** What motor.getPower() returns: hub-side power, converted back through the direction like DcMotorImpl.getPower(). */
    static double userPower(DcMotorImpl m, MotorChannel c) {
        double hubPower;
        switch (c.mode) {
            case RUN_TO_POSITION:
            case RUN_USING_ENCODER:
                hubPower = c.sdkMaxTicksPerSecond == 0 ? 0 : c.targetVelocity / c.sdkMaxTicksPerSecond;
                break;
            case STOP_AND_RESET_ENCODER:
                hubPower = 0;
                break;
            default:
                hubPower = c.constantPower / 32767.0;
        }
        if (c.mode == DcMotor.RunMode.RUN_TO_POSITION) return Math.abs(hubPower);
        return operationallyReversed(m, typeOf(m)) ? -hubPower : hubPower;
    }

    static int userPosition(DcMotorImpl m, MotorChannel c) {
        int p = c.encoderPosition();
        return operationallyReversed(m, typeOf(m)) ? -p : p;
    }

    private static final Field MOTOR_TYPE = field(DcMotorImpl.class, "motorType");

    private static MotorConfigurationType typeOf(DcMotorImpl m) {
        return (MotorConfigurationType) get(MOTOR_TYPE, m);
    }

    static double servoPosition(ServoChannel s, ServoImpl servo) {
        if (!s.pwmEnabled || s.pulseUs <= 0) return Double.NaN;
        double lower = servoLower(s);
        double upper = servoUpper(s);
        double controllerPos = (s.pulseUs - lower) / (upper - lower);
        double min = (Double) get(SERVO_MIN, servo);
        double max = (Double) get(SERVO_MAX, servo);
        double scaled = (controllerPos - min) / (max - min);
        if (get(SERVO_DIRECTION, servo) == Servo.Direction.REVERSE) scaled = 1.0 - scaled;
        return Math.max(0, Math.min(1, scaled));
    }

    static double servoLower(ServoChannel s) {
        return s.pulseRangeLower;
    }

    static double servoUpper(ServoChannel s) {
        return s.pulseRangeUpper;
    }

    static Servo.Direction servoDirection(ServoImpl s) {
        return (Servo.Direction) get(SERVO_DIRECTION, s);
    }

    static DcMotorSimple.Direction crDirection(CRServoImpl cr) {
        return (DcMotorSimple.Direction) get(CR_DIRECTION, cr);
    }

    /** CRServoImpl.setPower maps power -1..1 onto position 0..1 of the PWM range. */
    static double crPower(ServoChannel s, CRServoImpl cr) {
        if (!s.pwmEnabled || s.pulseUs <= 0) return 0;
        double pos = (s.pulseUs - s.pulseRangeLower) / (s.pulseRangeUpper - s.pulseRangeLower);
        double power = pos * 2 - 1;
        if (crDirection(cr) == DcMotorSimple.Direction.REVERSE) power = -power;
        return Math.max(-1, Math.min(1, power));
    }
}
