package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.hardware.HardwareDevice;
import com.qualcomm.robotcore.util.ElapsedTime;

import org.pyftc.sim.hw.Robot;

import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.Collection;
import java.util.IdentityHashMap;
import java.util.Map;

/**
 * Snapshot of the running OpMode's own fields (those declared in translated user
 * classes), read by reflection while the OpMode thread is parked, so the values
 * are consistent. Devices are shown by their configured name.
 */
public final class FieldWatch {
    private static final int MAX_DEPTH = 4;
    private static final int MAX_ENTRIES = 200;

    private FieldWatch() {}

    static JsonObject snapshot() {
        OpMode m = OpModeHost.opMode();
        JsonObject out = new JsonObject();
        if (m == null) return out;
        IdentityHashMap<Object, Boolean> seen = new IdentityHashMap<Object, Boolean>();
        for (Class<?> c = m.getClass(); c != null && Locator.isUserClass(c.getName()); c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (f.isSynthetic()) continue;
                try {
                    f.setAccessible(true);
                    Object v = Modifier.isStatic(f.getModifiers()) ? f.get(null) : f.get(m);
                    out.add(f.getName(), value(v, 0, seen));
                } catch (Throwable t) {
                    out.addProperty(f.getName(), "<" + t.getClass().getSimpleName() + ">");
                }
            }
        }
        return out;
    }

    static Object describe(Object v) {
        return value(v, MAX_DEPTH - 1, new IdentityHashMap<Object, Boolean>());
    }

    private static Field elapsedStartField;

    private static long elapsedStart(ElapsedTime t) {
        try {
            if (elapsedStartField == null) {
                elapsedStartField = ElapsedTime.class.getDeclaredField("nsStartTime");
                elapsedStartField.setAccessible(true);
            }
            return elapsedStartField.getLong(t);
        } catch (ReflectiveOperationException e) {
            return SimClock.peekNs();
        }
    }

    private static JsonElement value(Object v, int depth, IdentityHashMap<Object, Boolean> seen) {
        if (v == null) return JsonNull.INSTANCE;
        if (v instanceof Number) {
            double d = ((Number) v).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) return new JsonPrimitive(String.valueOf(d));
            return new JsonPrimitive((Number) v);
        }
        if (v instanceof Boolean) return new JsonPrimitive((Boolean) v);
        if (v instanceof CharSequence || v instanceof Character) return new JsonPrimitive(v.toString());
        if (v instanceof Enum) return new JsonPrimitive(((Enum<?>) v).name());
        if (v instanceof HardwareDevice) {
            JsonObject o = new JsonObject();
            String name = deviceName(v);
            o.addProperty("@device", name == null ? v.getClass().getSimpleName() : name);
            return o;
        }
        if (v instanceof ElapsedTime) {
            // Read the start time directly: calling nanoseconds() on the OpMode thread would charge sim time.
            JsonObject o = new JsonObject();
            o.addProperty("@type", "ElapsedTime");
            o.addProperty("seconds", (SimClock.peekNs() - elapsedStart((ElapsedTime) v)) / 1e9);
            return o;
        }
        if (depth >= MAX_DEPTH) return new JsonPrimitive("<" + v.getClass().getSimpleName() + ">");
        if (seen.containsKey(v)) return new JsonPrimitive("<cycle>");
        seen.put(v, true);
        try {
            if (v instanceof Map) {
                JsonObject o = new JsonObject();
                o.addProperty("@type", v.getClass().getSimpleName());
                JsonObject entries = new JsonObject();
                int n = 0;
                for (Map.Entry<?, ?> e : ((Map<?, ?>) v).entrySet()) {
                    if (n++ >= MAX_ENTRIES) break;
                    entries.add(String.valueOf(e.getKey()), value(e.getValue(), depth + 1, seen));
                }
                o.add("@entries", entries);
                return o;
            }
            if (v instanceof Collection) {
                JsonArray a = new JsonArray();
                int n = 0;
                for (Object e : (Collection<?>) v) {
                    if (n++ >= MAX_ENTRIES) break;
                    a.add(value(e, depth + 1, seen));
                }
                return a;
            }
            if (v.getClass().isArray()) {
                JsonArray a = new JsonArray();
                int len = Math.min(Array.getLength(v), MAX_ENTRIES);
                for (int i = 0; i < len; i++) a.add(value(Array.get(v, i), depth + 1, seen));
                return a;
            }
            if (Locator.isUserClass(v.getClass().getName())) {
                JsonObject o = new JsonObject();
                o.addProperty("@type", v.getClass().getSimpleName());
                for (Class<?> c = v.getClass(); c != null && Locator.isUserClass(c.getName()); c = c.getSuperclass()) {
                    for (Field f : c.getDeclaredFields()) {
                        if (f.isSynthetic() || Modifier.isStatic(f.getModifiers())) continue;
                        f.setAccessible(true);
                        o.add(f.getName(), value(f.get(v), depth + 1, seen));
                    }
                }
                return o;
            }
            return new JsonPrimitive(v.toString());
        } catch (Throwable t) {
            return new JsonPrimitive("<" + t.getClass().getSimpleName() + ">");
        } finally {
            seen.remove(v);
        }
    }

    private static String deviceName(Object device) {
        Robot r = Robot.get();
        if (r == null) return null;
        for (Robot.DeviceInfo d : r.devices) if (d.device == device) return d.name;
        return null;
    }
}
