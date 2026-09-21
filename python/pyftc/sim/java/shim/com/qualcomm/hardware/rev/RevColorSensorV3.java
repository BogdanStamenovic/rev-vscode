/*
 * Simulator stand-in for the FTC SDK 11.2.0 RevColorSensorV3 / BroadcomColorSensorImpl
 * (the real driver reads the APDS-9151 over I2C). The user-facing arithmetic is the
 * real driver's, kept line for line: red scaled by 1.07 and blue by 1.55, alpha as
 * their mean, normalised colours = count * gain / 65535, the inverse-square alpha
 * of getNormalizedColors, and getDistance() = inFromOptical(proximity) with the
 * driver's calibration (a=325.961, b^-1=-0.75934, c=26.980, 6 inch maximum). The
 * raw chip counts come from the scene's target colour and distance through a
 * placeholder brightness model (constants.json colorV3), so absolute raw counts
 * are approximate; proximity is the exact inverse of the driver's calibration.
 */
package com.qualcomm.hardware.rev;

import com.qualcomm.robotcore.hardware.ColorRangeSensor;
import com.qualcomm.robotcore.hardware.DistanceSensor;
import com.qualcomm.robotcore.hardware.HardwareDevice;
import com.qualcomm.robotcore.hardware.I2cAddr;
import com.qualcomm.robotcore.hardware.NormalizedRGBA;
import com.qualcomm.robotcore.hardware.OpticalDistanceSensor;
import com.qualcomm.robotcore.hardware.SwitchableLight;
import com.qualcomm.robotcore.util.Range;

import org.firstinspires.ftc.robotcore.external.navigation.DistanceUnit;
import org.pyftc.sim.Constants;
import org.pyftc.sim.hw.Hub;
import org.pyftc.sim.hw.SensorState;

import java.util.Locale;

public class RevColorSensorV3 implements DistanceSensor, OpticalDistanceSensor, ColorRangeSensor, SwitchableLight {
    protected static final double apiLevelMin = 0.0;
    protected static final double apiLevelMax = 1.0;
    double aParam = 325.961;
    double binvParam = -0.75934;
    double cParam = 26.980;
    double maxDist = 6.0;
    private static final int proximitySaturation = 2047;
    private static final int colorSaturation = 65535;

    private final Hub hub;
    private final SensorState state;
    private final int bus;
    private float softwareGain = 1;
    private boolean ledOn = true;
    private I2cAddr address = I2cAddr.create7bit(0x52);
    private int red, green, blue, alpha;
    private final NormalizedRGBA colors = new NormalizedRGBA();

    public RevColorSensorV3(Hub hub, SensorState state, int bus) {
        this.hub = hub;
        this.state = state;
        this.bus = bus;
    }

    /** Chip counts after the driver's channel corrections: {red, green, blue, alpha}. */
    public static int[] simulatedCounts(SensorState s) {
        double d = s.colorDistanceMm;
        double max = Constants.num("colorV3.proximityMaxMm");
        if (Double.isNaN(d) || d > max) return new int[]{0, 0, 0, 0};
        double k = Constants.num("colorV3.countsWhiteAt10mm") * Math.pow(10.0 / Math.max(d, 1.0), 2);
        int rawGreen = (int) Math.min(65535, s.g * k);
        int rawBlue = (int) Math.min(65535, s.b * k / 1.55);
        int rawRed = (int) Math.min(65535, s.r * k / 1.07);
        int green = rawGreen;
        int blue = Range.clip((int) (1.55 * rawBlue), 0, 65535);
        int red = Range.clip((int) (1.07 * rawRed), 0, 65535);
        return new int[]{red, green, blue, (red + green + blue) / 3};
    }

    private int simulatedProximity() {
        double d = state.colorDistanceMm;
        if (Double.isNaN(d) || d > Constants.num("colorV3.proximityMaxMm")) return (int) Math.ceil(cParam);
        double inches = Math.max(d, 1.0) / 25.4;
        double raw = aParam * Math.pow(inches, 1.0 / binvParam) + cParam;
        return (int) Math.min(proximitySaturation, Math.round(raw)) & 0x7FF;
    }

    private void read() {
        try {
            hub.transact(hub.i2cNs);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private synchronized void updateColors() {
        read();
        int[] c = simulatedCounts(state);
        this.red = c[0];
        this.green = c[1];
        this.blue = c[2];
        this.alpha = (this.red + this.green + this.blue) / 3;
        this.colors.red = Range.clip(((float) this.red * this.softwareGain) / colorSaturation, 0f, 1f);
        this.colors.green = Range.clip(((float) this.green * this.softwareGain) / colorSaturation, 0f, 1f);
        this.colors.blue = Range.clip(((float) this.blue * this.softwareGain) / colorSaturation, 0f, 1f);
        float avg = (float) (this.red + this.green + this.blue) / 3;
        this.colors.alpha = (float) (-(65535f / (Math.pow(avg, 2) + 65535)) + 1);
    }

    @Override public synchronized int red() { updateColors(); return this.red; }
    @Override public synchronized int green() { updateColors(); return this.green; }
    @Override public synchronized int blue() { updateColors(); return this.blue; }
    @Override public synchronized int alpha() { updateColors(); return this.alpha; }
    @Override public synchronized int argb() { return getNormalizedColors().toColor(); }
    @Override public void setGain(float newGain) { this.softwareGain = newGain; }
    @Override public float getGain() { return this.softwareGain; }
    @Override public NormalizedRGBA getNormalizedColors() { updateColors(); return this.colors; }
    @Override public synchronized void enableLed(boolean enable) { ledOn = enable; }
    @Override public void enableLight(boolean enable) { enableLed(enable); }
    @Override public boolean isLightOn() { return ledOn; }
    @Override public synchronized I2cAddr getI2cAddress() { return address; }
    @Override public synchronized void setI2cAddress(I2cAddr i2cAddr) { address = i2cAddr; }

    @Override public double getLightDetected() {
        return Range.clip(Range.scale(getRawLightDetected(), 0, getRawLightDetectedMax(), apiLevelMin, apiLevelMax), apiLevelMin, apiLevelMax);
    }
    @Override public double getRawLightDetected() { return rawOptical(); }
    @Override public double getRawLightDetectedMax() { return proximitySaturation; }
    @Override public String status() { return String.format(Locale.getDefault(), "%s on %s", getDeviceName(), getConnectionInfo()); }

    @Override public double getDistance(DistanceUnit unit) {
        int rawOptical = rawOptical();
        double inOptical = inFromOptical(rawOptical);
        return unit.fromUnit(DistanceUnit.INCH, inOptical);
    }

    protected double inFromOptical(int rawOptical) {
        if (rawOptical <= cParam) return maxDist;
        double dist = Math.pow((rawOptical - cParam) / aParam, binvParam);
        return Math.min(dist, maxDist);
    }

    public int rawOptical() {
        read();
        return simulatedProximity() & 0x7FF;
    }

    @Override public HardwareDevice.Manufacturer getManufacturer() { return HardwareDevice.Manufacturer.Broadcom; }
    @Override public String getDeviceName() { return "Rev Color Sensor v3"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo() + "; I2C port " + bus; }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
