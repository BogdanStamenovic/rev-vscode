/*
 * Simulator port of the FTC SDK 11.2.0 LinearOpMode (BSD-3-Clause, FIRST).
 * Identical public API and semantics; waiting, sleeping and yielding run on the
 * simulator's deterministic clock instead of Object.wait / Thread.sleep.
 */
package com.qualcomm.robotcore.eventloop.opmode;

import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.util.RobotLog;

import org.firstinspires.ftc.robotcore.internal.opmode.TelemetryInternal;
import org.pyftc.sim.OpModeHost;
import org.pyftc.sim.SimClock;

@SuppressWarnings("unused")
public abstract class LinearOpMode extends OpMode {

  private volatile boolean  userMethodReturned = false;
  private volatile boolean  userMonitoredForStart = false;

  public LinearOpMode() {
  }

  abstract public void runOpMode() throws InterruptedException;

  public void waitForStart() {
    OpModeHost.markWaitForStart();
    while (!isStarted()) {
      // The SDK waits on a monitor the event loop notifies every iteration; here the
      // thread parks until the next simulator step. An interrupt ends the wait.
      if (!SimClock.waitStep()) {
        Thread.currentThread().interrupt();
        return;
      }
    }
  }

  public final void idle() {
    SimClock.yieldCall();
  }

  public final void sleep(long milliseconds) {
    SimClock.sleepMs(milliseconds);
  }

  public final boolean opModeIsActive() {
    OpModeHost.loopBoundary();
    boolean isActive = !this.isStopRequested() && this.isStarted();
    if (isActive) {
      idle();
    }
    return isActive;
  }

  public final boolean opModeInInit() {
    SimClock.yieldCall();
    return !isStarted() && !isStopRequested();
  }

  public final boolean isStarted() {
    SimClock.yieldCall();
    if(isStarted) userMonitoredForStart = true;
    return this.isStarted || Thread.currentThread().isInterrupted();
  }

  public final boolean isStopRequested() {
    SimClock.yieldCall();
    return this.stopRequested || Thread.currentThread().isInterrupted();
  }

  @Override final public void init() { }
  @Override final public void init_loop() { }
  @Override final public void start() { }
  @Override final public void loop() { }
  @Override final public void stop() { }

  @Override
  final void internalRunOpMode() throws InterruptedException {
    userMethodReturned = false;
    userMonitoredForStart = false;

    runOpMode();
    userMethodReturned = true;
    RobotLog.d("User runOpModeMethod exited");
    requestOpModeStop();
  }

  @Override
  final void internalOnStart() {
    SimClock.wakeUser();
  }

  @Override
  final void internalOnEventLoopIteration() {
    time = getRuntime();
    if (telemetry instanceof TelemetryInternal) {
      ((TelemetryInternal)telemetry).tryUpdateIfDirty();
    }
  }

  @Override
  final void internalOnStopRequested() {
    if(!userMonitoredForStart && userMethodReturned) {
      RobotLog.addGlobalWarningMessage("The OpMode which was just initialized ended prematurely as a result of not monitoring for the start condition. Did you forget to call waitForStart()?");
      OpModeHost.returnedEarly();
    }
    OpModeHost.interruptOpModeThread();
  }

  @Override
  void newGamepadDataAvailable(Gamepad latestGamepad1Data, Gamepad latestGamepad2Data) {
    gamepad1.copy(latestGamepad1Data);
    gamepad2.copy(latestGamepad2Data);
  }
}
