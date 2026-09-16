import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseDevicesOutput, parseForwardOutput } from '../src/hub/adbParse';

test('parseDevicesOutput: parses a typical `adb devices` listing', () => {
  const stdout = 'List of devices attached\nfd6f053873e61e59\tdevice\n192.168.43.1:5555\toffline\n\n';
  assert.deepEqual(parseDevicesOutput(stdout), [
    { serial: 'fd6f053873e61e59', state: 'device' },
    { serial: '192.168.43.1:5555', state: 'offline' },
  ]);
});

test('parseDevicesOutput: no devices attached', () => {
  assert.deepEqual(parseDevicesOutput('List of devices attached\n\n'), []);
});

test('parseForwardOutput: parses the chosen local port from `adb forward tcp:0 tcp:8080`', () => {
  assert.equal(parseForwardOutput('42891\n'), 42891);
  assert.equal(parseForwardOutput('12345'), 12345);
});

test('parseForwardOutput: rejects unexpected output', () => {
  assert.throws(() => parseForwardOutput('error: no devices/emulators found\n'));
  assert.throws(() => parseForwardOutput(''));
  assert.throws(() => parseForwardOutput('123abc'));
});
