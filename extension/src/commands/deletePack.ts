// revFtc.deletePack: removes packs - a .py file, its generated man page, and
// its classes on the hub - with an Undo. Deploy uploads every .py in the
// source root and only prunes the hub after a fully successful deploy, so
// before this a stray pack stayed on the Driver Hub until every other file
// translated cleanly (the team's workaround was renaming it to .txt).
import * as vscode from 'vscode';
import * as path from 'node:path';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolveSourceRootDir } from '../workspaceRoot';
import { translateProject } from '../translate';
import { deleteFiles, fileTree, runBuild } from '../hub/onbotjava';
import { clearDiagnosticsForUri } from '../diagnostics';
import { canonical, hubFilesForPack, isDeployedSource, isGeneratedManual, opModeNames, orphanGroups } from '../packs';
import { log } from '../output';

interface LocalPack {
  kind: 'local';
  py: vscode.Uri;
  manual?: vscode.Uri;
  opModes: string[];
  hubFiles: string[];
}

interface HubOnlyPack {
  kind: 'hub';
  label: string;
  hubFiles: string[];
}

type Pack = LocalPack | HubOnlyPack;

interface Backup {
  dir: string;
  files: Array<{ uri: vscode.Uri; stored: string }>;
}

async function readText(uri: vscode.Uri): Promise<string | undefined> {
  try {
    return Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf8');
  } catch {
    return undefined;
  }
}

async function findLocalPacks(root: string): Promise<LocalPack[]> {
  const uris = await vscode.workspace.findFiles(new vscode.RelativePattern(root, '**/*.py'), '**/node_modules/**');
  const packs: LocalPack[] = [];
  for (const py of uris) {
    const rel = path.relative(root, py.fsPath);
    if (!isDeployedSource(rel)) {
      continue;
    }
    const source = (await readText(py)) ?? '';
    const mdUri = vscode.Uri.file(py.fsPath.replace(/\.py$/, '.md'));
    const md = await readText(mdUri);
    packs.push({
      kind: 'local',
      py,
      manual: md !== undefined && isGeneratedManual(md) ? mdUri : undefined,
      opModes: opModeNames(source),
      hubFiles: [],
    });
  }
  return packs.sort((a, b) => a.py.fsPath.localeCompare(b.py.fsPath));
}

/** What is on the hub and which pack owns it. Best effort: without a hub the
 * local files can still be deleted, and the next deploy prunes the hub. */
async function mapHub(root: string, packs: LocalPack[]): Promise<{ reachable: boolean; orphans: HubOnlyPack[] }> {
  let existing: string[];
  try {
    existing = await fileTree();
  } catch (err) {
    log(`deletePack: hub not reachable (${(err as Error).message}); deleting local files only`);
    return { reachable: false, orphans: [] };
  }
  const existingSet = new Set(existing);
  let translated: Array<{ source: string; className: string; hubPath: string }> = [];
  try {
    translated = (await translateProject(root)).files;
  } catch (err) {
    log(`deletePack: could not translate to map hub files (${(err as Error).message})`);
  }
  const claimed = new Set<string>();
  for (const p of packs) {
    p.hubFiles = hubFilesForPack(p.py.fsPath, translated, existingSet);
    p.hubFiles.forEach((f) => claimed.add(f));
  }
  const produced = new Set(translated.map((f) => canonical(f.hubPath)));
  const orphans = [...orphanGroups(existing, produced, claimed)].map(([label, hubFiles]) => ({
    kind: 'hub' as const,
    label,
    hubFiles,
  }));
  return { reachable: true, orphans };
}

function describe(p: Pack, root: string, reachable: boolean): vscode.QuickPickItem & { pack: Pack } {
  if (p.kind === 'hub') {
    return {
      pack: p,
      label: `$(cloud) ${p.label}`,
      description: 'on the hub only, no local file',
      detail: `removes ${p.hubFiles.length} file(s) from the hub`,
    };
  }
  const hub = !reachable ? 'hub not connected: removed there on the next deploy' : p.hubFiles.length ? `removes ${p.hubFiles.length} file(s) from the hub` : 'not on the hub';
  return {
    pack: p,
    label: `$(file-code) ${path.relative(root, p.py.fsPath)}`,
    description: p.opModes.join(', ') || 'no OpMode in this file',
    detail: `${p.manual ? 'with its man page, ' : ''}${hub}`,
  };
}

async function backUp(context: vscode.ExtensionContext, uris: vscode.Uri[]): Promise<Backup> {
  const dir = path.join(context.globalStorageUri.fsPath, 'deleted-packs', new Date().toISOString().replace(/[:.]/g, '-'));
  await mkdir(dir, { recursive: true });
  const files = [];
  for (const [i, uri] of uris.entries()) {
    const stored = path.join(dir, `${i}-${path.basename(uri.fsPath)}`);
    await writeFile(stored, await vscode.workspace.fs.readFile(uri));
    files.push({ uri, stored });
  }
  await writeFile(path.join(dir, 'manifest.json'), JSON.stringify(files.map((f) => ({ original: f.uri.fsPath, stored: f.stored })), null, 2));
  return { dir, files };
}

async function restore(backup: Backup): Promise<void> {
  for (const f of backup.files) {
    await vscode.workspace.fs.writeFile(f.uri, await readFile(f.stored));
  }
  const choice = await vscode.window.showInformationMessage(
    `REV FTC: restored ${backup.files.length} file(s). Deploy to put the pack back on the robot.`,
    'Deploy now'
  );
  if (choice === 'Deploy now') {
    await vscode.commands.executeCommand('revFtc.deploy');
  }
}

async function removeLocal(uri: vscode.Uri): Promise<void> {
  try {
    await vscode.workspace.fs.delete(uri, { useTrash: true });
  } catch (err) {
    // No trash on this filesystem. The file is already backed up for Undo,
    // so a plain delete loses nothing.
    log(`deletePack: trash unavailable for ${uri.fsPath} (${(err as Error).message}); deleting (backup kept for Undo)`);
    await vscode.workspace.fs.delete(uri);
  }
  clearDiagnosticsForUri(uri);
}

/** `options.confirmed` is for programmatic callers (the e2e suite, which
 * cannot click a modal dialog); the Explorer menu and the palette never pass
 * it, so a person always confirms. */
export async function runDeletePack(
  context: vscode.ExtensionContext,
  target?: vscode.Uri,
  options: { confirmed?: boolean } = {}
): Promise<void> {
  const root = resolveSourceRootDir();
  const local = await findLocalPacks(root);
  const { reachable, orphans } = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Window, title: 'REV FTC: checking the hub' },
    () => mapHub(root, local)
  );

  let chosen: Pack[];
  if (target) {
    const pack = local.find((p) => path.normalize(p.py.fsPath) === path.normalize(target.fsPath));
    if (!pack) {
      void vscode.window.showWarningMessage(`REV FTC: ${path.basename(target.fsPath)} is not a file deploy uploads.`);
      return;
    }
    chosen = [pack];
  } else {
    const items = [...local, ...orphans].map((p) => describe(p, root, reachable));
    if (items.length === 0) {
      void vscode.window.showInformationMessage('REV FTC: there are no packs to delete.');
      return;
    }
    const picked = await vscode.window.showQuickPick(items, {
      canPickMany: true,
      title: 'Delete packs',
      placeHolder: 'Pick the packs to delete (local files go to the Trash, with Undo)',
    });
    if (!picked || picked.length === 0) {
      return;
    }
    chosen = picked.map((i) => i.pack);
  }

  const localFiles = chosen.flatMap((p) => (p.kind === 'local' ? [p.py, ...(p.manual ? [p.manual] : [])] : []));
  const hubFiles = [...new Set(chosen.flatMap((p) => p.hubFiles))].sort();
  const summary = [
    localFiles.length ? `Move to Trash: ${localFiles.map((u) => path.relative(root, u.fsPath)).join(', ')}` : '',
    hubFiles.length ? `Remove from the hub: ${hubFiles.length} file(s), then rebuild` : '',
    !reachable && localFiles.length ? 'The hub is not connected; the next deploy removes the pack there.' : '',
  ].filter(Boolean).join('\n');
  if (!options.confirmed) {
    const confirm = await vscode.window.showWarningMessage('Delete the selected pack(s)?', { modal: true, detail: summary }, 'Delete');
    if (confirm !== 'Delete') {
      return;
    }
  }

  const backup = localFiles.length ? await backUp(context, localFiles) : undefined;
  for (const uri of localFiles) {
    await removeLocal(uri);
  }
  log(`deletePack: removed ${localFiles.length} local file(s)${backup ? `, backup in ${backup.dir}` : ''}`);

  let hubNote = '';
  if (reachable && hubFiles.length) {
    try {
      await deleteFiles(hubFiles);
      const build = await runBuild();
      hubNote = build.status.successful
        ? ` Removed from the hub; the Driver Hub no longer lists it.`
        : ` Removed from the hub, but the rebuild failed on other files, so the Driver Hub keeps its old list until they compile (see Deploy).`;
    } catch (err) {
      hubNote = ` Could not update the hub (${(err as Error).message}); the next deploy removes it.`;
    }
  } else if (!reachable && localFiles.length) {
    hubNote = ' The hub was not connected; the next deploy removes the pack there.';
  }

  const names = chosen.map((p) => (p.kind === 'local' ? path.basename(p.py.fsPath) : p.label)).join(', ');
  const message = `REV FTC: deleted ${names}.${hubNote}`;
  if (backup) {
    // Not awaited: the command is finished once the files are gone, and an
    // Undo nobody clicks must not keep it pending. The backup outlives the
    // notification, in globalStorage/deleted-packs.
    void vscode.window.showInformationMessage(message, 'Undo').then((choice) => {
      if (choice === 'Undo') {
        void restore(backup);
      }
    });
  } else {
    void vscode.window.showInformationMessage(message);
  }
}
