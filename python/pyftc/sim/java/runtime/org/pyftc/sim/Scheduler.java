package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import org.pyftc.sim.hw.Robot;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * The simulator's main loop: apply due commands, run the event-loop duties
 * (OpModeHost.tick), step physics by one fixed step, give the OpMode thread its
 * turn, emit state. In realtime mode sim time is paced to the wall clock (times
 * the speed factor); in fast mode it runs as fast as the host allows. Neither
 * changes what the OpMode sees: that only depends on sim time.
 */
public final class Scheduler {
    public static final long STEP_NS = 1_000_000L;
    private static final long USER_WALL_TIMEOUT_NS = 250_000_000L;

    static final ConcurrentLinkedQueue<JsonObject> incoming = new ConcurrentLinkedQueue<JsonObject>();
    private static final List<JsonObject> scheduled = new ArrayList<JsonObject>();

    static boolean realtime = true;
    static double speed = 1.0;
    static volatile boolean paused = false;
    /** Set through JDI by the debug bridge while the OpMode thread is stopped at a breakpoint. */
    public static volatile boolean debuggerHold = false;
    static volatile boolean quit = false;
    static double emitEverySimMs = 33;
    static double untilSec = Double.NaN;
    private static volatile boolean stateSoon;

    private static long lastEmitWallNs;
    private static long lastEmitSimNs;
    private static long lastEmitIteration;
    private static long wallBase;
    private static long simBase;
    private static boolean freeRunWarned;

    private Scheduler() {}

    static void requestStateSoon() {
        stateSoon = true;
    }

    static void run() {
        wallBase = System.nanoTime();
        simBase = SimClock.physicsNs;
        while (!quit) {
            drainCommands();
            if (quit) break;
            if (paused || debuggerHold) {
                // Time stopped at a breakpoint is not an OpMode spinning without SDK calls.
                SimClock.lastSdkCallWallNs = System.nanoTime();
                emitIfDue(true);
                sleepQuietly(5);
                wallBase = System.nanoTime();
                simBase = SimClock.physicsNs;
                continue;
            }
            OpModeHost.tick();
            Robot.get().step(STEP_NS / 1e9);
            SimClock.advancePhysics(STEP_NS);
            SimClock.runUser(USER_WALL_TIMEOUT_NS);
            watchFreeRun();
            emitIfDue(false);
            if (!Double.isNaN(untilSec) && SimClock.seconds() >= untilSec) {
                emitState();
                break;
            }
            pace();
        }
    }

    private static void pace() {
        if (!realtime) return;
        long simElapsed = SimClock.physicsNs - simBase;
        long wallTarget = wallBase + (long) (simElapsed / speed);
        long now = System.nanoTime();
        long ahead = wallTarget - now;
        if (ahead > 2_000_000L) {
            sleepQuietly(ahead / 1_000_000L);
        } else if (ahead < -200_000_000L) {
            // Host cannot keep up (or was suspended): do not try to catch up in a burst.
            wallBase = now;
            simBase = SimClock.physicsNs;
        }
    }

    private static void watchFreeRun() {
        if (!SimClock.isFreeRunning()) {
            freeRunWarned = false;
            return;
        }
        long idleMs = (System.nanoTime() - SimClock.lastSdkCallWallNs) / 1_000_000L;
        if (idleMs > 1000 && !freeRunWarned) {
            freeRunWarned = true;
            Thread t = SimClock.userThread();
            Locator.PyLoc where = t == null ? null : Locator.userFrame(t.getStackTrace());
            OpModeHost.warning("no-sdk-calls", null,
                    "The OpMode has been running for more than a second without calling anything on the robot (no hardware access, no opModeIsActive(), no sleep): it is stuck in a busy loop"
                            + (where != null ? " at " + where.shortName() : "")
                            + ". On the robot this freezes the OpMode the same way.", where, null);
        }
    }

    private static void drainCommands() {
        JsonObject c;
        while ((c = incoming.poll()) != null) {
            if (c.has("at") && !c.get("at").isJsonNull()) {
                scheduled.add(c);
                Collections.sort(scheduled, new Comparator<JsonObject>() {
                    @Override public int compare(JsonObject a, JsonObject b) {
                        return Double.compare(a.get("at").getAsDouble(), b.get("at").getAsDouble());
                    }
                });
            } else {
                Commands.apply(c);
            }
        }
        double now = SimClock.seconds();
        while (!scheduled.isEmpty() && scheduled.get(0).get("at").getAsDouble() <= now + 1e-9) {
            Commands.apply(scheduled.remove(0));
        }
    }

    private static void emitIfDue(boolean held) {
        long now = System.nanoTime();
        boolean due;
        if (realtime || held) {
            due = now - lastEmitWallNs >= 33_000_000L;
        } else {
            due = (SimClock.physicsNs - lastEmitSimNs) >= (long) (emitEverySimMs * 1e6);
        }
        if (stateSoon) {
            due = true;
            stateSoon = false;
        }
        if (due) {
            lastEmitWallNs = now;
            emitState();
        }
    }

    static void emitState() {
        long iter = OpModeHost.iteration();
        long dSim = SimClock.physicsNs - lastEmitSimNs;
        long dIter = iter - lastEmitIteration;
        lastEmitSimNs = SimClock.physicsNs;
        lastEmitIteration = iter;
        JsonObject o = new JsonObject();
        o.addProperty("type", "state");
        o.addProperty("t", SimClock.seconds());
        o.addProperty("phase", OpModeHost.phase().name());
        if (OpModeHost.opModeName() != null) o.addProperty("opMode", OpModeHost.opModeName());
        if (dIter > 0) o.addProperty("loopMs", dSim / 1e6 / dIter);
        o.addProperty("paused", paused);
        o.addProperty("debuggerHold", debuggerHold);
        o.add("devices", Robot.get().stateJson());
        JsonArray gp = new JsonArray();
        gp.add(Inputs.gamepadState(1));
        gp.add(Inputs.gamepadState(2));
        o.add("gamepads", gp);
        JsonArray ev = new JsonArray();
        for (JsonObject e : OpModeHost.drainEvents()) ev.add(e);
        o.add("events", ev);
        Out.send(o);
        JsonObject trace = Trace.snapshotJson();
        trace.add("fields", FieldWatch.snapshot());
        Out.send(trace);
    }

    static void restartIfStillAlive(final Thread t) {
        // A free-running thread makes no SDK calls, so the kill request can never reach it.
        final long waitMs = SimClock.isFreeRunning() ? 0 : 2000;
        Thread watcher = new Thread(new Runnable() {
            @Override public void run() {
                try {
                    if (waitMs > 0) t.join(waitMs);
                } catch (InterruptedException ignored) {
                }
                if (t.isAlive()) {
                    JsonObject o = new JsonObject();
                    o.addProperty("type", "fatal");
                    o.addProperty("restart", true);
                    o.addProperty("message", "The OpMode thread could not be stopped (it is spinning without making any SDK call). The real Robot Controller restarts its app in this situation; the simulator restarts too.");
                    Out.send(o);
                    Out.close();
                    Runtime.getRuntime().halt(3);
                }
            }
        }, "restart-watcher");
        watcher.setDaemon(true);
        watcher.start();
    }

    private static void sleepQuietly(long ms) {
        if (ms <= 0) return;
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
