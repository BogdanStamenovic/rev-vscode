// "Where did execution go": in every visible editor showing a simulated .py
// file, the lines that ran in the last loop iteration get a highlight and a
// gutter bar, the others are left as they are, and each line that assigned a
// local shows its new value at the end of the line, like a debugger's inline
// values.
import * as vscode from 'vscode';
import type { TraceView } from './protocol';

export class TraceDecorations implements vscode.Disposable {
  private readonly ran = vscode.window.createTextEditorDecorationType({
    isWholeLine: true,
    backgroundColor: new vscode.ThemeColor('editor.wordHighlightBackground'),
    overviewRulerColor: new vscode.ThemeColor('editorOverviewRuler.infoForeground'),
    overviewRulerLane: vscode.OverviewRulerLane.Left,
    borderWidth: '0 0 0 3px',
    borderStyle: 'solid',
    borderColor: new vscode.ThemeColor('editorInfo.foreground'),
  });
  private readonly value = vscode.window.createTextEditorDecorationType({});
  private current: TraceView | undefined;
  private readonly sub: vscode.Disposable;

  constructor() {
    this.sub = vscode.window.onDidChangeVisibleTextEditors(() => this.redraw());
  }

  show(view: TraceView): void {
    this.current = view;
    this.redraw();
  }

  clear(): void {
    this.current = undefined;
    this.redraw();
  }

  private redraw(): void {
    for (const editor of vscode.window.visibleTextEditors) {
      const file = editor.document.uri.fsPath;
      const lines = this.current?.lines.get(file) ?? [];
      const max = editor.document.lineCount;
      editor.setDecorations(this.ran, lines.filter((l) => l >= 1 && l <= max).map((l) => new vscode.Range(l - 1, 0, l - 1, 0)));
      const values = this.current?.values.get(file);
      const opts: vscode.DecorationOptions[] = [];
      if (values) {
        for (const [line, text] of values) {
          if (line < 1 || line > max) continue;
          const end = editor.document.lineAt(line - 1).range.end;
          opts.push({
            range: new vscode.Range(end, end),
            renderOptions: { after: { contentText: `  ◂ ${text}`, color: new vscode.ThemeColor('editorCodeLens.foreground'), fontStyle: 'italic' } },
          });
        }
      }
      editor.setDecorations(this.value, opts);
    }
  }

  dispose(): void {
    this.sub.dispose();
    this.ran.dispose();
    this.value.dispose();
  }
}
