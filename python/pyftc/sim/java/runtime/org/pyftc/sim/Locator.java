package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.util.HashMap;
import java.util.Map;

/**
 * Maps Java stack frames of translated user classes back to the Python source,
 * through the translator's lineMap (Contract 3: lineMap[javaLine-1] = python
 * line, 0 = synthetic).
 */
public final class Locator {
    public static final class PyLoc {
        public final String file;
        public final int line;
        public final boolean approximate;

        PyLoc(String file, int line, boolean approximate) {
            this.file = file;
            this.line = line;
            this.approximate = approximate;
        }

        public JsonObject json() {
            JsonObject o = new JsonObject();
            o.addProperty("file", file);
            o.addProperty("line", line);
            if (approximate) o.addProperty("approximate", true);
            return o;
        }

        public String shortName() {
            int slash = Math.max(file.lastIndexOf('/'), file.lastIndexOf('\\'));
            return file.substring(slash + 1) + ":" + line;
        }
    }

    private static final class ClassMap {
        final String source;
        final int[] lineMap;

        ClassMap(String source, int[] lineMap) {
            this.source = source;
            this.lineMap = lineMap;
        }
    }

    private static final Map<String, ClassMap> maps = new HashMap<String, ClassMap>();

    private Locator() {}

    static void load(JsonObject lineMaps) {
        for (Map.Entry<String, JsonElement> e : lineMaps.entrySet()) {
            JsonObject o = e.getValue().getAsJsonObject();
            JsonArray arr = o.getAsJsonArray("lineMap");
            int[] lm = new int[arr.size()];
            for (int i = 0; i < lm.length; i++) lm[i] = arr.get(i).getAsInt();
            maps.put(e.getKey(), new ClassMap(o.get("source").getAsString(), lm));
        }
    }

    private static String outer(String className) {
        int dollar = className.indexOf('$');
        return dollar < 0 ? className : className.substring(0, dollar);
    }

    public static boolean isUserClass(String className) {
        return maps.containsKey(outer(className));
    }

    public static PyLoc map(StackTraceElement f) {
        ClassMap m = maps.get(outer(f.getClassName()));
        if (m == null || f.getLineNumber() <= 0) return null;
        int idx = f.getLineNumber() - 1;
        if (idx < m.lineMap.length && m.lineMap[idx] > 0) {
            return new PyLoc(m.source, m.lineMap[idx], false);
        }
        for (int i = Math.min(idx, m.lineMap.length - 1); i >= 0; i--) {
            if (m.lineMap[i] > 0) return new PyLoc(m.source, m.lineMap[i], true);
        }
        return new PyLoc(m.source, 1, true);
    }

    /** Top-most frame that belongs to user code. */
    public static PyLoc userFrame(StackTraceElement[] stack) {
        for (StackTraceElement f : stack) {
            if (isUserClass(f.getClassName())) {
                PyLoc p = map(f);
                if (p != null) return p;
            }
        }
        return null;
    }

    public static PyLoc here() {
        return userFrame(new Throwable().getStackTrace());
    }

    public static String sourceOf(String className) {
        ClassMap m = maps.get(outer(className));
        return m == null ? null : m.source;
    }
}
