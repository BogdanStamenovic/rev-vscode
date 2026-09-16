// adb process wrapper: locating the binary, listing devices, port forwarding,
// and shelling out to read the hardware config off /sdcard.
import { spawn } from 'node:child_process';
import { access, constants } from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import * as settingsMod from '../settings';
import { logCli, log } from '../output';
import { parseDevicesOutput, parseForwardOutput, type AdbDevice } from './adbParse';

export class AdbNotFoundError extends Error {
  constructor() {
    super(
      "Could not find adb. Set 'revFtc.adbPath', install platform-tools, or install REV Hardware Client."
    );
    this.name = 'AdbNotFoundError';
  }
}

const BUNDLED_ADB = path.join(os.homedir(), '.local/opt/rev-hardware-client/lib/app/bin/adb');

async function isExecutable(p: string): Promise<boolean> {
  try {
    await access(p, constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

async function isOnPath(bin: string): Promise<boolean> {
  return new Promise((resolve) => {
    const child = spawn(bin, ['version']);
    child.on('error', () => resolve(false));
    child.on('exit', (code) => resolve(code === 0));
  });
}

let cachedAdbPath: string | undefined;

export async function resolveAdbPath(): Promise<string> {
  if (cachedAdbPath) {
    return cachedAdbPath;
  }
  const setting = settingsMod.adbPath();
  if (setting) {
    if (!(await isExecutable(setting))) {
      throw new AdbNotFoundError();
    }
    cachedAdbPath = setting;
    return setting;
  }
  if (await isOnPath('adb')) {
    cachedAdbPath = 'adb';
    return 'adb';
  }
  if (await isExecutable(BUNDLED_ADB)) {
    cachedAdbPath = BUNDLED_ADB;
    return BUNDLED_ADB;
  }
  throw new AdbNotFoundError();
}

export function invalidateAdbPath(): void {
  cachedAdbPath = undefined;
}

interface RunResult {
  stdout: string;
  stderr: string;
  code: number | null;
}

function runAdb(adbPath: string, args: string[], timeoutMs = 10_000): Promise<RunResult> {
  logCli([adbPath, ...args]);
  return new Promise((resolve, reject) => {
    const child = spawn(adbPath, args);
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill();
      reject(new Error(`adb ${args.join(' ')} timed out after ${timeoutMs}ms`));
    }, timeoutMs);
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('error', (err) => {
      clearTimeout(timer);
      reject(err);
    });
    child.on('exit', (code) => {
      clearTimeout(timer);
      resolve({ stdout, stderr, code });
    });
  });
}

export async function listDevices(adbPath: string): Promise<AdbDevice[]> {
  const { stdout } = await runAdb(adbPath, ['devices']);
  return parseDevicesOutput(stdout);
}

export async function getProp(adbPath: string, serial: string, prop: string): Promise<string> {
  const { stdout } = await runAdb(adbPath, ['-s', serial, 'shell', 'getprop', prop]);
  return stdout.trim();
}

/** `adb forward tcp:0 tcp:8080`: asks adb to pick any free local port and
 * forward it to the hub's web server on port 8080; adb prints the chosen
 * port back on stdout. */
export async function forwardTcp(adbPath: string, serial: string, remotePort = 8080): Promise<number> {
  const { stdout, code } = await runAdb(adbPath, ['-s', serial, 'forward', 'tcp:0', `tcp:${remotePort}`]);
  if (code !== 0) {
    throw new Error(`adb forward failed for ${serial}`);
  }
  return parseForwardOutput(stdout);
}

export async function shellCat(adbPath: string, serial: string, remotePath: string): Promise<string> {
  const { stdout, stderr, code } = await runAdb(adbPath, ['-s', serial, 'shell', 'cat', remotePath]);
  if (code !== 0 || /No such file/i.test(stderr)) {
    throw new Error(`adb shell cat ${remotePath} failed: ${stderr.trim() || `exit ${code}`}`);
  }
  return stdout;
}

/** Best-effort: hub may only be reachable via Wi-Fi adb at the RC's fixed
 * address. Failure here is non-fatal to callers - they fall back to
 * whatever `adb devices` already shows. */
export async function connectWifiAdb(adbPath: string, address = '192.168.43.1:5555'): Promise<boolean> {
  try {
    const { stdout, code } = await runAdb(adbPath, ['connect', address], 5_000);
    if (code === 0 && /connected/i.test(stdout)) {
      return true;
    }
    log(`adb connect ${address}: ${stdout.trim()}`);
    return false;
  } catch (err) {
    log(`adb connect ${address} failed: ${(err as Error).message}`);
    return false;
  }
}
