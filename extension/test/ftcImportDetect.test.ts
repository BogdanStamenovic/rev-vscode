import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hasFtcImport, stubDirFor } from '../src/python/ftcImportDetect';

test('hasFtcImport: plain "import ftc"', () => {
  assert.equal(hasFtcImport('import ftc\n'), true);
});

test('hasFtcImport: "import ftc.hardware"', () => {
  assert.equal(hasFtcImport('import ftc.hardware\n'), true);
});

test('hasFtcImport: "from ftc.opmode import LinearOpMode, TeleOp"', () => {
  assert.equal(hasFtcImport('from ftc.opmode import LinearOpMode, TeleOp\n'), true);
});

test('hasFtcImport: indented import (inside a try/except, etc.)', () => {
  assert.equal(hasFtcImport('try:\n    import ftc.hardware\nexcept ImportError:\n    pass\n'), true);
});

test('hasFtcImport: no import at all', () => {
  assert.equal(hasFtcImport('x = 1\nprint(x)\n'), false);
});

test('hasFtcImport: unrelated imports do not false-positive', () => {
  assert.equal(hasFtcImport('import os\nimport sys\nfrom math import sqrt\n'), false);
});

test('hasFtcImport: a package that merely starts with "ftc" is not a match ("ftclib" != "ftc")', () => {
  assert.equal(hasFtcImport('import ftclib\n'), false);
  assert.equal(hasFtcImport('from ftclib.thing import X\n'), false);
});

test('hasFtcImport: a comment mentioning ftc does not count', () => {
  assert.equal(hasFtcImport('# see ftc.hardware for details\n'), false);
});

test('stubDirFor: joins the extension path with "python"', () => {
  assert.equal(stubDirFor('/opt/rev-vscode-ext'), '/opt/rev-vscode-ext/python');
});
