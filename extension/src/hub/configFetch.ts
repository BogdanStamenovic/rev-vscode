// Reads and parses the active hardware config XML from the hub. There is no
// HTTP endpoint for this (ARCHITECTURE.md) - it lives at
// /sdcard/FIRST/<activeConfigName>.xml and is only reachable via adb.
import { resolveAdbPath, shellCat, connectWifiAdb } from './adb';
import { parseConfigXml, type ParsedConfig } from './config';
import type { HubConnection } from './connection';

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
