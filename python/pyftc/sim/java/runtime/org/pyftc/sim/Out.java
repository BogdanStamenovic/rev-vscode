package org.pyftc.sim;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;

import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.Writer;
import java.nio.charset.StandardCharsets;

/**
 * The protocol stream (Contract 5): one JSON object per line on the real stdout.
 * System.out is redirected to stderr at startup so that anything else printing
 * (user code's print(), stray SDK output) can never corrupt the stream.
 */
public final class Out {
    private static final Gson GSON = new GsonBuilder().serializeSpecialFloatingPointValues().disableHtmlEscaping().create();
    private static Writer writer;
    private static Writer record;

    private Out() {}

    static synchronized void init(PrintStream realStdout, String recordPath) throws IOException {
        writer = new BufferedWriter(new OutputStreamWriter(realStdout, StandardCharsets.UTF_8));
        if (recordPath != null) {
            record = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(recordPath), StandardCharsets.UTF_8));
        }
    }

    public static Gson gson() {
        return GSON;
    }

    public static synchronized void send(JsonElement e) {
        String line = GSON.toJson(e);
        try {
            if (writer != null) {
                writer.write(line);
                writer.write('\n');
                writer.flush();
            }
            if (record != null) {
                record.write(line);
                record.write('\n');
            }
        } catch (IOException ignored) {
            // The extension went away; the stdin reader notices EOF and exits.
        }
    }

    static synchronized void close() {
        try {
            if (writer != null) writer.flush();
            if (record != null) record.close();
        } catch (IOException ignored) {
        }
    }
}
