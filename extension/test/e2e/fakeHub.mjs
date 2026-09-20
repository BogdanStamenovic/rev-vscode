// Minimal HTTP stand-in for the hub's OnBot Java web server, used only by
// test/e2e/fakeSuite.js's config-watch/update flow. That flow never touches
// /java/file/* or /java/build/* (spawnStarterPack, configWatch and
// updateFromConfig only ever call GET /js/rcInfo.json - the active config
// XML itself has no HTTP endpoint at all, see fake_adb.py), so this server
// only implements that one route. Anything else 404s on purpose: a test
// that needed more would be relying on behavior this fake doesn't model.
import http from 'node:http';

export function startFakeHub(state) {
  const server = http.createServer((req, res) => {
    if (req.url === '/js/rcInfo.json') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(
        JSON.stringify({
          activeConfigName: state.activeConfigName,
          rcVersion: '11.2',
          sdkVersion: state.sdkVersion ?? '11.2.0',
          deviceName: 'Fake Hub',
          isREVControlHub: true,
          revHubNamesAndVersions: [],
        })
      );
      return;
    }
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('not faked');
  });

  return new Promise((resolve, reject) => {
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({
        url: `http://127.0.0.1:${address.port}`,
        close: () => new Promise((r) => server.close(() => r())),
      });
    });
  });
}
