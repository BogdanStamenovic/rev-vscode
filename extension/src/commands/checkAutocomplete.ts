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
import { buildAutocompleteReport, renderReportMarkdown, type AutocompleteCheckInputs } from '../python/checkAutocompleteReport';
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

function pylanceExtension(): vscode.Extension<unknown> | undefined {
  return vscode.extensions.getExtension('ms-python.vscode-pylance');
}

function languageServerStatus(): { active: boolean; name?: string } {
  const pylance = pylanceExtension();
  if (pylance) {
    return { active: pylance.isActive, name: 'Pylance' };
  }
  // No generic "which language server is active" API exists; best-effort
  // fallback for anyone using something other than Pylance (e.g. Jedi via a
  // third-party extension) so this check doesn't just declare defeat.
  const candidate = vscode.extensions.all.find(
    (e) => e.isActive && /python.*language|pyright|jedi/i.test(String(e.packageJSON?.displayName ?? e.id))
  );
  return candidate ? { active: true, name: String(candidate.packageJSON?.displayName ?? candidate.id) } : { active: false };
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
