import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mapJavaLineToPython } from '../src/hub/lineMap';

// From Contract 3's own example: lineMap: [0, 3, 3, 4]
const LINE_MAP = [0, 3, 3, 4];

test('mapJavaLineToPython: maps a real line to its python line', () => {
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 2), { pythonLine: 3, fallback: false });
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 3), { pythonLine: 3, fallback: false });
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 4), { pythonLine: 4, fallback: false });
});

test('mapJavaLineToPython: 0 means synthetic -> falls back to line 1', () => {
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 1), { pythonLine: 1, fallback: true });
});

test('mapJavaLineToPython: out-of-range java line -> falls back to line 1', () => {
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 99), { pythonLine: 1, fallback: true });
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, 0), { pythonLine: 1, fallback: true });
  assert.deepEqual(mapJavaLineToPython(LINE_MAP, -5), { pythonLine: 1, fallback: true });
});
