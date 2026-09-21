// Reads and parses the active hardware config XML from the hub. There is no
// HTTP endpoint for this (ARCHITECTURE.md) - it lives at
// /sdcard/FIRST/<activeConfigName>.xml and is only reachable via adb.
import * as path from 'node:path';
import { writeFile } from 'node:fs/promises';
import { XMLValidator } from 'fast-xml-parser';
import { ensureWifiAdb, isTransientAdbError, resolveAdbPath, shellCat, WIFI_ADB_SERIAL, type AdbState } from './adb';
import { parseConfigXml, type ParsedConfig } from './config';
import { getConnection, type HubConnection } from './connection';
import { fetchRcInfo, type RcInfo } from './rcinfo';

export interface ConfigReadOptions {
  /** Accept a copy read this recently instead of going to the hub again.
   * The config watcher runs on every 5 s hub-view tick; without this it did
   * its own adb read each time on top of the hub view's. 0 = always read. */
  maxAgeMs?: number;
}

interface CachedRead {
  name: string;
  xml: string;
  serial: string;
  at: number;
}

let lastRead: CachedRead | undefined;
const inFlight = new Map<string, Promise<CachedRead>>();

/** Human-readable reason for an adb state that cannot read files. */
function unreadableReason(state: AdbState): string {
  switch (state) {
    case 'offline':
      return 'adb over Wi-Fi to the hub is offline and did not come back after reconnecting';
    case 'unauthorized':
      return 'the hub refused adb (unauthorized); accept the prompt on the hub or re-pair it';
    default:
      return 'No adb connection to the hub, so the hardware config XML cannot be read (there is no HTTP endpoint for it).';
  }
}

/** One `cat`, rejected unless it is complete XML. The log showed a read that
 * came back cut short ("not well-formed ... line 22"), which then broke the
 * fingerprint; a partial file must count as a failed read, not a config. */
async function catConfig(adbPath: string, serial: string, remotePath: string): Promise<string> {
  const xml = await shellCat(adbPath, serial, remotePath);
  const valid = XMLValidator.validate(xml);
  if (valid !== true) {
    throw new Error(`incomplete config XML from adb (${valid.err.msg} at line ${valid.err.line})`);
  }
  return xml;
}

async function readFromHub(conn: HubConnection, activeConfigName: string): Promise<CachedRead> {
  const adbPath = await resolveAdbPath();
  const remotePath = `/sdcard/FIRST/${activeConfigName}.xml`;
  const overWifi = !conn.adbSerial;
  let serial = conn.adbSerial ?? WIFI_ADB_SERIAL;
  if (overWifi) {
    const state = await ensureWifiAdb(adbPath);
    if (state !== 'device') {
      throw new Error(unreadableReason(state));
    }
    serial = WIFI_ADB_SERIAL;
  }

  let xml: string;
  try {
    xml = await catConfig(adbPath, serial, remotePath);
  } catch (err) {
    const message = (err as Error).message;
    if (!isTransientAdbError(message) && !message.startsWith('incomplete config XML')) {
      throw err;
    }
    // One retry. Over Wi-Fi the link may have dropped between the state
    // check and the read, so re-establish it first; over USB just try again.
    if (overWifi) {
      const state = await ensureWifiAdb(adbPath);
      if (state !== 'device') {
        throw new Error(unreadableReason(state));
      }
    }
    xml = await catConfig(adbPath, serial, remotePath);
  }
  return { name: activeConfigName, xml, serial, at: Date.now() };
}

/** Reads the active hardware config XML off the hub. Callers that accept a
 * recent copy (maxAgeMs > 0) share reads; every adb call is serialized in
 * adb.ts, so the hub view, the watcher and a deploy never race each other. */
export async function fetchActiveConfigXml(
  conn: HubConnection,
  activeConfigName: string,
  options: ConfigReadOptions = {}
): Promise<{ xml: string; serial: string; readAt: number }> {
  const maxAge = options.maxAgeMs ?? 0;
  let pending: Promise<CachedRead> | undefined;
  if (maxAge > 0) {
    if (lastRead && lastRead.name === activeConfigName && Date.now() - lastRead.at <= maxAge) {
      return { xml: lastRead.xml, serial: lastRead.serial, readAt: lastRead.at };
    }
    pending = inFlight.get(activeConfigName);
  }
  // A caller wanting a fresh read never joins one already running: that read
  // started before it asked, possibly before the configuration changed
  // (Update from Config right after the robot was reconfigured). It still
  // cannot race anything - adb.ts runs one adb process at a time.
  if (!pending) {
    const started = readFromHub(conn, activeConfigName).finally(() => {
      if (inFlight.get(activeConfigName) === started) {
        inFlight.delete(activeConfigName);
      }
    });
    inFlight.set(activeConfigName, started);
    pending = started;
  }
  const read = await pending;
  lastRead = read;
  return { xml: read.xml, serial: read.serial, readAt: read.at };
}

export function parseActiveConfig(xml: string): ParsedConfig {
  return parseConfigXml(xml);
}

export interface HubConfigFiles {
  configPath: string;
  rcinfoPath: string;
  rcInfo: RcInfo;
}

/** Connects to the hub, fetches rcInfo + the active config XML, and writes
 * both to `dir` as the file pair Contract 3's `starter`, `starter-update`,
 * `manual` and `config-fingerprint` subcommands all require (they take file
 * paths, never stdin). Shared by spawnStarterPack.ts, configWatch.ts and
 * updateFromConfig.ts so the three flows can't quietly drift apart on how
 * that pair gets built. Throws (HubUnreachableError or otherwise) if the hub
 * or the config XML can't be reached - callers decide what "no hub" means
 * for them (spawnStarterPack falls back to an offline picker; configWatch
 * and updateFromConfig just skip the check). */
export async function fetchHubConfigFiles(dir: string, options: ConfigReadOptions = {}): Promise<HubConfigFiles> {
  const conn = await getConnection();
  const rcInfo = await fetchRcInfo();
  const { xml } = await fetchActiveConfigXml(conn, rcInfo.activeConfigName, options);

  const rcinfoPath = path.join(dir, 'rcInfo.json');
  const configPath = path.join(dir, `${rcInfo.activeConfigName}.xml`);
  await writeFile(rcinfoPath, JSON.stringify(rcInfo, null, 2), 'utf8');
  await writeFile(configPath, xml, 'utf8');
  return { configPath, rcinfoPath, rcInfo };
}
