// Single shared DiagnosticCollection for .py files: translation diagnostics
// (from pyftc) and, after a failed build, javac errors mapped back through
// lineMap. Both deploy.ts and showGeneratedJava.ts read/write this.
import * as vscode from 'vscode';

let collection: vscode.DiagnosticCollection | undefined;

export function getDiagnosticCollection(): vscode.DiagnosticCollection {
  if (!collection) {
    collection = vscode.languages.createDiagnosticCollection('revFtc');
  }
  return collection;
}

export function addDiagnostics(uri: vscode.Uri, diags: vscode.Diagnostic[]): void {
  const c = getDiagnosticCollection();
  const existing = c.get(uri) ?? [];
  c.set(uri, [...existing, ...diags]);
}

/** Drops every diagnostic for a file regardless of source - used when a .py
 * file is deleted (live diagnostics and any stale build errors both stop
 * meaning anything). */
export function clearDiagnosticsForUri(uri: vscode.Uri): void {
  getDiagnosticCollection().delete(uri);
}

/** Drops only the diagnostics tagged with `source` (e.g. 'pyftc' for live
 * translation diagnostics), leaving diagnostics from other sources (e.g.
 * 'pyftc-build', set by a real deploy) untouched. Used when a file is closed:
 * a live preview diagnostic stops being interesting once you're not looking
 * at the file, but a real build failure from the last deploy is still true
 * and should stay in the Problems panel until the next deploy fixes it. */
export function clearDiagnosticsBySource(uri: vscode.Uri, source: string): void {
  const c = getDiagnosticCollection();
  const existing = c.get(uri) ?? [];
  const kept = existing.filter((d) => d.source !== source);
  if (kept.length === existing.length) {
    return;
  }
  if (kept.length === 0) {
    c.delete(uri);
  } else {
    c.set(uri, kept);
  }
}

export function disposeDiagnosticCollection(): void {
  collection?.dispose();
  collection = undefined;
}
