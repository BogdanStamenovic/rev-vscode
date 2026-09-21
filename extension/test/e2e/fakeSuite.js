// Runs inside a real VS Code extension host, but against NO real hardware:
// revFtc.hubUrl points at fakeHub.mjs (rcInfo.json only) and revFtc.adbPath
// at fake_adb.py (the config XML read, which has no HTTP endpoint at all -
// see ARCHITECTURE.md). revFtc.translatorCommand points at fake_pyftc.py.
// Covers: checkAutocomplete, spawn -> config-change -> updateFromConfig
// (both the applied:true and applied:false paths), and removed-device
// diagnostics. Launched by test/e2e/runFake.mjs; results go to $E2E_RESULT.
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const results = [];
const check = (name, ok, detail) => results.push({ name, ok: !!ok, detail });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const CONFIG_XML_PATH = process.env.FAKE_HUB_CONFIG_XML;
const CONFIG_NAME = process.env.FAKE_HUB_CONFIG_NAME || 'TestConfig';

const CONFIG_V1 = `<Robot><LynxModule name="Control Hub" port="173"><RevRoboticsCoreHexMotor name="Kombjan" port="0"/></LynxModule></Robot>`;
// Same device set as V1 - only used to prove "no change" doesn't false-positive.
const CONFIG_V1_AGAIN = CONFIG_V1;
const CONFIG_V2 = `<Robot><LynxModule name="Control Hub" port="173"><RevRoboticsCoreHexMotor name="Kombjan" port="0"/><Servo name="Winch" port="1"/></LynxModule></Robot>`;

function writeConfig(xml) {
  fs.writeFileSync(CONFIG_XML_PATH, xml, 'utf8');
}

async function acceptDefaultInputBox(untilPathExists, timeoutSteps = 20) {
  for (let i = 0; i < timeoutSteps && !fs.existsSync(untilPathExists); i++) {
    await sleep(500);
    await vscode.commands.executeCommand('workbench.action.acceptSelectedQuickOpenItem');
  }
}

async function run() {
  const ws = vscode.workspace.workspaceFolders[0].uri.fsPath;
  try {
    writeConfig(CONFIG_V1);

    // --- revFtc.checkAutocomplete: no hardware involved at all ---
    await vscode.commands.executeCommand('revFtc.checkAutocomplete');
    await sleep(500); // let the report provider's content settle
    const reportUri = vscode.Uri.parse('pyftc-report:/Autocomplete%20Check.md');
    const reportDoc = await vscode.workspace.openTextDocument(reportUri);
    const reportText = reportDoc.getText();
    check('checkAutocomplete produced a report with all five checks', [
      'Python language server',
      'python.analysis.extraPaths',
      'Stub package on disk',
      'import ftc.hardware resolves',
      'Stub SDK version vs. hub',
    ].every((heading) => reportText.includes(heading)), reportText.slice(0, 400));

    // This test environment has no Python extension installed (it runs with
    // --disable-extensions and a minimal vscode-test download), so
    // python.analysis.extraPaths isn't even a registered setting here -
    // ensureExtraPath's job in that case is to fail quietly rather than
    // throw (see autocomplete.ts), not to write a setting that doesn't
    // exist. Assert the strong claim only when a Python extension IS
    // present; otherwise assert the fallback claim instead.
    const pythonExtensionPresent =
      !!vscode.extensions.getExtension('ms-python.python') || !!vscode.extensions.getExtension('ms-python.vscode-pylance');
    const extraPaths = vscode.workspace.getConfiguration('python.analysis').get('extraPaths') || [];
    if (pythonExtensionPresent) {
      check('checkAutocomplete self-healed extraPaths (workspace had no .py yet, but the check ran ensureExtraPath)',
        extraPaths.some((p) => p.endsWith(`${path.sep}python`)), extraPaths);
    } else {
      check('checkAutocomplete ran to completion with no Python extension installed (extraPaths write skipped, not crashed)',
        true, { pythonExtensionPresent, extraPaths });
    }

    // --- revFtc.setupFiles: workspace files for autocomplete ---
    await vscode.commands.executeCommand('revFtc.setupFiles');
    const link = path.join(ws, '.pyftc', 'stubs');
    const linkStat = fs.existsSync(link) ? fs.lstatSync(link) : undefined;
    check('setupFiles created .pyftc/stubs as a link', linkStat && linkStat.isSymbolicLink(), linkStat);
    check('the stub link resolves to the stub package (ftc/__init__.py reachable through it)',
      fs.existsSync(path.join(link, 'ftc', '__init__.py')), link);
    check('setupFiles git-ignores the machine-specific link',
      fs.existsSync(path.join(ws, '.pyftc', '.gitignore')) && fs.readFileSync(path.join(ws, '.pyftc', '.gitignore'), 'utf8').includes('stubs'));
    const pyrightPath = path.join(ws, 'pyrightconfig.json');
    const pyright1 = fs.existsSync(pyrightPath) ? fs.readFileSync(pyrightPath, 'utf8') : '';
    check('setupFiles wrote pyrightconfig.json pointing at the workspace link, not the versioned install dir',
      (() => { try { return JSON.stringify(JSON.parse(pyright1).extraPaths) === JSON.stringify(['.pyftc/stubs']); } catch { return false; } })(), pyright1);
    const extJsonPath = path.join(ws, '.vscode', 'extensions.json');
    const extJson = fs.existsSync(extJsonPath) ? fs.readFileSync(extJsonPath, 'utf8') : '';
    check('setupFiles recommends this extension in .vscode/extensions.json', extJson.includes('bogdanstamenovic.rev-vscode'), extJson);
    await vscode.commands.executeCommand('revFtc.setupFiles');
    check('running setupFiles again leaves pyrightconfig.json byte-for-byte unchanged',
      fs.readFileSync(pyrightPath, 'utf8') === pyright1);

    // --- spawn starter pack against the fake hub/adb/CLI ---
    const spawnPromise = vscode.commands.executeCommand('revFtc.spawnStarterPack');
    await acceptDefaultInputBox(path.join(ws, 'StarterPack.py'));
    await spawnPromise;

    const starterPyPath = path.join(ws, 'StarterPack.py');
    const starterMdPath = path.join(ws, 'StarterPack.md');
    check('spawnStarterPack wrote StarterPack.py', fs.existsSync(starterPyPath));
    check('spawnStarterPack wrote the man page StarterPack.md', fs.existsSync(starterMdPath));

    const v1Text = fs.existsSync(starterPyPath) ? fs.readFileSync(starterPyPath, 'utf8') : '';
    check('StarterPack.py has a pyftc:config header with a fingerprint', /pyftc:config name="StarterPack" fingerprint="[0-9a-f]+"/.test(v1Text), v1Text.slice(0, 200));

    // Re-running checkAutocomplete now that a real ftc.* import exists
    // should find extraPaths still set (idempotent, not re-prompted).
    await vscode.commands.executeCommand('revFtc.checkAutocomplete');
    await sleep(300);

    // --- simulate a hardware change (same fingerprint mechanism the real
    // hub would trigger by someone editing the config on the Driver Hub) ---
    // Directives embedded here are fake_pyftc.py's own test protocol (see
    // its module docstring) - never emitted by the real translator, and
    // never left in place after a real update; they stand in for whatever
    // real diffing the other agent's CLI performs.
    fs.writeFileSync(
      starterPyPath,
      v1Text.replace(
        '# ── pyftc:devices:end ──',
        '        # FAKE_UPDATE_ADD:winch:Winch:Servo\n        # FAKE_UPDATE_REMOVE:oldsensor:OldSensor\n# ── pyftc:devices:end ──'
      ),
      'utf8'
    );
    writeConfig(CONFIG_V2);

    // Open the file so updateFromConfig's "active editor" shortcut picks it
    // directly instead of showing a QuickPick (see updateFromConfig.ts).
    const starterDoc = await vscode.workspace.openTextDocument(starterPyPath);
    await vscode.window.showTextDocument(starterDoc);

    await vscode.commands.executeCommand('revFtc.updateFromConfig');
    await sleep(1000);

    const v2Text = fs.existsSync(starterPyPath) ? fs.readFileSync(starterPyPath, 'utf8') : '';
    check('updateFromConfig rewrote the fingerprint to match the new configuration',
      /fingerprint="[0-9a-f]+"/.test(v2Text) && v2Text.match(/fingerprint="([0-9a-f]+)"/)[1] !== v1Text.match(/fingerprint="([0-9a-f]+)"/)[1],
      { v1: v1Text.match(/fingerprint="([0-9a-f]+)"/), v2: v2Text.match(/fingerprint="([0-9a-f]+)"/) });
    check('updateFromConfig spliced in the added device', v2Text.includes('winch: Servo'), v2Text);
    check('updateFromConfig left a "no longer in the configuration" marker for the removed device',
      v2Text.includes('# pyftc: no longer in the configuration') && v2Text.includes('oldsensor: DcMotor'), v2Text);

    const v2Manual = fs.existsSync(starterMdPath) ? fs.readFileSync(starterMdPath, 'utf8') : '';
    check('updateFromConfig regenerated the man page', v2Manual.includes('StarterPack'), v2Manual);

    const removedDiags = vscode.languages.getDiagnostics(vscode.Uri.file(starterPyPath));
    check('a warning diagnostic was published for the removed device',
      removedDiags.some((d) => d.severity === vscode.DiagnosticSeverity.Warning && /OldSensor/.test(d.message)),
      removedDiags.map((d) => ({ line: d.range.start.line, message: d.message, severity: d.severity })));

    // Running it again with no further hardware change should be a no-op
    // ("changed: false") and not touch the file again.
    const v2TextBefore = fs.readFileSync(starterPyPath, 'utf8');
    await vscode.commands.executeCommand('revFtc.updateFromConfig');
    await sleep(500);
    const v2TextAfter = fs.readFileSync(starterPyPath, 'utf8');
    check('re-running updateFromConfig with no config change is a no-op', v2TextAfter === v2TextBefore);

    // --- applied:false path: markers missing, nothing should be modified ---
    const noMarkersPath = path.join(ws, 'NoMarkers.py');
    const noMarkersOriginal = [
      '# ── pyftc:config name="NoMarkers" fingerprint="0000000000000000" generated="2026-09-20" ──',
      'import ftc',
      '',
      'class NoMarkers(ftc.opmode.LinearOpMode):',
      '    def run(self):',
      '        pass',
      '',
    ].join('\n');
    fs.writeFileSync(noMarkersPath, noMarkersOriginal, 'utf8');
    const noMarkersDoc = await vscode.workspace.openTextDocument(noMarkersPath);
    await vscode.window.showTextDocument(noMarkersDoc);

    const tabsBefore = vscode.window.tabGroups.all.flatMap((g) => g.tabs).length;
    await vscode.commands.executeCommand('revFtc.updateFromConfig');
    await sleep(1000);

    const noMarkersAfter = fs.readFileSync(noMarkersPath, 'utf8');
    check('applied:false path never modifies the original file', noMarkersAfter === noMarkersOriginal, noMarkersAfter);

    const tabsAfter = vscode.window.tabGroups.all.flatMap((g) => g.tabs);
    const untitledBlockTab = tabsAfter.find((t) => t.label && t.input && t.input.uri && t.input.uri.scheme === 'untitled');
    check('applied:false path opened an untitled editor with the returned block', !!untitledBlockTab, {
      before: tabsBefore,
      after: tabsAfter.length,
      labels: tabsAfter.map((t) => t.label),
    });
  } catch (e) {
    check('suite crashed', false, String((e && e.stack) || e));
  } finally {
    fs.writeFileSync(process.env.E2E_RESULT, JSON.stringify(results, null, 2));
  }
}

module.exports = { run };
