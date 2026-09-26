/*
 * Simulator stand-in for the FTC SDK 11.2.0 LynxModule: only what OpModes use
 * it for, bulk caching. The real class is the hub's whole Lynx protocol
 * endpoint; here each simulated hub gets one, registered in the hardwareMap
 * under the hub's name like the Robot Controller does. The caching semantics
 * (one bulk command per snapshot, MANUAL stale until clearBulkCache(), AUTO
 * refreshing on a repeated read) live in org.pyftc.sim.hw.Hub.
 */
package com.qualcomm.hardware.lynx;

import com.qualcomm.robotcore.hardware.HardwareDevice;

import org.pyftc.sim.hw.Hub;

public class LynxModule implements HardwareDevice {
    public enum BulkCachingMode { OFF, MANUAL, AUTO }

    private final Hub hub;
    private BulkCachingMode mode = BulkCachingMode.OFF;

    public LynxModule(Hub hub) {
        this.hub = hub;
    }

    public BulkCachingMode getBulkCachingMode() {
        return mode;
    }

    public void setBulkCachingMode(BulkCachingMode mode) {
        this.mode = mode;
        hub.bulkMode = mode == BulkCachingMode.OFF ? Hub.BULK_OFF : mode == BulkCachingMode.MANUAL ? Hub.BULK_MANUAL : Hub.BULK_AUTO;
        hub.clearBulkCache();
    }

    public void clearBulkCache() {
        hub.clearBulkCache();
    }

    public boolean isParent() {
        return hub.controlHub;
    }

    public int getModuleAddress() {
        return hub.address;
    }

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return hub.controlHub ? "Control Hub" : "Expansion Hub"; }
    @Override public String getConnectionInfo() { return "simulated, address " + hub.address; }
    @Override public int getVersion() { return 1; }
    // As the SDK does at every OpMode start.
    @Override public void resetDeviceConfigurationForOpMode() { setBulkCachingMode(BulkCachingMode.OFF); }
    @Override public void close() { }
}
