// revFtc.setupFiles: makes a folder ready for writing robot code - the stub
// link, pyrightconfig.json, .vscode settings and extension recommendations,
// a checked Python interpreter, and a language server. Idempotent: every
// step merges into what is there, and a second run reports "unchanged".
import * as vscode from 'vscode';
import * as path from 'node:path';
import { spawn } from 'node:child_process';
import { lstat, mkdir, readFile, readlink, symlink, unlink, writeFile } from 'node:fs/promises';
import { resolvePythonPath } from '../cli';
import { stubDirFor } from '../python/ftcImportDetect';
import {
  STUB_LINK_REL,
  UnparseableJsonError,
  mergeExtensionsJson,
  mergeExtraPaths,
  mergePyrightConfig,
  parsePythonProbe,
  pythonIsNewEnough,
  recommendedExtensions,
  MIN_PYTHON,
} from '../python/workspaceSetup';
import { hostKind, languageServerStatus, offerLanguageServerInstall } from './checkAutocomplete';
import { getOutputChannel, log } from '../output';

type Outcome = 'created' | 'updated' | 'unchanged' | 'skipped' | 'failed';

interface Step {
  what: string;
  outcome: Outcome;
  detail?: string;
}

async function readIfExists(file: string): Promise<string | undefined> {
  try {
    return await readFile(file, 'utf8');
  } catch {
    return undefined;
  }
}

/** Points <root>/.pyftc/stubs at this install's stub directory. A junction
 * on Windows, since a real symlink there needs admin rights; the argument is
 * ignored elsewhere. Only ever replaces a link: a real directory at that path
 * is somebody's data and is reported, not deleted. */
export async function ensureStubLink(root: string, stubDir: string): Promise<Step> {
  const link = path.join(root, STUB_LINK_REL);
  const dir = path.dirname(link);
  await mkdir(dir, { recursive: true });
  const ignore = path.join(dir, '.gitignore');
  if ((await readIfExists(ignore)) === undefined) {
    // The link target is a path on this machine; committing it helps nobody.
    await writeFile(ignore, 'stubs\n', 'utf8');
  }

  let existing: Awaited<ReturnType<typeof lstat>> | undefined;
  try {
    existing = await lstat(link);
  } catch {
    existing = undefined;
  }
  if (existing && !existing.isSymbolicLink()) {
    return { what: STUB_LINK_REL, outcome: 'failed', detail: 'exists and is not a link; move it aside and run Setup Files again' };
  }
  if (existing) {
    if (path.resolve(dir, await readlink(link)) === path.resolve(stubDir)) {
      return { what: STUB_LINK_REL, outcome: 'unchanged' };
    }
    await unlink(link);
  }
  await symlink(stubDir, link, 'junction');
  return { what: STUB_LINK_REL, outcome: existing ? 'updated' : 'created', detail: `-> ${stubDir}` };
}

async function writeMerged(
  file: string,
  label: string,
  merge: (existing: string | undefined) => { text: string; changed: boolean }
): Promise<Step> {
  const existing = await readIfExists(file);
  try {
    const { text, changed } = merge(existing);
    if (!changed) {
      return { what: label, outcome: 'unchanged' };
    }
    await mkdir(path.dirname(file), { recursive: true });
    await writeFile(file, text, 'utf8');
    return { what: label, outcome: existing === undefined ? 'created' : 'updated' };
  } catch (err) {
    if (err instanceof UnparseableJsonError) {
      return { what: label, outcome: 'skipped', detail: err.message };
    }
    throw err;
  }
}

/** Writes extraPaths under a settings section through the configuration API,
 * which preserves comments in settings.json. The section only exists when the
 * matching extension is installed; update() throws otherwise, which is fine:
 * pyrightconfig.json already covers every language server. */
async function mergeSetting(section: string, stubDir: string): Promise<Step> {
  const label = `.vscode/settings.json: ${section}.extraPaths`;
  const config = vscode.workspace.getConfiguration(section);
  const current = config.inspect<string[]>('extraPaths')?.workspaceValue ?? [];
  const { value, changed } = mergeExtraPaths(current, stubDir);
  if (!changed) {
    return { what: label, outcome: 'unchanged' };
  }
  try {
    await config.update('extraPaths', value, vscode.ConfigurationTarget.Workspace);
    return { what: label, outcome: current.length ? 'updated' : 'created' };
  } catch {
    return { what: label, outcome: 'skipped', detail: 'setting not registered (its extension is not installed); pyrightconfig.json covers it' };
  }
}

function runProbe(python: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(python, ['-c', 'import sys; print(sys.executable); print("%d.%d" % sys.version_info[:2])']);
    let out = '';
    child.stdout.on('data', (d) => (out += d.toString()));
    child.on('error', reject);
    child.on('exit', (code) => (code === 0 ? resolve(out) : reject(new Error(`exited with ${code}`))));
  });
}

/** The translator needs Python >= 3.10 and nothing else (stdlib only), so
 * there is no venv to create. What the Python extension does want is an
 * interpreter it considers selected, or it nags on every .py file. */
async function checkPython(): Promise<Step> {
  const need = `${MIN_PYTHON[0]}.${MIN_PYTHON[1]}`;
  let probe: ReturnType<typeof parsePythonProbe>;
  try {
    probe = parsePythonProbe(await runProbe(await resolvePythonPath()));
  } catch (err) {
    return {
      what: 'Python interpreter',
      outcome: 'failed',
      detail: `none found (${(err as Error).message}). Install Python ${need}+ and run Setup Files again, or set revFtc.pythonPath`,
    };
  }
  if (!probe) {
    return { what: 'Python interpreter', outcome: 'failed', detail: 'could not read its version' };
  }
  const version = `${probe.major}.${probe.minor}`;
  if (!pythonIsNewEnough(probe.major, probe.minor)) {
    return { what: 'Python interpreter', outcome: 'failed', detail: `${probe.executable} is ${version}; the translator needs ${need}+` };
  }
  if (vscode.extensions.getExtension('ms-python.python')) {
    const config = vscode.workspace.getConfiguration('python');
    if (!config.inspect<string>('defaultInterpreterPath')?.workspaceValue) {
      await config.update('defaultInterpreterPath', probe.executable, vscode.ConfigurationTarget.Workspace);
      return { what: 'Python interpreter', outcome: 'updated', detail: `${probe.executable} (${version}) selected for the Python extension` };
    }
  }
  return { what: 'Python interpreter', outcome: 'unchanged', detail: `${probe.executable} (${version})` };
}

function workspaceRoot(): string | undefined {
  return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
}

export async function runSetupFiles(context: vscode.ExtensionContext): Promise<void> {
  const root = workspaceRoot();
  if (!root) {
    void vscode.window.showErrorMessage('REV FTC: open the folder with your robot code first, then run Setup Files.');
    return;
  }
  const stubDir = stubDirFor(context.extensionPath);
  const host = hostKind(vscode.env.appName);
  const steps: Step[] = [];
  const attempt = async (what: string, fn: () => Promise<Step>) => {
    try {
      steps.push(await fn());
    } catch (err) {
      steps.push({ what, outcome: 'failed', detail: (err as Error).message });
    }
  };

  await attempt(STUB_LINK_REL, () => ensureStubLink(root, stubDir));
  await attempt('pyrightconfig.json', () =>
    writeMerged(path.join(root, 'pyrightconfig.json'), 'pyrightconfig.json', (t) => mergePyrightConfig(t, stubDir))
  );
  await attempt('python.analysis', () => mergeSetting('python.analysis', stubDir));
  await attempt('basedpyright.analysis', () => mergeSetting('basedpyright.analysis', stubDir));
  await attempt('.vscode/extensions.json', () =>
    writeMerged(path.join(root, '.vscode', 'extensions.json'), '.vscode/extensions.json', (t) =>
      mergeExtensionsJson(t, recommendedExtensions(host))
    )
  );
  await attempt('Python interpreter', () => checkPython());

  const server = languageServerStatus();
  steps.push(
    server.active
      ? { what: 'Language server', outcome: 'unchanged', detail: server.name }
      : { what: 'Language server', outcome: 'failed', detail: 'none installed, so nothing will autocomplete' }
  );

  const out = getOutputChannel();
  out.appendLine(`Setup Files in ${root}:`);
  for (const s of steps) {
    out.appendLine(`  ${s.outcome.padEnd(9)} ${s.what}${s.detail ? ` - ${s.detail}` : ''}`);
  }
  log(`setupFiles: ${steps.map((s) => `${s.what}=${s.outcome}`).join(', ')}`);

  // Neither prompt is awaited: the command itself is done once the files
  // are written, and a notification nobody answers must not hang it.
  if (!server.active) {
    void offerLanguageServerInstall(host);
  }

  const failed = steps.filter((s) => s.outcome === 'failed');
  const changed = steps.filter((s) => s.outcome === 'created' || s.outcome === 'updated').length;
  const summary = failed.length
    ? `REV FTC: setup finished with ${failed.length} problem(s): ${failed.map((s) => s.what).join(', ')}.`
    : changed
      ? `REV FTC: workspace set up (${changed} change(s)). Autocomplete should work in a few seconds.`
      : 'REV FTC: workspace was already set up; nothing changed.';
  const show = failed.length ? vscode.window.showWarningMessage : vscode.window.showInformationMessage;
  void show(summary, 'Show details', 'Check autocomplete').then((choice) => {
    if (choice === 'Show details') {
      out.show(true);
    } else if (choice === 'Check autocomplete') {
      void vscode.commands.executeCommand('revFtc.checkAutocomplete');
    }
  });
}

/** Activation-time: an extension update moves the install directory, so a
 * workspace that already ran Setup Files gets its link re-pointed silently.
 * Workspaces that never ran it are left alone. */
export async function refreshStubLink(context: vscode.ExtensionContext): Promise<void> {
  const root = workspaceRoot();
  if (!root) {
    return;
  }
  try {
    if (!(await lstat(path.join(root, STUB_LINK_REL))).isSymbolicLink()) {
      return;
    }
  } catch {
    return;
  }
  const step = await ensureStubLink(root, stubDirFor(context.extensionPath)).catch((err: Error) => ({
    what: STUB_LINK_REL,
    outcome: 'failed' as const,
    detail: err.message,
  }));
  if (step.outcome !== 'unchanged') {
    log(`setupFiles: refreshed ${STUB_LINK_REL}: ${step.outcome}${step.detail ? ` ${step.detail}` : ''}`);
  }
}

/** True once Setup Files has run here; autocomplete.ts then stops writing
 * the absolute, version-specific stub path into settings. */
export async function workspaceIsSetUp(): Promise<boolean> {
  const root = workspaceRoot();
  if (!root) {
    return false;
  }
  try {
    return (await lstat(path.join(root, STUB_LINK_REL))).isSymbolicLink();
  } catch {
    return false;
  }
}
