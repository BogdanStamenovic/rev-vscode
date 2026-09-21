package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.VoltageSensor;

import org.pyftc.sim.Constants;

/** The hub's battery voltage reading (hardwareMap.voltageSensor); one command per read. */
public final class SimVoltageSensor implements VoltageSensor {
    private final Hub hub;

    SimVoltageSensor(Hub hub) {
        this.hub = hub;
    }

    public double volts() {
        return Constants.num("battery.nominalVoltage");
    }

    @Override public double getVoltage() {
        try {
            hub.command();
            return Math.round(volts() * 1000.0) * 0.001;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "Lynx Voltage Sensor"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo(); }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
