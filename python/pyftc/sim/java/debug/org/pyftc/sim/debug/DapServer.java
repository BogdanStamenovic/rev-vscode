package org.pyftc.sim.debug;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sun.jdi.AbsentInformationException;
import com.sun.jdi.ArrayReference;
import com.sun.jdi.Bootstrap;
import com.sun.jdi.BooleanValue;
import com.sun.jdi.CharValue;
import com.sun.jdi.ClassType;
import com.sun.jdi.Field;
import com.sun.jdi.IncompatibleThreadStateException;
import com.sun.jdi.LocalVariable;
import com.sun.jdi.Location;
import com.sun.jdi.ObjectReference;
import com.sun.jdi.PrimitiveValue;
import com.sun.jdi.ReferenceType;
import com.sun.jdi.StackFrame;
import com.sun.jdi.StringReference;
import com.sun.jdi.ThreadReference;
import com.sun.jdi.Value;
import com.sun.jdi.VirtualMachine;
import com.sun.jdi.connect.AttachingConnector;
import com.sun.jdi.connect.Connector;
import com.sun.jdi.event.BreakpointEvent;
import com.sun.jdi.event.ClassPrepareEvent;
import com.sun.jdi.event.Event;
import com.sun.jdi.event.EventSet;
import com.sun.jdi.event.StepEvent;
import com.sun.jdi.event.VMDeathEvent;
import com.sun.jdi.event.VMDisconnectEvent;
import com.sun.jdi.request.BreakpointRequest;
import com.sun.jdi.request.ClassPrepareRequest;
import com.sun.jdi.request.EventRequest;
import com.sun.jdi.request.EventRequestManager;
import com.sun.jdi.request.StepRequest;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Debug Adapter (DAP over stdio) for the simulator, in Python terms.
 *
 * It attaches with JDI to the running simulator JVM (started with a JDWP agent),
 * so breakpoints, stepping and variables are the JVM's own, not a
 * reimplementation. Python file:line is mapped to Java lines through the
 * translator's lineMap (manifest.json), both ways. Only the OpMode thread is
 * ever suspended; while it is, the adapter sets Scheduler.debuggerHold so sim
 * time, physics and the motors freeze with it.
 */
public final class DapServer {
    private static final String USER_PACKAGE = "org.firstinspires.ftc.teamcode.pyftc.";
    private final Gson gson = new Gson();
    private final OutputStream out;
    private int seq = 1;
    private VirtualMachine vm;
    private final Map<String, int[]> lineMaps = new HashMap<String, int[]>();
    private final Map<String, String> sources = new HashMap<String, String>();
    private final Map<String, List<int[]>> pendingBreakpoints = new HashMap<String, List<int[]>>();
    private final Map<String, List<BreakpointRequest>> activeBreakpoints = new HashMap<String, List<BreakpointRequest>>();
    private final Map<Integer, Object> handles = new HashMap<Integer, Object>();
    private int nextHandle = 1000;
    private ThreadReference stoppedThread;
    private int stepStartLine = -1;
    private int stepStartDepth = -1;
    private String stepStartFile;
    private int stepKind = -1;
    private final Object lock = new Object();
    private final Map<String, Integer> breakpointIds = new HashMap<String, Integer>();
    private int nextBreakpointId = 1;

    private DapServer(OutputStream out) {
        this.out = out;
    }

    public static void main(String[] args) throws Exception {
        String port = null;
        String manifest = null;
        for (int i = 0; i < args.length; i++) {
            if ("--port".equals(args[i])) port = args[++i];
            else if ("--manifest".equals(args[i])) manifest = args[++i];
        }
        DapServer s = new DapServer(System.out);
        System.setOut(System.err);
        s.loadManifest(manifest);
        s.serve(System.in, port);
    }

    private void loadManifest(String path) throws IOException {
        JsonObject m = new JsonParser().parse(new String(Files.readAllBytes(Paths.get(path)), StandardCharsets.UTF_8)).getAsJsonObject();
        for (Map.Entry<String, JsonElement> e : m.getAsJsonObject("lineMaps").entrySet()) {
            JsonObject o = e.getValue().getAsJsonObject();
            JsonArray a = o.getAsJsonArray("lineMap");
            int[] lm = new int[a.size()];
            for (int i = 0; i < lm.length; i++) lm[i] = a.get(i).getAsInt();
            lineMaps.put(e.getKey(), lm);
            sources.put(e.getKey(), o.get("source").getAsString());
        }
    }

    // ------------------------------------------------------------------ framing

    private void serve(InputStream in, String port) throws IOException {
        BufferedInputStream bin = new BufferedInputStream(in);
        while (true) {
            int length = -1;
            String line;
            while ((line = readLine(bin)) != null && !line.isEmpty()) {
                if (line.toLowerCase().startsWith("content-length:")) length = Integer.parseInt(line.substring(15).trim());
            }
            if (line == null || length < 0) return;
            byte[] body = new byte[length];
            int read = 0;
            while (read < length) {
                int n = bin.read(body, read, length - read);
                if (n < 0) return;
                read += n;
            }
            JsonObject req = new JsonParser().parse(new String(body, StandardCharsets.UTF_8)).getAsJsonObject();
            try {
                handle(req, port);
            } catch (Exception e) {
                respond(req, false, null, e.toString());
            }
        }
    }

    private static String readLine(InputStream in) throws IOException {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        int c;
        while ((c = in.read()) >= 0) {
            if (c == '\n') break;
            if (c != '\r') b.write(c);
        }
        if (c < 0 && b.size() == 0) return null;
        return new String(b.toByteArray(), StandardCharsets.UTF_8);
    }

    private void send(JsonObject msg) {
        synchronized (out) {
            msg.addProperty("seq", seq++);
            byte[] body = gson.toJson(msg).getBytes(StandardCharsets.UTF_8);
            try {
                out.write(("Content-Length: " + body.length + "\r\n\r\n").getBytes(StandardCharsets.US_ASCII));
                out.write(body);
                out.flush();
            } catch (IOException ignored) {
            }
        }
    }

    private void respond(JsonObject req, boolean ok, JsonObject body, String message) {
        JsonObject r = new JsonObject();
        r.addProperty("type", "response");
        r.addProperty("request_seq", req.get("seq").getAsInt());
        r.addProperty("command", req.get("command").getAsString());
        r.addProperty("success", ok);
        if (message != null) r.addProperty("message", message);
        if (body != null) r.add("body", body);
        send(r);
    }

    private void event(String name, JsonObject body) {
        JsonObject e = new JsonObject();
        e.addProperty("type", "event");
        e.addProperty("event", name);
        if (body != null) e.add("body", body);
        send(e);
    }

    // ------------------------------------------------------------------ requests

    private void handle(JsonObject req, String port) throws Exception {
        String cmd = req.get("command").getAsString();
        JsonObject args = req.has("arguments") && req.get("arguments").isJsonObject() ? req.getAsJsonObject("arguments") : new JsonObject();
        switch (cmd) {
            case "initialize": {
                JsonObject caps = new JsonObject();
                caps.addProperty("supportsConfigurationDoneRequest", true);
                caps.addProperty("supportsEvaluateForHovers", true);
                respond(req, true, caps, null);
                break;
            }
            case "attach":
            case "launch":
                attach(port);
                respond(req, true, null, null);
                event("initialized", null);
                break;
            case "setBreakpoints":
                respond(req, true, setBreakpoints(args), null);
                break;
            case "setExceptionBreakpoints":
            case "configurationDone":
                respond(req, true, null, null);
                break;
            case "threads": {
                JsonObject body = new JsonObject();
                JsonArray threads = new JsonArray();
                ThreadReference t = opModeThread();
                JsonObject o = new JsonObject();
                o.addProperty("id", t == null ? 1 : (int) t.uniqueID());
                o.addProperty("name", t == null ? "OpMode (not running)" : "OpMode");
                threads.add(o);
                body.add("threads", threads);
                respond(req, true, body, null);
                break;
            }
            case "stackTrace":
                respond(req, true, stackTrace(), null);
                break;
            case "scopes":
                respond(req, true, scopes(args.get("frameId").getAsInt()), null);
                break;
            case "variables":
                respond(req, true, variables(args.get("variablesReference").getAsInt()), null);
                break;
            case "evaluate":
                respond(req, true, evaluate(args), null);
                break;
            case "continue":
                resume();
                JsonObject cb = new JsonObject();
                cb.addProperty("allThreadsContinued", true);
                respond(req, true, cb, null);
                break;
            case "next":
                step(StepRequest.STEP_OVER);
                respond(req, true, null, null);
                break;
            case "stepIn":
                step(StepRequest.STEP_INTO);
                respond(req, true, null, null);
                break;
            case "stepOut":
                step(StepRequest.STEP_OUT);
                respond(req, true, null, null);
                break;
            case "pause": {
                ThreadReference t = opModeThread();
                if (t != null) {
                    t.suspend();
                    stopped(t, "pause");
                }
                respond(req, true, null, null);
                break;
            }
            case "disconnect":
            case "terminate":
                if (vm != null) {
                    setHold(false);
                    try {
                        vm.eventRequestManager().deleteAllBreakpoints();
                        vm.resume();
                        vm.dispose();
                    } catch (RuntimeException ignored) {
                    }
                }
                respond(req, true, null, null);
                System.exit(0);
                break;
            default:
                respond(req, true, null, null);
        }
    }

    private void attach(String port) throws Exception {
        AttachingConnector conn = null;
        for (AttachingConnector c : Bootstrap.virtualMachineManager().attachingConnectors()) {
            if ("dt_socket".equals(c.transport().name())) conn = c;
        }
        if (conn == null) throw new IllegalStateException("no JDWP socket connector in this JDK");
        Map<String, Connector.Argument> a = conn.defaultArguments();
        a.get("hostname").setValue("127.0.0.1");
        a.get("port").setValue(port);
        vm = conn.attach(a);
        EventRequestManager erm = vm.eventRequestManager();
        ClassPrepareRequest cpr = erm.createClassPrepareRequest();
        cpr.addClassFilter(USER_PACKAGE + "*");
        cpr.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        cpr.enable();
        Thread t = new Thread(this::eventLoop, "jdi-events");
        t.setDaemon(true);
        t.start();
    }

    private ThreadReference opModeThread() {
        if (vm == null) return null;
        for (ThreadReference t : vm.allThreads()) {
            if ("OpModeThread".equals(t.name())) return t;
        }
        return null;
    }

    // ------------------------------------------------------------------ breakpoints

    private JsonObject setBreakpoints(JsonObject args) {
        String file = args.getAsJsonObject("source").get("path").getAsString();
        List<int[]> lines = new ArrayList<int[]>();
        if (args.has("breakpoints")) {
            for (JsonElement e : args.getAsJsonArray("breakpoints")) lines.add(new int[]{e.getAsJsonObject().get("line").getAsInt()});
        }
        synchronized (lock) {
            pendingBreakpoints.put(file, lines);
            for (BreakpointRequest r : activeBreakpoints.getOrDefault(file, new ArrayList<BreakpointRequest>())) {
                vm.eventRequestManager().deleteEventRequest(r);
            }
            activeBreakpoints.put(file, new ArrayList<BreakpointRequest>());
        }
        JsonArray out = new JsonArray();
        for (int[] l : lines) {
            boolean verified = install(file, l[0]);
            JsonObject b = new JsonObject();
            b.addProperty("id", breakpointId(file, l[0]));
            b.addProperty("verified", verified);
            b.addProperty("line", l[0]);
            if (!verified) b.addProperty("message", "No code on this line in the translated OpMode (or its class is not loaded yet)");
            out.add(b);
        }
        JsonObject body = new JsonObject();
        body.add("breakpoints", out);
        return body;
    }

    private synchronized int breakpointId(String file, int line) {
        String key = file + ":" + line;
        Integer id = breakpointIds.get(key);
        if (id == null) {
            id = nextBreakpointId++;
            breakpointIds.put(key, id);
        }
        return id;
    }

    /** Break on the first Java line that maps to this Python line, in every loaded class of that file. */
    private boolean install(String file, int pyLine) {
        boolean any = false;
        for (Map.Entry<String, String> e : sources.entrySet()) {
            if (!samePath(e.getValue(), file)) continue;
            int[] lm = lineMaps.get(e.getKey());
            for (ReferenceType rt : vm.classesByName(e.getKey())) {
                for (int j = 0; j < lm.length; j++) {
                    if (lm[j] != pyLine) continue;
                    if (!rt.isPrepared()) break;
                    try {
                        List<Location> locs = rt.locationsOfLine(j + 1);
                        if (locs.isEmpty()) continue;
                        BreakpointRequest br = vm.eventRequestManager().createBreakpointRequest(locs.get(0));
                        br.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
                        br.enable();
                        synchronized (lock) {
                            activeBreakpoints.computeIfAbsent(file, k -> new ArrayList<BreakpointRequest>()).add(br);
                        }
                        any = true;
                        break;
                    } catch (AbsentInformationException ignored) {
                    }
                }
            }
        }
        return any;
    }

    private static boolean samePath(String a, String b) {
        try {
            return Paths.get(a).toRealPath().equals(Paths.get(b).toRealPath());
        } catch (IOException e) {
            return a.equals(b);
        }
    }

    // ------------------------------------------------------------------ events

    private void eventLoop() {
        try {
            while (true) {
                EventSet set = vm.eventQueue().remove();
                boolean resume = true;
                for (Event ev : set) {
                    if (ev instanceof ClassPrepareEvent) {
                        String name = ((ClassPrepareEvent) ev).referenceType().name();
                        String file = sources.get(name.split("\\$")[0]);
                        if (file != null) {
                            List<int[]> pend;
                            synchronized (lock) {
                                pend = pendingBreakpoints.getOrDefault(file, new ArrayList<int[]>());
                            }
                            for (int[] l : pend) {
                                // The OpMode class is prepared at INIT: the pending breakpoint becomes real now.
                                if (install(file, l[0])) {
                                    JsonObject bp = new JsonObject();
                                    bp.addProperty("id", breakpointId(file, l[0]));
                                    bp.addProperty("verified", true);
                                    bp.addProperty("line", l[0]);
                                    JsonObject b = new JsonObject();
                                    b.addProperty("reason", "changed");
                                    b.add("breakpoint", bp);
                                    event("breakpoint", b);
                                }
                            }
                        }
                    } else if (ev instanceof BreakpointEvent) {
                        resume = false;
                        stopped(((BreakpointEvent) ev).thread(), "breakpoint");
                    } else if (ev instanceof StepEvent) {
                        StepEvent se = (StepEvent) ev;
                        if (keepStepping(se)) continue;
                        vm.eventRequestManager().deleteEventRequest(se.request());
                        resume = false;
                        stopped(se.thread(), "step");
                    } else if (ev instanceof VMDeathEvent || ev instanceof VMDisconnectEvent) {
                        event("terminated", null);
                        return;
                    }
                }
                if (resume) set.resume();
            }
        } catch (InterruptedException | RuntimeException e) {
            JsonObject o = new JsonObject();
            o.addProperty("category", "console");
            java.io.StringWriter sw = new java.io.StringWriter();
            e.printStackTrace(new java.io.PrintWriter(sw));
            o.addProperty("output", "simulator debugger stopped: " + sw + "\n");
            event("output", o);
            event("terminated", null);
        }
    }

    /** One Python line is several Java lines, and some Java lines are synthetic: step until the Python line changes. */
    private boolean keepStepping(StepEvent se) {
        Location loc = se.location();
        int py = pyLine(loc);
        if (py <= 0) return true;
        try {
            int depth = se.thread().frameCount();
            String file = sources.get(loc.declaringType().name().split("\\$")[0]);
            if (stepKind == StepRequest.STEP_OVER && py == stepStartLine && depth == stepStartDepth && file != null && file.equals(stepStartFile)) return true;
            if (stepKind == StepRequest.STEP_INTO && py == stepStartLine && depth == stepStartDepth && file != null && file.equals(stepStartFile)) return true;
        } catch (IncompatibleThreadStateException ignored) {
        }
        return false;
    }

    private int pyLine(Location loc) {
        int[] lm = lineMaps.get(loc.declaringType().name().split("\\$")[0]);
        int j = loc.lineNumber();
        if (lm == null || j <= 0 || j > lm.length) return -1;
        return lm[j - 1];
    }

    private void stopped(ThreadReference t, String reason) {
        stoppedThread = t;
        handles.clear();
        setHold(true);
        JsonObject body = new JsonObject();
        body.addProperty("reason", reason);
        body.addProperty("threadId", (int) t.uniqueID());
        body.addProperty("allThreadsStopped", true);
        event("stopped", body);
    }

    private void setHold(boolean hold) {
        try {
            List<ReferenceType> types = vm.classesByName("org.pyftc.sim.Scheduler");
            if (types.isEmpty()) return;
            ClassType ct = (ClassType) types.get(0);
            Field f = ct.fieldByName("debuggerHold");
            ct.setValue(f, vm.mirrorOf(hold));
        } catch (Exception e) {
            System.err.println("could not " + (hold ? "freeze" : "unfreeze") + " sim time: " + e);
        }
    }

    private void resume() {
        ThreadReference t = stoppedThread;
        stoppedThread = null;
        handles.clear();
        setHold(false);
        if (t != null) {
            while (t.suspendCount() > 0) t.resume();
        }
    }

    private void step(int kind) throws IncompatibleThreadStateException {
        ThreadReference t = stoppedThread;
        if (t == null) return;
        EventRequestManager erm = vm.eventRequestManager();
        for (StepRequest r : new ArrayList<StepRequest>(erm.stepRequests())) erm.deleteEventRequest(r);
        StackFrame f = t.frame(0);
        stepStartLine = pyLine(f.location());
        stepStartDepth = t.frameCount();
        stepStartFile = sources.get(f.location().declaringType().name().split("\\$")[0]);
        stepKind = kind;
        StepRequest sr = erm.createStepRequest(t, StepRequest.STEP_LINE, kind);
        sr.addClassFilter(USER_PACKAGE + "*");
        sr.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        sr.enable();
        stoppedThread = null;
        handles.clear();
        setHold(false);
        while (t.suspendCount() > 0) t.resume();
    }

    // ------------------------------------------------------------------ inspection

    private JsonObject stackTrace() throws IncompatibleThreadStateException {
        JsonObject body = new JsonObject();
        JsonArray frames = new JsonArray();
        ThreadReference t = stoppedThread;
        if (t != null) {
            List<StackFrame> fs = t.frames();
            for (int i = 0; i < fs.size(); i++) {
                StackFrame f = fs.get(i);
                Location loc = f.location();
                String cls = loc.declaringType().name();
                String src = sources.get(cls.split("\\$")[0]);
                int py = pyLine(loc);
                if (src == null || py <= 0) continue;
                JsonObject o = new JsonObject();
                int id = handle(new Object[]{t, i});
                o.addProperty("id", id);
                String simple = cls.substring(cls.lastIndexOf('.') + 1).split("\\$")[0];
                o.addProperty("name", simple + "." + loc.method().name());
                JsonObject source = new JsonObject();
                source.addProperty("path", src);
                source.addProperty("name", Paths.get(src).getFileName().toString());
                o.add("source", source);
                o.addProperty("line", py);
                o.addProperty("column", 1);
                frames.add(o);
            }
        }
        body.add("stackFrames", frames);
        body.addProperty("totalFrames", frames.size());
        return body;
    }

    private int handle(Object o) {
        int h = nextHandle++;
        handles.put(h, o);
        return h;
    }

    private StackFrame frame(int id) throws IncompatibleThreadStateException {
        Object[] ref = (Object[]) handles.get(id);
        return ((ThreadReference) ref[0]).frame((Integer) ref[1]);
    }

    private JsonObject scopes(int frameId) throws IncompatibleThreadStateException {
        JsonArray scopes = new JsonArray();
        JsonObject locals = new JsonObject();
        locals.addProperty("name", "Locals");
        locals.addProperty("variablesReference", handle(new Object[]{"locals", frameId}));
        scopes.add(locals);
        StackFrame f = frame(frameId);
        ObjectReference self = f.thisObject();
        if (self != null) {
            JsonObject s = new JsonObject();
            s.addProperty("name", "self (OpMode fields)");
            s.addProperty("variablesReference", handle(self));
            scopes.add(s);
        }
        JsonObject body = new JsonObject();
        body.add("scopes", scopes);
        return body;
    }

    private JsonObject variables(int ref) throws Exception {
        JsonArray vars = new JsonArray();
        Object o = handles.get(ref);
        Map<String, Value> values = new LinkedHashMap<String, Value>();
        if (o instanceof Object[] && "locals".equals(((Object[]) o)[0])) {
            StackFrame f = frame((Integer) ((Object[]) o)[1]);
            try {
                for (LocalVariable v : f.visibleVariables()) values.put(v.name(), f.getValue(v));
            } catch (AbsentInformationException e) {
                values.put("(no local variable information)", null);
            }
        } else if (o instanceof ArrayReference) {
            List<Value> vs = ((ArrayReference) o).getValues();
            for (int i = 0; i < Math.min(vs.size(), 200); i++) values.put("[" + i + "]", vs.get(i));
        } else if (o instanceof ObjectReference) {
            ObjectReference obj = (ObjectReference) o;
            boolean user = obj.referenceType().name().startsWith(USER_PACKAGE);
            if (user || !isCollection(obj)) {
                for (Field f : obj.referenceType().allFields()) {
                    if (f.isSynthetic()) continue;
                    // For the OpMode itself show the fields the user declared, not the SDK base class internals.
                    if (user && !f.declaringType().name().startsWith(USER_PACKAGE)) continue;
                    values.put(f.name(), f.isStatic() ? f.declaringType().getValue(f) : obj.getValue(f));
                }
            } else {
                values.put("(contents)", obj);
            }
        }
        for (Map.Entry<String, Value> e : values.entrySet()) vars.add(variable(e.getKey(), e.getValue()));
        JsonObject body = new JsonObject();
        body.add("variables", vars);
        return body;
    }

    private static boolean isCollection(ObjectReference o) {
        String n = o.referenceType().name();
        return n.startsWith("java.util.");
    }

    private JsonObject variable(String name, Value v) {
        JsonObject o = new JsonObject();
        o.addProperty("name", name);
        o.addProperty("value", render(v));
        o.addProperty("type", v == null ? "None" : pythonType(v));
        int ref = 0;
        if (v instanceof ArrayReference || (v instanceof ObjectReference && !(v instanceof StringReference) && !boxed(v))) {
            ref = handle(v);
        }
        o.addProperty("variablesReference", ref);
        return o;
    }

    private static boolean boxed(Value v) {
        String n = v.type().name();
        return n.startsWith("java.lang.") && (n.endsWith("Integer") || n.endsWith("Double") || n.endsWith("Boolean")
                || n.endsWith("Long") || n.endsWith("Float") || n.endsWith("Short") || n.endsWith("Byte") || n.endsWith("Character"));
    }

    private static String pythonType(Value v) {
        String n = v.type().name();
        switch (n) {
            case "int": case "long": case "short": case "byte": case "java.lang.Integer": case "java.lang.Long": return "int";
            case "double": case "float": case "java.lang.Double": case "java.lang.Float": return "float";
            case "boolean": case "java.lang.Boolean": return "bool";
            case "java.lang.String": return "str";
            default: return n.substring(n.lastIndexOf('.') + 1);
        }
    }

    private String render(Value v) {
        if (v == null) return "None";
        if (v instanceof BooleanValue) return ((BooleanValue) v).value() ? "True" : "False";
        if (v instanceof CharValue) return "'" + ((CharValue) v).value() + "'";
        if (v instanceof PrimitiveValue) return v.toString();
        if (v instanceof StringReference) return gson.toJson(((StringReference) v).value());
        if (v instanceof ArrayReference) return "[" + ((ArrayReference) v).length() + " items]";
        ObjectReference o = (ObjectReference) v;
        if (boxed(v)) {
            Field f = o.referenceType().fieldByName("value");
            return f == null ? o.toString() : render(o.getValue(f));
        }
        String n = o.referenceType().name();
        return n.substring(n.lastIndexOf('.') + 1).replace('$', '.');
    }

    /** Watch/hover: a local, `self`, or a dotted path through fields (self.cycle_register, x.phase). */
    private JsonObject evaluate(JsonObject args) throws Exception {
        String expr = args.get("expression").getAsString().trim();
        JsonObject body = new JsonObject();
        if (!args.has("frameId") || stoppedThread == null) {
            body.addProperty("result", "(only while stopped)");
            body.addProperty("variablesReference", 0);
            return body;
        }
        StackFrame f = frame(args.get("frameId").getAsInt());
        String[] parts = expr.split("\\.");
        Value cur = null;
        boolean found = false;
        if ("self".equals(parts[0])) {
            cur = f.thisObject();
            found = true;
        } else {
            try {
                LocalVariable lv = f.visibleVariableByName(parts[0]);
                if (lv != null) {
                    cur = f.getValue(lv);
                    found = true;
                }
            } catch (AbsentInformationException ignored) {
            }
            if (!found && f.thisObject() != null) {
                Field fd = f.thisObject().referenceType().fieldByName(parts[0]);
                if (fd != null) {
                    cur = f.thisObject().getValue(fd);
                    found = true;
                }
            }
        }
        for (int i = 1; found && i < parts.length; i++) {
            if (!(cur instanceof ObjectReference)) {
                found = false;
                break;
            }
            Field fd = ((ObjectReference) cur).referenceType().fieldByName(parts[i]);
            if (fd == null) {
                found = false;
                break;
            }
            cur = ((ObjectReference) cur).getValue(fd);
        }
        if (!found) {
            body.addProperty("result", "(not a local or field: " + expr + ")");
            body.addProperty("variablesReference", 0);
            return body;
        }
        JsonObject v = variable(expr, cur);
        body.addProperty("result", v.get("value").getAsString());
        body.addProperty("variablesReference", v.get("variablesReference").getAsInt());
        return body;
    }
}
