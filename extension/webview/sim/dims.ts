import type { DeviceInfo, DeviceLayout } from './protocol';

// Physical sizes in metres. Each actuator's origin is the centre of its body; +Z is the shaft.

export type MotorShape = 'ultraplanetary' | 'hdhex' | 'corehex' | 'generic';

export function motorShape(tag: string): MotorShape {
  const t = tag.toLowerCase();
  if (t.includes('corehex')) return 'corehex';
  if (t.includes('ultraplanetary')) return 'ultraplanetary';
  if (t.includes('hdhex')) return 'hdhex';
  return 'generic';
}

export const MOTOR_DIA = 0.037;
export const MOTOR_CAN = 0.052;
export const STAGE_LEN = 0.017;
export const SHAFT_LEN = 0.02;
export const COREHEX = 0.045;
export const SERVO_BODY = { x: 0.04, y: 0.02, z: 0.038 };
export const HUB_BODY = { x: 0.103, y: 0.015, z: 0.143 };
export const SENSOR_BODY = { x: 0.03, y: 0.012, z: 0.02 };

export const CARTRIDGE_RATIO: Record<string, number> = { '3:1': 2.89, '4:1': 3.61, '5:1': 5.23 };

export function cartridges(dl: DeviceLayout | undefined): string[] {
  const c = dl?.motor?.cartridges;
  return Array.isArray(c) && c.length ? c.map(String) : ['4:1', '5:1'];
}

export function cartridgeRatio(c: string[]): number {
  return c.reduce((r, k) => r * (CARTRIDGE_RATIO[k] ?? 1), 1);
}

export function stageCount(info: DeviceInfo, dl: DeviceLayout | undefined): number {
  const shape = motorShape(info.tag);
  if (shape === 'ultraplanetary') return cartridges(dl).length;
  if (shape === 'hdhex') return 2;
  return 0;
}

// Body length along the shaft axis, face to back.
export function actuatorLength(info: DeviceInfo, dl: DeviceLayout | undefined): number {
  if (info.kind === 'servo' || info.kind === 'crservo') return SERVO_BODY.z;
  const shape = motorShape(info.tag);
  if (shape === 'corehex') return COREHEX;
  return MOTOR_CAN + stageCount(info, dl) * STAGE_LEN;
}

export function actuatorRadius(info: DeviceInfo): number {
  if (info.kind === 'servo' || info.kind === 'crservo') return 0.022;
  return motorShape(info.tag) === 'corehex' ? COREHEX / 2 : MOTOR_DIA / 2;
}

export function restingY(info: DeviceInfo): number {
  switch (info.kind) {
    case 'motor':
      return motorShape(info.tag) === 'corehex' ? COREHEX / 2 : MOTOR_DIA / 2;
    case 'servo':
    case 'crservo':
      return SERVO_BODY.y / 2;
    default:
      return SENSOR_BODY.y / 2;
  }
}
