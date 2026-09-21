package org.pyftc.sim;

import com.google.gson.JsonObject;

import org.pyftc.sim.hw.Robot;

/** Contract 5 commands, applied on the scheduler thread at a step boundary. */
final class Commands {
    private Commands() {}

    static void apply(JsonObject c) {
        String type = c.has("type") ? c.get("type").getAsString() : "";
        try {
            switch (type) {
                case "init":
                    OpModeHost.init(c.get("opMode").getAsString());
                    break;
                case "start":
                    OpModeHost.start();
                    break;
                case "stop":
                    OpModeHost.stop();
                    break;
                case "gamepad":
                    Inputs.setGamepad(c.get("index").getAsInt(),
                            c.has("gamepadType") ? c.get("gamepadType").getAsString() : null,
                            c.getAsJsonObject("state"));
                    break;
                case "sensor":
                    Robot.get().setSensor(c.get("device").getAsString(), c.getAsJsonObject("value"));
                    break;
                case "layout":
                    Robot.get().applyLayout(c.getAsJsonObject("layout"));
                    break;
                case "pause":
                    Scheduler.paused = true;
                    Scheduler.requestStateSoon();
                    break;
                case "resume":
                    Scheduler.paused = false;
                    Scheduler.requestStateSoon();
                    break;
                case "speed":
                    Scheduler.speed = Math.max(0.05, Math.min(8, c.get("factor").getAsDouble()));
                    break;
                case "quit":
                    Scheduler.quit = true;
                    break;
                default:
                    SimLog.warn("sim", "unknown command type '" + type + "'", null);
            }
        } catch (RuntimeException e) {
            SimLog.error("sim", "command " + type + " failed: " + e, e);
        }
    }
}
