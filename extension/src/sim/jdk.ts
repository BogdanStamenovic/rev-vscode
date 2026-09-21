// Finds a JDK for the simulator: revFtc.javaHome, then JAVA_HOME / PATH, then
// offers to download one (Eclipse Temurin 17 from the Adoptium API, the same
// JDK scripts/javac-env.sh uses for the translator's javac tests) into the
// extension's global storage. javac is required, not just java: the simulator
// compiles the translated OpModes itself. Every failure says exactly what is
// missing.
import * as vscode from 'vscode';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as https from 'node:https';
import { spawn } from 'node:child_process';
import * as settingsMod from '../settings';
import { log } from '../output';

export interface Jdk {
  javac: string;
  java: string;
  version: number;
  source: 'setting' | 'JAVA_HOME' | 'PATH' | 'downloaded';
}

export class JdkMissingError extends Error {}

const MIN_VERSION = 11;
const EXE = process.platform === 'win32' ? '.exe' : '';

/** "javac 17.0.20" / "javac 1.8.0_292" -> 17 / 8. */
export function parseJavacVersion(text: string): number | undefined {
  const m = /javac\s+(\d+)(?:\.(\d+))?/.exec(text);
  if (!m) return undefined;
  const major = parseInt(m[1], 10);
  return major === 1 && m[2] ? parseInt(m[2], 10) : major;
}

function run(cmd: string, args: string[]): Promise<{ code: number | null; out: string }> {
  return new Promise((resolve) => {
    let out = '';
    let child;
    try {
      child = spawn(cmd, args);
    } catch {
      resolve({ code: -1, out: '' });
      return;
    }
    child.stdout.on('data', (d) => (out += d.toString()));
    child.stderr.on('data', (d) => (out += d.toString()));
    child.on('error', () => resolve({ code: -1, out }));
    child.on('exit', (code) => resolve({ code, out }));
  });
}

async function probe(javac: string, source: Jdk['source']): Promise<Jdk | string> {
  const r = await run(javac, ['-version']);
  if (r.code !== 0) return `${javac} does not run`;
  const version = parseJavacVersion(r.out);
  if (version === undefined) return `${javac} -version printed "${r.out.trim()}"`;
  if (version < MIN_VERSION) return `${javac} is Java ${version}; the simulator needs ${MIN_VERSION} or newer`;
  const java = path.join(path.dirname(javac), `java${EXE}`);
  return { javac, java: fs.existsSync(java) ? java : 'java', version, source };
}

function javacIn(home: string): string {
  return path.join(home, 'bin', `javac${EXE}`);
}

/** The first usable JDK, or a list of the reasons nothing was usable. */
export async function findJdk(storageDir: string): Promise<Jdk | string[]> {
  const problems: string[] = [];
  const setting = settingsMod.javaHome();
  if (setting) {
    const javac = javacIn(setting);
    if (!fs.existsSync(javac)) {
      problems.push(`revFtc.javaHome is "${setting}" but ${javac} does not exist (a JRE is not enough: the simulator needs javac)`);
    } else {
      const r = await probe(javac, 'setting');
      if (typeof r !== 'string') return r;
      problems.push(r);
    }
  }
  if (process.env.JAVA_HOME && fs.existsSync(javacIn(process.env.JAVA_HOME))) {
    const r = await probe(javacIn(process.env.JAVA_HOME), 'JAVA_HOME');
    if (typeof r !== 'string') return r;
    problems.push(r);
  }
  const onPath = await probe(`javac${EXE}`, 'PATH');
  if (typeof onPath !== 'string') return onPath;
  problems.push('no javac on PATH');
  const downloaded = findDownloaded(storageDir);
  if (downloaded) {
    const r = await probe(downloaded, 'downloaded');
    if (typeof r !== 'string') return r;
    problems.push(r);
  }
  return problems;
}

function findDownloaded(storageDir: string): string | undefined {
  const root = path.join(storageDir, 'jdk');
  if (!fs.existsSync(root)) return undefined;
  for (const entry of fs.readdirSync(root)) {
    for (const home of [path.join(root, entry), path.join(root, entry, 'Contents', 'Home')]) {
      if (fs.existsSync(javacIn(home))) return javacIn(home);
    }
  }
  return undefined;
}

/** Resolve a JDK, offering the download when there is none. */
export async function resolveJdk(context: vscode.ExtensionContext): Promise<Jdk> {
  const storageDir = context.globalStorageUri.fsPath;
  const found = await findJdk(storageDir);
  if (!Array.isArray(found)) {
    log(`simulator: using ${found.javac} (Java ${found.version}, from ${found.source})`);
    return found;
  }
  const detail = found.join('; ');
  const choice = await vscode.window.showErrorMessage(
    `REV FTC: the simulator needs a Java Development Kit (javac, Java ${MIN_VERSION}+). ${detail}.`,
    'Download JDK 17 (about 190 MB)',
    'Set revFtc.javaHome…'
  );
  if (choice === 'Set revFtc.javaHome…') {
    await vscode.commands.executeCommand('workbench.action.openSettings', 'revFtc.javaHome');
    throw new JdkMissingError(`no JDK: ${detail}`);
  }
  if (!choice) throw new JdkMissingError(`no JDK: ${detail}`);
  await downloadJdk(storageDir);
  const again = await findJdk(storageDir);
  if (Array.isArray(again)) throw new JdkMissingError(`the downloaded JDK does not work: ${again.join('; ')}`);
  return again;
}

export function adoptiumUrl(platform = process.platform, arch = process.arch): string {
  const os = platform === 'darwin' ? 'mac' : platform === 'win32' ? 'windows' : 'linux';
  const cpu = arch === 'arm64' ? 'aarch64' : 'x64';
  return `https://api.adoptium.net/v3/binary/latest/17/ga/${os}/${cpu}/jdk/hotspot/normal/eclipse`;
}

function download(url: string, dest: string, progress: (bytes: number, total: number) => void, redirects = 5): Promise<void> {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirects > 0) {
        res.resume();
        download(new URL(res.headers.location, url).toString(), dest, progress, redirects - 1).then(resolve, reject);
        return;
      }
      if (res.statusCode !== 200) {
        res.resume();
        reject(new Error(`${url} answered HTTP ${res.statusCode}`));
        return;
      }
      const total = parseInt(res.headers['content-length'] ?? '0', 10);
      let got = 0;
      const file = fs.createWriteStream(dest);
      res.on('data', (chunk: Buffer) => {
        got += chunk.length;
        progress(got, total);
      });
      res.pipe(file);
      file.on('finish', () => file.close(() => resolve()));
      file.on('error', reject);
    }).on('error', reject);
  });
}

async function downloadJdk(storageDir: string): Promise<void> {
  const root = path.join(storageDir, 'jdk');
  fs.mkdirSync(root, { recursive: true });
  const archive = path.join(root, process.platform === 'win32' ? 'jdk.zip' : 'jdk.tar.gz');
  const url = adoptiumUrl();
  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'REV FTC: downloading JDK 17', cancellable: false },
    async (p) => {
      let last = 0;
      await download(url, archive, (got, total) => {
        const pct = total ? Math.floor((got / total) * 100) : 0;
        if (pct > last) {
          p.report({ increment: pct - last, message: `${Math.round(got / 1e6)} MB` });
          last = pct;
        }
      });
      p.report({ message: 'unpacking…' });
      // tar ships with Linux, macOS and Windows 10+, and handles .zip there too.
      const r = await run('tar', ['-xf', archive, '-C', root]);
      if (r.code !== 0) throw new Error(`unpacking ${archive} failed: ${r.out}`);
      fs.rmSync(archive, { force: true });
    }
  );
  log(`simulator: JDK downloaded from ${url} into ${root}`);
}
