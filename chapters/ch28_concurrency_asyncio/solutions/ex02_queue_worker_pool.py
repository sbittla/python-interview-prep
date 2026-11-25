"""
Exercise 02 — Producer–Consumer Worker Pool with queue.Queue   [Tier: ★ Core]
Chapter 28 · Pattern: thread-safe queue, sentinels, backpressure · Target time: 25 min

Problem
-------
Write `process_all(items, func, n_workers, maxsize)` that applies `func` to every item using
`n_workers` threads fed by one producer through a `queue.Queue(maxsize)`.

- Return a list in **input order**: `func(item)`, or the string `"error: <ExcType>: <msg>"`
  when `func` raises (one bad item must not kill a worker or the run).
- Shut down cleanly: one sentinel per worker, every thread joined.
- `peak` (second return value) is the largest queue size the producer saw right after a
  `put`; it must never exceed `maxsize`.

Examples
--------
>>> process_all([1, 2, 3], lambda x: x * 10, n_workers=2, maxsize=1)[0]
[10, 20, 30]
>>> process_all([1, 0], lambda x: 1 // x, n_workers=2, maxsize=4)[0]
[1, 'error: ZeroDivisionError: integer division or modulo by zero']

Constraints
-----------
- 0 <= len(items) <= 10**4, 1 <= n_workers <= 32, maxsize >= 1.
- Results are written by index, so the output does not depend on which worker ran first.

Approach ladder
---------------
1. Brute force — sequential loop: O(n·t) wall time for n items of t seconds of I/O each.
2. Improved   — one thread per item: overlaps I/O but creates n threads (memory, OS limits)
   and has no backpressure if items come from an endless stream.
3. Optimal    — k long-lived workers + bounded queue: wall time ≈ n·t/k for I/O-bound work,
   O(k + maxsize) memory, and the producer blocks on `put` when workers fall behind. CPU-bound
   work gains nothing from threads in the default build (GIL → §27.5): use processes (ex05).

Hints
-----
- Put `(index, item)` pairs on the queue so each worker knows where its answer goes.
- A sentinel object (`_STOP = object()`) per worker ends a `while True: q.get()` loop.
- Catch exceptions *inside* the worker loop. An escaped exception ends that worker: the
  traceback is printed (`threading.excepthook`) but the main thread is not told, its result
  slot stays empty, and with `task_done()`/`join()` the `join()` would hang.

Follow-ups
----------
- `q.task_done()` + `q.join()` waits for the work, but threads still need a stop signal.
- Results needed as soon as they finish? A second (result) queue drained by the caller.
- Priority work: `queue.PriorityQueue` with `(priority, seq, item)` to keep ties FIFO.
"""
from __future__ import annotations

import queue
import threading
from typing import Any, Callable

_STOP = object()


def sequential(items: list[Any], func: Callable[[Any], Any]) -> list[Any]:
    out = []
    for item in items:
        try:
            out.append(func(item))
        except Exception as exc:
            out.append(f"error: {type(exc).__name__}: {exc}")
    return out


def process_all(items: list[Any], func: Callable[[Any], Any],
                n_workers: int, maxsize: int) -> tuple[list[Any], int]:
    q: queue.Queue = queue.Queue(maxsize=maxsize)
    results: list[Any] = [None] * len(items)

    def worker() -> None:
        while True:
            job = q.get()                      # blocks until an item or a sentinel arrives
            if job is _STOP:
                return
            i, item = job
            try:
                results[i] = func(item)
            except Exception as exc:           # one bad item must not kill the worker
                results[i] = f"error: {type(exc).__name__}: {exc}"

    threads = [threading.Thread(target=worker) for _ in range(n_workers)]
    for t in threads:
        t.start()
    peak = 0
    for job in enumerate(items):
        q.put(job)                             # blocks while the queue is full: backpressure
        peak = max(peak, q.qsize())
    for _ in threads:
        q.put(_STOP)                           # one sentinel per worker
    for t in threads:
        t.join()
    return results, peak


def slow_square(x: int) -> int:  # given
    threading.Event().wait(0.002)              # stand-in for a short blocking I/O call
    if x == 13:
        raise ValueError("unlucky")
    return x * x


def main() -> None:
    items = list(range(20))
    res, peak = process_all(items, slow_square, n_workers=4, maxsize=3)
    print("results:", res)
    print("same as sequential:", res == sequential(items, slow_square))
    print("backlog never above maxsize=3:", peak <= 3)
    print("empty input:", process_all([], slow_square, n_workers=3, maxsize=1))
    print("1 worker, maxsize 1:", process_all([1, 2, 3], slow_square, 1, 1)[0])


if __name__ == "__main__":
    main()
