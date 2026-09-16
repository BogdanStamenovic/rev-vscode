// Maps a javac error line (in generated Java) back to the .py source line,
// using the per-class `lineMap` from Contract 3: lineMap[javaLine - 1] =
// python line (1-based), 0 = synthetic (no direct source line).

export interface MappedLine {
  /** 1-based python line to point the diagnostic at. */
  pythonLine: number;
  /** True when the map gave 0 or was out of range, so pythonLine is a
   * best-effort fallback (line 1) rather than a real mapping. */
  fallback: boolean;
}

export function mapJavaLineToPython(lineMap: number[], javaLine: number): MappedLine {
  const idx = javaLine - 1;
  const mapped = idx >= 0 && idx < lineMap.length ? lineMap[idx] : 0;
  if (mapped > 0) {
    return { pythonLine: mapped, fallback: false };
  }
  return { pythonLine: 1, fallback: true };
}
