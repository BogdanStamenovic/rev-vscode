// Pure parsing/decision logic for Contract 4's generated-file header line
// and its markers:
//
//   # ── pyftc:config name="Galerija" fingerprint="9f2c1ab30c4d5e6f" generated="2026-09-20" ──
//   ...
//       # ── pyftc:devices ──  ...  # ── pyftc:devices:end ──
//   # pyftc: no longer in the configuration
//
// No vscode dependency, so this is unit tested directly under node, same as
// config.ts/buildLog.ts/adbParse.ts. configWatch.ts and updateFromConfig.ts
// (which DO touch vscode/the filesystem) are thin wrappers around these.

export interface ConfigHeader {
  name: string;
  fingerprint: string;
  generated: string;
}

export interface ScannedHeader {
  /** True as soon as the line contains the "pyftc:config" marker text, even
   * if it failed to parse - lets callers warn about a corrupted header
   * instead of silently treating the file as "not one of ours". */
  looksLikeHeader: true;
  header: ConfigHeader | undefined;
  /** 0-based line index, for placing a diagnostic if the header is malformed. */
  lineIndex: number;
}

const HEADER_MARKER_RE = /pyftc:config\b/;
const ATTR_RE = /(\w+)="([^"]*)"/g;

/** Contract 4 always puts the header at the very top of a generated file.
 * Capping the scan keeps `findConfigHeader` cheap even on a large
 * hand-written .py file that happens to mention "pyftc" somewhere in a
 * docstring or comment further down. */
const MAX_HEADER_SEARCH_LINES = 10;

export function parseConfigHeaderLine(line: string): ConfigHeader | undefined {
  if (!HEADER_MARKER_RE.test(line)) {
    return undefined;
  }
  const attrs: Record<string, string> = {};
  for (const m of line.matchAll(ATTR_RE)) {
    attrs[m[1]] = m[2];
  }
  if (!attrs.name || !attrs.fingerprint || !attrs.generated) {
    return undefined; // present but malformed: missing a required attribute
  }
  return { name: attrs.name, fingerprint: attrs.fingerprint, generated: attrs.generated };
}

/** Scans file text for the pyftc:config marker line. Returns undefined when
 * the file has no such line at all (an ordinary, non-generated .py file -
 * the overwhelmingly common case, so this is the fast path). */
export function findConfigHeader(fileText: string): ScannedHeader | undefined {
  const lines = fileText.split(/\r?\n/);
  const limit = Math.min(lines.length, MAX_HEADER_SEARCH_LINES);
  for (let i = 0; i < limit; i++) {
    if (HEADER_MARKER_RE.test(lines[i])) {
      return { looksLikeHeader: true, header: parseConfigHeaderLine(lines[i]), lineIndex: i };
    }
  }
  return undefined;
}

export interface CandidateFile {
  /** Opaque identifier for the file - callers use a vscode.Uri's string form,
   * kept as a plain string here so this module stays vscode-free. */
  id: string;
  scanned: ScannedHeader;
}

export interface ConfigChangeDecision {
  /** Candidates whose recorded fingerprint no longer matches the hub's
   * current one - these are what revFtc.updateFromConfig should offer to
   * update. */
  stale: Array<{ id: string; header: ConfigHeader }>;
  /** Candidates that look like generated files but whose header didn't
   * parse - can't be fingerprint-compared at all. Surfaced separately so
   * the caller can log/warn instead of silently dropping them. */
  malformed: string[];
}

/** Pure decision: given the scan results and the hub's current
 * config-fingerprint, which files need `starter-update`? A file with no
 * header at all was already filtered out by the caller (findConfigHeader
 * returned undefined) and never reaches here. */
export function decideConfigChanges(candidates: CandidateFile[], currentFingerprint: string): ConfigChangeDecision {
  const stale: Array<{ id: string; header: ConfigHeader }> = [];
  const malformed: string[] = [];
  for (const c of candidates) {
    if (!c.scanned.header) {
      malformed.push(c.id);
      continue;
    }
    if (c.scanned.header.fingerprint !== currentFingerprint) {
      stale.push({ id: c.id, header: c.scanned.header });
    }
  }
  return { stale, malformed };
}

export interface RemovedDevice {
  name: string;
  field: string;
}

export interface RemovedDiagnostic {
  /** 0-based line index. */
  line: number;
  message: string;
}

const REMOVED_MARKER = '# pyftc: no longer in the configuration';

/** Contract 4: starter-update never deletes a field for a device that left
 * the hardware configuration - it inserts a `# pyftc: no longer in the
 * configuration` comment directly above it and leaves the field alone. This
 * finds those marker comments and matches each one to the CLI's `removed[]`
 * list by looking for the field's identifier (as a whole word, so "arm"
 * doesn't match "armLeft") on one of the next few non-blank lines, so the
 * warning diagnostic lands on the actual `self.<field> = ...` / field
 * declaration line rather than on the comment itself. */
export function buildRemovedDiagnostics(fileText: string, removed: RemovedDevice[]): RemovedDiagnostic[] {
  if (removed.length === 0) {
    return [];
  }
  const lines = fileText.split(/\r?\n/);
  const diags: RemovedDiagnostic[] = [];
  const unmatched = new Map(removed.map((r) => [r.field, r]));

  for (let i = 0; i < lines.length && unmatched.size > 0; i++) {
    if (!lines[i].includes(REMOVED_MARKER)) {
      continue;
    }
    for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
      const candidateLine = lines[j];
      if (candidateLine.trim().length === 0) {
        continue;
      }
      const match = [...unmatched.values()].find((r) => wholeWord(r.field).test(candidateLine));
      if (match) {
        diags.push({ line: j, message: removedMessage(match.name) });
        unmatched.delete(match.field);
      }
      break; // only the first non-blank line after the marker counts
    }
  }

  // Contract drift or unexpected formatting: don't drop a removed device
  // silently just because we couldn't line it up with a marker comment.
  for (const device of unmatched.values()) {
    diags.push({ line: 0, message: `${removedMessage(device.name)} (marker comment not found; check the file).` });
  }

  return diags;
}

function removedMessage(name: string): string {
  return `Device '${name}' is no longer in the hardware configuration.`;
}

function wholeWord(identifier: string): RegExp {
  return new RegExp(`\\b${identifier.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`);
}
