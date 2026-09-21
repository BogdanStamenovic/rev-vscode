/*
 * Simulator stand-in for the FTC SDK 11.2.0 ConfigurationTypeManager. The real one
 * scans the APK and builds its built-in types from Android string resources; here
 * the simulator registers the configuration types it builds from the same
 * @MotorType / @ServoType / @DeviceProperties annotations (org.pyftc.sim.hw.Robot),
 * and the lookups the SDK's device classes use are answered from that registry.
 */
package com.qualcomm.robotcore.hardware.configuration;

import com.qualcomm.robotcore.hardware.configuration.annotations.DeviceProperties;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.MotorConfigurationType;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.ServoConfigurationType;
import com.qualcomm.robotcore.hardware.configuration.typecontainers.UserConfigurationType;

import java.util.HashMap;
import java.util.Map;

public class ConfigurationTypeManager {
    public enum ClassSource {
        APK,
        ONBOTJAVA,
        EXTERNAL_LIB
    }

    public static final String TAG = "UserDeviceTypeManager";
    public static boolean DEBUG = false;
    public static String LEGACY_HD_HEX_MOTOR_TAG = "RevRoboticsHDHexMotor";
    public static String NEW_HD_HEX_MOTOR_40_TAG = "RevRobotics40HDHexMotor";

    private static final ConfigurationTypeManager theInstance = new ConfigurationTypeManager();

    private final Map<String, ConfigurationType> mapTagToConfigurationType = new HashMap<String, ConfigurationType>();

    public static ConfigurationTypeManager getInstance() {
        return theInstance;
    }

    public synchronized void register(ConfigurationType type) {
        mapTagToConfigurationType.put(type.getXmlTag(), type);
    }

    public synchronized ConfigurationType configurationTypeFromTag(String xmlTag) {
        ConfigurationType result = mapTagToConfigurationType.get(xmlTag);
        if (result == null) {
            throw new UnsupportedOperationException("not simulated: configuration type '" + xmlTag + "'");
        }
        return result;
    }

    public MotorConfigurationType getUnspecifiedMotorType() {
        return (MotorConfigurationType) configurationTypeFromTag("Motor");
    }

    public ServoConfigurationType getStandardServoType() {
        return (ServoConfigurationType) configurationTypeFromTag("Servo");
    }

    public UserConfigurationType userTypeFromClass(ConfigurationType.DeviceFlavor flavor, Class<?> clazz) {
        String xmlTag = getXmlTag(clazz);
        if (xmlTag == null) return null;
        ConfigurationType t;
        synchronized (this) {
            t = mapTagToConfigurationType.get(xmlTag);
        }
        return t instanceof UserConfigurationType ? (UserConfigurationType) t : null;
    }

    public static String getXmlTag(Class clazz) {
        DeviceProperties p = (DeviceProperties) clazz.getAnnotation(DeviceProperties.class);
        return p == null ? null : p.xmlTag().trim();
    }
}
