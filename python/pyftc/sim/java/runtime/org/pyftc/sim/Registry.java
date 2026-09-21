package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.qualcomm.robotcore.eventloop.opmode.Autonomous;
import com.qualcomm.robotcore.eventloop.opmode.Disabled;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;

import java.util.ArrayList;
import java.util.List;

/**
 * OpModes the Driver Station would list: classes that extend OpMode and carry
 * @TeleOp or @Autonomous without @Disabled, named by the annotation (default:
 * the class's simple name), as the RC's annotation-based registration does.
 */
public final class Registry {
    public static final class Entry {
        public final String name;
        public final String group;
        public final String kind;
        public final Class<?> clazz;
        public final String source;

        Entry(String name, String group, String kind, Class<?> clazz, String source) {
            this.name = name;
            this.group = group;
            this.kind = kind;
            this.clazz = clazz;
            this.source = source;
        }
    }

    private static final List<Entry> entries = new ArrayList<Entry>();

    private Registry() {}

    static void load(JsonArray classes) {
        for (JsonElement e : classes) {
            JsonObject c = e.getAsJsonObject();
            String className = c.get("className").getAsString();
            Class<?> clazz;
            try {
                clazz = Class.forName(className, false, Registry.class.getClassLoader());
            } catch (Throwable t) {
                SimLog.error("sim", "could not load " + className + ": " + t, t);
                continue;
            }
            if (!OpMode.class.isAssignableFrom(clazz) || clazz.isAnnotationPresent(Disabled.class)) continue;
            TeleOp teleOp = clazz.getAnnotation(TeleOp.class);
            Autonomous auto = clazz.getAnnotation(Autonomous.class);
            if (teleOp == null && auto == null) continue;
            String name = teleOp != null ? teleOp.name() : auto.name();
            String group = teleOp != null ? teleOp.group() : auto.group();
            if (name == null || name.trim().isEmpty()) name = clazz.getSimpleName();
            entries.add(new Entry(name, group, teleOp != null ? "TeleOp" : "Autonomous", clazz,
                    c.has("source") ? c.get("source").getAsString() : null));
        }
    }

    static Entry find(String name) {
        for (Entry e : entries) if (e.name.equals(name)) return e;
        for (Entry e : entries) if (e.clazz.getSimpleName().equals(name)) return e;
        return null;
    }

    static JsonArray describe() {
        JsonArray arr = new JsonArray();
        for (Entry e : entries) {
            JsonObject o = new JsonObject();
            o.addProperty("name", e.name);
            o.addProperty("group", e.group);
            o.addProperty("kind", e.kind);
            o.addProperty("className", e.clazz.getName());
            if (e.source != null) o.addProperty("source", e.source);
            arr.add(o);
        }
        return arr;
    }
}
