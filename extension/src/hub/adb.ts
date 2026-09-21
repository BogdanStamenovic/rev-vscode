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

// One adb process at a time. The hub view, the config watcher, deploy and
// the simulator each talk to adb on their own schedule; over Wi-Fi, their
// overlapping `adb connect`s against the same address are what kept knocking
// the hub's entry into "offline" (the extension log showed ~190 `device
// offline` failures, each straight after a connect).
let adbQueue: Promise<unknown> = Promise.resolve();

function runAdb(adbPath: string, args: string[], timeoutMs = 10_000): Promise<RunResult> {
  const run = () => spawnAdb(adbPath, args, timeoutMs);
  const next = adbQueue.then(run, run);
  adbQueue = next.catch(() => undefined);
  return next;
}

function spawnAdb(adbPath: string, args: string[], timeoutMs: number): Promise<RunResult> {
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

export const WIFI_ADB_SERIAL = '192.168.43.1:5555';

export type AdbState = 'device' | 'offline' | 'unauthorized' | 'absent';

/** `adb -s <serial> get-state`: prints "device" on success, otherwise an
 * error naming the state ("device offline", "device '...' not found"). */
export async function adbState(adbPath: string, serial: string): Promise<AdbState> {
  let result: RunResult;
  try {
    result = await runAdb(adbPath, ['-s', serial, 'get-state'], 5_000);
  } catch {
    return 'absent';
  }
  const out = `${result.stdout}\n${result.stderr}`.toLowerCase();
  if (result.code === 0 && result.stdout.trim() === 'device') {
    return 'device';
  }
  if (out.includes('offline')) {
    return 'offline';
  }
  if (out.includes('unauthorized')) {
    return 'unauthorized';
  }
  return 'absent';
}

/** adb reports a dropped Wi-Fi link in several ways; all of them are worth
 * one reconnect and retry rather than an error in the user's face. */
export function isTransientAdbError(message: string): boolean {
  return /offline|not found|closed|protocol fault|connection reset|no devices|broken pipe/i.test(message);
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

let wifiInFlight: Promise<AdbState> | undefined;

/** Makes the hub's Wi-Fi adb entry usable and returns its final state.
 *
 * Checks before connecting, so a healthy link costs one `get-state` instead
 * of a fresh `adb connect` on every refresh. The important case is a stale
 * "offline" entry: `adb connect` on it answers "already connected" and
 * changes nothing, which is how every read used to fail until the link
 * happened to reset itself. Only dropping the entry forces a new handshake.
 * Concurrent callers share one attempt. */
export function ensureWifiAdb(adbPath: string, address = WIFI_ADB_SERIAL): Promise<AdbState> {
  if (!wifiInFlight) {
    wifiInFlight = connectAndWait(adbPath, address).finally(() => {
      wifiInFlight = undefined;
    });
  }
  return wifiInFlight;
}

async function connectAndWait(adbPath: string, address: string): Promise<AdbState> {
  let state = await adbState(adbPath, address);
  if (state === 'device' || state === 'unauthorized') {
    return state;
  }
  if (state === 'offline') {
    log(`adb: ${address} is offline; dropping the stale entry and reconnecting`);
    await runAdb(adbPath, ['disconnect', address], 5_000).catch(() => undefined);
  }
  try {
    const { stdout, stderr } = await runAdb(adbPath, ['connect', address], 5_000);
    if (!/connected to/i.test(stdout)) {
      log(`adb connect ${address}: ${(stdout || stderr).trim()}`);
      return 'absent';
    }
  } catch (err) {
    log(`adb connect ${address} failed: ${(err as Error).message}`);
    return 'absent';
  }
  // The handshake finishes after `adb connect` returns; until then the entry
  // reads "offline" even though nothing is wrong.
  for (let i = 0; i < 10; i++) {
    state = await adbState(adbPath, address);
    if (state === 'device' || state === 'unauthorized') {
      break;
    }
    await sleep(300);
  }
  if (state !== 'device') {
    log(`adb: ${address} is still ${state} after reconnecting`);
  }
  return state;
}

/** Kept for callers that only need a yes/no. */
export async function connectWifiAdb(adbPath: string, address = WIFI_ADB_SERIAL): Promise<boolean> {
  return (await ensureWifiAdb(adbPath, address)) === 'device';
}
