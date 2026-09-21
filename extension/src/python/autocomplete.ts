// Wires python.analysis.extraPaths to the bundled ftc stub package so
// Pylance resolves `import ftc.*` automatically - no prompt, no "Enable FTC
// autocomplete?" dialog. ensureAutocomplete() is called from two triggers:
// extension activation (if the workspace already has a file importing
// ftc.*) and right after Spawn Starter Pack writes a new .py file (which
// always imports ftc.*). A live workspace-edit listener additionally covers
// the case where a user adds an `import ftc...` to an existing file mid
// session without either of those two moments happening.
//
// Opt-out rule (the "don't fight the user" requirement): we record, in
// workspaceState, the exact stub path we last added ourselves. On every
// check:
//   - path already present in extraPaths -> nothing to do, whoever put it
//     there (us or the user) is happy.
//   - path absent, and our record says we never added anything in this
//     workspace -> add it, record it. This is the common first-time case.
//   - path absent, and our record matches the path we'd add now -> the user
//     (or some other tool) removed exactly what we added, most likely on
//     purpose. We do NOT re-add it - just log that we're staying out of the
//     way. There is no dialog asking "did you mean to remove this?": the
//     whole point of going automatic is not re-litigating it every session.
// The only way to get autocomplete back after opting out this way is to add
// the path back by hand (or delete the workspaceState key, e.g. by clearing
// workspace storage) - a deliberate one-way door, not a bug.
import * as vscode from 'vscode';
import { log } from '../output';
import { hasFtcImport, stubDirFor } from './ftcImportDetect';
import { workspaceIsSetUp } from '../commands/setupFiles';

export { hasFtcImport, stubDirFor };

const MANAGED_PATH_KEY = 'revFtc.autocompleteManagedPath';

/** The idempotent, no-prompt "make sure extraPaths has our stub dir" step.
 * Safe to call as often as needed (activation, after spawning a starter
 * pack, on every relevant document event) - see the file header for the
 * opt-out rule that keeps it from re-fighting a deliberate removal. */
export async function ensureExtraPath(context: vscode.ExtensionContext): Promise<void> {
  if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
    return;
  }
  if (await workspaceIsSetUp()) {
    return; // Setup Files owns the paths now, via the stable .pyftc/stubs link
  }
  const stubPath = stubDirFor(context.extensionPath);
  const config = vscode.workspace.getConfiguration('python.analysis');
  const current = config.get<string[]>('extraPaths') ?? [];

  if (current.includes(stubPath)) {
    return;
  }

  const managedPath = context.workspaceState.get<string>(MANAGED_PATH_KEY);
  if (managedPath === stubPath) {
    log(
      `autocomplete: ${stubPath} is no longer in python.analysis.extraPaths but we previously added it - ` +
        'treating that as deliberate and leaving it removed'
    );
    return;
  }

  try {
    await config.update('extraPaths', [...current, stubPath], vscode.ConfigurationTarget.Workspace);
    await addBasedpyrightPath(stubPath);
  } catch (err) {
    // Happens when no Python language server extension is installed at all:
    // `python.analysis.extraPaths` isn't even a registered setting then, and
    // config.update() throws rather than no-op'ing. Not a bug to surface as
    // one - checkAutocomplete's "Python language server" check already
    // reports this state on its own; this call site just needs to not blow
    // up the caller (spawnStarterPack awaits us inside its own try/catch,
    // and a throw here would wrongly turn a successful spawn into a
    // reported failure).
    log(`autocomplete: could not write python.analysis.extraPaths (${(err as Error).message}) - is a Python extension installed?`);
    return;
  }
  await context.workspaceState.update(MANAGED_PATH_KEY, stubPath);
  log(`autocomplete: added ${stubPath} to python.analysis.extraPaths`);
}

/** basedpyright reads its own `basedpyright.analysis.extraPaths` rather
 * than Pylance's `python.analysis.*`, and it is the only language server
 * that works on Code - OSS builds (Pylance is gated to Microsoft's own
 * build). Writing both keys costs nothing and means the stubs resolve
 * whichever of the two is installed. Failing here is not fatal: the key is
 * unregistered when basedpyright is not installed. */
async function addBasedpyrightPath(stubPath: string): Promise<void> {
  try {
    const config = vscode.workspace.getConfiguration('basedpyright.analysis');
    const current = config.get<string[]>('extraPaths') ?? [];
    if (!current.includes(stubPath)) {
      await config.update('extraPaths', [...current, stubPath], vscode.ConfigurationTarget.Workspace);
    }
  } catch {
    // basedpyright not installed - nothing to configure.
  }
}

async function workspaceHasFtcImport(): Promise<boolean> {
  const found = await vscode.workspace.findFiles('**/*.py', '**/{node_modules,.git}/**', 200);
  for (const uri of found) {
    try {
      const bytes = await vscode.workspace.fs.readFile(uri);
      if (hasFtcImport(Buffer.from(bytes).toString('utf8'))) {
        return true;
      }
    } catch {
      // Unreadable/vanished mid-scan - skip it, don't fail the whole scan.
    }
  }
  return false;
}

/** Activation-time entry point: only wires extraPaths if the workspace
 * already looks like it has pyftc code in it. Also called directly by
 * spawnStarterPack.ts right after writing a new file, where the "does the
 * workspace import ftc.*" question is already known to be yes. */
export async function ensureAutocomplete(context: vscode.ExtensionContext): Promise<void> {
  if (await workspaceHasFtcImport()) {
    await ensureExtraPath(context);
  }
}

/** Live coverage for a file that starts importing ftc.* mid-session (e.g. a
 * hand-written import added to an existing file) without going through
 * either of ensureAutocomplete()'s two trigger moments. Registered once from
 * extension.ts; cheap because it only inspects documents already open in an
 * editor (no disk I/O) and short-circuits the instant it sees a match. */
export function watchForFtcImports(context: vscode.ExtensionContext): vscode.Disposable {
  const check = (doc: vscode.TextDocument) => {
    if (doc.languageId === 'python' && hasFtcImport(doc.getText())) {
      void ensureExtraPath(context);
    }
  };
  return vscode.Disposable.from(
    vscode.workspace.onDidOpenTextDocument(check),
    vscode.workspace.onDidSaveTextDocument(check)
  );
}
