// Pure parsers for adb command output.

export interface AdbDevice {
  serial: string;
  state: string; // "device", "offline", "unauthorized", ...
}

/** Parses `adb devices` output:
 *
 *   List of devices attached
 *   fd6f053873e61e59	device
 *   192.168.43.1:5555	offline
 */
export function parseDevicesOutput(stdout: string): AdbDevice[] {
  const devices: AdbDevice[] = [];
  for (const line of stdout.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (trimmed.length === 0 || trimmed.startsWith('List of devices attached') || trimmed.startsWith('*')) {
      continue;
    }
    const parts = trimmed.split(/\s+/);
    if (parts.length >= 2) {
      devices.push({ serial: parts[0], state: parts[1] });
    }
  }
  return devices;
}

/** Parses `adb -s <serial> forward tcp:0 tcp:8080` output: adb prints the
 * local port it actually chose (since we asked for "any free port" with
 * tcp:0), as a bare number on stdout. */
export function parseForwardOutput(stdout: string): number {
  const trimmed = stdout.trim();
  const port = parseInt(trimmed, 10);
  if (!Number.isFinite(port) || port <= 0 || String(port) !== trimmed) {
    throw new Error(`unexpected 'adb forward' output, expected a bare port number: ${JSON.stringify(stdout)}`);
  }
  return port;
}
