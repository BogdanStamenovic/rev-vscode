package org.pyftc.sim;

import com.google.gson.JsonObject;

/** RobotLog warnings/errors from real SDK classes, forwarded as `log` events. */
public final class SimLog {
    private SimLog() {}

    public static void warn(String tag, String message, Throwable t) {
        emit("warn", tag, message, t);
    }

    public static void error(String tag, String message, Throwable t) {
        emit("error", tag, message, t);
    }

    public static void info(String message) {
        emit("info", "sim", message, null);
    }

    private static void emit(String level, String tag, String message, Throwable t) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "log");
        o.addProperty("level", level);
        o.addProperty("t", SimClock.eventSeconds());
        String text = (tag == null ? "" : tag + ": ") + message;
        if (t != null) text += " (" + t + ")";
        o.addProperty("message", text);
        Out.send(o);
    }
}
