// Thin wrapper around the revFtc.* settings (package.json contributes.configuration).
import * as vscode from 'vscode';

function cfg(): vscode.WorkspaceConfiguration {
  return vscode.workspace.getConfiguration('revFtc');
}

/** Empty string means "not set" for these - matches the string settings' defaults. */
function nonEmpty(v: string | undefined): string | undefined {
  return v && v.trim().length > 0 ? v.trim() : undefined;
}

export function hubUrl(): string | undefined {
  return nonEmpty(cfg().get<string>('hubUrl'));
}

export function adbPath(): string | undefined {
  return nonEmpty(cfg().get<string>('adbPath'));
}

export function pythonPath(): string | undefined {
  return nonEmpty(cfg().get<string>('pythonPath'));
}

/** Workspace-relative; "" means the workspace root. */
export function sourceRoot(): string {
  return cfg().get<string>('sourceRoot') ?? '';
}

/** Advanced override for the translator command (e.g. to point at the test
 * fixture); empty array means "use `<pythonPath> -m pyftc`". */
export function translatorCommand(): string[] {
  const v = cfg().get<string[]>('translatorCommand');
  return Array.isArray(v) ? v.filter((s) => s.length > 0) : [];
}

/** Master switch for running translate-project in the background (see
 * liveDiagnostics.ts). Default true. */
export function liveDiagnostics(): boolean {
  return cfg().get<boolean>('liveDiagnostics') ?? true;
}

/** 'save' (default): re-run only on save, debounced just enough to coalesce
 * a "Save All". 'edit': also re-run on a debounce while typing. */
export function liveDiagnosticsTrigger(): 'save' | 'edit' {
  return cfg().get<string>('liveDiagnosticsTrigger') === 'edit' ? 'edit' : 'save';
}

export function liveDiagnosticsDebounceMs(): number {
  const v = cfg().get<number>('liveDiagnosticsDebounceMs');
  return typeof v === 'number' && v >= 0 ? v : 750;
}

/** Master switch for watching the hub's active hardware configuration for
 * changes (configWatch.ts). Default true. Only gates the automatic checks
 * (on connect / sidebar refresh / before deploy) - the revFtc.updateFromConfig
 * command still works when run by hand regardless of this setting. */
export function configWatch(): boolean {
  return cfg().get<boolean>('configWatch') ?? true;
}
