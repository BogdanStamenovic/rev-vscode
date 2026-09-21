import { h } from '../dom';

// Tree view of the OpMode's fields (Contract 5 `fields`): primitives, {"@type"} objects,
// {"@type","@entries"} maps, arrays and {"@device"} references.

function esc(s: string): string {
  return s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
}

export function pathKey(keys: string[]): string {
  return JSON.stringify(keys);
}

export function pathLabel(keys: string[]): string {
  return keys.join('.');
}

function children(v: unknown): Array<[string, unknown]> | null {
  if (Array.isArray(v)) return v.map((x, i) => [String(i), x]);
  if (v && typeof v === 'object') {
    const o = v as Record<string, unknown>;
    if ('@device' in o) return null;
    if ('@entries' in o && o['@entries'] && typeof o['@entries'] === 'object') return Object.entries(o['@entries'] as Record<string, unknown>);
    return Object.entries(o).filter(([k]) => k !== '@type');
  }
  return null;
}

export function resolvePath(root: unknown, keys: string[]): unknown {
  let v = root;
  for (const k of keys) {
    const ch = children(v);
    if (!ch) return undefined;
    const hit = ch.find(([ck]) => ck === k);
    if (!hit) return undefined;
    v = hit[1];
  }
  return v;
}

export function formatLeaf(v: unknown): string {
  if (v === null) return 'null';
  if (typeof v === 'string') return JSON.stringify(v);
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(Math.abs(v) >= 100 ? 1 : 3);
  if (typeof v === 'boolean') return String(v);
  if (v && typeof v === 'object' && '@device' in (v as object)) return `device ${(v as { '@device': string })['@device']}`;
  if (Array.isArray(v)) return `[${v.length}]`;
  if (v && typeof v === 'object') {
    const t = (v as Record<string, unknown>)['@type'];
    return t ? String(t) : '{...}';
  }
  return String(v);
}

export interface WatchHooks {
  selectDevice(name: string): void;
  pinsChanged(pins: string[][]): void;
}

export class WatchPanel {
  readonly el: HTMLElement;
  private tree: HTMLElement;
  private expanded = new Map<string, boolean>();
  private prev = new Map<string, string>();
  private changedAt = new Map<string, number>();
  private lastJson = '';
  private lastRender = 0;
  pins: string[][] = [];
  private fields: unknown = null;

  constructor(private hooks: WatchHooks, pins: string[][]) {
    this.pins = pins;
    this.tree = h('div', { class: 'watch-tree mono' });
    this.el = h('div', { class: 'watch' }, this.tree);
    this.tree.addEventListener('pointerdown', (e) => {
      const t = (e.target as HTMLElement).closest('[data-act]') as HTMLElement | null;
      if (!t) return;
      const keys = JSON.parse(t.dataset.path ?? '[]') as string[];
      const act = t.dataset.act;
      if (act === 'toggle') {
        const k = pathKey(keys);
        this.expanded.set(k, !this.isExpanded(keys));
      } else if (act === 'pin') {
        const k = pathKey(keys);
        const i = this.pins.findIndex((p) => pathKey(p) === k);
        if (i >= 0) this.pins.splice(i, 1);
        else this.pins.push(keys);
        this.hooks.pinsChanged(this.pins);
      } else if (act === 'device') {
        this.hooks.selectDevice(t.dataset.device ?? '');
      }
      this.lastJson = '';
      this.render(this.fields, true);
      e.preventDefault();
    });
  }

  private isExpanded(keys: string[]): boolean {
    const v = this.expanded.get(pathKey(keys));
    return v ?? keys.length <= 1;
  }

  isPinned(keys: string[]): boolean {
    const k = pathKey(keys);
    return this.pins.some((p) => pathKey(p) === k);
  }

  // Track changes on every frame (for the flash), re-render the DOM at most ~8 times a second.
  render(fields: unknown, force = false): void {
    this.fields = fields;
    const now = performance.now();
    const json = JSON.stringify(fields ?? null);
    if (json !== this.lastJson) {
      this.lastJson = json;
      this.scan(fields, []);
    }
    if (!force && now - this.lastRender < 120) return;
    this.lastRender = now;
    if (fields === null || fields === undefined || (typeof fields === 'object' && !Object.keys(fields as object).length)) {
      this.tree.innerHTML = '<div class="dim">No fields yet. They appear once the OpMode is initialised.</div>';
      return;
    }
    const out: string[] = [];
    this.emit(fields, [], out, now);
    this.tree.innerHTML = out.join('');
  }

  private scan(v: unknown, keys: string[]): void {
    const ch = children(v);
    if (!ch) {
      const s = formatLeaf(v);
      const k = pathKey(keys);
      const p = this.prev.get(k);
      if (p !== undefined && p !== s) this.changedAt.set(k, performance.now());
      this.prev.set(k, s);
      return;
    }
    for (const [ck, cv] of ch) this.scan(cv, [...keys, ck]);
  }

  private emit(v: unknown, keys: string[], out: string[], now: number): void {
    const ch = children(v);
    if (!ch) return;
    for (const [k, cv] of ch) {
      const path = [...keys, k];
      const pj = esc(JSON.stringify(path));
      const sub = children(cv);
      const depth = keys.length;
      const pinned = this.isPinned(path);
      const pinBtn = `<span class="pin${pinned ? ' on' : ''}" data-act="pin" data-path="${pj}" title="${pinned ? 'Unpin' : 'Pin to the 3D view'}">${pinned ? 'pinned' : 'pin'}</span>`;
      const indent = `style="padding-left:${depth * 12}px"`;
      if (sub) {
        const open = this.isExpanded(path);
        const type = (cv as Record<string, unknown>)['@type'];
        const summary = Array.isArray(cv) ? `[${cv.length}]` : `${sub.length} ${sub.length === 1 ? 'entry' : 'entries'}`;
        out.push(
          `<div class="w-row" ${indent}><span class="tw" data-act="toggle" data-path="${pj}">${open ? '▾' : '▸'} <span class="k">${esc(k)}</span></span>` +
            ` ${type ? `<span class="t">@${esc(String(type))}</span>` : ''} <span class="dim">${summary}</span>${pinBtn}</div>`,
        );
        if (open) this.emit(cv, path, out, now);
      } else {
        const age = now - (this.changedAt.get(pathKey(path)) ?? -1e9);
        const cls = age < 1000 ? ' chg' : '';
        let val: string;
        if (cv && typeof cv === 'object' && '@device' in (cv as object)) {
          const d = String((cv as Record<string, unknown>)['@device']);
          val = `<span class="devlink" data-act="device" data-device="${esc(d)}" data-path="${pj}">@device ${esc(d)}</span>`;
        } else {
          val = `<span class="v${cls}">${esc(formatLeaf(cv))}</span>`;
        }
        out.push(`<div class="w-row" ${indent}><span class="k">${esc(k)}</span>: ${val}${pinBtn}</div>`);
      }
    }
  }

  changedRecently(keys: string[]): boolean {
    return performance.now() - (this.changedAt.get(pathKey(keys)) ?? -1e9) < 1000;
  }
}
