import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hostKind } from '../src/commands/checkAutocomplete';

// The distinction that matters: Pylance only loads on Microsoft's build, so
// recommending it anywhere else is advice that cannot be followed.
test('hostKind: official VS Code', () => {
  assert.equal(hostKind('Visual Studio Code'), 'microsoft');
  assert.equal(hostKind('Visual Studio Code - Insiders'), 'microsoft');
});

test('hostKind: open-source builds', () => {
  assert.equal(hostKind('Code - OSS'), 'open-source');
  assert.equal(hostKind('VSCodium'), 'open-source');
  assert.equal(hostKind('Cursor'), 'open-source');
});
