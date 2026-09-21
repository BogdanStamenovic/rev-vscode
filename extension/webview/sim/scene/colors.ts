// Okabe-Ito derived pair: distinguishable with the common colour-vision deficiencies. Direction is also
// always spelled out in text next to the arrow.
export const C = {
  ccw: 0x1f77d0,
  cw: 0xe69f00,
  stopped: 0x8a8a8a,
  servoRange: 0x7a7a7a,
  servoTarget: 0xd55e00,
  metal: 0x9aa3ad,
  darkMetal: 0x4a5058,
  motorBody: 0x2b2f36,
  stage: 0x6c7580,
  servoBody: 0x303640,
  hub: 0x1d2a3a,
  unsupported: 0x777777,
};

export function spinColor(spin: string): number {
  return spin === 'CCW' ? C.ccw : spin === 'CW' ? C.cw : C.stopped;
}
