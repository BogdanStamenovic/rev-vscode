// Controller bridge: a plain browser page (served by the extension on 127.0.0.1) that reads
// controllers with the Gamepad API and POSTs their state to /gamepad on its own origin. Used when
// the VS Code webview is not allowed to read gamepads itself.
import type { BridgePost, GamepadState } from './protocol';
import { CONTROLLER_CHOICES, ControllerChoice, fromBrowserPad, guessChoice, listPads, sameGamepad, sdkType } from './gamepadInput';

interface Mapping {
  pad: number | null;
  choice: ControllerChoice;
  auto: boolean;
  last: GamepadState | null;
  lastAt: number;
  sel: HTMLSelectElement;
  typeSel: HTMLSelectElement;
  view: HTMLPreElement;
}

const DEADZONE = 0.05;
const root = document.getElementById('bridge')!;
root.innerHTML = `
  <h1>Controller bridge</h1>
  <div class="dim">Keep this page visible in its own window next to VS Code: browsers stop reading controllers in hidden or background tabs. Press any button on a controller so the browser notices it.</div>
  <div class="card"><span class="status" id="status">Connecting...</span></div>
  <div id="slots"></div>`;
const statusEl = document.getElementById('status')!;
const slotsEl = document.getElementById('slots')!;

function makeSlot(index: 1 | 2): Mapping {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `<b>gamepad${index}</b>`;
  const row = document.createElement('div');
  row.className = 'row';
  const sel = document.createElement('select');
  const typeSel = document.createElement('select');
  for (const [v, l] of CONTROLLER_CHOICES) typeSel.append(new Option(l, v));
  row.append('Controller ', sel, ' Type ', typeSel);
  const view = document.createElement('pre');
  card.append(row, view);
  slotsEl.append(card);
  const m: Mapping = { pad: null, choice: 'PS', auto: true, last: null, lastAt: 0, sel, typeSel, view };
  sel.addEventListener('change', () => {
    m.pad = sel.value === '' ? null : parseInt(sel.value, 10);
    m.auto = false;
    m.last = null;
  });
  typeSel.addEventListener('change', () => {
    m.choice = typeSel.value as ControllerChoice;
    m.last = null;
  });
  return m;
}

const slots: [Mapping, Mapping] = [makeSlot(1), makeSlot(2)];
let padKey = '';
let okCount = 0;
let failCount = 0;

function refreshOptions(): void {
  const pads = listPads();
  const key = pads.map((p) => p.index + p.id).join('|');
  if (key === padKey) return;
  padKey = key;
  for (const s of slots) {
    s.sel.innerHTML = '';
    s.sel.append(new Option('(none)', ''));
    for (const p of pads) s.sel.append(new Option(`#${p.index + 1} ${p.id}`, String(p.index)));
    if (s.auto) {
      const used = new Set(slots.filter((o) => o !== s && o.pad !== null).map((o) => o.pad));
      const free = pads.find((p) => !used.has(p.index));
      s.pad = s.pad !== null && pads.some((p) => p.index === s.pad) ? s.pad : free ? free.index : null;
      const gp = pads.find((p) => p.index === s.pad);
      if (gp) {
        s.choice = guessChoice(gp.id);
        s.typeSel.value = s.choice;
      }
    }
    s.sel.value = s.pad === null ? '' : String(s.pad);
  }
}

async function post(body: BridgePost): Promise<void> {
  try {
    const r = await fetch('/gamepad', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (r.ok) okCount++;
    else failCount++;
  } catch {
    failCount++;
  }
}

function tick(): void {
  refreshOptions();
  const pads = listPads();
  const now = performance.now();
  slots.forEach((s, i) => {
    const gp = pads.find((p) => p.index === s.pad);
    if (!gp) {
      s.view.textContent = s.pad === null ? 'No controller assigned.' : 'Controller disconnected.';
      return;
    }
    const st = fromBrowserPad(gp, DEADZONE);
    const changed = !s.last || !sameGamepad(st, s.last);
    // Send on change (at most 60 per second) and a keepalive every 500 ms.
    if ((changed && now - s.lastAt >= 1000 / 60) || now - s.lastAt >= 500) {
      s.last = st;
      s.lastAt = now;
      void post({ index: (i + 1) as 1 | 2, gamepadType: sdkType(s.choice), state: st });
    }
    const on = Object.entries(st)
      .filter(([, v]) => (typeof v === 'boolean' ? v : Math.abs(v as number) > 0.001))
      .map(([k, v]) => `${k} ${typeof v === 'number' ? v.toFixed(2) : v}`);
    s.view.textContent = on.length ? on.join('\n') : 'nothing pressed';
  });
  const status = failCount > 0 && okCount === 0 ? 'Cannot reach VS Code (is the simulator panel open?)' : `Connected: ${pads.length} controller(s) seen, ${okCount} updates sent`;
  statusEl.textContent = status;
  statusEl.className = 'status ' + (failCount > 0 && okCount === 0 ? 'bad' : 'ok');
}

window.addEventListener('gamepadconnected', () => (padKey = ''));
window.addEventListener('gamepaddisconnected', () => (padKey = ''));
// A timer rather than requestAnimationFrame: rAF stops entirely when the window is not painted.
setInterval(tick, 1000 / 60);
