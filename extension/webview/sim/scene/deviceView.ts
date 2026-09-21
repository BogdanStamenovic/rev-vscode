import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import type { DeviceInfo, DeviceLayout, DeviceState, MotorState, CrServoState, ServoState } from '../protocol';
import { ArcArrow, thinArc } from './arrows';
import { C } from './colors';
import { buildDevice, buildHub, buildObstacle, BuiltDevice } from './primitives';
import { cartridges } from '../dims';
import { isVec3 } from '../layout';

const DEG = Math.PI / 180;

export function applyPose(obj: THREE.Object3D, position: unknown, rotation: unknown): void {
  if (isVec3(position)) obj.position.set(position[0], position[1], position[2]);
  if (isVec3(rotation)) obj.rotation.set(rotation[0] * DEG, rotation[1] * DEG, rotation[2] * DEG, 'XYZ');
}

function tagSelectable(obj: THREE.Object3D, selId: string): void {
  obj.traverse((o) => {
    o.userData.selId = selId;
  });
}

function esc(s: string): string {
  return s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
}

function num(n: number | undefined | null, d = 2): string {
  if (n === undefined || n === null || !Number.isFinite(n)) return '-';
  const s = n.toFixed(d);
  return s === (-0).toFixed(d) ? (0).toFixed(d) : s;
}

export type LabelMode = 'off' | 'short' | 'full';

export interface ViewOpts {
  labels: LabelMode;
  selected: boolean;
  // Seconds since this state arrived; used to extrapolate the shaft angle between 30 Hz frames (live only).
  age: number;
}

// Real shaft speeds strobe at 30-60 fps (a 300 rpm output turns 60 degrees per sim frame), so the
// animation runs at a scaled-down rate: direction and relative speed stay exact, the free speed is
// shown as about one turn per second.
const VIS_MAX_RAD_S = 2 * Math.PI * 1.0;
const DEFAULT_CRSERVO_RPM = 130;

export class DeviceView {
  readonly root = new THREE.Group();
  readonly selId: string;
  readonly label: CSS2DObject;
  private labelEl: HTMLDivElement;
  private labelHtml = '';
  private built!: BuiltDevice;
  private arrow: ArcArrow | null = null;
  private servoGroup: THREE.Group | null = null;
  private servoRange = -1;
  private servoReversed = false;
  private servoTicks: CSS2DObject[] = [];
  private targetMarker: THREE.Mesh | null = null;
  private buildKey = '';
  private ray: THREE.Line | null = null;
  private rayHit: THREE.Mesh | null = null;
  lastState: DeviceState | undefined;

  constructor(readonly info: DeviceInfo, dl: DeviceLayout | undefined) {
    this.selId = 'dev:' + info.name;
    this.root.name = info.name;
    this.labelEl = document.createElement('div');
    this.labelEl.className = 'dev-label';
    this.label = new CSS2DObject(this.labelEl);
    this.label.center.set(0.5, 1);
    this.rebuild(dl);
  }

  get isActuator(): boolean {
    return this.info.kind === 'motor' || this.info.kind === 'crservo';
  }

  rebuild(dl: DeviceLayout | undefined): void {
    const key = JSON.stringify([cartridges(dl), dl?.servo?.rangeDeg]);
    if (key !== this.buildKey) {
      this.buildKey = key;
      if (this.built) this.root.remove(this.built.body);
      this.built = buildDevice(this.info, dl);
      this.root.add(this.built.body);
      this.arrow = null;
      this.servoGroup = null;
      this.servoRange = -1;
      this.ray = null;
      if (this.isActuator) {
        const r = this.built.arrowRadius;
        this.arrow = new ArcArrow(r, 0.0012, 0.0042);
        const rp = this.built.rotor?.position ?? new THREE.Vector3();
        this.arrow.group.position.set(rp.x, rp.y, this.built.faceZ + 0.006);
        this.built.body.add(this.arrow.group);
      }
      if (this.info.kind === 'distance') {
        const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, 0, 1)]);
        this.ray = new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xff3030, transparent: true, opacity: 0.9 }));
        this.ray.position.z = this.built.faceZ + 0.002;
        this.ray.userData.noPick = true;
        this.built.body.add(this.ray);
        this.rayHit = new THREE.Mesh(new THREE.SphereGeometry(0.004, 10, 8), new THREE.MeshBasicMaterial({ color: 0xff3030 }));
        this.rayHit.userData.noPick = true;
        this.ray.add(this.rayHit);
      }
    }
    applyPose(this.root, dl?.position, dl?.rotation);
    tagSelectable(this.root, this.selId);
  }

  // Distance sensor ray origin/direction in world space.
  rayWorld(): { origin: THREE.Vector3; dir: THREE.Vector3; maxZ: number } {
    const origin = new THREE.Vector3(0, 0, this.built.faceZ + 0.002).applyMatrix4(this.root.matrixWorld);
    const q = this.root.getWorldQuaternion(new THREE.Quaternion());
    return { origin, dir: new THREE.Vector3(0, 0, 1).applyQuaternion(q), maxZ: 2 };
  }

  setRayLength(m: number | null): void {
    if (!this.ray || !this.rayHit) return;
    const len = m === null ? 2 : Math.max(0.001, m);
    this.ray.scale.set(1, 1, len);
    this.rayHit.visible = m !== null;
    this.rayHit.scale.set(1, 1, 1 / len);
    this.rayHit.position.z = 1;
    (this.ray.material as THREE.LineBasicMaterial).opacity = m === null ? 0.25 : 0.9;
  }

  update(st: DeviceState | undefined, o: ViewOpts): void {
    this.lastState = st;
    const full = o.selected || o.labels === 'full';
    let html = `<span class="n">${esc(this.info.name)}</span>`;
    if (!st) {
      html += ' <span class="dim">no data</span>';
      this.arrow?.set(0, 0);
    } else if (st.kind === 'motor' || st.kind === 'crservo') {
      html += this.updateActuator(st, o.age, full);
    } else if (st.kind === 'servo') {
      html += this.updateServo(st, full);
    } else {
      html += this.updateSensor(st);
    }
    this.labelEl.classList.toggle('selected', o.selected);
    this.label.visible = o.labels !== 'off' || o.selected;
    if (html !== this.labelHtml) {
      this.labelHtml = html;
      this.labelEl.innerHTML = html;
    }
  }

  private visScale(): number {
    const rpm = this.info.kind === 'motor' ? this.info.motor?.freeSpeedRpm || this.info.motor?.maxRPM || 300 : DEFAULT_CRSERVO_RPM;
    return Math.min(1, VIS_MAX_RAD_S / ((rpm * 2 * Math.PI) / 60));
  }

  private updateActuator(st: MotorState | CrServoState, age: number, full: boolean): string {
    const k = this.visScale();
    const omega = Number.isFinite(st.omegaRadS) ? st.omegaRadS : 0;
    const angle = (Number.isFinite(st.angleRad) ? st.angleRad : 0) + omega * Math.min(age, 0.07);
    if (this.built.rotor) this.built.rotor.rotation.z = angle * k;
    const dir = st.spin === 'CCW' ? 1 : st.spin === 'CW' ? -1 : 0;
    let frac: number;
    let rpm: number;
    if (st.kind === 'motor') {
      rpm = Math.abs(st.rpm ?? (st.omegaRadS * 60) / (2 * Math.PI));
      const free = this.info.motor?.freeSpeedRpm || this.info.motor?.maxRPM || 0;
      frac = free > 0 ? rpm / free : Math.min(1, Math.abs(st.power));
    } else {
      rpm = Math.abs(st.rpm ?? (st.omegaRadS * 60) / (2 * Math.PI));
      frac = Math.min(1, Math.abs(st.power));
    }
    this.arrow?.set(dir, frac);
    const spinCls = st.spin === 'CCW' ? 'ccw' : st.spin === 'CW' ? 'cw' : 'stopped';
    const spinTxt = st.spin === 'stopped' ? 'stopped' : full ? `${st.spin} (seen from shaft)` : st.spin;
    const arrowCh = st.spin === 'CCW' ? '\u21ba ' : st.spin === 'CW' ? '\u21bb ' : '';
    let s = full
      ? ` power ${num(st.power)} <span class="dir">${esc(st.direction)}</span> ${rpm.toFixed(0)} rpm <span class="spin ${spinCls}">${arrowCh}${spinTxt}</span>`
      : ` ${num(st.power)} <span class="spin ${spinCls}">${arrowCh}${spinTxt}</span>`;
    if (st.direction === 'REVERSE') s += ' <span class="badge rev">REVERSED</span>';
    const orient = st.kind === 'motor' ? st.orientation ?? this.info.motor?.orientation : undefined;
    if (orient === 'CCW' && full) {
      s +=
        st.direction === 'FORWARD'
          ? ' <span class="badge type">motor type reverses</span>'
          : ' <span class="badge type">REVERSE cancels the motor type flip</span>';
    }
    return s;
  }

  private updateServo(st: ServoState, full: boolean): string {
    const range = st.rangeDeg || 270;
    const reversed = st.direction === 'REVERSE';
    if (range !== this.servoRange || reversed !== this.servoReversed) this.buildServoArc(range, reversed);
    if (this.built.horn) this.built.horn.rotation.z = (st.angleDeg || 0) * DEG;
    if (this.targetMarker) {
      const a = (90 + (st.targetAngleDeg || 0)) * DEG;
      this.targetMarker.position.set(Math.cos(a) * 0.03, Math.sin(a) * 0.03, 0);
      this.targetMarker.rotation.z = a - Math.PI / 2;
    }
    let s = full ? ` position ${num(st.position)} (target ${num(st.targetAngleDeg, 1)} deg, at ${num(st.angleDeg, 1)} deg)` : ` pos ${num(st.position)}`;
    if (!st.enabled) s += ' <span class="dim">disabled</span>';
    if (reversed) s += ' <span class="badge rev">REVERSED</span>';
    return s;
  }

  // Range arc on the horn plane, centred on neutral (+Y). Ticks mark where position 0 and 1 end up.
  private buildServoArc(range: number, reversed: boolean): void {
    if (!this.built.horn || this.built.hornZ === undefined) return;
    if (this.servoGroup) this.built.body.remove(this.servoGroup);
    for (const t of this.servoTicks) t.removeFromParent();
    this.servoTicks = [];
    this.servoRange = range;
    this.servoReversed = reversed;
    const g = new THREE.Group();
    g.position.set(this.built.horn.position.x, this.built.horn.position.y, this.built.hornZ + 0.0035);
    const R = 0.03;
    const start = (90 - range / 2) * DEG;
    g.add(thinArc(R, 0.0009, start, range * DEG, C.servoRange));
    const tickAt = (deg: number, text: string): void => {
      const a = (90 + deg) * DEG;
      const tick = new THREE.Mesh(new THREE.BoxGeometry(0.0016, 0.008, 0.001), new THREE.MeshBasicMaterial({ color: C.servoRange }));
      tick.position.set(Math.cos(a) * R, Math.sin(a) * R, 0);
      tick.rotation.z = a - Math.PI / 2;
      g.add(tick);
      const el = document.createElement('div');
      el.className = 'tick-label';
      el.textContent = text;
      const lbl = new CSS2DObject(el);
      lbl.position.set(Math.cos(a) * (R + 0.009), Math.sin(a) * (R + 0.009), 0);
      g.add(lbl);
      this.servoTicks.push(lbl);
    };
    const half = range / 2;
    tickAt(reversed ? half : -half, '0');
    tickAt(reversed ? -half : half, '1');
    const tm = new THREE.Mesh(new THREE.ConeGeometry(0.0035, 0.008, 12), new THREE.MeshBasicMaterial({ color: C.servoTarget }));
    g.add(tm);
    this.targetMarker = tm;
    g.traverse((o) => (o.userData.noPick = true));
    this.servoGroup = g;
    this.built.body.add(g);
  }

  private updateSensor(st: DeviceState): string {
    switch (st.kind) {
      case 'touch': {
        if (this.built.plunger) {
          this.built.plunger.scale.z = st.pressed ? 0.35 : 1;
          this.built.plunger.position.z = this.built.faceZ + (st.pressed ? 0.0014 : 0.004);
          this.built.plunger.material = st.pressed ? pressedMat : releasedMat;
        }
        return st.pressed ? ' <span class="badge on">PRESSED</span>' : ' released';
      }
      case 'digital': {
        if (this.built.indicator) (this.built.indicator.material as THREE.MeshBasicMaterial).color.setHex(st.state ? 0x2ca02c : 0x444444);
        return ` state <b>${st.state}</b>`;
      }
      case 'distance':
        return ` ${st.mm === null ? 'out of range' : num(st.mm, 0) + ' mm'}`;
      case 'color': {
        const m = Math.max(1, st.red, st.green, st.blue);
        if (this.built.swatch) (this.built.swatch.material as THREE.MeshBasicMaterial).color.setRGB(st.red / m, st.green / m, st.blue / m);
        return ` r ${st.red} g ${st.green} b ${st.blue} a ${st.alpha}  ${st.distanceMm === null ? '' : num(st.distanceMm, 0) + ' mm'}`;
      }
      case 'potentiometer':
        if (this.built.knob) this.built.knob.rotation.z = -(st.angleDeg - 135) * DEG;
        return ` ${num(st.angleDeg, 0)} deg ${num(st.volts, 2)} V`;
      case 'analog':
        return ` ${num(st.volts, 2)} V`;
      case 'unsupported':
        return ` <span class="dim">${esc(this.info.tag)} (not simulated)</span>`;
      default:
        return '';
    }
  }
}

const pressedMat = new THREE.MeshStandardMaterial({ color: 0x2ca02c });
const releasedMat = new THREE.MeshStandardMaterial({ color: 0xd62728 });

export class HubView {
  readonly root = new THREE.Group();
  readonly selId: string;
  readonly label: CSS2DObject;
  constructor(readonly name: string, readonly isControlHub: boolean) {
    this.selId = 'hub:' + name;
    const { body } = buildHub(isControlHub);
    this.root.add(body);
    const el = document.createElement('div');
    el.className = 'hub-label';
    el.textContent = name + (isControlHub ? ' (IMU)' : '');
    this.label = new CSS2DObject(el);
    this.label.center.set(0.5, 1);
    tagSelectable(this.root, this.selId);
  }
}

export class ObstacleView {
  readonly root: THREE.Mesh;
  constructor(readonly index: number, size: [number, number, number], color: string) {
    this.root = buildObstacle(size, color);
    this.root.userData.selId = 'obs:' + index;
    this.root.userData.obstacle = true;
  }
  get color(): THREE.Color {
    return (this.root.material as THREE.MeshStandardMaterial).color;
  }
}
