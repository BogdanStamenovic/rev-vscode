package org.pyftc.sim;

/**
 * Deterministic lockstep clock shared by the scheduler (physics, inputs, output)
 * and the OpMode thread.
 *
 * Exactly one of the two runs at a time. The OpMode thread owns {@code userNs}:
 * every SDK call charges it a cost (a Lynx command costs what it costs on a
 * real hub, a plain SDK call a small CPU cost). When the OpMode thread's time
 * gets ahead of the physics time it parks and hands the turn to the scheduler,
 * which steps physics in fixed steps until it has caught up, then hands the
 * turn back. The result depends only on the sequence of calls, never on how
 * fast the host machine is, so headless runs are reproducible.
 *
 * If the OpMode thread does not come back within a wall-clock timeout (a busy
 * loop that makes no SDK calls at all) the scheduler stops waiting and keeps
 * stepping physics on its own ("free run"); the OpMode thread re-synchronises
 * at its next SDK call. That is the only non-deterministic path, and the
 * simulator reports it as a warning with the line the thread is spinning on.
 */
public final class SimClock {
    /** Arbitrary non-zero boot time, like Android's uptime base for System.nanoTime(). */
    public static final long BOOT_NS = 10_000_000_000L;

    static final Object LOCK = new Object();

    static volatile long physicsNs = BOOT_NS;
    private static long userNs = BOOT_NS;
    private static volatile Thread userThread;
    private static boolean userTurn;
    private static boolean userParked;
    private static boolean userSleeping;
    private static boolean wakeRequested;
    private static volatile boolean freeRun;
    private static volatile boolean killRequested;
    static volatile long lastSdkCallWallNs = System.nanoTime();

    /** Cost charged for any SDK call that does not talk to a hub. */
    static long callCostNs = 20_000L;

    private SimClock() {}

    /** Thrown inside the OpMode thread when the simulator has to get rid of it
     *  (the real Robot Controller restarts the whole app in that situation). */
    public static final class SimThreadDeath extends Error {
        SimThreadDeath() { super("OpMode thread stopped by the simulator"); }
    }

    public static boolean isUserThread() {
        return Thread.currentThread() == userThread;
    }

    public static long nanoTime() {
        if (Thread.currentThread() == userThread) {
            charge(callCostNs);
            synchronized (LOCK) { return userNs; }
        }
        return physicsNs;
    }

    /** Current time for the calling thread without charging anything (for the simulator's own reads). */
    public static long peekNs() {
        if (Thread.currentThread() == userThread) {
            synchronized (LOCK) { return userNs; }
        }
        return physicsNs;
    }

    /** Sim time as the scheduler sees it, in seconds since the process started. */
    public static double seconds() {
        return (physicsNs - BOOT_NS) / 1e9;
    }

    public static void yieldCall() {
        charge(callCostNs);
    }

    public static void charge(long ns) {
        if (Thread.currentThread() != userThread) return;
        lastSdkCallWallNs = System.nanoTime();
        synchronized (LOCK) {
            if (freeRun) {
                freeRun = false;
                userNs = Math.max(userNs, physicsNs) + ns;
                park(false);
                return;
            }
            userNs += ns;
            if (userNs > physicsNs) park(false);
        }
    }

    /** LinearOpMode.sleep(): Thread.sleep in the SDK; an interrupt (STOP) ends it early. */
    public static void sleepMs(long ms) {
        if (Thread.currentThread() != userThread) return;
        if (Thread.currentThread().isInterrupted()) return;
        lastSdkCallWallNs = System.nanoTime();
        synchronized (LOCK) {
            freeRun = false;
            userNs = Math.max(userNs, physicsNs) + Math.max(0, ms) * 1_000_000L;
            park(true);
        }
    }

    /** One event-loop tick of waiting (waitForStart). Returns false if interrupted. */
    public static boolean waitStep() {
        if (Thread.currentThread() != userThread) return !Thread.currentThread().isInterrupted();
        if (Thread.currentThread().isInterrupted()) return false;
        lastSdkCallWallNs = System.nanoTime();
        synchronized (LOCK) {
            freeRun = false;
            userNs = Math.max(userNs, physicsNs) + Scheduler.STEP_NS;
            park(true);
        }
        return !Thread.currentThread().isInterrupted();
    }

    public static void wakeUser() {
        synchronized (LOCK) {
            if (userSleeping) {
                userNs = Math.min(userNs, physicsNs);
                wakeRequested = true;
            }
        }
    }

    /**
     * Objects the scheduler thread also locks (TelemetryImpl's lock, for the event
     * loop's periodic telemetry flush). The OpMode thread can park in the middle of an
     * SDK method that holds one; the scheduler must then leave that object alone
     * until the next turn, or the two threads deadlock.
     */
    private static final java.util.List<Object> sharedLocks = new java.util.concurrent.CopyOnWriteArrayList<Object>();
    private static final java.util.Set<Object> heldWhileParked =
            java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<Object, Boolean>());

    static void registerSharedLock(Object lock) {
        if (lock != null && !sharedLocks.contains(lock)) sharedLocks.add(lock);
    }

    static void clearSharedLocks() {
        sharedLocks.clear();
    }

    /** True if the parked OpMode thread holds this lock (so the scheduler must not take it now). */
    static boolean userHolds(Object lock) {
        synchronized (LOCK) {
            return userParked && heldWhileParked.contains(lock);
        }
    }

    private static void park(boolean sleeping) {
        heldWhileParked.clear();
        for (Object l : sharedLocks) if (Thread.holdsLock(l)) heldWhileParked.add(l);
        userParked = true;
        userSleeping = sleeping;
        userTurn = false;
        LOCK.notifyAll();
        boolean interrupted = false;
        while (!userTurn) {
            try {
                LOCK.wait();
            } catch (InterruptedException e) {
                interrupted = true;
            }
        }
        userParked = false;
        userSleeping = false;
        if (interrupted) Thread.currentThread().interrupt();
        if (killRequested) throw new SimThreadDeath();
    }

    // ------------------------------------------------------------------ scheduler side

    static void registerUserThread(Thread t) {
        synchronized (LOCK) {
            userThread = t;
            userNs = physicsNs;
            userTurn = false;
            userParked = false;
            freeRun = false;
            killRequested = false;
            wakeRequested = false;
            lastSdkCallWallNs = System.nanoTime();
        }
    }

    /** First thing the OpMode thread does: wait for its first turn. */
    static void enterUser() {
        synchronized (LOCK) {
            userNs = physicsNs;
            park(false);
        }
    }

    static void userExited() {
        synchronized (LOCK) {
            if (Thread.currentThread() == userThread) {
                userThread = null;
                userTurn = false;
                userParked = false;
                freeRun = false;
                LOCK.notifyAll();
            }
        }
    }

    static Thread userThread() {
        return userThread;
    }

    static boolean isFreeRunning() {
        return freeRun;
    }

    static void advancePhysics(long ns) {
        physicsNs += ns;
    }

    /**
     * Hand the turn to the OpMode thread if it is due, and wait until it parks
     * again, exits, or the wall-clock timeout expires (then it is free-running).
     */
    static void runUser(long wallTimeoutNs) {
        synchronized (LOCK) {
            if (userThread == null || freeRun || !userParked) return;
            if (userNs > physicsNs && !wakeRequested) return;
            wakeRequested = false;
            userTurn = true;
            LOCK.notifyAll();
            long deadline = System.nanoTime() + wallTimeoutNs;
            while (userTurn && userThread != null) {
                long remaining = deadline - System.nanoTime();
                if (remaining <= 0) {
                    freeRun = true;
                    return;
                }
                try {
                    LOCK.wait(remaining / 1_000_000L, (int) (remaining % 1_000_000L));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    /** STOP: interrupt the OpMode thread; a sleeping thread wakes immediately, as Thread.sleep would. */
    static void interruptUser() {
        synchronized (LOCK) {
            Thread t = userThread;
            if (t == null) return;
            t.interrupt();
            if (userSleeping) {
                userNs = Math.min(userNs, physicsNs);
                wakeRequested = true;
            }
        }
    }

    /** Make the OpMode thread throw SimThreadDeath at its next SDK call. */
    static void requestKill() {
        synchronized (LOCK) {
            killRequested = true;
            if (userParked) {
                userTurn = true;
                LOCK.notifyAll();
            }
        }
    }

    /** User time in seconds, for event timestamps taken on the OpMode thread. */
    static double userSeconds() {
        synchronized (LOCK) {
            return (userNs - BOOT_NS) / 1e9;
        }
    }

    /** Timestamp for something happening on the current thread. */
    public static double eventSeconds() {
        return Thread.currentThread() == userThread ? userSeconds() : seconds();
    }
}
