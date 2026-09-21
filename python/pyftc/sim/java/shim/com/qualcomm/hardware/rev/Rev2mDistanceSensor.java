/*
 * Simulator stand-in for the FTC SDK 11.2.0 Rev2mDistanceSensor / VL53L0X driver
 * (the real one speaks the chip's I2C register protocol). getDistance() follows
 * VL53L0X.getDistance: millimetres from the chip, divided into the requested
 * unit; the chip reading comes from the scene (raycast or manual override) with
 * REV's published 5..200 cm range and 1 mm resolution. What the chip reports
 * with nothing in range is not documented; see constants.json distance2m.
 */
package com.qualcomm.hardware.rev;

import com.qualcomm.robotcore.hardware.DistanceSensor;
import com.qualcomm.robotcore.hardware.HardwareDevice;

import org.firstinspires.ftc.robotcore.external.navigation.DistanceUnit;
import org.pyftc.sim.Constants;
import org.pyftc.sim.hw.Hub;
import org.pyftc.sim.hw.SensorState;

public class Rev2mDistanceSensor implements DistanceSensor {
    private final Hub hub;
    private final SensorState state;
    private final int bus;
    private boolean didTimeout = false;

    public Rev2mDistanceSensor(Hub hub, SensorState state, int bus) {
        this.hub = hub;
        this.state = state;
        this.bus = bus;
    }

    public static int simulatedReadingMm(SensorState s) {
        double d = s.distanceMm;
        if (Double.isNaN(d) || d > Constants.num("distance2m.maxMm")) {
            return (int) Constants.num("distance2m.outOfRangeMm");
        }
        return (int) Math.round(Math.max(0, d));
    }

    protected int readRangeContinuousMillimeters() {
        try {
            hub.transact(hub.i2cNs);
        } catch (InterruptedException e) {
            // VL53L0X returns FAKE_DISTANCE_MM when the thread is interrupted.
            Thread.currentThread().interrupt();
            return 65535;
        }
        return simulatedReadingMm(state);
    }

    @Override public double getDistance(DistanceUnit unit) {
        double range = (double) this.readRangeContinuousMillimeters();
        if (unit == DistanceUnit.CM) {
            return range / 10;
        } else if (unit == DistanceUnit.METER) {
            return range / 1000;
        } else if (unit == DistanceUnit.INCH) {
            return range / 25.4;
        } else {
            return range;
        }
    }

    public boolean didTimeoutOccur() {
        return didTimeout;
    }

    public byte getModelID() {
        return (byte) 0xEE;
    }

    @Override public HardwareDevice.Manufacturer getManufacturer() { return HardwareDevice.Manufacturer.Other; }
    @Override public String getDeviceName() { return "REV 2M ToF Distance Sensor"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo() + "; I2C port " + bus; }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
