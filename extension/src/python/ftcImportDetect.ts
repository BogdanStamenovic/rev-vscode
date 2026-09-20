// Pure helpers for python/autocomplete.ts and commands/checkAutocomplete.ts,
// split out so they have no vscode dependency and can be unit tested
// directly under node - same reasoning as hub/config.ts vs hub/configFetch.ts
// (pure parsing/logic module vs. the vscode/fs-touching glue around it).
import * as path from 'node:path';

const FTC_IMPORT_RE = /^\s*(from\s+ftc(?:\.\w+)*\s+import\b|import\s+ftc(?:\.\w+)*\b)/m;

export function hasFtcImport(text: string): boolean {
  return FTC_IMPORT_RE.test(text);
}

export function stubDirFor(extensionPath: string): string {
  return path.join(extensionPath, 'python');
}
