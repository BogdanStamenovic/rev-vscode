import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildAutocompleteReport, renderReportMarkdown, type AutocompleteCheckInputs } from '../src/python/checkAutocompleteReport';

const STUB_DIR = '/ext/python';

function baseInputs(overrides: Partial<AutocompleteCheckInputs> = {}): AutocompleteCheckInputs {
  return {
    languageServer: { active: true, name: 'Pylance' },
    extraPaths: [STUB_DIR],
    stubDir: STUB_DIR,
    stubDirExists: true,
    importResolves: 'yes',
    stubSdkVersion: '11.2.0',
    hubSdkVersion: '11.2.0',
    ...overrides,
  };
}

function statusOf(items: ReturnType<typeof buildAutocompleteReport>, id: string): string {
  const found = items.find((i) => i.id === id);
  assert.ok(found, `no item with id ${id}`);
  return found!.status;
}

test('buildAutocompleteReport: everything healthy is all-pass', () => {
  const items = buildAutocompleteReport(baseInputs());
  assert.equal(items.length, 5);
  for (const item of items) {
    assert.equal(item.status, 'pass', `${item.id} expected pass, got ${item.status}: ${item.detail}`);
  }
});

test('buildAutocompleteReport: no active language server fails, with a fix', () => {
  const items = buildAutocompleteReport(baseInputs({ languageServer: { active: false } }));
  const item = items.find((i) => i.id === 'language-server')!;
  assert.equal(item.status, 'fail');
  assert.ok(item.fix);
});

test('buildAutocompleteReport: stub dir missing from extraPaths fails', () => {
  assert.equal(statusOf(buildAutocompleteReport(baseInputs({ extraPaths: [] })), 'extra-paths'), 'fail');
});

test('buildAutocompleteReport: stub dir not on disk fails, independent of extraPaths', () => {
  assert.equal(statusOf(buildAutocompleteReport(baseInputs({ stubDirExists: false })), 'stub-dir'), 'fail');
});

test('buildAutocompleteReport: import resolution unknown is reported as "unknown", never a hard fail', () => {
  const items = buildAutocompleteReport(baseInputs({ importResolves: 'unknown' }));
  assert.equal(statusOf(items, 'import-resolves'), 'unknown');
});

test('buildAutocompleteReport: hub unreachable -> sdk-version check is "unknown", not "fail"', () => {
  const items = buildAutocompleteReport(baseInputs({ hubSdkVersion: undefined }));
  assert.equal(statusOf(items, 'sdk-version'), 'unknown');
});

test('buildAutocompleteReport: matching sdk versions pass', () => {
  const items = buildAutocompleteReport(baseInputs({ stubSdkVersion: '11.2.0', hubSdkVersion: '11.2.0' }));
  assert.equal(statusOf(items, 'sdk-version'), 'pass');
});

test('buildAutocompleteReport: mismatched sdk versions warn (not fail) - stale, not broken', () => {
  const items = buildAutocompleteReport(baseInputs({ stubSdkVersion: '11.2.0', hubSdkVersion: '12.0.0' }));
  const item = items.find((i) => i.id === 'sdk-version')!;
  assert.equal(item.status, 'warn');
  assert.match(item.detail, /12\.0\.0/);
});

test('buildAutocompleteReport: no bundled sdk json at all is a hard fail when the hub IS reachable', () => {
  const items = buildAutocompleteReport(baseInputs({ stubSdkVersion: undefined, hubSdkVersion: '11.2.0' }));
  assert.equal(statusOf(items, 'sdk-version'), 'fail');
});

test('renderReportMarkdown: pass items never show a Fix line even if one is set', () => {
  const items = buildAutocompleteReport(baseInputs());
  const md = renderReportMarkdown(items, new Date('2026-09-20T00:00:00Z'));
  assert.equal(md.includes('**Fix:**'), false);
});

test('renderReportMarkdown: a failing item includes its fix text', () => {
  const items = buildAutocompleteReport(baseInputs({ languageServer: { active: false } }));
  const md = renderReportMarkdown(items, new Date('2026-09-20T00:00:00Z'));
  assert.match(md, /\*\*Fix:\*\*/);
  assert.match(md, /Pylance/);
});

test('renderReportMarkdown: includes every item label as a heading', () => {
  const items = buildAutocompleteReport(baseInputs());
  const md = renderReportMarkdown(items, new Date());
  for (const item of items) {
    assert.ok(md.includes(item.label), `missing heading for ${item.label}`);
  }
});
