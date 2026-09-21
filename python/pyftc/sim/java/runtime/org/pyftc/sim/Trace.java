package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

/**
 * Sink for the simulator-only line/assignment hooks the translator adds with
 * --sim-trace (never in code deployed to the robot). Each hook records which
 * Python line ran and what a local variable was assigned; nothing here charges
 * sim time or touches user state, so an instrumented build behaves exactly like
 * the plain one (the test suite checks that).
 */
public final class Trace {
    private static final Object LOCK = new Object();
    private static String[] files = new String[0];
    private static List<TreeSet<Integer>> current = new ArrayList<TreeSet<Integer>>();
    private static List<TreeSet<Integer>> last = new ArrayList<TreeSet<Integer>>();
    private static final Map<String, Map<String, Object>> locals = new LinkedHashMap<String, Map<String, Object>>();
    private static List<Object[]> changedCurrent = new ArrayList<Object[]>();
    private static List<Object[]> changedLast = new ArrayList<Object[]>();
    private static long iterationsClosed;

    private Trace() {}

    static void setFiles(String[] f) {
        synchronized (LOCK) {
            files = f;
            reset();
        }
    }

    static void reset() {
        synchronized (LOCK) {
            current = new ArrayList<TreeSet<Integer>>();
            last = new ArrayList<TreeSet<Integer>>();
            for (int i = 0; i < files.length; i++) {
                current.add(new TreeSet<Integer>());
                last.add(new TreeSet<Integer>());
            }
            locals.clear();
            changedCurrent = new ArrayList<Object[]>();
            changedLast = new ArrayList<Object[]>();
            iterationsClosed = 0;
        }
    }

    /** A Python line is about to run. */
    public static void l(int file, int line) {
        synchronized (LOCK) {
            if (file >= 0 && file < current.size()) current.get(file).add(line);
        }
    }

    /** A local variable was assigned on a Python line. */
    public static void a(int file, int line, String scope, String name, Object value) {
        synchronized (LOCK) {
            Map<String, Object> m = locals.get(scope);
            if (m == null) {
                m = new LinkedHashMap<String, Object>();
                locals.put(scope, m);
            }
            m.put(name, snapshot(value));
            changedCurrent.add(new Object[]{file, line, name, snapshot(value)});
            if (changedCurrent.size() > 500) changedCurrent.remove(0);
        }
    }

    private static Object snapshot(Object v) {
        if (v == null || v instanceof Number || v instanceof Boolean || v instanceof String || v instanceof Character) return v;
        if (v instanceof Enum) return ((Enum<?>) v).name();
        return FieldWatch.describe(v);
    }

    /** Loop iteration boundary (opModeIsActive / loop()). */
    static void boundary() {
        synchronized (LOCK) {
            boolean any = false;
            for (TreeSet<Integer> s : current) if (!s.isEmpty()) any = true;
            if (!any) return;
            last = current;
            current = new ArrayList<TreeSet<Integer>>();
            for (int i = 0; i < files.length; i++) current.add(new TreeSet<Integer>());
            changedLast = changedCurrent;
            changedCurrent = new ArrayList<Object[]>();
            iterationsClosed++;
        }
    }

    static boolean enabled() {
        return files.length > 0;
    }

    static JsonObject snapshotJson() {
        JsonObject o = new JsonObject();
        o.addProperty("type", "trace");
        o.addProperty("t", SimClock.seconds());
        o.addProperty("iteration", OpModeHost.iteration());
        synchronized (LOCK) {
            JsonObject lines = new JsonObject();
            // Before the first loop boundary (init code) show what has run so far.
            List<TreeSet<Integer>> src = iterationsClosed == 0 ? current : last;
            for (int i = 0; i < files.length && i < src.size(); i++) {
                JsonArray arr = new JsonArray();
                for (Integer n : src.get(i)) arr.add(n);
                lines.add(files[i], arr);
            }
            o.add("lines", lines);
            JsonArray changed = new JsonArray();
            List<Object[]> ch = iterationsClosed == 0 ? changedCurrent : changedLast;
            for (Object[] c : ch) {
                JsonObject e = new JsonObject();
                e.addProperty("name", (String) c[2]);
                e.add("value", Out.gson().toJsonTree(c[3]));
                int f = (Integer) c[0];
                if (f >= 0 && f < files.length) e.addProperty("file", files[f]);
                e.addProperty("line", (Integer) c[1]);
                changed.add(e);
            }
            o.add("changed", changed);
            JsonObject loc = new JsonObject();
            for (Map.Entry<String, Map<String, Object>> e : locals.entrySet()) {
                JsonObject m = new JsonObject();
                for (Map.Entry<String, Object> v : e.getValue().entrySet()) m.add(v.getKey(), Out.gson().toJsonTree(v.getValue()));
                loc.add(e.getKey(), m);
            }
            o.add("locals", loc);
        }
        return o;
    }
}
