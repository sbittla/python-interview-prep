# Chapter 28 — Concurrency and asyncio

Manuscript: `manuscript/ch28_concurrency_asyncio.md`. Standard library only
(`threading`, `queue`, `concurrent.futures`, `multiprocessing`, `asyncio`).

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Lost updates and the lock that fixes them | ★ Core | `Lock`, read-modify-write, check-then-act, sharding | 28.2 |
| ex02 | Producer–consumer worker pool | ★ Core | `queue.Queue(maxsize)`, sentinels, backpressure | 28.3 |
| ex03 | Print in order, ping-pong, zero-even-odd | ★ Core | `Event` / `Semaphore` hand-off | 28.11 |
| ex04 | Bounded blocking buffer | ★ Core | one lock, two `Condition`s, `wait_for` | 28.2, 28.11 |
| ex05 | Thread and process pools | ◆ Extended | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `map` vs `as_completed` | 28.1, 28.4 |
| ex06 | Coroutines, gather and as_completed | ★ Core | overlap waits on one loop, `return_exceptions` | 28.5, 28.6 |
| ex07 | Timeouts, cancellation, fail-fast groups | ◆ Extended | `wait_for`, `asyncio.timeout` (3.11+), `TaskGroup` (3.11+), `wait(FIRST_EXCEPTION)` | 28.6, 28.7 |
| ex08 | Bounded concurrency | ★ Core | `asyncio.Semaphore`, k-worker pool | 28.8 |
| ex09 | Blocking call freezes the loop | ◆ Extended | `to_thread`, `run_in_executor`, process pool from async | 28.9 |
| ex10 | Async producer–consumer pipeline | ★ Core | bounded `asyncio.Queue`, `join` + cancel shutdown | 28.10 |
| ex11 | Retry with timeout and backoff | ◆ Extended | `wait_for` per attempt, exponential backoff + full jitter | 28.7 |

## How to run

```bash
.venv/Scripts/python chapters/ch28_concurrency_asyncio/solutions/ex08_semaphore_limit.py
.venv/Scripts/python -m pytest chapters/ch28_concurrency_asyncio                  # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch28_concurrency_asyncio # your stubs
.venv/Scripts/python tools/run_all.py --chapter 28                                # regenerate outputs/
.venv/Scripts/python tools/run_all.py --chapter 28 --check                        # determinism check
```

## Determinism

Concurrency output is byte-identical on every run:

- Results are stored by index or key and printed in input order, never completion order
  (the exception is ex06 `as_completed`, whose order is forced by distinct virtual delays).
- Race demos force the bad interleaving with a `threading.Barrier`, then print a boolean
  or a forced value instead of a racy count.
- The async exercises ex06–ex08 and ex10–ex11 run on **`vclock.run_virtual`**, a helper in
  `solutions/` (copied into `exercises/`). It runs an event loop whose clock jumps to the next
  timer instead of sleeping, so `asyncio.sleep`, `wait_for`, `asyncio.timeout` and `loop.time()`
  give exact timings in no real time. Do not use it with threads or real I/O.
- ex09 needs real threads, so it uses `asyncio.run`. Its outputs come from `threading.Event`
  hand-offs, not from timing.

## Windows / multiprocessing notes

ex05 and ex09 create a `ProcessPoolExecutor`. Windows and macOS use the *spawn* start
method, so the worker functions are top-level and the pools are created under
`if __name__ == "__main__":`. Under pytest the `load` fixture imports each solution under a
name that child processes cannot import. The process-pool tests therefore run the file as a
script in a subprocess, and the in-process tests use `ThreadPoolExecutor`.

Each solution docstring holds the full statement, approach ladder, hints and follow-ups. The
`exercises/` copies keep everything except the ladder, and their bodies are replaced by
`raise NotImplementedError("TODO")`. Helpers marked `# given` are kept. Code is portable to
Python 3.10. Everything that needs 3.11+ (`asyncio.timeout`, `TaskGroup`) is flagged and
skipped on older versions.
