// Hardware-configuration change watcher: on hub connect, on a sidebar
// refresh, and before a deploy, compares the fingerprint every generated
// starter-pack file was written against to the hub's CURRENT active
// configuration (via `pyftc config-fingerprint`), and offers to run
// revFtc.updateFromConfig when they differ.
//
// Trigger wiring: hubTreeProvider.ts's doRefresh() already runs on view
// visibility (which is "on hub connect" for all practical purposes - the
// tree becomes visible/refreshes right when a connection is first
// established), on the manual refresh button, and on its 5s auto-tick;
// calling check() from there covers both "on hub connect" and "on the
// sidebar refresh" with one code path instead of two. deploy.ts calls it a
// second time right before translating, per the task brief's third trigger.
//
// Cost control: config-fingerprint is documented (ARCHITECTURE.md Contract
// 3) as cheap enough to run on every hub refresh - it never touches the SDK
// type database. The workspace .py scan reads whole file bodies, which is
// only cheap because robot-code workspaces are small (a handful of files);
// see configHeader.ts's MAX_HEADER_SEARCH_LINES for the other half of
// keeping it cheap (bail out of a file's scan after its first few lines).
import * as vscode from 'vscode';
import { withTempDir } from '../tempDir';
import { fetchHubConfigFiles } from './configFetch';
import { configFingerprint } from '../starterCli';
import { findConfigHeader, decideConfigChanges, type CandidateFile } from './configHeader';
import * as settingsMod from '../settings';
import { log } from '../output';

const PY_GLOB = '**/*.py';
const EXCLUDE_GLOB = '**/{node_modules,.git}/**';

export interface ScanResult {
  currentFingerprint: string;
  stale: Array<{ uri: vscode.Uri; name: string }>;
  malformed: vscode.Uri[];
}

async function scanWorkspaceForCandidates(): Promise<Array<{ uri: vscode.Uri; text: string }>> {
  const uris = await vscode.workspace.findFiles(PY_GLOB, EXCLUDE_GLOB);
  const out: Array<{ uri: vscode.Uri; text: string }> = [];
  for (const uri of uris) {
    try {
      const bytes = await vscode.workspace.fs.readFile(uri);
      out.push({ uri, text: Buffer.from(bytes).toString('utf8') });
    } catch {
      // Deleted between findFiles() and readFile(), or unreadable - skip it.
    }
  }
  return out;
}

/** Fetches the hub's current fingerprint and compares it against every
 * generated file's recorded one. Returns undefined if the hub isn't
 * reachable or the config XML can't be read - callers treat that as "nothing
 * to report" rather than an error, since this runs opportunistically on
 * ordinary UI events that shouldn't fail loudly over a disconnected hub. */
export async function scanForConfigChanges(): Promise<ScanResult | undefined> {
  let currentFingerprint: string;
  try {
    currentFingerprint = await withTempDir(async (dir) => {
      const { configPath } = await fetchHubConfigFiles(dir);
      const result = await configFingerprint(configPath);
      return result.fingerprint;
    });
  } catch (err) {
    log(`configWatch: could not compute the hub's current fingerprint: ${(err as Error).message}`);
    return undefined;
  }

  const files = await scanWorkspaceForCandidates();
  const candidates: CandidateFile[] = [];
  const uriById = new Map<string, vscode.Uri>();
  for (const { uri, text } of files) {
    const scanned = findConfigHeader(text);
    if (!scanned) {
      continue; // not a pyftc-generated file at all - the common case
    }
    const id = uri.toString();
    uriById.set(id, uri);
    candidates.push({ id, scanned });
  }

  const decision = decideConfigChanges(candidates, currentFingerprint);
  return {
    currentFingerprint,
    stale: decision.stale.map((s) => ({ uri: uriById.get(s.id)!, name: s.header.name })),
    malformed: decision.malformed.map((id) => uriById.get(id)!),
  };
}

// Avoid re-showing the same toast every 5s auto-refresh tick: only notify
// again once the hub's fingerprint has actually moved on from the last one
// we notified about (a new configuration change, or the same one - either
// way, going quiet after the first toast for an unchanged situation is the
// point; the notification's own action is always available on demand via
// revFtc.updateFromConfig for anyone who dismissed it and changed their mind).
let lastNotifiedFingerprint: string | undefined;

async function notifyIfStale(scan: ScanResult): Promise<void> {
  if (scan.stale.length === 0) {
    return;
  }
  if (scan.currentFingerprint === lastNotifiedFingerprint) {
    return;
  }
  lastNotifiedFingerprint = scan.currentFingerprint;

  const plural = scan.stale.length === 1 ? '' : 's';
  const names = scan.stale.map((s) => s.name).join(', ');
  const choice = await vscode.window.showInformationMessage(
    `REV FTC: the hub's hardware configuration changed since ${scan.stale.length} generated file${plural} (${names}) ${plural ? 'were' : 'was'} written.`,
    'Add new hardware'
  );
  if (choice === 'Add new hardware') {
    await vscode.commands.executeCommand('revFtc.updateFromConfig');
  }
}

let inFlight: Promise<void> | undefined;

/** Entry point for the three automatic triggers. Gated on revFtc.configWatch
 * (the manual revFtc.updateFromConfig command is not - see settings.ts).
 * Coalesces overlapping calls (e.g. a deploy starting right as the sidebar's
 * 5s tick fires) into one actual check rather than two adb round trips. */
export async function checkConfigChanges(): Promise<void> {
  if (!settingsMod.configWatch()) {
    return;
  }
  if (inFlight) {
    return inFlight;
  }
  inFlight = doCheck().finally(() => {
    inFlight = undefined;
  });
  return inFlight;
}

async function doCheck(): Promise<void> {
  try {
    const scan = await scanForConfigChanges();
    if (!scan) {
      return;
    }
    if (scan.malformed.length > 0) {
      log(
        `configWatch: ${scan.malformed.length} file(s) look like generated starter packs but their pyftc:config header did not parse: ${scan.malformed.map((u) => u.fsPath).join(', ')}`
      );
    }
    await notifyIfStale(scan);
  } catch (err) {
    log(`configWatch: check failed: ${(err as Error).message}`);
  }
}
