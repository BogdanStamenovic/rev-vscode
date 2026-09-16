// revFtc.showGeneratedJava: translates just the active .py file and opens
// the generated Java in a read-only virtual document (pyftc-java: scheme),
// beside the editor - "users must be able to see exactly what goes to the
// robot" (spec). A .py file can yield more than one class (one entry per
// class per Contract 3); we open one tab per class.
import * as vscode from 'vscode';
import { translateFiles, TranslatorError } from '../translate';

export const SCHEME = 'pyftc-java';

export class GeneratedJavaProvider implements vscode.TextDocumentContentProvider {
  private readonly changeEmitter = new vscode.EventEmitter<vscode.Uri>();
  readonly onDidChange = this.changeEmitter.event;
  private readonly content = new Map<string, string>();

  set(uri: vscode.Uri, text: string): void {
    const isNew = !this.content.has(uri.toString());
    this.content.set(uri.toString(), text);
    if (!isNew) {
      this.changeEmitter.fire(uri);
    }
  }

  provideTextDocumentContent(uri: vscode.Uri): string {
    return this.content.get(uri.toString()) ?? '// no generated Java cached for this document';
  }
}

function javaUriFor(sourcePath: string, className: string): vscode.Uri {
  // Query carries the source path so re-running the command on the same
  // file updates the same virtual document instead of piling up tabs.
  return vscode.Uri.parse(`${SCHEME}:/${className}.java?src=${encodeURIComponent(sourcePath)}`);
}

export async function runShowGeneratedJava(provider: GeneratedJavaProvider): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'python') {
    vscode.window.showWarningMessage('REV FTC: open a .py OpMode file first.');
    return;
  }

  const sourcePath = editor.document.uri.fsPath;
  if (editor.document.isDirty) {
    await editor.document.save();
  }

  try {
    const result = await translateFiles([sourcePath]);
    const classes = result.files.filter((f) => f.source === sourcePath);
    if (classes.length === 0) {
      const hasErrors = [...result.diagnostics, ...result.files.flatMap((f) => f.diagnostics)].some(
        (d) => d.severity === 'error'
      );
      vscode.window.showWarningMessage(
        hasErrors
          ? 'REV FTC: this file has translation errors — see the Problems panel.'
          : 'REV FTC: no OpMode class found in this file.'
      );
      return;
    }

    for (const cls of classes) {
      const uri = javaUriFor(sourcePath, cls.className);
      provider.set(uri, cls.java);
      const doc = await vscode.workspace.openTextDocument(uri);
      await vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside, preview: false });
    }
  } catch (err) {
    const message = err instanceof TranslatorError ? err.message : err instanceof Error ? err.message : String(err);
    vscode.window.showErrorMessage(`REV FTC: could not generate Java: ${message}`);
  }
}
