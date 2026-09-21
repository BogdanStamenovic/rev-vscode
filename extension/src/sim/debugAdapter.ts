// "Debug in the simulator": a VS Code debug type (revftc-sim) whose adapter is
// the simulator's own JDI-based DAP server (python/pyftc/sim/java/debug). It
// attaches to the running simulator JVM; breakpoints, the call stack, locals and
// watches are in Python files, lines and names; sim time freezes while stopped.
import * as vscode from 'vscode';
import { SimPanel } from './panel';

export const DEBUG_TYPE = 'revftc-sim';

export class SimDebugAdapterFactory implements vscode.DebugAdapterDescriptorFactory {
  createDebugAdapterDescriptor(): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
    const target = SimPanel.current?.session.debugTarget;
    if (!target || !SimPanel.current?.session.running()) {
      throw new Error('Open the simulator (REV FTC: Open Simulator) and let it start before debugging.');
    }
    return new vscode.DebugAdapterExecutable(target.java, [
      '-cp', target.classpath.join(process.platform === 'win32' ? ';' : ':'),
      'org.pyftc.sim.debug.DapServer', '--port', String(target.port), '--manifest', target.manifest,
    ]);
  }
}

export async function debugInSimulator(context: vscode.ExtensionContext): Promise<boolean> {
  const panel = SimPanel.show(context);
  for (let i = 0; i < 600 && !(panel.session.running() && panel.session.lastReady); i++) {
    await new Promise((r) => setTimeout(r, 250));
  }
  if (!panel.session.running()) {
    vscode.window.showErrorMessage('REV FTC: the simulator is not running, so there is nothing to debug yet.');
    return false;
  }
  // Sources open in the first group when the OpMode stops; the simulator sits in another.
  await vscode.commands.executeCommand('workbench.action.focusFirstEditorGroup');
  return vscode.debug.startDebugging(vscode.workspace.workspaceFolders?.[0], {
    type: DEBUG_TYPE, request: 'attach', name: 'REV FTC Simulator',
  });
}
