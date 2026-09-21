// One simulator run: `pyftc sim-prepare` (translate + compile against the
// simulation SDK), then the Java sim process, spoken to over NDJSON on stdio
// (Contract 5). Sim events go to the listener (the panel) verbatim; exceptions
// and warnings with a Python location also become Problems, compile errors
// too; `trace` events drive the "lines that ran" decorations in the editor.
import * as vscode from 'vscode';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as net from 'node:net';
import { spawn, type ChildProcess } from 'node:child_process';
import { runPyftcJson } from '../cli';
import { log } from '../output';
import * as settingsMod from '../settings';
import { resolveSourceRootDir } from '../workspaceRoot';
import { fetchHubConfigFiles } from '../hub/configFetch';
import { resolveJdk, type Jdk } from './jdk';
import { LineSplitter, parseLine, problemFor, traceView, type SimMessage } from './protocol';
import { TraceDecorations } from './traceDecorations';
import type { PyftcDiagnostic } from '../pyftcContract';

export interface PrepareResult {
  ok: boolean;
  stage?: string;
  diagnostics: PyftcDiagnostic[];
  java?: string;
  classpath?: string[];
  mainClass?: string;
  manifest?: string;
  constants?: string;
  config?: { name: string; source: string; devices: number };
  debugClasspath?: string[];
}

/** What the debug adapter needs to attach to the running simulator. */
export interface DebugTarget {
  java: string;
  classpath: string[];
  port: number;
  manifest: string;
}

export type StatusState = 'preparing' | 'compiling' | 'running' | 'error' | 'exited';

export interface SessionListener {
  onSimMessage(msg: SimMessage): void;
  onStatus(state: StatusState, message?: string): void;
  onCompileErrors(errors: Array<{ file: string; line: number; message: string }>): void;
  onSources(files: Record<string, string>): void;
}

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.once('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const addr = srv.address();
      const port = typeof addr === 'object' && addr ? addr.port : 0;
      srv.close(() => resolve(port));
    });
  });
}

export class SimSession implements vscode.Disposable {
  private proc: ChildProcess | undefined;
  private readonly diagnostics = vscode.languages.createDiagnosticCollection('revFtcSim');
  private readonly decorations = new TraceDecorations();
  private jdk: Jdk | undefined;
  private lastTraceDraw = 0;
  private stoppedOnPurpose = false;
  lastReady: SimMessage | undefined;
  debugTarget: DebugTarget | undefined;
  lastState: SimMessage | undefined;
  readonly counts = { state: 0, trace: 0, exception: 0 };
  /** Last lines the sim process wrote to stderr and how it last exited (diagnostics, tests). */
  readonly stderrTail: string[] = [];
  lastExit: string | undefined;

  constructor(private readonly context: vscode.ExtensionContext, private readonly listener: SessionListener) {}

  workspaceDir(): string {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0) throw new Error('Open a workspace folder first.');
    return folders[0].uri.fsPath;
  }

  layoutPath(): string {
    return path.join(this.workspaceDir(), '.pyftc', 'sim-layout.json');
  }

  /** (Re)build and (re)start the simulator. */
  async start(): Promise<void> {
    this.stop();
    this.diagnostics.clear();
    this.decorations.clear();
    this.listener.onStatus('preparing', 'Looking for a JDK…');
    try {
      this.jdk = this.jdk ?? (await resolveJdk(this.context));
    } catch (err) {
      this.listener.onStatus('error', err instanceof Error ? err.message : String(err));
      return;
    }
    const root = resolveSourceRootDir();
    const storage = this.context.storageUri?.fsPath ?? path.join(this.context.globalStorageUri.fsPath, 'workspace');
    const out = path.join(storage, 'sim-build');
    const cache = path.join(this.context.globalStorageUri.fsPath, 'simsdk');
    const args = ['sim-prepare', '--root', root, '--out', out, '--cache', cache, '--javac', this.jdk.javac];
    const hubConfig = await this.hubConfig(storage);
    if (hubConfig) args.push('--config', hubConfig, '--config-source', 'hub');

    this.listener.onStatus('compiling', 'Translating and compiling for the simulator… (the first run also builds the simulation SDK)');
    this.listener.onSources(await this.readSources(root));
    let prep: PrepareResult;
    try {
      const outcome = await runPyftcJson<PrepareResult>(args);
      if (!outcome.result) {
        this.listener.onStatus('error', outcome.stderr.trim() || `pyftc sim-prepare exited with ${outcome.code}`);
        return;
      }
      prep = outcome.result;
    } catch (err) {
      this.listener.onStatus('error', err instanceof Error ? err.message : String(err));
      return;
    }
    this.publishCompileDiagnostics(prep.diagnostics);
    if (!prep.ok) {
      this.listener.onStatus('error', prep.stage === 'translate'
        ? 'The code does not translate; see the Problems panel.'
        : 'The code uses something the simulator does not support; see the Problems panel.');
      return;
    }
    log(`simulator: config "${prep.config?.name}" from ${prep.config?.source} (${prep.config?.devices} devices)`);
    await this.spawnSim(prep);
  }

  private async hubConfig(storage: string): Promise<string | undefined> {
    if (settingsMod.simulatorConfigSource() !== 'auto') return undefined;
    try {
      const dir = path.join(storage, 'hub-config');
      fs.mkdirSync(dir, { recursive: true });
      const files = await Promise.race([
        fetchHubConfigFiles(dir),
        new Promise<never>((_, reject) => setTimeout(() => reject(new Error('timeout')), 4000)),
      ]);
      return files.configPath;
    } catch (err) {
      log(`simulator: no hub configuration (${err instanceof Error ? err.message : String(err)}); using the workspace`);
      return undefined;
    }
  }

  private async readSources(root: string): Promise<Record<string, string>> {
    const files: Record<string, string> = {};
    const uris = await vscode.workspace.findFiles(new vscode.RelativePattern(root, '**/*.py'), '**/{node_modules,.git,.pyftc}/**');
    for (const u of uris) {
      try {
        files[u.fsPath] = fs.readFileSync(u.fsPath, 'utf8');
      } catch {
        // unreadable file: nothing to show
      }
    }
    return files;
  }

  private publishCompileDiagnostics(diags: PyftcDiagnostic[]): void {
    const byFile = new Map<string, vscode.Diagnostic[]>();
    const errors: Array<{ file: string; line: number; message: string }> = [];
    for (const d of diags) {
      if (!d.source) continue;
      const range = new vscode.Range(Math.max(0, d.line - 1), d.col, Math.max(0, d.endLine - 1), d.endCol);
      const diag = new vscode.Diagnostic(range, d.message, d.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning);
      diag.source = 'pyftc-sim';
      const list = byFile.get(d.source) ?? [];
      list.push(diag);
      byFile.set(d.source, list);
      if (d.severity === 'error') errors.push({ file: d.source, line: d.line, message: d.message });
    }
    for (const [file, list] of byFile) this.diagnostics.set(vscode.Uri.file(file), list);
    this.listener.onCompileErrors(errors);
  }

  private async spawnSim(prep: PrepareResult): Promise<void> {
    const ws = this.workspaceDir();
    const firstDir = path.join(ws, '.pyftc', 'sim-files', 'FIRST');
    // A JDWP agent is always on (localhost only, quiet so it never writes to stdout):
    // the debugger attaches to it with JDI when the user starts a debug session.
    const port = await freePort();
    const java = prep.java ?? this.jdk?.java ?? 'java';
    this.debugTarget = { java, classpath: prep.debugClasspath ?? [], port, manifest: prep.manifest ?? '' };
    const javaArgs = ['-Xss4m', `-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=127.0.0.1:${port},quiet=y`,
      `-Dpyftc.sim.firstDir=${firstDir}`, '-cp', (prep.classpath ?? []).join(path.delimiter),
      prep.mainClass ?? 'org.pyftc.sim.Main', '--manifest', prep.manifest ?? '', '--constants', prep.constants ?? ''];
    if (fs.existsSync(this.layoutPath())) javaArgs.push('--layout', this.layoutPath());
    log(`simulator: ${java} ${javaArgs.slice(-6).join(' ')}`);
    const proc = spawn(java, javaArgs, { cwd: ws });
    this.proc = proc;
    this.stoppedOnPurpose = false;
    const splitter = new LineSplitter();
    proc.stdout.setEncoding('utf8');
    proc.stdout.on('data', (chunk: string) => {
      for (const line of splitter.push(chunk)) {
        const msg = parseLine(line);
        if (msg) this.handle(msg);
      }
    });
    proc.stderr.setEncoding('utf8');
    proc.stderr.on('data', (chunk: string) => {
      log(`sim stderr: ${chunk.trimEnd()}`);
      this.stderrTail.push(chunk.trimEnd());
      if (this.stderrTail.length > 20) this.stderrTail.shift();
    });
    proc.on('error', (err) => this.listener.onStatus('error', `could not start ${java}: ${err.message}`));
    proc.on('exit', (code, signal) => {
      this.lastExit = `code ${code} signal ${signal} onPurpose ${this.stoppedOnPurpose}`;
      if (this.proc === proc) this.proc = undefined;
      if (!this.stoppedOnPurpose) this.listener.onStatus('exited', `simulator process exited (code ${code})`);
    });
    this.listener.onStatus('running');
  }

  private handle(msg: SimMessage): void {
    switch (msg.type) {
      case 'ready':
        this.lastReady = msg;
        break;
      case 'state':
        this.counts.state++;
        this.lastState = msg;
        break;
      case 'trace': {
        this.counts.trace++;
        const now = Date.now();
        if (now - this.lastTraceDraw > 200) {
          this.lastTraceDraw = now;
          this.decorations.show(traceView(msg));
        }
        break;
      }
      case 'exception':
      case 'warning': {
        if (msg.type === 'exception') this.counts.exception++;
        const p = problemFor(msg);
        if (p) this.addProblem(p.file, p.line, p.message, p.severity, p.code);
        break;
      }
      case 'fatal':
        if (msg.restart) {
          log('simulator: restarting after a stuck OpMode (as the Robot Controller would)');
          void this.start();
        }
        break;
      default:
        break;
    }
    this.listener.onSimMessage(msg);
  }

  private addProblem(file: string, line: number, message: string, severity: 'error' | 'warning', code: string): void {
    const uri = vscode.Uri.file(file);
    const existing = this.diagnostics.get(uri) ?? [];
    const range = new vscode.Range(Math.max(0, line - 1), 0, Math.max(0, line - 1), Number.MAX_SAFE_INTEGER);
    if (existing.some((d) => d.range.start.line === range.start.line && d.message === message)) return;
    const diag = new vscode.Diagnostic(range, message, severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning);
    diag.source = 'pyftc-sim';
    diag.code = code;
    this.diagnostics.set(uri, [...existing, diag]);
  }

  diagnosticsFor(file: string): readonly vscode.Diagnostic[] {
    return this.diagnostics.get(vscode.Uri.file(file)) ?? [];
  }

  send(cmd: object): void {
    if (!this.proc || !this.proc.stdin || this.proc.stdin.destroyed) return;
    const c = cmd as { type?: string };
    if (c.type === 'init') {
      // A new run: problems from the previous run are no longer about this one.
      this.diagnostics.forEach((uri, list) => {
        const kept = list.filter((d) => !String(d.code ?? '').startsWith('sim-'));
        this.diagnostics.set(uri, kept);
      });
    }
    this.proc.stdin.write(JSON.stringify(cmd) + '\n');
  }

  running(): boolean {
    return this.proc !== undefined;
  }

  stop(): void {
    const p = this.proc;
    this.proc = undefined;
    if (p) {
      this.stoppedOnPurpose = true;
      try {
        p.stdin?.end();
      } catch {
        // already gone
      }
      setTimeout(() => p.kill(), 1500);
    }
  }

  dispose(): void {
    this.stop();
    this.diagnostics.dispose();
    this.decorations.dispose();
  }
}
