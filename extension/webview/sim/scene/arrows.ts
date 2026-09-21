import * as THREE from 'three';
import { C, spinColor } from './colors';

const LEVELS = 12;
const torusCache = new Map<string, THREE.TorusGeometry>();

function torusArc(radius: number, tube: number, arc: number): THREE.TorusGeometry {
  const key = `${radius.toFixed(4)}|${tube.toFixed(5)}|${arc.toFixed(3)}`;
  let g = torusCache.get(key);
  if (!g) {
    g = new THREE.TorusGeometry(radius, tube, 8, Math.max(12, Math.round((arc / (Math.PI * 2)) * 64)), arc);
    torusCache.set(key, g);
  }
  return g;
}

const coneGeom = new THREE.ConeGeometry(1, 1, 16);
coneGeom.translate(0, 0.5, 0);

function makeMat(color: number): THREE.MeshBasicMaterial {
  return new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, depthTest: true });
}

// A curved arrow in the local XY plane, around local +Z. CCW is drawn as seen looking down -Z from +Z
// (i.e. looking at the face the arrow sits in front of); CW is the same shape mirrored.
export class ArcArrow {
  readonly group = new THREE.Group();
  private arcMesh: THREE.Mesh;
  private head: THREE.Mesh;
  private ring: THREE.Mesh;
  private mat: THREE.MeshBasicMaterial;
  private ringMat: THREE.MeshBasicMaterial;
  private ghostMat: THREE.MeshBasicMaterial;
  private arcGhost: THREE.Mesh;
  private headGhost: THREE.Mesh;
  private key = '';

  constructor(
    private radius: number,
    private minTube: number,
    private maxTube: number,
    private startDeg = 90,
    private minSweepDeg = 70,
    private maxSweepDeg = 320,
  ) {
    this.mat = makeMat(C.ccw);
    this.ringMat = makeMat(C.stopped);
    // A faint copy drawn through everything, so the direction stays readable when the arrow is behind
    // the motor body or another device.
    this.ghostMat = makeMat(C.ccw);
    this.ghostMat.depthTest = false;
    this.ghostMat.depthWrite = false;
    this.ghostMat.transparent = true;
    this.ghostMat.opacity = 0.3;
    this.ringMat.transparent = true;
    this.ringMat.opacity = 0.7;
    this.arcMesh = new THREE.Mesh(torusArc(radius, minTube, Math.PI), this.mat);
    this.head = new THREE.Mesh(coneGeom, this.mat);
    this.ring = new THREE.Mesh(torusArc(radius, minTube * 0.6, Math.PI * 2), this.ringMat);
    this.arcGhost = new THREE.Mesh(this.arcMesh.geometry, this.ghostMat);
    this.headGhost = new THREE.Mesh(coneGeom, this.ghostMat);
    this.arcGhost.renderOrder = 10;
    this.headGhost.renderOrder = 10;
    this.group.add(this.arcMesh, this.head, this.ring, this.arcGhost, this.headGhost);
    this.set(0, 0);
  }

  // dir: +1 CCW, -1 CW, 0 stopped. frac: 0..1 magnitude.
  set(dir: number, frac: number, color?: number): void {
    const level = dir === 0 ? 0 : Math.max(1, Math.round(Math.min(1, Math.abs(frac)) * LEVELS));
    const key = `${dir}|${level}|${color ?? ''}`;
    if (key === this.key) return;
    this.key = key;
    const stopped = dir === 0;
    this.ring.visible = stopped;
    this.arcMesh.visible = !stopped;
    this.head.visible = !stopped;
    this.arcGhost.visible = !stopped;
    this.headGhost.visible = !stopped;
    if (stopped) return;
    const f = level / LEVELS;
    const sweep = THREE.MathUtils.degToRad(this.minSweepDeg + (this.maxSweepDeg - this.minSweepDeg) * f);
    const tube = this.minTube + (this.maxTube - this.minTube) * f;
    this.mat.color.setHex(color ?? spinColor(dir > 0 ? 'CCW' : 'CW'));
    this.arcMesh.geometry = torusArc(this.radius, tube, sweep);
    const a0 = THREE.MathUtils.degToRad(this.startDeg);
    this.arcMesh.rotation.z = a0;
    const aEnd = a0 + sweep;
    const headLen = Math.max(tube * 5, this.radius * 0.45);
    const headR = Math.max(tube * 2.6, this.radius * 0.2);
    this.head.scale.set(headR, headLen, headR);
    this.head.position.set(Math.cos(aEnd) * this.radius, Math.sin(aEnd) * this.radius, 0);
    // Cone points along local +Y; rotating by aEnd aligns it with the CCW tangent (-sin, cos).
    this.head.rotation.set(0, 0, aEnd);
    this.ghostMat.color.copy(this.mat.color);
    this.arcGhost.geometry = this.arcMesh.geometry;
    this.arcGhost.rotation.copy(this.arcMesh.rotation);
    this.headGhost.position.copy(this.head.position);
    this.headGhost.rotation.copy(this.head.rotation);
    this.headGhost.scale.copy(this.head.scale);
    this.group.scale.x = dir > 0 ? 1 : -1;
  }
}

// Straight flat arrow along +Y of its group, length set at run time.
export class StraightArrow {
  readonly group = new THREE.Group();
  private shaft: THREE.Mesh;
  private head: THREE.Mesh;
  private mat: THREE.MeshBasicMaterial;
  constructor(color: number, private radius: number) {
    this.mat = makeMat(color);
    const sg = new THREE.CylinderGeometry(1, 1, 1, 12);
    sg.translate(0, 0.5, 0);
    this.shaft = new THREE.Mesh(sg, this.mat);
    this.head = new THREE.Mesh(coneGeom, this.mat);
    this.group.add(this.shaft, this.head);
    this.shaft.renderOrder = 2;
    this.head.renderOrder = 2;
  }
  setColor(c: number): void {
    this.mat.color.setHex(c);
  }
  // Points the arrow from its origin along dir (world or parent frame) with the given length.
  set(dir: THREE.Vector3, length: number): void {
    if (length <= 1e-6 || dir.lengthSq() < 1e-12) {
      this.group.visible = false;
      return;
    }
    this.group.visible = true;
    const headLen = Math.min(length * 0.45, this.radius * 6);
    const shaftLen = Math.max(0, length - headLen);
    this.shaft.scale.set(this.radius, shaftLen || 1e-4, this.radius);
    this.head.position.set(0, shaftLen, 0);
    this.head.scale.set(this.radius * 2.6, headLen, this.radius * 2.6);
    this.group.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
  }
}

export function thinArc(radius: number, tube: number, startRad: number, arcRad: number, color: number): THREE.Mesh {
  const m = new THREE.Mesh(torusArc(radius, tube, Math.max(0.01, arcRad)), makeMat(color));
  m.rotation.z = startRad;
  return m;
}
