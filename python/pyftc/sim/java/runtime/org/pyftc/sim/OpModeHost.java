package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.OpModeManagerImpl;
import com.qualcomm.robotcore.eventloop.opmode.SimOpModeAccess;
import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.robocol.TelemetryMessage;

import org.pyftc.sim.hw.Robot;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Does for the simulator what the Robot Controller's OpModeManagerImpl does on
 * the hub: constructs the OpMode at INIT, runs it on its own thread, starts and
 * stops it, notices exceptions, and applies the SDK's stop rules: the OpMode
 * thread is interrupted at STOP; if it has not finished after
 * MS_BEFORE_FORCE_STOP_AFTER_STOP_REQUESTED (900 ms) hardware access throws
 * ForceStopException; if it still has not finished 100 ms later the real app
 * restarts ("OpMode '%s' stuck in stop(). Restarting robot controller app.").
 * After an OpMode ends, the SDK's DefaultOpMode sets every motor to 0 and the
 * hub failsafe cuts all outputs 100 ms later.
 */
public final class OpModeHost {
    public enum Phase { idle, init, running, stopping, stopped, crashed }

    private static volatile Phase phase = Phase.idle;
    private static volatile OpMode opMode;
    private static volatile String opModeName;
    private static volatile Thread opModeThread;
    private static volatile boolean stopPending;
    private static volatile boolean forceStopArmed;
    private static long stopStartNs;
    private static long failsafeAtNs = -1;
    private static boolean forceStopReported;
    private static boolean exceptionReported;
    private static volatile boolean waitForStartCalled;
    private static volatile long iteration;

    private static final Object EVENTS = new Object();
    private static List<JsonObject> events = new ArrayList<JsonObject>();
    private static final Set<String> warned = new HashSet<String>();

    // double-write detection: per device, the last write in the current loop iteration
    private static final Map<String, Object[]> writesThisIteration = new java.util.HashMap<String, Object[]>();

    private static volatile Object telemetryLock;

    private OpModeHost() {}

    private static Object telemetryLockOf(OpMode m) {
        try {
            java.lang.reflect.Field f = m.telemetry.getClass().getDeclaredField("theLock");
            f.setAccessible(true);
            return f.get(m.telemetry);
        } catch (ReflectiveOperationException | RuntimeException e) {
            return null;
        }
    }

    public static Phase phase() {
        return phase;
    }

    public static String opModeName() {
        return opModeName;
    }

    public static OpMode opMode() {
        return opMode;
    }

    public static long iteration() {
        return iteration;
    }

    // ---------------------------------------------------------------- lifecycle (scheduler thread)

    static void init(String name) {
        if (phase == Phase.init || phase == Phase.running || phase == Phase.stopping) {
            SimLog.warn("sim", "INIT ignored: an OpMode is already active; press STOP first", null);
            return;
        }
        Registry.Entry entry = Registry.find(name);
        if (entry == null) {
            SimLog.error("sim", "No OpMode named '" + name + "'", null);
            return;
        }
        Robot.get().prepareForOpMode();
        opModeName = entry.name;
        exceptionReported = false;
        forceStopReported = false;
        forceStopArmed = false;
        stopPending = false;
        waitForStartCalled = false;
        failsafeAtNs = -1;
        synchronized (warned) { warned.clear(); }
        synchronized (writesThisIteration) { writesThisIteration.clear(); }
        Trace.reset();
        forgetCommands();
        iteration = 0;
        setPhase(Phase.init);
        OpMode instance;
        try {
            instance = (OpMode) entry.clazz.getDeclaredConstructor().newInstance();
        } catch (java.lang.reflect.InvocationTargetException e) {
            reportException(e.getCause() != null ? e.getCause() : e, "init");
            setPhase(Phase.crashed);
            return;
        } catch (Throwable e) {
            reportException(e, "init");
            setPhase(Phase.crashed);
            return;
        }
        instance.hardwareMap = Robot.get().hardwareMap();
        instance.gamepad1 = new Gamepad();
        instance.gamepad2 = new Gamepad();
        telemetryLock = telemetryLockOf(instance);
        SimClock.clearSharedLocks();
        SimClock.registerSharedLock(telemetryLock);
        opMode = instance;
        Inputs.pushGamepads();
        SimOpModeAccess.init(instance);
    }

    static void start() {
        if (phase != Phase.init || opMode == null) {
            SimLog.warn("sim", "START ignored: INIT an OpMode first", null);
            return;
        }
        setPhase(Phase.running);
        Inputs.pushGamepads();
        SimOpModeAccess.start(opMode);
        SimClock.wakeUser();
    }

    static void stop() {
        if (opMode == null || (phase != Phase.init && phase != Phase.running)) return;
        stopPending = false;
        stopStartNs = SimClock.physicsNs;
        setPhase(Phase.stopping);
        SimOpModeAccess.beginStop(opMode);
    }

    /** Called by the scheduler once per physics step. */
    static void tick() {
        OpMode m = opMode;
        if (m != null) {
            if ((phase == Phase.running || phase == Phase.init) && !SimClock.userHolds(telemetryLock)) {
                SimOpModeAccess.eventLoopIteration(m);
            }
            if (stopPending && (phase == Phase.init || phase == Phase.running)) {
                stop();
            }
            if ((phase == Phase.init || phase == Phase.running) && SimOpModeAccess.threadFinished(m) && opModeThread == null) {
                // The OpMode thread ended on its own: exception, or runOpMode returned.
                if (!checkException(m)) {
                    stop();
                } else {
                    finishStop(Phase.crashed);
                }
            }
            if (phase == Phase.stopping) {
                if (SimOpModeAccess.threadFinished(m) && opModeThread == null) {
                    boolean crashed = checkException(m);
                    if (forceStopArmed && !forceStopReported) {
                        forceStopReported = true;
                        warning("stuck-stop", null, "User OpMode was stuck in stop(), but was able to be force stopped without restarting the app. It appears this was a linear OpMode; make sure you are calling opModeIsActive() in any loops.", Locator.userFrame(lastUserStack()), null);
                    }
                    forceStopArmed = false;
                    finishStop(crashed ? Phase.crashed : Phase.stopped);
                } else {
                    long elapsedMs = (SimClock.physicsNs - stopStartNs) / 1_000_000L;
                    if (!forceStopArmed && elapsedMs >= SimOpModeAccess.FORCE_STOP_MS) {
                        forceStopArmed = true;
                        captureUserStack();
                    }
                    if (forceStopArmed && elapsedMs >= SimOpModeAccess.FORCE_STOP_MS + 100) {
                        stuckRestart();
                    }
                }
            }
        }
        if (failsafeAtNs >= 0 && SimClock.physicsNs >= failsafeAtNs) {
            failsafeAtNs = -1;
            Robot.get().failsafe();
            forgetCommands();
            recordEvent("robot", "failsafe", "all motors and servos off", null);
        }
    }

    private static void finishStop(Phase end) {
        Robot.get().stopRobot();
        failsafeAtNs = SimClock.physicsNs + (long) (Constants.num("lynx.failsafeDelayMs") * 1e6);
        setPhase(end);
    }

    private static void stuckRestart() {
        StackTraceElement[] stack = lastUserStack();
        Locator.PyLoc where = Locator.userFrame(stack);
        String message = String.format("OpMode '%s' stuck in %s. Restarting robot controller app.", opModeName, "stop()");
        warning("stuck-stop", null, message + " The loop never checks opModeIsActive() (or it ignores it)"
                + (where != null ? ", it was running " + where.shortName() : "") + ".", where, null);
        SimClock.requestKill();
        forceStopArmed = false;
        Robot.get().stopRobot();
        Robot.get().failsafe();
        setPhase(Phase.crashed);
        Thread t = opModeThread;
        if (t != null) {
            // A thread that makes no SDK calls cannot be stopped from inside; the real
            // Robot Controller restarts the whole app, and so does the simulator process.
            Scheduler.restartIfStillAlive(t);
        }
    }

    private static StackTraceElement[] savedStack = new StackTraceElement[0];

    private static void captureUserStack() {
        Thread t = opModeThread;
        if (t != null) savedStack = t.getStackTrace();
    }

    private static StackTraceElement[] lastUserStack() {
        Thread t = opModeThread;
        if (t != null) {
            StackTraceElement[] s = t.getStackTrace();
            if (s.length > 0) return s;
        }
        return savedStack;
    }

    private static boolean checkException(OpMode m) {
        Throwable e = SimOpModeAccess.exception(m);
        if (e == null) e = SimOpModeAccess.error(m);
        if (e == null) return false;
        SimOpModeAccess.clearException(m);
        if (e instanceof OpModeManagerImpl.ForceStopException) {
            // terminateOpModeNow() or the stop timeout: the RC stops quietly.
            return false;
        }
        if (!exceptionReported) {
            exceptionReported = true;
            reportException(e, phase.name());
        }
        return true;
    }

    private static void setPhase(Phase p) {
        phase = p;
        JsonObject v = new JsonObject();
        recordEvent("opmode", "phase", p.name(), null);
        Scheduler.requestStateSoon();
    }

    // ---------------------------------------------------------------- called from shims

    public static void startOpModeThread(final OpMode m, final Runnable body) {
        Thread t = new Thread(new Runnable() {
            @Override public void run() {
                try {
                    SimClock.enterUser();
                    body.run();
                } catch (SimClock.SimThreadDeath ignored) {
                    // killed after the stop timeout; already reported
                } finally {
                    opModeThread = null;
                    SimClock.userExited();
                }
            }
        }, "OpModeThread");
        t.setDaemon(true);
        opModeThread = t;
        SimClock.registerUserThread(t);
        t.start();
    }

    public static void requestOpModeStop(OpMode m) {
        if (m == opMode) stopPending = true;
    }

    public static void interruptOpModeThread() {
        SimClock.interruptUser();
    }

    public static void checkForceStop() {
        if (forceStopArmed && SimClock.isUserThread()) {
            throw new OpModeManagerImpl.ForceStopException();
        }
    }

    public static void markWaitForStart() {
        waitForStartCalled = true;
    }

    public static void returnedEarly() {
        warning("returned-early", null, "The OpMode which was just initialized ended prematurely as a result of not monitoring for the start condition. Did you forget to call waitForStart()?", null, null);
    }

    public static void telemetry(OpMode m, TelemetryMessage msg) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "telemetry");
        o.addProperty("t", SimClock.eventSeconds());
        JsonArray lines = new JsonArray();
        for (Map.Entry<String, String> e : msg.getDataStrings().entrySet()) {
            lines.add(e.getValue());
        }
        o.add("lines", lines);
        Out.send(o);
    }

    /** LinearOpMode.opModeIsActive() / iterative loop(): one loop iteration ends here. */
    public static void loopBoundary() {
        iteration++;
        synchronized (writesThisIteration) { writesThisIteration.clear(); }
        Trace.boundary();
    }

    public static void notSimulated(String what, String detail) {
        warning("not-simulated", what, what + ": " + detail, Locator.here(), null);
    }

    /** Every setPower/setPosition call, before the SDK's cache decides whether to send it. */
    public static void noteWrite(String device, String op, double value) {
        if (device == null || !SimClock.isUserThread()) return;
        String key = device + "." + op;
        Object[] prev;
        synchronized (writesThisIteration) {
            prev = writesThisIteration.get(key);
        }
        if (prev != null && ((Double) prev[0]) != value) {
            Locator.PyLoc here = Locator.here();
            Locator.PyLoc first = (Locator.PyLoc) prev[1];
            String dedupe = "double-write:" + key + ":" + (first == null ? "?" : first.line) + ":" + (here == null ? "?" : here.line);
            boolean fresh;
            synchronized (warned) { fresh = warned.add(dedupe); }
            if (fresh) {
                double lastedMs = (SimClock.eventSeconds() - (Double) prev[2]) * 1000.0;
                String msg = String.format("%s.%s() was called twice in one loop iteration with different values: %s at %s, then %s at %s. Only the last value stays; the first one is on the device for about %.1f ms of each loop.",
                        device, op, fmt((Double) prev[0]), first == null ? "?" : first.shortName(), fmt(value), here == null ? "?" : here.shortName(), lastedMs);
                warning("double-write", device, msg, here, first);
            }
        }
        Locator.PyLoc loc = prev == null ? Locator.here() : null;
        synchronized (writesThisIteration) {
            if (prev == null) {
                writesThisIteration.put(key, new Object[]{value, loc, SimClock.eventSeconds()});
            } else {
                prev[0] = value;
                prev[1] = Locator.here();
                prev[2] = SimClock.eventSeconds();
            }
        }
    }

    private static String fmt(double v) {
        return String.format("%.2f", v);
    }

    // Last value per device command: the SDK re-sends unchanged commands (its 500 ms
    // LastKnown caches expire), which costs bus time but is not news for the event list.
    private static final Map<String, Object> lastCommand = new java.util.HashMap<String, Object>();

    private static boolean changed(String device, String op, Object value) {
        synchronized (lastCommand) {
            Object prev = lastCommand.put(device + "." + op, value);
            return prev == null || !prev.equals(value);
        }
    }

    public static void recordCommand(String device, String op, Object value) {
        if (!changed(device, op, value)) return;
        recordEvent(device, op, value, SimClock.isUserThread() ? Locator.here() : null);
    }

    /** A command whose hub-side value differs from the value in the code (motor direction). */
    public static void recordCommand(String device, String op, Object value, double hubValue) {
        if (!changed(device, op, value + "/" + hubValue)) return;
        JsonObject e = recordEvent(device, op, value, SimClock.isUserThread() ? Locator.here() : null);
        e.addProperty("hub", hubValue);
    }

    static void forgetCommands() {
        synchronized (lastCommand) {
            lastCommand.clear();
        }
    }

    static JsonObject recordEvent(String device, String op, Object value, Locator.PyLoc where) {
        JsonObject e = new JsonObject();
        e.addProperty("t", SimClock.eventSeconds());
        e.addProperty("dev", device);
        e.addProperty("op", op);
        if (value instanceof Number) e.addProperty("v", (Number) value);
        else if (value instanceof Boolean) e.addProperty("v", (Boolean) value);
        else if (value instanceof JsonObject) e.add("v", (JsonObject) value);
        else if (value != null) e.addProperty("v", value.toString());
        if (where != null) e.add("py", where.json());
        synchronized (EVENTS) {
            events.add(e);
            if (events.size() > 2000) events.remove(0);
        }
        return e;
    }

    static List<JsonObject> drainEvents() {
        synchronized (EVENTS) {
            List<JsonObject> out = events;
            events = new ArrayList<JsonObject>();
            return out;
        }
    }

    static void warning(String code, String device, String message, Locator.PyLoc where, Locator.PyLoc related) {
        String key = code + ":" + (device == null ? "" : device) + ":" + message;
        if (!"double-write".equals(code)) {
            synchronized (warned) {
                if (!warned.add(key)) return;
            }
        }
        JsonObject o = new JsonObject();
        o.addProperty("type", "warning");
        o.addProperty("t", SimClock.eventSeconds());
        o.addProperty("code", code);
        if (device != null) o.addProperty("device", device);
        o.addProperty("message", message);
        if (where != null) o.add("py", where.json());
        if (related != null) {
            JsonArray r = new JsonArray();
            r.add(related.json());
            o.add("related", r);
        }
        Out.send(o);
    }

    static void reportException(Throwable e, String phaseName) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "exception");
        o.addProperty("t", SimClock.eventSeconds());
        o.addProperty("phase", phaseName);
        o.addProperty("exception", e.getClass().getName());
        o.addProperty("message", e.getMessage() == null ? "" : e.getMessage());
        StackTraceElement[] stack = e.getStackTrace();
        Locator.PyLoc top = Locator.userFrame(stack);
        if (top != null) o.add("py", top.json());
        JsonArray frames = new JsonArray();
        StringBuilder ds = new StringBuilder(e.toString());
        int shown = 1;
        for (StackTraceElement f : stack) {
            JsonObject fr = new JsonObject();
            fr.addProperty("class", f.getClassName());
            fr.addProperty("method", f.getMethodName());
            fr.addProperty("javaLine", f.getLineNumber());
            Locator.PyLoc p = Locator.isUserClass(f.getClassName()) ? Locator.map(f) : null;
            if (p != null) fr.add("py", p.json());
            frames.add(fr);
            if (shown < 15) {
                ds.append("\n\tat ").append(f.toString());
                shown++;
            }
        }
        o.add("frames", frames);
        // What the Driver Hub shows: Log.getStackTraceString(e), first 15 lines (OpModeManagerImpl.handleSendStacktrace).
        o.addProperty("driverHub", ds.toString());
        o.addProperty("hint", ExceptionHints.hint(e));
        Out.send(o);
        recordEvent("opmode", "exception", e.getClass().getSimpleName(), top);
    }
}
