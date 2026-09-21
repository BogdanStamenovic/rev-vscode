// Usage: node test/e2e/runSim.mjs   (run it under Xvfb: it opens a VS Code window)
// Extension-host test of the simulator with no hardware attached (simSuite.js).
// Needs a JDK: REVFTC_E2E_JAVA_HOME, else the repo's .cache/javac/jdk-* from
// scripts/javac-env.sh.
import { runTests } from '@vscode/test-electron';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Under Xvfb (DISPLAY set, WAYLAND_DISPLAY unset) Electron still auto-selects its
// Wayland backend and connects to the default wayland-0 socket, i.e. the user's real
// screen. Forcing X11 keeps the test window on the Xvfb display.
const OZONE = process.env.DISPLAY && !process.env.WAYLAND_DISPLAY ? ['--ozone-platform=x11', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] : [];
const ext = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const repo = path.dirname(ext);
const tmp = mkdtempSync(path.join(os.tmpdir(), 'rev-e2e-sim-'));
const ws = path.join(tmp, 'ws');
mkdirSync(path.join(ws, '.vscode'), { recursive: true });

let javaHome = process.env.REVFTC_E2E_JAVA_HOME;
if (!javaHome) {
  const cache = path.join(repo, '.cache', 'javac');
  const jdk = existsSync(cache) ? readdirSync(cache).find((d) => d.startsWith('jdk-')) : undefined;
  if (!jdk) {
    console.error('no JDK: run scripts/javac-env.sh or set REVFTC_E2E_JAVA_HOME');
    process.exit(2);
  }
  javaHome = path.join(cache, jdk);
}

writeFileSync(path.join(ws, 'Robot.xml'), readFileSync(path.join(repo, 'python/tests/fixtures/Mixed.xml'), 'utf8'));
const bench = `from ftc.opmode import LinearOpMode, TeleOp
from ftc.hardware import DcMotor


@TeleOp(name="Bench", group="e2e")
class Bench(LinearOpMode):
    drive: DcMotor

    def runOpMode(self) -> None:
        self.drive = self.hardwareMap.get(DcMotor, "frontLeft")
        self.waitForStart()
        while self.opModeIsActive():
            self.drive.setPower(-self.gamepad1.left_stick_y)
            if self.gamepad1.cross:
                arm = self.hardwareMap.get(DcMotor, "armm")
                arm.setPower(1)
`;
writeFileSync(path.join(ws, 'Bench.py'), bench);
const throwLine = bench.split('\n').findIndex((l) => l.includes('"armm"')) + 1;
const bpLine = bench.split('\n').findIndex((l) => l.includes('self.drive.setPower')) + 1;

writeFileSync(path.join(ws, '.vscode/settings.json'), JSON.stringify({
  'revFtc.pythonPath': 'python3',
  'revFtc.javaHome': javaHome,
  'revFtc.simulatorConfigSource': 'workspace',
  'revFtc.liveDiagnostics': false,
  'revFtc.configWatch': false,
}));

execFileSync('node', [path.join(ext, 'scripts/copy-python.mjs')]);
execFileSync('npm', ['run', '-s', 'build'], { cwd: ext });

const resultFile = path.join(tmp, 'result.json');
try {
  await runTests({
    extensionDevelopmentPath: ext,
    extensionTestsPath: path.join(ext, 'test/e2e/simSuite.js'),
    launchArgs: [ws, '--disable-extensions', '--user-data-dir', path.join(tmp, 'user'), ...OZONE],
    extensionTestsEnv: { E2E_RESULT: resultFile, E2E_THROW_LINE: String(throwLine), E2E_BP_LINE: String(bpLine), E2E_HOLD_MS: process.env.E2E_HOLD_MS || '' },
  });
} catch (e) {
  console.error('VS Code test run failed:', e);
}
if (!existsSync(resultFile)) {
  console.error('no result file');
  process.exit(2);
}
let bad = 0;
for (const c of JSON.parse(readFileSync(resultFile, 'utf8'))) {
  console.log((c.ok ? 'PASS ' : 'FAIL ') + c.name + (c.ok && !process.env.E2E_VERBOSE ? '' : '  ' + JSON.stringify(c.detail)));
  bad += !c.ok;
}
process.exit(bad ? 1 : 0);
