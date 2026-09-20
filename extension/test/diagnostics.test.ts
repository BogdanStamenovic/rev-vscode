// Exercises the diagnostics lifecycle (publish / clear-by-source / clear-all)
// that liveDiagnostics.ts and updateFromConfig.ts rely on. Runs against the
// tiny vscode-shim (test/vscode-shim/vscode.js, loaded via NODE_PATH - see
// package.json's "test" script) rather than a real extension host, same
// approach as hub-smoke.ts uses for the hub/* modules.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as vscode from 'vscode';
import {
  getDiagnosticCollection,
  addDiagnostics,
  clearDiagnosticsForUri,
  clearDiagnosticsBySource,
  disposeDiagnosticCollection,
} from '../src/diagnostics';

function diag(message: string, source: string): vscode.Diagnostic {
  const range = new vscode.Range(0, 0, 0, 1);
  const d = new vscode.Diagnostic(range, message, vscode.DiagnosticSeverity.Warning);
  d.source = source;
  return d;
}

// Each test gets a fresh collection - the module holds one as a singleton,
// same lifecycle real activation/deactivation gives it.
function reset(): void {
  disposeDiagnosticCollection();
}

test('addDiagnostics: publishes diagnostics for a fresh uri', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('bad thing', 'pyftc')]);
  const got = getDiagnosticCollection().get(uri);
  assert.equal(got?.length, 1);
  assert.equal(got?.[0].message, 'bad thing');
});

test('addDiagnostics: appends to, rather than replaces, existing diagnostics for the same uri', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('translation error', 'pyftc')]);
  addDiagnostics(uri, [diag('build error', 'pyftc-build')]);
  const got = getDiagnosticCollection().get(uri) ?? [];
  assert.equal(got.length, 2);
  assert.deepEqual(
    got.map((d) => d.source),
    ['pyftc', 'pyftc-build']
  );
});

test('clearDiagnosticsForUri: removes every diagnostic for that uri regardless of source', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('a', 'pyftc'), diag('b', 'pyftc-build')]);
  clearDiagnosticsForUri(uri);
  assert.equal(getDiagnosticCollection().get(uri), undefined);
});

test('clearDiagnosticsForUri: does not touch other files', () => {
  reset();
  const a = vscode.Uri.file('/ws/A.py');
  const b = vscode.Uri.file('/ws/B.py');
  addDiagnostics(a, [diag('a', 'pyftc')]);
  addDiagnostics(b, [diag('b', 'pyftc')]);
  clearDiagnosticsForUri(a);
  assert.equal(getDiagnosticCollection().get(a), undefined);
  assert.equal(getDiagnosticCollection().get(b)?.length, 1);
});

test('clearDiagnosticsBySource: drops only the named source, keeps the rest (live vs. build diagnostics)', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('translation error', 'pyftc'), diag('build error', 'pyftc-build')]);
  clearDiagnosticsBySource(uri, 'pyftc');
  const got = getDiagnosticCollection().get(uri) ?? [];
  assert.equal(got.length, 1);
  assert.equal(got[0].source, 'pyftc-build');
});

test('clearDiagnosticsBySource: deletes the uri entirely once its last diagnostic is cleared', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('translation error', 'pyftc')]);
  clearDiagnosticsBySource(uri, 'pyftc');
  assert.equal(getDiagnosticCollection().get(uri), undefined);
});

test('clearDiagnosticsBySource: a no-op when the source is not present (does not throw, does not touch other diagnostics)', () => {
  reset();
  const uri = vscode.Uri.file('/ws/Drive.py');
  addDiagnostics(uri, [diag('build error', 'pyftc-build')]);
  clearDiagnosticsBySource(uri, 'pyftc'); // 'pyftc' was never added
  const got = getDiagnosticCollection().get(uri) ?? [];
  assert.equal(got.length, 1);
  assert.equal(got[0].source, 'pyftc-build');
});

test('this simulates a fixed file: re-publishing with clear()+set() drops stale diagnostics for files no longer reported', () => {
  reset();
  const stillBroken = vscode.Uri.file('/ws/Broken.py');
  const nowFixed = vscode.Uri.file('/ws/Fixed.py');
  addDiagnostics(stillBroken, [diag('still an error', 'pyftc')]);
  addDiagnostics(nowFixed, [diag('used to be an error', 'pyftc')]);

  // This is exactly what translate.ts's applyTranslationDiagnostics() does
  // on every live-diagnostics run: clear the whole collection, then only
  // re-set diagnostics for sources the latest translate-project result
  // still reports. Fixed.py isn't in that result anymore, so it should end
  // up with nothing.
  const collection = getDiagnosticCollection();
  collection.clear();
  collection.set(stillBroken, [diag('still an error', 'pyftc')]);

  assert.equal(collection.get(stillBroken)?.length, 1);
  assert.equal(collection.get(nowFixed), undefined);
});
