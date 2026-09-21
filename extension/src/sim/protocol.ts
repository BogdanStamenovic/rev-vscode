// Contract 5 (docs/ARCHITECTURE.md) on the extension side: framing of the sim
// process's NDJSON stream and the mapping from sim events to Python-line
// problems. No vscode import, so it is unit tested under plain node.

export interface PyLoc {
  file: string;
  line: number;
  approximate?: boolean;
}

export type SimMessage = { type: string; [k: string]: unknown };

/** Splits a byte stream into complete lines; keeps a partial last line for the next chunk. */
export class LineSplitter {
  private buf = '';

  push(chunk: string): string[] {
    this.buf += chunk;
    const parts = this.buf.split('\n');
    this.buf = parts.pop() ?? '';
    return parts.filter((p) => p.trim().length > 0);
  }
}

export function parseLine(line: string): SimMessage | undefined {
  try {
    const o = JSON.parse(line);
    return o && typeof o === 'object' && typeof o.type === 'string' ? (o as SimMessage) : undefined;
  } catch {
    return undefined;
  }
}

export interface SimProblem {
  file: string;
  line: number; // 1-based
  severity: 'error' | 'warning';
  message: string;
  code: string;
}

/** A Python-line problem for an `exception` or `warning` event, or undefined when it has no Python location. */
export function problemFor(msg: SimMessage): SimProblem | undefined {
  const py = msg.py as PyLoc | undefined;
  if (!py || typeof py.file !== 'string' || typeof py.line !== 'number') return undefined;
  if (msg.type === 'exception') {
    const cls = String(msg.exception ?? 'Exception');
    const simple = cls.slice(cls.lastIndexOf('.') + 1);
    const hint = typeof msg.hint === 'string' && msg.hint ? `\n${msg.hint}` : '';
    const where = typeof msg.phase === 'string' ? ` (during ${msg.phase})` : '';
    return {
      file: py.file,
      line: py.line,
      severity: 'error',
      message: `Simulator: ${simple}: ${String(msg.message ?? '')}${where}${hint}`,
      code: 'sim-exception',
    };
  }
  if (msg.type === 'warning') {
    return {
      file: py.file,
      line: py.line,
      severity: 'warning',
      message: `Simulator: ${String(msg.message ?? '')}`,
      code: `sim-${String(msg.code ?? 'warning')}`,
    };
  }
  return undefined;
}

export interface TraceView {
  /** Python file -> lines that ran in the last complete loop iteration. */
  lines: Map<string, number[]>;
  /** Python file -> line -> "name = value" texts assigned on that line. */
  values: Map<string, Map<number, string>>;
}

function short(v: unknown): string {
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
  if (typeof v === 'string') return JSON.stringify(v);
  if (v === null || v === undefined) return 'None';
  if (typeof v === 'boolean') return v ? 'True' : 'False';
  const s = JSON.stringify(v);
  return s.length > 40 ? s.slice(0, 37) + '…' : s;
}

/** What to draw in the editors for a `trace` event. */
export function traceView(msg: SimMessage): TraceView {
  const lines = new Map<string, number[]>();
  const raw = (msg.lines ?? {}) as Record<string, number[]>;
  for (const [file, ls] of Object.entries(raw)) lines.set(file, ls);
  const values = new Map<string, Map<number, string>>();
  for (const c of (msg.changed ?? []) as Array<{ name: string; value: unknown; file?: string; line: number }>) {
    if (!c.file) continue;
    const perFile = values.get(c.file) ?? new Map<number, string>();
    perFile.set(c.line, `${c.name} = ${short(c.value)}`);
    values.set(c.file, perFile);
  }
  return { lines, values };
}
