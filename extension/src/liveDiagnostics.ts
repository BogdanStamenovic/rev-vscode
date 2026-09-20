// Runs `pyftc translate-project` in the background so translation errors
// show up in the Problems panel before a deploy, not during one. Reuses
// translate.ts's translateProject() and applyTranslationDiagnostics() -
// the exact same call and diagnostic-population logic deploy.ts uses - so a
// live run and a deploy's own translate step can never disagree about what
// "clean" looks like.
//
// Concurrency (debounce / never-concurrent / cancel-and-supersede) is
// handled by debouncedRunner.ts, unit tested there in isolation. This file
// is just the vscode-facing wiring: which events schedule a run, and what a
// run actually does. Rules, restated where they matter here:
//  - On-save triggers coalesce within SAVE_DEBOUNCE_MS so a "Save All"
//    across several files runs translate-project once, not once per file.
//  - The optional on-edit trigger (revFtc.liveDiagnosticsTrigger) uses the
//    user-configurable revFtc.liveDiagnosticsDebounceMs instead, since
//    unlike a save it fires on every keystroke and must not compete with
//    typing.
//  - A run that CliAbortedError'd (killed by cli.ts because a newer trigger
//    superseded it) is expected and silent - no toast, no diagnostics write.
import * as vscode from 'vscode';
import { translateProject, applyTranslationDiagnostics, TranslatorError } from './translate';
import { CliAbortedError } from './cli';
import { DebouncedRunner } from './debouncedRunner';
import { getDiagnosticCollection, clearDiagnosticsForUri, clearDiagnosticsBySource } from './diagnostics';
import { resolveSourceRootDir } from './workspaceRoot';
import * as settingsMod from './settings';
import { log } from './output';

const SAVE_DEBOUNCE_MS = 250;
const TRANSLATION_DIAGNOSTIC_SOURCE = 'pyftc';

function isPython(doc: vscode.TextDocument): boolean {
  return doc.languageId === 'python';
}

export class LiveDiagnosticsController implements vscode.Disposable {
  private readonly disposables: vscode.Disposable[] = [];
  private readonly runner: DebouncedRunner;

  constructor() {
    this.runner = new DebouncedRunner((signal, generation) => this.runOnce(signal, generation), {
      onError: (err) => this.onRunError(err),
    });

    const watcher = vscode.workspace.createFileSystemWatcher('**/*.py');
    this.disposables.push(
      vscode.workspace.onDidSaveTextDocument((doc) => this.onSave(doc)),
      vscode.workspace.onDidChangeTextDocument((e) => this.onEdit(e.document)),
      vscode.workspace.onDidCloseTextDocument((doc) => this.onClose(doc)),
      vscode.workspace.onDidDeleteFiles((e) => this.onDeleteUris(e.files)),
      watcher,
      // workspace.onDidDeleteFiles only fires for deletions made through
      // VS Code's own file operations (Explorer, the workspace.fs API). An
      // external `rm` (terminal, git checkout) only shows up here.
      watcher.onDidDelete((uri) => this.onDeleteUris([uri]))
    );
  }

  private async runOnce(signal: AbortSignal, generation: number): Promise<void> {
    const root = resolveSourceRootDir();
    const result = await translateProject(root, signal);
    if (this.runner.currentGeneration() !== generation) {
      return; // superseded while the process was running
    }
    applyTranslationDiagnostics(getDiagnosticCollection(), result);
  }

  private onRunError(err: unknown): void {
    if (err instanceof CliAbortedError) {
      // Expected: aborted by a newer trigger, which already scheduled its
      // own run. Nothing to report.
      return;
    }
    if (err instanceof TranslatorError) {
      log(`live diagnostics: translator error: ${err.message}`);
      return;
    }
    // Includes "no workspace folder" from resolveSourceRootDir() - not worth
    // a toast for a background pass; the output channel has it.
    log(`live diagnostics: ${(err as Error).message}`);
  }

  private onSave(doc: vscode.TextDocument): void {
    if (!settingsMod.liveDiagnostics() || !isPython(doc)) {
      return;
    }
    this.runner.schedule(SAVE_DEBOUNCE_MS);
  }

  private onEdit(doc: vscode.TextDocument): void {
    if (!settingsMod.liveDiagnostics() || !isPython(doc)) {
      return;
    }
    if (settingsMod.liveDiagnosticsTrigger() !== 'edit') {
      return;
    }
    this.runner.schedule(settingsMod.liveDiagnosticsDebounceMs());
  }

  private onClose(doc: vscode.TextDocument): void {
    if (!isPython(doc)) {
      return;
    }
    // Drop only OUR diagnostics for the closed file; a 'pyftc-build' entry
    // from a real deploy is still true and stays until the next deploy.
    clearDiagnosticsBySource(doc.uri, TRANSLATION_DIAGNOSTIC_SOURCE);
  }

  private onDeleteUris(uris: readonly vscode.Uri[]): void {
    for (const uri of uris) {
      if (uri.fsPath.endsWith('.py')) {
        clearDiagnosticsForUri(uri);
      }
    }
  }

  dispose(): void {
    this.runner.dispose();
    for (const d of this.disposables) {
      d.dispose();
    }
  }
}
