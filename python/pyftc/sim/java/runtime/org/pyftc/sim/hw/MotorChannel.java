package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.PIDFCoefficients;

import org.pyftc.sim.Constants;

import java.util.EnumMap;
import java.util.Map;

/**
 * One motor port of a simulated hub: the firmware-side state that Lynx commands
 * set (mode, power, target velocity/position, enable, zero power behaviour,
 * encoder) and the physics of the motor attached to it.
 *
 * Sign convention inside the channel: positive = the direction in which the
 * encoder counts up, which is the direction a positive hub voltage turns the
 * motor. Which way that is physically comes from the SDK's @MotorType
 * orientation ("direction of rotation in which encoder counts increase when
 * looking down the motor shaft towards the motor"): CW for the UltraPlanetary
 * HD Hex, CCW for the Core Hex.
 */
public final class MotorChannel {
    public final int port;
    public MotorSpec spec;
    public String deviceName;
    /** true when encoder counts increase with the shaft turning clockwise seen from the shaft face. */
    public boolean orientationCW = true;
    public double loadInertia;

    // firmware state
    public DcMotor.RunMode mode = DcMotor.RunMode.RUN_WITHOUT_ENCODER;
    public DcMotor.ZeroPowerBehavior zeroPower = DcMotor.ZeroPowerBehavior.FLOAT;
    public boolean enabled = false;
    public int constantPower = 0;        // -32767..32767
    public int targetVelocity = 0;       // ticks/s
    public int targetPosition = 0;
    public int tolerance = 5;
    public boolean targetSet = false;
    public long encoderOffset = 0;
    public final Map<DcMotor.RunMode, PIDFCoefficients> pidf = new EnumMap<DcMotor.RunMode, PIDFCoefficients>(DcMotor.RunMode.class);
    public double currentAlertMa = 5000;

    // physics state (output shaft, encoder-positive direction)
    public double omega;     // rad/s
    public double theta;     // rad, unwrapped
    public double current;   // A
    public double appliedFraction;  // -1..1 of battery voltage, what the H-bridge drives

    public MotorChannel(int port) {
        this.port = port;
    }

    public boolean attached() {
        return spec != null;
    }

    public int encoderPosition() {
        if (spec == null) return 0;
        return (int) (Math.round(theta / (2 * Math.PI) * spec.countsPerOutputRev()) - encoderOffset);
    }

    public double velocityTicksPerSec() {
        if (spec == null) return 0;
        return omega / (2 * Math.PI) * spec.countsPerOutputRev();
    }

    /** Output shaft angular velocity about the shaft axis, + = counter-clockwise seen from the shaft face. */
    public double physicalOmega() {
        return orientationCW ? -omega : omega;
    }

    public double physicalAngle() {
        return orientationCW ? -theta : theta;
    }

    /** Achievable max ticks/s as the SDK computes it (MotorConfigurationType), used by RUN_USING_ENCODER scaling. */
    public double sdkMaxTicksPerSecond = 2380;
    /** The real SDK motor object on this port (for reading its direction without calling it). */
    public com.qualcomm.robotcore.hardware.DcMotorImpl device;

    void step(double dt, double batteryVolts) {
        if (spec == null) return;
        double frac = 0;
        boolean driven = enabled;
        if (driven) {
            switch (mode) {
                case RUN_WITHOUT_ENCODER:
                    frac = constantPower / 32767.0;
                    break;
                case RUN_USING_ENCODER:
                    frac = velocityLoop(targetVelocity);
                    break;
                case RUN_TO_POSITION: {
                    double error = targetPosition - encoderPosition();
                    double cap = Math.abs(targetVelocity);
                    double want = Math.max(-cap, Math.min(cap, error * Constants.num("firmware.positionLoopGain")));
                    if (Math.abs(error) <= tolerance) want = 0;
                    frac = velocityLoop(want);
                    break;
                }
                case STOP_AND_RESET_ENCODER:
                default:
                    frac = 0;
                    driven = false;
                    break;
            }
        }
        frac = Math.max(-1, Math.min(1, frac));
        appliedFraction = driven ? frac : 0;

        double n = spec.ratio;
        double eff = spec.efficiency;
        double jTotal = spec.rotorInertia * n * n + loadInertia;
        double omegaMotor = omega * n;

        // Terminal behaviour: driven (PWM at frac of battery), or zero drive with the
        // brake mode deciding whether the terminals are shorted (BRAKE) or open (FLOAT).
        // A disabled channel (failsafe, never enabled) floats.
        boolean shorted = driven || (enabled && zeroPower == DcMotor.ZeroPowerBehavior.BRAKE);
        double v = appliedFraction * batteryVolts;
        double friction = spec.frictionTorque * n * eff;

        if (shorted) {
            // Semi-implicit in the back-EMF term so a light load cannot make the step unstable.
            double drive = n * eff * spec.kt * v / spec.resistance;
            double damping = n * n * eff * spec.kt * spec.ke / spec.resistance;
            double omegaNew = (omega + dt * drive / jTotal) / (1 + dt * damping / jTotal);
            omegaNew = applyFriction(omegaNew, friction, dt, jTotal);
            omega = omegaNew;
            current = (v - spec.ke * omega * n) / spec.resistance;
        } else {
            omega = applyFriction(omega, friction, dt, jTotal);
            current = 0;
        }
        theta += omega * dt;
        omegaMotor = omega * n;
        if (Math.abs(omegaMotor) < 1e-9) omega = 0;
    }

    private static double applyFriction(double w, double frictionTorque, double dt, double j) {
        if (frictionTorque <= 0) return w;
        double dw = frictionTorque / j * dt;
        if (Math.abs(w) <= dw) return 0;
        return w - Math.signum(w) * dw;
    }

    private double velocityLoop(double targetTps) {
        double freeTps = spec.freeSpeedMotorRadS / spec.ratio / (2 * Math.PI) * spec.countsPerOutputRev();
        double ff = targetTps / freeTps;
        double fb = Constants.num("firmware.velocityLoopKp") * (targetTps - velocityTicksPerSec());
        return ff + fb;
    }
}
