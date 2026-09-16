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
