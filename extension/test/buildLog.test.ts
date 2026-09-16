import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseBuildLog, formatBuildLogError } from '../src/hub/buildLog';

const REAL_LOG_SAMPLE = `org/firstinspires/ftc/teamcode/pyftc/DeploySpike.java(11:18): ERROR: cannot find symbol
  symbol:   method updat()
  location: variable telemetry of type org.firstinspires.ftc.robotcore.external.Telemetry
org/firstinspires/ftc/teamcode/pyftc/DeploySpike.java(12:17): ERROR: incompatible types: java.lang.String cannot be converted to int
`;

test('parseBuildLog: parses the real hub log sample into two errors', () => {
  const errors = parseBuildLog(REAL_LOG_SAMPLE);
  assert.equal(errors.length, 2);

  assert.deepEqual(errors[0], {
    file: 'org/firstinspires/ftc/teamcode/pyftc/DeploySpike.java',
    line: 11,
    col: 18,
    severity: 'error',
    message: 'cannot find symbol',
    continuation: [
      'symbol:   method updat()',
      'location: variable telemetry of type org.firstinspires.ftc.robotcore.external.Telemetry',
    ],
  });

  assert.deepEqual(errors[1], {
    file: 'org/firstinspires/ftc/teamcode/pyftc/DeploySpike.java',
    line: 12,
    col: 17,
    severity: 'error',
    message: 'incompatible types: java.lang.String cannot be converted to int',
    continuation: [],
  });
});

test('parseBuildLog: empty log means no errors (build succeeded)', () => {
  assert.deepEqual(parseBuildLog(''), []);
  assert.deepEqual(parseBuildLog('\n\n'), []);
});

test('parseBuildLog: distinguishes WARNING from ERROR severity', () => {
  const [err] = parseBuildLog('org/x/Y.java(1:1): WARNING: deprecated API\n');
  assert.equal(err.severity, 'warning');
});

test('formatBuildLogError: joins header and continuation lines', () => {
  const [err] = parseBuildLog(REAL_LOG_SAMPLE);
  assert.equal(
    formatBuildLogError(err),
    'cannot find symbol\nsymbol:   method updat()\nlocation: variable telemetry of type org.firstinspires.ftc.robotcore.external.Telemetry'
  );
});
