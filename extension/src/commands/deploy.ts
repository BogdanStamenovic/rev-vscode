// revFtc.deploy: save dirty .py -> translate -> diff against the hub's
// /src/.../pyftc/ folder -> save + build -> map javac errors back to .py
// lines via lineMap, or notify (not diagnose) for errors in hand-written
// OnBot Java outside our folder, since the build compiles all of /src.
import * as vscode from 'vscode';
import { translateProject, applyTranslationDiagnostics, TranslatorError } from '../translate';
import { fileTree, saveFile, deleteFiles, runBuild } from '../hub/onbotjava';
import { canonicalHubPath, type TranslatedFile } from '../pyftcContract';
import { mapJavaLineToPython } from '../hub/lineMap';
import { formatBuildLogError, type BuildLogError } from '../hub/buildLog';
import { getDiagnosticCollection, addDiagnostics } from '../diagnostics';
import { log } from '../output';
import { HubUnreachableError } from '../hub/connection';
import { resolveSourceRootDir } from '../workspaceRoot';
import { checkConfigChanges } from '../hub/configWatch';

const OUR_FOLDER_PREFIX = 'org/firstinspires/ftc/teamcode/pyftc/';

async function saveDirtyPythonFiles(): Promise<void> {
  const dirty = vscode.workspace.textDocuments.filter((d) => d.languageId === 'python' && d.isDirty);
  for (const doc of dirty) {
    await doc.save();
  }
}

export async function runDeploy(): Promise<void> {
  const collection = getDiagnosticCollection();

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'REV FTC deploy', cancellable: false },
    async (progress) => {
      try {
        await saveDirtyPythonFiles();

        // Third configWatch.ts trigger ("before a deploy"). Best-effort and
        // non-blocking of the deploy itself: a slow/unreachable hub here
        // just means no notification this time, not a failed deploy - the
        // deploy's own hub calls below will surface any real connectivity
        // problem on their own.
        void checkConfigChanges();

        const root = resolveSourceRootDir();

        progress.report({ message: 'Translating...' });
        const result = await translateProject(root);
        const hasErrors = applyTranslationDiagnostics(collection, result);
        if (hasErrors) {
          vscode.window.showErrorMessage(
            'REV FTC: translation errors — see the Problems panel before deploying.'
          );
          return;
        }
        if (result.files.length === 0) {
          vscode.window.showWarningMessage('REV FTC: no OpMode classes found to deploy.');
          return;
        }

        progress.report({ message: 'Checking hub files...' });
        const existing = await fileTree();
        const produced = new Map<string, TranslatedFile>();
        for (const f of result.files) {
          produced.set(canonicalHubPath(f.hubPath), f);
        }
        // The tree lists directories too (".../pyftc/"); deleting that would take
        // every generated file with it, so only stale .java files qualify.
        const toDelete = existing.filter(
          (p) => p.startsWith(OUR_FOLDER_PREFIX) && p.endsWith('.java') && !produced.has(p)
        );
        if (toDelete.length > 0) {
          log(`deploy: deleting ${toDelete.length} stale file(s) from ${OUR_FOLDER_PREFIX}`);
          await deleteFiles(toDelete);
        }

        progress.report({ message: `Saving ${result.files.length} file(s)...` });
        for (const f of result.files) {
          await saveFile(f.hubPath, f.java);
        }

        progress.report({ message: 'Building...' });
        const build = await runBuild();

        if (build.status.successful) {
          const seconds = ((build.status.timestamp - build.status.startTimestamp) / 1000).toFixed(1);
          vscode.window.showInformationMessage(
            `REV FTC: deployed ${result.files.length} OpMode(s) (build ${seconds}s).`
          );
          return;
        }

        reportBuildFailure(build.errors, produced);
      } catch (err) {
        vscode.window.showErrorMessage(`REV FTC deploy failed: ${friendlyMessage(err)}`);
      }
    }
  );
}

function reportBuildFailure(errors: BuildLogError[], produced: Map<string, TranslatedFile>): void {
  const foreignFiles = new Set<string>();

  for (const err of errors) {
    const file = produced.get(err.file);
    if (!file) {
      // Not one of ours: the hub build compiles everything under /src, so
      // this is hand-written OnBot Java breaking the build. We have no
      // lineMap for it, so surface it as a notification naming the file
      // rather than a (wrong) diagnostic on some .py file.
      foreignFiles.add(err.file);
      continue;
    }
    const mapped = mapJavaLineToPython(file.lineMap, err.line);
    const line0 = Math.max(0, mapped.pythonLine - 1);
    const range = new vscode.Range(line0, 0, line0, Number.MAX_SAFE_INTEGER);
    const message = mapped.fallback
      ? `${formatBuildLogError(err)}\n(java ${err.file}:${err.line}:${err.col} — could not map to an exact source line)`
      : formatBuildLogError(err);
    const diag = new vscode.Diagnostic(
      range,
      message,
      err.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning
    );
    diag.source = 'pyftc-build';
    addDiagnostics(vscode.Uri.file(file.source), [diag]);
  }

  if (foreignFiles.size > 0) {
    vscode.window.showWarningMessage(
      `REV FTC: build also failed in file(s) not managed by this extension: ${[...foreignFiles].join(', ')}. ` +
        'These are hand-written OnBot Java files breaking the shared build.'
    );
  }

  vscode.window.showErrorMessage('REV FTC: build failed — see the Problems panel.');
}

function friendlyMessage(err: unknown): string {
  if (err instanceof TranslatorError) {
    return `translator error: ${err.message}`;
  }
  if (err instanceof HubUnreachableError) {
    return err.message;
  }
  return err instanceof Error ? err.message : String(err);
}
