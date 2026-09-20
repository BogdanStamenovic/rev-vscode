#!/usr/bin/env bash
# Ownbox lifecycle for rev-vscode: setup | update | remove.
#
# Two independent halves:
#   1. The `pyftc` CLI: a venv in the checkout with python/ installed editable,
#      so `pyftc translate-project --root .` etc. work standalone (used by
#      anything that wants the translator without VS Code at all).
#   2. The VS Code extension: `npm ci && npm run package`, then installed into
#      the user's `code` with the CLI's `--install-extension`.
#
# Half 2 is optional and degrades honestly: missing npm/node or a missing
# `code` CLI is reported plainly and setup still succeeds, because half 1
# alone is a complete, working tool. What never happens is claiming the
# extension got installed when it did not.
#
# Environment knobs:
#   REV_VSCODE_SKIP_CODE_INSTALL=1   build the .vsix but never call
#                                    `code --install-extension` (non-interactive
#                                    or test runs, or CI without a real VS Code)
set -euo pipefail

here=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$here"

action=${1:-}
venv=.venv
vsix=extension/dist/rev-vscode.vsix
extension_id=bogdanstamenovic.rev-vscode

say() { printf 'rev-vscode: %s\n' "$*" >&2; }

setup_venv() {
  local py=/usr/bin/python3
  [ -x "$py" ] || py=$(command -v python3) || { say "python3 not found on PATH"; exit 1; }
  if [ ! -x "$venv/bin/python" ]; then
    "$py" -m venv "$venv"
  fi
  # Editable: pyftc is stdlib-only, and this way `ownbox update`'s git pull is
  # enough to pick up translator changes without a reinstall.
  "$venv/bin/python" -m pip install --quiet --upgrade pip
  "$venv/bin/python" -m pip install --quiet -e ./python
  say "pyftc CLI ready: $venv/bin/pyftc"
}

# Builds the .vsix. Prints why and returns 1 (never exits the script) when
# npm/node are missing, so callers can skip the rest of the extension half
# without failing the whole install.
build_extension() {
  if ! command -v npm >/dev/null 2>&1 || ! command -v node >/dev/null 2>&1; then
    say "npm/node not found on PATH; skipping the VS Code extension"
    say "the pyftc CLI above still works standalone; install Node.js and re-run"
    say "'./ownbox.sh $action' to also get the extension"
    return 1
  fi
  (cd extension && npm ci && npm run package)
  [ -f "$vsix" ] || { say "npm run package did not produce $vsix"; exit 1; }
  say "extension built: $here/$vsix"
}

# Installs/updates the .vsix into the user's real VS Code, or says exactly
# what to run by hand. Never fails the script either way.
install_extension() {
  if [ "${REV_VSCODE_SKIP_CODE_INSTALL:-0}" = 1 ]; then
    say "REV_VSCODE_SKIP_CODE_INSTALL=1: not touching the local VS Code install"
    say "run this yourself when ready: code --install-extension $here/$vsix"
    return 0
  fi
  if ! command -v code >/dev/null 2>&1; then
    say "the 'code' CLI is not on PATH; VS Code was not updated"
    say "open VS Code, run 'Shell Command: Install code command in PATH', or install by hand:"
    say "  code --install-extension $here/$vsix"
    return 0
  fi
  code --install-extension "$vsix" --force >&2
  say "installed into VS Code: $extension_id"
}

case $action in
  setup|update)
    setup_venv
    if build_extension; then
      install_extension
    fi
    ;;
  remove)
    if command -v code >/dev/null 2>&1; then
      code --uninstall-extension "$extension_id" >&2 || say "extension was not installed in VS Code"
    else
      say "'code' CLI not on PATH; if the extension is still installed, remove it from VS Code by hand"
    fi
    say "removed. Ownbox deletes the checkout (and the venv inside it) itself."
    ;;
  *)
    say "usage: ownbox.sh setup|update|remove"; exit 2
    ;;
esac
