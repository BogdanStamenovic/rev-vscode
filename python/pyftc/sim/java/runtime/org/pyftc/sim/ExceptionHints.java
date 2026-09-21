package org.pyftc.sim;

import org.pyftc.sim.hw.Robot;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** A plain-language hint for the exceptions robot code most often hits. */
final class ExceptionHints {
    private static final Pattern NOT_FOUND = Pattern.compile("Unable to find a hardware device with name \"(.*)\" and type (\\w+)");

    private ExceptionHints() {}

    static String hint(Throwable e) {
        String msg = e.getMessage() == null ? "" : e.getMessage();
        Matcher m = NOT_FOUND.matcher(msg);
        if (e instanceof IllegalArgumentException && m.find()) {
            String wanted = m.group(1);
            String type = m.group(2);
            StringBuilder names = new StringBuilder();
            String closest = null;
            int best = Integer.MAX_VALUE;
            Robot r = Robot.get();
            if (r != null) {
                for (Robot.DeviceInfo d : r.devices) {
                    if (names.length() > 0) names.append(", ");
                    names.append('"').append(d.name).append("\" (").append(d.kind).append(')');
                    int dist = distance(wanted.toLowerCase(), d.name.toLowerCase());
                    if (dist < best) {
                        best = dist;
                        closest = d.name;
                    }
                }
            }
            String sameName = null;
            if (r != null) {
                for (Robot.DeviceInfo d : r.devices) if (d.name.equals(wanted)) sameName = d.kind;
            }
            if (sameName != null) {
                return "A device named \"" + wanted + "\" exists but it is a " + sameName + ", not a " + type + ". Ask hardwareMap for the type it is configured as.";
            }
            return "The name must match the robot configuration exactly, including upper/lower case."
                    + (closest != null && best <= Math.max(2, wanted.length() / 3) ? " Did you mean \"" + closest + "\"?" : "")
                    + " Configured devices: " + names + ".";
        }
        if (e instanceof NullPointerException) {
            return "Something was used before it was given a value, for example a device field that was never assigned with hardwareMap.get() or a list/dict entry that does not exist.";
        }
        if (e instanceof ClassCastException) {
            return "A value was used as a type it is not; with hardware this usually means hardwareMap.get() asked for a different device type than the configuration has.";
        }
        if (e.getClass().getName().equals("com.qualcomm.robotcore.exception.TargetPositionNotSetException")) {
            return "Call setTargetPosition() before switching the motor to RUN_TO_POSITION.";
        }
        if (e instanceof ArithmeticException) {
            return "Integer division or modulo by zero.";
        }
        if (e instanceof IndexOutOfBoundsException) {
            return "A list or array index outside its length.";
        }
        return "";
    }

    private static int distance(String a, String b) {
        int[] prev = new int[b.length() + 1];
        int[] cur = new int[b.length() + 1];
        for (int j = 0; j <= b.length(); j++) prev[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            cur[0] = i;
            for (int j = 1; j <= b.length(); j++) {
                int cost = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                cur[j] = Math.min(Math.min(cur[j - 1] + 1, prev[j] + 1), prev[j - 1] + cost);
            }
            int[] t = prev;
            prev = cur;
            cur = t;
        }
        return prev[b.length()];
    }
}
