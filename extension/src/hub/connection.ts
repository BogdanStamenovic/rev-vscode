// Resolves how to reach the hub's OnBot Java web server, per
// ARCHITECTURE.md / the deploy spec's resolution order:
//   1. revFtc.hubUrl setting, if set.
//   2. Direct Wi-Fi: http://192.168.43.1:8080 (1.5s probe).
//   3. USB/adb: find a Control Hub device, `adb forward tcp:0 tcp:8080`,
//      use the loopback port adb hands back.
// The result is cached; callers that hit a network failure should call
// invalidateConnection() and retry once (see hub/http.ts).
import * as settingsMod from '../settings';
import { log } from '../output';
import { resolveAdbPath, listDevices, getProp, forwardTcp, connectWifiAdb } from './adb';

export type Transport = 'manual' | 'wifi-direct' | 'usb';

export interface HubConnection {
  baseUrl: string;
  transport: Transport;
  /** adb serial to use for reading /sdcard config files. Undefined when we
   * have no working adb (e.g. manual hubUrl override with no adb around, or
   * direct Wi-Fi with no adb at all) - callers needing it must handle that. */
  adbSerial?: string;
}

export class HubUnreachableError extends Error {
  constructor(details: string) {
    super(`Could not reach the hub. ${details}`);
    this.name = 'HubUnreachableError';
  }
}

const WIFI_DIRECT_BASE_URL = 'http://192.168.43.1:8080';
const WIFI_ADB_SERIAL = '192.168.43.1:5555';

let cached: HubConnection | undefined;
let inFlight: Promise<HubConnection> | undefined;

export async function getConnection(forceRefresh = false): Promise<HubConnection> {
  if (cached && !forceRefresh) {
    return cached;
  }
  if (!inFlight) {
    inFlight = resolveConnection().finally(() => {
      inFlight = undefined;
    });
  }
  cached = await inFlight;
  return cached;
}

export function invalidateConnection(): void {
  cached = undefined;
}

async function probeWifiDirect(timeoutMs = 1500): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${WIFI_DIRECT_BASE_URL}/js/rcInfo.json`, { signal: controller.signal });
    return res.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function resolveConnection(): Promise<HubConnection> {
  const manual = settingsMod.hubUrl();
  if (manual) {
    const baseUrl = manual.replace(/\/+$/, '');
    log(`connection: using revFtc.hubUrl override ${baseUrl}`);
    return { baseUrl, transport: 'manual', adbSerial: await detectAdbSerialBestEffort() };
  }

  if (await probeWifiDirect()) {
    log(`connection: hub reachable directly over Wi-Fi at ${WIFI_DIRECT_BASE_URL}`);
    return { baseUrl: WIFI_DIRECT_BASE_URL, transport: 'wifi-direct', adbSerial: await detectAdbSerialBestEffort() };
  }

  return resolveViaAdb();
}

/** Best-effort adb serial lookup that never throws - used when we already
 * have a working HTTP base URL and just want the serial for config reads. */
async function detectAdbSerialBestEffort(): Promise<string | undefined> {
  try {
    const adbPath = await resolveAdbPath();
    const devices = (await listDevices(adbPath)).filter((d) => d.state === 'device');
    return await pickControlHubSerial(adbPath, devices.map((d) => d.serial));
  } catch {
    return undefined;
  }
}

async function pickControlHubSerial(adbPath: string, serials: string[]): Promise<string | undefined> {
  for (const serial of serials) {
    if (serial === WIFI_ADB_SERIAL) {
      continue; // checked last, below
    }
    const model = await getProp(adbPath, serial, 'ro.product.model').catch(() => '');
    if (model.includes('Control Hub')) {
      return serial;
    }
  }
  if (serials.includes(WIFI_ADB_SERIAL)) {
    return WIFI_ADB_SERIAL;
  }
  return undefined;
}

async function resolveViaAdb(): Promise<HubConnection> {
  let adbPath: string;
  try {
    adbPath = await resolveAdbPath();
  } catch (err) {
    throw new HubUnreachableError(
      `No hub found over Wi-Fi and adb is unavailable (${(err as Error).message})`
    );
  }

  let ready = (await listDevices(adbPath)).filter((d) => d.state === 'device');
  if (ready.length === 0) {
    // Last resort before giving up: the hub may only be reachable over
    // Wi-Fi adb even though the direct HTTP probe failed (busy server,
    // captive portal quirk, etc). Non-fatal if this doesn't work either.
    await connectWifiAdb(adbPath);
    ready = (await listDevices(adbPath)).filter((d) => d.state === 'device');
  }
  if (ready.length === 0) {
    throw new HubUnreachableError(
      'No hub reachable over Wi-Fi, and no adb device is attached/authorized.'
    );
  }

  const serials = ready.map((d) => d.serial);
  let chosen = await pickControlHubSerial(adbPath, serials);
  if (!chosen && ready.length === 1) {
    // Only one candidate and it didn't identify as a Control Hub (older RC,
    // unusual ro.product.model) - assume it's the hub rather than failing
    // when there was never an ambiguity to resolve.
    chosen = ready[0].serial;
    log(`connection: assuming sole adb device ${chosen} is the Control Hub`);
  }
  if (!chosen) {
    throw new HubUnreachableError(
      `Multiple adb devices attached (${serials.join(', ')}) and none identifies as a Control Hub. Set 'revFtc.hubUrl' or 'revFtc.adbPath' to disambiguate.`
    );
  }

  const port = await forwardTcp(adbPath, chosen);
  log(`connection: adb forward tcp:${port} -> tcp:8080 on ${chosen}`);
  return { baseUrl: `http://127.0.0.1:${port}`, transport: 'usb', adbSerial: chosen };
}
