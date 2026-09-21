import { emptyGamepad, GamepadState, GamepadType } from './protocol';

// Shared by the webview and the standalone controller bridge page.

export type ControllerChoice = 'F310' | 'XBOX' | 'PS' | 'REVPS4';

export const CONTROLLER_CHOICES: Array<[ControllerChoice, string, GamepadType]> = [
  ['F310', 'Logitech F310', 'LOGITECH_F310'],
  ['XBOX', 'Xbox 360/One', 'XBOX_360'],
  ['PS', 'PS4 / PS5 (DualShock/DualSense)', 'SONY_PS4'],
  ['REVPS4', 'REV USB PS4 Compatible Gamepad', 'SONY_PS4'],
];

export function sdkType(c: ControllerChoice): GamepadType {
  return CONTROLLER_CHOICES.find((x) => x[0] === c)?.[2] ?? 'UNKNOWN';
}

export function choiceFromType(t: GamepadType): ControllerChoice {
  return t === 'SONY_PS4' ? 'PS' : t === 'XBOX_360' ? 'XBOX' : 'F310';
}

// Best guess from a browser Gamepad id string (vendor ids: 054c Sony, 045e Microsoft, 046d Logitech).
export function guessChoice(id: string): ControllerChoice {
  const s = id.toLowerCase();
  if (s.includes('054c') || s.includes('sony') || s.includes('dualshock') || s.includes('dualsense') || s.includes('wireless controller')) return 'PS';
  if (s.includes('045e') || s.includes('xbox') || s.includes('xinput')) return 'XBOX';
  if (s.includes('046d') || s.includes('logitech') || s.includes('f310')) return 'F310';
  return 'PS';
}

export interface ButtonLabels {
  a: string;
  b: string;
  x: string;
  y: string;
  back: string;
  start: string;
  guide: string;
  lb: string;
  rb: string;
  lt: string;
  rt: string;
  ps: boolean;
}

export function labelsFor(c: ControllerChoice): ButtonLabels {
  if (c === 'PS' || c === 'REVPS4') {
    return { a: 'Cross', b: 'Circle', x: 'Square', y: 'Triangle', back: 'Share', start: 'Options', guide: 'PS', lb: 'L1', rb: 'R1', lt: 'L2', rt: 'R2', ps: true };
  }
  const guide = c === 'XBOX' ? 'Guide' : 'Logitech';
  return { a: 'A', b: 'B', x: 'X', y: 'Y', back: 'Back', start: 'Start', guide, lb: 'LB', rb: 'RB', lt: 'LT', rt: 'RT', ps: false };
}

// SDK alias names the code can read for each canonical field, per controller family.
export function sdkNames(field: keyof GamepadState, ps: boolean): string[] {
  const psAlias: Partial<Record<keyof GamepadState, string>> = {
    a: 'cross',
    b: 'circle',
    x: 'square',
    y: 'triangle',
    back: 'share',
    start: 'options',
    guide: 'ps',
  };
  const alias = psAlias[field];
  if (!alias) return [field];
  return ps ? [alias, field] : [field, alias];
}

export function gamepadApiStatus(): { ok: boolean; reason?: string } {
  const doc = document as Document & { featurePolicy?: { allowsFeature(f: string): boolean } };
  try {
    if (doc.featurePolicy && !doc.featurePolicy.allowsFeature('gamepad')) return { ok: false, reason: 'permissions policy disallows gamepad' };
    if (typeof navigator.getGamepads !== 'function') return { ok: false, reason: 'Gamepad API missing' };
    navigator.getGamepads();
    return { ok: true };
  } catch (e) {
    return { ok: false, reason: String((e as Error).message || e) };
  }
}

export function gamepadEnv(): { type: 'env'; gamepadApi: 'allowed' | 'blocked' | 'missing'; detail: string; featurePolicyGamepad: boolean | null } {
  const doc = document as Document & { featurePolicy?: { allowsFeature?(f: string): boolean } };
  let fp: boolean | null = null;
  try {
    fp = typeof doc.featurePolicy?.allowsFeature === 'function' ? doc.featurePolicy.allowsFeature('gamepad') : null;
  } catch {
    fp = null;
  }
  if (typeof navigator.getGamepads !== 'function') return { type: 'env', gamepadApi: 'missing', detail: 'navigator.getGamepads is not a function', featurePolicyGamepad: fp };
  try {
    const pads = navigator.getGamepads();
    const n = Array.from(pads ?? []).filter(Boolean).length;
    if (fp === false) return { type: 'env', gamepadApi: 'blocked', detail: `featurePolicy.allowsFeature('gamepad') = false (getGamepads returned ${n} pads)`, featurePolicyGamepad: fp };
    return { type: 'env', gamepadApi: 'allowed', detail: `getGamepads() returned ${n} connected pad(s)`, featurePolicyGamepad: fp };
  } catch (e) {
    const err = e as Error;
    return { type: 'env', gamepadApi: 'blocked', detail: `${err.name ?? 'Error'}: ${err.message ?? String(e)}`, featurePolicyGamepad: fp };
  }
}

export function listPads(): Gamepad[] {
  try {
    return Array.from(navigator.getGamepads?.() ?? []).filter((g): g is Gamepad => Boolean(g && g.connected));
  } catch {
    return [];
  }
}

function dz(v: number, deadzone: number): number {
  if (!Number.isFinite(v) || Math.abs(v) < deadzone) return 0;
  return Math.max(-1, Math.min(1, v));
}

// Standard mapping (https://w3c.github.io/gamepad/#remapping). Stick Y is up = -1, same as the SDK.
export function fromBrowserPad(gp: Gamepad, deadzone: number): GamepadState {
  const s = emptyGamepad();
  const b = (i: number): boolean => Boolean(gp.buttons[i]?.pressed);
  const bv = (i: number): number => gp.buttons[i]?.value ?? 0;
  s.left_stick_x = dz(gp.axes[0] ?? 0, deadzone);
  s.left_stick_y = dz(gp.axes[1] ?? 0, deadzone);
  s.right_stick_x = dz(gp.axes[2] ?? 0, deadzone);
  s.right_stick_y = dz(gp.axes[3] ?? 0, deadzone);
  s.a = b(0);
  s.b = b(1);
  s.x = b(2);
  s.y = b(3);
  s.left_bumper = b(4);
  s.right_bumper = b(5);
  s.left_trigger = round3(bv(6));
  s.right_trigger = round3(bv(7));
  s.back = b(8);
  s.start = b(9);
  s.left_stick_button = b(10);
  s.right_stick_button = b(11);
  s.dpad_up = b(12);
  s.dpad_down = b(13);
  s.dpad_left = b(14);
  s.dpad_right = b(15);
  s.guide = b(16);
  s.touchpad = b(17);
  s.left_stick_x = round3(s.left_stick_x);
  s.left_stick_y = round3(s.left_stick_y);
  s.right_stick_x = round3(s.right_stick_x);
  s.right_stick_y = round3(s.right_stick_y);
  return s;
}

function round3(v: number): number {
  return Math.round(v * 1000) / 1000;
}

export const KEY_LEGEND: Array<[string, string]> = [
  ['W A S D', 'left stick'],
  ['I J K L', 'right stick'],
  ['Arrow keys', 'dpad'],
  ['F', 'A / cross'],
  ['G', 'B / circle'],
  ['R', 'X / square'],
  ['T', 'Y / triangle'],
  ['Q / E', 'left / right bumper'],
  ['Z / C', 'left / right trigger'],
  ['Backspace', 'back / share'],
  ['Enter', 'start / options'],
  ['X / M', 'left / right stick button'],
];

const KEY_BUTTONS: Record<string, keyof GamepadState> = {
  ArrowUp: 'dpad_up',
  ArrowDown: 'dpad_down',
  ArrowLeft: 'dpad_left',
  ArrowRight: 'dpad_right',
  KeyF: 'a',
  KeyG: 'b',
  KeyR: 'x',
  KeyT: 'y',
  KeyQ: 'left_bumper',
  KeyE: 'right_bumper',
  Backspace: 'back',
  Enter: 'start',
  KeyX: 'left_stick_button',
  KeyM: 'right_stick_button',
};

export const KEYBOARD_CODES = new Set([
  ...Object.keys(KEY_BUTTONS),
  'KeyW',
  'KeyA',
  'KeyS',
  'KeyD',
  'KeyI',
  'KeyJ',
  'KeyK',
  'KeyL',
  'KeyZ',
  'KeyC',
]);

export function fromKeys(keys: Set<string>): GamepadState {
  const s = emptyGamepad();
  const axis = (neg: string, pos: string): number => (keys.has(pos) ? 1 : 0) - (keys.has(neg) ? 1 : 0);
  s.left_stick_x = axis('KeyA', 'KeyD');
  s.left_stick_y = axis('KeyW', 'KeyS');
  s.right_stick_x = axis('KeyJ', 'KeyL');
  s.right_stick_y = axis('KeyI', 'KeyK');
  s.left_trigger = keys.has('KeyZ') ? 1 : 0;
  s.right_trigger = keys.has('KeyC') ? 1 : 0;
  for (const [code, f] of Object.entries(KEY_BUTTONS)) if (keys.has(code)) (s as unknown as Record<string, boolean>)[f] = true;
  return s;
}

export function sameGamepad(a: GamepadState, b: GamepadState): boolean {
  for (const k of Object.keys(a) as Array<keyof GamepadState>) if (a[k] !== b[k]) return false;
  return true;
}
