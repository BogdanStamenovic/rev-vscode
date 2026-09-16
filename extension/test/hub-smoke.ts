// Integration smoke test against the REAL hub (adb serial fd6f053873e61e59
// per the task brief). Exercises connection resolution, rcInfo/config
// reads, and a full save->build->fail->delete->build cycle against OnBot
// Java, then leaves the hub clean.
//
// Runs outside the extension host, so 'vscode' is resolved to the tiny
// shim at test/vscode-shim/vscode.js via NODE_PATH (see package.json's
// "smoke" script). Another agent may be using the same hub concurrently;
// each hub-touching step retries once on failure before giving up.
import { getConnection } from '../src/hub/connection';
import { fetchRcInfo } from '../src/hub/rcinfo';
import { fetchActiveConfigXml, parseActiveConfig } from '../src/hub/configFetch';
import { saveFile, deleteFiles, runBuild, fileTree } from '../src/hub/onbotjava';

const HUB_PATH = '/src/org/firstinspires/ftc/teamcode/pyftc/SmokeTest.java';
const CANONICAL_PATH = 'org/firstinspires/ftc/teamcode/pyftc/SmokeTest.java';

const VALID_JAVA = `package org.firstinspires.ftc.teamcode.pyftc;

import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;

@TeleOp(name = "SmokeTest")
public class SmokeTest extends LinearOpMode {
    @Override
    public void runOpMode() {
        waitForStart();
        while (opModeIsActive()) {
            telemetry.update();
        }
    }
}
`;

// Line 12 is `telemetry.updat();` once broken - the assertion below checks
// the parsed build error lands on exactly that line.
const BROKEN_JAVA = VALID_JAVA.replace('telemetry.update();', 'telemetry.updat();');

async function step<T>(name: string, fn: () => Promise<T>): Promise<T> {
  process.stdout.write(`\n--- ${name} ---\n`);
  const result = await fn();
  process.stdout.write(`ok: ${name}\n`);
  return result;
}

async function retryOnce<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    process.stdout.write(`(retrying once after: ${(err as Error).message})\n`);
    return fn();
  }
}

async function main(): Promise<void> {
  let needsCleanup = true;
  try {
    const conn = await step('(a) resolve connection via adb forward', () => getConnection());
    console.log(JSON.stringify(conn, null, 2));
    if (conn.transport !== 'usb' || !conn.adbSerial) {
      throw new Error(`expected transport "usb" with an adbSerial, got ${JSON.stringify(conn)}`);
    }

    const rcInfo = await step('(b) fetch rcInfo.json (passphrase stripped)', () => fetchRcInfo());
    console.log(JSON.stringify(rcInfo, null, 2));
    if (Object.prototype.hasOwnProperty.call(rcInfo, 'passphrase')) {
      throw new Error('passphrase leaked into RcInfo!');
    }

    const { xml } = await step('(c) read active config xml via adb', () =>
      fetchActiveConfigXml(conn, rcInfo.activeConfigName)
    );
    const parsedConfig = parseActiveConfig(xml);
    console.log(
      `config hubs: ${parsedConfig.hubs.map((h) => `${h.name} (${h.devices.length} device(s))`).join(', ') || '(none)'}`
    );

    await step('(d) save + build a valid SmokeTest.java, expect success', () =>
      retryOnce(async () => {
        await saveFile(HUB_PATH, VALID_JAVA);
        const build = await runBuild();
        if (!build.status.successful) {
          throw new Error(`expected a successful build, got errors: ${JSON.stringify(build.errors)}`);
        }
      })
    );

    await step('(e) save + build a broken SmokeTest.java, expect the right line', () =>
      retryOnce(async () => {
        await saveFile(HUB_PATH, BROKEN_JAVA);
        const build = await runBuild();
        if (build.status.successful) {
          throw new Error('expected the build to fail on the broken file, but it succeeded');
        }
        const err = build.errors.find((e) => e.file === CANONICAL_PATH);
        if (!err) {
          throw new Error(`no build error reported for ${CANONICAL_PATH}: ${JSON.stringify(build.errors)}`);
        }
        if (err.line !== 12) {
          throw new Error(`expected the error on line 12, got line ${err.line}: ${JSON.stringify(err)}`);
        }
        console.log(`got expected error: ${JSON.stringify(err)}`);
      })
    );

    await step('(f) delete SmokeTest.java and rebuild clean', () =>
      retryOnce(async () => {
        await deleteFiles([CANONICAL_PATH]);
        const tree = await fileTree();
        if (tree.includes(CANONICAL_PATH)) {
          throw new Error('SmokeTest.java is still present in the hub file tree after delete');
        }
        const build = await runBuild();
        if (!build.status.successful) {
          throw new Error(`expected a clean build after delete, got errors: ${JSON.stringify(build.errors)}`);
        }
      })
    );

    needsCleanup = false;
    console.log('\nALL SMOKE TESTS PASSED');
  } catch (err) {
    console.error('\nSMOKE TEST FAILED:', err);
    if (needsCleanup) {
      console.error('attempting cleanup: deleting SmokeTest.java from the hub...');
      try {
        await deleteFiles([CANONICAL_PATH]);
        console.error('cleanup: deleted.');
      } catch (cleanupErr) {
        console.error('cleanup also failed - hub may still have SmokeTest.java on it:', cleanupErr);
      }
    }
    process.exitCode = 1;
  }
}

void main();
