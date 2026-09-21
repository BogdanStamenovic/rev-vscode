package org.pyftc.sim.hw;

import com.google.gson.JsonObject;
import com.qualcomm.hardware.bosch.BHI260IMU;
import com.qualcomm.hardware.lynx.LynxEmbeddedBNO055IMUNew;
import com.qualcomm.hardware.rev.RevHubOrientationOnRobot;
import com.qualcomm.robotcore.hardware.HardwareDevice;
import com.qualcomm.robotcore.hardware.IMU;
import com.qualcomm.robotcore.hardware.QuaternionBasedImuHelper;

import org.firstinspires.ftc.robotcore.external.navigation.AngleUnit;
import org.firstinspires.ftc.robotcore.external.navigation.AngularVelocity;
import org.firstinspires.ftc.robotcore.external.navigation.Quaternion;
import org.firstinspires.ftc.robotcore.external.navigation.YawPitchRollAngles;
import org.pyftc.sim.SimClock;

import java.util.HashMap;
import java.util.Map;

/**
 * The IMU chip inside a simulated hub, feeding the SDK's real
 * QuaternionBasedImuHelper (the code BHI260IMU and BNO055IMUNew both use), so
 * mounting orientation, resetYaw and the yaw/pitch/roll conventions are the SDK's.
 *
 * The chip's orientation comes from the hub's pose in the scene. Per the SDK
 * (RevImuOrientationOnRobot): with the logo up and the USB ports forward, the
 * IMU's axes are the robot's axes rotated -90 degrees about Z; the chip's Z
 * always points up. The scene is three.js-framed (Y up, forward = -Z); the
 * robot frame is FTC's (X right, Y forward, Z up).
 */
public final class SimImu {
    public static final class Core {
        public final Hub hub;
        public final String name;
        public final QuaternionBasedImuHelper helper;
        public boolean initialized;

        Core(Hub hub, String name) {
            this.hub = hub;
            this.name = name;
            IMU.Parameters defaults = new IMU.Parameters(new RevHubOrientationOnRobot(
                    RevHubOrientationOnRobot.LogoFacingDirection.UP, RevHubOrientationOnRobot.UsbFacingDirection.FORWARD));
            this.helper = new QuaternionBasedImuHelper(defaults.imuOrientationOnRobot);
            // The SDK drivers reset the yaw when the hardware map is built.
            helper.resetYaw(name, this::rawQuaternion, 0);
        }

        public Quaternion rawQuaternion() {
            double[] q = chipQuaternion(hub);
            return new Quaternion((float) q[0], (float) q[1], (float) q[2], (float) q[3], System.nanoTime());
        }

        public AngularVelocity rawAngularVelocity() {
            double[] w = chipRates(hub);
            return new AngularVelocity(AngleUnit.RADIANS, (float) w[0], (float) w[1], (float) w[2], System.nanoTime());
        }

        public void read() {
            try {
                hub.transact(hub.i2cNs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private static final Map<Hub, double[]> hubRotationScene = new HashMap<Hub, double[]>();
    private static final Map<Hub, double[]> prevChip = new HashMap<Hub, double[]>();
    private static final Map<Hub, double[]> chipRates = new HashMap<Hub, double[]>();
    private static final Map<HardwareDevice, Core> cores = new HashMap<HardwareDevice, Core>();

    private SimImu() {}

    static HardwareDevice create(String tag, Hub hub, String name) {
        Core core = new Core(hub, name);
        HardwareDevice d = "LynxEmbeddedIMU".equals(tag) ? new LynxEmbeddedBNO055IMUNew(core) : new BHI260IMU(core);
        cores.put(d, core);
        return d;
    }

    static void setHubRotation(Hub hub, double rxDeg, double ryDeg, double rzDeg) {
        synchronized (hubRotationScene) {
            hubRotationScene.put(hub, new double[]{rxDeg, ryDeg, rzDeg});
        }
    }

    /** w,x,y,z of the chip frame in the robot frame. */
    static double[] chipQuaternion(Hub hub) {
        double[] e;
        synchronized (hubRotationScene) {
            e = hubRotationScene.get(hub);
        }
        double[] qScene = e == null ? new double[]{1, 0, 0, 0} : eulerXYZ(e[0], e[1], e[2]);
        // Change of basis scene -> FTC robot frame: x' = x, y' = -z, z' = y. For a quaternion
        // that is the same rotation with its vector part mapped the same way.
        double[] qHub = {qScene[0], qScene[1], -qScene[3], qScene[2]};
        double[] zMinus90 = {Math.cos(Math.toRadians(-45)), 0, 0, Math.sin(Math.toRadians(-45))};
        return normalize(mul(qHub, zMinus90));
    }

    static double[] chipRates(Hub hub) {
        synchronized (chipRates) {
            double[] w = chipRates.get(hub);
            return w == null ? new double[]{0, 0, 0} : w;
        }
    }

    static void step(double dt) {
        synchronized (hubRotationScene) {
            for (Hub hub : hubRotationScene.keySet().toArray(new Hub[0])) {
                double[] q = chipQuaternion(hub);
                double[] p = prevChip.get(hub);
                double[] w = {0, 0, 0};
                if (p != null) {
                    // body rates from q_prev^-1 * q_now
                    double[] d = mul(conj(p), q);
                    if (d[0] < 0) d = new double[]{-d[0], -d[1], -d[2], -d[3]};
                    double angle = 2 * Math.acos(Math.min(1, d[0]));
                    double s = Math.sqrt(Math.max(0, 1 - d[0] * d[0]));
                    if (s > 1e-9) w = new double[]{d[1] / s * angle / dt, d[2] / s * angle / dt, d[3] / s * angle / dt};
                }
                prevChip.put(hub, q);
                synchronized (chipRates) {
                    chipRates.put(hub, w);
                }
            }
        }
    }

    static void describe(HardwareDevice d, JsonObject o) {
        Core core = cores.get(d);
        if (core == null) return;
        Quaternion raw = core.rawQuaternion();
        YawPitchRollAngles ypr = core.helper.getRobotYawPitchRollAngles(core.name, core::rawQuaternion);
        o.addProperty("yawDeg", ypr.getYaw(AngleUnit.DEGREES));
        o.addProperty("pitchDeg", ypr.getPitch(AngleUnit.DEGREES));
        o.addProperty("rollDeg", ypr.getRoll(AngleUnit.DEGREES));
        o.addProperty("initialized", core.initialized);
        if (raw != null) o.addProperty("chipW", raw.w);
    }

    private static double[] eulerXYZ(double rx, double ry, double rz) {
        // three.js Euler order 'XYZ': q = qx * qy * qz
        double[] qx = {Math.cos(Math.toRadians(rx) / 2), Math.sin(Math.toRadians(rx) / 2), 0, 0};
        double[] qy = {Math.cos(Math.toRadians(ry) / 2), 0, Math.sin(Math.toRadians(ry) / 2), 0};
        double[] qz = {Math.cos(Math.toRadians(rz) / 2), 0, 0, Math.sin(Math.toRadians(rz) / 2)};
        return mul(mul(qx, qy), qz);
    }

    static double[] mul(double[] a, double[] b) {
        return new double[]{
            a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
            a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
            a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
            a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0],
        };
    }

    private static double[] conj(double[] q) {
        return new double[]{q[0], -q[1], -q[2], -q[3]};
    }

    private static double[] normalize(double[] q) {
        double n = Math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
        return new double[]{q[0] / n, q[1] / n, q[2] / n, q[3] / n};
    }
}
