package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.AnalogInputController;
import com.qualcomm.robotcore.util.SerialNumber;

/**
 * Port of the FTC SDK 11.2.0 LynxAnalogInputController: one ADC command per read,
 * value in whole millivolts (the hub's ENGINEERING mode), max voltage 3.3 as the
 * SDK reports it.
 */
public final class SimAnalogController implements AnalogInputController {
    private final Hub hub;

    SimAnalogController(Hub hub) {
        this.hub = hub;
    }

    @Override public double getAnalogInputVoltage(int port) {
        if (port < 0 || port > 3) {
            throw new IllegalArgumentException(String.format("port %d is invalid; valid ports are %d..%d", port, 0, 3));
        }
        try {
            hub.command();
            return Math.round(hub.analogVolts[port] * 1000.0) * 0.001;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return 0;
    }

    @Override public double getMaxAnalogInputVoltage() { return 3.3; }
    @Override public SerialNumber getSerialNumber() { return SerialNumber.createFake(); }
    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "Expansion Hub Analog Input Controller"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo(); }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
