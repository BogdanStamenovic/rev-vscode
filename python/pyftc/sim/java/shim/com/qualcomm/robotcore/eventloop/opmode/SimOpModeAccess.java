/*
 * Simulator-only bridge (not part of the SDK and not visible to user code: it is
 * left out of the compile-time API jar). Gives the simulator host access to the
 * package-private OpMode lifecycle methods, the way OpModeManagerImpl calls them.
 */
package com.qualcomm.robotcore.eventloop.opmode;

import com.qualcomm.robotcore.hardware.Gamepad;

public final class SimOpModeAccess {
  private SimOpModeAccess() {}

  public static final int FORCE_STOP_MS = OpModeInternal.MS_BEFORE_FORCE_STOP_AFTER_STOP_REQUESTED;

  public static void init(OpMode opMode) { opMode.internalInit(); }
  public static void start(OpMode opMode) { opMode.internalStart(); }
  public static boolean beginStop(OpMode opMode) { return opMode.internalBeginStop(); }
  public static void eventLoopIteration(OpMode opMode) { opMode.internalOnEventLoopIteration(); }
  public static void gamepads(OpMode opMode, Gamepad g1, Gamepad g2) { opMode.newGamepadDataAvailable(g1, g2); }
  public static boolean threadFinished(OpMode opMode) { return opMode.opModeThreadFinished; }
  public static boolean isStarted(OpMode opMode) { return opMode.isStarted; }
  public static boolean stopRequested(OpMode opMode) { return opMode.stopRequested; }
  public static RuntimeException exception(OpMode opMode) { return opMode.exception; }
  public static Throwable error(OpMode opMode) {
    if (opMode.noClassDefFoundError != null) return opMode.noClassDefFoundError;
    return opMode.otherError;
  }
  public static void clearException(OpMode opMode) { opMode.exception = null; opMode.noClassDefFoundError = null; opMode.otherError = null; }
}
