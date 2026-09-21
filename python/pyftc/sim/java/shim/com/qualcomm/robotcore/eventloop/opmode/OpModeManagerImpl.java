/*
 * Simulator stand-in for the FTC SDK 11.2.0 OpModeManagerImpl (BSD-3-Clause, FIRST).
 * Only the members that real SDK classes used by the simulator reference:
 * ForceStopException (thrown by terminateOpModeNow() and by hardware access
 * after the stop timeout) and updateTelemetryNow() (called by TelemetryImpl).
 * The manager's real work (OpMode lifecycle, stuck detection) is done by
 * org.pyftc.sim.OpModeHost following the SDK's rules.
 */
package com.qualcomm.robotcore.eventloop.opmode;

import com.qualcomm.robotcore.robocol.TelemetryMessage;

public class OpModeManagerImpl {
  public static final String DEFAULT_OP_MODE_NAME = "$Stop$Robot$";

  public static class ForceStopException extends RuntimeException {}

  public static void updateTelemetryNow(OpMode opMode, TelemetryMessage telemetry) {
    opMode.internalUpdateTelemetryNow(telemetry);
  }
}
