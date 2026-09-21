package org.pyftc.sim;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Every physical constant the simulator uses comes from constants.json
 * (python/pyftc/sim/constants.json): value, unit, source, and whether it is a
 * verified published spec or a labelled placeholder. Nothing physical is
 * hard-coded in Java.
 */
public final class Constants {
    private static JsonObject root = new JsonObject();

    private Constants() {}

    static void load(String path) throws IOException {
        try (Reader r = new InputStreamReader(Files.newInputStream(Paths.get(path)), StandardCharsets.UTF_8)) {
            root = new JsonParser().parse(r).getAsJsonObject();
        }
    }

    private static JsonObject entry(String key) {
        String[] parts = key.split("\\.");
        JsonElement cur = root;
        for (String p : parts) {
            if (cur == null || !cur.isJsonObject() || !cur.getAsJsonObject().has(p)) {
                throw new IllegalStateException("constants.json has no entry '" + key + "'");
            }
            cur = cur.getAsJsonObject().get(p);
        }
        if (!cur.isJsonObject() || !cur.getAsJsonObject().has("value")) {
            throw new IllegalStateException("constants.json entry '" + key + "' has no value");
        }
        return cur.getAsJsonObject();
    }

    public static double num(String key) {
        return entry(key).get("value").getAsDouble();
    }

    public static boolean verified(String key) {
        JsonObject e = entry(key);
        return e.has("verified") && e.get("verified").getAsBoolean();
    }
}
