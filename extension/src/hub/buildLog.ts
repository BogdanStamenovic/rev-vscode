// Pure parser for `GET /java/build/log`, e.g.:
//
//   org/.../DeploySpike.java(11:18): ERROR: cannot find symbol
//     symbol:   method updat()
//     location: variable telemetry of type org.firstinspires.ftc.robotcore.external.Telemetry
//   org/.../DeploySpike.java(12:17): ERROR: incompatible types: java.lang.String cannot be converted to int
//
// No vscode/fetch dependency so it can be unit tested directly under node.

export interface BuildLogError {
  /** Canonical path, e.g. "org/firstinspires/ftc/teamcode/pyftc/DeploySpike.java" (no leading slash). */
  file: string;
  line: number;
  col: number;
  severity: 'error' | 'warning';
  message: string;
  /** Indented continuation lines (javac's "symbol:"/"location:" detail), trimmed. */
  continuation: string[];
}

const HEADER_RE = /^(\S+)\((\d+):(\d+)\):\s+(ERROR|WARNING):\s+(.*)$/;

export function parseBuildLog(log: string): BuildLogError[] {
  const errors: BuildLogError[] = [];
  const lines = log.split(/\r?\n/);
  let current: BuildLogError | null = null;

  for (const rawLine of lines) {
    if (rawLine.length === 0) {
      continue;
    }
    const match = HEADER_RE.exec(rawLine);
    if (match) {
      const [, file, lineStr, colStr, sev, message] = match;
      current = {
        file,
        line: parseInt(lineStr, 10),
        col: parseInt(colStr, 10),
        severity: sev === 'ERROR' ? 'error' : 'warning',
        message,
        continuation: [],
      };
      errors.push(current);
    } else if (current && /^\s+/.test(rawLine)) {
      // Continuation line (javac detail) belonging to the previous header.
      current.continuation.push(rawLine.trim());
    }
    // A non-indented, non-header line with no current error is stray output;
    // ignore rather than throw, since a build log that fails to parse
    // perfectly should still surface whatever we could extract.
  }

  return errors;
}

/** Full human-readable message: header + continuation lines joined. */
export function formatBuildLogError(err: BuildLogError): string {
  if (err.continuation.length === 0) {
    return err.message;
  }
  return [err.message, ...err.continuation].join('\n');
}
