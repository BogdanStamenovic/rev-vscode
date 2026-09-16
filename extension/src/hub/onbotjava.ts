// OnBot Java HTTP client: save/delete/tree/build/log. See ARCHITECTURE.md's
// "Verified hub facts" for the exact endpoint shapes - notably that save
// and delete bodies are application/x-www-form-urlencoded, not JSON, and
// that /java/build/wait must not be used (it returns before the build is
// actually done; poll /java/build/status instead).
import { hubFetch } from './http';
import { parseBuildLog, type BuildLogError } from './buildLog';

export class BuildTimeoutError extends Error {
  constructor(ms: number) {
    super(`Build did not complete within ${ms}ms`);
    this.name = 'BuildTimeoutError';
  }
}

export interface BuildStatus {
  completed: boolean;
  running: boolean;
  successful: boolean;
  startTimestamp: number;
  timestamp: number;
}

async function expectOk(res: Response, what: string): Promise<void> {
  if (!res.ok) {
    throw new Error(`${what} failed: HTTP ${res.status}`);
  }
}

/** hubPath as given by Contract 3, e.g. "/src/org/firstinspires/ftc/teamcode/pyftc/Drive.java". */
export async function saveFile(hubPath: string, source: string): Promise<void> {
  const res = await hubFetch(`/java/file/save?f=${encodeURIComponent(hubPath)}`, {
    method: 'POST',
    body: new URLSearchParams({ data: source }),
  });
  await expectOk(res, `save ${hubPath}`);
}

/** canonicalPaths: no leading slash, no "src/" prefix, e.g.
 * "org/firstinspires/ftc/teamcode/pyftc/Old.java" (as returned by fileTree()). */
export async function deleteFiles(canonicalPaths: string[]): Promise<void> {
  if (canonicalPaths.length === 0) {
    return;
  }
  const body = new URLSearchParams({
    delete: JSON.stringify(canonicalPaths.map((p) => `src/${p}`)),
  });
  const res = await hubFetch('/java/file/delete', { method: 'POST', body });
  await expectOk(res, 'delete files');
}

/** Returns canonical paths (no leading slash, no "src/" prefix) for every
 * file currently on the hub under /src. */
export async function fileTree(): Promise<string[]> {
  const res = await hubFetch('/java/file/tree');
  await expectOk(res, 'file tree');
  const json = (await res.json()) as { src?: string[] };
  const entries = json.src ?? [];
  return entries.map((e) => e.replace(/^\/+/, ''));
}

/** Returns the build start timestamp (opaque number to pass to pollBuildStatus). */
export async function buildStart(): Promise<number> {
  const res = await hubFetch('/java/build/start');
  await expectOk(res, 'build start');
  const text = (await res.text()).trim();
  const ts = Number(text);
  if (!Number.isFinite(ts)) {
    throw new Error(`unexpected /java/build/start response: ${JSON.stringify(text)}`);
  }
  return ts;
}

export async function fetchBuildStatus(): Promise<BuildStatus> {
  const res = await hubFetch('/java/build/status');
  await expectOk(res, 'build status');
  return (await res.json()) as BuildStatus;
}

export async function fetchBuildLog(): Promise<string> {
  const res = await hubFetch('/java/build/log');
  await expectOk(res, 'build log');
  return res.text();
}

/** Polls /java/build/status until completed && startTimestamp == start, per
 * ARCHITECTURE.md ("do not use /java/build/wait; it returns immediately
 * while the build is only PENDING"). */
export async function pollBuildStatus(
  start: number,
  opts: { timeoutMs?: number; intervalMs?: number } = {}
): Promise<BuildStatus> {
  const timeoutMs = opts.timeoutMs ?? 120_000;
  const intervalMs = opts.intervalMs ?? 300;
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const status = await fetchBuildStatus();
    if (status.completed && status.startTimestamp === start) {
      return status;
    }
    if (Date.now() >= deadline) {
      throw new BuildTimeoutError(timeoutMs);
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

export interface BuildResult {
  status: BuildStatus;
  errors: BuildLogError[];
}

/** start -> poll -> (on failure) fetch+parse the log, all in one call. */
export async function runBuild(opts?: { timeoutMs?: number; intervalMs?: number }): Promise<BuildResult> {
  const start = await buildStart();
  const status = await pollBuildStatus(start, opts);
  if (status.successful) {
    return { status, errors: [] };
  }
  const log = await fetchBuildLog();
  return { status, errors: parseBuildLog(log) };
}
