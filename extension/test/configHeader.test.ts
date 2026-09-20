import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseConfigHeaderLine,
  findConfigHeader,
  decideConfigChanges,
  buildRemovedDiagnostics,
} from '../src/hub/configHeader';

const REAL_HEADER_LINE = '# ── pyftc:config name="Galerija" fingerprint="9f2c1ab30c4d5e6f" generated="2026-09-20" ──';

test('parseConfigHeaderLine: parses the exact Contract 4 header line', () => {
  assert.deepEqual(parseConfigHeaderLine(REAL_HEADER_LINE), {
    name: 'Galerija',
    fingerprint: '9f2c1ab30c4d5e6f',
    generated: '2026-09-20',
  });
});

test('parseConfigHeaderLine: tolerates attribute reordering', () => {
  const reordered = '# ── pyftc:config generated="2026-09-20" fingerprint="abc123" name="X" ──';
  assert.deepEqual(parseConfigHeaderLine(reordered), { name: 'X', fingerprint: 'abc123', generated: '2026-09-20' });
});

test('parseConfigHeaderLine: an ordinary comment is not a header', () => {
  assert.equal(parseConfigHeaderLine('# just a comment'), undefined);
  assert.equal(parseConfigHeaderLine(''), undefined);
});

test('parseConfigHeaderLine: malformed (missing a required attribute) returns undefined, not a throw', () => {
  assert.equal(parseConfigHeaderLine('# ── pyftc:config name="X" fingerprint="abc123" ──'), undefined); // no generated=
  assert.equal(parseConfigHeaderLine('# ── pyftc:config ──'), undefined); // no attributes at all
  // An empty required attribute is treated as missing, same as an absent
  // one - a name/fingerprint/generated that parsed to "" is not usable.
  assert.equal(parseConfigHeaderLine('# ── pyftc:config name="" fingerprint="abc" generated="x" ──'), undefined);
});

test('findConfigHeader: finds the header among other lines and reports its index', () => {
  const text = ['# a license header', REAL_HEADER_LINE, 'import ftc', ''].join('\n');
  const found = findConfigHeader(text);
  assert.ok(found);
  assert.equal(found!.lineIndex, 1);
  assert.deepEqual(found!.header, { name: 'Galerija', fingerprint: '9f2c1ab30c4d5e6f', generated: '2026-09-20' });
  assert.equal(found!.looksLikeHeader, true);
});

test('findConfigHeader: an ordinary hand-written file has no header', () => {
  const text = 'from ftc.opmode import LinearOpMode\n\nclass X(LinearOpMode):\n    pass\n';
  assert.equal(findConfigHeader(text), undefined);
});

test('findConfigHeader: a malformed header still reports looksLikeHeader so callers can warn', () => {
  const text = '# ── pyftc:config fingerprint="abc" ──\nimport ftc\n';
  const found = findConfigHeader(text);
  assert.ok(found);
  assert.equal(found!.looksLikeHeader, true);
  assert.equal(found!.header, undefined);
});

test('findConfigHeader: only looks at the first few lines (cheap-scan cap)', () => {
  const padding = Array.from({ length: 20 }, (_, i) => `# filler line ${i}`).join('\n');
  const text = `${padding}\n${REAL_HEADER_LINE}\n`;
  assert.equal(findConfigHeader(text), undefined);
});

test('decideConfigChanges: files whose fingerprint matches are not stale', () => {
  const decision = decideConfigChanges(
    [{ id: 'a', scanned: { looksLikeHeader: true, header: { name: 'A', fingerprint: 'same', generated: 'x' }, lineIndex: 0 } }],
    'same'
  );
  assert.deepEqual(decision.stale, []);
  assert.deepEqual(decision.malformed, []);
});

test('decideConfigChanges: a mismatched fingerprint is stale', () => {
  const decision = decideConfigChanges(
    [{ id: 'a', scanned: { looksLikeHeader: true, header: { name: 'A', fingerprint: 'old', generated: 'x' }, lineIndex: 0 } }],
    'new'
  );
  assert.equal(decision.stale.length, 1);
  assert.equal(decision.stale[0].id, 'a');
  assert.equal(decision.stale[0].header.fingerprint, 'old');
});

test('decideConfigChanges: an unparseable header is reported as malformed, not stale', () => {
  const decision = decideConfigChanges(
    [{ id: 'broken', scanned: { looksLikeHeader: true, header: undefined, lineIndex: 0 } }],
    'new'
  );
  assert.deepEqual(decision.stale, []);
  assert.deepEqual(decision.malformed, ['broken']);
});

test('decideConfigChanges: mixed set of matching/stale/malformed', () => {
  const decision = decideConfigChanges(
    [
      { id: 'ok', scanned: { looksLikeHeader: true, header: { name: 'A', fingerprint: 'cur', generated: 'x' }, lineIndex: 0 } },
      { id: 'stale', scanned: { looksLikeHeader: true, header: { name: 'B', fingerprint: 'old', generated: 'x' }, lineIndex: 0 } },
      { id: 'broken', scanned: { looksLikeHeader: true, header: undefined, lineIndex: 0 } },
    ],
    'cur'
  );
  assert.deepEqual(decision.stale.map((s) => s.id), ['stale']);
  assert.deepEqual(decision.malformed, ['broken']);
});

const REMOVED = [{ name: 'Old Sensor', field: 'oldSensor' }];

test('buildRemovedDiagnostics: places the warning on the field line after the marker comment', () => {
  const text = [
    'class X:',
    '    def run(self):',
    '        # pyftc: no longer in the configuration',
    '        oldSensor: DcMotor',
    '        arm: DcMotor',
  ].join('\n');
  const diags = buildRemovedDiagnostics(text, REMOVED);
  assert.deepEqual(diags, [{ line: 3, message: "Device 'Old Sensor' is no longer in the hardware configuration." }]);
});

test('buildRemovedDiagnostics: skips blank lines between the marker and the field', () => {
  const text = ['        # pyftc: no longer in the configuration', '', '        oldSensor: DcMotor'].join('\n');
  const diags = buildRemovedDiagnostics(text, REMOVED);
  assert.deepEqual(diags, [{ line: 2, message: "Device 'Old Sensor' is no longer in the hardware configuration." }]);
});

test('buildRemovedDiagnostics: whole-word match does not confuse "arm" with "armLeft"', () => {
  const removed = [{ name: 'Arm', field: 'arm' }];
  const text = ['        # pyftc: no longer in the configuration', '        armLeft: DcMotor', '        arm: DcMotor'].join('\n');
  const diags = buildRemovedDiagnostics(text, removed);
  // The scanner only looks at the first non-blank line after the marker,
  // and "armLeft" does not whole-word-match "arm" - falls through to the
  // unmatched fallback rather than a wrong match.
  assert.equal(diags.length, 1);
  assert.match(diags[0].message, /marker comment not found/);
});

test('buildRemovedDiagnostics: no removed devices -> no diagnostics', () => {
  assert.deepEqual(buildRemovedDiagnostics('anything', []), []);
});

test('buildRemovedDiagnostics: a removed device with no marker in the file falls back to line 0', () => {
  const diags = buildRemovedDiagnostics('class X:\n    pass\n', REMOVED);
  assert.equal(diags.length, 1);
  assert.equal(diags[0].line, 0);
  assert.match(diags[0].message, /marker comment not found/);
});

test('buildRemovedDiagnostics: multiple removed devices each get their own diagnostic', () => {
  const removed = [
    { name: 'Old Sensor', field: 'oldSensor' },
    { name: 'Old Motor', field: 'oldMotor' },
  ];
  const text = [
    '        # pyftc: no longer in the configuration',
    '        oldSensor: DcMotor',
    '        # pyftc: no longer in the configuration',
    '        oldMotor: DcMotor',
  ].join('\n');
  const diags = buildRemovedDiagnostics(text, removed);
  assert.deepEqual(
    diags.map((d) => d.line),
    [1, 3]
  );
});
