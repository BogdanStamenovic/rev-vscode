// Types for the simulator protocol (Contract 5), the scene layout (Contract 6) and the UI-only
// webview <-> extension messages. Frames: +Y up, robot forward = -Z, right = +X. Every actuator's
// local +Z is its output shaft; omegaRadS > 0 = CCW seen looking at the shaft face.

export type Vec3 = [number, number, number];

export type GamepadType = 'LOGITECH_F310' | 'XBOX_360' | 'SONY_PS4' | 'UNKNOWN';

export interface GamepadState {
  left_stick_x: number;
  left_stick_y: number;
  right_stick_x: number;
  right_stick_y: number;
  left_trigger: number;
  right_trigger: number;
  dpad_up: boolean;
  dpad_down: boolean;
  dpad_left: boolean;
  dpad_right: boolean;
  a: boolean;
  b: boolean;
  x: boolean;
  y: boolean;
  guide: boolean;
  start: boolean;
  back: boolean;
  left_bumper: boolean;
  right_bumper: boolean;
  left_stick_button: boolean;
  right_stick_button: boolean;
  touchpad: boolean;
}

export const GAMEPAD_AXES = [
  'left_stick_x',
  'left_stick_y',
  'right_stick_x',
  'right_stick_y',
  'left_trigger',
  'right_trigger',
] as const;
export const GAMEPAD_BUTTONS = [
  'dpad_up',
  'dpad_down',
  'dpad_left',
  'dpad_right',
  'a',
  'b',
  'x',
  'y',
  'guide',
  'start',
  'back',
  'left_bumper',
  'right_bumper',
  'left_stick_button',
  'right_stick_button',
  'touchpad',
] as const;
export type GamepadAxis = (typeof GAMEPAD_AXES)[number];
export type GamepadButton = (typeof GAMEPAD_BUTTONS)[number];

export function emptyGamepad(): GamepadState {
  return {
    left_stick_x: 0,
    left_stick_y: 0,
    right_stick_x: 0,
    right_stick_y: 0,
    left_trigger: 0,
    right_trigger: 0,
    dpad_up: false,
    dpad_down: false,
    dpad_left: false,
    dpad_right: false,
    a: false,
    b: false,
    x: false,
    y: false,
    guide: false,
    start: false,
    back: false,
    left_bumper: false,
    right_bumper: false,
    left_stick_button: false,
    right_stick_button: false,
    touchpad: false,
  };
}

export interface PyLoc {
  file: string;
  line: number;
}

// ---- Sim commands (webview -> extension -> sim) ----

export type SensorValue =
  | { pressed: boolean }
  | { state: boolean }
  | { mm: number | null }
  | { r: number; g: number; b: number; distanceMm: number | null }
  | { volts: number }
  | { angleDeg: number };

export type SimCommand =
  | { type: 'init'; opMode: string; at?: number }
  | { type: 'start'; at?: number }
  | { type: 'stop'; at?: number }
  | { type: 'gamepad'; index: 1 | 2; gamepadType: GamepadType; state: GamepadState; at?: number }
  | { type: 'sensor'; device: string; value: SensorValue; at?: number }
  | { type: 'layout'; layout: SceneLayout; at?: number }
  | { type: 'pause'; at?: number }
  | { type: 'resume'; at?: number }
  | { type: 'speed'; factor: number; at?: number }
  | { type: 'quit' };

// ---- Sim events (sim -> extension -> webview) ----

export type DeviceKind =
  | 'motor'
  | 'crservo'
  | 'servo'
  | 'touch'
  | 'digital'
  | 'analog'
  | 'potentiometer'
  | 'distance'
  | 'color'
  | 'imu'
  | 'voltage'
  | 'unsupported';

export interface MotorSpec {
  orientation?: 'CW' | 'CCW';
  ticksPerRev?: number;
  maxRPM?: number;
  freeSpeedRpm?: number;
  gearRatio?: number;
  specVerified?: boolean;
}

export interface DeviceInfo {
  name: string;
  kind: DeviceKind;
  tag: string;
  displayName?: string;
  hub?: string;
  port?: number;
  motor?: MotorSpec;
}

export interface OpModeInfo {
  name: string;
  group?: string;
  kind: 'TeleOp' | 'Autonomous' | string;
  className?: string;
  source?: string;
}

export interface HubInfo {
  name: string;
  address?: number;
  kind: 'ControlHub' | 'ExpansionHub' | string;
}

export interface ReadyMsg {
  type: 'ready';
  protocol: number;
  sdkVersion?: string;
  opModes: OpModeInfo[];
  devices: DeviceInfo[];
  hubs: HubInfo[];
  config?: { name: string; source: string };
  notSimulated?: string[];
}

export type Spin = 'CW' | 'CCW' | 'stopped';
export type Direction = 'FORWARD' | 'REVERSE';

export interface MotorState {
  kind: 'motor';
  power: number;
  direction: Direction;
  orientation?: 'CW' | 'CCW';
  reversed: boolean;
  applied?: number;
  spin: Spin;
  omegaRadS: number;
  rpm: number;
  angleRad: number;
  mode?: string;
  zeroPower?: string;
  position?: number;
  target?: number;
  busy?: boolean;
  velocity?: number;
  currentA?: number;
}

export interface CrServoState {
  kind: 'crservo';
  power: number;
  direction: Direction;
  reversed: boolean;
  spin: Spin;
  omegaRadS: number;
  angleRad: number;
  pwmUs?: number;
  // CONTRACT-EXTENSION: optional rpm for CR servos (the UI falls back to |omegaRadS| * 60 / 2pi).
  rpm?: number;
}

export interface ServoState {
  kind: 'servo';
  position: number;
  direction: Direction;
  scaled?: number;
  pwmUs?: number;
  angleDeg: number;
  targetAngleDeg: number;
  rangeDeg: number;
  enabled: boolean;
}

export interface TouchState {
  kind: 'touch';
  pressed: boolean;
}
export interface DigitalState {
  kind: 'digital';
  state: boolean;
  mode?: string;
}
export interface AnalogState {
  kind: 'analog';
  volts: number;
}
export interface PotState {
  kind: 'potentiometer';
  volts: number;
  angleDeg: number;
}
export interface DistanceState {
  kind: 'distance';
  mm: number | null;
}
export interface ColorState {
  kind: 'color';
  red: number;
  green: number;
  blue: number;
  alpha: number;
  distanceMm: number | null;
}
export interface ImuState {
  kind: 'imu';
  yawDeg: number;
  pitchDeg: number;
  rollDeg: number;
  initialized: boolean;
}
export interface VoltageState {
  kind: 'voltage';
  volts: number;
}
export interface UnsupportedState {
  kind: 'unsupported';
}

export type DeviceState =
  | MotorState
  | CrServoState
  | ServoState
  | TouchState
  | DigitalState
  | AnalogState
  | PotState
  | DistanceState
  | ColorState
  | ImuState
  | VoltageState
  | UnsupportedState;

export interface WheelState {
  device: string;
  rollMps: number;
  slipMps: number;
}

export interface ChassisState {
  enabled: boolean;
  forwardMps: number;
  rightMps: number;
  turnDegS: number;
  fight: number;
  wheels: WheelState[];
}

export interface SimEvent {
  t: number;
  dev: string;
  op: string;
  v: unknown;
  py?: PyLoc;
}

export type Phase = 'idle' | 'init' | 'running' | 'stopping' | 'stopped' | 'crashed';

export interface StateMsg {
  type: 'state';
  t: number;
  phase: Phase;
  opMode?: string | null;
  loopMs?: number | null;
  devices: Record<string, DeviceState>;
  chassis?: ChassisState;
  fields?: Record<string, unknown>;
  gamepads?: Array<Partial<GamepadState> & { index?: number }>;
  events?: SimEvent[];
}

export interface TelemetryMsg {
  type: 'telemetry';
  t: number;
  lines: string[];
  log?: string[];
}

export interface ExceptionFrame {
  class: string;
  method: string;
  javaLine?: number;
  py?: PyLoc;
}

export interface ExceptionMsg {
  type: 'exception';
  t: number;
  phase?: Phase;
  exception: string;
  message: string;
  py?: PyLoc;
  frames?: ExceptionFrame[];
  driverHub?: string;
}

export type WarningCode = 'double-write' | 'stuck-stop' | 'no-sdk-calls' | 'returned-early' | 'not-simulated' | string;

export interface WarningMsg {
  type: 'warning';
  t: number;
  code: WarningCode;
  device?: string;
  message: string;
  py?: PyLoc;
  related?: PyLoc[];
}

export interface LogMsg {
  type: 'log';
  level: 'info' | 'warn' | 'error';
  message: string;
  // CONTRACT-EXTENSION: optional sim time on log lines so they can sit on the timeline.
  t?: number;
}

export interface FatalMsg {
  type: 'fatal';
  message: string;
}

// Executed-line trace of the most recent complete loop iteration (sent by the sim about 30/s).
export interface TraceMsg {
  type: 'trace';
  t: number;
  iteration: number;
  lines: Record<string, number[]>;
  changed?: Array<{ name: string; value: unknown; file?: string; line?: number }>;
  locals?: Record<string, Record<string, unknown>>;
  fields?: Record<string, unknown>;
}

export type SimMsg = ReadyMsg | StateMsg | TelemetryMsg | ExceptionMsg | WarningMsg | LogMsg | FatalMsg | TraceMsg;

// ---- Contract 6: scene layout ----

export type WheelType = 'traction' | 'omni' | 'mecanum';

export interface WheelConfig {
  type: WheelType;
  diameterMm: number;
  mecanum?: 'left' | 'right';
  ratio: number;
}

export interface DeviceLayout {
  position?: Vec3;
  rotation?: Vec3;
  motor?: { cartridges?: string[]; load?: 'free' | 'wheel' | 'arm'; [k: string]: unknown };
  wheel?: WheelConfig;
  servo?: { rangeDeg?: number; [k: string]: unknown };
  sensor?: { override?: SensorValue | null; [k: string]: unknown };
  [k: string]: unknown;
}

export interface ObstacleLayout {
  kind: 'box';
  position: Vec3;
  size: Vec3;
  color?: string;
  // CONTRACT-EXTENSION: optional rotation (degrees, XYZ Euler) so walls can be turned.
  rotation?: Vec3;
  [k: string]: unknown;
}

export interface SceneLayout {
  version: number;
  hubs?: Record<string, { position?: Vec3; rotation?: Vec3; [k: string]: unknown }>;
  devices?: Record<string, DeviceLayout>;
  chassis?: { enabled?: boolean; [k: string]: unknown };
  obstacles?: ObstacleLayout[];
  camera?: { position?: Vec3; target?: Vec3; [k: string]: unknown };
  [k: string]: unknown;
}

// ---- UI-only messages ----

export type WebviewToExt =
  | { type: 'ready' }
  | { type: 'sim'; msg: SimCommand }
  | { type: 'layoutChanged'; layout: SceneLayout }
  | { type: 'openSource'; file: string; line: number }
  | { type: 'rebuild' }
  // CONTRACT-EXTENSION: start a debug session attached to the running simulator.
  | { type: 'debug' }
  // CONTRACT-EXTENSION: ask the extension to serve dist/sim/bridge.html on 127.0.0.1 and open it in the
  // system browser (the Gamepad API is often blocked inside webview iframes).
  | { type: 'openGamepadBridge' }
  // What the Gamepad API does inside this webview, reported once on load (requested by the extension side).
  | { type: 'env'; gamepadApi: 'allowed' | 'blocked' | 'missing'; detail: string; featurePolicyGamepad: boolean | null };

export interface CompileError {
  file: string;
  line: number;
  message: string;
  // CONTRACT-EXTENSION: optional column, used for the openSource link when present.
  column?: number;
}

export type ExtToWebview =
  | { type: 'hello'; layout: SceneLayout | null; workspaceName?: string }
  | { type: 'status'; state: 'preparing' | 'compiling' | 'running' | 'error' | 'exited'; message?: string }
  | { type: 'compileErrors'; errors: CompileError[] }
  | { type: 'sim'; msg: SimMsg }
  // CONTRACT-EXTENSION: gamepad input posted by the bridge page, forwarded verbatim by the extension.
  | { type: 'bridgeGamepad'; index: 1 | 2; gamepadType: GamepadType; state: GamepadState; deviceName?: string }
  // Controllers seen by the extension's system-level reader (evdev); it does the Start+A / Start+B claiming.
  | { type: 'systemGamepads'; devices: SystemGamepad[]; error?: string }
  // Python sources of the current build, for the live code view.
  | { type: 'sources'; files: Record<string, string> }
  // CONTRACT-EXTENSION: bridge page URL once served (shown in the Gamepads panel so it can be reopened).
  | { type: 'bridgeInfo'; url: string };

export interface SystemGamepad {
  id: string;
  name: string;
  assigned: 1 | 2 | null;
  warning?: string;
}

export interface BridgePost {
  index: 1 | 2;
  gamepadType: GamepadType;
  state: GamepadState;
}
