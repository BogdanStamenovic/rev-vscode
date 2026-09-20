// Generic "debounce, then run at most one task at a time, cancel/supersede
// whatever's in flight rather than queue behind it" scheduler. Factored out
// of liveDiagnostics.ts so the concurrency policy itself - the part with the
// real edge cases (a trigger arriving mid-run, two triggers landing in the
// same debounce window, a run's result arriving after it's already been
// superseded) - has no vscode dependency and can be unit tested directly
// under node with real timers, rather than mocked through half of vscode's
// document-event API.
export interface DebouncedRunnerOptions {
  /** Called for any error `task` throws/rejects with, INCLUDING an abort -
   * callers that care about telling "cancelled" apart from "really failed"
   * (see liveDiagnostics.ts) check the error's type themselves. */
  onError?: (err: unknown) => void;
}

export class DebouncedRunner {
  private debounceTimer: ReturnType<typeof setTimeout> | undefined;
  private running = false;
  private rerunRequested = false;
  private generation = 0;
  private currentAbort: AbortController | undefined;

  constructor(
    /** `generation` is the run's own sequence number - if it no longer
     * equals `currentGeneration()` by the time an await inside `task`
     * resolves, this run has been superseded and should discard its
     * result rather than act on it. */
    private readonly task: (signal: AbortSignal, generation: number) => Promise<void>,
    private readonly opts: DebouncedRunnerOptions = {}
  ) {}

  /** (Re)starts the debounce timer. A call while a timer is already pending
   * replaces it - the classic debounce behavior needed to coalesce a rapid
   * burst (e.g. "Save All" firing N onDidSave events) into one run. */
  schedule(delayMs: number): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(() => {
      this.debounceTimer = undefined;
      void this.trigger();
    }, delayMs);
  }

  /** The generation number of the most recently started run - `task` should
   * compare its own `generation` argument against this after any `await` to
   * detect having been superseded. */
  currentGeneration(): number {
    return this.generation;
  }

  private async trigger(): Promise<void> {
    if (this.running) {
      // Never run twice concurrently: abort what's running and let its
      // `finally` below start a fresh run once the abort is observed,
      // rather than queuing this request behind a stale one.
      this.rerunRequested = true;
      this.currentAbort?.abort();
      return;
    }

    this.running = true;
    const generation = ++this.generation;
    this.currentAbort = new AbortController();
    try {
      await this.task(this.currentAbort.signal, generation);
    } catch (err) {
      this.opts.onError?.(err);
    } finally {
      this.running = false;
      this.currentAbort = undefined;
      if (this.rerunRequested) {
        this.rerunRequested = false;
        void this.trigger();
      }
    }
  }

  /** Runs immediately, bypassing the debounce timer (still subject to the
   * "never twice concurrently" rule above). Not currently used by
   * liveDiagnostics.ts, but kept symmetrical with schedule() for tests and
   * any future caller that wants an un-debounced first run. */
  runNow(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = undefined;
    }
    void this.trigger();
  }

  dispose(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = undefined;
    }
    this.currentAbort?.abort();
  }
}
