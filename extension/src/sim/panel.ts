// The simulator panel (revFtc.openSimulator): hosts the webview (three.js
// bench, Driver Hub, gamepads, code trace), owns the SimSession, persists the
// scene layout to .pyftc/sim-layout.json (Contract 6) and routes messages:
// webview -> sim commands, sim events -> webview, controllers -> webview.
import * as vscode from 'vscode';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';
import { SimSession, type StatusState } from './session';
import { SystemGamepadReader, GamepadBridgeServer } from './controllers';
import type { SimMessage } from './protocol';
import { log } from '../output';

export class SimPanel implements vscode.Disposable {
  static current: SimPanel | undefined;

  readonly panel: vscode.WebviewPanel;
  readonly session: SimSession;
  private readonly reader: SystemGamepadReader;
  private readonly bridge: GamepadBridgeServer;
  private readonly disposables: vscode.Disposable[] = [];
  private layoutTimer: NodeJS.Timeout | undefined;
  private started = false;
  /** Probe state for tests (revFtc._simulatorProbe). */
  readonly probe = { webviewReady: false, delivered: 0, env: undefined as unknown, lastStatus: '' as string };

  static show(context: vscode.ExtensionContext): SimPanel {
    if (SimPanel.current) {
      // Reveal where it already is: moving a live webview panel to another group while a
      // debug session opens sources closed it (VS Code 1.138).
      SimPanel.current.panel.reveal(undefined, true);
      return SimPanel.current;
    }
    SimPanel.current = new SimPanel(context);
    return SimPanel.current;
  }

  private constructor(context: vscode.ExtensionContext) {
    const dist = vscode.Uri.joinPath(context.extensionUri, 'dist', 'sim');
    // Keep the simulator in a group of its own: source files (breakpoints, error links)
    // then open in the other group instead of taking the simulator's place.
    const column = vscode.window.activeTextEditor ? vscode.ViewColumn.Beside : vscode.ViewColumn.Two;
    this.panel = vscode.window.createWebviewPanel('revFtcSimulator', 'REV FTC Simulator', column, {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: [dist],
    });
    this.panel.iconPath = vscode.Uri.joinPath(context.extensionUri, 'media', 'activity-icon.svg');
    this.panel.webview.html = this.html(dist);
    this.session = new SimSession(context, {
      onSimMessage: (msg) => this.post({ type: 'sim', msg }),
      onStatus: (state: StatusState, message?: string) => {
        this.probe.lastStatus = state;
        this.post({ type: 'status', state, message });
        if (state === 'error' && message) vscode.window.showWarningMessage(`REV FTC simulator: ${message}`);
      },
      onCompileErrors: (errors) => this.post({ type: 'compileErrors', errors }),
      onSources: (files) => this.post({ type: 'sources', files }),
    });
    const toWebview = (m: SimMessage): void => this.post(m);
    this.reader = new SystemGamepadReader(toWebview);
    this.bridge = new GamepadBridgeServer(dist.fsPath, toWebview);
    this.panel.webview.onDidReceiveMessage((m) => this.onMessage(m), undefined, this.disposables);
    this.panel.onDidDispose(() => this.dispose(), undefined, this.disposables);
    this.disposables.push(vscode.workspace.onDidSaveTextDocument((doc) => {
      if (doc.languageId === 'python' && this.started) void this.session.start();
    }));
  }

  private html(dist: vscode.Uri): string {
    const nonce = crypto.randomBytes(16).toString('base64');
    const w = this.panel.webview;
    const csp = w.cspSource;
    const js = w.asWebviewUri(vscode.Uri.joinPath(dist, 'webview.js'));
    const css = w.asWebviewUri(vscode.Uri.joinPath(dist, 'webview.css'));
    return `<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${csp} data: blob:; style-src ${csp} 'unsafe-inline'; script-src 'nonce-${nonce}'; font-src ${csp}; connect-src ${csp};">
<link rel="stylesheet" href="${css}"></head>
<body><div id="app"></div><script nonce="${nonce}" src="${js}"></script></body></html>`;
  }

  post(msg: object): void {
    void this.panel.webview.postMessage(msg).then((ok) => {
      if (ok) this.probe.delivered++;
    });
  }

  private readLayout(): unknown {
    try {
      return JSON.parse(fs.readFileSync(this.session.layoutPath(), 'utf8'));
    } catch {
      return null;
    }
  }

  private async onMessage(m: { type: string; [k: string]: unknown }): Promise<void> {
    switch (m.type) {
      case 'ready':
        this.probe.webviewReady = true;
        this.post({ type: 'hello', layout: this.readLayout(), workspaceName: vscode.workspace.name });
        if (!this.started) {
          this.started = true;
          void this.reader.start();
          await this.session.start();
        }
        break;
      case 'env':
        this.probe.env = m;
        log(`simulator webview: Gamepad API ${String(m.gamepadApi)} (${String(m.detail)})`);
        break;
      case 'sim':
        this.session.send(m.msg as object);
        break;
      case 'layoutChanged':
        this.saveLayout(m.layout);
        this.session.send({ type: 'layout', layout: m.layout });
        break;
      case 'openSource': {
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(String(m.file)));
        const line = Math.max(0, Number(m.line) - 1);
        await vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.One, selection: new vscode.Range(line, 0, line, 0) });
        break;
      }
      case 'rebuild':
        await this.session.start();
        break;
      case 'debug':
        await vscode.commands.executeCommand('revFtc.debugSimulator');
        break;
      case 'openGamepadBridge': {
        const url = await this.bridge.start();
        this.post({ type: 'bridgeInfo', url });
        await vscode.env.openExternal(vscode.Uri.parse(url));
        break;
      }
      default:
        break;
    }
  }

  private saveLayout(layout: unknown): void {
    if (this.layoutTimer) clearTimeout(this.layoutTimer);
    this.layoutTimer = setTimeout(() => {
      try {
        const p = this.session.layoutPath();
        fs.mkdirSync(path.dirname(p), { recursive: true });
        fs.writeFileSync(p, JSON.stringify(layout, null, 2) + '\n', 'utf8');
      } catch (err) {
        log(`simulator: could not save the layout: ${err instanceof Error ? err.message : String(err)}`);
      }
    }, 400);
  }

  private disposed = false;

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    if (SimPanel.current === this) SimPanel.current = undefined;
    if (this.layoutTimer) clearTimeout(this.layoutTimer);
    this.session.dispose();
    this.reader.dispose();
    this.bridge.dispose();
    for (const d of this.disposables) d.dispose();
    this.panel.dispose();
  }
}
