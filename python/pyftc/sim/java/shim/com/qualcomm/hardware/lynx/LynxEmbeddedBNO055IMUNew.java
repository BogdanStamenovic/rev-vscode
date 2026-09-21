/*
 * Simulator stand-in for the FTC SDK 11.2.0 LynxEmbeddedBNO055IMUNew (hubs made before
 * September 2022, BNO055). The real driver talks to the chip over I2C and hands the raw
 * quaternion to QuaternionBasedImuHelper; this one gets the raw quaternion from
 * the simulated hub's pose and uses the same helper, so every user-facing
 * value is computed by the SDK's own code.
 */
package com.qualcomm.hardware.lynx;

import com.qualcomm.robotcore.hardware.IMU;

import org.firstinspires.ftc.robotcore.external.navigation.AngleUnit;
import org.firstinspires.ftc.robotcore.external.navigation.AngularVelocity;
import org.firstinspires.ftc.robotcore.external.navigation.AxesOrder;
import org.firstinspires.ftc.robotcore.external.navigation.AxesReference;
import org.firstinspires.ftc.robotcore.external.navigation.Orientation;
import org.firstinspires.ftc.robotcore.external.navigation.Quaternion;
import org.firstinspires.ftc.robotcore.external.navigation.YawPitchRollAngles;
import org.pyftc.sim.hw.SimImu;

public class LynxEmbeddedBNO055IMUNew implements IMU {
    private static final String TAG = "LynxEmbeddedBNO055IMUNew";
    private final SimImu.Core core;

    public LynxEmbeddedBNO055IMUNew(SimImu.Core core) {
        this.core = core;
    }

    @Override public boolean initialize(Parameters parameters) {
        core.read();
        parameters = parameters.copy();
        core.helper.setImuOrientationOnRobot(parameters.imuOrientationOnRobot);
        core.initialized = true;
        return true;
    }

    @Override public void resetYaw() {
        core.read();
        core.helper.resetYaw(TAG, core::rawQuaternion, 50);
    }

    @Override public YawPitchRollAngles getRobotYawPitchRollAngles() {
        core.read();
        return core.helper.getRobotYawPitchRollAngles(TAG, core::rawQuaternion);
    }

    @Override public Orientation getRobotOrientation(AxesReference reference, AxesOrder order, AngleUnit angleUnit) {
        core.read();
        return core.helper.getRobotOrientation(TAG, core::rawQuaternion, reference, order, angleUnit);
    }

    @Override public Quaternion getRobotOrientationAsQuaternion() {
        core.read();
        return core.helper.getRobotOrientationAsQuaternion(TAG, core::rawQuaternion, true);
    }

    @Override public AngularVelocity getRobotAngularVelocity(AngleUnit angleUnit) {
        core.read();
        return core.helper.getRobotAngularVelocity(core.rawAngularVelocity(), angleUnit);
    }

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "BNO055 IMU (embedded)"; }
    @Override public String getConnectionInfo() { return core.hub.connectionInfo() + "; I2C port 0"; }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
