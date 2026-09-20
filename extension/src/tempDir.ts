// Shared scratch-directory helper: several flows need to hand the CLI a
// config XML / rcInfo.json pair as files (Contract 3's `starter`,
// `starter-update`, `manual`, `config-fingerprint` all take file paths, not
// stdin), so this got pulled out of spawnStarterPack.ts once configWatch.ts
// and updateFromConfig.ts needed the exact same pattern.
import * as os from 'node:os';
import * as path from 'node:path';
import { mkdtemp, rm } from 'node:fs/promises';

export async function withTempDir<T>(fn: (dir: string) => Promise<T>): Promise<T> {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'rev-vscode-'));
  try {
    return await fn(dir);
  } finally {
    await rm(dir, { recursive: true, force: true }).catch(() => undefined);
  }
}
