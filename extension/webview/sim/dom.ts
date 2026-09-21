type Attrs = Record<string, string | number | boolean | null | undefined | EventListener>;
type Child = Node | string | null | undefined | false;

export function h<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  attrs: Attrs | null = null,
  ...children: Array<Child | Child[]>
): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k.startsWith('on') && typeof v === 'function') {
        el.addEventListener(k.slice(2).toLowerCase(), v as EventListener);
      } else if (k === 'class') {
        el.className = String(v);
      } else if (k === 'value' && 'value' in el) {
        (el as unknown as HTMLInputElement).value = String(v);
      } else if (k === 'checked' && 'checked' in el) {
        (el as unknown as HTMLInputElement).checked = Boolean(v);
      } else if (v === true) {
        el.setAttribute(k, '');
      } else {
        el.setAttribute(k, String(v));
      }
    }
  }
  append(el, children);
  return el;
}

function append(el: Element, children: Array<Child | Child[]>): void {
  for (const c of children) {
    if (Array.isArray(c)) append(el, c);
    else if (c === null || c === undefined || c === false) continue;
    else el.append(c);
  }
}

export function clear(el: Element): void {
  while (el.firstChild) el.removeChild(el.firstChild);
}

export function fmt(n: number | null | undefined, digits = 2): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return '-';
  const s = n.toFixed(digits);
  return n >= 0 && !s.startsWith('-') ? ' ' + s : s;
}

export function fmtSigned(n: number, digits = 2): string {
  const s = n.toFixed(digits);
  return s === (-0).toFixed(digits) ? (0).toFixed(digits) : s.startsWith('-') ? s : '+' + s;
}

export function baseName(file: string): string {
  const i = Math.max(file.lastIndexOf('/'), file.lastIndexOf('\\'));
  return i >= 0 ? file.slice(i + 1) : file;
}

export function selectEl(options: Array<[string, string]>, value: string, onChange: (v: string) => void): HTMLSelectElement {
  const s = h('select', null, ...options.map(([v, label]) => h('option', { value: v }, label)));
  s.value = value;
  s.addEventListener('change', () => onChange(s.value));
  return s;
}

export function numberInput(value: number, step: number, onChange: (v: number) => void, attrs: Attrs = {}): HTMLInputElement {
  const i = h('input', { type: 'number', step, ...attrs });
  i.value = String(value);
  i.addEventListener('change', () => {
    const v = parseFloat(i.value);
    if (Number.isFinite(v)) onChange(v);
  });
  return i;
}
