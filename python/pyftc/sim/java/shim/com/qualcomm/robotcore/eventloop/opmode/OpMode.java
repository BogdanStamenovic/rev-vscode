/*
 * Simulator port of the FTC SDK 11.2.0 OpMode (BSD-3-Clause, Qualcomm / FIRST).
 * Identical public API; System.nanoTime() and Thread.sleep() are replaced by the
 * simulator clock so runtime and loop pacing follow sim time.
 */
package com.qualcomm.robotcore.eventloop.opmode;

import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.robocol.TelemetryMessage;

import org.firstinspires.ftc.robotcore.external.Telemetry;
import org.pyftc.sim.OpModeHost;
import org.pyftc.sim.SimClock;

import java.util.HashMap;
import java.util.concurrent.TimeUnit;

public abstract class OpMode extends OpModeInternal {

  public final static HashMap<String, Object> blackboard = new HashMap<>();

  public volatile double time = 0.0;

  private volatile long startTime = 0;

  private volatile Gamepad latestGamepad1Data = new Gamepad();
  private volatile Gamepad latestGamepad2Data = new Gamepad();

  public OpMode() {
    startTime = SimClock.nanoTime();
  }

  abstract public void init();

  public void init_loop() {};

  public void start() {};

  abstract public void loop();

  public void stop() {};

  public final void terminateOpModeNow() {
    throw new OpModeManagerImpl.ForceStopException();
  }

  public double getRuntime() {
    final double NANOSECONDS_PER_SECOND = TimeUnit.SECONDS.toNanos(1);
    return (SimClock.nanoTime() - startTime) / NANOSECONDS_PER_SECOND;
  }

  public void resetRuntime() {
    startTime = SimClock.nanoTime();
  }

  public void updateTelemetry(Telemetry telemetry) {
    telemetry.update();
  }

  @Deprecated public int msStuckDetectInit     = 5000;
  @Deprecated public int msStuckDetectInitLoop = 5000;
  @Deprecated public int msStuckDetectStart    = 5000;
  @Deprecated public int msStuckDetectLoop     = 5000;

  @Override
  void internalRunOpMode() throws InterruptedException {
    internalPreInit();
    init();

    while (!isStarted && !stopRequested) {
      internalPreUserCode();
      init_loop();
      internalPostUserCode();
      internalPostInitLoop();
      SimClock.sleepMs(1);
    }

    if (isStarted) {
      internalPreUserCode();
      start();
      internalPostUserCode();

      while (!stopRequested) {
        OpModeHost.loopBoundary();
        internalPreUserCode();
        loop();
        internalPostUserCode();
        internalPostLoop();
        SimClock.sleepMs(1);
      }
    }

    internalPreUserCode();
    stop();
    internalPostUserCode();
  }

  @Override
  void newGamepadDataAvailable(Gamepad latestGamepad1Data, Gamepad latestGamepad2Data) {
    this.latestGamepad1Data = latestGamepad1Data;
    this.latestGamepad2Data = latestGamepad2Data;
  }

  public final void internalUpdateTelemetryNow(TelemetryMessage telemetry) {
    OpModeHost.telemetry(this, telemetry);
  }

  private void internalPreUserCode() {
    time = getRuntime();
    gamepad1.copy(latestGamepad1Data);
    gamepad2.copy(latestGamepad2Data);
  }

  private void internalPostUserCode() {
    telemetry.update();
  }

  @Deprecated public void internalPreInit() { }
  @Deprecated public void internalPostInitLoop() { }
  @Deprecated public void internalPostLoop() { }
}
