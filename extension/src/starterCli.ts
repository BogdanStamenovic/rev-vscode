// Thin wrappers around the three Contract 3 subcommands that back
// hardware-configuration change detection: `config-fingerprint`,
// `starter-update`, and `manual`. Mirrors translate.ts's shape (a `run`
// helper that turns the CliOutcome into either a parsed result or a thrown
// error) rather than reusing translate.ts itself, since these are a
// different subcommand family with a different exit-code story: all three
// only ever mean "ok" (exit 0) or "usage/internal error" (message on
// stderr) - there is no Contract-3 "exit 1 = user code errors" case for
// them the way there is for translate-project.
import { runPyftcJson } from './cli';
import type { ConfigFingerprintResult, ManualResult, StarterUpdateResult } from './pyftcContract';

export class PyftcCommandError extends Error {}

async function run<T>(args: string[]): Promise<T> {
  const outcome = await runPyftcJson<T>(args);
  if (outcome.code === 0) {
    if (!outcome.result) {
      throw new PyftcCommandError('pyftc printed no parseable result');
    }
    return outcome.result;
  }
  throw new PyftcCommandError(outcome.stderr.trim() || `pyftc exited with code ${outcome.code}`);
}

export function configFingerprint(configPath: string): Promise<ConfigFingerprintResult> {
  return run<ConfigFingerprintResult>(['config-fingerprint', '--config', configPath]);
}

export function starterUpdate(filePath: string, configPath: string, rcinfoPath: string): Promise<StarterUpdateResult> {
  return run<StarterUpdateResult>([
    'starter-update',
    '--file', filePath,
    '--config', configPath,
    '--rcinfo', rcinfoPath,
  ]);
}

export function regenerateManual(configPath: string, rcinfoPath: string, name: string): Promise<ManualResult> {
  return run<ManualResult>(['manual', '--config', configPath, '--rcinfo', rcinfoPath, '--name', name]);
}
