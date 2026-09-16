// Ensures Pylance can resolve `import ftc...` by adding the bundled stub
// package to python.analysis.extraPaths (a workspace setting). Asks once per
// workspace; the answer (yes or no) is remembered in workspaceState so we
// never nag again, even if they said no.
import * as vscode from 'vscode';
import * as path from 'node:path';
import { log } from '../output';

const ASKED_KEY = 'revFtc.autocompleteAsked';

export async function ensureAutocomplete(context: vscode.ExtensionContext): Promise<void> {
  if (context.workspaceState.get<boolean>(ASKED_KEY)) {
    return;
  }
  const found = await vscode.workspace.findFiles('**/*.py', '**/{node_modules,.git}/**', 1);
  if (found.length === 0) {
    return; // no .py files yet - don't mark as asked, so we ask once one appears
  }

  const choice = await vscode.window.showInformationMessage(
    'Enable FTC autocomplete in this workspace?',
    'Enable',
    'Not now'
  );
  await context.workspaceState.update(ASKED_KEY, true);
  if (choice !== 'Enable') {
    return;
  }
  await addExtraPath(context.extensionPath);
}

async function addExtraPath(extensionPath: string): Promise<void> {
  const stubPath = path.join(extensionPath, 'python');
  const config = vscode.workspace.getConfiguration('python.analysis');
  const current = config.get<string[]>('extraPaths') ?? [];
  if (current.includes(stubPath)) {
    return;
  }
  await config.update('extraPaths', [...current, stubPath], vscode.ConfigurationTarget.Workspace);
  log(`autocomplete: added ${stubPath} to python.analysis.extraPaths`);
}
