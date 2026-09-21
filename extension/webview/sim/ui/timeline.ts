import type { PyLoc } from '../protocol';
import type { RecordedEvent, Recorder } from '../recorder';
import { baseName, clear, h } from '../dom';

export interface TimelineHooks {
  scrub(t: number | null): void;
  pauseSim(paused: boolean): void;
  openSource(loc: PyLoc): void;
  kindOf(dev: string): string;
  selectDevice(dev: string): void;
}

const KIND_COLORS: Record<string, string> = {
  motor: '#1f77d0',
  crservo: '#17becf',
  servo: '#9467bd',
  touch: '#8c564b',
  digital: '#8c564b',
  distance: '#7f7f7f',
  color: '#7f7f7f',
  potentiometer: '#7f7f7f',
};

function fmtV(v: unknown): string {
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(2);
  if (typeof v === 'string') return v;
  return JSON.stringify(v);
}

export class TimelinePanel {
  readonly el: HTMLElement;
  private canvas: HTMLCanvasElement;
  private list: HTMLElement;
  private timeEl: HTMLElement;
  private liveBtn: HTMLButtonElement;
  private playBtn: HTMLButtonElement;
  private rateSel: HTMLSelectElement;
  private simPauseBtn: HTMLButtonElement;
  replayT: number | null = null;
  private playing = false;
  private rate = 1;
  private span = 30;
  private viewEnd = 0;
  private dragging = false;
  private listKey = '';
  simPaused = false;

  constructor(private rec: Recorder, private hooks: TimelineHooks) {
    this.canvas = h('canvas', { class: 'tl-canvas' });
    this.list = h('div', { class: 'tl-list mono' });
    this.timeEl = h('span', { class: 'mono tl-time' }, 'live');
    this.liveBtn = h('button', { class: 'live on', onclick: () => this.goLive(), title: 'Follow the live simulation' }, '● Live');
    this.playBtn = h('button', { onclick: () => this.togglePlay(), title: 'Play the recording from the cursor' }, '▶ Play');
    this.rateSel = h('select', { title: 'Playback speed of the recording' }, h('option', { value: '0.25' }, '0.25x'), h('option', { value: '1' }, '1x'));
    this.rateSel.value = '1';
    this.rateSel.addEventListener('change', () => (this.rate = parseFloat(this.rateSel.value)));
    this.simPauseBtn = h('button', { onclick: () => hooks.pauseSim(!this.simPaused), title: 'Freeze or continue the simulation itself' }, 'Pause sim');
    this.el = h(
      'div',
      { class: 'timeline' },
      h('div', { class: 'tl-controls' }, this.liveBtn, this.playBtn, this.rateSel, this.simPauseBtn, this.timeEl, h('span', { class: 'dim small tl-hint' }, 'drag to scrub, wheel to zoom')),
      this.canvas,
      this.list,
    );
    this.wire();
  }

  setSimPaused(p: boolean): void {
    this.simPaused = p;
    this.simPauseBtn.textContent = p ? 'Resume sim' : 'Pause sim';
    this.simPauseBtn.classList.toggle('active', p);
  }

  private wire(): void {
    const tAt = (e: PointerEvent | WheelEvent): number => {
      const r = this.canvas.getBoundingClientRect();
      const f = (e.clientX - r.left) / r.width;
      return this.viewEnd - this.span + f * this.span;
    };
    this.canvas.addEventListener('pointerdown', (e) => {
      if (!this.rec.count) return;
      this.dragging = true;
      this.canvas.setPointerCapture(e.pointerId);
      this.playing = false;
      this.setReplay(tAt(e));
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (this.dragging) this.setReplay(tAt(e));
    });
    const up = (): void => {
      this.dragging = false;
    };
    this.canvas.addEventListener('pointerup', up);
    this.canvas.addEventListener('pointercancel', up);
    this.canvas.addEventListener(
      'wheel',
      (e) => {
        e.preventDefault();
        const t = tAt(e);
        const f = (t - (this.viewEnd - this.span)) / this.span;
        const ns = Math.max(1, Math.min(3600, this.span * (e.deltaY > 0 ? 1.25 : 0.8)));
        this.viewEnd = t + (1 - f) * ns;
        this.span = ns;
      },
      { passive: false },
    );
  }

  private setReplay(t: number): void {
    const clamped = Math.max(this.rec.startT, Math.min(this.rec.endT, t));
    this.replayT = clamped;
    this.hooks.scrub(clamped);
  }

  goLive(): void {
    this.replayT = null;
    this.playing = false;
    this.hooks.scrub(null);
  }

  private togglePlay(): void {
    if (this.playing) {
      this.playing = false;
      return;
    }
    if (this.replayT === null) this.setReplay(Math.max(this.rec.startT, this.rec.endT - 10));
    else if (this.replayT >= this.rec.endT - 1e-3) this.setReplay(this.rec.startT);
    this.playing = true;
  }

  tick(dt: number): void {
    if (this.playing && this.replayT !== null) {
      const t = this.replayT + dt * this.rate;
      if (t >= this.rec.endT) {
        this.setReplay(this.rec.endT);
        this.playing = false;
      } else this.setReplay(t);
    }
    const live = this.replayT === null;
    this.liveBtn.classList.toggle('on', live);
    this.playBtn.textContent = this.playing ? '❚❚ Stop' : '▶ Play';
    const end = this.rec.endT;
    if (live && !this.dragging) this.viewEnd = Math.max(end + this.span * 0.03, this.span * 0.97);
    else if (!live && this.replayT !== null && !this.dragging) {
      if (this.replayT > this.viewEnd || this.replayT < this.viewEnd - this.span) this.viewEnd = this.replayT + this.span / 2;
    }
    this.timeEl.textContent = live ? `live  t=${end.toFixed(2)} s` : `REPLAY t=${this.replayT!.toFixed(2)} s  (live ${end.toFixed(2)} s)`;
    this.timeEl.classList.toggle('replay', !live);
    this.draw();
    this.renderList();
  }

  private draw(): void {
    const c = this.canvas;
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(10, c.clientWidth);
    const hh = Math.max(10, c.clientHeight);
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(hh * dpr)) {
      c.width = Math.round(w * dpr);
      c.height = Math.round(hh * dpr);
    }
    const g = c.getContext('2d')!;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const cs = getComputedStyle(this.el);
    const fg = cs.getPropertyValue('--fg').trim() || '#ccc';
    const dim = cs.getPropertyValue('--dim').trim() || '#888';
    g.clearRect(0, 0, w, hh);
    const t0 = this.viewEnd - this.span;
    const x = (t: number): number => ((t - t0) / this.span) * w;
    // Recorded range.
    if (this.rec.count) {
      g.fillStyle = 'rgba(128,128,128,0.15)';
      g.fillRect(x(this.rec.startT), 14, x(this.rec.endT) - x(this.rec.startT), hh - 14);
    }
    // Axis.
    g.strokeStyle = dim;
    g.fillStyle = dim;
    g.font = '10px sans-serif';
    g.textBaseline = 'top';
    const step = niceStep(this.span / Math.max(1, w / 70));
    g.beginPath();
    for (let t = Math.ceil(t0 / step) * step; t <= this.viewEnd; t += step) {
      const px = Math.round(x(t)) + 0.5;
      g.moveTo(px, 0);
      g.lineTo(px, 4);
      g.fillText(t.toFixed(step < 1 ? 1 : 0) + 's', px + 2, 0);
    }
    g.stroke();
    // Markers: one per pixel column per kind is enough.
    const seen = new Set<string>();
    for (const m of this.rec.markers) {
      if (m.t < t0 || m.t > this.viewEnd) continue;
      const px = Math.round(x(m.t));
      const key = px + m.kind + (m.dev ?? '');
      if (seen.has(key)) continue;
      seen.add(key);
      if (m.kind === 'event') {
        g.fillStyle = KIND_COLORS[this.hooks.kindOf(m.dev ?? '')] ?? dim;
        g.fillRect(px, 30, 1, hh - 38);
      } else if (m.kind === 'warning') {
        g.fillStyle = '#e0b000';
        g.fillRect(px - 1, 16, 3, hh - 16);
        g.beginPath();
        g.moveTo(px - 5, 16);
        g.lineTo(px + 5, 16);
        g.lineTo(px, 24);
        g.fill();
      } else if (m.kind === 'exception' || (m.kind === 'log' && m.label === 'error')) {
        g.fillStyle = '#d62728';
        g.fillRect(px - 1, 16, 3, hh - 16);
        g.fillText(m.label ?? '', px + 3, hh - 12);
      } else if (m.kind === 'phase' || m.kind === 'field') {
        g.strokeStyle = m.kind === 'phase' ? '#2ca02c' : '#cc3fa6';
        g.beginPath();
        g.moveTo(px + 0.5, 14);
        g.lineTo(px + 0.5, hh);
        g.stroke();
        g.fillStyle = m.kind === 'phase' ? '#2ca02c' : '#cc3fa6';
        g.fillRect(px, 14, 6, 6);
        g.fillStyle = fg;
        g.fillText(m.label ?? '', px + 7, m.kind === 'phase' ? 14 : 22);
      }
    }
    // Cursor.
    const cur = this.replayT ?? this.rec.endT;
    const cx = Math.round(x(cur)) + 0.5;
    g.strokeStyle = this.replayT === null ? '#2ca02c' : '#ff6b00';
    g.lineWidth = 2;
    g.beginPath();
    g.moveTo(cx, 0);
    g.lineTo(cx, hh);
    g.stroke();
    g.lineWidth = 1;
  }

  // Events around the cursor, with flicker groups, warnings and exceptions interleaved.
  private renderList(): void {
    const cur = this.replayT ?? this.rec.endT;
    const live = this.replayT === null;
    const evs = this.rec.eventsBetween(live ? -Infinity : cur - 2, live ? Infinity : cur + 0.5).slice(-200);
    const tail = evs.slice(-60);
    const warns = this.rec.warnings.filter((w) => w.t >= cur - 5 && w.t <= cur + 0.5);
    const exs = this.rec.exceptions.filter((x) => x.t >= cur - 5 && x.t <= cur + 0.5);
    const key = `${this.rec.version}|${cur.toFixed(2)}|${tail.length}`;
    if (key === this.listKey) return;
    this.listKey = key;
    clear(this.list);
    type Row = { t: number; el: HTMLElement };
    const rows: Row[] = [];
    for (const e of tail) rows.push({ t: e.t, el: this.eventRow(e, cur) });
    for (const w of warns) {
      rows.push({
        t: w.t,
        el: h('div', { class: 'tl-row warn' + (w.code === 'double-write' ? ' double' : '') }, h('span', { class: 't' }, w.t.toFixed(3)), ` WARNING ${w.code}: ${w.message} `, this.src(w.py)),
      });
    }
    for (const x of exs) {
      rows.push({ t: x.t, el: h('div', { class: 'tl-row exc' }, h('span', { class: 't' }, x.t.toFixed(3)), ` EXCEPTION ${x.exception.split('.').pop()}: ${x.message} `, this.src(x.py)) });
    }
    rows.sort((a, b) => a.t - b.t);
    if (!rows.length) this.list.append(h('div', { class: 'dim' }, 'No events near the cursor.'));
    for (const r of rows) this.list.append(r.el);
    if (this.replayT === null) this.list.scrollTop = this.list.scrollHeight;
    else {
      const near = rows.findIndex((r) => r.t >= cur);
      const el = rows[Math.max(0, near === -1 ? rows.length - 1 : near - 1)]?.el;
      el?.classList.add('cursor');
      el?.scrollIntoView({ block: 'nearest' });
    }
  }

  private eventRow(e: RecordedEvent, cur: number): HTMLElement {
    let text: string;
    if (e.op === 'phase') text = `opmode phase -> ${fmtV(e.v)}`;
    else if (e.op === 'input') text = `${e.dev} ${fmtV(e.v)}`;
    else text = `${e.dev}.${e.op}(${fmtV(e.v)})`;
    const cls = 'tl-row' + (e.flicker ? ' flicker ' + e.flicker : '') + (e.t > cur ? ' future' : '') + (e.op === 'phase' ? ' phase' : '');
    const devEl = h('span', { class: 'ev', onclick: () => e.dev && this.hooks.selectDevice(e.dev) }, text.padEnd(28));
    return h(
      'div',
      { class: cls, title: e.flickerNote ?? '' },
      h('span', { class: 't' }, e.t.toFixed(3)),
      '  ',
      devEl,
      ' ',
      this.src(e.py),
      e.flicker ? h('span', { class: 'flag' }, e.flicker === 'flicker' ? ' flicker: changed and changed back in one frame' : ' written twice in one frame') : null,
    );
  }

  private src(loc: PyLoc | undefined): HTMLElement | string {
    if (!loc) return '';
    return h('a', { href: '#', class: 'src', title: loc.file, onclick: (ev: Event) => (ev.preventDefault(), this.hooks.openSource(loc)) }, `${baseName(loc.file)}:${loc.line}`);
  }
}

function niceStep(raw: number): number {
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  for (const m of [1, 2, 5, 10]) if (m * p >= raw) return m * p;
  return 10 * p;
}
