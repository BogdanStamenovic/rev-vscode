import * as vscode from 'vscode';
import { setExtensionPath } from './cli';
import { getOutputChannel, disposeOutputChannel, log } from './output';
import { disposeDiagnosticCollection } from './diagnostics';
import { HubTreeProvider } from './sidebar/hubTreeProvider';
import { runDeploy } from './commands/deploy';
import { runSpawnStarterPack } from './commands/spawnStarterPack';
import { GeneratedJavaProvider, SCHEME as JAVA_SCHEME, runShowGeneratedJava } from './commands/showGeneratedJava';
import { runUpdateFromConfig } from './commands/updateFromConfig';
import { AutocompleteReportProvider, REPORT_SCHEME, runCheckAutocomplete } from './commands/checkAutocomplete';
import { ensureAutocomplete, watchForFtcImports } from './python/autocomplete';
import { LiveDiagnosticsController } from './liveDiagnostics';
import { SimPanel } from './sim/panel';
import { SimDebugAdapterFactory, DEBUG_TYPE, debugInSimulator } from './sim/debugAdapter';

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

  const reportProvider = new AutocompleteReportProvider();
  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider(REPORT_SCHEME, reportProvider)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('revFtc.deploy', () => runDeploy()),
    vscode.commands.registerCommand('revFtc.spawnStarterPack', () => runSpawnStarterPack(context)),
    vscode.commands.registerCommand('revFtc.showGeneratedJava', () => runShowGeneratedJava(javaProvider)),
    vscode.commands.registerCommand('revFtc.refreshHubView', () => hubTreeProvider.refresh(true)),
    vscode.commands.registerCommand('revFtc.updateFromConfig', () => runUpdateFromConfig()),
    vscode.commands.registerCommand('revFtc.checkAutocomplete', () => runCheckAutocomplete(context, reportProvider)),
    vscode.commands.registerCommand('revFtc.openSimulator', () => {
      SimPanel.show(context);
    }),
    // Not contributed: lets the extension-host tests see what the simulator panel did.
    vscode.commands.registerCommand('revFtc._simulatorProbe', (file?: string) => {
      const p = SimPanel.current;
      if (!p) return { open: false };
      return {
        open: true,
        ...p.probe,
        running: p.session.running(),
        counts: p.session.counts,
        stderrTail: p.session.stderrTail,
        lastExit: p.session.lastExit,
        ready: p.session.lastReady,
        lastState: p.session.lastState,
        diagnostics: file ? p.session.diagnosticsFor(file).map((d) => ({ line: d.range.start.line + 1, message: d.message, severity: d.severity })) : [],
      };
    }),
    vscode.commands.registerCommand('revFtc.debugSimulator', () => debugInSimulator(context)),
    vscode.debug.registerDebugAdapterDescriptorFactory(DEBUG_TYPE, new SimDebugAdapterFactory()),
    vscode.commands.registerCommand('revFtc._simulatorSend', (cmd: object) => SimPanel.current?.session.send(cmd))
  );

  const liveDiagnostics = new LiveDiagnosticsController();
  context.subscriptions.push(liveDiagnostics);
  context.subscriptions.push(watchForFtcImports(context));

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
