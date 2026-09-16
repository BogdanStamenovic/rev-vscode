// Minimal stand-in for the 'vscode' module, used ONLY so hub-smoke.ts can
// import the real src/hub/* and src/settings.ts modules and run them under
// plain node (outside the extension host) against the real hub. It
// implements just enough of the API surface those modules touch:
// vscode.window.createOutputChannel and vscode.workspace.getConfiguration.
// Loaded via NODE_PATH, see test/hub-smoke.ts / package.json script.
'use strict';

function createOutputChannel(name) {
  return {
    appendLine(line) {
      process.stderr.write(`[${name}] ${line}\n`);
    },
    dispose() {},
  };
}

// Optional overrides for ad hoc offline verification scripts (e.g.
// exercising cli.ts against the fake fixture): set REVFTC_SHIM_CONFIG to a
// JSON object of {settingKey: value}. Unset for the hub smoke test, where
// every revFtc.* setting should be "unset" so real connection/adb
// resolution runs.
const overrides = process.env.REVFTC_SHIM_CONFIG ? JSON.parse(process.env.REVFTC_SHIM_CONFIG) : {};

function getConfiguration(_section) {
  return {
    get(key) {
      return overrides[key];
    },
  };
}

class EventEmitter {
  constructor() {
    this._listeners = [];
  }
  event = (listener) => {
    this._listeners.push(listener);
    return { dispose() {} };
  };
  fire(value) {
    for (const l of this._listeners) l(value);
  }
  dispose() {}
}

class Position {
  constructor(line, character) {
    this.line = line;
    this.character = character;
  }
}
class Range {
  constructor(startLine, startChar, endLine, endChar) {
    this.start = new Position(startLine, startChar);
    this.end = new Position(endLine, endChar);
  }
}
const DiagnosticSeverity = { Error: 0, Warning: 1, Information: 2, Hint: 3 };
class Diagnostic {
  constructor(range, message, severity) {
    this.range = range;
    this.message = message;
    this.severity = severity;
  }
}

const Uri = {
  file(fsPath) {
    return { fsPath, toString: () => `file://${fsPath}` };
  },
  parse(s) {
    return { fsPath: s, toString: () => s };
  },
};

module.exports = {
  window: { createOutputChannel },
  workspace: { getConfiguration },
  EventEmitter,
  Position,
  Range,
  Diagnostic,
  DiagnosticSeverity,
  Uri,
};
