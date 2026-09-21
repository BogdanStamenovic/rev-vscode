package org.pyftc.sim.hw;

import com.qualcomm.robotcore.exception.TargetPositionNotSetException;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorController;
import com.qualcomm.robotcore.hardware.DcMotorControllerEx;
import com.qualcomm.robotcore.hardware.PIDCoefficients;
import com.qualcomm.robotcore.hardware.PIDFCoefficients;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType;
import com.qualcomm.robotcore.util.LastKnown;
import com.qualcomm.robotcore.util.Range;

import org.firstinspires.ftc.robotcore.external.navigation.AngleUnit;
import org.firstinspires.ftc.robotcore.external.navigation.CurrentUnit;
import org.firstinspires.ftc.robotcore.external.navigation.UnnormalizedAngleUnit;
import org.pyftc.sim.OpModeHost;

/**
 * Port of the FTC SDK 11.2.0 LynxDcMotorController (Hardware-11.2.0-sources.jar),
 * the class the real DcMotorImpl talks to on a REV hub. The SDK-side logic is
 * kept line for line: power clipping to [-1, 1], the 500 ms LastKnown caches
 * that decide whether a command is sent at all, RUN_WITHOUT_ENCODER power
 * quantised to -32767..32767, RUN_USING_ENCODER/RUN_TO_POSITION power turned
 * into a target velocity from the motor type's achievable max ticks/s, mode
 * changes re-sending power, STOP_AND_RESET_ENCODER ignoring power, and the
 * TargetPositionNotSetException the hub's NACK produces. Where the real class
 * sends a Lynx command, this one charges the command's time and applies it to
 * the simulated hub (Hub / MotorChannel).
 */
public final class SimDcMotorController implements DcMotorController, DcMotorControllerEx {
    public static final int apiMotorFirst = 0;
    public static final int apiMotorLast = 3;
    public static final double apiPowerFirst = -1.0;
    public static final double apiPowerLast = 1.0;
    private static final int constantPowerLast = 32767;
    private static final int velocityFirst = -32767;
    private static final int velocityLast = 32767;

    private final Hub hub;

    private final class MotorProperties {
        LastKnown<Double> lastKnownPower = new LastKnown<Double>();
        LastKnown<Integer> lastKnownTargetPosition = new LastKnown<Integer>();
        LastKnown<DcMotor.RunMode> lastKnownMode = new LastKnown<DcMotor.RunMode>();
        LastKnown<DcMotor.ZeroPowerBehavior> lastKnownZeroPowerBehavior = new LastKnown<DcMotor.ZeroPowerBehavior>();
        LastKnown<Boolean> lastKnownEnable = new LastKnown<Boolean>();
        LastKnown<Double> lastKnownCurrentAlert = new LastKnown<Double>();
        MotorConfigurationType motorType = null;
        MotorConfigurationType internalMotorType = null;
    }

    private final MotorProperties[] motors = new MotorProperties[4];

    SimDcMotorController(Hub hub) {
        this.hub = hub;
        for (int i = 0; i < motors.length; i++) motors[i] = new MotorProperties();
    }

    public void forgetLastKnown() {
        for (MotorProperties motor : motors) {
            motor.lastKnownMode.invalidate();
            motor.lastKnownPower.invalidate();
            motor.lastKnownTargetPosition.invalidate();
            motor.lastKnownZeroPowerBehavior.invalidate();
            motor.lastKnownEnable.invalidate();
        }
    }

    private void validateMotor(int motor) {
        if (motor < apiMotorFirst || motor > apiMotorLast) {
            throw new IllegalArgumentException(String.format("motor %d is invalid; valid motors are %d..%d", motor, apiMotorFirst, apiMotorLast));
        }
    }

    private void validatePIDMode(int motor, DcMotor.RunMode runMode) {
        if (!runMode.isPIDMode()) {
            throw new IllegalArgumentException(String.format("motor %d: mode %s is invalid as PID Mode", motor, runMode));
        }
    }

    private MotorChannel ch(int motorZ) {
        return hub.motors[motorZ];
    }

    private void event(int motorZ, String op, Object value) {
        OpModeHost.recordCommand(ch(motorZ).deviceName != null ? ch(motorZ).deviceName : hub.name + " motor " + motorZ, op, value);
    }

    /**
     * Event for a power command in the terms the code used: the controller only sees the
     * hub-side power, after DcMotorImpl applied the direction (REVERSE, or a CCW motor
     * type), so the call's own value is recovered from the device's current direction.
     */
    private void userPowerEvent(int motorZ, double hubPower) {
        MotorChannel c = ch(motorZ);
        double user = hubPower;
        if (c.device != null && c.mode != DcMotor.RunMode.RUN_TO_POSITION && DeviceState.operationallyReversed(c.device, c.device.getMotorType())) {
            user = -hubPower;
        }
        OpModeHost.recordCommand(c.deviceName != null ? c.deviceName : hub.name + " motor " + motorZ, "setPower", user, hubPower);
    }

    // --------------------------------------------------------------- enable

    @Override public synchronized void setMotorEnable(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        internalSetMotorEnable(motor, true);
    }

    @Override public synchronized void setMotorDisable(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        internalSetMotorEnable(motor, false);
    }

    void internalSetMotorEnable(int motorZ, boolean enable) {
        if (motors[motorZ].lastKnownEnable.updateValue(enable)) {
            try {
                hub.command();
                MotorChannel c = ch(motorZ);
                if (enable && c.mode == DcMotor.RunMode.RUN_TO_POSITION && !c.targetSet) {
                    // The hub NACKs with MOTOR_NOT_CONFIG_BEFORE_ENABLED; the SDK turns that into this exception.
                    motors[motorZ].lastKnownEnable.invalidate();
                    throw new TargetPositionNotSetException();
                }
                c.enabled = enable;
                event(motorZ, enable ? "enable" : "disable", enable);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    @Override public synchronized boolean isMotorEnabled(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        Boolean result = motors[motor].lastKnownEnable.getValue();
        if (result != null) return result;
        try {
            hub.command();
            result = ch(motor).enabled;
            motors[motor].lastKnownEnable.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }

    // --------------------------------------------------------------- type / config

    @Override public synchronized void resetDeviceConfigurationForOpMode(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        ch(motor).pidf.clear();
        if (motors[motor].internalMotorType != null) {
            setMotorType(motor + apiMotorFirst, motors[motor].internalMotorType);
        }
    }

    @Override public synchronized MotorConfigurationType getMotorType(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return motors[motor].motorType;
    }

    @Override public synchronized void setMotorType(int motor, MotorConfigurationType motorType) {
        validateMotor(motor); motor -= apiMotorFirst;
        motors[motor].motorType = motorType;
        if (motors[motor].internalMotorType == null) {
            motors[motor].internalMotorType = motorType;
        }
        ch(motor).sdkMaxTicksPerSecond = motorType.getAchieveableMaxTicksPerSecondRounded();
    }

    private int getDefaultMaxMotorSpeed(int motorZ) {
        MotorConfigurationType t = motors[motorZ].motorType;
        return t == null ? 0 : t.getAchieveableMaxTicksPerSecondRounded();
    }

    // --------------------------------------------------------------- mode

    @Override public synchronized void setMotorMode(int motor, DcMotor.RunMode mode) {
        validateMotor(motor); motor -= apiMotorFirst;
        if (!motors[motor].lastKnownMode.isValue(mode)) {
            Double prevPower = motors[motor].lastKnownPower.getNonTimedValue();
            if (prevPower == null) {
                prevPower = internalGetMotorPower(motor);
            }
            DcMotor.ZeroPowerBehavior zeroPowerBehavior = DcMotor.ZeroPowerBehavior.UNKNOWN;
            boolean reset = mode == DcMotor.RunMode.STOP_AND_RESET_ENCODER;
            if (reset) {
                internalSetMotorPower(motor, 0);
            } else {
                zeroPowerBehavior = internalGetZeroPowerBehavior(motor);
            }
            try {
                hub.command();
                MotorChannel c = ch(motor);
                if (reset) {
                    c.encoderOffset += c.encoderPosition();
                    c.targetSet = false;
                    c.mode = DcMotor.RunMode.STOP_AND_RESET_ENCODER;
                } else {
                    c.mode = mode;
                    c.zeroPower = zeroPowerBehavior;
                }
                event(motor, "setMode", mode.toString());
                motors[motor].lastKnownMode.setValue(mode);
                internalSetMotorPower(motor, prevPower, true);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    @Override public synchronized DcMotor.RunMode getMotorMode(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return internalGetPublicMotorMode(motor);
    }

    private DcMotor.RunMode internalGetPublicMotorMode(int motorZ) {
        DcMotor.RunMode result = motors[motorZ].lastKnownMode.getValue();
        if (result != null) return result;
        if (motors[motorZ].lastKnownMode.getNonTimedValue() == DcMotor.RunMode.STOP_AND_RESET_ENCODER) {
            return DcMotor.RunMode.STOP_AND_RESET_ENCODER;
        }
        try {
            hub.command();
            result = hardwareMode(motorZ);
            motors[motorZ].lastKnownMode.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return DcMotor.RunMode.RUN_WITHOUT_ENCODER;
    }

    private DcMotor.RunMode internalGetMotorChannelMode(int motorZ) {
        DcMotor.RunMode result = motors[motorZ].lastKnownMode.getValue();
        if (result != null && result != DcMotor.RunMode.STOP_AND_RESET_ENCODER) return result;
        try {
            hub.command();
            return hardwareMode(motorZ);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return DcMotor.RunMode.RUN_WITHOUT_ENCODER;
    }

    /** The hub reports the channel mode; after a reset the channel keeps its previous run mode. */
    private DcMotor.RunMode hardwareMode(int motorZ) {
        DcMotor.RunMode m = ch(motorZ).mode;
        return m == DcMotor.RunMode.STOP_AND_RESET_ENCODER ? DcMotor.RunMode.RUN_WITHOUT_ENCODER : m;
    }

    // --------------------------------------------------------------- power

    @Override public synchronized void setMotorPower(int motor, double apiMotorPower) {
        validateMotor(motor); motor -= apiMotorFirst;
        OpModeHost.noteWrite(ch(motor).deviceName, "setPower", Range.clip(apiMotorPower, apiPowerFirst, apiPowerLast));
        internalSetMotorPower(motor, apiMotorPower);
    }

    @Override public synchronized double getMotorPower(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return internalGetMotorPower(motor);
    }

    private DcMotor.ZeroPowerBehavior internalGetZeroPowerBehavior(int motorZ) {
        DcMotor.ZeroPowerBehavior result = motors[motorZ].lastKnownZeroPowerBehavior.getValue();
        if (result != null) return result;
        try {
            hub.command();
            result = ch(motorZ).zeroPower;
            motors[motorZ].lastKnownZeroPowerBehavior.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return DcMotor.ZeroPowerBehavior.BRAKE;
    }

    private void internalSetZeroPowerBehavior(int motorZ, DcMotor.ZeroPowerBehavior behavior) {
        if (motors[motorZ].lastKnownZeroPowerBehavior.updateValue(behavior)) {
            DcMotor.RunMode runMode = internalGetMotorChannelMode(motorZ);
            try {
                hub.command();
                MotorChannel c = ch(motorZ);
                if (c.mode != DcMotor.RunMode.STOP_AND_RESET_ENCODER) c.mode = runMode;
                c.zeroPower = behavior;
                event(motorZ, "setZeroPowerBehavior", behavior.toString());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void internalSetMotorPower(int motorZ, double apiPower) {
        internalSetMotorPower(motorZ, apiPower, false);
    }

    private void internalSetMotorPower(int motorZ, double apiPower, boolean forceUpdate) {
        double power = Range.clip(apiPower, apiPowerFirst, apiPowerLast);
        if (motors[motorZ].lastKnownPower.updateValue(power) || forceUpdate) {
            DcMotor.RunMode mode = internalGetPublicMotorMode(motorZ);
            boolean send = true;
            int iPower = 0;
            boolean velocity = false;
            switch (mode) {
                case RUN_TO_POSITION:
                case RUN_USING_ENCODER: {
                    double p = Math.signum(power) * Range.scale(Math.abs(power), 0, apiPowerLast, 0, getDefaultMaxMotorSpeed(motorZ));
                    iPower = (int) p;
                    velocity = true;
                    break;
                }
                case RUN_WITHOUT_ENCODER: {
                    double p = Range.scale(power, apiPowerFirst, apiPowerLast, -constantPowerLast, constantPowerLast);
                    iPower = (int) p;
                    break;
                }
                case STOP_AND_RESET_ENCODER:
                default:
                    send = false;
                    break;
            }
            try {
                if (send) {
                    hub.command();
                    MotorChannel c = ch(motorZ);
                    if (velocity) c.targetVelocity = iPower; else c.constantPower = iPower;
                    userPowerEvent(motorZ, power);
                    internalSetMotorEnable(motorZ, true);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private double internalGetMotorPower(int motorZ) {
        Double result = motors[motorZ].lastKnownPower.getValue();
        if (result != null) return result;
        DcMotor.RunMode mode = internalGetPublicMotorMode(motorZ);
        try {
            hub.command();
            MotorChannel c = ch(motorZ);
            switch (mode) {
                case RUN_TO_POSITION:
                case RUN_USING_ENCODER: {
                    int iVelocity = c.targetVelocity;
                    result = Math.signum(iVelocity) * Range.scale(Math.abs(iVelocity), 0, getDefaultMaxMotorSpeed(motorZ), 0, apiPowerLast);
                    break;
                }
                case RUN_WITHOUT_ENCODER:
                default: {
                    result = Range.scale(c.constantPower, -constantPowerLast, constantPowerLast, apiPowerFirst, apiPowerLast);
                }
            }
            result = Range.clip(result, apiPowerFirst, apiPowerLast);
            motors[motorZ].lastKnownPower.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    @Override public synchronized boolean isBusy(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        if (internalGetMotorChannelMode(motor) != DcMotor.RunMode.RUN_TO_POSITION) {
            return false;
        }
        try {
            hub.command();
            MotorChannel c = ch(motor);
            return Math.abs(c.targetPosition - c.encoderPosition()) > c.tolerance;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return false;
    }

    @Override public synchronized void setMotorZeroPowerBehavior(int motor, DcMotor.ZeroPowerBehavior zeroPowerBehavior) {
        validateMotor(motor); motor -= apiMotorFirst;
        if (zeroPowerBehavior == DcMotor.ZeroPowerBehavior.UNKNOWN) throw new IllegalArgumentException("zeroPowerBehavior may not be UNKNOWN");
        internalSetZeroPowerBehavior(motor, zeroPowerBehavior);
    }

    @Override public synchronized DcMotor.ZeroPowerBehavior getMotorZeroPowerBehavior(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return internalGetZeroPowerBehavior(motor);
    }

    public synchronized void setMotorPowerFloat(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        internalSetZeroPowerBehavior(motor, DcMotor.ZeroPowerBehavior.FLOAT);
        internalSetMotorPower(motor, 0);
    }

    @Override public synchronized boolean getMotorPowerFloat(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return internalGetZeroPowerBehavior(motor) == DcMotor.ZeroPowerBehavior.FLOAT && internalGetMotorPower(motor) == 0;
    }

    // --------------------------------------------------------------- position

    @Override public synchronized void setMotorTargetPosition(int motor, int position) {
        setMotorTargetPosition(motor, position, 5);
    }

    @Override public synchronized void setMotorTargetPosition(int motor, int position, int tolerance) {
        validateMotor(motor); motor -= apiMotorFirst;
        try {
            hub.command();
            MotorChannel c = ch(motor);
            c.targetPosition = position;
            c.tolerance = tolerance;
            c.targetSet = true;
            event(motor, "setTargetPosition", position);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Override public synchronized int getMotorTargetPosition(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        try {
            hub.command();
            return ch(motor).targetPosition;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    @Override public synchronized int getMotorCurrentPosition(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        try {
            hub.command();
            return ch(motor).encoderPosition();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    // --------------------------------------------------------------- velocity

    @Override public synchronized void setMotorVelocity(int motor, double ticksPerSecond) {
        switch (getMotorMode(motor)) {
            case RUN_USING_ENCODER:
            case RUN_TO_POSITION:
                break;
            default:
                setMotorMode(motor, DcMotor.RunMode.RUN_USING_ENCODER);
        }
        validateMotor(motor); motor -= apiMotorFirst;
        int iTicksPerSecond = Range.clip((int) Math.round(ticksPerSecond), velocityFirst, velocityLast);
        try {
            hub.command();
            ch(motor).targetVelocity = iTicksPerSecond;
            event(motor, "setVelocity", iTicksPerSecond);
            internalSetMotorEnable(motor, true);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Override public synchronized void setMotorVelocity(int motor, double angularRate, AngleUnit unit) {
        validateMotor(motor); motor -= apiMotorFirst;
        double degreesPerSecond = UnnormalizedAngleUnit.DEGREES.fromUnit(unit.getUnnormalized(), angularRate);
        double revolutionsPerSecond = degreesPerSecond / 360.0;
        double ticksPerSecond = motors[motor].motorType.getTicksPerRev() * revolutionsPerSecond;
        setMotorVelocity(motor + apiMotorFirst, ticksPerSecond);
    }

    @Override public synchronized double getMotorVelocity(int motor) {
        validateMotor(motor); motor -= apiMotorFirst;
        return internalGetMotorTicksPerSecond(motor);
    }

    @Override public synchronized double getMotorVelocity(int motor, AngleUnit unit) {
        validateMotor(motor); motor -= apiMotorFirst;
        int ticksPerSecond = internalGetMotorTicksPerSecond(motor);
        double revsPerSecond = ticksPerSecond / motors[motor].motorType.getTicksPerRev();
        return unit.getUnnormalized().fromDegrees(revsPerSecond * 360.0);
    }

    private int internalGetMotorTicksPerSecond(int motorZ) {
        try {
            hub.command();
            return (int) Math.round(ch(motorZ).velocityTicksPerSec());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    // --------------------------------------------------------------- PID

    @Override public void setPIDCoefficients(int motor, DcMotor.RunMode mode, PIDCoefficients pidCoefficients) {
        setPIDFCoefficients(motor, mode, new PIDFCoefficients(pidCoefficients));
    }

    @Override public synchronized void setPIDFCoefficients(int motor, DcMotor.RunMode mode, PIDFCoefficients pidfCoefficients) {
        validatePIDMode(motor, mode);
        validateMotor(motor); motor -= apiMotorFirst;
        mode = mode.migrate();
        try {
            hub.command();
            ch(motor).pidf.put(mode, new PIDFCoefficients(pidfCoefficients));
            OpModeHost.notSimulated("DcMotorEx.setPIDFCoefficients", "the coefficients are stored and read back, but the simulated hub's control loop does not use them (the real firmware loop is closed source)");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Override public synchronized PIDCoefficients getPIDCoefficients(int motor, DcMotor.RunMode mode) {
        PIDFCoefficients f = getPIDFCoefficients(motor, mode);
        return new PIDCoefficients(f.p, f.i, f.d);
    }

    @Override public synchronized PIDFCoefficients getPIDFCoefficients(int motor, DcMotor.RunMode mode) {
        validateMotor(motor); motor -= apiMotorFirst;
        try {
            hub.command();
            PIDFCoefficients stored = ch(motor).pidf.get(mode.migrate());
            if (stored != null) return new PIDFCoefficients(stored);
            MotorConfigurationType t = motors[motor].motorType;
            if (t != null) {
                if (mode.migrate() == DcMotor.RunMode.RUN_TO_POSITION && t.hasExpansionHubPositionParams()) {
                    return new PIDFCoefficients(t.getHubPositionParams().getPidfCoefficients());
                }
                if (mode.migrate() == DcMotor.RunMode.RUN_USING_ENCODER && t.hasExpansionHubVelocityParams()) {
                    return new PIDFCoefficients(t.getHubVelocityParams().getPidfCoefficients());
                }
            }
            OpModeHost.notSimulated("DcMotorEx.getPIDFCoefficients", "the hub firmware's default coefficients are not known to the simulator; returning zeros");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return new PIDFCoefficients();
    }

    // --------------------------------------------------------------- current

    @Override public double getMotorCurrent(int motor, CurrentUnit unit) {
        validateMotor(motor);
        try {
            hub.command();
            return unit.convert(Math.abs(ch(motor).current) * 1000.0, CurrentUnit.MILLIAMPS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0.0;
    }

    @Override public double getMotorCurrentAlert(int motor, CurrentUnit unit) {
        Double cachedCurrent = motors[motor].lastKnownCurrentAlert.getValue();
        if (cachedCurrent != null) return unit.convert(cachedCurrent, CurrentUnit.MILLIAMPS);
        try {
            hub.command();
            double limit = ch(motor).currentAlertMa;
            motors[motor].lastKnownCurrentAlert.setValue(limit);
            return unit.convert(limit, CurrentUnit.MILLIAMPS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0.0;
    }

    @Override public void setMotorCurrentAlert(int motor, double current, CurrentUnit unit) {
        try {
            hub.command();
            ch(motor).currentAlertMa = Math.round(unit.toMilliAmps(current));
            motors[motor].lastKnownCurrentAlert.setValue((double) ch(motor).currentAlertMa);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Override public boolean isMotorOverCurrent(int motor) {
        try {
            hub.command();
            return Math.abs(ch(motor).current) * 1000.0 > ch(motor).currentAlertMa;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return false;
    }

    // --------------------------------------------------------------- HardwareDevice

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "Expansion Hub Motor Controller"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo(); }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }

    // --------------------------------------------------------------- simulator side

    /** DefaultOpMode after STOP: setPower(0) on everything, then the hub failsafe disables all channels. */
    public void failsafe() {
        for (int i = 0; i < motors.length; i++) {
            ch(i).enabled = false;
            motors[i].lastKnownEnable.invalidate();
            motors[i].lastKnownPower.invalidate();
        }
    }
}
