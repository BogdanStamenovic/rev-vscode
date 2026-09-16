// Runs inside a real VS Code extension host against the REAL hub:
// spawn starter pack -> deploy -> javac error mapped to a .py line -> stale
// file removal. Launched by test/e2e/run.sh; results go to $E2E_RESULT.
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const HUB = process.env.E2E_HUB_URL;
const results = [];
const check = (name, ok, detail) => results.push({ name, ok: !!ok, detail });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function hubTree() {
  const r = await fetch(`${HUB}/java/file/tree`);
  return (await r.json()).src.filter((p) => p.includes('/pyftc/') && p.endsWith('.java'));
}

async function run() {
  const ws = vscode.workspace.workspaceFolders[0].uri.fsPath;
  try {
    const spawn = vscode.commands.executeCommand('revFtc.spawnStarterPack');
    // the class-name input box waits for the user; accept the default
    for (let i = 0; i < 20 && !fs.existsSync(path.join(ws, 'StarterPack.py')); i++) {
      await sleep(1000);
      await vscode.commands.executeCommand('workbench.action.acceptSelectedQuickOpenItem');
    }
    await spawn;
    const starter = path.join(ws, 'StarterPack.py');
    const src = fs.existsSync(starter) ? fs.readFileSync(starter, 'utf8') : '';
    check('starter pack file created', src.includes('class StarterPack(LinearOpMode)'), src.slice(0, 200));
    check('starter pack lists live hardware', src.includes('"petranje"') && src.includes('What a DcMotor can do'));

    await vscode.commands.executeCommand('revFtc.deploy');
    let tree = await hubTree();
    check('deploy put StarterPack.java on hub', tree.some((p) => p.endsWith('/StarterPack.java')), tree);
    const status = await (await fetch(`${HUB}/java/build/status`)).json();
    check('hub build succeeded', status.successful, status);

    const broken = path.join(ws, 'Broken.py');
    fs.writeFileSync(broken, [
      'from ftc.opmode import LinearOpMode, TeleOp',
      '',
      '',
      '@TeleOp(name="Broken", group="pyftc")',
      'class Broken(LinearOpMode):',
      '    def runOpMode(self) -> None:',
      '        self.waitForStart()',
      '        return',
      '        self.telemetry.update()',
      '',
    ].join('\n'));
    await vscode.commands.executeCommand('revFtc.deploy');
    const diags = vscode.languages.getDiagnostics(vscode.Uri.file(broken));
    check('javac error mapped to Broken.py line 9',
      diags.some((d) => d.range.start.line === 8 && /unreachable/i.test(d.message)),
      diags.map((d) => ({ line: d.range.start.line + 1, message: d.message })));

    fs.unlinkSync(broken);
    await vscode.commands.executeCommand('revFtc.deploy');
    tree = await hubTree();
    check('stale Broken.java removed from hub', !tree.some((p) => p.endsWith('/Broken.java')), tree);
    check('StarterPack.java still on hub', tree.some((p) => p.endsWith('/StarterPack.java')), tree);
    const status2 = await (await fetch(`${HUB}/java/build/status`)).json();
    check('final hub build succeeded', status2.successful, status2);
    check('Broken.py diagnostics cleared', vscode.languages.getDiagnostics(vscode.Uri.file(broken)).length === 0);
  } catch (e) {
    check('suite crashed', false, String(e && e.stack || e));
  } finally {
    fs.writeFileSync(process.env.E2E_RESULT, JSON.stringify(results, null, 2));
  }
}

module.exports = { run };
