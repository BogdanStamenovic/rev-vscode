import type { CompileError, ExceptionMsg, OpModeInfo, Phase, PyLoc, TelemetryMsg, WarningMsg } from '../protocol';
import { baseName, clear, h } from '../dom';

export interface DriverHubHooks {
  init(opMode: string): void;
  start(): void;
  stop(): void;
  rebuild(): void;
  debug(): void;
  speed(f: number): void;
  pause(paused: boolean): void;
  openSource(loc: PyLoc): void;
  opModeChosen(name: string): void;
}

export function srcLink(loc: PyLoc | undefined, open: (l: PyLoc) => void): HTMLElement | null {
  if (!loc || !loc.file) return null;
  return h('a', { class: 'src', href: '#', title: loc.file, onclick: (e: Event) => (e.preventDefault(), open(loc)) }, `${baseName(loc.file)}:${loc.line}`);
}

export class DriverHubPanel {
  readonly el: HTMLElement;
  private opSel: HTMLSelectElement;
  private btnInit: HTMLButtonElement;
  private btnStart: HTMLButtonElement;
  private btnStop: HTMLButtonElement;
  private phaseEl: HTMLElement;
  private timeEl: HTMLElement;
  private loopEl: HTMLElement;
  private telemEl: HTMLElement;
  private logEl: HTMLElement;
  private errorsEl: HTMLElement;
  private statusEl: HTMLElement;
  private compileEl: HTMLElement;
  private pauseBtn: HTMLButtonElement;
  private speedSel: HTMLSelectElement;
  private opModes: OpModeInfo[] = [];
  private phase: Phase = 'idle';
  private telemKey = '';
  paused = false;
  replay = false;
  private exceptions: ExceptionMsg[] = [];
  private warnings: WarningMsg[] = [];
  private fatal: string | null = null;

  constructor(private hooks: DriverHubHooks, private preferred: string | undefined) {
    this.opSel = h('select', { class: 'dh-op' });
    this.opSel.addEventListener('change', () => hooks.opModeChosen(this.opSel.value));
    this.btnInit = h('button', { class: 'dh-btn init', onclick: () => this.opSel.value && hooks.init(this.opSel.value) }, 'INIT');
    this.btnStart = h('button', { class: 'dh-btn start', onclick: () => hooks.start() }, '▶ START');
    this.btnStop = h('button', { class: 'dh-btn stop', onclick: () => hooks.stop() }, '■ STOP');
    this.phaseEl = h('span', { class: 'phase idle' }, 'idle');
    this.timeEl = h('span', { class: 'mono' }, 't=0.00 s');
    this.loopEl = h('span', { class: 'mono dim' }, '');
    this.telemEl = h('pre', { class: 'telemetry' });
    this.logEl = h('pre', { class: 'telemetry log' });
    this.errorsEl = h('div', { class: 'errors' });
    this.statusEl = h('div', { class: 'status small' }, 'Waiting for the simulator...');
    this.compileEl = h('div', { class: 'compile-errors' });
    this.pauseBtn = h('button', { onclick: () => hooks.pause(!this.paused) }, 'Pause');
    this.speedSel = h('select', null, ...[0.25, 0.5, 1, 2].map((f) => h('option', { value: f }, `${f}x`)));
    this.speedSel.value = '1';
    this.speedSel.addEventListener('change', () => hooks.speed(parseFloat(this.speedSel.value)));
    this.el = h(
      'div',
      { class: 'driverhub' },
      h('div', { class: 'dh-screen' },
        h('div', { class: 'dh-top' }, this.phaseEl, this.timeEl, this.loopEl),
        h('div', { class: 'dh-row' }, this.opSel),
        h('div', { class: 'dh-row buttons' }, this.btnInit, this.btnStart, this.btnStop),
        h('div', { class: 'dh-label' }, 'Telemetry'),
        this.telemEl,
        this.logEl,
      ),
      this.errorsEl,
      this.compileEl,
      h('div', { class: 'row' }, h('button', { onclick: () => hooks.rebuild(), title: 'Re-translate, recompile and restart the simulator' }, 'Rebuild'),
        h('button', { onclick: () => hooks.debug(), title: 'Attach VS Code\'s debugger: breakpoints in your .py files pause the OpMode and freeze sim time' }, 'Debug'), h('span', { class: 'small dim' }, 'Speed'), this.speedSel, this.pauseBtn),
      this.statusEl,
    );
    this.renderButtons();
  }

  setOpModes(list: OpModeInfo[]): void {
    this.opModes = list;
    const cur = this.opSel.value || this.preferred;
    clear(this.opSel);
    const groups: Array<[string, OpModeInfo[]]> = [
      ['TeleOp', list.filter((o) => o.kind === 'TeleOp')],
      ['Autonomous', list.filter((o) => o.kind === 'Autonomous')],
      ['Other', list.filter((o) => o.kind !== 'TeleOp' && o.kind !== 'Autonomous')],
    ];
    for (const [g, ops] of groups) {
      if (!ops.length) continue;
      this.opSel.append(h('optgroup', { label: g }, ...ops.map((o) => h('option', { value: o.name }, o.group ? `${o.name}  (${o.group})` : o.name))));
    }
    if (cur && list.some((o) => o.name === cur)) this.opSel.value = cur;
    if (!list.length) this.opSel.append(h('option', { value: '' }, 'No OpModes found'));
    this.renderButtons();
  }

  setPaused(p: boolean): void {
    this.paused = p;
    this.pauseBtn.textContent = p ? 'Resume' : 'Pause';
    this.pauseBtn.classList.toggle('active', p);
  }

  setStatus(state: string, message?: string): void {
    this.statusEl.textContent = `Simulator: ${state}${message ? ' - ' + message : ''}`;
    this.statusEl.className = 'status small ' + state;
  }

  setFatal(msg: string | null): void {
    this.fatal = msg;
    this.renderErrors();
  }

  setCompileErrors(errs: CompileError[]): void {
    clear(this.compileEl);
    if (!errs.length) return;
    this.compileEl.append(h('div', { class: 'err-title' }, `Build errors (${errs.length})`));
    for (const e of errs) {
      this.compileEl.append(h('div', { class: 'err' }, srcLink({ file: e.file, line: e.line }, this.hooks.openSource), ' ', e.message));
    }
  }

  setIssues(exceptions: ExceptionMsg[], warnings: WarningMsg[]): void {
    if (exceptions.length === this.exceptions.length && warnings.length === this.warnings.length) return;
    this.exceptions = exceptions.slice();
    this.warnings = warnings.slice();
    this.renderErrors();
  }

  private renderErrors(): void {
    clear(this.errorsEl);
    if (this.fatal) this.errorsEl.append(h('div', { class: 'err fatal' }, h('b', null, 'Simulator stopped: '), this.fatal));
    for (const ex of this.exceptions.slice(-5).reverse()) {
      this.errorsEl.append(
        h('div', { class: 'err exception' },
          h('div', null, h('b', null, ex.exception.split('.').pop() ?? ex.exception), ' ', srcLink(ex.py, this.hooks.openSource), h('span', { class: 'dim small' }, `  t=${ex.t.toFixed(2)} s, ${ex.phase ?? ''}`)),
          h('div', { class: 'msg' }, ex.message),
          ex.driverHub ? h('div', { class: 'dh-text mono small' }, ex.driverHub) : null,
        ),
      );
    }
    for (const w of this.warnings.slice(-8).reverse()) {
      this.errorsEl.append(
        h('div', { class: 'err warning' + (w.code === 'double-write' ? ' double' : '') },
          h('div', null, h('b', null, w.code), ' ', srcLink(w.py, this.hooks.openSource), ...(w.related ?? []).map((r) => [' ', srcLink(r, this.hooks.openSource)]).flat(), h('span', { class: 'dim small' }, `  t=${w.t.toFixed(2)} s`)),
          h('div', { class: 'msg' }, w.message),
        ),
      );
    }
  }

  private renderButtons(): void {
    const p = this.phase;
    const live = !this.replay;
    const has = this.opModes.length > 0;
    this.btnInit.disabled = !(live && has && (p === 'idle' || p === 'stopped' || p === 'crashed'));
    this.btnStart.disabled = !(live && p === 'init');
    this.btnStop.disabled = !(live && (p === 'init' || p === 'running'));
    this.opSel.disabled = !(p === 'idle' || p === 'stopped' || p === 'crashed');
  }

  update(t: number, phase: Phase, opMode: string | null | undefined, loopMs: number | null | undefined, telem: TelemetryMsg | null): void {
    if (phase !== this.phase) {
      this.phase = phase;
      this.phaseEl.textContent = phase + (opMode && phase !== 'idle' ? ` - ${opMode}` : '');
      this.phaseEl.className = 'phase ' + phase;
    }
    this.renderButtons();
    this.timeEl.textContent = `t=${t.toFixed(2)} s`;
    this.loopEl.textContent = loopMs ? `loop ${loopMs.toFixed(1)} ms` : '';
    const key = telem ? telem.lines.join('\n') + '\u0000' + (telem.log ?? []).join('\n') : '';
    if (key !== this.telemKey) {
      this.telemKey = key;
      this.telemEl.textContent = telem ? telem.lines.join('\n') : '';
      this.logEl.textContent = telem?.log?.length ? telem.log.join('\n') : '';
      this.logEl.style.display = telem?.log?.length ? '' : 'none';
    }
  }
}
