// Thin fetch wrapper over the resolved hub connection: logs every call to
// the output channel and retries once (re-resolving the connection) on a
// network-level failure, per ARCHITECTURE.md's "cache; re-resolve on
// failure" instruction. HTTP-level error statuses (4xx/5xx) are returned
// as-is for the caller to interpret - they aren't a connectivity problem.
import { getConnection, invalidateConnection, HubUnreachableError } from './connection';
import { logHttp } from '../output';

export async function hubFetch(path: string, init?: RequestInit): Promise<Response> {
  return attempt(path, init, true);
}

async function attempt(path: string, init: RequestInit | undefined, allowRetry: boolean): Promise<Response> {
  const conn = await getConnection();
  const url = `${conn.baseUrl}${path}`;
  const method = init?.method ?? 'GET';
  const start = Date.now();
  try {
    const res = await fetch(url, init);
    logHttp(method, path, res.status, Date.now() - start);
    return res;
  } catch (err) {
    logHttp(method, path, 'error', Date.now() - start);
    if (allowRetry) {
      invalidateConnection();
      return attempt(path, init, false);
    }
    throw new HubUnreachableError(`request to ${path} failed: ${(err as Error).message}`);
  }
}
