import type { DeviceInfo, DeviceLayout, DeviceState, HubInfo, ImuState, ObstacleLayout, SceneLayout, SensorValue, Vec3 } from '../protocol';
import { clear, h, numberInput, selectEl } from '../dom';
import { CARTRIDGE_RATIO, cartridgeRatio, cartridges, motorShape } from '../dims';
import { isVec3 } from '../layout';

export interface InspectorCtx {
  layout(): SceneLayout;
  devices(): DeviceInfo[];
  hubs(): HubInfo[];
  stateOf(name: string): DeviceState | undefined;
  imu(): ImuState | undefined;
  hubVolts(hub: string): number | undefined;
  edited(opts: { device?: string; hub?: string; obstacles?: boolean; rebuild?: boolean }): void;
  sendSensor(name: string, value: SensorValue): void;
  select(id: string | null): void;
  setGizmoMode(m: 'translate' | 'rotate'): void;
  gizmoMode(): 'translate' | 'rotate';
  touchPress(name: string, pressed: boolean): void;
  isTouchPressed(name: string): boolean;
  sceneSensor(name: string): string;
}

const r3 = (v: number): number => Math.round(v * 1e4) / 1e4;

export class InspectorPanel {
  readonly el: HTMLElement;
  private body: HTMLElement;
  private liveEl: HTMLElement | null = null;
  private poseInputs: HTMLInputElement[] = [];
  private sel: string | null = null;
  private liveKey = '';
  private sensorSceneEl: HTMLElement | null = null;

  constructor(private ctx: InspectorCtx) {
    this.body = h('div', { class: 'inspector' });
    this.el = this.body;
    this.show(null);
  }

  get selected(): string | null {
    return this.sel;
  }

  show(selId: string | null): void {
    this.sel = selId;
    this.liveEl = null;
    this.sensorSceneEl = null;
    this.poseInputs = [];
    this.liveKey = '';
    clear(this.body);
    if (!selId) return this.showNothing();
    const [kind, ...rest] = selId.split(':');
    const id = rest.join(':');
    if (kind === 'dev') this.showDevice(id);
    else if (kind === 'hub') this.showHub(id);
    else if (kind === 'obs') this.showObstacle(parseInt(id, 10));
  }

  // ---- nothing selected: walls ----
  private showNothing(): void {
    const L = this.ctx.layout();
    this.body.append(h('div', { class: 'dim small' }, 'Click a device in the 3D view to inspect, move (G) or rotate (R) it. Double-click focuses the camera on it.'));
    const obs = L.obstacles ?? [];
    this.body.append(
      section('Walls (for distance and colour sensors)',
        ...obs.map((o, i) => h('div', { class: 'row' }, h('a', { href: '#', onclick: (e: Event) => (e.preventDefault(), this.ctx.select('obs:' + i)) }, `Wall ${i + 1}`), h('span', { class: 'dim small' }, ` ${o.size.map((v) => (v * 1000).toFixed(0)).join(' x ')} mm`))),
        h('button', { onclick: () => this.addWall() }, 'Add wall'),
      ),
    );
  }

  private addWall(): void {
    const L = this.ctx.layout();
    const o: ObstacleLayout = { kind: 'box', position: [0, 0.1, -0.6], size: [0.6, 0.2, 0.05], color: '#3060ff' };
    L.obstacles = [...(L.obstacles ?? []), o];
    this.ctx.edited({ obstacles: true });
    this.ctx.select('obs:' + (L.obstacles.length - 1));
  }

  // ---- device ----
  private showDevice(name: string): void {
    const info = this.ctx.devices().find((d) => d.name === name);
    if (!info) {
      this.body.append(h('div', null, `Unknown device ${name}`));
      return;
    }
    const L = this.ctx.layout();
    const dl: DeviceLayout = L.devices![name] ?? (L.devices![name] = {});
    this.body.append(
      h('div', { class: 'insp-head' }, h('b', null, name), h('span', { class: 'kind' }, info.kind)),
      h('table', { class: 'kv' },
        h('tr', null, h('td', null, 'type'), h('td', null, info.displayName ? `${info.displayName} (${info.tag})` : info.tag)),
        h('tr', null, h('td', null, 'hub / port'), h('td', null, `${info.hub ?? '-'} / ${info.port ?? '-'}`)),
        info.motor ? h('tr', null, h('td', null, 'spec'), h('td', null, `orientation ${info.motor.orientation ?? '?'}, ${info.motor.ticksPerRev ?? '?'} ticks/rev, free ${info.motor.freeSpeedRpm ?? info.motor.maxRPM ?? '?'} rpm${info.motor.specVerified === false ? ' (unverified spec)' : ''}`)) : null,
      ),
    );
    this.liveEl = h('table', { class: 'kv live' });
    this.body.append(section('Live values', this.liveEl));
    this.body.append(this.poseSection(dl, () => this.ctx.edited({ device: name })));
    if (info.kind === 'motor' && motorShape(info.tag) === 'ultraplanetary') this.body.append(this.cartridgeSection(name, dl));
    if (info.kind === 'motor') {
      const load = selectEl([['free', 'free'], ['wheel', 'wheel'], ['arm', 'arm']], dl.motor?.load ?? 'free', (v) => {
        dl.motor = { ...(dl.motor ?? {}), load: v as 'free' | 'wheel' | 'arm' };
        this.ctx.edited({ device: name });
      });
      this.body.append(section('Load', h('div', { class: 'row' }, load)));
    }
    if (info.kind === 'servo') {
      const range = numberInput(dl.servo?.rangeDeg ?? 270, 5, (v) => {
        dl.servo = { ...(dl.servo ?? {}), rangeDeg: v };
        this.ctx.edited({ device: name, rebuild: true });
      }, { min: 10, max: 360 });
      this.body.append(section('Servo', h('label', null, 'Range (degrees) ', range)));
    }
    const sens = this.sensorSection(info, dl);
    if (sens) this.body.append(sens);
  }

  private poseSection(obj: { position?: Vec3; rotation?: Vec3 }, changed: () => void, withSize?: ObstacleLayout): HTMLElement {
    const pos = isVec3(obj.position) ? obj.position : [0, 0, 0];
    const rot = isVec3(obj.rotation) ? obj.rotation : [0, 0, 0];
    const mk = (arr: 'position' | 'rotation', i: number, v: number, scale: number, step: number): HTMLInputElement => {
      const inp = numberInput(r3(v * scale), step, (nv) => {
        const cur = (isVec3(obj[arr]) ? [...obj[arr]!] : [0, 0, 0]) as Vec3;
        cur[i] = r3(nv / scale);
        obj[arr] = cur;
        changed();
      }, { class: 'narrow' });
      inp.dataset.arr = arr;
      inp.dataset.i = String(i);
      inp.dataset.scale = String(scale);
      this.poseInputs.push(inp);
      return inp;
    };
    const mode = this.ctx.gizmoMode();
    const tBtn = h('button', { class: mode === 'translate' ? 'active' : '', onclick: () => (this.ctx.setGizmoMode('translate'), this.show(this.sel)) }, 'Move (G)');
    const rBtn = h('button', { class: mode === 'rotate' ? 'active' : '', onclick: () => (this.ctx.setGizmoMode('rotate'), this.show(this.sel)) }, 'Rotate (R)');
    const rows: HTMLElement[] = [
      h('tr', null, h('td', null, 'position mm'), h('td', null, mk('position', 0, pos[0], 1000, 5), mk('position', 1, pos[1], 1000, 5), mk('position', 2, pos[2], 1000, 5))),
      h('tr', null, h('td', null, 'rotation deg'), h('td', null, mk('rotation', 0, rot[0], 1, 15), mk('rotation', 1, rot[1], 1, 15), mk('rotation', 2, rot[2], 1, 15))),
    ];
    if (withSize) {
      const sz = (i: number): HTMLInputElement =>
        numberInput(r3(withSize.size[i] * 1000), 10, (nv) => {
          withSize.size[i] = Math.max(0.005, nv / 1000);
          changed();
        }, { class: 'narrow' });
      rows.push(h('tr', null, h('td', null, 'size mm'), h('td', null, sz(0), sz(1), sz(2))));
    }
    return section('Pose', h('div', { class: 'row' }, tBtn, rBtn, h('span', { class: 'dim small' }, 'x right, y up, z back (forward is -z)')), h('table', { class: 'kv' }, ...rows));
  }

  private cartridgeSection(name: string, dl: DeviceLayout): HTMLElement {
    const c = cartridges(dl);
    const box = h('div', null);
    const render = (): void => {
      clear(box);
      const cur = cartridges(dl);
      const count = selectEl([['1', '1 stage'], ['2', '2 stages'], ['3', '3 stages'], ['4', '4 stages']], String(cur.length), (v) => {
        const n = parseInt(v, 10);
        const next = cur.slice(0, n);
        while (next.length < n) next.push('4:1');
        dl.motor = { ...(dl.motor ?? {}), cartridges: next };
        this.ctx.edited({ device: name, rebuild: true });
        render();
      });
      box.append(h('div', { class: 'row' }, count));
      cur.forEach((k, i) => {
        box.append(
          h('div', { class: 'row' }, h('span', { class: 'small' }, `stage ${i + 1} `),
            selectEl(Object.keys(CARTRIDGE_RATIO).map((r) => [r, `${r} (${CARTRIDGE_RATIO[r]})`]), k, (v) => {
              const next = cartridges(dl).slice();
              next[i] = v;
              dl.motor = { ...(dl.motor ?? {}), cartridges: next };
              this.ctx.edited({ device: name, rebuild: true });
              render();
            }),
          ),
        );
      });
      box.append(h('div', { class: 'small' }, `Actual ratio ${cartridgeRatio(cur).toFixed(2)}:1`));
    };
    render();
    void c;
    return section('UltraPlanetary cartridges', box);
  }

  private sensorSection(info: DeviceInfo, dl: DeviceLayout): HTMLElement | null {
    const name = info.name;
    const setOverride = (v: SensorValue | null): void => {
      dl.sensor = { ...(dl.sensor ?? {}), override: v };
      this.ctx.edited({ device: name });
      if (v) this.ctx.sendSensor(name, v);
    };
    const ov = dl.sensor?.override ?? null;
    switch (info.kind) {
      case 'touch':
      case 'digital': {
        const btn = h('button', { class: 'hold' }, 'Hold to press');
        btn.addEventListener('pointerdown', () => this.ctx.touchPress(name, true));
        btn.addEventListener('pointerup', () => this.ctx.touchPress(name, false));
        btn.addEventListener('pointerleave', () => this.ctx.touchPress(name, false));
        const latch = h('input', { type: 'checkbox', checked: Boolean(ov) });
        latch.addEventListener('change', () => {
          const v: SensorValue = info.kind === 'touch' ? { pressed: latch.checked } : { state: latch.checked };
          setOverride(latch.checked ? v : null);
          if (!latch.checked) this.ctx.sendSensor(name, info.kind === 'touch' ? { pressed: false } : { state: false });
        });
        return section('Sensor', h('div', { class: 'row' }, btn, h('label', null, latch, ' latched (stays pressed)')), h('div', { class: 'dim small' }, 'In 3D: click and hold the sensor to press it; shift-click latches.'));
      }
      case 'distance': {
        const useScene = h('input', { type: 'checkbox', checked: !ov });
        const mmIn = h('input', { type: 'range', min: 0, max: 2100, step: 1, value: ov && 'mm' in ov && ov.mm !== null ? ov.mm : 2100 });
        const mmTxt = h('span', { class: 'mono' });
        const upd = (): void => {
          const v = parseFloat(mmIn.value);
          mmTxt.textContent = v > 2000 ? 'nothing in range' : `${v.toFixed(0)} mm`;
        };
        upd();
        useScene.addEventListener('change', () => setOverride(useScene.checked ? null : { mm: parseFloat(mmIn.value) > 2000 ? null : parseFloat(mmIn.value) }));
        mmIn.addEventListener('input', () => {
          upd();
          useScene.checked = false;
          const v = parseFloat(mmIn.value);
          setOverride({ mm: v > 2000 ? null : v });
        });
        this.sensorSceneEl = h('div', { class: 'small dim' });
        return section('Sensor', h('label', null, useScene, ' Use scene (ray along the sensor +Z against walls and devices)'), this.sensorSceneEl, h('div', { class: 'row' }, 'Manual ', mmIn, mmTxt));
      }
      case 'color': {
        const useScene = h('input', { type: 'checkbox', checked: !ov });
        const cur = ov && 'r' in ov ? ov : { r: 1, g: 1, b: 1, distanceMm: 20 };
        const hex = '#' + [cur.r, cur.g, cur.b].map((c) => Math.round(Math.max(0, Math.min(1, c)) * 255).toString(16).padStart(2, '0')).join('');
        const pick = h('input', { type: 'color', value: hex });
        const dist = numberInput(cur.distanceMm ?? 20, 1, () => send(), { class: 'narrow' });
        const send = (): void => {
          const v = pick.value;
          const d = parseFloat(dist.value);
          useScene.checked = false;
          setOverride({ r: parseInt(v.slice(1, 3), 16) / 255, g: parseInt(v.slice(3, 5), 16) / 255, b: parseInt(v.slice(5, 7), 16) / 255, distanceMm: Number.isFinite(d) ? d : null });
        };
        pick.addEventListener('input', send);
        useScene.addEventListener('change', () => (useScene.checked ? setOverride(null) : send()));
        this.sensorSceneEl = h('div', { class: 'small dim' });
        return section('Sensor', h('label', null, useScene, ' Use scene (colour of the wall within 100 mm)'), this.sensorSceneEl, h('div', { class: 'row' }, 'Manual ', pick, ' distance mm ', dist));
      }
      case 'potentiometer': {
        const a = ov && 'angleDeg' in ov ? ov.angleDeg : 135;
        const sl = h('input', { type: 'range', min: 0, max: 270, step: 1, value: a });
        const txt = h('span', { class: 'mono' }, `${a} deg`);
        sl.addEventListener('input', () => {
          txt.textContent = `${sl.value} deg`;
          setOverride({ angleDeg: parseFloat(sl.value) });
        });
        return section('Sensor', h('div', { class: 'row' }, 'Angle ', sl, txt));
      }
      case 'analog': {
        const vv = ov && 'volts' in ov ? ov.volts : 0;
        const sl = h('input', { type: 'range', min: 0, max: 3.3, step: 0.01, value: vv });
        const txt = h('span', { class: 'mono' }, `${vv} V`);
        sl.addEventListener('input', () => {
          txt.textContent = `${sl.value} V`;
          setOverride({ volts: parseFloat(sl.value) });
        });
        return section('Sensor', h('div', { class: 'row' }, 'Voltage ', sl, txt));
      }
      default:
        return null;
    }
  }

  // ---- hub ----
  private showHub(name: string): void {
    const hub = this.ctx.hubs().find((x) => x.name === name);
    const L = this.ctx.layout();
    const hl = L.hubs![name] ?? (L.hubs![name] = {});
    this.body.append(
      h('div', { class: 'insp-head' }, h('b', null, name), h('span', { class: 'kind' }, hub?.kind ?? 'hub')),
      h('div', { class: 'small dim' }, hub?.kind === 'ControlHub' ? 'The Control Hub carries the IMU: rotate the hub to tilt or turn the IMU. RGB arrows are the hub axes x, y, z.' : ''),
    );
    this.liveEl = h('table', { class: 'kv live' });
    this.body.append(section('Live values', this.liveEl));
    this.body.append(this.poseSection(hl, () => this.ctx.edited({ hub: name })));
  }

  // ---- obstacle ----
  private showObstacle(i: number): void {
    const L = this.ctx.layout();
    const o = L.obstacles?.[i];
    if (!o) return this.showNothing();
    const color = h('input', { type: 'color', value: o.color ?? '#3060ff' });
    color.addEventListener('input', () => {
      o.color = color.value;
      this.ctx.edited({ obstacles: true });
    });
    this.body.append(
      h('div', { class: 'insp-head' }, h('b', null, `Wall ${i + 1}`), h('span', { class: 'kind' }, 'obstacle')),
      this.poseSection(o, () => this.ctx.edited({ obstacles: true }), o),
      section('Look', h('label', null, 'Colour (seen by colour sensors) ', color)),
      h('button', {
        class: 'danger',
        onclick: () => {
          L.obstacles!.splice(i, 1);
          this.ctx.edited({ obstacles: true });
          this.ctx.select(null);
        },
      }, 'Delete wall'),
    );
  }

  // Called ~10 times a second.
  refreshLive(): void {
    if (!this.sel) return;
    const [kind, ...rest] = this.sel.split(':');
    const id = rest.join(':');
    if (this.sensorSceneEl) this.sensorSceneEl.textContent = this.ctx.sceneSensor(id);
    if (!this.liveEl) return;
    let rows: Array<[string, string]> = [];
    if (kind === 'dev') {
      const st = this.ctx.stateOf(id);
      if (st) rows = Object.entries(st).filter(([k]) => k !== 'kind').map(([k, v]) => [k, fmtVal(v)]);
      else rows = [['', 'no data yet']];
    } else if (kind === 'hub') {
      const imu = this.ctx.imu();
      const hub = this.ctx.hubs().find((x) => x.name === id);
      if (imu && hub?.kind === 'ControlHub') {
        rows.push(['IMU yaw', `${imu.yawDeg.toFixed(1)} deg`], ['IMU pitch', `${imu.pitchDeg.toFixed(1)} deg`], ['IMU roll', `${imu.rollDeg.toFixed(1)} deg`], ['IMU initialised', String(imu.initialized)]);
      }
      const v = this.ctx.hubVolts(id);
      if (v !== undefined) rows.push(['battery', `${v.toFixed(2)} V`]);
      if (!rows.length) rows.push(['', 'no data yet']);
    }
    const key = JSON.stringify(rows);
    if (key === this.liveKey) return;
    this.liveKey = key;
    clear(this.liveEl);
    for (const [k, v] of rows) this.liveEl.append(h('tr', null, h('td', null, k), h('td', { class: 'mono' }, v)));
  }

  // Pose changed from the gizmo: update the numbers unless one is being typed in.
  refreshPose(obj: { position?: Vec3; rotation?: Vec3 } | undefined): void {
    if (!obj) return;
    for (const inp of this.poseInputs) {
      if (document.activeElement === inp) continue;
      const arr = inp.dataset.arr as 'position' | 'rotation';
      const v = obj[arr];
      if (!isVec3(v)) continue;
      inp.value = String(r3(v[parseInt(inp.dataset.i!, 10)] * parseFloat(inp.dataset.scale!)));
    }
  }
}

function fmtVal(v: unknown): string {
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(3);
  if (v === null) return 'null';
  return typeof v === 'object' ? JSON.stringify(v) : String(v);
}

function section(title: string, ...children: Array<Node | null>): HTMLElement {
  return h('div', { class: 'insp-sec' }, h('div', { class: 'insp-title' }, title), ...children);
}
