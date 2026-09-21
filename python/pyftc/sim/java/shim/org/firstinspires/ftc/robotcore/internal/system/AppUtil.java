/*
 * Simulator stand-in for the FTC SDK 11.2.0 AppUtil (BSD-3-Clause, FIRST): only
 * the file helpers OpModes use. The Robot Controller's /sdcard/FIRST folder maps
 * to the directory given by the system property pyftc.sim.firstDir (the
 * extension points it at <workspace>/.pyftc/sim-files/FIRST), so settings files
 * written by one simulated OpMode are there for the next, like on the hub.
 */
package org.firstinspires.ftc.robotcore.internal.system;

import java.io.File;

public class AppUtil {
    public static final File ROOT_FOLDER = new File(System.getProperty("pyftc.sim.rootDir", System.getProperty("java.io.tmpdir") + "/pyftc-sim-sdcard"));
    public static final File FIRST_FOLDER = new File(System.getProperty("pyftc.sim.firstDir", ROOT_FOLDER + "/FIRST"));
    public static final File LOG_FOLDER = ROOT_FOLDER;
    public static final File MATCH_LOG_FOLDER = new File(FIRST_FOLDER + "/matchlogs/");
    public static final File CONFIG_FILES_DIR = FIRST_FOLDER;
    public static final File ROBOT_SETTINGS = new File(FIRST_FOLDER, "/settings/");
    public static final File ROBOT_DATA_DIR = new File(FIRST_FOLDER, "/data/");
    public static final String TAG = "AppUtil";

    private static final AppUtil theInstance = new AppUtil();

    public static AppUtil getInstance() {
        return theInstance;
    }

    /** The Robot Controller's Android application context; there is none in the simulator. */
    public static android.app.Application getDefContext() {
        throw new UnsupportedOperationException("not simulated: this SDK call needs the Robot Controller's Android context (AppUtil.getDefContext), which the simulator does not have");
    }

    public File getSettingsFile(String filename) {
        File file = new File(filename);
        if (!file.isAbsolute()) {
            ensureDirectoryExists(ROBOT_SETTINGS);
            file = new File(ROBOT_SETTINGS, filename);
        }
        return file;
    }

    public void ensureDirectoryExists(final File directory) {
        ensureDirectoryExists(directory, true);
    }

    public void ensureDirectoryExists(final File directory, boolean notify) {
        if (!directory.isDirectory()) {
            directory.mkdirs();
        }
    }

    public File getRelativePath(File root, File child) {
        File result = new File("");
        while (!root.equals(child)) {
            File parent = child.getParentFile();
            result = new File(new File(child.getName()), result.getPath());
            if (parent == null) break;
            child = parent;
        }
        return result;
    }
}
