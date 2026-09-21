import { test } from 'node:test';
import assert from 'node:assert/strict';
import { HUB_PREFIX, hubFilesForPack, isDeployedSource, isGeneratedManual, opModeNames, orphanGroups } from '../src/packs';

test('isDeployedSource mirrors the translator: skips hidden dirs, venvs, stubs and __init__', () => {
  assert.ok(isDeployedSource('main.py'));
  assert.ok(isDeployedSource('autos/left.py'));
  assert.ok(!isDeployedSource('Starter.txt'));
  assert.ok(!isDeployedSource('.pyftc/stubs/ftc/hardware.py'));
  assert.ok(!isDeployedSource('.venv/lib/x.py'));
  assert.ok(!isDeployedSource('pkg/__init__.py'));
});

test('opModeNames lists what the Driver Hub shows', () => {
  const src = '@TeleOp(name="Main", group="pyftc")\nclass Main: ...\n@Autonomous(name = "Left")\nclass Left: ...';
  assert.deepEqual(opModeNames(src), ['Main (TeleOp)', 'Left (Autonomous)']);
  assert.deepEqual(opModeNames(''), []);
});

test('isGeneratedManual: the generated man page yes, a user note with the same name no', () => {
  assert.ok(isGeneratedManual('# Main: robot reference\n\nGenerated from hardware configuration "X". Configuration fingerprint `abc`.'));
  assert.ok(!isGeneratedManual('# Main\n\nmy notes about the shooter'));
});

const translated = [
  { source: '/ws/main.py', className: 'Main', hubPath: `/src/${HUB_PREFIX}main/Main.java` },
  { source: '/ws/main.py', className: 'Cycle', hubPath: `/src/${HUB_PREFIX}main/Cycle.java` },
  { source: '/ws/aftercare.py', className: 'aftercare', hubPath: `/src/${HUB_PREFIX}aftercare/aftercare.java` },
];

test('hubFilesForPack: the pack\'s classes, including copies left at the old flat location', () => {
  const existing = new Set([`${HUB_PREFIX}main/Main.java`, `${HUB_PREFIX}Main.java`, `${HUB_PREFIX}aftercare/aftercare.java`]);
  assert.deepEqual(hubFilesForPack('/ws/main.py', translated, existing), [`${HUB_PREFIX}Main.java`, `${HUB_PREFIX}main/Main.java`]);
});

test('hubFilesForPack: only files actually on the hub', () => {
  assert.deepEqual(hubFilesForPack('/ws/main.py', translated, new Set()), []);
});

test('orphanGroups: hub files no local pack produces, one group per pack directory or flat file', () => {
  const existing = [
    `${HUB_PREFIX}main/Main.java`,
    `${HUB_PREFIX}starter/StarterPack.java`,
    `${HUB_PREFIX}starter/Helper.java`,
    `${HUB_PREFIX}Old.java`,
    'org/firstinspires/ftc/teamcode/HandWritten.java',
    `${HUB_PREFIX}notes.txt`,
  ];
  const produced = new Set([`${HUB_PREFIX}main/Main.java`]);
  const groups = orphanGroups(existing, produced, new Set());
  assert.deepEqual([...groups.keys()].sort(), ['Old.java', 'starter']);
  assert.equal(groups.get('starter')!.length, 2);
});
