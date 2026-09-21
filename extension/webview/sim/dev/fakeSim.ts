// A stand-in for the Java simulator process plus the extension host, good enough to develop the UI
// in a plain browser. It speaks the same messages the extension relays.
import type {
  DeviceInfo,
  DeviceState,
  ExtToWebview,
  GamepadState,
  Phase,
  ReadyMsg,
  SceneLayout,
  SensorValue,
  SimEvent,
  SimMsg,
  StateMsg,
  WebviewToExt,
} from '../protocol';
import { emptyGamepad } from '../protocol';
import { MAIN_PY, lineOf, linesBetween } from './fakeSource';

const PY = '/home/team/robot/main.py';
const L = {
  dirLF: lineOf('self.lf.setDirection'),
  dirLB: lineOf('self.lb.setDirection'),
  lf: lineOf('self.lf.setPower'),
  lb: lineOf('self.lb.setPower'),
  rf: lineOf('self.rf.setPower'),
  rb: lineOf('self.rb.setPower'),
  shooter1: lineOf('self.shooter.setPower(0.8)'),
  shooter0: lineOf('self.shooter.setPower(0.3)'),
  intake: lineOf('intake.setPower'),
  chainHi: lineOf('chain_drop.setPosition(0.8)'),
  chainLo: lineOf('chain_drop.setPosition(0.25)'),
  colector: lineOf('"Colector"'),
  phaseSet: lineOf('cycle.phase = (cycle.phase + 1)'),
  countSet: lineOf('cycle.count += 1'),
  stateShoot: lineOf('self.state = "SHOOTING"'),
  stateDump: lineOf('self.state = "DUMPING"'),
  stateIdle: lineOf('self.state = "IDLE"', 1),
};

interface Act {
  power: number;
  direction: 'FORWARD' | 'REVERSE';
  omega: number;
  angle: number;
  position: number;
}

export class FakeSim {
  t = 0;
  phase: Phase = 'idle';
  opMode: string | null = null;
  paused = false;
  speed = 1;
  autoDrive = true;
  private timer = 0;
  private lastWall = 0;
  private telemAt = 0;
  private gp: Record<number, GamepadState> = { 1: emptyGamepad(), 2: emptyGamepad() };
  private prevGp: Record<number, GamepadState> = { 1: emptyGamepad(), 2: emptyGamepad() };
  private acts: Record<string, Act> = {};
  private servos: Record<string, { pos: number; angle: number; dir: 'FORWARD' | 'REVERSE' }> = {};
  private sensors: Record<string, SensorValue> = {};
  private events: SimEvent[] = [];
  private cycle = { count: 0, phase: 0, last_ms: 0 };
  private runStart = 0;
  private warned = false;
  private layout: SceneLayout | null = null;
  private lastPowers: Record<string, number> = {};

  constructor(private deliver: (m: ExtToWebview) => void) {
    try {
      const s = localStorage.getItem('harness-layout');
      this.layout = s ? (JSON.parse(s) as SceneLayout) : null;
    } catch {
      this.layout = null;
    }
  }

  private sim(msg: SimMsg): void {
    this.deliver({ type: 'sim', msg });
  }

  handle(m: WebviewToExt): void {
    switch (m.type) {
      case 'ready':
        this.deliver({ type: 'hello', layout: this.layout, workspaceName: 'harness' });
        this.deliver({ type: 'status', state: 'compiling', message: 'translating main.py' });
        setTimeout(() => this.boot(), 250);
        break;
      case 'layoutChanged':
        this.layout = m.layout;
        try {
          localStorage.setItem('harness-layout', JSON.stringify(m.layout));
        } catch {
          /* private mode */
        }
        break;
      case 'rebuild':
        this.deliver({ type: 'status', state: 'compiling', message: 'rebuilding' });
        setTimeout(() => this.boot(), 400);
        break;
      case 'openSource':
        console.log('[harness] openSource', m.file, m.line);
        (window as unknown as { lastOpenSource: unknown }).lastOpenSource = m;
        break;
      case 'openGamepadBridge':
        this.deliver({ type: 'bridgeInfo', url: 'http://127.0.0.1:43117/' });
        break;
      case 'sim':
        this.command(m.msg);
        break;
    }
  }

  private boot(): void {
    this.t = 0;
    this.phase = 'idle';
    this.opMode = null;
    this.warned = false;
    this.cycle = { count: 0, phase: 0, last_ms: 0 };
    for (const n of ['LF', 'RF', 'LB', 'RB', 'shooter', 'intake']) this.acts[n] = { power: 0, direction: 'FORWARD', omega: 0, angle: 0, position: 0 };
    this.servos = { chainDrop: { pos: 0.25, angle: -67.5, dir: 'FORWARD' }, claw: { pos: 0.5, angle: 0, dir: 'REVERSE' } };
    this.deliver({ type: 'status', state: 'running', message: 'simulator ready' });
    this.deliver({ type: 'compileErrors', errors: [] });
    this.deliver({ type: 'sources', files: { [PY]: MAIN_PY } });
    this.sim(READY);
    window.clearInterval(this.timer);
    this.lastWall = performance.now();
    this.timer = window.setInterval(() => this.step(), 1000 / 30);
  }

  private command(c: import('../protocol').SimCommand): void {
    switch (c.type) {
      case 'init':
        if (this.phase === 'idle' || this.phase === 'stopped' || this.phase === 'crashed') {
          this.opMode = c.opMode;
          this.setPhase('init');
          this.acts.LF.direction = 'REVERSE';
          this.acts.LB.direction = 'REVERSE';
          this.event('LF', 'setDirection', 'REVERSE', L.dirLF);
          this.event('LB', 'setDirection', 'REVERSE', L.dirLB);
          this.cycle = { count: 0, phase: 0, last_ms: 0 };
          this.telemetry(['Initialised. Press START.']);
        }
        break;
      case 'start':
        if (this.phase === 'init') {
          this.setPhase('running');
          this.runStart = this.t;
        }
        break;
      case 'stop':
        if (this.phase === 'init' || this.phase === 'running') {
          this.setPhase('stopped');
          for (const a of Object.values(this.acts)) a.power = 0;
          this.telemetry([]);
        }
        break;
      case 'gamepad':
        this.gp[c.index] = { ...c.state };
        break;
      case 'sensor':
        this.sensors[c.device] = c.value;
        break;
      case 'pause':
        this.paused = true;
        break;
      case 'resume':
        this.paused = false;
        break;
      case 'speed':
        this.speed = c.factor;
        break;
      default:
        break;
    }
  }

  private setPhase(p: Phase): void {
    this.phase = p;
    this.events.push({ t: this.t, dev: 'opmode', op: 'phase', v: p });
  }

  private event(dev: string, op: string, v: unknown, line: number): void {
    this.events.push({ t: this.t, dev, op, v, py: { file: PY, line } });
  }

  private telemetry(lines: string[]): void {
    this.sim({ type: 'telemetry', t: this.t, lines, log: [] });
  }

  throwException(): void {
    this.sim({
      type: 'exception',
      t: this.t,
      phase: this.phase,
      exception: 'java.lang.IllegalArgumentException',
      message: 'Unable to find a hardware device with name "Colector" and type DcMotor',
      py: { file: PY, line: L.colector },
      frames: [{ class: 'org.firstinspires.ftc.teamcode.pyftc.Main', method: 'runOpMode', javaLine: 142, py: { file: PY, line: L.colector } }],
      driverHub: 'User code threw an uncaught exception: IllegalArgumentException - Unable to find a hardware device with name "Colector" and type DcMotor',
    });
    this.setPhase('crashed');
    for (const a of Object.values(this.acts)) a.power = 0;
  }

  private step(): void {
    const now = performance.now();
    const wall = Math.min(0.1, (now - this.lastWall) / 1000);
    this.lastWall = now;
    if (this.paused) {
      this.emit();
      return;
    }
    const dt = wall * this.speed;
    this.t += dt;
    if (this.phase === 'running') this.loop(dt);
    for (const [name, a] of Object.entries(this.acts)) {
      const orient = name === 'shooter' ? -1 : 1;
      const raw = a.power * (a.direction === 'REVERSE' ? -1 : 1) * orient;
      const free = name === 'shooter' ? 125 : name === 'intake' ? 130 : 300;
      const target = (raw * free * 2 * Math.PI) / 60;
      a.omega += (target - a.omega) * Math.min(1, dt * 8);
      if (Math.abs(a.omega) < 0.05 && a.power === 0) a.omega = 0;
      a.angle += a.omega * dt;
      a.position += ((a.omega * dt) / (2 * Math.PI)) * 560 * (a.direction === 'REVERSE' ? -1 : 1) * orient;
    }
    for (const s of Object.values(this.servos)) {
      const phys = s.dir === 'REVERSE' ? 1 - s.pos : s.pos;
      const target = (phys - 0.5) * 270;
      const maxStep = 300 * dt;
      s.angle += Math.max(-maxStep, Math.min(maxStep, target - s.angle));
    }
    this.emit();
  }

  private loop(dt: number): void {
    let g = this.gp[1];
    const idle = Object.values(g).every((v) => v === 0 || v === false);
    if (this.autoDrive && idle) {
      const k = this.t - this.runStart;
      g = { ...emptyGamepad(), left_stick_y: -0.6 * Math.max(0, Math.sin(k * 0.6)), right_stick_x: 0.5 * Math.sin(k * 0.35) };
    }
    const y = -g.left_stick_y;
    const x = g.right_stick_x;
    const pw: Record<string, number> = { LF: y + x, LB: y + x, RF: y - x, RB: y - x };
    for (const [n, v] of Object.entries(pw)) this.setPower(n, Math.max(-1, Math.min(1, Math.round(v * 100) / 100)), L[n.toLowerCase() as 'lf' | 'lb' | 'rf' | 'rb']);
    const p1 = this.prevGp[1];
    const real = this.gp[1];
    if (real.a && !p1.a) {
      this.cycle.phase = (this.cycle.phase + 1) % 3;
      this.cycle.count++;
      this.cycle.last_ms = Math.round(this.t * 1000);
      this.events.push({ t: this.t, dev: 'gamepad1', op: 'input', v: { a: true } });
    }
    const pressed = real.a && !p1.a;
    if (real.y && !p1.y) this.throwException();
    this.trace(y, x, pressed, Boolean(real.y));
    this.prevGp[1] = { ...real };
    this.setPower('shooter', this.cycle.phase === 1 ? 0.8 : 0.3, this.cycle.phase === 1 ? L.shooter1 : this.cycle.phase === 2 ? L.shooter0 : lineOf('self.shooter.setPower(0.3)', 1));
    this.setPower('intake', Math.round((real.right_trigger - real.left_trigger) * 100) / 100 || (this.cycle.phase === 2 ? -0.6 : 0.4), L.intake);
    const cd = this.cycle.phase === 2 ? 0.8 : 0.25;
    if (this.servos.chainDrop.pos !== cd) {
      this.servos.chainDrop.pos = cd;
      this.event('chainDrop', 'setPosition', cd, cd > 0.5 ? L.chainHi : L.chainLo);
    }
    const claw = Math.round((0.5 + 0.45 * Math.sin((this.t - this.runStart) * 1.3)) * 100) / 100;
    this.servos.claw.pos = claw;
    // A deliberate double write a few seconds in, like `lf.setPower(0.8)` followed by `lf.setPower(0)`.
    if (!this.warned && this.t - this.runStart > 3) {
      this.warned = true;
      this.event('LF', 'setPower', 0.8, L.lf);
      this.event('LF', 'setPower', this.acts.LF.power, L.lb);
      this.sim({
        type: 'warning',
        t: this.t,
        code: 'double-write',
        device: 'LF',
        message: 'LF.setPower() was called twice in one loop iteration with different values: 0.80 at main.py:' + L.lf + ', then ' + this.acts.LF.power.toFixed(2) + ' at main.py:' + L.lb + '. Only the last value stays; the first one reaches the motor for about 4 ms.',
        py: { file: PY, line: L.lb },
        related: [{ file: PY, line: L.lf }],
      });
    }
    if (this.t - this.telemAt > 0.25) {
      this.telemAt = this.t;
      this.telemetry([
        `Phase: ${this.cycle.phase}   cycles: ${this.cycle.count}`,
        `Drive   y ${y.toFixed(2)}   x ${x.toFixed(2)}`,
        `LF ${this.acts.LF.power.toFixed(2)}  RF ${this.acts.RF.power.toFixed(2)}`,
        `Shooter ${this.acts.shooter.power.toFixed(2)}`,
      ]);
    }
    void dt;
  }

  private iteration = 0;
  private prevCycle = '';

  // Lines of one loop iteration, following the branches of the fake source.
  private trace(y: number, x: number, pressed: boolean, triangle: boolean): void {
    this.iteration++;
    const lines = linesBetween('while self.opModeIsActive()', 'cycle = self.cycle_register');
    lines.push(lineOf('if self.gamepad1.cross and not was_cross'));
    if (pressed) lines.push(L.phaseSet, L.countSet, lineOf('cycle.last_ms = self.timer'));
    lines.push(lineOf('was_cross = self.gamepad1.cross'), lineOf('if cycle.phase == 1:'));
    const ph = this.cycle.phase;
    if (ph === 1) lines.push(L.stateShoot, L.shooter1);
    else {
      lines.push(lineOf('elif cycle.phase == 2:'));
      if (ph === 2) lines.push(L.stateDump, L.shooter0);
      else lines.push(lineOf('else:', 0), L.stateIdle, lineOf('self.shooter.setPower(0.3)', 1));
    }
    lines.push(L.intake, lineOf('if cycle.phase == 2:', 1));
    lines.push(ph === 2 ? L.chainHi : L.chainLo);
    if (ph !== 2) lines.push(lineOf('else:', 1));
    lines.push(lineOf('if self.gamepad1.triangle'));
    if (triangle) lines.push(L.colector);
    lines.push(...linesBetween('self.telemetry.addData("Phase"', 'self.telemetry.update()', ));
    const cyc = JSON.stringify(this.cycle);
    const changed: Array<{ name: string; value: unknown; file?: string; line?: number }> = [];
    if (cyc !== this.prevCycle && this.prevCycle) {
      changed.push({ name: 'cycle.phase', value: ph, file: PY, line: L.phaseSet }, { name: 'cycle.count', value: this.cycle.count, file: PY, line: L.countSet });
      changed.push({ name: 'self.state', value: ph === 1 ? 'SHOOTING' : ph === 2 ? 'DUMPING' : 'IDLE', file: PY, line: ph === 1 ? L.stateShoot : ph === 2 ? L.stateDump : L.stateIdle });
    }
    this.prevCycle = cyc;
    this.sim({
      type: 'trace',
      t: this.t,
      iteration: this.iteration,
      lines: { [PY]: [...new Set(lines)].sort((a, b) => a - b) },
      changed,
      locals: { 'Main.runOpMode': { y: Math.round(y * 100) / 100, x: Math.round(x * 100) / 100, was_cross: this.gp[1].a, cycle: { '@type': 'Cycle', phase: ph, count: this.cycle.count }, intake: { '@device': 'intake' }, chain_drop: { '@device': 'chainDrop' } } },
    });
  }

  simulateSystemController(on: boolean): void {
    if (!on) {
      this.deliver({ type: 'systemGamepads', devices: [], error: 'no permission on /dev/input/event5: add yourself to the input group' });
      return;
    }
    this.deliver({
      type: 'systemGamepads',
      devices: [
        { id: 'event5', name: 'Sony Interactive Entertainment Wireless Controller', assigned: 1 },
        { id: 'event7', name: 'Logitech Gamepad F310', assigned: null, warning: 'F310 in D mode: flip the switch on the back to X' },
      ],
    });
    const st = { ...emptyGamepad(), left_stick_y: -0.5, a: false };
    this.deliver({ type: 'bridgeGamepad', index: 1, gamepadType: 'SONY_PS4', state: st, deviceName: 'Sony Interactive Entertainment Wireless Controller' });
  }

  private setPower(n: string, v: number, line: number): void {
    const a = this.acts[n];
    a.power = v;
    if (this.lastPowers[n] !== v) {
      this.lastPowers[n] = v;
      this.event(n, 'setPower', v, line);
    }
  }

  private emit(): void {
    const devices: Record<string, DeviceState> = {};
    for (const [n, a] of Object.entries(this.acts)) {
      const spin = Math.abs(a.omega) < 0.05 ? 'stopped' : a.omega > 0 ? 'CCW' : 'CW';
      if (n === 'intake') {
        devices[n] = { kind: 'crservo', power: a.power, direction: a.direction, reversed: a.direction === 'REVERSE', spin, omegaRadS: a.omega, angleRad: a.angle, pwmUs: 1500 + a.power * 500 };
      } else {
        const orientation = n === 'shooter' ? 'CCW' : 'CW';
        devices[n] = {
          kind: 'motor',
          power: a.power,
          direction: a.direction,
          orientation,
          reversed: a.direction === 'REVERSE',
          applied: a.power,
          spin,
          omegaRadS: a.omega,
          rpm: Math.abs((a.omega * 60) / (2 * Math.PI)),
          angleRad: a.angle,
          mode: 'RUN_WITHOUT_ENCODER',
          zeroPower: 'BRAKE',
          position: Math.round(a.position),
          target: 0,
          busy: false,
          velocity: (a.omega / (2 * Math.PI)) * 560,
          currentA: Math.abs(a.power) * 1.8,
        };
      }
    }
    for (const [n, s] of Object.entries(this.servos)) {
      const phys = s.dir === 'REVERSE' ? 1 - s.pos : s.pos;
      devices[n] = { kind: 'servo', position: s.pos, direction: s.dir, scaled: s.pos, pwmUs: 500 + phys * 2000, angleDeg: s.angle, targetAngleDeg: (phys - 0.5) * 270, rangeDeg: 270, enabled: this.phase !== 'idle' };
    }
    const touch = this.sensors.touch1 as { pressed?: boolean } | undefined;
    devices.touch1 = { kind: 'touch', pressed: Boolean(touch?.pressed) };
    const lim = this.sensors.limit as { state?: boolean } | undefined;
    devices.limit = { kind: 'digital', state: lim?.state ?? true, mode: 'INPUT' };
    const d = this.sensors.dist as { mm?: number | null } | undefined;
    devices.dist = { kind: 'distance', mm: d?.mm ?? null };
    const c = this.sensors.color as { r: number; g: number; b: number; distanceMm: number | null } | undefined;
    devices.color = { kind: 'color', red: Math.round((c?.r ?? 0) * 400), green: Math.round((c?.g ?? 0) * 400), blue: Math.round((c?.b ?? 0) * 400), alpha: 500, distanceMm: c?.distanceMm ?? null };
    const pot = this.sensors.pot as { angleDeg?: number } | undefined;
    const pa = pot?.angleDeg ?? 135;
    devices.pot = { kind: 'potentiometer', angleDeg: pa, volts: (pa / 270) * 3.3 };
    const rot = this.layout?.hubs?.['Control Hub']?.rotation ?? [0, 0, 0];
    devices.imu = { kind: 'imu', yawDeg: rot[1], pitchDeg: rot[0], rollDeg: rot[2], initialized: this.phase !== 'idle' };
    devices['Control Hub'] = { kind: 'voltage', volts: 12.6 - Math.abs(this.acts.LF.power) * 0.4 };
    const fields = this.phase === 'idle' ? {} : {
      InUse: 'MagDump',
      cycle_register: { '@type': 'HashMap', '@entries': { MagDump: { '@type': 'Cycle', count: this.cycle.count, phase: this.cycle.phase, last_ms: this.cycle.last_ms } } },
      timer: { '@type': 'ElapsedTime', seconds: Math.round((this.t - this.runStart) * 100) / 100 },
      drive_scale: 1.0,
      state: this.cycle.phase === 1 ? 'SHOOTING' : this.cycle.phase === 2 ? 'DUMPING' : 'IDLE',
      lf: { '@device': 'LF' },
      rf: { '@device': 'RF' },
      shooter: { '@device': 'shooter' },
    };
    const st: StateMsg = {
      type: 'state',
      t: Math.round(this.t * 1000) / 1000,
      phase: this.phase,
      opMode: this.opMode,
      loopMs: this.phase === 'running' ? 18 + Math.random() * 4 : null,
      devices,
      fields,
      gamepads: [{ index: 1, ...this.gp[1] }, { index: 2, ...this.gp[2] }],
      events: this.events,
    };
    this.events = [];
    this.sim(st);
  }
}

const motor = (name: string, port: number, hub = 'Control Hub'): DeviceInfo => ({
  name,
  kind: 'motor',
  tag: 'RevRoboticsUltraplanetaryHDHexMotor',
  displayName: 'REV Robotics Ultraplanetary HD Hex Motor',
  hub,
  port,
  motor: { orientation: 'CW', ticksPerRev: 28, maxRPM: 6000, freeSpeedRpm: 300, gearRatio: 20, specVerified: false },
});

export const READY: ReadyMsg = {
  type: 'ready',
  protocol: 1,
  sdkVersion: '11.2.0',
  opModes: [
    { name: 'Main', group: 'pyftc', kind: 'TeleOp', className: 'org.firstinspires.ftc.teamcode.pyftc.Main', source: PY },
    { name: 'AutoLeft', group: 'pyftc', kind: 'Autonomous', className: 'org.firstinspires.ftc.teamcode.pyftc.AutoLeft', source: '/home/team/robot/auto.py' },
  ],
  devices: [
    motor('LF', 0),
    motor('RF', 1),
    motor('LB', 2),
    motor('RB', 3),
    { name: 'shooter', kind: 'motor', tag: 'RevRoboticsCoreHexMotor', displayName: 'REV Robotics Core Hex Motor', hub: 'Expansion Hub 2', port: 0, motor: { orientation: 'CCW', ticksPerRev: 288, maxRPM: 125, freeSpeedRpm: 125, gearRatio: 72, specVerified: true } },
    { name: 'intake', kind: 'crservo', tag: 'RevRoboticsServo', displayName: 'Continuous Rotation Servo', hub: 'Control Hub', port: 0 },
    { name: 'chainDrop', kind: 'servo', tag: 'RevSmartServo', displayName: 'REV Smart Robot Servo', hub: 'Control Hub', port: 1 },
    { name: 'claw', kind: 'servo', tag: 'RevSmartServo', displayName: 'REV Smart Robot Servo', hub: 'Expansion Hub 2', port: 0 },
    { name: 'touch1', kind: 'touch', tag: 'RevTouchSensor', hub: 'Control Hub', port: 0 },
    { name: 'limit', kind: 'digital', tag: 'DigitalDevice', displayName: 'Magnetic limit switch', hub: 'Control Hub', port: 2 },
    { name: 'dist', kind: 'distance', tag: 'REV_VL53L0X_RANGE_SENSOR', hub: 'Control Hub', port: 1 },
    { name: 'color', kind: 'color', tag: 'RevColorSensorV3', hub: 'Expansion Hub 2', port: 1 },
    { name: 'pot', kind: 'potentiometer', tag: 'AnalogInput', hub: 'Control Hub', port: 0 },
    { name: 'imu', kind: 'imu', tag: 'ControlHubImuBHI260AP', hub: 'Control Hub', port: 0 },
    { name: 'Control Hub', kind: 'voltage', tag: 'LynxVoltageSensor', hub: 'Control Hub' },
  ],
  hubs: [
    { name: 'Control Hub', address: 173, kind: 'ControlHub' },
    { name: 'Expansion Hub 2', address: 2, kind: 'ExpansionHub' },
  ],
  config: { name: 'FGC2026-Harness', source: 'file' },
  notSimulated: [],
};
