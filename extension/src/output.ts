// Single shared "REV FTC" output channel. Every HTTP call and CLI
// invocation gets logged here (method/path/status/ms, or command+args) -
// never a passphrase, never a request/response body (source code, hub
// responses). See ARCHITECTURE.md's passphrase warning and the deploy spec's
// "no source bodies" rule.
import * as vscode from 'vscode';

let channel: vscode.OutputChannel | undefined;

export function getOutputChannel(): vscode.OutputChannel {
  if (!channel) {
    channel = vscode.window.createOutputChannel('REV FTC');
  }
  return channel;
}

function timestamp(): string {
  return new Date().toISOString().split('T')[1].replace('Z', '');
}

export function log(message: string): void {
  getOutputChannel().appendLine(`[${timestamp()}] ${message}`);
}

export function logHttp(method: string, path: string, status: number | 'error', ms: number): void {
  log(`HTTP ${method} ${path} -> ${status} (${ms}ms)`);
}

export function logCli(command: string[]): void {
  log(`CLI ${command.map(shellQuote).join(' ')}`);
}

function shellQuote(arg: string): string {
  return /[\s"']/.test(arg) ? JSON.stringify(arg) : arg;
}

export function disposeOutputChannel(): void {
  channel?.dispose();
  channel = undefined;
}
