import type { DeviceInfo, ReadyMsg, SceneLayout, Vec3 } from './protocol';
import { restingY } from './dims';

export function normalizeLayout(l: SceneLayout | null | undefined): SceneLayout {
  const out: SceneLayout = l && typeof l === 'object' ? l : { version: 1 };
  if (typeof out.version !== 'number') out.version = 1;
  if (!out.hubs || typeof out.hubs !== 'object') out.hubs = {};
  if (!out.devices || typeof out.devices !== 'object') out.devices = {};
  if (!Array.isArray(out.obstacles)) out.obstacles = [];
  return out;
}

export function isVec3(v: unknown): v is Vec3 {
  return Array.isArray(v) && v.length === 3 && v.every((x) => typeof x === 'number' && Number.isFinite(x));
}

// Devices drawn as their own object in the scene (IMU and voltage live on the hub).
export function hasSceneObject(d: DeviceInfo, hubNames: Set<string>): boolean {
  if (d.kind === 'imu' || d.kind === 'voltage') return false;
  return !hubNames.has(d.name);
}

const KIND_ORDER: Record<string, number> = {
  motor: 0,
  crservo: 1,
  servo: 2,
  touch: 3,
  digital: 4,
  distance: 5,
  color: 6,
  potentiometer: 7,
  analog: 8,
  unsupported: 9,
};

// Grid by hub, sorted by kind then port, 0.16 m apart; actuators float with shafts toward +Z (the default camera).
export function autoLayout(ready: ReadyMsg, layout: SceneLayout): boolean {
  const hubs = layout.hubs!;
  const devs = layout.devices!;
  const hubNames = new Set(ready.hubs.map((h) => h.name));
  let changed = false;
  const hubOrder = ready.hubs.map((h) => h.name);
  for (const d of ready.devices) if (d.hub && !hubOrder.includes(d.hub)) hubOrder.push(d.hub);
  const SP = 0.16;
  const PER_ROW = 4;
  let rowBase = 0;
  hubOrder.forEach((hubName) => {
    const members = ready.devices
      .filter((d) => (d.hub ?? '') === hubName && hasSceneObject(d, hubNames))
      .sort((a, b) => (KIND_ORDER[a.kind] ?? 9) - (KIND_ORDER[b.kind] ?? 9) || (a.port ?? 0) - (b.port ?? 0));
    const rows = Math.max(1, Math.ceil(members.length / PER_ROW));
    if (hubNames.has(hubName) && !(hubs[hubName] && isVec3(hubs[hubName].position))) {
      hubs[hubName] = { ...(hubs[hubName] ?? {}), position: [-0.4, 0.0075, rowBase - ((rows - 1) * SP) / 2], rotation: [0, 0, 0] };
      changed = true;
    }
    members.forEach((d, i) => {
      const dl = devs[d.name] ?? (devs[d.name] = {});
      if (isVec3(dl.position)) return;
      const col = i % PER_ROW;
      const row = Math.floor(i / PER_ROW);
      dl.position = [-0.24 + col * SP, restingY(d), rowBase - row * SP];
      dl.rotation = isVec3(dl.rotation) ? dl.rotation : [0, 0, 0];
      changed = true;
    });
    rowBase -= rows * SP + 0.2;
  });
  // Devices on no known hub.
  const orphans = ready.devices.filter((d) => !d.hub && hasSceneObject(d, hubNames) && !isVec3(devs[d.name]?.position));
  orphans.forEach((d, i) => {
    const dl = devs[d.name] ?? (devs[d.name] = {});
    dl.position = [-0.24 + (i % PER_ROW) * SP, restingY(d), rowBase - Math.floor(i / PER_ROW) * SP];
    dl.rotation = [0, 0, 0];
    changed = true;
  });
  return changed;
}
