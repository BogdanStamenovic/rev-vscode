import { test } from 'node:test';
import assert from 'node:assert/strict';
import { stripPassphrase } from '../src/hub/rcinfoTypes';

const SAMPLE_RCINFO = {
  activeConfigName: 'test_config',
  appUpdateRequiresReboot: false,
  availableChannels: [1, 6, 11],
  chOsVersion: '1.0',
  currentChannel: 6,
  deviceName: 'My Control Hub',
  ftcUserAgentCategory: 'RC',
  includedFirmwareFileVersion: '1.9.2',
  isREVControlHub: true,
  networkName: 'FTC-1234',
  passphrase: 'super-secret-wifi-password',
  rcVersion: '11.2',
  revHubNamesAndVersions: [{ name: 'Control Hub', firmwareVersion: '1.9.2' }],
  sdkVersion: '11.2.0',
  serialNumber: 'ABC123',
  serverIsAlive: true,
  serverUrl: 'http://192.168.43.1:8080',
  supports5GhzAp: true,
  supportsOtaUpdate: true,
  webSocketApiVersion: '1',
};

test('stripPassphrase: removes passphrase, keeps everything else', () => {
  const cleaned = stripPassphrase(SAMPLE_RCINFO);
  assert.equal('passphrase' in cleaned, false);
  assert.equal(cleaned.deviceName, 'My Control Hub');
  assert.equal(cleaned.activeConfigName, 'test_config');
  assert.equal(cleaned.revHubNamesAndVersions.length, 1);
});

test('stripPassphrase: never lets passphrase through JSON.stringify either', () => {
  const cleaned = stripPassphrase(SAMPLE_RCINFO);
  assert.equal(JSON.stringify(cleaned).includes('super-secret-wifi-password'), false);
});

test('stripPassphrase: tolerates a missing revHubNamesAndVersions field', () => {
  const cleaned = stripPassphrase({ activeConfigName: 'x', passphrase: 'y' });
  assert.deepEqual(cleaned.revHubNamesAndVersions, []);
});

test('stripPassphrase: rejects non-object input', () => {
  assert.throws(() => stripPassphrase(null));
  assert.throws(() => stripPassphrase('not an object'));
});
