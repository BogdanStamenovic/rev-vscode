import { emptyGamepad, GAMEPAD_AXES, GAMEPAD_BUTTONS, GamepadState, GamepadType, SystemGamepad } from '../protocol';
import { h, clear } from '../dom';
import {
  CONTROLLER_CHOICES,
  ControllerChoice,
  KEY_LEGEND,
  choiceFromType,
  fromBrowserPad,
  fromKeys,
  gamepadApiStatus,
  labelsFor,
  listPads,
  sameGamepad,
  sdkNames,
  sdkType,
} from '../gamepadInput';

const SVGNS = 'http://www.w3.org/2000/svg';

function svg<K extends keyof SVGElementTagNameMap>(tag: K, attrs: Record<string, string | number>, text?: string): SVGElementTagNameMap[K] {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
  if (text !== undefined) el.textContent = text;
  return el;
}

type Source = string; // 'none' | 'system' | 'keyboard' | 'bridge' | 'pad:<index>'

interface Overlay {
  buttons: Set<keyof GamepadState>;
  left: [number, number] | null;
  right: [number, number] | null;
  lt: number | null;
  rt: number | null;
}

class Slot {
  choice: ControllerChoice = 'PS';
  source: Source = 'none';
  bridge: GamepadState | null = null;
  bridgeAt = 0;
  bridgeName = '';
  deviceLine!: HTMLElement;
  overlay: Overlay = { buttons: new Set(), left: null, right: null, lt: null, rt: null };
  current: GamepadState = emptyGamepad();
  lastSent: GamepadState | null = null;
  lastSentAt = 0;
  lastSentType: GamepadType | null = null;
  el!: HTMLElement;
  svgEl!: SVGSVGElement;
  codeLine!: HTMLElement;
  sourceSel!: HTMLSelectElement;
  typeSel!: HTMLSelectElement;
  parts = new Map<string, SVGElement>();
  sticks: Record<'left' | 'right', SVGCircleElement> = {} as Record<'left' | 'right', SVGCircleElement>;
  trig: Record<'lt' | 'rt', SVGRectElement> = {} as Record<'lt' | 'rt', SVGRectElement>;
  labels: SVGTextElement[] = [];
  constructor(readonly index: 1 | 2) {}
}

export interface GamepadPanelHooks {
  send(index: 1 | 2, type: GamepadType, state: GamepadState): void;
  openBridge(): void;
  prefsChanged(types: Record<string, string>, sources: Record<string, string>): void;
  keyboardSlotChanged(index: 0 | 1 | 2): void;
}

export class GamepadPanel {
  readonly el: HTMLElement;
  readonly slots: [Slot, Slot] = [new Slot(1), new Slot(2)];
  private apiStatus = gamepadApiStatus();
  private blockedEl: HTMLElement;
  private legendEl: HTMLElement;
  private systemEl: HTMLElement;
  private systemDevices: SystemGamepad[] = [];
  private systemError = '';
  private bridgeUrl = '';
  private padIds = '';
  deadzone = 0.05;
  replay = false;

  constructor(private hooks: GamepadPanelHooks, types: Record<string, string>, sources: Record<string, string>) {
    this.el = h('div', { class: 'gamepads' });
    this.blockedEl = h('div', { class: 'gp-blocked' });
    this.systemEl = h('div', { class: 'gp-system' });
    this.systemEl.style.display = 'none';
    this.legendEl = h('div', { class: 'gp-legend' });
    for (const s of this.slots) {
      const t = types[String(s.index)];
      if (t && CONTROLLER_CHOICES.some((c) => c[0] === t)) s.choice = t as ControllerChoice;
      const src = sources[String(s.index)];
      if (src === 'keyboard' || src === 'bridge' || src === 'none' || src === 'system') s.source = src;
    }
    this.el.append(this.systemEl, this.blockedEl);
    for (const s of this.slots) this.el.append(this.buildSlot(s));
    const dzIn = h('input', { type: 'number', min: 0, max: 0.5, step: 0.01, value: this.deadzone, class: 'narrow' });
    dzIn.addEventListener('change', () => {
      const v = parseFloat(dzIn.value);
      if (Number.isFinite(v)) this.deadzone = Math.max(0, Math.min(0.5, v));
    });
    this.el.append(h('div', { class: 'row small' }, h('label', null, 'Stick deadzone (UI setting, not an SDK value) ', dzIn)));
    this.el.append(this.legendEl);
    this.renderBlocked();
    this.renderLegend();
    window.addEventListener('gamepadconnected', () => this.refreshSources());
    window.addEventListener('gamepaddisconnected', () => this.refreshSources());
  }

  setBridgeUrl(url: string): void {
    this.bridgeUrl = url;
    this.renderBlocked();
  }

  private renderBlocked(): void {
    clear(this.blockedEl);
    if (this.apiStatus.ok) {
      this.blockedEl.style.display = 'none';
      return;
    }
    this.blockedEl.style.display = '';
    this.blockedEl.append(
      h('div', null, 'This VS Code build blocks controllers inside panels. Open the controller bridge in your browser.'),
      h('div', { class: 'dim small' }, `(${this.apiStatus.reason ?? 'Gamepad API unavailable'})`),
      h('button', { onclick: () => this.hooks.openBridge() }, 'Open controller bridge'),
    );
    if (this.bridgeUrl) this.blockedEl.append(h('div', { class: 'small' }, 'Bridge: ', h('code', null, this.bridgeUrl)));
  }

  private renderLegend(): void {
    clear(this.legendEl);
    const kb = this.slots.find((s) => s.source === 'keyboard');
    this.legendEl.style.display = kb ? '' : 'none';
    if (!kb) return;
    this.legendEl.append(
      h('div', { class: 'small b' }, `Keyboard drives gamepad ${kb.index} (click the 3D view first; Tab switches Keys mode)`),
      h('table', { class: 'legend' }, ...KEY_LEGEND.map(([k, v]) => h('tr', null, h('td', null, h('kbd', null, k)), h('td', null, v)))),
    );
  }

  private sourceOptions(): Array<[string, string]> {
    const opts: Array<[string, string]> = [['none', 'None'], ['system', 'Controller (system)']];
    for (const p of listPads()) opts.push([`pad:${p.index}`, `Controller #${p.index + 1} (${p.id.slice(0, 48)})`]);
    opts.push(['keyboard', 'Keyboard'], ['bridge', 'Bridge (browser page)']);
    return opts;
  }

  private refreshSources(): void {
    const ids = listPads().map((p) => p.index + p.id).join('|');
    if (ids === this.padIds) return;
    this.padIds = ids;
    const pads = listPads();
    for (const s of this.slots) {
      const cur = s.source;
      clear(s.sourceSel);
      for (const [v, l] of this.sourceOptions()) s.sourceSel.append(h('option', { value: v }, l));
      // Auto-assign newly connected controllers to free slots.
      if (cur === 'none') {
        const used = new Set(this.slots.map((x) => x.source));
        const free = pads.find((p) => !used.has(`pad:${p.index}`));
        if (free) s.source = `pad:${free.index}`;
      }
      s.sourceSel.value = s.source;
      if (s.sourceSel.value !== s.source) {
        s.source = 'none';
        s.sourceSel.value = 'none';
      }
    }
    this.savePrefs();
  }

  setSource(index: 1 | 2, src: Source): void {
    const s = this.slots[index - 1];
    if (src === 'keyboard') for (const o of this.slots) if (o !== s && o.source === 'keyboard') o.source = 'none';
    s.source = src;
    for (const o of this.slots) o.sourceSel.value = o.source;
    this.renderLegend();
    this.savePrefs();
  }

  private savePrefs(): void {
    const types: Record<string, string> = {};
    const sources: Record<string, string> = {};
    for (const s of this.slots) {
      types[s.index] = s.choice;
      // Browser pads and the system reader are re-detected on every load.
      sources[s.index] = s.source.startsWith('pad:') || s.source === 'system' ? 'none' : s.source;
    }
    this.hooks.prefsChanged(types, sources);
  }

  private buildSlot(s: Slot): HTMLElement {
    s.typeSel = h('select', null, ...CONTROLLER_CHOICES.map(([v, l]) => h('option', { value: v }, l)));
    s.typeSel.value = s.choice;
    s.typeSel.addEventListener('change', () => {
      s.choice = s.typeSel.value as ControllerChoice;
      this.applyLabels(s);
      this.savePrefs();
    });
    s.sourceSel = h('select', null, ...this.sourceOptions().map(([v, l]) => h('option', { value: v }, l)));
    s.sourceSel.value = s.source;
    s.sourceSel.addEventListener('change', () => {
      this.setSource(s.index, s.sourceSel.value);
      this.hooks.keyboardSlotChanged(this.keyboardSlot());
    });
    s.svgEl = this.buildSvg(s);
    s.codeLine = h('div', { class: 'gp-code mono small' });
    s.deviceLine = h('div', { class: 'small dim' });
    s.el = h(
      'div',
      { class: 'gp-slot' },
      h('div', { class: 'gp-head' }, h('b', null, `gamepad${s.index}`), s.typeSel),
      h('div', { class: 'gp-head' }, h('span', { class: 'dim small' }, 'Input'), s.sourceSel),
      s.deviceLine,
      s.svgEl,
      s.codeLine,
    );
    this.applyLabels(s);
    return s.el;
  }

  keyboardSlot(): 0 | 1 | 2 {
    const k = this.slots.find((s) => s.source === 'keyboard');
    return k ? k.index : 0;
  }

  private buildSvg(s: Slot): SVGSVGElement {
    const root = svg('svg', { viewBox: '0 0 300 170', class: 'gp-svg' });
    root.append(
      svg('path', {
        d: 'M60 40 Q150 22 240 40 Q285 50 292 120 Q296 160 262 160 Q238 160 222 128 L78 128 Q62 160 38 160 Q4 160 8 120 Q15 50 60 40 Z',
        class: 'gp-body',
      }),
    );
    const part = (key: string, el: SVGElement): SVGElement => {
      el.dataset.part = key;
      el.classList.add('gp-part');
      s.parts.set(key, el);
      root.append(el);
      return el;
    };
    // Triggers (fill bars) and bumpers.
    const trig = (key: 'lt' | 'rt', x: number): void => {
      const bg = svg('rect', { x, y: 2, width: 44, height: 12, rx: 3, class: 'gp-trig-bg' });
      bg.dataset.part = key;
      root.append(bg);
      const fill = svg('rect', { x, y: 2, width: 0, height: 12, rx: 3, class: 'gp-trig' });
      fill.dataset.part = key;
      root.append(fill);
      s.trig[key] = fill;
    };
    trig('lt', 36);
    trig('rt', 220);
    part('left_bumper', svg('rect', { x: 36, y: 18, width: 44, height: 12, rx: 4 }));
    part('right_bumper', svg('rect', { x: 220, y: 18, width: 44, height: 12, rx: 4 }));
    // D-pad.
    part('dpad_up', svg('rect', { x: 56, y: 52, width: 14, height: 16, rx: 2 }));
    part('dpad_down', svg('rect', { x: 56, y: 82, width: 14, height: 16, rx: 2 }));
    part('dpad_left', svg('rect', { x: 40, y: 68, width: 16, height: 14, rx: 2 }));
    part('dpad_right', svg('rect', { x: 70, y: 68, width: 16, height: 14, rx: 2 }));
    // Face buttons.
    const face: Array<[keyof GamepadState, number, number]> = [
      ['y', 240, 56],
      ['x', 222, 74],
      ['b', 258, 74],
      ['a', 240, 92],
    ];
    for (const [k, x, y] of face) part(k, svg('circle', { cx: x, cy: y, r: 9 }));
    part('back', svg('rect', { x: 110, y: 52, width: 18, height: 9, rx: 4 }));
    part('start', svg('rect', { x: 172, y: 52, width: 18, height: 9, rx: 4 }));
    part('guide', svg('circle', { cx: 150, cy: 84, r: 7 }));
    part('touchpad', svg('rect', { x: 128, y: 42, width: 44, height: 22, rx: 4 }));
    // Sticks.
    const stick = (side: 'left' | 'right', cx: number, cy: number): void => {
      const ring = svg('circle', { cx, cy, r: 18, class: 'gp-stick-ring' });
      ring.dataset.stick = side;
      root.append(ring);
      part(side === 'left' ? 'left_stick_button' : 'right_stick_button', svg('circle', { cx, cy, r: 5, class: 'gp-stick-btn' }));
      const dot = svg('circle', { cx, cy, r: 8, class: 'gp-stick-dot' });
      dot.dataset.stick = side;
      root.append(dot);
      s.sticks[side] = dot;
    };
    stick('left', 105, 108);
    stick('right', 195, 108);
    // Text labels, set per controller type.
    const lbl = (x: number, y: number, anchor = 'middle'): SVGTextElement => {
      const t = svg('text', { x, y, 'text-anchor': anchor, class: 'gp-lbl' });
      root.append(t);
      s.labels.push(t);
      return t;
    };
    lbl(58, 12); // lt
    lbl(242, 12); // rt
    lbl(58, 27); // lb
    lbl(242, 27); // rb
    lbl(240, 59); // y
    lbl(222, 77); // x
    lbl(258, 77); // b
    lbl(240, 95); // a
    lbl(119, 71); // back
    lbl(181, 71); // start
    lbl(150, 100); // guide
    lbl(150, 38); // touchpad
    this.wireSvg(s, root);
    return root;
  }

  private applyLabels(s: Slot): void {
    const L = labelsFor(s.choice);
    const psSym: Record<string, string> = { Cross: '✕', Circle: '○', Square: '□', Triangle: '△' };
    const face = (t: string): string => (L.ps ? psSym[t] ?? t : t);
    const texts = [L.lt, L.rt, L.lb, L.rb, face(L.y), face(L.x), face(L.b), face(L.a), L.back, L.start, L.guide, L.ps ? 'touchpad' : ''];
    s.labels.forEach((t, i) => (t.textContent = texts[i]));
    const titles: Record<string, string> = { a: L.a, b: L.b, x: L.x, y: L.y, back: L.back, start: L.start, guide: L.guide, left_bumper: L.lb, right_bumper: L.rb };
    for (const [k, el] of s.parts) {
      const tt = el.querySelector('title') ?? el.appendChild(svg('title', {}));
      tt.textContent = titles[k] ?? k;
    }
    const tp = s.parts.get('touchpad');
    if (tp) tp.style.display = L.ps ? '' : 'none';
    s.svgEl.classList.toggle('ps', L.ps);
  }

  // On-screen drawing as a last-resort input: click buttons, drag stick dots, click triggers.
  private wireSvg(s: Slot, root: SVGSVGElement): void {
    let dragging: 'left' | 'right' | null = null;
    const toSvg = (e: PointerEvent): { x: number; y: number } => {
      const r = root.getBoundingClientRect();
      return { x: ((e.clientX - r.left) / r.width) * 300, y: ((e.clientY - r.top) / r.height) * 170 };
    };
    const centre = { left: [105, 108], right: [195, 108] } as const;
    const move = (e: PointerEvent): void => {
      if (!dragging) return;
      const p = toSvg(e);
      const [cx, cy] = centre[dragging];
      let dx = (p.x - cx) / 18;
      let dy = (p.y - cy) / 18;
      const m = Math.hypot(dx, dy);
      if (m > 1) {
        dx /= m;
        dy /= m;
      }
      s.overlay[dragging] = [Math.round(dx * 100) / 100, Math.round(dy * 100) / 100];
    };
    root.addEventListener('pointerdown', (e) => {
      const t = e.target as SVGElement;
      if (this.replay) return;
      root.setPointerCapture(e.pointerId);
      if (t.dataset.stick) {
        dragging = t.dataset.stick as 'left' | 'right';
        move(e);
      } else if (t.dataset.part === 'lt' || t.dataset.part === 'rt') {
        s.overlay[t.dataset.part] = 1;
      } else if (t.dataset.part) {
        s.overlay.buttons.add(t.dataset.part as keyof GamepadState);
      }
      e.preventDefault();
    });
    root.addEventListener('pointermove', move);
    const up = (): void => {
      dragging = null;
      s.overlay = { buttons: new Set(), left: null, right: null, lt: null, rt: null };
    };
    root.addEventListener('pointerup', up);
    root.addEventListener('pointercancel', up);
  }

  setSystemGamepads(devices: SystemGamepad[], error: string | undefined): void {
    this.systemDevices = devices;
    this.systemError = error ?? '';
    // A controller the extension can read directly becomes the default input.
    if (devices.length) for (const s of this.slots) if (s.source === 'none') this.setSource(s.index, 'system');
    this.renderSystem();
  }

  private renderSystem(): void {
    clear(this.systemEl);
    const show = this.systemDevices.length > 0 || Boolean(this.systemError);
    this.systemEl.style.display = show ? '' : 'none';
    if (!show) return;
    this.systemEl.append(h('div', { class: 'small b' }, 'Controllers (system)'));
    if (this.systemError) this.systemEl.append(h('div', { class: 'gp-error' }, this.systemError));
    for (const d of this.systemDevices) {
      this.systemEl.append(
        h('div', { class: 'gp-sysdev' },
          h('span', { class: 'gp-assign' + (d.assigned ? ' on' : '') }, d.assigned ? `gamepad${d.assigned}` : 'unassigned'),
          ' ', h('span', null, d.name),
          d.warning ? h('div', { class: 'gp-warning' }, d.warning) : null,
        ),
      );
    }
    if (this.systemDevices.some((d) => !d.assigned)) {
      this.systemEl.append(h('div', { class: 'small dim' }, 'Like the Driver Station: hold Start and press A to become gamepad1, Start + B for gamepad2.'));
    }
  }

  receiveBridge(index: 1 | 2, type: GamepadType, state: GamepadState, deviceName?: string): void {
    const s = this.slots[index - 1];
    const first = !s.bridge;
    s.bridge = state;
    s.bridgeAt = performance.now();
    s.bridgeName = deviceName ?? '';
    if (s.source === 'system') return;
    if (first && s.source !== 'bridge') {
      s.choice = choiceFromType(type) === 'PS' && s.choice === 'REVPS4' ? 'REVPS4' : choiceFromType(type);
      s.typeSel.value = s.choice;
      this.applyLabels(s);
      this.setSource(index, 'bridge');
    }
  }

  // Reads every source; returns true if anything was sent.
  poll(keys: Set<string>, now: number): void {
    this.refreshSources();
    const pads = listPads();
    for (const s of this.slots) {
      let st: GamepadState = emptyGamepad();
      if (s.source === 'keyboard') st = fromKeys(keys);
      else if (s.source === 'bridge' || s.source === 'system') st = s.bridge ? { ...s.bridge } : emptyGamepad();
      else if (s.source.startsWith('pad:')) {
        const gp = pads.find((p) => `pad:${p.index}` === s.source);
        if (gp) st = fromBrowserPad(gp, this.deadzone);
      }
      const o = s.overlay;
      for (const b of o.buttons) (st as unknown as Record<string, boolean>)[b] = true;
      if (o.left) [st.left_stick_x, st.left_stick_y] = o.left;
      if (o.right) [st.right_stick_x, st.right_stick_y] = o.right;
      if (o.lt !== null) st.left_trigger = o.lt;
      if (o.rt !== null) st.right_trigger = o.rt;
      s.current = st;
      const type = sdkType(s.choice);
      const changed = !s.lastSent || !sameGamepad(st, s.lastSent) || type !== s.lastSentType;
      if (changed && now - s.lastSentAt >= 1000 / 60) {
        s.lastSent = { ...st };
        s.lastSentAt = now;
        s.lastSentType = type;
        this.hooks.send(s.index, type, st);
      }
    }
  }

  resendAll(): void {
    for (const s of this.slots) s.lastSent = null;
  }

  render(recorded: Array<Partial<GamepadState> & { index?: number }> | undefined): void {
    for (const s of this.slots) {
      let st: GamepadState = s.current;
      if (this.replay) {
        const r = recorded?.find((g, i) => (g.index ?? i + 1) === s.index);
        st = { ...emptyGamepad(), ...(r ?? {}) } as GamepadState;
      }
      this.draw(s, st);
    }
  }

  private draw(s: Slot, st: GamepadState): void {
    let dev = '';
    if (s.source === 'system') {
      const d = this.systemDevices.find((x) => x.assigned === s.index);
      dev = d ? `Reading: ${d.name}` : 'No controller claimed yet: hold Start and press ' + (s.index === 1 ? 'A' : 'B') + ' on it.';
    } else if (s.source === 'bridge') dev = s.bridge ? `Bridge input${s.bridgeName ? ': ' + s.bridgeName : ''}` : 'Waiting for the browser bridge page...';
    if (s.deviceLine.textContent !== dev) s.deviceLine.textContent = dev;
    for (const b of GAMEPAD_BUTTONS) s.parts.get(b)?.classList.toggle('on', Boolean(st[b]));
    const place = (side: 'left' | 'right', x: number, y: number, cx: number, cy: number): void => {
      s.sticks[side].setAttribute('cx', String(cx + x * 14));
      s.sticks[side].setAttribute('cy', String(cy + y * 14));
      s.sticks[side].classList.toggle('on', Math.abs(x) > 0.01 || Math.abs(y) > 0.01);
    };
    place('left', st.left_stick_x, st.left_stick_y, 105, 108);
    place('right', st.right_stick_x, st.right_stick_y, 195, 108);
    s.trig.lt.setAttribute('width', String(44 * Math.max(0, Math.min(1, st.left_trigger))));
    s.trig.rt.setAttribute('width', String(44 * Math.max(0, Math.min(1, st.right_trigger))));
    const ps = labelsFor(s.choice).ps;
    const parts: string[] = [];
    for (const a of GAMEPAD_AXES) {
      const v = st[a];
      if (Math.abs(v) > 0.001) parts.push(`gamepad${s.index}.${a} ${v.toFixed(2)}`);
    }
    for (const b of GAMEPAD_BUTTONS) {
      if (!st[b]) continue;
      const [main, ...alias] = sdkNames(b, ps);
      parts.push(`gamepad${s.index}.${main}${alias.length ? ` (= ${alias.join(', ')})` : ''} true`);
    }
    const text = parts.length ? parts.join('\n') : `gamepad${s.index}: nothing pressed`;
    if (s.codeLine.textContent !== text) s.codeLine.textContent = text;
  }
}
