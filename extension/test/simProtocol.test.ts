import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LineSplitter, parseLine, problemFor, traceView } from '../src/sim/protocol';
import { parseJavacVersion, adoptiumUrl } from '../src/sim/jdk';

test('LineSplitter: keeps a partial line until its newline arrives', () => {
  const s = new LineSplitter();
  assert.deepEqual(s.push('{"type":"a"}\n{"ty'), ['{"type":"a"}']);
  assert.deepEqual(s.push('pe":"b"}\n\n'), ['{"type":"b"}']);
});

test('parseLine: only objects with a string type are messages', () => {
  assert.deepEqual(parseLine('{"type":"state","t":1}'), { type: 'state', t: 1 });
  assert.equal(parseLine('not json'), undefined);
  assert.equal(parseLine('[1,2]'), undefined);
  assert.equal(parseLine('{"t":1}'), undefined);
});

test('problemFor: an exception with a Python location becomes an error on that line', () => {
  const p = problemFor({
    type: 'exception', exception: 'java.lang.IllegalArgumentException', phase: 'running',
    message: 'Unable to find a hardware device with name "Colector" and type DcMotor',
    py: { file: '/ws/main.py', line: 42 }, hint: 'Did you mean "Collector"?',
  });
  assert.equal(p?.file, '/ws/main.py');
  assert.equal(p?.line, 42);
  assert.equal(p?.severity, 'error');
  assert.match(p!.message, /IllegalArgumentException: Unable to find .*Colector/);
  assert.match(p!.message, /Did you mean "Collector"/);
});

test('problemFor: warnings become warnings, events without a location are skipped', () => {
  assert.equal(problemFor({ type: 'warning', code: 'double-write', message: 'x', py: { file: '/a.py', line: 3 } })?.severity, 'warning');
  assert.equal(problemFor({ type: 'exception', exception: 'E', message: 'm' }), undefined);
  assert.equal(problemFor({ type: 'state', py: { file: '/a.py', line: 1 } }), undefined);
});

test('traceView: lines per file and inline values per assigning line', () => {
  const v = traceView({
    type: 'trace',
    lines: { '/ws/main.py': [10, 11, 14] },
    changed: [{ name: 'MagDump', value: 1, file: '/ws/main.py', line: 11 }, { name: 'speed', value: 0.25, file: '/ws/main.py', line: 14 }],
  });
  assert.deepEqual(v.lines.get('/ws/main.py'), [10, 11, 14]);
  assert.equal(v.values.get('/ws/main.py')?.get(11), 'MagDump = 1');
  assert.equal(v.values.get('/ws/main.py')?.get(14), 'speed = 0.25');
});

test('parseJavacVersion: modern and legacy version strings', () => {
  assert.equal(parseJavacVersion('javac 17.0.20.1'), 17);
  assert.equal(parseJavacVersion('javac 21'), 21);
  assert.equal(parseJavacVersion('javac 1.8.0_292'), 8);
  assert.equal(parseJavacVersion('bash: javac: command not found'), undefined);
});

test('adoptiumUrl: platform and cpu mapping', () => {
  assert.equal(adoptiumUrl('linux', 'x64'), 'https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse');
  assert.equal(adoptiumUrl('darwin', 'arm64'), 'https://api.adoptium.net/v3/binary/latest/17/ga/mac/aarch64/jdk/hotspot/normal/eclipse');
  assert.equal(adoptiumUrl('win32', 'x64'), 'https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse');
});
