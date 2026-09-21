import type { ExceptionMsg, LogMsg, SimEvent, StateMsg, TelemetryMsg, TraceMsg, WarningMsg } from './protocol';

export interface RecordedEvent extends SimEvent {
  // Set when the same device/op was written more than once within one state frame.
  flicker?: 'flicker' | 'multi';
  flickerNote?: string;
}

export type MarkerKind = 'event' | 'warning' | 'exception' | 'phase' | 'field' | 'log';

export interface Marker {
  t: number;
  kind: MarkerKind;
  dev?: string;
  label?: string;
}

// 10 minutes at 30 frames per second is the floor the UI promises; keep a bit more.
const MAX_FRAMES = 20000;
const MAX_EVENTS = 200000;

function lowerBound<T>(arr: T[], start: number, t: number, key: (x: T) => number): number {
  let lo = start;
  let hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (key(arr[mid]) < t) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function sameValue(a: unknown, b: unknown): boolean {
  return a === b || JSON.stringify(a) === JSON.stringify(b);
}

export class Recorder {
  private frames: StateMsg[] = [];
  private frameStart = 0;
  readonly events: RecordedEvent[] = [];
  readonly telemetry: TelemetryMsg[] = [];
  readonly warnings: WarningMsg[] = [];
  readonly exceptions: ExceptionMsg[] = [];
  readonly logs: LogMsg[] = [];
  readonly markers: Marker[] = [];
  readonly traces: TraceMsg[] = [];
  private lastValue = new Map<string, unknown>();
  private lastPhaseFields = new Map<string, unknown>();
  version = 0;

  clear(): void {
    this.frames = [];
    this.frameStart = 0;
    this.events.length = 0;
    this.telemetry.length = 0;
    this.warnings.length = 0;
    this.exceptions.length = 0;
    this.logs.length = 0;
    this.markers.length = 0;
    this.traces.length = 0;
    this.lastValue.clear();
    this.lastPhaseFields.clear();
    this.version++;
  }

  get count(): number {
    return this.frames.length - this.frameStart;
  }

  get startT(): number {
    return this.count ? this.frames[this.frameStart].t : 0;
  }

  get endT(): number {
    return this.count ? this.frames[this.frames.length - 1].t : 0;
  }

  get latest(): StateMsg | null {
    return this.count ? this.frames[this.frames.length - 1] : null;
  }

  addState(s: StateMsg): void {
    const last = this.latest;
    // The sim restarted (rebuild): sim time went backwards.
    if (last && s.t + 0.5 < last.t) this.clear();
    this.frames.push(s);
    if (this.count > MAX_FRAMES) {
      this.frameStart += 1000;
      if (this.frameStart > 5000) {
        this.frames = this.frames.slice(this.frameStart);
        this.frameStart = 0;
      }
      this.trimTo(this.startT);
    }
    if (s.events && s.events.length) this.addEvents(s.events);
    this.scanPhaseFields(s);
    this.version++;
  }

  private addEvents(evs: SimEvent[]): void {
    const groups = new Map<string, RecordedEvent[]>();
    for (const e of evs) {
      const re: RecordedEvent = { ...e };
      if (e.op === 'phase' && e.dev === 'opmode') {
        this.markers.push({ t: e.t, kind: 'phase', label: String(e.v) });
      } else if (e.op !== 'input') {
        this.markers.push({ t: e.t, kind: 'event', dev: e.dev });
        const key = e.dev + '.' + e.op;
        let g = groups.get(key);
        if (!g) groups.set(key, (g = []));
        g.push(re);
      }
      this.events.push(re);
    }
    for (const [key, g] of groups) {
      if (g.length >= 2) {
        const before = this.lastValue.get(key);
        const lastV = g[g.length - 1].v;
        const flick = before !== undefined && sameValue(before, lastV);
        for (const e of g) {
          e.flicker = flick ? 'flicker' : 'multi';
          e.flickerNote = flick
            ? `${key} changed and changed back within one frame (${g.length} writes)`
            : `${key} written ${g.length} times within one frame`;
        }
      }
      this.lastValue.set(key, g[g.length - 1].v);
    }
    if (this.events.length > MAX_EVENTS) this.events.splice(0, this.events.length - MAX_EVENTS);
  }

  // Flags on the timeline whenever a field called "phase" (or "state") changes anywhere in the tree.
  private scanPhaseFields(s: StateMsg): void {
    if (!s.fields) return;
    const visit = (v: unknown, path: string, depth: number): void => {
      if (depth > 5 || v === null || typeof v !== 'object') return;
      if (Array.isArray(v)) return;
      for (const [k, child] of Object.entries(v as Record<string, unknown>)) {
        const p = k === '@entries' ? path : path ? path + '.' + k : k;
        if ((k === 'phase' || k === 'state') && (typeof child === 'number' || typeof child === 'string')) {
          const prev = this.lastPhaseFields.get(p);
          if (prev !== undefined && prev !== child) {
            this.markers.push({ t: s.t, kind: 'field', label: `${p}=${child}` });
          }
          this.lastPhaseFields.set(p, child);
        } else if (child && typeof child === 'object') {
          visit(child, p, depth + 1);
        }
      }
    };
    visit(s.fields, '', 0);
  }

  addTelemetry(m: TelemetryMsg): void {
    this.telemetry.push(m);
    if (this.telemetry.length > 20000) this.telemetry.splice(0, 5000);
    this.version++;
  }

  addTrace(m: TraceMsg): void {
    this.traces.push(m);
    if (this.traces.length > 20000) this.traces.splice(0, 5000);
  }

  traceAt(t: number): TraceMsg | null {
    const i = lowerBound(this.traces, 0, t + 1e-9, (m) => m.t);
    return i > 0 ? this.traces[i - 1] : null;
  }

  addWarning(m: WarningMsg): void {
    this.warnings.push(m);
    this.markers.push({ t: m.t, kind: 'warning', dev: m.device, label: m.code });
    this.version++;
  }

  addException(m: ExceptionMsg): void {
    this.exceptions.push(m);
    this.markers.push({ t: m.t, kind: 'exception', label: m.exception.split('.').pop() });
    this.version++;
  }

  addLog(m: LogMsg, fallbackT: number): void {
    const withT = { ...m, t: m.t ?? fallbackT };
    this.logs.push(withT);
    if (m.level !== 'info') this.markers.push({ t: withT.t, kind: 'log', label: m.level });
    this.version++;
  }

  frameAt(t: number): StateMsg | null {
    if (!this.count) return null;
    const i = lowerBound(this.frames, this.frameStart, t, (f) => f.t);
    if (i >= this.frames.length) return this.frames[this.frames.length - 1];
    if (i === this.frameStart) return this.frames[i];
    const a = this.frames[i - 1];
    const b = this.frames[i];
    return t - a.t <= b.t - t ? a : b;
  }

  telemetryAt(t: number): TelemetryMsg | null {
    const i = lowerBound(this.telemetry, 0, t + 1e-9, (m) => m.t);
    return i > 0 ? this.telemetry[i - 1] : null;
  }

  eventsBetween(t0: number, t1: number): RecordedEvent[] {
    const i = lowerBound(this.events, 0, t0, (e) => e.t);
    const out: RecordedEvent[] = [];
    for (let k = i; k < this.events.length && this.events[k].t <= t1; k++) out.push(this.events[k]);
    return out;
  }

  private trimTo(t0: number): void {
    const cut = (arr: Array<{ t?: number }>): void => {
      let n = 0;
      while (n < arr.length && (arr[n].t ?? 0) < t0) n++;
      if (n) arr.splice(0, n);
    };
    cut(this.events);
    cut(this.markers);
    cut(this.telemetry);
    cut(this.traces);
  }
}
