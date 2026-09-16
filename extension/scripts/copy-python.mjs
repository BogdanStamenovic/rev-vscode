// vsce only packs files inside extension/. The python/ translator lives one
// level up (owned by another agent, built concurrently) so we mirror it into
// extension/python before packaging. extension/python is gitignored; this
// copy is regenerated on every `npm run package`.
import { cpSync, rmSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const extensionDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const src = path.join(extensionDir, '..', 'python');
const dest = path.join(extensionDir, 'python');

if (!existsSync(src)) {
  console.error(`copy-python: source ${src} does not exist`);
  process.exit(1);
}

const EXCLUDE_BASENAMES = new Set(['__pycache__', '.pytest_cache', 'tests', '.git']);

rmSync(dest, { recursive: true, force: true });
cpSync(src, dest, {
  recursive: true,
  // Only pyftc/ and ftc/ (and any sibling runtime package/data dirs) are
  // needed at runtime - test suites and bytecode caches would just bloat
  // the shipped vsix for no benefit.
  filter: (source) => !EXCLUDE_BASENAMES.has(path.basename(source)),
});
console.log(`copy-python: mirrored ${src} -> ${dest} (excluding ${[...EXCLUDE_BASENAMES].join(', ')})`);
