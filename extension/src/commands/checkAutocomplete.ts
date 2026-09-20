// revFtc.checkAutocomplete: gathers the real state of every autocomplete
// precondition and shows it as a Markdown preview (see ReportProvider below)
// rather than a toast - there are five independent things to report, each
// with its own pass/fail and fix, which does not fit in a notification.
//
// Markdown preview over a webview: it reuses VS Code's own renderer (headings,
// checkmarks, bold) for free, and follows the same virtual-document pattern
// showGeneratedJava.ts already established for "read-only generated content
// beside the editor" (GeneratedJavaProvider) - one pattern for both, not two.
import * as vscode from 'vscode';
import * as path from 'node:path';
import { readdir, readFile, stat } from 'node:fs/promises';
import { ensureExtraPath } from '../python/autocomplete';
import { stubDirFor } from '../python/ftcImportDetect';
import { fetchRcInfo } from '../hub/rcinfo';
import {
  buildAutocompleteReport,
  renderReportMarkdown,
  BASEDPYRIGHT_ID,
  type AutocompleteCheckInputs,
} from '../python/checkAutocompleteReport';
import { log } from '../output';

export const REPORT_SCHEME = 'pyftc-report';
const REPORT_URI = vscode.Uri.parse(`${REPORT_SCHEME}:/Autocomplete%20Check.md`);

export class AutocompleteReportProvider implements vscode.TextDocumentContentProvider {
  private readonly changeEmitter = new vscode.EventEmitter<vscode.Uri>();
  readonly onDidChange = this.changeEmitter.event;
  private content = '_Run "REV FTC: Check Autocomplete" to generate a report._\n';

  set(text: string): void {
    this.content = text;
    this.changeEmitter.fire(REPORT_URI);
  }

  provideTextDocumentContent(): string {
    return this.content;
  }
}

/** Extensions that actually provide Python completions, best first. The
 * Python extension itself is deliberately NOT in this list: since it
 * dropped its bundled Jedi server it contributes no completion engine at
 * all, so treating its presence as "a language server is installed" is what
 * let a completely dead autocomplete report as healthy. */
const LANGUAGE_SERVERS: Array<{ id: string; name: string }> = [
  { id: 'ms-python.vscode-pylance', name: 'Pylance' },
  { id: BASEDPYRIGHT_ID, name: 'basedpyright' },
  { id: 'ms-pyright.pyright', name: 'Pyright' },
];

/** Pylance is licensed and gated to Microsoft's own build, so on Code - OSS,
 * VSCodium and friends it is not installable advice. `vscode.env.appName`
 * is the only signal available to an extension. */
export function hostKind(appName: string): 'microsoft' | 'open-source' {
  return /^visual studio code/i.test(appName.trim()) ? 'microsoft' : 'open-source';
}

function languageServerStatus(): { active: boolean; name?: string } {
  for (const server of LANGUAGE_SERVERS) {
    const ext = vscode.extensions.getExtension(server.id);
    if (ext) {
      return { active: true, name: server.name };
    }
  }
  const candidate = vscode.extensions.all.find(
    (e) => e.isActive && /pyright|jedi|python.*language server/i.test(String(e.packageJSON?.displayName ?? e.id))
  );
  return candidate ? { active: true, name: String(candidate.packageJSON?.displayName ?? candidate.id) } : { active: false };
}

/** Offered only when the report says there is no language server at all -
 * installing an extension is the user's call, so this asks rather than
 * doing it, and a decline is remembered for the session by simply never
 * asking again outside an explicit Check Autocomplete run. */
async function offerLanguageServerInstall(host: 'microsoft' | 'open-source'): Promise<void> {
  if (host === 'microsoft') {
    void vscode.window.showWarningMessage(
      'REV FTC: no Python language server found, so nothing will autocomplete. Install Pylance from the Extensions view.'
    );
    return;
  }
  const choice = await vscode.window.showWarningMessage(
    'REV FTC: no Python language server found, so nothing will autocomplete. Pylance does not run on this build of VS Code; ' +
      'basedpyright is the open-source equivalent.',
    'Install basedpyright',
    'Not now'
  );
  if (choice !== 'Install basedpyright') {
    return;
  }
  try {
    await vscode.commands.executeCommand('workbench.extensions.installExtension', BASEDPYRIGHT_ID);
    void vscode.window.showInformationMessage('REV FTC: basedpyright installed. Reload the window to start using it.');
  } catch (err) {
    void vscode.window.showErrorMessage(`REV FTC: could not install ${BASEDPYRIGHT_ID}: ${(err as Error).message}`);
  }
}

async function pathExists(p: string): Promise<boolean> {
  try {
    await stat(p);
    return true;
  } catch {
    return false;
  }
}

/** Reads sdkVersion out of whichever bundled python/pyftc/data/sdk-*.json is
 * newest by filename (there is normally exactly one). */
async function readStubSdkVersion(extensionPath: string): Promise<string | undefined> {
  const dataDir = path.join(extensionPath, 'python', 'pyftc', 'data');
  try {
    const entries = (await readdir(dataDir)).filter((f) => /^sdk-.*\.json$/.test(f)).sort();
    const newest = entries.at(-1);
    if (!newest) {
      return undefined;
    }
    const raw = await readFile(path.join(dataDir, newest), 'utf8');
    const parsed = JSON.parse(raw) as { sdkVersion?: unknown };
    return typeof parsed.sdkVersion === 'string' ? parsed.sdkVersion : undefined;
  } catch {
    return undefined;
  }
}

async function readHubSdkVersion(): Promise<string | undefined> {
  try {
    const rcInfo = await fetchRcInfo();
    return rcInfo.sdkVersion;
  } catch {
    return undefined; // hub unreachable - not a failure for this report
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Asks the active language server to resolve `import ftc.hardware` in a
 * throwaway, never-shown document, via the same command the editor itself
 * uses for go-to-definition. Retries once after a longer wait, since
 * Pylance's first analysis pass after an extraPaths change can take a few
 * seconds - see checkAutocompleteReport.ts's comment on why this never
 * reports a hard "no". */
async function checkImportResolves(): Promise<'yes' | 'unknown'> {
  try {
    const doc = await vscode.workspace.openTextDocument({ language: 'python', content: 'import ftc.hardware\n' });
    const position = new vscode.Position(0, 'import '.length + 2); // inside "ftc"
    for (const waitMs of [300, 2000]) {
      await sleep(waitMs);
      const definitions = await vscode.commands.executeCommand<(vscode.Location | vscode.LocationLink)[]>(
        'vscode.executeDefinitionProvider',
        doc.uri,
        position
      );
      if (definitions && definitions.length > 0) {
        return 'yes';
      }
    }
    return 'unknown';
  } catch (err) {
    log(`checkAutocomplete: import-resolution probe failed: ${(err as Error).message}`);
    return 'unknown';
  }
}

async function gatherInputs(context: vscode.ExtensionContext): Promise<AutocompleteCheckInputs> {
  const stubDir = stubDirFor(context.extensionPath);
  const extraPaths = vscode.workspace.getConfiguration('python.analysis').get<string[]>('extraPaths') ?? [];
  const [stubDirExists, importResolves, stubSdkVersion, hubSdkVersion] = await Promise.all([
    pathExists(stubDir),
    checkImportResolves(),
    readStubSdkVersion(context.extensionPath),
    readHubSdkVersion(),
  ]);
  return {
    languageServer: languageServerStatus(),
    host: hostKind(vscode.env.appName),
    extraPaths,
    stubDir,
    stubDirExists,
    importResolves,
    stubSdkVersion,
    hubSdkVersion,
  };
}

export async function runCheckAutocomplete(context: vscode.ExtensionContext, provider: AutocompleteReportProvider): Promise<void> {
  // Self-healing best effort before reporting: if extraPaths is missing and
  // the user hasn't opted out (autocomplete.ts's rule), just fix it so the
  // report reflects the corrected state instead of nagging about something
  // we could have silently done ourselves.
  await ensureExtraPath(context);

  const inputs = await gatherInputs(context);
  const items = buildAutocompleteReport(inputs);
  provider.set(renderReportMarkdown(items, new Date()));

  const failed = items.filter((i) => i.status === 'fail').length;
  const warned = items.filter((i) => i.status === 'warn').length;
  log(`checkAutocomplete: ${items.length} check(s), ${failed} failing, ${warned} warning`);

  if (!inputs.languageServer.active) {
    void offerLanguageServerInstall(inputs.host);
  }

  const opened = await vscode.workspace.openTextDocument(REPORT_URI);
  const shown = await vscode.commands.executeCommand('markdown.showPreview', opened.uri).then(
    () => true,
    () => false
  );
  if (!shown) {
    // Markdown preview unavailable for some reason (extension disabled) -
    // fall back to the raw document rather than silently doing nothing.
    await vscode.window.showTextDocument(opened, { preview: false });
  }
}
