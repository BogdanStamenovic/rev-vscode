import type { WebviewToExt } from './protocol';

interface VsCodeApi {
  postMessage(msg: unknown): void;
  getState(): unknown;
  setState(state: unknown): void;
}

declare global {
  interface Window {
    acquireVsCodeApi?: () => VsCodeApi;
  }
}

export interface UiPrefs {
  sidebarWidth?: number;
  timelineHeight?: number;
  collapsed?: Record<string, boolean>;
  gamepadTypes?: Record<string, string>;
  gamepadSources?: Record<string, string>;
  labels?: string;
  pinned?: string[];
  deadzone?: number;
  snap?: boolean;
  expanded?: string[];
  opMode?: string;
}

export class Host {
  private api: VsCodeApi;
  private prefs: UiPrefs;
  private saveTimer = 0;

  constructor() {
    // The API may only be acquired once per webview; the dev harness installs a stub.
    this.api = window.acquireVsCodeApi
      ? window.acquireVsCodeApi()
      : { postMessage: (m) => console.log('[post]', m), getState: () => undefined, setState: () => undefined };
    const s = this.api.getState();
    this.prefs = s && typeof s === 'object' ? (s as UiPrefs) : {};
  }

  post(msg: WebviewToExt): void {
    this.api.postMessage(msg);
  }

  get ui(): UiPrefs {
    return this.prefs;
  }

  savePrefs(patch: Partial<UiPrefs>): void {
    Object.assign(this.prefs, patch);
    window.clearTimeout(this.saveTimer);
    this.saveTimer = window.setTimeout(() => this.api.setState(this.prefs), 200);
  }
}
