/*
 * Simulator port of the FTC SDK 11.2.0 ElapsedTime (BSD-3-Clause, Qualcomm / FIRST).
 * Identical to the SDK source except nsNow(), which reads the simulator's
 * deterministic clock instead of System.nanoTime(): user code timing must follow
 * sim time, not the host's wall clock.
 */
package com.qualcomm.robotcore.util;

import org.pyftc.sim.SimClock;

import java.util.concurrent.TimeUnit;

@SuppressWarnings("WeakerAccess")
public class ElapsedTime {

  public enum Resolution {
    SECONDS,
    MILLISECONDS
  }

  public static final long SECOND_IN_NANO = 1000000000;

  public static final long MILLIS_IN_NANO = 1000000;

  protected volatile long nsStartTime;
  protected final double resolution;

  public ElapsedTime() {
    reset();
    this.resolution = SECOND_IN_NANO;
  }

  public ElapsedTime(long startTime) {
    this.nsStartTime = startTime;
    this.resolution = SECOND_IN_NANO;
  }

  public ElapsedTime(Resolution resolution) {
    reset();
    switch (resolution) {
      case SECONDS:
      default:
        this.resolution = SECOND_IN_NANO;
        break;
      case MILLISECONDS:
        this.resolution = MILLIS_IN_NANO;
        break;
    }
  }

  protected long nsNow() {
    return SimClock.nanoTime();
  }

  public long now(TimeUnit unit) {
    return unit.convert(nsNow(), TimeUnit.NANOSECONDS);
  }

  public void reset() {
    nsStartTime = nsNow();
  }

  public double startTime() {
    return nsStartTime / resolution;
  }

  public long startTimeNanoseconds() {
    return this.nsStartTime;
  }

  public double time() {
    return (nsNow() - nsStartTime) / resolution;
  }

  public long time(TimeUnit unit) {
    return unit.convert(nanoseconds(), TimeUnit.NANOSECONDS);
  }

  public double seconds() {
    return nanoseconds() / ((double)(SECOND_IN_NANO));
  }

  public double milliseconds() {
    return seconds() * 1000;
  }

  public long nanoseconds() {
    return (nsNow() - nsStartTime);
  }

  public Resolution getResolution() {
    if (this.resolution == MILLIS_IN_NANO)
      return Resolution.MILLISECONDS;
    else
      return Resolution.SECONDS;
  }

  private String resolutionStr() {
    if (resolution == SECOND_IN_NANO) {
      return "seconds";
    } else if (resolution == MILLIS_IN_NANO) {
      return "milliseconds";
    } else {
      return "unknown units";
    }
  }

  public void log(String label) {
    RobotLog.v(String.format("TIMER: %20s - %1.3f %s", label, time(), resolutionStr()));
  }

  @Override
  public String toString() {
    return String.format("%1.4f %s", time(), resolutionStr());
  }
}
