// Types + passphrase stripping for GET /js/rcInfo.json.
//
// rcInfo.passphrase is the robot's Wi-Fi password. ARCHITECTURE.md is
// explicit that it must never be logged or displayed, so RcInfo (the type
// the rest of the extension is allowed to touch) simply has no such field,
// and stripPassphrase() deletes it the moment the raw JSON is parsed -
// before it reaches the output channel, the tree view, or anywhere else.
//
// No vscode dependency, so this is unit tested directly under node.

export interface RevHubInfo {
  name: string;
  firmwareVersion: string;
  moduleAddress?: string | number;
  imuType?: string;
  parentSerial?: string;
  revProductNumber?: string;
  [extra: string]: unknown;
}

export interface RcInfo {
  activeConfigName: string;
  rcVersion: string;
  sdkVersion: string;
  deviceName: string;
  chOsVersion?: string;
  isREVControlHub?: boolean;
  networkName?: string;
  serialNumber?: string;
  serverIsAlive?: boolean;
  revHubNamesAndVersions: RevHubInfo[];
  [extra: string]: unknown;
}

/** Parses raw rcInfo.json text/object and strips `passphrase` immediately. */
export function stripPassphrase(raw: unknown): RcInfo {
  if (raw === null || typeof raw !== 'object') {
    throw new Error('rcInfo.json did not parse to an object');
  }
  const copy: Record<string, unknown> = { ...(raw as Record<string, unknown>) };
  delete copy.passphrase;
  if (!Array.isArray(copy.revHubNamesAndVersions)) {
    copy.revHubNamesAndVersions = [];
  }
  return copy as unknown as RcInfo;
}
