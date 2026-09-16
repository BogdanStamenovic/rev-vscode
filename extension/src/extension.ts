import * as vscode from 'vscode';
import { setExtensionPath } from './cli';
import { getOutputChannel, disposeOutputChannel, log } from './output';
import { disposeDiagnosticCollection } from './diagnostics';
import { HubTreeProvider } from './sidebar/hubTreeProvider';
import { runDeploy } from './commands/deploy';
import { runSpawnStarterPack } from './commands/spawnStarterPack';
import { GeneratedJavaProvider, SCHEME as JAVA_SCHEME, runShowGeneratedJava } from './commands/showGeneratedJava';
import { ensureAutocomplete } from './python/autocomplete';

export function activate(context: vscode.ExtensionContext): void {
  setExtensionPath(context.extensionPath);
  const output = getOutputChannel();
  context.subscriptions.push(output);
  log('REV FTC extension activated');

  const hubTreeProvider = new HubTreeProvider();
  context.subscriptions.push(hubTreeProvider);
  const treeView = vscode.window.createTreeView('revFtcHub', { treeDataProvider: hubTreeProvider });
  context.subscriptions.push(treeView);
  context.subscriptions.push(
    treeView.onDidChangeVisibility((e) => {
      if (e.visible) {
        void hubTreeProvider.refresh(true);
        hubTreeProvider.startAutoRefresh();
      } else {
        hubTreeProvider.stopAutoRefresh();
      }
    })
  );
  if (treeView.visible) {
    void hubTreeProvider.refresh(true);
    hubTreeProvider.startAutoRefresh();
  }

  const javaProvider = new GeneratedJavaProvider();
  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider(JAVA_SCHEME, javaProvider)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('revFtc.deploy', () => void runDeploy()),
    vscode.commands.registerCommand('revFtc.spawnStarterPack', () => void runSpawnStarterPack()),
    vscode.commands.registerCommand('revFtc.showGeneratedJava', () => void runShowGeneratedJava(javaProvider)),
    vscode.commands.registerCommand('revFtc.refreshHubView', () => void hubTreeProvider.refresh(true))
  );

  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBarItem.text = '$(play) Deploy to Hub';
  statusBarItem.tooltip = 'REV FTC: translate and deploy to the Control Hub';
  statusBarItem.command = 'revFtc.deploy';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  context.subscriptions.push({ dispose: disposeDiagnosticCollection });

  void ensureAutocomplete(context);
}

export function deactivate(): void {
  disposeOutputChannel();
}
