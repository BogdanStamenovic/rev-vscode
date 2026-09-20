// Reads and parses the active hardware config XML from the hub. There is no
// HTTP endpoint for this (ARCHITECTURE.md) - it lives at
// /sdcard/FIRST/<activeConfigName>.xml and is only reachable via adb.
import * as path from 'node:path';
import { writeFile } from 'node:fs/promises';
import { resolveAdbPath, shellCat, connectWifiAdb } from './adb';
import { parseConfigXml, type ParsedConfig } from './config';
import { getConnection, type HubConnection } from './connection';
import { fetchRcInfo, type RcInfo } from './rcinfo';

/** Given a resolved connection (for adbSerial) and the active config name
 * from rcInfo, fetches and parses the config XML. If the connection has no
 * adbSerial (e.g. hub reached over direct Wi-Fi with adb not yet paired),
 * tries `adb connect 192.168.43.1:5555` once, per the spawn-starter-pack
 * flow in the spec. */
export async function fetchActiveConfigXml(
  conn: HubConnection,
  activeConfigName: string
): Promise<{ xml: string; serial: string }> {
  const adbPath = await resolveAdbPath();
  let serial = conn.adbSerial;
  if (!serial) {
    const connected = await connectWifiAdb(adbPath);
    if (connected) {
      serial = '192.168.43.1:5555';
    }
  }
  if (!serial) {
    throw new Error(
      'No adb connection to the hub, so the hardware config XML cannot be read (there is no HTTP endpoint for it).'
    );
  }
  const xml = await shellCat(adbPath, serial, `/sdcard/FIRST/${activeConfigName}.xml`);
  return { xml, serial };
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
export async function fetchHubConfigFiles(dir: string): Promise<HubConfigFiles> {
  const conn = await getConnection();
  const rcInfo = await fetchRcInfo();
  const { xml } = await fetchActiveConfigXml(conn, rcInfo.activeConfigName);

  const rcinfoPath = path.join(dir, 'rcInfo.json');
  const configPath = path.join(dir, `${rcInfo.activeConfigName}.xml`);
  await writeFile(rcinfoPath, JSON.stringify(rcInfo, null, 2), 'utf8');
  await writeFile(configPath, xml, 'utf8');
  return { configPath, rcinfoPath, rcInfo };
}
