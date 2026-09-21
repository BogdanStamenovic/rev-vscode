package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.PwmControl;
import com.qualcomm.robotcore.hardware.ServoController;
import com.qualcomm.robotcore.hardware.ServoControllerEx;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.ServoConfigurationType;
import com.qualcomm.robotcore.util.LastKnown;
import com.qualcomm.robotcore.util.Range;

import org.pyftc.sim.OpModeHost;

/**
 * Port of the FTC SDK 11.2.0 LynxServoController (Hardware-11.2.0-sources.jar).
 * Same caching, position -> pulse width scaling over the port's PWM range,
 * validation and auto-enable after a pulse is set. Sending a command charges
 * its time and sets the simulated port's pulse (Hub / ServoChannel).
 */
public final class SimServoController implements ServoController, ServoControllerEx {
    public static final int apiServoFirst = 0;
    public static final int apiServoLast = 5;
    public static final double apiPositionFirst = 0.0;
    public static final double apiPositionLast = 1.0;
    private static final int apiPulseWidthFirst = 1;
    private static final int apiPulseWidthLast = 65535;

    private final Hub hub;
    private final LastKnown<Double>[] lastKnownCommandedPosition;
    private final LastKnown<Boolean>[] lastKnownEnabled;
    private final LastKnown<Integer>[] lastKnownPulseWidthMicroseconds;
    private final PwmControl.PwmRange[] pwmRanges;
    private final PwmControl.PwmRange[] defaultPwmRanges;

    SimServoController(Hub hub) {
        this.hub = hub;
        lastKnownCommandedPosition = LastKnown.createArray(6);
        lastKnownEnabled = LastKnown.createArray(6);
        lastKnownPulseWidthMicroseconds = LastKnown.createArray(6);
        pwmRanges = new PwmControl.PwmRange[6];
        defaultPwmRanges = new PwmControl.PwmRange[6];
        for (int i = 0; i < 6; i++) {
            pwmRanges[i] = PwmControl.PwmRange.defaultRange;
            defaultPwmRanges[i] = PwmControl.PwmRange.defaultRange;
        }
    }

    public void forgetLastKnown() {
        LastKnown.invalidateArray(lastKnownCommandedPosition);
        LastKnown.invalidateArray(lastKnownEnabled);
        LastKnown.invalidateArray(lastKnownPulseWidthMicroseconds);
    }

    @Override public synchronized void forgetLastKnownPosition(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        lastKnownCommandedPosition[servo].invalidate();
    }

    private void event(int servoZ, String op, Object value) {
        String name = hub.servos[servoZ].deviceName;
        OpModeHost.recordCommand(name != null ? name : hub.name + " servo " + servoZ, op, value);
    }

    @Override public synchronized void pwmEnable() {
        for (int servoZ = 0; servoZ < 6; servoZ++) internalSetPwmEnable(servoZ, true);
    }

    @Override public synchronized void pwmDisable() {
        for (int servoZ = 0; servoZ < 6; servoZ++) internalSetPwmEnable(servoZ, false);
    }

    @Override public synchronized PwmStatus getPwmStatus() {
        Boolean enabled = null;
        for (int servoZ = 0; servoZ < 6; servoZ++) {
            boolean localEnabled = internalGetPwmEnable(servoZ);
            if (enabled == null) enabled = localEnabled;
            else if (enabled != localEnabled) return PwmStatus.MIXED;
        }
        return enabled ? PwmStatus.ENABLED : PwmStatus.DISABLED;
    }

    @Override public synchronized void setServoPwmEnable(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        internalSetPwmEnable(servo, true);
    }

    @Override public synchronized void setServoPwmDisable(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        internalSetPwmEnable(servo, false);
    }

    @Override public synchronized boolean isServoPwmEnabled(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        return internalGetPwmEnable(servo);
    }

    @Override public void setServoType(int servo, ServoConfigurationType servoType) {
        validateServo(servo); servo -= apiServoFirst;
        PwmControl.PwmRange newDefaultPwmRange = new PwmControl.PwmRange(servoType.getUsPulseLower(), servoType.getUsPulseUpper(), servoType.getUsFrame());
        defaultPwmRanges[servo] = newDefaultPwmRange;
        setServoPwmRange(servo, newDefaultPwmRange);
    }

    private void internalSetPwmEnable(int servoZ, boolean enable) {
        if (lastKnownEnabled[servoZ].updateValue(enable)) {
            if (!enable) {
                lastKnownCommandedPosition[servoZ].invalidate();
                lastKnownPulseWidthMicroseconds[servoZ].invalidate();
            }
            try {
                hub.command();
                hub.servos[servoZ].pwmEnabled = enable;
                event(servoZ, enable ? "pwmEnable" : "pwmDisable", enable);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private boolean internalGetPwmEnable(int servoZ) {
        Boolean result = lastKnownEnabled[servoZ].getValue();
        if (result != null) return result;
        try {
            hub.command();
            result = hub.servos[servoZ].pwmEnabled;
            lastKnownEnabled[servoZ].setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }

    @Override public synchronized void setServoPosition(int servo, double position) {
        validateServo(servo); servo -= apiServoFirst;
        validateApiServoPosition(position);
        OpModeHost.noteWrite(hub.servos[servo].deviceName, "setPosition", position);
        if (lastKnownCommandedPosition[servo].updateValue(position)) {
            double pwm = Range.scale(position, apiPositionFirst, apiPositionLast, pwmRanges[servo].usPulseLower, pwmRanges[servo].usPulseUpper);
            pwm = Range.clip(pwm, apiPulseWidthFirst, apiPulseWidthLast);
            internalSetPulseWidth(servo, (int) pwm);
        }
    }

    @Override public synchronized double getServoPosition(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        Double result = lastKnownCommandedPosition[servo].getValue();
        if (result != null) return result;
        int pwm = internalGetPulseWidth(servo);
        if (pwm != 0) {
            result = Range.scale(pwm, pwmRanges[servo].usPulseLower, pwmRanges[servo].usPulseUpper, apiPositionFirst, apiPositionLast);
            result = Range.clip(result, apiPositionFirst, apiPositionLast);
            lastKnownCommandedPosition[servo].setValue(result);
            return result;
        }
        return 0;
    }

    @Override public synchronized void setServoPwmRange(int servo, PwmControl.PwmRange range) {
        validateServo(servo); servo -= apiServoFirst;
        if (!range.equals(pwmRanges[servo])) {
            pwmRanges[servo] = range;
            hub.servos[servo].pulseRangeLower = range.usPulseLower;
            hub.servos[servo].pulseRangeUpper = range.usPulseUpper;
            try {
                hub.command();
                hub.servos[servo].usFrame = range.usFrame;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    @Override public synchronized PwmControl.PwmRange getServoPwmRange(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        return pwmRanges[servo];
    }

    @Override public synchronized void setPulseWidth(int servo, double usWidth) {
        validateServo(servo); servo -= apiServoFirst;
        lastKnownCommandedPosition[servo].invalidate();
        internalSetPulseWidth(servo, (int) usWidth);
    }

    @Override public synchronized double getPulseWidth(int servo) {
        validateServo(servo); servo -= apiServoFirst;
        return internalGetPulseWidth(servo);
    }

    private void internalSetPulseWidth(int servo, int usWidth) {
        lastKnownPulseWidthMicroseconds[servo].updateValue(usWidth);
        try {
            hub.command();
            hub.servos[servo].pulseUs = usWidth;
            event(servo, "pulseWidth", usWidth);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        internalSetPwmEnable(servo, true);
    }

    private int internalGetPulseWidth(int servo) {
        Integer result = lastKnownPulseWidthMicroseconds[servo].getValue();
        if (result != null) return result;
        try {
            hub.command();
            result = hub.servos[servo].pulseUs;
            lastKnownPulseWidthMicroseconds[servo].setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    private void validateServo(int servo) {
        if (servo < apiServoFirst || servo > apiServoLast) {
            throw new IllegalArgumentException(String.format("Servo %d is invalid; valid servos are %d..%d", servo, apiServoFirst, apiServoLast));
        }
    }

    private void validateApiServoPosition(double position) {
        if (!(apiPositionFirst <= position && position <= apiPositionLast)) {
            throw new IllegalArgumentException(String.format("illegal servo position %f; must be in interval [%f,%f]", position, apiPositionFirst, apiPositionLast));
        }
    }

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "Expansion Hub Servo Controller"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo(); }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }

    public void failsafe() {
        for (int i = 0; i < 6; i++) {
            hub.servos[i].pwmEnabled = false;
            lastKnownEnabled[i].invalidate();
            lastKnownCommandedPosition[i].invalidate();
            lastKnownPulseWidthMicroseconds[i].invalidate();
        }
    }
}
