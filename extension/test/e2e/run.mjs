// Usage: E2E_HUB_URL=http://127.0.0.1:18080 node test/e2e/run.mjs
// Downloads a separate VS Code build into .vscode-test (not the user's editor)
// and runs suite.js inside its extension host against the real hub.
import { runTests } from '@vscode/test-electron';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ext = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const tmp = mkdtempSync(path.join(os.tmpdir(), 'rev-e2e-'));
mkdirSync(path.join(tmp, 'ws/.vscode'), { recursive: true });
writeFileSync(path.join(tmp, 'ws/.vscode/settings.json'), JSON.stringify({ 'revFtc.pythonPath': 'python3' }));
execFileSync('node', [path.join(ext, 'scripts/copy-python.mjs')]);
execFileSync('npm', ['run', '-s', 'build'], { cwd: ext });
process.env.E2E_RESULT = path.join(tmp, 'result.json');

try {
  await runTests({
    extensionDevelopmentPath: ext,
    extensionTestsPath: path.join(ext, 'test/e2e/suite.js'),
    launchArgs: [path.join(tmp, 'ws'), '--disable-extensions', '--user-data-dir', path.join(tmp, 'user')],
    extensionTestsEnv: { E2E_RESULT: process.env.E2E_RESULT, E2E_HUB_URL: process.env.E2E_HUB_URL },
  });
} catch (e) {
  console.error('VS Code test run failed:', e);
}
if (!existsSync(process.env.E2E_RESULT)) {
  console.error('no result file');
  process.exit(2);
}
let bad = 0;
for (const c of JSON.parse(readFileSync(process.env.E2E_RESULT, 'utf8'))) {
  console.log((c.ok ? 'PASS ' : 'FAIL ') + c.name + (c.ok ? '' : '  ' + JSON.stringify(c.detail)));
  bad += !c.ok;
}
process.exit(bad ? 1 : 0);
