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


Hints
-----
- Put `(index, item)` pairs on the queue so each worker knows where its answer goes.
- A sentinel object (`_STOP = object()`) per worker ends a `while True: q.get()` loop.
- Catch exceptions *inside* the worker loop; an escaped exception silently ends the thread.

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
    raise NotImplementedError("TODO")


def process_all(items: list[Any], func: Callable[[Any], Any],
                n_workers: int, maxsize: int) -> tuple[list[Any], int]:
    raise NotImplementedError("TODO")


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
