import type { DeviceInfo, DeviceState, PyLoc, ReadyMsg, StateMsg, TraceMsg } from '../protocol';
import { baseName, clear, h } from '../dom';
import { formatLeaf } from './watch';

export interface CodeHooks {
  openSource(loc: PyLoc): void;
  selectDevice(name: string): void;
}

const SEP = '␟';

// Where each device is held in the OpMode: paths of {"@device": name} entries in fields / locals.
function devicePaths(root: unknown, prefix: string, out: Map<string, string[]>, depth = 0): void {
  if (!root || typeof root !== 'object' || depth > 5) return;
  if (Array.isArray(root)) {
    root.forEach((v, i) => devicePaths(v, `${prefix}[${i}]`, out, depth + 1));
    return;
  }
  const o = root as Record<string, unknown>;
  if (typeof o['@device'] === 'string') {
    const name = o['@device'];
    const list = out.get(name) ?? [];
    if (!list.includes(prefix)) list.push(prefix);
    out.set(name, list);
    return;
  }
  const src = o['@entries'] && typeof o['@entries'] === 'object' ? (o['@entries'] as Record<string, unknown>) : o;
  for (const [k, v] of Object.entries(src)) {
    if (k === '@type') continue;
    devicePaths(v, prefix ? `${prefix}.${k}` : k, out, depth + 1);
  }
}

export class CodePanel {
  readonly el: HTMLElement;
  private files = new Map<string, string[]>();
  private current: string | null = null;
  private userPicked = false;
  private fileSel: HTMLSelectElement;
  private codeEl: HTMLElement;
  private rows: HTMLElement[] = [];
  private notes: HTMLElement[] = [];
  private hitKey = '';
  private noteKey = '';
  private localsEl: HTMLElement;
  private devicesEl: HTMLElement;
  private iterEl: HTMLElement;
  private followChk: HTMLInputElement;
  private prevLocals = new Map<string, string>();
  private localChanged = new Map<string, number>();
  private localsKey = '';
  private devKey = '';
  private lastDevRender = 0;

  constructor(private hooks: CodeHooks, watchEl: HTMLElement) {
    this.fileSel = h('select', { class: 'code-file' });
    this.fileSel.addEventListener('change', () => {
      this.userPicked = true;
      this.show(this.fileSel.value);
    });
    this.followChk = h('input', { type: 'checkbox', checked: true });
    this.iterEl = h('span', { class: 'dim small mono' });
    this.codeEl = h('div', { class: 'code-view mono' }, h('div', { class: 'dim' }, 'The Python source appears here after a build.'));
    this.codeEl.addEventListener('click', (e) => {
      const row = (e.target as HTMLElement).closest('[data-line]') as HTMLElement | null;
      if (row && this.current) this.hooks.openSource({ file: this.current, line: parseInt(row.dataset.line!, 10) });
    });
    this.localsEl = h('div', { class: 'code-locals mono' });
    this.devicesEl = h('div', { class: 'code-devices' });
    this.el = h(
      'div',
      { class: 'code-panel' },
      h('div', { class: 'row' }, this.fileSel, h('label', { class: 'small', title: 'Scroll to the lines that ran' }, this.followChk, ' follow'), this.iterEl),
      h('div', { class: 'small dim' }, 'Highlighted: lines that ran in the last loop iteration. Click a line to open it in the editor.'),
      this.codeEl,
      h('div', { class: 'code-sub' }, 'Local variables'),
      this.localsEl,
      h('div', { class: 'code-sub' }, 'OpMode fields'),
      watchEl,
      h('div', { class: 'code-sub' }, 'Devices'),
      this.devicesEl,
    );
  }

  setSources(files: Record<string, string>): void {
    this.files.clear();
    for (const [f, text] of Object.entries(files)) this.files.set(f, text.split(/\r?\n/));
    clear(this.fileSel);
    for (const f of this.files.keys()) this.fileSel.append(h('option', { value: f, title: f }, baseName(f)));
    const first = this.files.keys().next();
    const keep = this.current && this.files.has(this.current) ? this.current : first.done ? null : first.value;
    this.current = null;
    if (keep) this.show(keep);
  }

  private show(file: string): void {
    if (file === this.current) return;
    this.current = file;
    this.fileSel.value = file;
    this.hitKey = '';
    this.noteKey = '';
    clear(this.codeEl);
    this.rows = [];
    this.notes = [];
    const lines = this.files.get(file) ?? [];
    const frag = document.createDocumentFragment();
    lines.forEach((text, i) => {
      const note = h('span', { class: 'note' });
      const row = h('div', { class: 'cl', 'data-line': i + 1 }, h('span', { class: 'ln' }, String(i + 1)), h('span', { class: 'tx' }, text || ' '), note);
      this.rows.push(row);
      this.notes.push(note);
      frag.append(row);
    });
    this.codeEl.append(frag);
  }

  render(trace: TraceMsg | null, state: StateMsg | null, ready: ReadyMsg | null, preferredFile: string | undefined, now: number): void {
    const lines = trace?.lines ?? {};
    // Follow the file that is actually running, unless the user picked one.
    if (!this.userPicked) {
      const running = Object.keys(lines).find((f) => this.files.has(f) && lines[f].length);
      const want = running ?? (preferredFile && this.files.has(preferredFile) ? preferredFile : null);
      if (want && want !== this.current) this.show(want);
    }
    const iter = trace ? `iteration ${trace.iteration}  t=${trace.t.toFixed(2)} s` : '';
    if (this.iterEl.textContent !== iter) this.iterEl.textContent = iter;
    const hits = (this.current && lines[this.current]) || [];
    const key = hits.join(',');
    if (key !== this.hitKey) {
      this.hitKey = key;
      const set = new Set(hits);
      this.codeEl.classList.toggle('tracing', set.size > 0);
      this.rows.forEach((r, i) => r.classList.toggle('hit', set.has(i + 1)));
      if (hits.length && this.followChk.checked) {
        const first = this.rows[Math.min(...hits) - 1];
        const last = this.rows[Math.max(...hits) - 1];
        if (first && last) this.scrollIntoCode(first, last);
      }
    }
    const changed = (trace?.changed ?? []).filter((c) => c.file === this.current && c.line);
    const nk = JSON.stringify(changed);
    if (nk !== this.noteKey) {
      this.noteKey = nk;
      for (const n of this.notes) {
        if (!n.textContent) continue;
        n.textContent = '';
        n.parentElement?.classList.remove('changed');
      }
      for (const c of changed) {
        const n = this.notes[(c.line ?? 0) - 1];
        if (!n) continue;
        n.textContent = (n.textContent ? n.textContent + ', ' : '  ← ') + `${c.name} = ${formatLeaf(c.value)}`;
        n.parentElement?.classList.add('changed');
      }
    }
    this.renderLocals(trace?.locals ?? {}, now);
    if (now - this.lastDevRender > 200) {
      this.lastDevRender = now;
      this.renderDevices(ready, state, trace);
    }
  }

  private scrollIntoCode(first: HTMLElement, last: HTMLElement): void {
    const c = this.codeEl;
    const top = first.offsetTop;
    const bottom = last.offsetTop + last.offsetHeight;
    if (top >= c.scrollTop && bottom <= c.scrollTop + c.clientHeight) return;
    c.scrollTop = Math.max(0, top - 24);
  }

  private renderLocals(locals: Record<string, Record<string, unknown>>, now: number): void {
    const rows: Array<[string, string, string]> = [];
    for (const [method, vars] of Object.entries(locals)) {
      for (const [name, v] of Object.entries(vars ?? {})) {
        const k = method + SEP + name;
        const s = formatLeaf(v);
        const prev = this.prevLocals.get(k);
        if (prev !== undefined && prev !== s) this.localChanged.set(k, now);
        this.prevLocals.set(k, s);
        rows.push([method, name, s]);
      }
    }
    const flashing = rows.map(([m, n]) => now - (this.localChanged.get(m + SEP + n) ?? -1e9) < 1000);
    const key = JSON.stringify(rows) + flashing.join();
    if (key === this.localsKey) return;
    this.localsKey = key;
    clear(this.localsEl);
    if (!rows.length) {
      this.localsEl.append(h('div', { class: 'dim' }, 'No locals reported yet.'));
      return;
    }
    let lastMethod = '';
    rows.forEach(([m, n, v], i) => {
      if (m !== lastMethod) {
        lastMethod = m;
        this.localsEl.append(h('div', { class: 'lm' }, m));
      }
      this.localsEl.append(h('div', { class: 'lv' }, h('span', { class: 'k' }, n), ' = ', h('span', { class: 'v' + (flashing[i] ? ' chg' : '') }, v)));
    });
  }

  private renderDevices(ready: ReadyMsg | null, state: StateMsg | null, trace: TraceMsg | null): void {
    const devs = (ready?.devices ?? []).filter((d) => d.kind !== 'voltage' && d.kind !== 'imu');
    const paths = new Map<string, string[]>();
    devicePaths(trace?.fields ?? state?.fields, '', paths);
    for (const vars of Object.values(trace?.locals ?? {})) devicePaths(vars, '', paths);
    const rows = devs.map((d) => [d, state?.devices?.[d.name], paths.get(d.name) ?? []] as const);
    const key = JSON.stringify(rows.map(([d, st, p]) => [d.name, st, p]));
    if (key === this.devKey) return;
    this.devKey = key;
    clear(this.devicesEl);
    if (!rows.length) {
      this.devicesEl.append(h('div', { class: 'dim' }, 'No devices yet.'));
      return;
    }
    for (const [d, st, p] of rows) this.devicesEl.append(this.deviceRow(d, st, p));
  }

  private deviceRow(d: DeviceInfo, st: DeviceState | undefined, paths: string[]): HTMLElement {
    const bits: string[] = [];
    if (st && (st.kind === 'motor' || st.kind === 'crservo')) {
      bits.push(st.direction, `power ${st.power.toFixed(2)}`);
      if (st.kind === 'motor') {
        if (st.mode) bits.push(st.mode);
        if (st.zeroPower) bits.push(`zero ${st.zeroPower}`);
        if (st.position !== undefined) bits.push(`enc ${st.position}`);
      }
      bits.push(st.spin === 'stopped' ? 'stopped' : `spins ${st.spin}`);
    } else if (st && st.kind === 'servo') {
      bits.push(st.direction, `position ${st.position.toFixed(2)}`, `${st.angleDeg.toFixed(0)} deg`);
    } else if (st && st.kind !== 'unsupported') {
      for (const [k, v] of Object.entries(st)) if (k !== 'kind') bits.push(`${k} ${formatLeaf(v)}`);
    }
    const spinCls = st && 'spin' in st ? ' ' + st.spin.toLowerCase() : '';
    return h(
      'div',
      { class: 'cd-row' + spinCls },
      h('div', null,
        h('a', { href: '#', class: 'b', onclick: (e: Event) => (e.preventDefault(), this.hooks.selectDevice(d.name)) }, d.name),
        paths.length ? h('span', { class: 'py mono' }, '  ' + paths.join(', ')) : h('span', { class: 'dim small' }, '  (not held in a field)'),
        h('span', { class: 'dim small' }, `  ${d.hub ?? '?'}:${d.port ?? '-'}  ${d.displayName ?? d.tag}`),
      ),
      h('div', { class: 'mono small' }, bits.join('  ')),
    );
  }
}
