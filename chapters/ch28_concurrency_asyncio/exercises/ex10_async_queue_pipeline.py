"""
Exercise 10 — Async Producer–Consumer Pipeline with asyncio.Queue   [Tier: ★ Core]
Chapter 28 · Pattern: bounded asyncio.Queue, k workers, join + cancel shutdown · Target time: 30 min

Problem
-------
A producer emits `n_items` jobs (job i "arrives" every `arrival` seconds). `n_workers`
consumers each take a job, spend `work` seconds on it, and record `(i, i * i)`.

Write `pipeline(n_items, n_workers, maxsize, arrival, work)` that connects them with an
`asyncio.Queue(maxsize)` and returns `(sorted_results, peak_queue_size, elapsed)`:

- the producer must block (`await q.put`) when the queue is full: memory stays O(maxsize);
- shut down with `await q.join()` (every job's `task_done()` was called), then cancel the
  idle workers and await them;
- a job whose number is in `poison` raises inside the worker; record `(i, "error")` and keep
  the worker alive (call `task_done()` in a `finally`).

Runs on the virtual clock (`vclock.run_virtual`), so `elapsed` is exact.

Examples
--------
>>> run_virtual(pipeline(4, 2, maxsize=1, arrival=0, work=1.0))
([(0, 0), (1, 1), (2, 4), (3, 9)], 1, 2.0)

Constraints
-----------
- n_items <= 10**4, n_workers >= 1, maxsize >= 1 (maxsize 0 would mean unbounded).


Hints
-----
- `q.join()` returns once the count of unfinished jobs hits 0; it does not stop workers.
- Workers blocked in `await q.get()` are cancelled cleanly by `task.cancel()`.
- Alternatively, push one sentinel per worker after the last job (as in ex02).

Follow-ups
----------
- Multi-stage pipeline: chain queues; size each stage's worker count by its service time.
- A consumer crashes outright: `TaskGroup` (3.11+) or a supervisor that restarts it.
- Ordered output while processing out of order: a min-heap re-sequencer keyed by i.
"""
from __future__ import annotations

import asyncio

from vclock import run_virtual


async def pipeline(n_items: int, n_workers: int, maxsize: int, arrival: float, work: float,
                   poison: frozenset[int] = frozenset()) -> tuple[list, int, float]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("4 items, 2 workers:", run_virtual(pipeline(4, 2, maxsize=1, arrival=0, work=1.0)))
    for workers in (1, 2, 4):
        res, peak, secs = run_virtual(pipeline(8, workers, maxsize=2, arrival=0.1, work=0.4))
        print(f"8 items, arrival 0.1 s, work 0.4 s, {workers} worker(s): "
              f"elapsed {secs} s, peak queue {peak}")
    res, peak, secs = run_virtual(pipeline(5, 2, maxsize=2, arrival=0, work=0.5,
                                           poison=frozenset({3})))
    print("with poison job 3:", res)
    print("no items:", run_virtual(pipeline(0, 3, maxsize=1, arrival=0, work=1)))


if __name__ == "__main__":
    main()
