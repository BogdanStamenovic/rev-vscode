package org.pyftc.sim.hw;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import org.pyftc.sim.Constants;

import java.util.ArrayList;
import java.util.List;

/**
 * Physical parameters of one configured motor, from constants.json (published REV
 * specs where they exist, labelled placeholders where they do not) and, for the
 * UltraPlanetary, the cartridge stack the team set in the scene layout.
 *
 * DC motor model constants are derived so that the model hits the published
 * stall point and free-speed point exactly:
 *   R = V / I_stall, kt = T_stall / I_stall, ke = (V - I_free R) / w_free,
 *   friction torque = kt * I_free.
 */
public final class MotorSpec {
    public final String tag;
    public final String family;
    public final double voltage;
    public final double freeSpeedMotorRadS;
    public final double stallTorqueMotor;
    public final double stallCurrent;
    public final double freeCurrent;
    public final double ratio;
    public final double countsPerMotorRev;
    public final double rotorInertia;
    public final double efficiency;
    public final List<String> cartridges;
    public final boolean verified;
    public final String note;

    public final double resistance;
    public final double kt;
    public final double ke;
    public final double frictionTorque;

    private MotorSpec(String tag, String family, double voltage, double freeRpm, double stallTorque, double stallCurrent,
                      double freeCurrent, double ratio, double countsPerMotorRev, double rotorInertia, double efficiency,
                      List<String> cartridges, boolean verified, String note) {
        this.tag = tag;
        this.family = family;
        this.voltage = voltage;
        this.freeSpeedMotorRadS = freeRpm * 2 * Math.PI / 60.0;
        this.stallTorqueMotor = stallTorque;
        this.stallCurrent = stallCurrent;
        this.freeCurrent = freeCurrent;
        this.ratio = ratio;
        this.countsPerMotorRev = countsPerMotorRev;
        this.rotorInertia = rotorInertia;
        this.efficiency = efficiency;
        this.cartridges = cartridges;
        this.verified = verified;
        this.note = note;
        this.resistance = voltage / stallCurrent;
        this.kt = stallTorque / stallCurrent;
        this.ke = (voltage - freeCurrent * resistance) / freeSpeedMotorRadS;
        this.frictionTorque = kt * freeCurrent;
    }

    public double countsPerOutputRev() {
        return countsPerMotorRev * ratio;
    }

    public double freeSpeedOutputRpm() {
        return freeSpeedMotorRadS / ratio * 60.0 / (2 * Math.PI);
    }

    /** @param sdkProps the xmlTags props of the SDK type database (ticksPerRev, maxRPM, gearing) */
    public static MotorSpec forTag(String tag, JsonObject sdkProps, JsonObject layoutMotor) {
        if ("RevRoboticsUltraplanetaryHDHexMotor".equals(tag)) {
            List<String> stack = new ArrayList<String>();
            if (layoutMotor != null && layoutMotor.has("cartridges") && layoutMotor.get("cartridges").isJsonArray()) {
                JsonArray arr = layoutMotor.getAsJsonArray("cartridges");
                for (JsonElement e : arr) stack.add(e.getAsString());
            }
            boolean stackGiven = !stack.isEmpty();
            if (!stackGiven) {
                stack.add("4:1");
                stack.add("5:1");
            }
            double ratio = 1.0;
            for (String c : stack) ratio *= cartridgeRatio(c);
            return hdHex(tag, "hdhex-ultraplanetary", ratio, stack,
                    stackGiven ? "UltraPlanetary stack from the scene layout" : "UltraPlanetary stack not set: assumed 4:1 + 5:1 (nominal 20:1, actual 18.9:1)");
        }
        if ("RevRobotics20HDHexMotor".equals(tag) || "RevRobotics40HDHexMotor".equals(tag)) {
            double ratio = sdkProps != null && sdkProps.has("gearing") ? sdkProps.get("gearing").getAsDouble() : 20;
            return hdHex(tag, "hdhex-spur", ratio, new ArrayList<String>(),
                    "HD Hex spur gearbox (not in the FGC 2026 kit): nominal gearing from the SDK annotation");
        }
        if ("RevRoboticsCoreHexMotor".equals(tag)) {
            double ratio = Constants.num("coreHex.gearRatio");
            double freeRpmMotor = Constants.num("coreHex.freeSpeed") * ratio;
            double stallTorqueMotor = Constants.num("coreHex.stallTorque") / ratio;
            return new MotorSpec(tag, "corehex", Constants.num("coreHex.voltage"), freeRpmMotor, stallTorqueMotor,
                    Constants.num("coreHex.stallCurrent"), Constants.num("coreHex.freeCurrent"), ratio,
                    Constants.num("coreHex.countsPerMotorRev"), Constants.num("coreHex.rotorInertia"), 1.0,
                    new ArrayList<String>(), false,
                    "Core Hex: output speed/torque/current from REV; no-load current and rotor inertia not published");
        }
        double gearing = sdkProps != null && sdkProps.has("gearing") ? sdkProps.get("gearing").getAsDouble() : 52;
        double maxRpm = sdkProps != null && sdkProps.has("maxRPM") ? sdkProps.get("maxRPM").getAsDouble() : 165;
        double ticks = sdkProps != null && sdkProps.has("ticksPerRev") ? sdkProps.get("ticksPerRev").getAsDouble() : 1440;
        double stallTorqueMotor = Constants.num("genericMotor.stallTorqueAtOutputPerRatio");
        return new MotorSpec(tag, "generic", Constants.num("battery.nominalVoltage"), maxRpm * gearing, stallTorqueMotor,
                8.5, 0.0, gearing, ticks / gearing, Constants.num("hdHex.rotorInertia"), 1.0, new ArrayList<String>(), false,
                "Not a FGC 2026 kit motor: free speed and gearing from the SDK's @MotorType, torque is a placeholder");
    }

    private static MotorSpec hdHex(String tag, String family, double ratio, List<String> stack, String note) {
        boolean verified = Constants.verified("hdHex.freeSpeed") && Constants.verified("hdHex.stallTorque");
        return new MotorSpec(tag, family, Constants.num("hdHex.voltage"), Constants.num("hdHex.freeSpeed"),
                Constants.num("hdHex.stallTorque"), Constants.num("hdHex.stallCurrent"), Constants.num("hdHex.freeCurrent"),
                ratio, Constants.num("hdHex.countsPerMotorRev"), Constants.num("hdHex.rotorInertia"),
                Constants.num("ultraPlanetary.efficiency"), stack, verified, note);
    }

    public static double cartridgeRatio(String nominal) {
        String n = nominal.trim();
        if (n.startsWith("3")) return Constants.num("ultraPlanetary.cartridge3");
        if (n.startsWith("4")) return Constants.num("ultraPlanetary.cartridge4");
        if (n.startsWith("5")) return Constants.num("ultraPlanetary.cartridge5");
        throw new IllegalArgumentException("unknown UltraPlanetary cartridge '" + nominal + "' (use 3:1, 4:1 or 5:1)");
    }
}
