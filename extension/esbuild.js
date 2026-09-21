// Bundles the extension into dist/extension.js. 'vscode' is provided by the
// extension host at runtime and must stay external; everything else (e.g.
// fast-xml-parser) gets bundled so `vsce package --no-dependencies` works.
const esbuild = require('esbuild');

const watch = process.argv.includes('--watch');

const options = {
  entryPoints: ['src/extension.ts'],
  bundle: true,
  outfile: 'dist/extension.js',
  external: ['vscode'],
  format: 'cjs',
  platform: 'node',
  target: 'node18',
  sourcemap: true,
  logLevel: 'info',
};

// Webview bundles (simulator panel, controller bridge page, dev harness). They
// run in a browser under a strict CSP: one self-contained IIFE per page, no
// runtime imports, no eval.
const fs = require('fs');
const path = require('path');

const webviewCommon = {
  bundle: true,
  format: 'iife',
  platform: 'browser',
  target: 'es2020',
  sourcemap: true,
  logLevel: 'info',
  loader: { '.css': 'css' },
  minify: true,
};

const webviewBuilds = [
  { ...webviewCommon, entryPoints: ['webview/sim/main.ts'], outfile: 'dist/sim/webview.js' },
  { ...webviewCommon, entryPoints: ['webview/sim/bridge.ts'], outfile: 'dist/sim/bridge.js' },
  { ...webviewCommon, entryPoints: ['webview/sim/dev/harness.ts'], outfile: 'dist/sim-dev/harness.js' },
];

const staticCopies = [
  ['webview/sim/bridge.html', 'dist/sim/bridge.html'],
  ['webview/sim/dev/harness.html', 'dist/sim-dev/harness.html'],
];

function copyStatic() {
  for (const [from, to] of staticCopies) {
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.copyFileSync(from, to);
  }
}

const copyStaticPlugin = {
  name: 'copy-static',
  setup(build) {
    build.onEnd(() => copyStatic());
  },
};

const webviewOnly = process.argv.includes('--webview-only');

async function run() {
  const all = webviewOnly ? [] : [options];
  all.push(...webviewBuilds.map((b, i) => (i === 0 ? { ...b, plugins: [copyStaticPlugin] } : b)));
  if (watch) {
    for (const o of all) {
      const ctx = await esbuild.context(o);
      await ctx.watch();
    }
    if (fs.watch) {
      for (const [from] of staticCopies) fs.watch(from, () => copyStatic());
    }
    console.log('watching...');
  } else {
    await Promise.all(all.map((o) => esbuild.build(o)));
    copyStatic();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
