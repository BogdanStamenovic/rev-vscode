/*
 * Simulator replacement for the FTC SDK RobotLog. The real class writes to
 * android.util.Log and the RC's log files, neither of which exists here.
 * Same public static signatures as SDK 11.2.0 so real SDK classes that log
 * keep linking; warnings and errors are forwarded to the simulator's log
 * stream, verbose/debug/info are dropped (the SDK is chatty at those levels).
 */
package com.qualcomm.robotcore.util;

import org.pyftc.sim.SimLog;

import com.qualcomm.robotcore.exception.RobotCoreException;

import java.util.ArrayList;
import java.util.List;

@SuppressWarnings({"unused", "WeakerAccess"})
public class RobotLog {

  public static final String OPMODE_START_TAG = "******************** START - OPMODE %s ********************";
  public static final String OPMODE_STOP_TAG  = "******************** STOP - OPMODE %s ********************";
  public static final String TAG = "RobotCore";

  private static volatile String globalErrorMessage = "";
  private static final List<String> globalWarnings = new ArrayList<String>();

  public static class GlobalWarningMessage {
    public final String message;
    public final boolean isSticky;
    public GlobalWarningMessage(String message, boolean isSticky) { this.message = message; this.isSticky = isSticky; }
  }

  private static String fmt(String format, Object... args) {
    if (args == null || args.length == 0) return format;
    try { return String.format(format, args); } catch (RuntimeException e) { return format; }
  }

  private static void warn(String tag, Throwable t, String message) { SimLog.warn(tag, message, t); }
  private static void error(String tag, Throwable t, String message) { SimLog.error(tag, message, t); }

  public static void processTimeSynch(long t0, long t1, long t2, long t3) { }
  public static void setMsTimeOffset(double offset) { }
  public static long getRemoteTime() { return System.currentTimeMillis(); }
  public static long getRemoteTime(long localTime) { return localTime; }
  public static long getLocalTime(long remoteTime) { return remoteTime; }

  public static void a(String format, Object... args) { }
  public static void a(String message) { }
  public static void aa(String tag, String format, Object... args) { }
  public static void aa(String tag, String message) { }
  public static void aa(String tag, Throwable throwable, String format, Object... args) { }
  public static void aa(String tag, Throwable throwable, String message) { }

  public static void v(String format, Object... args) { }
  public static void v(String message) { }
  public static void vv(String tag, String format, Object... args) { }
  public static void vv(String tag, String message) { }
  public static void vv(String tag, Throwable throwable, String format, Object... args) { }
  public static void vv(String tag, Throwable throwable, String message) { }

  public static void d(String format, Object... args) { }
  public static void d(String message) { }
  public static void dd(String tag, String format, Object... args) { }
  public static void dd(String tag, String message) { }
  public static void dd(String tag, Throwable throwable, String format, Object... args) { }
  public static void dd(String tag, Throwable throwable, String message) { }

  public static void i(String format, Object... args) { }
  public static void i(String message) { }
  public static void ii(String tag, String format, Object... args) { }
  public static void ii(String tag, String message) { }
  public static void ii(String tag, Throwable throwable, String format, Object... args) { }
  public static void ii(String tag, Throwable throwable, String message) { }

  public static void w(String format, Object... args) { warn(TAG, null, fmt(format, args)); }
  public static void w(String message) { warn(TAG, null, message); }
  public static void ww(String tag, String format, Object... args) { warn(tag, null, fmt(format, args)); }
  public static void ww(String tag, String message) { warn(tag, null, message); }
  public static void ww(String tag, Throwable throwable, String format, Object... args) { warn(tag, throwable, fmt(format, args)); }
  public static void ww(String tag, Throwable throwable, String message) { warn(tag, throwable, message); }

  public static void e(String format, Object... args) { error(TAG, null, fmt(format, args)); }
  public static void e(String message) { error(TAG, null, message); }
  public static void ee(String tag, String format, Object... args) { error(tag, null, fmt(format, args)); }
  public static void ee(String tag, String message) { error(tag, null, message); }
  public static void ee(String tag, Throwable throwable, String format, Object... args) { error(tag, throwable, fmt(format, args)); }
  public static void ee(String tag, Throwable throwable, String message) { error(tag, throwable, message); }

  public static void internalLog(int priority, String tag, String message) { if (priority >= 5) warn(tag, null, message); }
  public static void internalLog(int priority, String tag, Throwable throwable, String message) { if (priority >= 5) warn(tag, throwable, message); }

  public static void logExceptionHeader(Exception e, String format, Object... args) { error(TAG, e, fmt(format, args)); }
  public static void logExceptionHeader(String tag, Exception e, String format, Object... args) { error(tag, e, fmt(format, args)); }
  public static void logStacktrace(Throwable e) { }
  public static void logStackTrace(Throwable e) { }
  public static void logStackTrace(Thread thread, String format, Object... args) { }
  public static void logStackTrace(Thread thread, StackTraceElement[] stackTrace) { }
  public static void logStackTrace(String tag, Throwable e) { }

  public static boolean setGlobalErrorMsg(String message) {
    if (globalErrorMessage.isEmpty()) {
      globalErrorMessage = message;
      SimLog.error("GlobalError", message, null);
      return true;
    }
    return false;
  }
  public static void setGlobalErrorMsg(String format, Object... args) { setGlobalErrorMsg(fmt(format, args)); }
  public static void addGlobalWarningMessage(String msg) {
    synchronized (globalWarnings) { if (!globalWarnings.contains(msg)) globalWarnings.add(msg); }
    SimLog.warn("GlobalWarning", msg, null);
  }
  public static void addGlobalWarningMessage(String format, Object... args) { addGlobalWarningMessage(fmt(format, args)); }
  public static void registerGlobalWarningSource(GlobalWarningSource globalWarningSource) { }
  public static void unregisterGlobalWarningSource(GlobalWarningSource globalWarningSource) { }
  public static void setGlobalErrorMsg(RuntimeException e, String message) { setGlobalErrorMsg(message); }
  public static void setGlobalErrorMsg(RobotCoreException e, String message) { setGlobalErrorMsg(message); }
  public static void setGlobalErrorMsgAndThrow(RobotCoreException e, String message) throws RobotCoreException { setGlobalErrorMsg(message); throw e; }
  public static void setGlobalErrorMsgAndThrow(RuntimeException e, String message) throws RobotCoreException { setGlobalErrorMsg(message); throw e; }
  public static void logAndThrow(String errMsg) throws RobotCoreException { error(TAG, null, errMsg); throw new RobotCoreException(errMsg); }
  public static String getGlobalErrorMsg() { return globalErrorMessage; }
  public static void setGlobalErrorMsgSticky(boolean sticky) { }
  public static GlobalWarningMessage getGlobalWarningMessage() {
    synchronized (globalWarnings) { return new GlobalWarningMessage(combineGlobalWarnings(globalWarnings), false); }
  }
  public static void setGlobalWarningMsgSticky(boolean sticky) { }
  public static String combineGlobalWarnings(List<String> warnings) {
    StringBuilder b = new StringBuilder();
    for (String w : warnings) { if (b.length() > 0) b.append("; "); b.append(w); }
    return b.toString();
  }
  public static boolean hasGlobalErrorMsg() { return !globalErrorMessage.isEmpty(); }
  public static boolean hasGlobalWarningMsg() { synchronized (globalWarnings) { return !globalWarnings.isEmpty(); } }
  public static void clearGlobalErrorMsg() { globalErrorMessage = ""; }
  public static void clearGlobalWarningMsg() { synchronized (globalWarnings) { globalWarnings.clear(); } }
  public static void onApplicationStart() { }
  public static void logAppInfo() { }
  public static void logDeviceInfo() { }
  public static void logBytes(String tag, String caption, byte[] data, int cb) { }
  public static void logBytes(String tag, String caption, byte[] data, int ibStart, int cb) { }
}
