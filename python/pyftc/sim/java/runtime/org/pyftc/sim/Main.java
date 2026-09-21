package org.pyftc.sim;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.pyftc.sim.hw.Robot;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Entry point of the simulator process (Contract 5).
 *
 *   java -cp <simsdk runtime>:<user classes>:<SDK jars>:<gson> org.pyftc.sim.Main
 *        --manifest manifest.json --constants constants.json [--layout sim-layout.json]
 *        [--fast] [--emit-ms 20] [--script commands.jsonl] [--until 12.5] [--record out.jsonl]
 */
public final class Main {
    private Main() {}

    public static void main(String[] args) throws Exception {
        PrintStream realOut = System.out;
        System.setOut(System.err);

        String manifestPath = null, constantsPath = null, layoutPath = null, scriptPath = null, recordPath = null;
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--manifest": manifestPath = args[++i]; break;
                case "--constants": constantsPath = args[++i]; break;
                case "--layout": layoutPath = args[++i]; break;
                case "--script": scriptPath = args[++i]; break;
                case "--record": recordPath = args[++i]; break;
                case "--fast": Scheduler.realtime = false; break;
                case "--emit-ms": Scheduler.emitEverySimMs = Double.parseDouble(args[++i]); break;
                case "--until": Scheduler.untilSec = Double.parseDouble(args[++i]); break;
                default:
                    System.err.println("unknown argument " + args[i]);
                    System.exit(2);
            }
        }
        Out.init(realOut, recordPath);
        try {
            if (manifestPath == null || constantsPath == null) throw new IllegalArgumentException("--manifest and --constants are required");
            Constants.load(constantsPath);
            SimClock.callCostNs = (long) (Constants.num("sim.sdkCallCostUs") * 1000);
            JsonObject manifest = readJson(manifestPath).getAsJsonObject();
            JsonObject layout = layoutPath != null && Files.exists(Paths.get(layoutPath)) ? readJson(layoutPath).getAsJsonObject() : null;
            Locator.load(manifest.getAsJsonObject("lineMaps"));
            if (manifest.has("traceFiles")) {
                JsonArray tf = manifest.getAsJsonArray("traceFiles");
                String[] files = new String[tf.size()];
                for (int i = 0; i < files.length; i++) files[i] = tf.get(i).getAsString();
                Trace.setFiles(files);
            }
            Robot robot = Robot.build(manifest.getAsJsonObject("config"), layout);
            Registry.load(manifest.getAsJsonArray("classes"));

            JsonObject ready = new JsonObject();
            ready.addProperty("type", "ready");
            ready.addProperty("protocol", 1);
            ready.addProperty("sdkVersion", manifest.has("sdkVersion") ? manifest.get("sdkVersion").getAsString() : "?");
            ready.add("opModes", Registry.describe());
            ready.add("devices", robot.describeDevices());
            ready.add("hubs", robot.describeHubs());
            JsonObject cfg = new JsonObject();
            JsonObject mc = manifest.getAsJsonObject("config");
            cfg.addProperty("name", mc.has("name") ? mc.get("name").getAsString() : "?");
            cfg.addProperty("source", mc.has("source") ? mc.get("source").getAsString() : "?");
            ready.add("config", cfg);
            JsonArray ns = new JsonArray();
            for (String s : robot.notSimulated) ns.add(s);
            ready.add("notSimulated", ns);
            ready.addProperty("trace", Trace.enabled());
            Out.send(ready);

            if (scriptPath != null) {
                for (String line : Files.readAllLines(Paths.get(scriptPath), StandardCharsets.UTF_8)) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) continue;
                    Scheduler.incoming.add(new JsonParser().parse(line).getAsJsonObject());
                }
            } else {
                startStdinReader();
            }
            Scheduler.run();
        } catch (Throwable t) {
            JsonObject o = new JsonObject();
            o.addProperty("type", "fatal");
            o.addProperty("message", t.toString());
            Out.send(o);
            t.printStackTrace(System.err);
            Out.close();
            System.exit(1);
        }
        Out.close();
        // Daemon OpMode threads must not keep the JVM alive.
        System.exit(0);
    }

    private static JsonElement readJson(String path) throws IOException {
        return new JsonParser().parse(new String(Files.readAllBytes(Paths.get(path)), StandardCharsets.UTF_8));
    }

    private static void startStdinReader() {
        Thread t = new Thread(new Runnable() {
            @Override public void run() {
                try (BufferedReader r = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = r.readLine()) != null) {
                        line = line.trim();
                        if (line.isEmpty()) continue;
                        try {
                            Scheduler.incoming.add(new JsonParser().parse(line).getAsJsonObject());
                        } catch (RuntimeException e) {
                            SimLog.warn("sim", "bad command line: " + e.getMessage(), null);
                        }
                    }
                } catch (IOException ignored) {
                }
                // The extension closed our stdin: shut down.
                Scheduler.quit = true;
            }
        }, "stdin");
        t.setDaemon(true);
        t.start();
    }
}
