import * as THREE from 'three';
import type {
  DeviceInfo,
  DeviceState,
  ExtToWebview,
  GamepadState,
  GamepadType,
  ImuState,
  PyLoc,
  ReadyMsg,
  SceneLayout,
  SensorValue,
  SimCommand,
  SimMsg,
  StateMsg,
  TelemetryMsg,
  TraceMsg,
  Vec3,
} from './protocol';
import { Host } from './vscode';
import { Recorder } from './recorder';
import { h, clear } from './dom';
import { autoLayout, hasSceneObject, isVec3, normalizeLayout } from './layout';
import { Viewport } from './scene/viewport';
import { DeviceView, HubView, LabelMode, ObstacleView, applyPose } from './scene/deviceView';
import { GamepadPanel } from './ui/gamepads';
import { WatchPanel, resolvePath, formatLeaf, pathLabel, pathKey } from './ui/watch';
import { DriverHubPanel } from './ui/driverHub';
import { TimelinePanel } from './ui/timeline';
import { InspectorPanel } from './ui/inspector';
import { KEYBOARD_CODES, gamepadEnv } from './gamepadInput';
import { CodePanel } from './ui/code';

const DEG = 180 / Math.PI;
const FLY_CODES = new Set(['KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyQ', 'KeyE', 'ShiftLeft', 'ShiftRight']);

function r4(v: number): number {
  return Math.round(v * 10000) / 10000;
}

export class App {
  private host = new Host();
  private rec = new Recorder();
  private ready: ReadyMsg | null = null;
  private layout: SceneLayout = normalizeLayout(null);
  private live: StateMsg | null = null;
  private liveAt = 0;
  private liveTelemetry: TelemetryMsg | null = null;
  private infos = new Map<string, DeviceInfo>();
  private views = new Map<string, DeviceView>();
  private hubViews = new Map<string, HubView>();
  private obstacleViews: ObstacleView[] = [];
  private selected: string | null = null;
  private gizmoMode: 'translate' | 'rotate' = 'translate';
  private labels: LabelMode;
  private snapOn: boolean;
  private keysMode: 0 | 1 | 2 = 0;
  private keys = new Set<string>();
  private paused = false;
  private replayT: number | null = null;
  private touchHeld = new Set<string>();
  private lastSensor = new Map<string, string>();
  private sceneSensorText = new Map<string, string>();
  private layoutTimer = 0;
  private cameraTimer = 0;
  private lastFrameTime = performance.now();
  private lastInspector = 0;
  private lastPhase = '';
  private pointerStart: { x: number; y: number; id: string | null; touch: string | null } | null = null;

  private vp!: Viewport;
  private gamepads!: GamepadPanel;
  private watch!: WatchPanel;
  private code!: CodePanel;
  private liveTrace: TraceMsg | null = null;
  private hub!: DriverHubPanel;
  private timeline!: TimelinePanel;
  private inspector!: InspectorPanel;
  private vpEl!: HTMLElement;
  private pinnedEl!: HTMLElement;
  private bannerEl!: HTMLElement;
  private keysBtns: HTMLButtonElement[] = [];
  private modeBtns: HTMLButtonElement[] = [];
  private emptyEl!: HTMLElement;

  constructor(private root: HTMLElement) {
    const ui = this.host.ui;
    this.labels = ui.labels === 'off' || ui.labels === 'full' ? ui.labels : 'short';
    this.snapOn = Boolean(ui.snap);
    this.buildDom();
    this.applyTheme();
    new MutationObserver(() => this.applyTheme()).observe(document.body, { attributes: true, attributeFilter: ['class'] });
    window.addEventListener('message', (e) => this.onMessage(e.data as ExtToWebview));
    this.host.post({ type: 'ready' });
    this.host.post(gamepadEnv());
    requestAnimationFrame(() => this.frame());
  }

  // ---------------- DOM ----------------

  private buildDom(): void {
    const ui = this.host.ui;
    this.vpEl = h('div', { class: 'viewport', tabindex: 0 });
    this.vp = new Viewport(this.vpEl);
    this.vp.setSnap(this.snapOn);
    this.vp.gizmo.addEventListener('objectChange', () => this.onGizmoChange());
    this.vp.orbit.addEventListener('end', () => this.saveCameraSoon());

    this.pinnedEl = h('div', { class: 'pinned' });
    this.bannerEl = h('div', { class: 'replay-banner' });
    this.emptyEl = h('div', { class: 'empty-note' }, 'Waiting for the simulator to load the robot configuration...');

    this.keysBtns = (['Camera', 'Gamepad 1', 'Gamepad 2'] as const).map((l, i) =>
      h('button', { onclick: () => this.setKeysMode(i as 0 | 1 | 2), title: 'Tab cycles while the 3D view has focus' }, l),
    );
    const labelsSel = h('select', { title: 'Labels next to each device (the selected device always shows the full label)' },
      h('option', { value: 'off' }, 'off'), h('option', { value: 'short' }, 'short'), h('option', { value: 'full' }, 'full'));
    labelsSel.value = this.labels;
    labelsSel.addEventListener('change', () => {
      this.labels = labelsSel.value as LabelMode;
      this.host.savePrefs({ labels: this.labels });
    });
    const snapChk = h('input', { type: 'checkbox', checked: this.snapOn });
    snapChk.addEventListener('change', () => {
      this.snapOn = snapChk.checked;
      this.vp.setSnap(this.snapOn);
      this.host.savePrefs({ snap: this.snapOn });
    });
    this.modeBtns = [
      h('button', { onclick: () => this.setGizmoMode('translate'), title: 'G' }, 'Move'),
      h('button', { onclick: () => this.setGizmoMode('rotate'), title: 'R' }, 'Rotate'),
    ];
    const toolbar = h(
      'div',
      { class: 'vp-toolbar' },
      h('div', { class: 'seg' }, h('span', { class: 'seg-l' }, 'Keys:'), ...this.keysBtns),
      h('div', { class: 'seg' }, ...this.modeBtns, h('label', null, snapChk, ' Snap 5 mm / 15°'), h('label', null, 'Labels ', labelsSel)),
    );
    const hint = h(
      'div',
      { class: 'vp-hint' },
      'Drag: orbit · Right/Shift-drag: pan · Wheel: zoom · WASD QE: fly (Shift faster) · Click: select · Double-click: focus · G/R: move/rotate · Esc: deselect',
    );
    const legend = h(
      'div',
      { class: 'vp-legend' },
      h('span', { class: 'sw ccw' }), ' \u21ba CCW  ', h('span', { class: 'sw cw' }), ' \u21bb CW  as seen looking at the yellow SHAFT face. ',
      h('span', { class: 'dim' }, 'Spin is animated slower than real (about 1 turn/s at free speed) so it never strobes; direction and relative speed are exact.'),
    );
    this.vpEl.append(this.pinnedEl, toolbar, this.bannerEl, this.emptyEl, legend, hint);
    this.wireViewport();

    this.gamepads = new GamepadPanel(
      {
        send: (index, type, state) => this.sendGamepad(index, type, state),
        openBridge: () => this.host.post({ type: 'openGamepadBridge' }),
        prefsChanged: (types, sources) => this.host.savePrefs({ gamepadTypes: types, gamepadSources: sources }),
        keyboardSlotChanged: (i) => {
          this.keysMode = i;
          this.renderKeysMode();
        },
      },
      ui.gamepadTypes ?? {},
      ui.gamepadSources ?? {},
    );
    this.keysMode = this.gamepads.keyboardSlot();
    this.watch = new WatchPanel(
      {
        selectDevice: (n) => this.select('dev:' + n),
        pinsChanged: (pins) => this.host.savePrefs({ pinned: pins.map((p) => JSON.stringify(p)) }),
      },
      (ui.pinned ?? []).map((s) => {
        try {
          return JSON.parse(s) as string[];
        } catch {
          return [s];
        }
      }),
    );
    this.code = new CodePanel({ openSource: (l) => this.openSource(l), selectDevice: (n) => this.select('dev:' + n) }, this.watch.el);
    this.hub = new DriverHubPanel(
      {
        init: (op) => this.sim({ type: 'init', opMode: op }),
        start: () => this.sim({ type: 'start' }),
        stop: () => this.sim({ type: 'stop' }),
        rebuild: () => this.host.post({ type: 'rebuild' }),
        debug: () => this.host.post({ type: 'debug' }),
        speed: (f) => this.sim({ type: 'speed', factor: f }),
        pause: (p) => this.setPaused(p),
        openSource: (l) => this.openSource(l),
        opModeChosen: (n) => this.host.savePrefs({ opMode: n }),
      },
      ui.opMode,
    );
    this.inspector = new InspectorPanel({
      layout: () => this.layout,
      devices: () => this.ready?.devices ?? [],
      hubs: () => this.ready?.hubs ?? [],
      stateOf: (n) => this.viewFrame()?.devices?.[n],
      imu: () => this.imuState(),
      hubVolts: (n) => {
        const st = this.viewFrame()?.devices?.[n];
        return st && st.kind === 'voltage' ? st.volts : undefined;
      },
      edited: (o) => this.edited(o),
      sendSensor: (n, v) => this.sendSensor(n, v, true),
      select: (id) => this.select(id),
      setGizmoMode: (m) => this.setGizmoMode(m),
      gizmoMode: () => this.gizmoMode,
      touchPress: (n, p) => this.touchPress(n, p),
      isTouchPressed: (n) => this.touchHeld.has(n),
      sceneSensor: (n) => this.sceneSensorText.get(n) ?? '',
    });
    this.timeline = new TimelinePanel(this.rec, {
      scrub: (t) => this.setReplay(t),
      pauseSim: (p) => this.setPaused(p),
      openSource: (l) => this.openSource(l),
      kindOf: (d) => this.infos.get(d)?.kind ?? '',
      selectDevice: (d) => this.infos.has(d) && this.select('dev:' + d),
    });

    const collapsed = ui.collapsed ?? {};
    const section = (id: string, title: string, body: HTMLElement): HTMLElement => {
      const sec = h('section', { class: 'side-sec' + (collapsed[id] ? ' collapsed' : ''), 'data-id': id });
      const head = h('header', { onclick: () => {
        sec.classList.toggle('collapsed');
        collapsed[id] = sec.classList.contains('collapsed');
        this.host.savePrefs({ collapsed });
      } }, h('span', { class: 'chev' }), title);
      sec.append(head, h('div', { class: 'side-body' }, body));
      return sec;
    };
    const sidebar = h(
      'div',
      { class: 'sidebar' },
      section('hub', 'Driver Hub', this.hub.el),
      section('gamepads', 'Gamepads', this.gamepads.el),
      section('code', 'Code (live)', this.code.el),
      section('inspector', 'Inspector', this.inspector.el),
    );
    const vsplit = h('div', { class: 'vsplit', title: 'Drag to resize' });
    const hsplit = h('div', { class: 'hsplit', title: 'Drag to resize' });
    const shell = h('div', { class: 'shell' }, h('div', { class: 'main' }, this.vpEl, vsplit, sidebar), hsplit, this.timeline.el);
    clear(this.root);
    this.root.append(shell);
    const sw = ui.sidebarWidth ?? 380;
    const th = ui.timelineHeight ?? 190;
    shell.style.setProperty('--side-w', sw + 'px');
    shell.style.setProperty('--tl-h', th + 'px');
    this.dragSplit(vsplit, 'x', (d0) => {
      const w = Math.max(260, Math.min(window.innerWidth - 300, d0));
      shell.style.setProperty('--side-w', w + 'px');
      this.host.savePrefs({ sidebarWidth: w });
    }, () => parseFloat(shell.style.getPropertyValue('--side-w')));
    this.dragSplit(hsplit, 'y', (d0) => {
      const hh = Math.max(90, Math.min(window.innerHeight - 250, d0));
      shell.style.setProperty('--tl-h', hh + 'px');
      this.host.savePrefs({ timelineHeight: hh });
    }, () => parseFloat(shell.style.getPropertyValue('--tl-h')));
    this.renderKeysMode();
    this.renderGizmoMode();
  }

  private dragSplit(el: HTMLElement, axis: 'x' | 'y', set: (v: number) => void, get: () => number): void {
    el.addEventListener('pointerdown', (e) => {
      el.setPointerCapture(e.pointerId);
      const start = axis === 'x' ? e.clientX : e.clientY;
      const v0 = get();
      const move = (ev: PointerEvent): void => set(v0 - ((axis === 'x' ? ev.clientX : ev.clientY) - start));
      const up = (): void => {
        el.removeEventListener('pointermove', move);
        el.removeEventListener('pointerup', up);
      };
      el.addEventListener('pointermove', move);
      el.addEventListener('pointerup', up);
    });
  }

  private applyTheme(): void {
    const light = document.body.classList.contains('vscode-light') || document.body.classList.contains('vscode-high-contrast-light');
    this.vp.setTheme(!light);
  }

  // ---------------- viewport interaction ----------------

  private wireViewport(): void {
    const canvas = this.vp.canvas;
    canvas.addEventListener('pointerdown', (e) => {
      this.vpEl.focus({ preventScroll: true });
      if (e.button !== 0) return;
      const gizmoAxis = (this.vp.gizmo as unknown as { axis: string | null }).axis;
      if (gizmoAxis) {
        this.pointerStart = null;
        return;
      }
      const hit = this.vp.pick(e.clientX, e.clientY);
      let touch: string | null = null;
      if (hit?.selId.startsWith('dev:')) {
        const name = hit.selId.slice(4);
        const k = this.infos.get(name)?.kind;
        if (k === 'touch' || k === 'digital') {
          touch = name;
          if (e.shiftKey) this.toggleLatch(name);
          else this.touchPress(name, true);
          // Do not orbit while holding a button down.
          this.vp.orbit.enabled = false;
        }
      }
      this.pointerStart = { x: e.clientX, y: e.clientY, id: hit?.selId ?? null, touch };
    });
    window.addEventListener('pointerup', (e) => {
      const ps = this.pointerStart;
      this.pointerStart = null;
      if (!ps) return;
      if (ps.touch) {
        this.touchPress(ps.touch, false);
        this.vp.orbit.enabled = true;
      }
      if (Math.hypot(e.clientX - ps.x, e.clientY - ps.y) < 5 && !this.vp.gizmoDragging) this.select(ps.id);
    });
    canvas.addEventListener('dblclick', (e) => {
      const hit = this.vp.pick(e.clientX, e.clientY);
      if (!hit) return;
      const obj = this.objectFor(hit.selId);
      this.vp.focusOn(obj ? obj.getWorldPosition(new THREE.Vector3()) : hit.point);
    });
    this.vpEl.addEventListener('keydown', (e) => this.onKey(e, true));
    this.vpEl.addEventListener('keyup', (e) => this.onKey(e, false));
    this.vpEl.addEventListener('blur', () => {
      this.keys.clear();
      this.vp.clearFly();
    });
    this.vpEl.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  private onKey(e: KeyboardEvent, down: boolean): void {
    const tgt = e.target as HTMLElement;
    if (tgt !== this.vpEl) return;
    if (down && e.code === 'Tab') {
      e.preventDefault();
      this.setKeysMode(((this.keysMode + 1) % 3) as 0 | 1 | 2);
      return;
    }
    if (down && e.code === 'Escape') {
      this.select(null);
      return;
    }
    if (this.keysMode === 0) {
      if (FLY_CODES.has(e.code)) {
        this.vp.setFlyKey(e.code, down);
        e.preventDefault();
      } else if (down && e.code === 'KeyG') this.setGizmoMode('translate');
      else if (down && e.code === 'KeyR') this.setGizmoMode('rotate');
    } else if (KEYBOARD_CODES.has(e.code)) {
      if (down) this.keys.add(e.code);
      else this.keys.delete(e.code);
      e.preventDefault();
    }
  }

  private setKeysMode(m: 0 | 1 | 2): void {
    this.keysMode = m;
    this.keys.clear();
    this.vp.clearFly();
    if (m === 0) {
      const k = this.gamepads.keyboardSlot();
      if (k) this.gamepads.setSource(k, 'none');
    } else this.gamepads.setSource(m, 'keyboard');
    this.renderKeysMode();
  }

  private renderKeysMode(): void {
    this.keysBtns.forEach((b, i) => b.classList.toggle('active', i === this.keysMode));
  }

  private setGizmoMode(m: 'translate' | 'rotate'): void {
    this.gizmoMode = m;
    this.vp.setMode(m);
    this.renderGizmoMode();
  }

  private renderGizmoMode(): void {
    this.modeBtns[0].classList.toggle('active', this.gizmoMode === 'translate');
    this.modeBtns[1].classList.toggle('active', this.gizmoMode === 'rotate');
  }

  private objectFor(selId: string | null): THREE.Object3D | null {
    if (!selId) return null;
    const [k, ...rest] = selId.split(':');
    const id = rest.join(':');
    if (k === 'dev') return this.views.get(id)?.root ?? null;
    if (k === 'hub') return this.hubViews.get(id)?.root ?? null;
    if (k === 'obs') return this.obstacleViews[parseInt(id, 10)]?.root ?? null;
    return null;
  }

  private select(id: string | null): void {
    if (id && !this.objectFor(id)) id = null;
    this.selected = id;
    this.vp.select(this.objectFor(id), this.gizmoMode);
    this.inspector.show(id);
    // Make sure the inspector is visible when something gets selected.
    const sec = this.root.querySelector('.side-sec[data-id="inspector"]');
    if (id && sec?.classList.contains('collapsed')) sec.classList.remove('collapsed');
  }

  private onGizmoChange(): void {
    const obj = this.vp.gizmo.object;
    if (!obj || !this.selected) return;
    const pos: Vec3 = [r4(obj.position.x), r4(obj.position.y), r4(obj.position.z)];
    const rot: Vec3 = [r4(obj.rotation.x * DEG), r4(obj.rotation.y * DEG), r4(obj.rotation.z * DEG)];
    const [k, ...rest] = this.selected.split(':');
    const id = rest.join(':');
    let target: { position?: Vec3; rotation?: Vec3 } | undefined;
    if (k === 'dev') target = this.layout.devices![id] ?? (this.layout.devices![id] = {});
    else if (k === 'hub') target = this.layout.hubs![id] ?? (this.layout.hubs![id] = {});
    else if (k === 'obs') target = this.layout.obstacles![parseInt(id, 10)];
    if (!target) return;
    target.position = pos;
    target.rotation = rot;
    this.inspector.refreshPose(target);
    this.postLayoutSoon();
  }

  // ---------------- layout ----------------

  private postLayoutSoon(): void {
    window.clearTimeout(this.layoutTimer);
    this.layoutTimer = window.setTimeout(() => this.host.post({ type: 'layoutChanged', layout: this.layout }), 300);
  }

  private saveCameraSoon(): void {
    window.clearTimeout(this.cameraTimer);
    this.cameraTimer = window.setTimeout(() => {
      const c = this.vp.camera.position;
      const t = this.vp.orbit.target;
      this.layout.camera = { ...(this.layout.camera ?? {}), position: [r4(c.x), r4(c.y), r4(c.z)], target: [r4(t.x), r4(t.y), r4(t.z)] };
      this.postLayoutSoon();
    }, 1500);
  }

  private edited(o: { device?: string; hub?: string; obstacles?: boolean; rebuild?: boolean }): void {
    if (o.device) this.views.get(o.device)?.rebuild(this.layout.devices![o.device]);
    if (o.hub) {
      const hv = this.hubViews.get(o.hub);
      const hl = this.layout.hubs![o.hub];
      if (hv && hl) applyPose(hv.root, hl.position, hl.rotation);
    }
    if (o.obstacles) {
      this.buildObstacles();
      if (this.selected?.startsWith('obs:')) this.vp.select(this.objectFor(this.selected), this.gizmoMode);
      else if (!this.selected) this.inspector.show(null);
    }
    this.postLayoutSoon();
  }

  private rebuildScene(): void {
    for (const v of this.views.values()) {
      v.root.removeFromParent();
      v.label.removeFromParent();
    }
    for (const hv of this.hubViews.values()) {
      hv.root.removeFromParent();
      hv.label.removeFromParent();
    }
    this.views.clear();
    this.hubViews.clear();
    this.infos.clear();
    const r = this.ready;
    if (!r) return;
    for (const d of r.devices) this.infos.set(d.name, d);
    const hubNames = new Set(r.hubs.map((x) => x.name));
    if (autoLayout(r, this.layout)) this.postLayoutSoon();
    for (const hub of r.hubs) {
      const hv = new HubView(hub.name, hub.kind === 'ControlHub');
      const hl = this.layout.hubs![hub.name];
      applyPose(hv.root, hl?.position, hl?.rotation);
      this.vp.world.add(hv.root);
      this.vp.labelLayer.add(hv.label);
      this.hubViews.set(hub.name, hv);
    }
    for (const d of r.devices) {
      if (!hasSceneObject(d, hubNames)) continue;
      const v = new DeviceView(d, this.layout.devices![d.name]);
      this.vp.world.add(v.root);
      this.vp.labelLayer.add(v.label);
      this.views.set(d.name, v);
    }
    this.buildObstacles();
    const cp = this.layout.camera?.position;
    const ct = this.layout.camera?.target;
    if (isVec3(cp) && isVec3(ct)) {
      this.vp.camera.position.set(cp[0], cp[1], cp[2]);
      this.vp.orbit.target.set(ct[0], ct[1], ct[2]);
    } else this.vp.fitAll();
    this.emptyEl.style.display = r.devices.length ? 'none' : '';
    if (!r.devices.length) this.emptyEl.textContent = 'The robot configuration has no devices.';
    this.select(this.selected);
  }

  private buildObstacles(): void {
    for (const o of this.obstacleViews) o.root.removeFromParent();
    this.obstacleViews = (this.layout.obstacles ?? []).map((o, i) => {
      const size = isVec3(o.size) ? o.size : ([0.3, 0.2, 0.05] as Vec3);
      const v = new ObstacleView(i, size, o.color ?? '#3060ff');
      applyPose(v.root, o.position, o.rotation);
      this.vp.world.add(v.root);
      return v;
    });
  }

  // ---------------- messages ----------------

  private onMessage(m: ExtToWebview): void {
    if (!m || typeof m !== 'object') return;
    switch (m.type) {
      case 'hello':
        this.layout = normalizeLayout(m.layout);
        this.rebuildScene();
        break;
      case 'status':
        this.hub.setStatus(m.state, m.message);
        break;
      case 'compileErrors':
        this.hub.setCompileErrors(m.errors ?? []);
        break;
      case 'bridgeGamepad':
        this.gamepads.receiveBridge(m.index, m.gamepadType, m.state, m.deviceName);
        break;
      case 'systemGamepads':
        this.gamepads.setSystemGamepads(m.devices ?? [], m.error);
        break;
      case 'sources':
        this.code.setSources(m.files ?? {});
        break;
      case 'bridgeInfo':
        this.gamepads.setBridgeUrl(m.url);
        break;
      case 'sim':
        this.onSim(m.msg);
        break;
    }
  }

  private onSim(msg: SimMsg): void {
    switch (msg.type) {
      case 'ready':
        this.ready = msg;
        this.rec.clear();
        this.live = null;
        this.liveTelemetry = null;
        this.liveTrace = null;
        this.hub.setFatal(null);
        this.hub.setIssues([], []);
        this.hub.setOpModes(msg.opModes ?? []);
        this.rebuildScene();
        this.lastSensor.clear();
        this.resendInputs();
        this.timeline.goLive();
        break;
      case 'state':
        this.rec.addState(msg);
        this.live = msg;
        this.liveAt = performance.now();
        if (msg.phase !== this.lastPhase) {
          if (msg.phase === 'init') this.resendInputs();
          this.lastPhase = msg.phase;
        }
        break;
      case 'trace':
        this.rec.addTrace(msg);
        this.liveTrace = msg;
        break;
      case 'telemetry':
        this.rec.addTelemetry(msg);
        this.liveTelemetry = msg;
        break;
      case 'exception':
        this.rec.addException(msg);
        this.hub.setIssues(this.rec.exceptions, this.rec.warnings);
        break;
      case 'warning':
        this.rec.addWarning(msg);
        this.hub.setIssues(this.rec.exceptions, this.rec.warnings);
        break;
      case 'log':
        this.rec.addLog(msg, this.live?.t ?? 0);
        if (msg.level === 'error') console.warn('[sim]', msg.message);
        break;
      case 'fatal':
        this.hub.setFatal(msg.message);
        break;
    }
  }

  private sim(cmd: SimCommand): void {
    this.host.post({ type: 'sim', msg: cmd });
  }

  private openSource(l: PyLoc): void {
    this.host.post({ type: 'openSource', file: l.file, line: l.line });
  }

  private setPaused(p: boolean): void {
    this.paused = p;
    this.sim({ type: p ? 'pause' : 'resume' });
    this.hub.setPaused(p);
    this.timeline.setSimPaused(p);
  }

  private setReplay(t: number | null): void {
    this.replayT = t;
    const replay = t !== null;
    this.gamepads.replay = replay;
    this.hub.replay = replay;
    this.vpEl.classList.toggle('replaying', replay);
  }

  private sendGamepad(index: 1 | 2, type: GamepadType, state: GamepadState): void {
    this.sim({ type: 'gamepad', index, gamepadType: type, state });
  }

  // After a (re)start of the sim or a new INIT: sensor overrides and gamepad state go out again.
  private resendInputs(): void {
    this.lastSensor.clear();
    this.gamepads.resendAll();
    for (const [name, dl] of Object.entries(this.layout.devices ?? {})) {
      const ov = dl.sensor?.override;
      if (ov && this.infos.has(name)) this.sendSensor(name, ov, true);
    }
  }

  private sendSensor(name: string, value: SensorValue, force = false): void {
    const key = JSON.stringify(value);
    if (!force && this.lastSensor.get(name) === key) return;
    this.lastSensor.set(name, key);
    this.sim({ type: 'sensor', device: name, value });
  }

  private touchPress(name: string, pressed: boolean): void {
    const kind = this.infos.get(name)?.kind;
    if (pressed) this.touchHeld.add(name);
    else this.touchHeld.delete(name);
    const ov = this.layout.devices?.[name]?.sensor?.override;
    const eff = pressed || Boolean(ov && ('pressed' in ov ? ov.pressed : 'state' in ov ? ov.state : false));
    this.sendSensor(name, kind === 'digital' ? { state: eff } : { pressed: eff });
  }

  private toggleLatch(name: string): void {
    const kind = this.infos.get(name)?.kind;
    const dl = this.layout.devices![name] ?? (this.layout.devices![name] = {});
    const on = !dl.sensor?.override;
    const v: SensorValue = kind === 'digital' ? { state: on } : { pressed: on };
    dl.sensor = { ...(dl.sensor ?? {}), override: on ? v : null };
    this.sendSensor(name, v, true);
    this.postLayoutSoon();
    if (this.selected === 'dev:' + name) this.inspector.show(this.selected);
  }

  private imuState(): ImuState | undefined {
    const devs = this.viewFrame()?.devices;
    if (!devs) return undefined;
    for (const st of Object.values(devs)) if (st.kind === 'imu') return st;
    return undefined;
  }

  private viewFrame(): StateMsg | null {
    if (this.replayT !== null) return this.rec.frameAt(this.replayT);
    return this.live;
  }

  // ---------------- per-frame ----------------

  private frame(): void {
    requestAnimationFrame(() => this.frame());
    const now = performance.now();
    const dt = Math.min(0.1, (now - this.lastFrameTime) / 1000);
    this.lastFrameTime = now;
    try {
      this.gamepads.poll(this.keys, now);
      this.timeline.tick(dt);
      const f = this.viewFrame();
      const telem = this.replayT !== null ? this.rec.telemetryAt(this.replayT) : this.liveTelemetry;
      this.updateScene(f);
      this.updateSensors();
      this.hub.update(f?.t ?? 0, f?.phase ?? 'idle', f?.opMode, f?.loopMs, telem);
      const trace = this.replayT !== null ? this.rec.traceAt(this.replayT) : this.liveTrace;
      this.watch.render(trace?.fields ?? f?.fields ?? null);
      const src = this.ready?.opModes.find((o) => o.name === f?.opMode)?.source;
      this.code.render(trace, f, this.ready, src, now);
      this.gamepads.render(f?.gamepads);
      this.renderOverlays(f);
      if (now - this.lastInspector > 100) {
        this.lastInspector = now;
        this.inspector.refreshLive();
      }
      this.vp.render(dt);
    } catch (e) {
      console.error(e);
    }
  }

  private updateScene(f: StateMsg | null): void {
    const devs: Record<string, DeviceState> = f?.devices ?? {};
    const tmp = new THREE.Vector3();
    const age = this.replayT === null && f ? (performance.now() - this.liveAt) / 1000 : 0;
    for (const [name, v] of this.views) {
      v.update(devs[name], { labels: this.labels, selected: this.selected === v.selId, age });
      v.root.updateMatrixWorld();
      v.root.getWorldPosition(tmp);
      v.label.position.set(tmp.x, tmp.y + 0.05, tmp.z);
    }
    for (const hv of this.hubViews.values()) {
      hv.root.getWorldPosition(tmp);
      hv.label.position.set(tmp.x, tmp.y + 0.03, tmp.z - 0.075);
    }
  }

  // Scene-driven sensors: distance and colour rays against walls and other devices.
  private updateSensors(): void {
    for (const [name, v] of this.views) {
      const kind = v.info.kind;
      if (kind !== 'distance' && kind !== 'color') continue;
      const ov = this.layout.devices?.[name]?.sensor?.override;
      const r = v.rayWorld();
      if (kind === 'distance') {
        if (ov && 'mm' in ov) {
          v.setRayLength(ov.mm === null ? null : ov.mm / 1000);
          this.sceneSensorText.set(name, 'Manual override active.');
          continue;
        }
        const hit = this.vp.castRay(r.origin, r.dir, 2.0, v.root);
        const mm = hit ? Math.round(hit.distance * 1000) : null;
        v.setRayLength(hit ? hit.distance : null);
        this.sceneSensorText.set(name, mm === null ? 'Scene: nothing within 2 m' : `Scene: ${mm} mm to ${hit!.object.userData.selId ?? 'object'}`);
        const last = this.lastSensor.get(name);
        const lastMm = last ? (JSON.parse(last) as { mm: number | null }).mm : undefined;
        if (last === undefined || (mm === null) !== (lastMm === null) || (mm !== null && lastMm !== null && lastMm !== undefined && Math.abs(mm - lastMm) > 1)) {
          this.sendSensor(name, { mm });
        }
      } else {
        if (ov) {
          this.sceneSensorText.set(name, 'Manual override active.');
          continue;
        }
        const hit = this.vp.castRay(r.origin, r.dir, 0.1, v.root);
        let val: SensorValue;
        if (hit) {
          const mat = (hit.object as THREE.Mesh).material as THREE.MeshStandardMaterial;
          const c = hit.object.userData.obstacle && mat?.color ? mat.color : new THREE.Color(0.3, 0.3, 0.3);
          val = { r: r4(c.r), g: r4(c.g), b: r4(c.b), distanceMm: Math.round(hit.distance * 1000) };
          this.sceneSensorText.set(name, `Scene: #${c.getHexString()} at ${Math.round(hit.distance * 1000)} mm`);
        } else {
          val = { r: 0, g: 0, b: 0, distanceMm: null };
          this.sceneSensorText.set(name, 'Scene: nothing within 100 mm');
        }
        this.sendSensor(name, val);
      }
    }
  }

  private renderOverlays(f: StateMsg | null): void {
    if (this.replayT !== null) {
      this.bannerEl.style.display = '';
      const key = this.replayT.toFixed(2);
      if (this.bannerEl.dataset.k !== key) {
        this.bannerEl.dataset.k = key;
        clear(this.bannerEl);
        this.bannerEl.append(
          h('span', null, `REPLAY t=${this.replayT.toFixed(2)} s`),
          h('span', { class: 'small' }, this.paused ? '  (simulation paused)' : '  (simulation still running)'),
          h('button', { onclick: () => this.timeline.goLive() }, 'Back to live'),
        );
      }
    } else this.bannerEl.style.display = 'none';
    const pins = this.watch.pins;
    const parts = pins.map((p) => {
      const v = resolvePath(f?.fields, p);
      return [p, v === undefined ? '-' : formatLeaf(v)] as const;
    });
    const key = JSON.stringify(parts) + parts.map(([p]) => this.watch.changedRecently(p)).join();
    if (this.pinnedEl.dataset.k === key) return;
    this.pinnedEl.dataset.k = key;
    clear(this.pinnedEl);
    this.pinnedEl.style.display = parts.length ? '' : 'none';
    for (const [p, v] of parts) {
      this.pinnedEl.append(
        h('span', { class: 'pin-item' + (this.watch.changedRecently(p) ? ' chg' : '') },
          h('span', { class: 'k' }, pathLabel(p)), ' = ', h('b', null, v),
          h('span', { class: 'x', title: 'Unpin', onclick: () => {
            const i = this.watch.pins.findIndex((q) => pathKey(q) === pathKey(p));
            if (i >= 0) this.watch.pins.splice(i, 1);
            this.host.savePrefs({ pinned: this.watch.pins.map((q) => JSON.stringify(q)) });
            this.watch.render(f?.fields ?? null, true);
          } }, '×'),
        ),
      );
    }
  }
}
