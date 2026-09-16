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

export function disposeDiagnosticCollection(): void {
  collection?.dispose();
  collection = undefined;
}
