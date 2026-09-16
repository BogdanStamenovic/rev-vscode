import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseConfigXml } from '../src/hub/config';

const REAL_CONFIG_SAMPLE = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<Robot type="FirstInspires-FTC">
    <LynxUsbDevice name="Control Hub Portal" serialNumber="(embedded)" parentModuleAddress="173">
        <LynxModule name="Expansion Hub 2" port="2">
            <RevRoboticsCoreHexMotor name="Kombjan" port="0" />
            <RevRoboticsUltraplanetaryHDHexMotor name="Shooter 3" port="1" />
        </LynxModule>
        <LynxModule name="Control Hub" port="173">
            <RevRoboticsUltraplanetaryHDHexMotor name="Shooter1" port="0" />
            <ControlHubImuBHI260AP name="imu" port="0" bus="0" />
        </LynxModule>
    </LynxUsbDevice>
</Robot>
`;

test('parseConfigXml: real sample yields two hubs with the right devices', () => {
  const parsed = parseConfigXml(REAL_CONFIG_SAMPLE);
  assert.equal(parsed.hubs.length, 2);

  const [expansion, control] = parsed.hubs;
  assert.equal(expansion.name, 'Expansion Hub 2');
  assert.equal(expansion.port, '2');
  assert.deepEqual(expansion.devices, [
    { name: 'Kombjan', xmlTag: 'RevRoboticsCoreHexMotor', port: '0' },
    { name: 'Shooter 3', xmlTag: 'RevRoboticsUltraplanetaryHDHexMotor', port: '1' },
  ]);

  assert.equal(control.name, 'Control Hub');
  assert.equal(control.port, '173');
  assert.deepEqual(control.devices, [
    { name: 'Shooter1', xmlTag: 'RevRoboticsUltraplanetaryHDHexMotor', port: '0' },
    { name: 'imu', xmlTag: 'ControlHubImuBHI260AP', port: '0' },
  ]);
});

test('parseConfigXml: a hub with a single device does not lose it to array-vs-object ambiguity', () => {
  const xml = `<Robot><LynxUsbDevice><LynxModule name="Hub" port="1">
    <RevRoboticsCoreHexMotor name="Solo" port="0" />
  </LynxModule></LynxUsbDevice></Robot>`;
  const parsed = parseConfigXml(xml);
  assert.equal(parsed.hubs.length, 1);
  assert.equal(parsed.hubs[0].devices.length, 1);
  assert.equal(parsed.hubs[0].devices[0].name, 'Solo');
});

test('parseConfigXml: empty robot yields no hubs', () => {
  const parsed = parseConfigXml('<Robot type="FirstInspires-FTC"></Robot>');
  assert.deepEqual(parsed.hubs, []);
});
