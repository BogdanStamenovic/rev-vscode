/*
 * Simulator port of the FTC SDK 11.2.0 OpModeInternal (BSD-3-Clause, FIRST).
 * Same fields and lifecycle as the SDK; the executor thread, the OpMode
 * services and the "wait forever for the OpMode thread" loop are delegated to
 * org.pyftc.sim.OpModeHost, which runs the OpMode thread on the simulator's
 * deterministic clock.
 */
package com.qualcomm.robotcore.eventloop.opmode;

import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.util.RobotLog;

import org.firstinspires.ftc.robotcore.external.Telemetry;
import org.firstinspires.ftc.robotcore.internal.opmode.TelemetryImpl;
import org.firstinspires.ftc.robotcore.internal.opmode.TelemetryInternal;
import org.pyftc.sim.OpModeHost;

import java.util.concurrent.CancellationException;

abstract class OpModeInternal {
    public static final int MS_BEFORE_FORCE_STOP_AFTER_STOP_REQUESTED = 900;

    public volatile Gamepad gamepad1 = null;
    public volatile Gamepad gamepad2 = null;
    public Telemetry telemetry = new TelemetryImpl((OpMode) this);
    public volatile HardwareMap hardwareMap = null;

    @Deprecated public int msStuckDetectStop = MS_BEFORE_FORCE_STOP_AFTER_STOP_REQUESTED;

    volatile boolean isStarted = false;
    volatile boolean stopRequested = false;
    volatile boolean opModeThreadFinished = false;
    volatile RuntimeException exception = null;
    volatile NoClassDefFoundError noClassDefFoundError = null;
    volatile Throwable otherError = null;

    public final void requestOpModeStop() {
        OpModeHost.requestOpModeStop((OpMode) this);
    }

    abstract void internalRunOpMode() throws InterruptedException;
    void internalOnStart() { }
    void internalOnEventLoopIteration() { }
    void internalOnStopRequested() { }
    abstract void newGamepadDataAvailable(Gamepad latestGamepad1Data, Gamepad latestGamepad2Data);

    final void internalInit() {
        exception = null;
        noClassDefFoundError = null;
        otherError = null;
        isStarted = false;
        stopRequested = false;
        opModeThreadFinished = false;

        if (telemetry instanceof TelemetryInternal) {
            ((TelemetryInternal)telemetry).resetTelemetryForOpMode();
        }

        gamepad1.resetEdgeDetection();
        gamepad2.resetEdgeDetection();
        gamepad1.setTriggerThreshold(Gamepad.DEFAULT_TRIGGER_THRESHOLD);
        gamepad2.setTriggerThreshold(Gamepad.DEFAULT_TRIGGER_THRESHOLD);

        OpModeHost.startOpModeThread((OpMode) this, new Runnable() {
            @Override public void run() {
                try {
                    internalRunOpMode();
                } catch (InterruptedException ie) {
                    RobotLog.d("OpMode received an InterruptedException; shutting down");
                    requestOpModeStop();
                } catch (CancellationException ie) {
                    RobotLog.d("OpMode received a CancellationException; shutting down");
                    requestOpModeStop();
                } catch (RuntimeException e) {
                    exception = e;
                } catch (NoClassDefFoundError e) {
                    noClassDefFoundError = e;
                } catch (Error e) {
                    // The real RC lets any other Error kill the app; the simulator reports it instead.
                    otherError = e;
                } finally {
                    if (telemetry instanceof TelemetryInternal) {
                        telemetry.setMsTransmissionInterval(0);
                        ((TelemetryInternal) telemetry).tryUpdateIfDirty();
                    }
                    opModeThreadFinished = true;
                }
            }
        });
    }

    final void internalStart() {
        gamepad1.resetEdgeDetection();
        gamepad2.resetEdgeDetection();
        stopRequested = false;
        isStarted = true;
        internalOnStart();
    }

    final void internalThrowOpModeExceptionIfPresent() {
        if (exception != null) {
            throw exception;
        }
        if (noClassDefFoundError != null) {
            throw noClassDefFoundError;
        }
    }

    /** First half of the SDK's internalStop(): flag the stop and let the OpMode react.
     *  The SDK then busy-waits for the OpMode thread; the simulator host does that
     *  wait on sim time and applies the real stuck-OpMode rules. */
    final boolean internalBeginStop() {
        if (stopRequested) { return false; }
        stopRequested = true;
        internalOnStopRequested();
        return true;
    }
}
