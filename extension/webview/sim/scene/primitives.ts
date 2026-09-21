import * as THREE from 'three';
import type { DeviceInfo, DeviceLayout } from '../protocol';
import { C } from './colors';
import {
  COREHEX,
  HUB_BODY,
  MOTOR_CAN,
  MOTOR_DIA,
  SENSOR_BODY,
  SERVO_BODY,
  SHAFT_LEN,
  STAGE_LEN,
  actuatorLength,
  motorShape,
  stageCount,
} from '../dims';

const matCache = new Map<number, THREE.MeshStandardMaterial>();
export function mat(color: number): THREE.MeshStandardMaterial {
  let m = matCache.get(color);
  if (!m) {
    m = new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.25 });
    matCache.set(color, m);
  }
  return m;
}

let capTexture: THREE.CanvasTexture | null = null;
// Yellow cap with a black radial notch and the word SHAFT: marks the face that CW/CCW is judged from,
// and rotates with the shaft so motion is visible even when the arrow is small.
function shaftCapTexture(): THREE.CanvasTexture {
  if (capTexture) return capTexture;
  const cv = document.createElement('canvas');
  cv.width = cv.height = 256;
  const g = cv.getContext('2d')!;
  g.fillStyle = '#f0e442';
  g.beginPath();
  g.arc(128, 128, 126, 0, Math.PI * 2);
  g.fill();
  g.fillStyle = '#1a1a1a';
  g.fillRect(118, 0, 20, 128);
  g.beginPath();
  g.arc(128, 128, 22, 0, Math.PI * 2);
  g.fill();
  g.font = 'bold 44px sans-serif';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.fillText('SHAFT', 128, 190);
  capTexture = new THREE.CanvasTexture(cv);
  capTexture.colorSpace = THREE.SRGBColorSpace;
  return capTexture;
}

function shaftCap(radius: number): THREE.Mesh {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(radius, 40),
    new THREE.MeshBasicMaterial({ map: shaftCapTexture(), side: THREE.FrontSide }),
  );
  m.name = 'shaftCap';
  return m;
}

// Bright flag on the shaft tip that sticks out past the body outline, so rotation is readable from the
// side and from behind too, not only when looking at the shaft face.
function shaftFin(length: number, z: number): THREE.Group {
  const g = new THREE.Group();
  const bar = new THREE.Mesh(new THREE.BoxGeometry(0.008, length, 0.004), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  bar.position.set(0, length / 2, z);
  const tip = new THREE.Mesh(new THREE.BoxGeometry(0.011, 0.011, 0.005), new THREE.MeshBasicMaterial({ color: 0xd62728 }));
  tip.position.set(0, length - 0.0055, z);
  g.add(bar, tip);
  return g;
}

// Yellow band around the edge of the shaft face: marks which end is the shaft from any side.
function faceRing(radius: number, z: number): THREE.Mesh {
  const m = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.0018, 8, 48), new THREE.MeshBasicMaterial({ color: 0xf0e442 }));
  m.position.z = z;
  return m;
}

function cylZ(r: number, len: number, color: number, segments = 32): THREE.Mesh {
  const g = new THREE.CylinderGeometry(r, r, len, segments);
  g.rotateX(Math.PI / 2);
  return new THREE.Mesh(g, mat(color));
}

function box(x: number, y: number, z: number, color: number): THREE.Mesh {
  return new THREE.Mesh(new THREE.BoxGeometry(x, y, z), mat(color));
}

export interface BuiltDevice {
  body: THREE.Group;
  rotor: THREE.Group | null;
  faceZ: number;
  arrowRadius: number;
  // Servo only: horn group (rotated to angleDeg) and the z of the horn plane.
  horn?: THREE.Group;
  hornZ?: number;
  // Sensors: parts that change with state.
  plunger?: THREE.Mesh;
  swatch?: THREE.Mesh;
  knob?: THREE.Group;
  indicator?: THREE.Mesh;
}

export function buildDevice(info: DeviceInfo, dl: DeviceLayout | undefined): BuiltDevice {
  switch (info.kind) {
    case 'motor':
      return buildMotor(info, dl);
    case 'servo':
    case 'crservo':
      return buildServo(info, dl);
    default:
      return buildSensor(info);
  }
}

function buildMotor(info: DeviceInfo, dl: DeviceLayout | undefined): BuiltDevice {
  const body = new THREE.Group();
  const rotor = new THREE.Group();
  const shape = motorShape(info.tag);
  const L = actuatorLength(info, dl);
  const faceZ = L / 2;
  if (shape === 'corehex') {
    const b = new THREE.Mesh(roundedBox(COREHEX, COREHEX, L, 0.006), mat(C.motorBody));
    body.add(b);
    const ring = cylZ(0.012, 0.003, C.darkMetal);
    ring.position.z = faceZ + 0.0015;
    body.add(ring);
  } else {
    const r = MOTOR_DIA / 2;
    const can = cylZ(r, MOTOR_CAN, shape === 'generic' ? 0x555a60 : C.motorBody);
    can.position.z = -L / 2 + MOTOR_CAN / 2;
    body.add(can);
    const n = stageCount(info, dl);
    for (let i = 0; i < n; i++) {
      const st = cylZ(r * 1.02, STAGE_LEN * 0.92, i % 2 ? C.stage : C.metal);
      st.position.z = -L / 2 + MOTOR_CAN + STAGE_LEN * (i + 0.5);
      body.add(st);
      const band = cylZ(r * 1.06, 0.002, C.darkMetal);
      band.position.z = -L / 2 + MOTOR_CAN + STAGE_LEN * i;
      body.add(band);
    }
  }
  const capR = shape === 'corehex' ? COREHEX * 0.42 : MOTOR_DIA * 0.45;
  const cap = shaftCap(capR);
  cap.position.z = 0.0035;
  rotor.add(cap);
  const shaft = cylZ(0.004, SHAFT_LEN, C.metal, 6);
  shaft.position.z = SHAFT_LEN / 2;
  rotor.add(shaft);
  const outline = shape === 'corehex' ? COREHEX * 0.72 : MOTOR_DIA * 0.5;
  rotor.add(shaftFin(outline + 0.012, SHAFT_LEN - 0.003));
  rotor.position.z = faceZ;
  body.add(rotor);
  if (shape !== 'corehex') body.add(faceRing(MOTOR_DIA * 0.515, faceZ - 0.001));
  return { body, rotor, faceZ, arrowRadius: (shape === 'corehex' ? COREHEX * 0.62 : MOTOR_DIA * 0.72) };
}

function buildServo(info: DeviceInfo, _dl: DeviceLayout | undefined): BuiltDevice {
  const body = new THREE.Group();
  const B = SERVO_BODY;
  const b = box(B.x, B.y, B.z, C.servoBody);
  body.add(b);
  const ears = box(B.x * 1.36, B.y * 0.9, 0.003, C.servoBody);
  ears.position.z = B.z * 0.22;
  body.add(ears);
  const faceZ = B.z / 2;
  // Output spline sits off-centre on the top face, like the real Smart Robot Servo.
  const splineX = B.x * 0.22;
  const rotor = new THREE.Group();
  rotor.position.set(splineX, 0, faceZ);
  const spline = cylZ(0.004, 0.006, C.metal, 12);
  spline.position.z = 0.003;
  rotor.add(spline);
  body.add(rotor);
  if (info.kind === 'crservo') {
    const disc = cylZ(0.019, 0.004, 0x3a3f46);
    disc.position.z = 0.008;
    rotor.add(disc);
    const cap = shaftCap(0.018);
    cap.position.z = 0.0105;
    rotor.add(cap);
    rotor.add(shaftFin(0.03, 0.013));
    return { body, rotor, faceZ: faceZ + 0.01, arrowRadius: 0.027 };
  }
  const horn = new THREE.Group();
  horn.position.set(splineX, 0, faceZ + 0.008);
  const arm = box(0.007, 0.03, 0.003, 0xe8e8e8);
  arm.position.y = 0.011;
  horn.add(arm);
  const hub = cylZ(0.006, 0.004, 0xe8e8e8, 16);
  horn.add(hub);
  const tip = cylZ(0.0025, 0.0045, C.servoTarget, 10);
  tip.position.set(0, 0.024, 0);
  horn.add(tip);
  const cap = shaftCap(0.0055);
  cap.position.z = 0.0022;
  horn.add(cap);
  body.add(horn);
  return { body, rotor: null, faceZ: faceZ + 0.008, arrowRadius: 0.035, horn, hornZ: faceZ + 0.008 };
}

function buildSensor(info: DeviceInfo): BuiltDevice {
  const body = new THREE.Group();
  const S = SENSOR_BODY;
  const out: BuiltDevice = { body, rotor: null, faceZ: S.z / 2, arrowRadius: 0.02 };
  switch (info.kind) {
    case 'touch': {
      body.add(box(S.x, S.y, S.z, 0x2d2d33));
      const plunger = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.008, 16).rotateX(Math.PI / 2), mat(0xd62728));
      plunger.position.z = S.z / 2 + 0.004;
      body.add(plunger);
      out.plunger = plunger;
      break;
    }
    case 'digital': {
      body.add(box(S.x * 0.9, S.y, S.z * 0.8, 0x2e3a2e));
      const ind = new THREE.Mesh(new THREE.SphereGeometry(0.003, 12, 8), new THREE.MeshBasicMaterial({ color: 0x444444 }));
      ind.position.set(0, S.y / 2 + 0.002, 0);
      body.add(ind);
      out.indicator = ind;
      break;
    }
    case 'distance': {
      body.add(box(S.x, S.y, S.z, 0x202a40));
      const lens = cylZ(0.004, 0.002, 0x101010, 16);
      lens.position.z = S.z / 2 + 0.001;
      body.add(lens);
      break;
    }
    case 'color': {
      body.add(box(S.x * 0.8, S.y, S.z, 0x3a2040));
      const sw = new THREE.Mesh(new THREE.PlaneGeometry(0.014, 0.008), new THREE.MeshBasicMaterial({ color: 0xffffff }));
      sw.position.z = S.z / 2 + 0.0005;
      body.add(sw);
      out.swatch = sw;
      break;
    }
    case 'potentiometer':
    case 'analog': {
      body.add(box(S.x * 0.8, S.y, S.z * 0.8, 0x403a20));
      const knob = new THREE.Group();
      const k = cylZ(0.006, 0.008, 0xcfcfcf, 20);
      k.position.z = 0.004;
      knob.add(k);
      const mark = box(0.0015, 0.005, 0.0012, 0x111111);
      mark.position.set(0, 0.003, 0.0085);
      knob.add(mark);
      knob.position.z = S.z * 0.4;
      body.add(knob);
      out.knob = knob;
      break;
    }
    default:
      body.add(box(S.x, S.y, S.z, C.unsupported));
  }
  return out;
}

export function buildHub(isControlHub: boolean): { body: THREE.Group; axes: THREE.Group } {
  const body = new THREE.Group();
  const B = HUB_BODY;
  const b = new THREE.Mesh(roundedBox(B.x, B.y, B.z, 0.008), mat(isControlHub ? C.hub : 0x2a3340));
  body.add(b);
  const stripe = box(B.x * 0.96, 0.001, 0.012, isControlHub ? 0xe03a3a : 0x3a7ae0);
  stripe.position.set(0, B.y / 2 + 0.0005, -B.z / 2 + 0.012);
  body.add(stripe);
  // The simulated IMU takes this model's pose literally, with the SDK's reference
  // orientation (RevHubOrientationOnRobot UP/FORWARD = identity): REV logo on the top
  // face (+Y) and the USB ports on the -Z face (robot forward). Both are marked.
  const logo = box(0.03, 0.001, 0.03, 0xf5f5f5);
  logo.position.set(0, B.y / 2 + 0.0008, 0.02);
  body.add(logo);
  const usb = box(0.03, B.y * 0.5, 0.004, 0x111111);
  usb.position.set(0, 0, -B.z / 2 - 0.002);
  body.add(usb);
  const axes = new THREE.Group();
  if (isControlHub) {
    const mk = (color: number, dir: THREE.Vector3): THREE.ArrowHelper =>
      new THREE.ArrowHelper(dir, new THREE.Vector3(0, B.y / 2 + 0.002, 0), 0.06, color, 0.014, 0.008);
    axes.add(mk(0xe03a3a, new THREE.Vector3(1, 0, 0)), mk(0x2ca02c, new THREE.Vector3(0, 1, 0)), mk(0x1f77d0, new THREE.Vector3(0, 0, 1)));
    body.add(axes);
  }
  return { body, axes };
}

function roundedBox(x: number, y: number, z: number, r: number): THREE.BufferGeometry {
  const shape = new THREE.Shape();
  const hx = x / 2 - r;
  const hy = y / 2 - r;
  if (hy <= 0) return new THREE.BoxGeometry(x, y, z);
  shape.moveTo(-hx, -y / 2);
  shape.lineTo(hx, -y / 2);
  shape.quadraticCurveTo(x / 2, -y / 2, x / 2, -hy);
  shape.lineTo(x / 2, hy);
  shape.quadraticCurveTo(x / 2, y / 2, hx, y / 2);
  shape.lineTo(-hx, y / 2);
  shape.quadraticCurveTo(-x / 2, y / 2, -x / 2, hy);
  shape.lineTo(-x / 2, -hy);
  shape.quadraticCurveTo(-x / 2, -y / 2, -hx, -y / 2);
  const g = new THREE.ExtrudeGeometry(shape, { depth: z, bevelEnabled: false, curveSegments: 4 });
  g.translate(0, 0, -z / 2);
  return g;
}

export function buildObstacle(size: [number, number, number], color: string): THREE.Mesh {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(size[0], size[1], size[2]),
    new THREE.MeshStandardMaterial({ color: new THREE.Color(color), roughness: 0.8, transparent: true, opacity: 0.85 }),
  );
  return m;
}
