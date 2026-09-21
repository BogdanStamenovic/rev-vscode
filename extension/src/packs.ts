// Pure helpers for revFtc.deletePack (commands/deletePack.ts owns the
// vscode, filesystem and hub calls). A "pack" is one .py file in the source
// root: deploy uploads every one of them, so deleting a pack means removing
// the file and its classes from the hub.
import * as path from 'node:path';

export const HUB_PREFIX = 'org/firstinspires/ftc/teamcode/pyftc/';

/** Directories `pyftc translate-project --root` skips (collect_sources in
 * python/pyftc/translate.py). Kept identical so the picker offers exactly
 * the files a deploy would upload. */
const SKIPPED_DIRS = new Set(['__pycache__', 'node_modules', 'venv', '.venv', 'env', 'ftc', 'pyftc', 'typings']);

export function isDeployedSource(relPath: string): boolean {
  const parts = relPath.split(/[\\/]/);
  const file = parts.pop() ?? '';
  if (!file.endsWith('.py') || file === '__init__.py') {
    return false;
  }
  return !parts.some((p) => p.startsWith('.') || SKIPPED_DIRS.has(p));
}

const OPMODE_RE = /@(TeleOp|Autonomous)\s*\(\s*name\s*=\s*["']([^"']+)["']/g;

/** The OpMode names a file registers, as the Driver Hub lists them. */
export function opModeNames(source: string): string[] {
  return [...source.matchAll(OPMODE_RE)].map((m) => `${m[2]} (${m[1]})`);
}

/** Only the man page Spawn Starter Pack generates is deleted alongside its
 * .py; a hand-written Notes.md that happens to share the name is not. */
export function isGeneratedManual(markdown: string): boolean {
  return /^# .+: robot reference\s*$/m.test(markdown) && /configuration fingerprint/i.test(markdown);
}

export function canonical(hubPath: string): string {
  return hubPath.replace(/^\/?src\//, '');
}

/** Hub files a pack owns: the classes the translator produced from it, plus
 * any copies of those classes left at the old flat location
 * (pyftc/<Class>.java), from before each pack got its own package. */
export function hubFilesForPack(
  source: string,
  translated: ReadonlyArray<{ source: string; className: string; hubPath: string }>,
  existing: ReadonlySet<string>
): string[] {
  const out = new Set<string>();
  for (const f of translated) {
    if (path.normalize(f.source) !== path.normalize(source)) {
      continue;
    }
    const current = canonical(f.hubPath);
    if (existing.has(current)) {
      out.add(current);
    }
    const legacy = `${HUB_PREFIX}${f.className}.java`;
    if (legacy !== current && existing.has(legacy)) {
      out.add(legacy);
    }
  }
  return [...out].sort();
}

/** Our .java files on the hub that no local file produces any more, grouped
 * the way they would be picked: one group per pack directory, or per file
 * for the old flat layout. */
export function orphanGroups(existing: readonly string[], produced: ReadonlySet<string>, claimed: ReadonlySet<string>): Map<string, string[]> {
  const groups = new Map<string, string[]>();
  for (const p of existing) {
    if (!p.startsWith(HUB_PREFIX) || !p.endsWith('.java') || produced.has(p) || claimed.has(p)) {
      continue;
    }
    const rest = p.slice(HUB_PREFIX.length);
    const key = rest.includes('/') ? rest.slice(0, rest.lastIndexOf('/')) : rest;
    groups.set(key, [...(groups.get(key) ?? []), p]);
  }
  return groups;
}
