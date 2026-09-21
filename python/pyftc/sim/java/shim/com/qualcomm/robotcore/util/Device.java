/*
 * Simulator stand-in for the FTC SDK 11.2.0 com.qualcomm.robotcore.util.Device.
 * The real class initialises from Android services at class-load time; the
 * simulator is always "a REV Control Hub", which is what HardwareMap.tryGet asks.
 */
package com.qualcomm.robotcore.util;

public final class Device {
  public static final String MANUFACTURER_REV = "REV Robotics";
  public static final String MODEL_CONTROL_HUB = "Control Hub";

  private Device() {}

  public static boolean isRevControlHub() { return true; }
  public static boolean isRevDriverHub() { return false; }
  public static boolean useUsbForLynx() { return false; }
  public static boolean isMoto() { return false; }
  public static String getSerialNumberOrUnknown() { return "SIMULATED"; }
}
