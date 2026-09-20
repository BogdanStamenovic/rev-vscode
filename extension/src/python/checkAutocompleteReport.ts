// Pure report-building logic for revFtc.checkAutocomplete: turns a bag of
// already-gathered facts (see AutocompleteCheckInputs) into a list of
// pass/fail/warn/unknown items with a suggested fix. Kept separate from the
// command in commands/checkAutocomplete.ts, which is the only part that
// actually touches vscode/fs/the hub, so this half is unit testable with
// hand-built inputs and no vscode shim.

export type CheckStatus = 'pass' | 'fail' | 'warn' | 'unknown';

export interface CheckItem {
  id: string;
  label: string;
  status: CheckStatus;
  detail: string;
  fix?: string;
}

export interface AutocompleteCheckInputs {
  languageServer: { active: boolean; name?: string };
  /** 'microsoft' = official VS Code, the only build Pylance will run on.
   * 'open-source' = Code - OSS / VSCodium / any build served by Open VSX:
   * Pylance refuses to load there, and ms-python.python alone ships no
   * completion engine of its own, so recommending Pylance would be advice
   * that cannot work. basedpyright is the Open VSX equivalent. */
  host: 'microsoft' | 'open-source';
  extraPaths: string[];
  stubDir: string;
  stubDirExists: boolean;
  /** 'yes' when a definition provider actually resolved the import to a
   * location; 'unknown' otherwise. There is deliberately no 'no' - we have
   * no reliable way to tell "genuinely broken" from "Pylance hasn't
   * finished indexing yet", and a false "broken" is worse than an honest
   * "couldn't confirm". */
  importResolves: 'yes' | 'unknown';
  /** sdkVersion field out of the bundled python/pyftc/data/sdk-*.json;
   * undefined if that file is missing (a broken install) or unreadable. */
  stubSdkVersion?: string;
  /** rcInfo.sdkVersion from the hub; undefined when the hub isn't reachable
   * right now (not itself a failure - most of this report is meaningful
   * without a hub connected at all). */
  hubSdkVersion?: string;
}

export const BASEDPYRIGHT_ID = 'detachhead.basedpyright';
const INSTALL_BASEDPYRIGHT_HINT = `run "Extensions: Install Extension" and pick ${BASEDPYRIGHT_ID}, or "REV FTC: Check Autocomplete" offers to install it for you. Reload the window afterwards.`;

function item(id: string, label: string, status: CheckStatus, detail: string, fix?: string): CheckItem {
  return { id, label, status, detail, fix };
}

export function buildAutocompleteReport(inputs: AutocompleteCheckInputs): CheckItem[] {
  const items: CheckItem[] = [];

  items.push(
    inputs.languageServer.active
      ? item(
          'language-server',
          'Python language server',
          'pass',
          `${inputs.languageServer.name ?? 'A Python language server'} is installed and active.`
        )
      : item(
          'language-server',
          'Python language server',
          'fail',
          inputs.host === 'open-source'
            ? 'No Python language server was found. This editor is a Code - OSS build, and the Python extension on its own ' +
              'provides no completions: that engine is Pylance, which Microsoft only ships for official VS Code.'
            : 'No active Python language server was found.',
          inputs.host === 'open-source'
            ? `Install basedpyright, the open-source equivalent that works here: ${INSTALL_BASEDPYRIGHT_HINT}`
            : "Install the 'Pylance' extension from the Extensions view, then reload the window."
        )
  );

  const hasExtraPath = inputs.extraPaths.includes(inputs.stubDir);
  items.push(
    hasExtraPath
      ? item('extra-paths', 'python.analysis.extraPaths', 'pass', `Contains the stub directory (${inputs.stubDir}).`)
      : item(
          'extra-paths',
          'python.analysis.extraPaths',
          'fail',
          `Does not contain ${inputs.stubDir}.`,
          'If you removed this on purpose, this is expected - the extension records that and will not re-add it. ' +
            `Otherwise add it yourself: Settings -> python.analysis.extraPaths -> add "${inputs.stubDir}".`
        )
  );

  items.push(
    inputs.stubDirExists
      ? item('stub-dir', 'Stub package on disk', 'pass', `${inputs.stubDir} exists.`)
      : item(
          'stub-dir',
          'Stub package on disk',
          'fail',
          `${inputs.stubDir} does not exist.`,
          'Reinstall the extension - the bundled python/ directory is missing from this install.'
        )
  );

  items.push(
    inputs.importResolves === 'yes'
      ? item('import-resolves', 'import ftc.hardware resolves', 'pass', 'The language server resolved the import to a real location.')
      : item(
          'import-resolves',
          'import ftc.hardware resolves',
          'unknown',
          'Could not confirm this. Either one of the checks above is failing, or the language server just has not finished indexing yet.',
          'Fix the checks above if any failed, then reload the window (or run "Python: Restart Language Server") and check again in a few seconds.'
        )
  );

  if (!inputs.hubSdkVersion) {
    items.push(
      item(
        'sdk-version',
        'Stub SDK version vs. hub',
        'unknown',
        `Stub is built for SDK ${inputs.stubSdkVersion ?? '(unknown)'}; the hub is not reachable right now, so its SDK version can't be compared.`,
        'Connect to the hub (Wi-Fi or USB) and run this check again.'
      )
    );
  } else if (!inputs.stubSdkVersion) {
    items.push(
      item(
        'sdk-version',
        'Stub SDK version vs. hub',
        'fail',
        'No bundled sdk-<version>.json was found to compare against.',
        'Reinstall the extension.'
      )
    );
  } else if (inputs.stubSdkVersion === inputs.hubSdkVersion) {
    items.push(item('sdk-version', 'Stub SDK version vs. hub', 'pass', `Both are SDK ${inputs.stubSdkVersion}.`));
  } else {
    items.push(
      item(
        'sdk-version',
        'Stub SDK version vs. hub',
        'warn',
        `Stub is built for SDK ${inputs.stubSdkVersion}, but the hub reports SDK ${inputs.hubSdkVersion}. ` +
          "APIs new in the hub's SDK will not autocomplete (or translate) until the stub is regenerated.",
        "Regenerate the stub and type database for the hub's SDK version (see sdkgen in ARCHITECTURE.md), or ignore this if you haven't hit a missing API yet."
      )
    );
  }

  return items;
}

const STATUS_ICON: Record<CheckStatus, string> = { pass: '✅', fail: '❌', warn: '⚠️', unknown: '❔' };

export function renderReportMarkdown(items: CheckItem[], generatedAt: Date): string {
  const lines: string[] = ['# REV FTC: Autocomplete Check', '', `Generated ${generatedAt.toISOString()}`, ''];
  for (const it of items) {
    lines.push(`## ${STATUS_ICON[it.status]} ${it.label}`, '', it.detail);
    if (it.fix && it.status !== 'pass') {
      lines.push('', `**Fix:** ${it.fix}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}
