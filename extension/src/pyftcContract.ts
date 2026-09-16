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
}

/** Strips the leading "/src/" (or "src/") a hubPath/tree path may carry, to
 * get the canonical form used for comparisons: "org/.../Name.java". */
export function canonicalHubPath(p: string): string {
  return p.replace(/^\/?src\//, '');
}
