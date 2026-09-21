// Reproduces the Wi-Fi adb failure from the extension log (a stale "offline"
// entry that `adb connect` reports as "already connected") against a fake adb
// with the same behaviour, and checks the read path recovers from it.
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';

const FAKE = path.resolve(__dirname, '../../test/fixtures/fake_adb_wifi.py');
const XML = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<Robot type="FirstInspires-FTC">
  <LynxUsbDevice name="Control Hub Portal" serialNumber="(embedded)" parentModuleAddress="173">
    <LynxModule name="Control Hub" port="173">
      <RevRoboticsUltraPlanetaryHdHexMotor name="shooter" port="0" />
      <RevRoboticsUltraPlanetaryHdHexMotor name="Collector" port="1" />
    </LynxModule>
  </LynxUsbDevice>
</Robot>
`;

let dir: string;
const conn = { baseUrl: 'http://192.168.43.1:8080', transport: 'wifi-direct' } as never;

function setState(name: string, value: string | undefined): void {
  const p = path.join(dir, name);
  if (value === undefined) fs.rmSync(p, { force: true });
  else fs.writeFileSync(p, value);
}

function calls(): { start: number; end: number; argv: string }[] {
  const p = path.join(dir, 'calls.log');
  if (!fs.existsSync(p)) return [];
  return fs.readFileSync(p, 'utf8').trim().split('\n').map((l) => {
    const [s, e, ...rest] = l.split(' ');
    return { start: Number(s), end: Number(e), argv: rest.join(' ') };
  });
}

// Settings are read when the vscode shim loads, so it is configured before
// the first import of anything that pulls it in.
process.env.FAKE_ADB_STATE_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'fake-adb-'));
process.env.REVFTC_SHIM_CONFIG = JSON.stringify({ adbPath: FAKE });
const load = async () => ({ ...(await import('../src/hub/adb')), ...(await import('../src/hub/configFetch')) });
let seq = 0;

beforeEach(() => {
  dir = process.env.FAKE_ADB_STATE_DIR!;
  for (const f of fs.readdirSync(dir)) fs.rmSync(path.join(dir, f));
  const xmlPath = path.join(dir, `config.xml`);
  fs.writeFileSync(xmlPath, XML);
  process.env.FAKE_HUB_CONFIG_XML = xmlPath;
});

const name = () => `Cfg${seq++}`; // a fresh config name per test sidesteps the read cache

test('a stale offline entry is dropped and reconnected, and the read succeeds', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'offline');
  const { xml } = await fetchActiveConfigXml(conn, name());
  assert.equal(xml, XML);
  const argv = calls().map((c) => c.argv);
  assert.ok(argv.includes('disconnect 192.168.43.1:5555'), argv.join('\n'));
  assert.ok(argv.indexOf('disconnect 192.168.43.1:5555') < argv.indexOf('connect 192.168.43.1:5555'));
});

test('a healthy link is used as-is: no `adb connect` on every read', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  await fetchActiveConfigXml(conn, name());
  assert.ok(!calls().some((c) => c.argv.startsWith('connect')), calls().map((c) => c.argv).join('\n'));
});

test('a link that drops between the state check and the read is recovered with one retry', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  setState('drop_once', '');
  const { xml } = await fetchActiveConfigXml(conn, name());
  assert.equal(xml, XML);
});

test('a truncated read is rejected and re-read, never returned as a config', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  setState('truncate_once', '');
  const { xml } = await fetchActiveConfigXml(conn, name());
  assert.equal(xml, XML);
});

test('readers that accept a recent copy share one read', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  const n = name();
  const opts = { maxAgeMs: 15_000 };
  await Promise.all([fetchActiveConfigXml(conn, n, opts), fetchActiveConfigXml(conn, n, opts), fetchActiveConfigXml(conn, n, opts)]);
  assert.equal(calls().filter((c) => c.argv.includes('shell cat')).length, 1);
});

test('a fresh read never reuses one that started before it asked', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  const n = name();
  const early = fetchActiveConfigXml(conn, n, { maxAgeMs: 15_000 });
  const changed = XML.replace('Collector', 'Winch');
  fs.writeFileSync(process.env.FAKE_HUB_CONFIG_XML!, changed); // the robot gets reconfigured
  const fresh = await fetchActiveConfigXml(conn, n);
  await early;
  assert.equal(fresh.xml, changed);
});

test('concurrent fresh readers never run adb processes at the same time', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  const n = name();
  await Promise.all([fetchActiveConfigXml(conn, n), fetchActiveConfigXml(conn, n), fetchActiveConfigXml(conn, n)]);
  const log = calls();
  const sorted = [...log].sort((a, b) => a.start - b.start);
  for (let i = 1; i < sorted.length; i++) {
    assert.ok(sorted[i].start >= sorted[i - 1].end, `adb calls overlapped: ${sorted[i - 1].argv} / ${sorted[i].argv}`);
  }
});

test('maxAgeMs reuses a recent read instead of going back to the hub', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('entry', 'device');
  const n = name();
  await fetchActiveConfigXml(conn, n);
  const before = calls().length;
  await fetchActiveConfigXml(conn, n, { maxAgeMs: 15_000 });
  assert.equal(calls().length, before);
});

test('an unreachable hub gives a plain reason, not a stack of adb noise', async () => {
  const { fetchActiveConfigXml } = await load();
  setState('connect', 'fail');
  await assert.rejects(fetchActiveConfigXml(conn, name()), /No adb connection to the hub/);
});

test('isTransientAdbError covers the messages seen in the real log', async () => {
  const { isTransientAdbError } = await load();
  assert.ok(isTransientAdbError('adb shell cat /sdcard/FIRST/FGC2026-Incheon.xml failed: adb: device offline'));
  assert.ok(isTransientAdbError("error: device '192.168.43.1:5555' not found"));
  assert.ok(!isTransientAdbError('cat: /sdcard/FIRST/Nope.xml: No such file or directory'));
});
