// Wraps `python -m pyftc translate-project` (Contract 3) and turns its
// diagnostics into vscode.Diagnostic objects. Shared by the deploy command
// and "Show Generated Java".
import * as vscode from 'vscode';
import { runPyftcJson } from './cli';
import type { PyftcDiagnostic, TranslateProjectResult } from './pyftcContract';

export class TranslatorError extends Error {}

async function run(args: string[], signal?: AbortSignal): Promise<TranslateProjectResult> {
  // Note: a CliAbortedError (cli.ts) intentionally propagates as-is rather
  // than being wrapped in TranslatorError - callers that pass a signal (only
  // liveDiagnostics.ts today) need to tell "cancelled" apart from "the
  // translator actually failed", and TranslatorError would erase that.
  const outcome = await runPyftcJson<TranslateProjectResult>(args, signal);
  // Contract 3: exit 0 = ok, 1 = user code errors (JSON still printed on
  // stdout), 2 = usage/internal error (message on stderr, no JSON).
  if (outcome.code === 0 || outcome.code === 1) {
    if (!outcome.result) {
      throw new TranslatorError('pyftc printed no parseable result');
    }
    return outcome.result;
  }
  throw new TranslatorError(outcome.stderr.trim() || `pyftc exited with code ${outcome.code}`);
}

export function translateProject(root: string, signal?: AbortSignal): Promise<TranslateProjectResult> {
  return run(['translate-project', '--root', root], signal);
}

/** Single/multi-file translate, used by "Show Generated Java" so it doesn't
 * have to translate the whole project just to preview one file. */
export function translateFiles(absolutePyPaths: string[], signal?: AbortSignal): Promise<TranslateProjectResult> {
  return run(['translate-project', '--files', ...absolutePyPaths], signal);
}

export function toVscodeDiagnostic(d: PyftcDiagnostic): vscode.Diagnostic {
  const range = new vscode.Range(
    new vscode.Position(Math.max(0, d.line - 1), d.col),
    new vscode.Position(Math.max(0, d.endLine - 1), d.endCol)
  );
  const diag = new vscode.Diagnostic(
    range,
    d.message,
    d.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning
  );
  diag.source = 'pyftc';
  return diag;
}

/** Populates `collection` from both the per-class and top-level diagnostics
 * (deduped - the translator may report a diagnostic in both places), keyed
 * by .py source file. Returns true iff any diagnostic is severity "error"
 * (warnings alone should not block a deploy, per the translator author's
 * clarification). */
export function applyTranslationDiagnostics(
  collection: vscode.DiagnosticCollection,
  result: TranslateProjectResult
): boolean {
  collection.clear();

  const all = [...result.diagnostics, ...result.files.flatMap((f) => f.diagnostics)];
  const seen = new Set<string>();
  const bySource = new Map<string, vscode.Diagnostic[]>();
  let hasError = false;

  for (const d of all) {
    const key = `${d.source}:${d.line}:${d.col}:${d.endLine}:${d.endCol}:${d.severity}:${d.message}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    if (d.severity === 'error') {
      hasError = true;
    }
    const list = bySource.get(d.source) ?? [];
    list.push(toVscodeDiagnostic(d));
    bySource.set(d.source, list);
  }

  for (const [source, diags] of bySource) {
    collection.set(vscode.Uri.file(source), diags);
  }

  return hasError;
}
