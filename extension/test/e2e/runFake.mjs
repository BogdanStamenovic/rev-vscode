// Usage: node test/e2e/runFake.mjs
// Same shape as run.mjs (downloads/reuses a separate VS Code build into
// .vscode-test and runs an extension-host test), but against a fake hub
// (fakeHub.mjs, HTTP) and fake adb (fake_adb.py) instead of real hardware -
// see fakeSuite.js's header for exactly what that does and doesn't cover.
// Safe to run with no Control Hub attached; that's the whole point.
import { runTests } from '@vscode/test-electron';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startFakeHub } from './fakeHub.mjs';

const ext = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const tmp = mkdtempSync(path.join(os.tmpdir(), 'rev-e2e-fake-'));
mkdirSync(path.join(tmp, 'ws/.vscode'), { recursive: true });

const configName = 'TestConfig';
const configXmlPath = path.join(tmp, `${configName}.xml`);
writeFileSync(configXmlPath, '<Robot></Robot>', 'utf8'); // fakeSuite.js overwrites this itself

const fakeHub = await startFakeHub({ activeConfigName: configName, sdkVersion: '11.2.0' });

writeFileSync(
  path.join(tmp, 'ws/.vscode/settings.json'),
  JSON.stringify({
    'revFtc.pythonPath': 'python3',
    'revFtc.translatorCommand': ['python3', path.join(ext, 'test/fixtures/fake_pyftc.py')],
    'revFtc.hubUrl': fakeHub.url,
    'revFtc.adbPath': path.join(ext, 'test/fixtures/fake_adb.py'),
  })
);

execFileSync('node', [path.join(ext, 'scripts/copy-python.mjs')]);
execFileSync('npm', ['run', '-s', 'build'], { cwd: ext });

process.env.E2E_RESULT = path.join(tmp, 'result.json');

let bad = 1;
try {
  await runTests({
    extensionDevelopmentPath: ext,
    extensionTestsPath: path.join(ext, 'test/e2e/fakeSuite.js'),
    launchArgs: [path.join(tmp, 'ws'), '--disable-extensions', '--user-data-dir', path.join(tmp, 'user')],
    extensionTestsEnv: {
      E2E_RESULT: process.env.E2E_RESULT,
      FAKE_HUB_CONFIG_XML: configXmlPath,
      FAKE_HUB_CONFIG_NAME: configName,
      FAKE_HUB_SERIAL: 'FAKEHUBSERIAL',
    },
  });
} catch (e) {
  console.error('VS Code test run failed:', e);
} finally {
  await fakeHub.close();
}

if (!existsSync(process.env.E2E_RESULT)) {
  console.error('no result file');
  process.exit(2);
}
bad = 0;
for (const c of JSON.parse(readFileSync(process.env.E2E_RESULT, 'utf8'))) {
  console.log((c.ok ? 'PASS ' : 'FAIL ') + c.name + (c.ok ? '' : '  ' + JSON.stringify(c.detail)));
  bad += !c.ok;
}
process.exit(bad ? 1 : 0);
