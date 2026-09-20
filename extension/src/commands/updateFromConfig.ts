// revFtc.updateFromConfig: runs `pyftc starter-update` for one or more
// generated starter-pack files whose fingerprint no longer matches the
// hub's active hardware configuration. Triggered either from the
// "Add new hardware" action on configWatch.ts's notification, or by hand
// from the command palette / sidebar - either way, running the command IS
// the user's confirmation (per the task brief's "never surprise-write a
// file"); there is no second modal on top of that.
import * as vscode from 'vscode';
import * as path from 'node:path';
import { withTempDir } from '../tempDir';
import { fetchHubConfigFiles } from '../hub/configFetch';
import { scanForConfigChanges } from '../hub/configWatch';
import { starterUpdate } from '../starterCli';
import { buildRemovedDiagnostics } from '../hub/configHeader';
import { getDiagnosticCollection, clearDiagnosticsBySource } from '../diagnostics';
import { log } from '../output';

const DIAGNOSTIC_SOURCE = 'pyftc-config';

interface PickItem extends vscode.QuickPickItem {
  uri: vscode.Uri;
}

async function pickFiles(stale: Array<{ uri: vscode.Uri; name: string }>): Promise<vscode.Uri[] | undefined> {
  const activeUri = vscode.window.activeTextEditor?.document.uri.toString();
  const activeMatch = stale.find((s) => s.uri.toString() === activeUri);
  if (activeMatch) {
    return [activeMatch.uri];
  }
  if (stale.length === 1) {
    return [stale[0].uri];
  }

  const items: PickItem[] = stale.map((s) => ({
    label: path.basename(s.uri.fsPath),
    description: s.name,
    detail: s.uri.fsPath,
    uri: s.uri,
    picked: true,
  }));
  const picked = await vscode.window.showQuickPick(items, {
    canPickMany: true,
    title: 'Update from hardware configuration',
    placeHolder: 'Select the generated starter pack(s) to update',
  });
  return picked?.map((p) => p.uri);
}

async function applyUpdateToFile(uri: vscode.Uri): Promise<void> {
  await withTempDir(async (dir) => {
    const { configPath, rcinfoPath } = await fetchHubConfigFiles(dir);
    const result = await starterUpdate(uri.fsPath, configPath, rcinfoPath);

    if (!result.ok) {
      vscode.window.showErrorMessage(`REV FTC: could not update ${path.basename(uri.fsPath)} from the hardware configuration.`);
      return;
    }

    if (!result.changed) {
      vscode.window.showInformationMessage(`REV FTC: ${path.basename(uri.fsPath)} already matches the hub's configuration.`);
      return;
    }

    if (!result.applied) {
      // Contract 4: markers are gone, nothing was touched. Hand the new
      // code to the user beside the file rather than guessing where to
      // paste it.
      const untitled = await vscode.workspace.openTextDocument({
        language: 'python',
        content: result.block ?? '(no block returned)',
      });
      await vscode.window.showTextDocument(untitled, { viewColumn: vscode.ViewColumn.Beside, preview: false });
      vscode.window.showWarningMessage(
        `REV FTC: ${path.basename(uri.fsPath)}'s pyftc markers are missing - nothing was changed. ` +
          'The new code was opened beside it for you to place by hand.'
      );
      return;
    }

    const newText = result.python ?? '';
    await vscode.workspace.fs.writeFile(uri, Buffer.from(newText, 'utf8'));

    if (result.manual !== undefined) {
      const manualUri = uri.with({ path: uri.path.replace(/\.py$/, '.md') });
      await vscode.workspace.fs.writeFile(manualUri, Buffer.from(result.manual, 'utf8'));
    }

    clearDiagnosticsBySource(uri, DIAGNOSTIC_SOURCE);
    const removedDiags = buildRemovedDiagnostics(newText, result.removed);
    if (removedDiags.length > 0) {
      const collection = getDiagnosticCollection();
      const existing = collection.get(uri) ?? [];
      const diags = removedDiags.map((d) => {
        const range = new vscode.Range(d.line, 0, d.line, Number.MAX_SAFE_INTEGER);
        const diag = new vscode.Diagnostic(range, d.message, vscode.DiagnosticSeverity.Warning);
        diag.source = DIAGNOSTIC_SOURCE;
        return diag;
      });
      collection.set(uri, [...existing, ...diags]);
    }

    const summary: string[] = [];
    if (result.added.length > 0) {
      summary.push(`added ${result.added.map((a) => a.name).join(', ')}`);
    }
    if (result.removed.length > 0) {
      summary.push(`removed ${result.removed.map((r) => r.name).join(', ')}`);
    }
    if (result.hubsAdded.length > 0) {
      summary.push(`new hub(s) ${result.hubsAdded.map((h) => h.name).join(', ')}`);
    }
    const summaryLine = summary.length > 0 ? summary.join('; ') : 'no device changes (fingerprint moved, contents unaffected)';
    log(`updateFromConfig: ${uri.fsPath}: ${summaryLine}`);
    if (result.notes.length > 0) {
      log(`updateFromConfig: ${uri.fsPath} notes: ${result.notes.join(' | ')}`);
    }
    vscode.window.showInformationMessage(`REV FTC: updated ${path.basename(uri.fsPath)} — ${summaryLine}.`);
  });
}

export async function runUpdateFromConfig(): Promise<void> {
  try {
    const scan = await scanForConfigChanges();
    if (!scan) {
      vscode.window.showErrorMessage('REV FTC: could not reach the hub to check its hardware configuration.');
      return;
    }
    if (scan.stale.length === 0) {
      vscode.window.showInformationMessage('REV FTC: every generated starter pack already matches the hub\'s hardware configuration.');
      return;
    }

    const targets = await pickFiles(scan.stale);
    if (!targets || targets.length === 0) {
      return;
    }

    for (const uri of targets) {
      await applyUpdateToFile(uri);
    }
  } catch (err) {
    vscode.window.showErrorMessage(
      `REV FTC: update from hardware configuration failed: ${err instanceof Error ? err.message : String(err)}`
    );
  }
}
