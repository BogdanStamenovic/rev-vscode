import { hubFetch } from './http';
import { stripPassphrase, type RcInfo } from './rcinfoTypes';

export type { RcInfo } from './rcinfoTypes';

export async function fetchRcInfo(): Promise<RcInfo> {
  const res = await hubFetch('/js/rcInfo.json');
  if (!res.ok) {
    throw new Error(`rcInfo.json fetch failed: HTTP ${res.status}`);
  }
  const raw = await res.json();
  return stripPassphrase(raw);
}
