// Runs inside a real VS Code extension host with NO robot hardware: opens the
// simulator panel (revFtc.openSimulator), checks the webview loaded and gets
// state from a running Java sim, drives an OpMode through the same command
// path the Driver Hub buttons use, and checks that a Java exception thrown by
// the translated code lands as a Problem on the right Python line. Launched
// by test/e2e/runSim.mjs; results go to $E2E_RESULT.
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const results = [];
const check = (name, ok, detail) => results.push({ name, ok: !!ok, detail });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function until(fn, timeoutMs, stepMs = 250) {
  const end = Date.now() + timeoutMs;
  let last;
  while (Date.now() < end) {
    last = await fn();
    if (last && last.ok) return last;
    await sleep(stepMs);
  }
  return last || { ok: false };
}

const probe = (file) => vscode.commands.executeCommand('revFtc._simulatorProbe', file);
const send = (cmd) => vscode.commands.executeCommand('revFtc._simulatorSend', cmd);

async function run() {
  const ws = vscode.workspace.workspaceFolders[0].uri.fsPath;
  const opmode = path.join(ws, 'Bench.py');
  const expectedLine = Number(process.env.E2E_THROW_LINE);
  try {
    await vscode.commands.executeCommand('revFtc.openSimulator');
    const opened = await until(async () => {
      const p = await probe();
      return { ok: p.open && p.webviewReady, p };
    }, 30000);
    check('openSimulator opens the panel and its webview script runs (it posted "ready")', opened.ok, opened.p);

    const running = await until(async () => {
      const p = await probe();
      return { ok: p.running && p.counts && p.counts.state > 5 && p.ready, p };
    }, 180000, 500);
    check('the Java simulator started and streams state', running.ok, running.p && { status: running.p.lastStatus, counts: running.p.counts });
    const ready = running.p && running.p.ready;
    check('ready lists the OpMode and the configured devices',
      ready && ready.opModes.some((o) => o.name === 'Bench') && ready.devices.some((d) => d.name === 'frontLeft' && d.kind === 'motor'),
      ready && { opModes: ready.opModes, devices: ready.devices.map((d) => d.name) });

    const delivered0 = (await probe()).delivered;
    await sleep(1500);
    const delivered1 = (await probe()).delivered;
    check('state messages are delivered to the webview (postMessage resolved true)', delivered1 > delivered0 + 10, { delivered0, delivered1 });

    const env = (await probe()).env;
    check('the webview reported what the Gamepad API does inside VS Code', env && ['allowed', 'blocked', 'missing'].includes(env.gamepadApi), env);

    await send({ type: 'init', opMode: 'Bench' });
    await sleep(1000);
    await send({ type: 'start' });
    await send({ type: 'gamepad', index: 1, gamepadType: 'SONY_PS4', state: { left_stick_y: -1 } });
    const spinning = await until(async () => {
      const p = await probe();
      const m = p.lastState && p.lastState.devices && p.lastState.devices.frontLeft;
      return { ok: p.lastState && p.lastState.phase === 'running' && m && m.power > 0.9 && m.spin === 'CW', m };
    }, 20000);
    check('gamepad input reaches the running OpMode and the motor spins (CW, as the SDK commands it)', spinning.ok, spinning.m);
    if (process.env.E2E_HOLD_MS) {
      // Manual/visual runs only: keep the motor spinning so a screenshot can be taken.
      await vscode.commands.executeCommand('workbench.action.closeSidebar');
      await sleep(Number(process.env.E2E_HOLD_MS));
    }

    // --- Debug in the simulator: a breakpoint on a Python line stops the OpMode there ---
    const seen = [];
    vscode.debug.registerDebugAdapterTrackerFactory('revftc-sim', { createDebugAdapterTracker: () => ({ onDidSendMessage: (m) => seen.push(m) }) });
    const bpLine = Number(process.env.E2E_BP_LINE);
    vscode.debug.addBreakpoints([new vscode.SourceBreakpoint(new vscode.Location(vscode.Uri.file(opmode), new vscode.Position(bpLine - 1, 0)))]);
    const tabsBefore = vscode.window.tabGroups.all.map((g) => g.tabs.map((t) => `${g.viewColumn}:${t.label}:${t.isPreview ? 'preview' : 'pinned'}`));
    const started = await vscode.commands.executeCommand('revFtc.debugSimulator');
    const stopped = await until(async () => {
      const ev = seen.find((m) => m.type === 'event' && m.event === 'stopped');
      return { ok: !!ev, ev };
    }, 30000);
    let frameLine;
    let frameVars;
    let requestError;
    const st = await until(async () => {
      const r = seen.find((m) => m.type === 'response' && m.command === 'stackTrace' && m.success);
      return { ok: !!r, r };
    }, 15000);
    if (st.ok) {
      frameLine = st.r.body.stackFrames[0] && st.r.body.stackFrames[0].line;
      for (let attempt = 0; attempt < 5 && !frameVars; attempt++) {
        try {
          const sc = await vscode.debug.activeDebugSession.customRequest('scopes', { frameId: st.r.body.stackFrames[0].id });
          const vars = await vscode.debug.activeDebugSession.customRequest('variables', { variablesReference: sc.scopes[1].variablesReference });
          frameVars = vars.variables.map((v) => `${v.name}=${v.value}`);
        } catch (e) {
          requestError = String(e);
          await sleep(500);
        }
      }
    }
    await sleep(800);
    const heldProbe = await probe();
    const held = heldProbe.lastState;
    check('Debug in Simulator: the breakpoint on the Python line is hit, frames and OpMode fields are in Python terms, and sim time freezes',
      started && stopped.ok && frameLine === bpLine && frameVars && frameVars.some((v) => v.startsWith('drive=')) && held && held.debuggerHold === true,
      { started, frameLine, bpLine, frameVars, requestError, debuggerHold: held && held.debuggerHold, dap: seen.filter((m) => m.type !== 'response' || !m.success).slice(0, 8), all: seen.map((m) => m.command || m.event).join(','), exit: heldProbe.lastExit, stderr: heldProbe.stderrTail, open: heldProbe.open, tabsBefore, tabsAfter: vscode.window.tabGroups.all.map((g) => g.tabs.map((t) => `${g.viewColumn}:${t.label}:${t.isPreview}`)), running: heldProbe.running });
    vscode.debug.removeBreakpoints(vscode.debug.breakpoints);
    if (vscode.debug.activeDebugSession) await vscode.debug.stopDebugging(vscode.debug.activeDebugSession);
    await sleep(1000);

    await send({ type: 'gamepad', index: 1, gamepadType: 'SONY_PS4', state: { left_stick_y: -1, a: true } });
    const crashed = await until(async () => {
      const p = await probe(opmode);
      const d = (p.diagnostics || []).find((x) => /IllegalArgumentException/.test(x.message));
      return { ok: !!d, d, all: p.diagnostics };
    }, 20000);
    check('a Java exception in the OpMode becomes a Problem on the right Python line',
      crashed.ok && crashed.d.line === expectedLine && /"armm"/.test(crashed.d.message), { expectedLine, got: crashed.d, all: crashed.all });
    const fromApi = vscode.languages.getDiagnostics(vscode.Uri.file(opmode)).find((d) => d.source === 'pyftc-sim');
    check('the Problem is visible through the VS Code diagnostics API', fromApi && fromApi.range.start.line + 1 === expectedLine,
      fromApi && { line: fromApi.range.start.line + 1, message: fromApi.message });
  } catch (e) {
    check('suite crashed', false, String((e && e.stack) || e));
  } finally {
    fs.writeFileSync(process.env.E2E_RESULT, JSON.stringify(results, null, 2));
  }
}

module.exports = { run };
