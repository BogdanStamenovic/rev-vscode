import * as vscode from 'vscode';
import * as path from 'node:path';
import * as settingsMod from './settings';

/** Resolves revFtc.sourceRoot (workspace-relative, "" = workspace root)
 * against the first workspace folder. Shared by deploy and starter-pack. */
export function resolveSourceRootDir(): string {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    throw new Error('Open a workspace folder first.');
  }
  const rel = settingsMod.sourceRoot();
  return rel ? path.join(folders[0].uri.fsPath, rel) : folders[0].uri.fsPath;
}
