// Pure merge logic for revFtc.setupFiles (commands/setupFiles.ts owns every
// vscode and filesystem call). Each function takes a file's current text and
// returns the new text plus whether anything changed, so a second run of
// Setup Files is a no-op and nothing the user put in those files is lost.
import * as path from 'node:path';

/** Workspace-relative home of the stubs. It is a link to <extension>/python,
 * not a copy and not an absolute path: the extension's install directory
 * carries its version (bogdanstamenovic.rev-vscode-0.1.0), so an absolute
 * path written into workspace config silently breaks autocomplete on the
 * next update. The link is re-pointed on every activation instead. */
export const STUB_LINK_REL = '.pyftc/stubs';

/** An extraPaths entry an older build of this extension wrote: the absolute
 * stub directory inside some installed version of it. */
export function isStaleStubPath(p: string, currentStubDir: string): boolean {
  if (path.normalize(p) === path.normalize(currentStubDir)) {
    return true;
  }
  return /bogdanstamenovic\.rev-vscode-[^/\\]+[/\\]python[/\\]?$/.test(p);
}

export interface Merged {
  text: string;
  changed: boolean;
}

export function mergeExtraPaths(existing: readonly string[], currentStubDir: string): { value: string[]; changed: boolean } {
  const kept = existing.filter((p) => !isStaleStubPath(p, currentStubDir));
  const value = kept.includes(STUB_LINK_REL) ? kept : [...kept, STUB_LINK_REL];
  const changed = value.length !== existing.length || value.some((p, i) => p !== existing[i]);
  return { value, changed };
}

export class UnparseableJsonError extends Error {}

function parseObject(text: string, file: string): Record<string, unknown> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (err) {
    // Comments or trailing commas: editing it through JSON.parse would drop
    // them, so leave the file alone and say so rather than rewrite it.
    throw new UnparseableJsonError(`${file} is not plain JSON (${(err as Error).message}); left unchanged`);
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new UnparseableJsonError(`${file} is not a JSON object; left unchanged`);
  }
  return parsed as Record<string, unknown>;
}

function render(obj: Record<string, unknown>): string {
  return JSON.stringify(obj, null, 2) + '\n';
}

/** pyrightconfig.json is read by Pylance, pyright and basedpyright alike, and
 * whether or not a Python extension has registered python.analysis.*, which
 * makes it the one place that works for every language server. */
export function mergePyrightConfig(existing: string | undefined, currentStubDir: string): Merged {
  if (existing === undefined) {
    return { text: render({ extraPaths: [STUB_LINK_REL], typeCheckingMode: 'basic' }), changed: true };
  }
  const obj = parseObject(existing, 'pyrightconfig.json');
  const current = Array.isArray(obj.extraPaths) ? obj.extraPaths.filter((p): p is string => typeof p === 'string') : [];
  const { value, changed: pathsChanged } = mergeExtraPaths(current, currentStubDir);
  let changed = pathsChanged || !Array.isArray(obj.extraPaths);
  obj.extraPaths = value;
  if (obj.typeCheckingMode === undefined) {
    // basedpyright defaults to its strictest mode, which buries a starter
    // pack in warnings about the SDK's own loosely typed signatures.
    obj.typeCheckingMode = 'basic';
    changed = true;
  }
  return { text: changed ? render(obj) : existing, changed };
}

export function mergeExtensionsJson(existing: string | undefined, recommendations: readonly string[]): Merged {
  const obj = existing === undefined ? {} : parseObject(existing, '.vscode/extensions.json');
  const current = Array.isArray(obj.recommendations)
    ? obj.recommendations.filter((r): r is string => typeof r === 'string')
    : [];
  const missing = recommendations.filter((r) => !current.includes(r));
  if (existing !== undefined && missing.length === 0) {
    return { text: existing, changed: false };
  }
  obj.recommendations = [...current, ...missing];
  return { text: render(obj), changed: true };
}

/** The language server worth recommending depends on the editor build:
 * Pylance refuses to load outside Microsoft's own VS Code. */
export function recommendedExtensions(host: 'microsoft' | 'open-source'): string[] {
  const own = 'bogdanstamenovic.rev-vscode';
  return host === 'microsoft'
    ? [own, 'ms-python.python', 'ms-python.vscode-pylance']
    : [own, 'detachhead.basedpyright'];
}

export const MIN_PYTHON: readonly [number, number] = [3, 10];

/** Parses the two lines `python -c` prints in setupFiles.ts: sys.executable,
 * then "major.minor". */
export function parsePythonProbe(stdout: string): { executable: string; major: number; minor: number } | undefined {
  const [executable, version] = stdout.trim().split(/\r?\n/);
  const m = /^(\d+)\.(\d+)$/.exec(version ?? '');
  if (!executable || !m) {
    return undefined;
  }
  return { executable, major: Number(m[1]), minor: Number(m[2]) };
}

export function pythonIsNewEnough(major: number, minor: number): boolean {
  return major > MIN_PYTHON[0] || (major === MIN_PYTHON[0] && minor >= MIN_PYTHON[1]);
}
