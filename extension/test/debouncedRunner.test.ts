import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DebouncedRunner } from '../src/debouncedRunner';

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

test('DebouncedRunner: coalesces multiple schedule() calls within the window into one run', async () => {
  let calls = 0;
  const runner = new DebouncedRunner(async () => {
    calls++;
  });
  runner.schedule(15);
  runner.schedule(15);
  runner.schedule(15);
  await sleep(60);
  assert.equal(calls, 1);
});

test('DebouncedRunner: a schedule() after the previous run finished starts a new run', async () => {
  let calls = 0;
  const runner = new DebouncedRunner(async () => {
    calls++;
  });
  runner.schedule(5);
  await sleep(40);
  assert.equal(calls, 1);
  runner.schedule(5);
  await sleep(40);
  assert.equal(calls, 2);
});

test('DebouncedRunner: never runs two tasks concurrently - a trigger mid-run aborts it and reruns after, never overlaps', async () => {
  const events: string[] = [];
  let callCount = 0;
  const runner = new DebouncedRunner(async (signal) => {
    callCount++;
    const myCall = callCount;
    events.push(`start-${myCall}`);
    if (myCall === 1) {
      // Blocks until either aborted (by the second trigger) or a safety
      // timeout - never itself, so we can observe "start-1" alone first.
      await new Promise<void>((resolve) => {
        signal.addEventListener('abort', () => resolve());
      });
    }
    events.push(`end-${myCall}`);
  });

  runner.schedule(5);
  await sleep(40); // let run 1 actually start and block on its promise
  assert.deepEqual(events, ['start-1']);

  runner.schedule(5); // should abort run 1 and rerun once it actually stops
  await sleep(80);
  assert.deepEqual(events, ['start-1', 'end-1', 'start-2', 'end-2']);
});

test('DebouncedRunner: currentGeneration() increments by one per run, so a task can detect being superseded', async () => {
  const generations: number[] = [];
  const runner = new DebouncedRunner(async (_signal, generation) => {
    generations.push(generation);
  });
  runner.schedule(5);
  await sleep(30);
  runner.schedule(5);
  await sleep(30);
  runner.schedule(5);
  await sleep(30);
  assert.deepEqual(generations, [1, 2, 3]);
  assert.equal(runner.currentGeneration(), 3);
});

test('DebouncedRunner: onError receives whatever the task throws (including an abort)', async () => {
  const errors: unknown[] = [];
  const runner = new DebouncedRunner(
    async () => {
      throw new Error('boom');
    },
    { onError: (err) => errors.push(err) }
  );
  runner.schedule(5);
  await sleep(30);
  assert.equal(errors.length, 1);
  assert.equal((errors[0] as Error).message, 'boom');
});

test('DebouncedRunner: an error in one run does not stop a later schedule() from running', async () => {
  let calls = 0;
  const runner = new DebouncedRunner(
    async () => {
      calls++;
      if (calls === 1) {
        throw new Error('first run fails');
      }
    },
    { onError: () => undefined }
  );
  runner.schedule(5);
  await sleep(30);
  runner.schedule(5);
  await sleep(30);
  assert.equal(calls, 2);
});

test('DebouncedRunner: dispose() cancels a pending (not yet fired) debounce timer', async () => {
  let calls = 0;
  const runner = new DebouncedRunner(async () => {
    calls++;
  });
  runner.schedule(20);
  runner.dispose();
  await sleep(50);
  assert.equal(calls, 0);
});

test('DebouncedRunner: dispose() aborts a currently running task', async () => {
  let aborted = false;
  const runner = new DebouncedRunner(async (signal) => {
    await new Promise<void>((resolve) => {
      signal.addEventListener('abort', () => {
        aborted = true;
        resolve();
      });
    });
  });
  runner.schedule(5);
  await sleep(30);
  runner.dispose();
  await sleep(30);
  assert.equal(aborted, true);
});

test('DebouncedRunner: runNow() bypasses the debounce delay', async () => {
  let calls = 0;
  const runner = new DebouncedRunner(async () => {
    calls++;
  });
  runner.runNow();
  await sleep(10);
  assert.equal(calls, 1);
});
