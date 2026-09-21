package org.pyftc.sim.hw;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import org.pyftc.sim.Constants;

/** Scene-driven input of one sensor (set by `sensor` commands or the layout's override). */
public final class SensorState {
    public boolean pressed;
    public boolean digitalState = true;
    public double volts;
    public double angleDeg;
    /** Distance to the nearest target along the sensor's axis, or NaN for nothing in range. */
    public double distanceMm = Double.NaN;
    public double r, g, b;
    public double colorDistanceMm = Double.NaN;

    void apply(JsonObject v) {
        if (v.has("pressed")) pressed = v.get("pressed").getAsBoolean();
        if (v.has("state")) digitalState = v.get("state").getAsBoolean();
        if (v.has("volts")) volts = v.get("volts").getAsDouble();
        if (v.has("angleDeg")) {
            angleDeg = v.get("angleDeg").getAsDouble();
            double range = Constants.num("potentiometer.rangeDeg");
            double a = Math.max(0, Math.min(range, angleDeg));
            volts = a / range * Constants.num("potentiometer.maxVolts");
        }
        if (v.has("mm")) distanceMm = numOrNaN(v.get("mm"));
        if (v.has("r")) r = clamp01(v.get("r").getAsDouble());
        if (v.has("g")) g = clamp01(v.get("g").getAsDouble());
        if (v.has("b")) b = clamp01(v.get("b").getAsDouble());
        if (v.has("distanceMm")) colorDistanceMm = numOrNaN(v.get("distanceMm"));
    }

    private static double numOrNaN(JsonElement e) {
        return e == null || e.isJsonNull() ? Double.NaN : e.getAsDouble();
    }

    private static double clamp01(double x) {
        return Math.max(0, Math.min(1, x));
    }

    void describe(String kind, Hub hub, int port, JsonObject o) {
        if ("touch".equals(kind)) {
            o.addProperty("pressed", pressed);
        } else if ("digital".equals(kind)) {
            o.addProperty("state", hub.digitalMode[port] == com.qualcomm.robotcore.hardware.DigitalChannel.Mode.OUTPUT ? hub.digitalOutput[port] : hub.digitalInput[port]);
            o.addProperty("mode", hub.digitalMode[port].toString());
        } else if ("analog".equals(kind)) {
            o.addProperty("volts", hub.analogVolts[port]);
        } else if ("potentiometer".equals(kind)) {
            o.addProperty("volts", hub.analogVolts[port]);
            o.addProperty("angleDeg", angleDeg);
        } else if ("distance".equals(kind)) {
            if (Double.isNaN(distanceMm)) o.add("mm", com.google.gson.JsonNull.INSTANCE);
            else o.addProperty("mm", distanceMm);
            o.addProperty("reads", com.qualcomm.hardware.rev.Rev2mDistanceSensor.simulatedReadingMm(this));
        } else if ("color".equals(kind)) {
            int[] c = com.qualcomm.hardware.rev.RevColorSensorV3.simulatedCounts(this);
            o.addProperty("red", c[0]);
            o.addProperty("green", c[1]);
            o.addProperty("blue", c[2]);
            o.addProperty("alpha", c[3]);
            if (Double.isNaN(colorDistanceMm)) o.add("distanceMm", com.google.gson.JsonNull.INSTANCE);
            else o.addProperty("distanceMm", colorDistanceMm);
            o.addProperty("r", r);
            o.addProperty("g", g);
            o.addProperty("b", b);
        }
    }
}
