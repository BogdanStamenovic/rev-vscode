// revFtc.spawnStarterPack: connect -> rcInfo.json -> adb cat active config
// xml -> `pyftc starter` -> write <sourceRoot>/<Name>.py -> open it.
// Falls back to picking a config XML by hand when no hub is reachable at
// all (offline generation).
import * as vscode from 'vscode';
import * as path from 'node:path';
import { writeFile, readFile } from 'node:fs/promises';
import { HubUnreachableError } from '../hub/connection';
import { fetchHubConfigFiles } from '../hub/configFetch';
import { runPyftcJson } from '../cli';
import type { StarterResult } from '../pyftcContract';
import { resolveSourceRootDir } from '../workspaceRoot';
import { withTempDir } from '../tempDir';
import { ensureAutocomplete } from '../python/autocomplete';
import { log } from '../output';

const PY_IDENTIFIER_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;
const PY_KEYWORDS = new Set([
  'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
  'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in',
  'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
]);

function validateClassName(name: string): string | undefined {
  const trimmed = name.trim();
  if (trimmed.length === 0) {
    return 'Class name cannot be empty.';
  }
  if (!PY_IDENTIFIER_RE.test(trimmed)) {
    return 'Must be a valid Python identifier: letters, digits, underscore; cannot start with a digit.';
  }
  if (PY_KEYWORDS.has(trimmed)) {
    return `'${trimmed}' is a Python keyword.`;
  }
  return undefined;
}

async function promptClassName(): Promise<string | undefined> {
  return vscode.window.showInputBox({
    prompt: 'Starter OpMode class name',
    value: 'StarterPack',
    validateInput: validateClassName,
  });
}

async function generateFromHub(dir: string): Promise<{ config: string; rcinfo: string } | undefined> {
  const { configPath, rcinfoPath } = await fetchHubConfigFiles(dir);
  return { config: configPath, rcinfo: rcinfoPath };
}

/** Contract 3's `starter` subcommand requires --rcinfo as well as --config,
 * but when generating offline (no hub reachable) we have no rcInfo.json to
 * hand it. There is no offline-friendly variant in the contract, so we
 * synthesize a minimal placeholder rcInfo carrying only what a config-only
 * starter pack can know (the config's own file name as the active config
 * name); everything else is a clearly-fake placeholder. Flagged to the user
 * as a contract ambiguity - not something to silently paper over. */
async function generateOffline(dir: string): Promise<{ config: string; rcinfo: string } | undefined> {
  const picked = await vscode.window.showOpenDialog({
    canSelectMany: false,
    filters: { 'Config XML': ['xml'] },
    openLabel: 'Use as hardware config',
    title: 'Pick a config XML file',
  });
  if (!picked || picked.length === 0) {
    return undefined;
  }
  const configSrc = picked[0].fsPath;
  const configPath = path.join(dir, path.basename(configSrc));
  await writeFile(configPath, await readFile(configSrc, 'utf8'), 'utf8');

  const activeConfigName = path.basename(configSrc, path.extname(configSrc));
  const placeholderRcInfo = {
    activeConfigName,
    rcVersion: 'unknown (offline)',
    sdkVersion: 'unknown (offline)',
    deviceName: 'Offline Config',
    revHubNamesAndVersions: [] as unknown[],
  };
  const rcinfoPath = path.join(dir, 'rcInfo.json');
  await writeFile(rcinfoPath, JSON.stringify(placeholderRcInfo, null, 2), 'utf8');
  log('starter pack: generating offline with a synthesized placeholder rcInfo.json (no hub reachable)');
  return { config: configPath, rcinfo: rcinfoPath };
}

export async function runSpawnStarterPack(context?: vscode.ExtensionContext): Promise<void> {
  try {
    await withTempDir(async (dir) => {
      let inputs: { config: string; rcinfo: string } | undefined;
      try {
        inputs = await generateFromHub(dir);
      } catch (err) {
        const reachError = err instanceof HubUnreachableError;
        const message = err instanceof Error ? err.message : String(err);
        const choice = await vscode.window.showErrorMessage(
          reachError ? message : `REV FTC: ${message}`,
          'Pick a config XML file…'
        );
        if (choice !== 'Pick a config XML file…') {
          return;
        }
        inputs = await generateOffline(dir);
      }
      if (!inputs) {
        return;
      }

      const name = await promptClassName();
      if (!name) {
        return;
      }

      const outcome = await runPyftcJson<StarterResult>([
        'starter',
        '--config', inputs.config,
        '--rcinfo', inputs.rcinfo,
        '--name', name,
      ]);
      if (outcome.code !== 0 || !outcome.result?.ok) {
        vscode.window.showErrorMessage(
          `REV FTC: starter pack generation failed: ${outcome.stderr.trim() || 'unknown error'}`
        );
        return;
      }

      const sourceRootDir = resolveSourceRootDir();
      const targetUri = vscode.Uri.file(path.join(sourceRootDir, `${name}.py`));
      const exists = await vscode.workspace.fs.stat(targetUri).then(
        () => true,
        () => false
      );
      if (exists) {
        const overwrite = await vscode.window.showWarningMessage(
          `${name}.py already exists in the source root.`,
          { modal: true },
          'Overwrite'
        );
        if (overwrite !== 'Overwrite') {
          return;
        }
      }

      await vscode.workspace.fs.writeFile(targetUri, Buffer.from(outcome.result.python, 'utf8'));

      // Man page next to the .py, same name/folder, per the task brief -
      // it's the CLI's own `manual` field, not something we generate.
      const manualUri = vscode.Uri.file(path.join(sourceRootDir, `${name}.md`));
      await vscode.workspace.fs.writeFile(manualUri, Buffer.from(outcome.result.manual, 'utf8'));

      const doc = await vscode.workspace.openTextDocument(targetUri);
      await vscode.window.showTextDocument(doc);

      // A freshly spawned starter pack always imports ftc.* - this is the
      // "right after a starter pack is spawned" trigger for automatic
      // autocomplete wiring (python/autocomplete.ts), so users who skipped
      // (or never saw) the activation-time scan still get it without asking.
      if (context) {
        await ensureAutocomplete(context);
      }
    });
  } catch (err) {
    vscode.window.showErrorMessage(
      `REV FTC: spawn starter pack failed: ${err instanceof Error ? err.message : String(err)}`
    );
  }
}
