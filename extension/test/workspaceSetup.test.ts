import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  STUB_LINK_REL,
  UnparseableJsonError,
  isStaleStubPath,
  mergeExtensionsJson,
  mergeExtraPaths,
  mergePyrightConfig,
  parsePythonProbe,
  pythonIsNewEnough,
  recommendedExtensions,
} from '../src/python/workspaceSetup';

const STUB = '/home/u/.vscode-oss/extensions/bogdanstamenovic.rev-vscode-0.2.0/python';
const OLD = '/home/u/.vscode-oss/extensions/bogdanstamenovic.rev-vscode-0.1.0/python';

test('isStaleStubPath: any installed version of this extension, and nothing else', () => {
  assert.ok(isStaleStubPath(OLD, STUB));
  assert.ok(isStaleStubPath(STUB, STUB));
  assert.ok(!isStaleStubPath('/home/u/my-libs', STUB));
  assert.ok(!isStaleStubPath(STUB_LINK_REL, STUB));
});

test('mergeExtraPaths: replaces the versioned install path with the link, keeps the user\'s own entries', () => {
  const { value, changed } = mergeExtraPaths(['/home/u/my-libs', OLD], STUB);
  assert.deepEqual(value, ['/home/u/my-libs', STUB_LINK_REL]);
  assert.ok(changed);
});

test('mergeExtraPaths: already set up is unchanged', () => {
  const { value, changed } = mergeExtraPaths([STUB_LINK_REL], STUB);
  assert.deepEqual(value, [STUB_LINK_REL]);
  assert.ok(!changed);
});

test('mergePyrightConfig: creates a fresh file', () => {
  const { text, changed } = mergePyrightConfig(undefined, STUB);
  assert.ok(changed);
  assert.deepEqual(JSON.parse(text), { extraPaths: [STUB_LINK_REL], typeCheckingMode: 'basic' });
});

test('mergePyrightConfig: fixes the absolute path an earlier setup wrote, keeps other keys', () => {
  const before = JSON.stringify({ extraPaths: [OLD], typeCheckingMode: 'standard', reportMissingModuleSource: 'none' });
  const { text, changed } = mergePyrightConfig(before, STUB);
  assert.ok(changed);
  assert.deepEqual(JSON.parse(text), {
    extraPaths: [STUB_LINK_REL],
    typeCheckingMode: 'standard',
    reportMissingModuleSource: 'none',
  });
});

test('mergePyrightConfig: second run is a byte-for-byte no-op', () => {
  const first = mergePyrightConfig(undefined, STUB).text;
  const second = mergePyrightConfig(first, STUB);
  assert.ok(!second.changed);
  assert.equal(second.text, first);
});

test('mergePyrightConfig: a file with comments is refused, not rewritten', () => {
  assert.throws(() => mergePyrightConfig('{ // mine\n "extraPaths": [] }', STUB), UnparseableJsonError);
});

test('mergeExtensionsJson: appends only what is missing', () => {
  const before = JSON.stringify({ recommendations: ['someone.else', 'detachhead.basedpyright'] });
  const { text, changed } = mergeExtensionsJson(before, recommendedExtensions('open-source'));
  assert.ok(changed);
  assert.deepEqual(JSON.parse(text).recommendations, ['someone.else', 'detachhead.basedpyright', 'bogdanstamenovic.rev-vscode']);
  assert.ok(!mergeExtensionsJson(text, recommendedExtensions('open-source')).changed);
});

test('recommendedExtensions: never recommends Pylance on an open-source build', () => {
  assert.ok(!recommendedExtensions('open-source').includes('ms-python.vscode-pylance'));
  assert.ok(recommendedExtensions('microsoft').includes('ms-python.vscode-pylance'));
});

test('parsePythonProbe / pythonIsNewEnough', () => {
  assert.deepEqual(parsePythonProbe('/usr/bin/python3\n3.14\n'), { executable: '/usr/bin/python3', major: 3, minor: 14 });
  assert.equal(parsePythonProbe('garbage'), undefined);
  assert.ok(pythonIsNewEnough(3, 10));
  assert.ok(!pythonIsNewEnough(3, 9));
  assert.ok(pythonIsNewEnough(4, 0));
});
