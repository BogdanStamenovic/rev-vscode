// Physical controllers for the simulator, read outside the webview.
//
// VS Code runs webviews in cross-origin iframes, where Chromium's permissions
// policy can block the Gamepad API. Two routes that do not depend on it:
//  - `python -m pyftc gamepad`: a stdlib evdev reader (Linux) that streams FTC
//    Gamepad state, with Driver Station style Start+A / Start+B assignment;
//  - a local "controller bridge" page served on 127.0.0.1 and opened in the
//    system browser, which posts Gamepad API state back here.
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';
import { spawn, type ChildProcess } from 'node:child_process';
import { pythonProcess } from '../cli';
import { log } from '../output';
import { LineSplitter, parseLine, type SimMessage } from './protocol';

export type ControllerSink = (msg: SimMessage) => void;

export class SystemGamepadReader {
  private proc: ChildProcess | undefined;

  constructor(private readonly sink: ControllerSink) {}

  async start(): Promise<void> {
    if (this.proc || process.platform !== 'linux') return;
    try {
      const { python, env } = await pythonProcess();
      const proc = spawn(python, ['-m', 'pyftc', 'gamepad'], { env });
      this.proc = proc;
      const splitter = new LineSplitter();
      proc.stdout.setEncoding('utf8');
      proc.stdout.on('data', (chunk: string) => {
        for (const line of splitter.push(chunk)) {
          const m = parseLine(line);
          if (!m) continue;
          if (m.type === 'devices') {
            const errors = (m.errors as string[] | undefined) ?? [];
            this.sink({ type: 'systemGamepads', devices: m.devices, ...(errors.length ? { error: errors.join('\n') } : {}) });
          } else if (m.type === 'state') {
            this.sink({ type: 'bridgeGamepad', index: m.index, gamepadType: m.gamepadType, state: m.state, deviceName: m.id });
          } else if (m.type === 'error') {
            this.sink({ type: 'systemGamepads', devices: [], error: String(m.message) });
          }
        }
      });
      proc.stderr.setEncoding('utf8');
      proc.stderr.on('data', (d: string) => log(`gamepad reader: ${d.trimEnd()}`));
      proc.on('exit', () => {
        if (this.proc === proc) this.proc = undefined;
      });
      proc.on('error', (e) => log(`gamepad reader failed to start: ${e.message}`));
    } catch (e) {
      log(`gamepad reader unavailable: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  dispose(): void {
    this.proc?.kill();
    this.proc = undefined;
  }
}

/** Serves dist/sim/bridge.html + bridge.js and accepts POST /gamepad from it. */
export class GamepadBridgeServer {
  private server: http.Server | undefined;
  private url: string | undefined;

  constructor(private readonly distDir: string, private readonly sink: ControllerSink) {}

  async start(): Promise<string> {
    if (this.url) return this.url;
    const server = http.createServer((req, res) => this.handle(req, res));
    await new Promise<void>((resolve, reject) => {
      server.once('error', reject);
      server.listen(0, '127.0.0.1', () => resolve());
    });
    this.server = server;
    const addr = server.address();
    const port = typeof addr === 'object' && addr ? addr.port : 0;
    this.url = `http://127.0.0.1:${port}/`;
    log(`simulator: controller bridge at ${this.url}`);
    return this.url;
  }

  private handle(req: http.IncomingMessage, res: http.ServerResponse): void {
    const csp = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:";
    if (req.method === 'GET' && (req.url === '/' || req.url === '/bridge.html' || req.url === '/bridge.js')) {
      const file = req.url === '/bridge.js' ? 'bridge.js' : 'bridge.html';
      try {
        const body = fs.readFileSync(path.join(this.distDir, file));
        res.writeHead(200, {
          'Content-Type': file.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'text/html; charset=utf-8',
          'Content-Security-Policy': csp,
        });
        res.end(body);
      } catch {
        res.writeHead(404).end();
      }
      return;
    }
    if (req.method === 'POST' && req.url === '/gamepad') {
      let body = '';
      req.on('data', (c) => {
        body += c;
        if (body.length > 65536) req.destroy();
      });
      req.on('end', () => {
        const m = parseLine(JSON.stringify({ type: 'bridgeGamepad', ...safeJson(body) }));
        if (m && (m.index === 1 || m.index === 2)) this.sink(m);
        res.writeHead(204).end();
      });
      return;
    }
    res.writeHead(404).end();
  }

  dispose(): void {
    this.server?.close();
    this.server = undefined;
    this.url = undefined;
  }
}

function safeJson(text: string): Record<string, unknown> {
  try {
    const o = JSON.parse(text);
    return o && typeof o === 'object' ? o : {};
  } catch {
    return {};
  }
}
