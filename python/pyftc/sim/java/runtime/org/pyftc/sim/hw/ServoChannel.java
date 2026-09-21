package org.pyftc.sim.hw;

import org.pyftc.sim.Constants;

/**
 * One servo port and the Smart Robot Servo attached to it. The hub only
 * produces a pulse width; what the servo does with it follows REV's SRS spec:
 * 500..2500 µs maps to 270° (centre 1500 µs) in angular mode, or to direction
 * and speed in continuous mode, moving at the published slew rate.
 */
public final class ServoChannel {
    public final int port;
    public String deviceName;
    public boolean continuous;
    public double rangeDeg = 270;

    public boolean pwmEnabled = false;
    public int pulseUs = 0;
    public double usFrame = 20000;
    /** The SDK-side PWM range of the port (PwmControl.PwmRange), for converting pulses back to positions. */
    public double pulseRangeLower = 600;
    public double pulseRangeUpper = 2400;

    /** Output angle in degrees from the centre position, + = counter-clockwise seen from the spline. */
    public double angleDeg = 0;
    /** Continuous mode: unwrapped output angle in radians and speed, + = CCW seen from the spline. */
    public double spinRad = 0;
    public double omega = 0;

    public ServoChannel(int port) {
        this.port = port;
    }

    private double sign() {
        return Constants.num("srs.pulseIncreasesCounterClockwise") >= 0.5 ? 1 : -1;
    }

    /** Angle the pulse commands, or NaN with no pulse. */
    public double targetAngleDeg() {
        if (!pwmEnabled || pulseUs <= 0) return Double.NaN;
        double lo = Constants.num("srs.pulseMinUs");
        double hi = Constants.num("srs.pulseMaxUs");
        double centre = (lo + hi) / 2;
        double us = Math.max(lo, Math.min(hi, pulseUs));
        return sign() * (us - centre) / (hi - lo) * rangeDeg;
    }

    void step(double dt) {
        if (continuous) {
            double target = 0;
            if (pwmEnabled && pulseUs > 0) {
                double lo = Constants.num("srs.pulseMinUs");
                double hi = Constants.num("srs.pulseMaxUs");
                double centre = (lo + hi) / 2;
                double us = Math.max(lo, Math.min(hi, pulseUs));
                double freeRadS = Constants.num("srs.continuousFreeSpeed") * 2 * Math.PI / 60.0;
                target = sign() * (us - centre) / ((hi - lo) / 2) * freeRadS;
            }
            omega = target;
            spinRad += omega * dt;
            return;
        }
        double target = targetAngleDeg();
        if (Double.isNaN(target)) {
            omega = 0;
            return;
        }
        double maxStep = 60.0 / Constants.num("srs.speedSecPer60Deg") * dt;
        double d = target - angleDeg;
        if (Math.abs(d) <= maxStep) {
            omega = d / dt * Math.PI / 180.0;
            angleDeg = target;
        } else {
            omega = Math.signum(d) * maxStep / dt * Math.PI / 180.0;
            angleDeg += Math.signum(d) * maxStep;
        }
    }
}
