import '../styles.css';
import { App } from '../app';
import { FakeSim } from './fakeSim';
import type { ExtToWebview, WebviewToExt } from '../protocol';

const DARK: Record<string, string> = {
  '--vscode-editor-background': '#1e1e1e',
  '--vscode-foreground': '#cccccc',
  '--vscode-descriptionForeground': '#9d9d9d',
  '--vscode-panel-border': '#3c3c3c',
  '--vscode-sideBar-background': '#252526',
  '--vscode-sideBarSectionHeader-background': '#2d2d30',
  '--vscode-button-background': '#0e639c',
  '--vscode-button-foreground': '#ffffff',
  '--vscode-button-hoverBackground': '#1177bb',
  '--vscode-button-secondaryBackground': '#3a3d41',
  '--vscode-button-secondaryForeground': '#ffffff',
  '--vscode-input-background': '#3c3c3c',
  '--vscode-input-foreground': '#cccccc',
  '--vscode-input-border': '#3c3c3c',
  '--vscode-textLink-foreground': '#3794ff',
  '--vscode-font-family': 'system-ui, -apple-system, "Segoe UI", sans-serif',
  '--vscode-editor-font-family': '"DejaVu Sans Mono", monospace',
  '--vscode-font-size': '13px',
};
const LIGHT: Record<string, string> = {
  ...DARK,
  '--vscode-editor-background': '#ffffff',
  '--vscode-foreground': '#3b3b3b',
  '--vscode-descriptionForeground': '#717171',
  '--vscode-panel-border': '#d4d4d4',
  '--vscode-sideBar-background': '#f3f3f3',
  '--vscode-sideBarSectionHeader-background': '#e7e7e7',
  '--vscode-button-background': '#005fb8',
  '--vscode-button-secondaryBackground': '#e5e5e5',
  '--vscode-button-secondaryForeground': '#3b3b3b',
  '--vscode-input-background': '#ffffff',
  '--vscode-input-foreground': '#3b3b3b',
  '--vscode-input-border': '#cecece',
  '--vscode-textLink-foreground': '#005fb8',
};

function setTheme(light: boolean): void {
  document.body.classList.toggle('vscode-light', light);
  document.body.classList.toggle('vscode-dark', !light);
  const vars = light ? LIGHT : DARK;
  for (const [k, v] of Object.entries(vars)) document.documentElement.style.setProperty(k, v);
}

const params = new URLSearchParams(location.search);
setTheme(params.get('theme') === 'light');

const deliver = (m: ExtToWebview): void => window.postMessage(m, '*');
const sim = new FakeSim(deliver);
const posted: WebviewToExt[] = [];
window.acquireVsCodeApi = () => ({
  postMessage: (m: unknown) => {
    posted.push(m as WebviewToExt);
    setTimeout(() => sim.handle(m as WebviewToExt), 0);
  },
  getState: () => {
    try {
      return JSON.parse(localStorage.getItem('harness-ui') ?? 'null');
    } catch {
      return null;
    }
  },
  setState: (s: unknown) => {
    try {
      localStorage.setItem('harness-ui', JSON.stringify(s));
    } catch {
      /* ignore */
    }
  },
});

// Small control strip for the harness itself (not part of the real panel).
const bar = document.getElementById('harness-bar')!;
const btn = (label: string, fn: () => void): HTMLButtonElement => {
  const b = document.createElement('button');
  b.textContent = label;
  b.addEventListener('click', fn);
  bar.append(b);
  return b;
};
bar.append('Harness: ');
btn('Toggle theme', () => setTheme(!document.body.classList.contains('vscode-light')));
btn('Auto-drive on/off', () => (sim.autoDrive = !sim.autoDrive));
btn('Throw exception', () => sim.throwException());
btn('Compile error', () => deliver({ type: 'compileErrors', errors: [{ file: '/home/team/robot/main.py', line: 12, message: "NameError: name 'hardwareMpa' is not defined" }] }));
let sys = false;
btn('System controller', () => {
  sys = !sys;
  sim.simulateSystemController(sys);
});
btn('Reset layout', () => {
  localStorage.removeItem('harness-layout');
  location.reload();
});

(window as unknown as { harness: unknown }).harness = { sim, posted, deliver, setTheme };
(window as unknown as { app: unknown }).app = new App(document.getElementById('app')!);
