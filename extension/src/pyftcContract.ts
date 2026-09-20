// Types for Contract 3 (`python -m pyftc`), ARCHITECTURE.md.
//
// Clarifications from the translator author (2026-09-16), folded in here:
//  - Diagnostic.line/endLine are 1-based, col/endCol are 0-based (Python ast
//    convention == vscode.Position convention: use them directly as
//    `new vscode.Position(line - 1, col)`).
//  - `files[]` has one entry PER JAVA CLASS, not per .py source file: a .py
//    file with two top-level OpMode classes yields two entries sharing
//    `source` but with distinct `className`/`hubPath`/`java`/`lineMap`.
//  - `diagnostics` may contain "warning" entries even when ok is true.
//    Only "error" severity should block a deploy.

export interface PyftcDiagnostic {
  source: string;
  line: number; // 1-based
  col: number; // 0-based
  endLine: number; // 1-based
  endCol: number; // 0-based
  severity: 'error' | 'warning';
  message: string;
}

export interface TranslatedFile {
  source: string; // absolute path to the .py file this class came from
  className: string;
  hubPath: string; // "/src/org/firstinspires/ftc/teamcode/pyftc/<Name>.java"
  java: string;
  lineMap: number[]; // lineMap[javaLine - 1] = python line (1-based), 0 = synthetic
  diagnostics: PyftcDiagnostic[];
}

export interface TranslateProjectResult {
  ok: boolean;
  files: TranslatedFile[];
  diagnostics: PyftcDiagnostic[];
}

export interface StarterResult {
  ok: boolean;
  python: string;
  /** 16 hex chars, see ARCHITECTURE.md's "Fingerprint" section. Embedded by
   * the CLI itself into `python`'s `# ── pyftc:config ... ──` header line -
   * this field just saves us from re-parsing it back out for the man page
   * write and other bookkeeping that happens at spawn time. */
  fingerprint: string;
  /** Markdown reference for this robot's configured hardware, written to
   * `<Name>.md` next to `<Name>.py` (Contract 4 activity in the task brief). */
  manual: string;
}

export interface ManualResult {
  ok: boolean;
  markdown: string;
  fingerprint: string;
}

export interface ConfigFingerprintResult {
  ok: boolean;
  fingerprint: string;
}

export interface AddedDevice {
  name: string;
  field: string;
  type: string;
  control: string;
}

export interface RemovedDevice {
  name: string;
  field: string;
}

export interface HubAdded {
  name: string;
  address: string;
}

export interface StarterUpdateResult {
  ok: boolean;
  /** false when the fingerprint already matched the file's header - nothing
   * to do. */
  changed: boolean;
  /** false when the file's markers (Contract 4) are gone: the CLI refused to
   * touch the file. `python`/`manual` are absent in that case; `block` holds
   * the code the user must place by hand instead. */
  applied: boolean;
  fingerprint: string;
  python?: string;
  block?: string;
  manual?: string;
  added: AddedDevice[];
  removed: RemovedDevice[];
  hubsAdded: HubAdded[];
  notes: string[];
}

/** Strips the leading "/src/" (or "src/") a hubPath/tree path may carry, to
 * get the canonical form used for comparisons: "org/.../Name.java". */
export function canonicalHubPath(p: string): string {
  return p.replace(/^\/?src\//, '');
}
