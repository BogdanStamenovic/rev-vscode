package org.pyftc.sim;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.SimOpModeAccess;
import com.qualcomm.robotcore.hardware.Gamepad;

import java.util.Map;

/**
 * Driver Station inputs. Gamepad state arrives in the SDK's canonical field
 * names (a/b/x/y, sticks with up = -1) and reaches the OpMode the way the RC
 * delivers a Driver Station packet: a Gamepad object is filled in and handed to
 * newGamepadDataAvailable(), whose Gamepad.copy() goes through the SDK's own
 * serialisation, button aliasing (cross = a, ...) and edge detection.
 */
public final class Inputs {
    private static final JsonObject[] state = {new JsonObject(), new JsonObject()};
    private static final String[] type = {"UNKNOWN", "UNKNOWN"};

    private Inputs() {}

    static synchronized void setGamepad(int index, String gamepadType, JsonObject s) {
        if (index < 1 || index > 2) return;
        JsonObject prev = state[index - 1];
        JsonObject changed = new JsonObject();
        for (Map.Entry<String, JsonElement> e : s.entrySet()) {
            if (!prev.has(e.getKey()) || !prev.get(e.getKey()).equals(e.getValue())) changed.add(e.getKey(), e.getValue());
        }
        state[index - 1] = copy(s);
        if (gamepadType != null) type[index - 1] = gamepadType;
        if (changed.size() > 0) OpModeHost.recordEvent("gamepad" + index, "input", changed, null);
        pushGamepads();
    }

    static synchronized JsonObject gamepadState(int index) {
        return copy(state[index - 1]);
    }

    // gson 2.8 (the version the SDK ships) has no public deepCopy(); state is flat.
    private static JsonObject copy(JsonObject o) {
        JsonObject c = new JsonObject();
        for (Map.Entry<String, JsonElement> e : o.entrySet()) c.add(e.getKey(), e.getValue());
        return c;
    }

    static synchronized void pushGamepads() {
        OpMode m = OpModeHost.opMode();
        if (m == null || m.gamepad1 == null) return;
        SimOpModeAccess.gamepads(m, build(0), build(1));
    }

    private static float f(JsonObject s, String k) {
        return s.has(k) && !s.get(k).isJsonNull() ? Math.max(-1f, Math.min(1f, s.get(k).getAsFloat())) : 0f;
    }

    private static boolean b(JsonObject s, String k) {
        return s.has(k) && !s.get(k).isJsonNull() && s.get(k).getAsBoolean();
    }

    private static Gamepad build(int i) {
        JsonObject s = state[i];
        Gamepad g = new Gamepad();
        try {
            g.type = Gamepad.Type.valueOf(type[i]);
        } catch (IllegalArgumentException e) {
            g.type = Gamepad.Type.UNKNOWN;
        }
        g.left_stick_x = f(s, "left_stick_x");
        g.left_stick_y = f(s, "left_stick_y");
        g.right_stick_x = f(s, "right_stick_x");
        g.right_stick_y = f(s, "right_stick_y");
        g.left_trigger = Math.max(0f, f(s, "left_trigger"));
        g.right_trigger = Math.max(0f, f(s, "right_trigger"));
        g.dpad_up = b(s, "dpad_up");
        g.dpad_down = b(s, "dpad_down");
        g.dpad_left = b(s, "dpad_left");
        g.dpad_right = b(s, "dpad_right");
        g.a = b(s, "a");
        g.b = b(s, "b");
        g.x = b(s, "x");
        g.y = b(s, "y");
        g.guide = b(s, "guide");
        g.start = b(s, "start");
        g.back = b(s, "back");
        g.left_bumper = b(s, "left_bumper");
        g.right_bumper = b(s, "right_bumper");
        g.left_stick_button = b(s, "left_stick_button");
        g.right_stick_button = b(s, "right_stick_button");
        g.touchpad = b(s, "touchpad");
        return g;
    }
}
