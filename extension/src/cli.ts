// Spawns `python -m pyftc ...` (Contract 3), or the revFtc.translatorCommand
// override used by the fake CLI fixture in tests. stdout is JSON-only per
// the contract; stderr carries the message for exit code 2 (usage/internal
// error). PYTHONPATH is extended so `import ftc...` resolves against the
// stub package bundled at <extensionPath>/python.
import { spawn } from 'node:child_process';
import * as path from 'node:path';
import * as settingsMod from './settings';
import { logCli } from './output';

let extensionPath: string | undefined;

/** Must be called once during activate(). */
export function setExtensionPath(p: string): void {
  extensionPath = p;
}

function requireExtensionPath(): string {
  if (!extensionPath) {
    throw new Error('cli.setExtensionPath() was not called before use');
  }
  return extensionPath;
}

async function isOnPath(bin: string): Promise<boolean> {
  return new Promise((resolve) => {
    const child = spawn(bin, ['--version']);
    child.on('error', () => resolve(false));
    child.on('exit', (code) => resolve(code === 0));
  });
}

let cachedPythonPath: string | undefined;

export async function resolvePythonPath(): Promise<string> {
  if (cachedPythonPath) {
    return cachedPythonPath;
  }
  const setting = settingsMod.pythonPath();
  if (setting) {
    cachedPythonPath = setting;
    return setting;
  }
  if (await isOnPath('python3')) {
    cachedPythonPath = 'python3';
    return 'python3';
  }
  if (await isOnPath('python')) {
    cachedPythonPath = 'python';
    return 'python';
  }
  throw new Error("Could not find a Python interpreter. Set 'revFtc.pythonPath'.");
}

async function buildCommand(): Promise<string[]> {
  const override = settingsMod.translatorCommand();
  if (override.length > 0) {
    return override;
  }
  const python = await resolvePythonPath();
  return [python, '-m', 'pyftc'];
}

/** Thrown when a caller-supplied AbortSignal killed the process before it
 * exited on its own - used by live diagnostics (liveDiagnostics.ts) to tell
 * "superseded by a newer run" apart from a real translator failure, so a
 * cancelled background run never surfaces as an error toast or wipes
 * diagnostics that the newer run hasn't replaced yet. */
export class CliAbortedError extends Error {
  constructor() {
    super('pyftc process was aborted (superseded by a newer request)');
    this.name = 'CliAbortedError';
  }
}

interface SpawnCollectResult {
  stdout: string;
  stderr: string;
  code: number | null;
}

function spawnCollect(command: string[], env: NodeJS.ProcessEnv, signal?: AbortSignal): Promise<SpawnCollectResult> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new CliAbortedError());
      return;
    }
    const child = spawn(command[0], command.slice(1), { env });
    let stdout = '';
    let stderr = '';
    let aborted = false;
    const onAbort = () => {
      aborted = true;
      child.kill('SIGTERM');
    };
    signal?.addEventListener('abort', onAbort);
    const cleanup = () => signal?.removeEventListener('abort', onAbort);

    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('error', (err) => {
      cleanup();
      if (aborted) {
        reject(new CliAbortedError());
      } else if (isEnoent(err)) {
        reject(new Error(`Could not run '${command[0]}': ${err.message}`));
      } else {
        reject(err);
      }
    });
    child.on('exit', (code) => {
      cleanup();
      if (aborted) {
        reject(new CliAbortedError());
        return;
      }
      resolve({ stdout, stderr, code });
    });
  });
}

function isEnoent(err: unknown): boolean {
  return typeof err === 'object' && err !== null && (err as { code?: string }).code === 'ENOENT';
}

export interface CliOutcome<T> {
  /** 0 = ok, 1 = user code errors (result is still populated), 2/other = usage/internal error. */
  code: number;
  result?: T;
  stderr: string;
}

export async function runPyftcJson<T>(args: string[], signal?: AbortSignal): Promise<CliOutcome<T>> {
  const base = await buildCommand();
  const full = [...base, ...args];
  logCli(full);

  const extPythonDir = path.join(requireExtensionPath(), 'python');
  const env: NodeJS.ProcessEnv = {
    ...process.env,
    PYTHONPATH: process.env.PYTHONPATH ? `${extPythonDir}${path.delimiter}${process.env.PYTHONPATH}` : extPythonDir,
  };

  const { stdout, stderr, code } = await spawnCollect(full, env, signal);

  if (code === 0 || code === 1) {
    try {
      const result = JSON.parse(stdout) as T;
      return { code, result, stderr };
    } catch (err) {
      throw new Error(
        `pyftc produced non-JSON stdout on exit ${code}: ${(err as Error).message}\n---stdout---\n${stdout.slice(0, 2000)}`
      );
    }
  }

  return { code: code ?? -1, stderr };
}
