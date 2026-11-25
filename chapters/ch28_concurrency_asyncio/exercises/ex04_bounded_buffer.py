"""
Exercise 04 — Bounded Blocking Buffer from a Lock and Conditions   [Tier: ★ Core]
Chapter 28 · Pattern: Condition variables, wait in a loop · Target time: 30 min

Problem
-------
Implement `BoundedBuffer(capacity)` without using `queue.Queue`:

- `put(item, timeout=None)` blocks while the buffer is full; `get(timeout=None)` blocks while
  it is empty and returns items in FIFO order.
- With a timeout, give up after `timeout` seconds and raise `TimeoutError`.
- `max_seen` records the largest size ever reached (it must never exceed `capacity`).

Then `run_pipeline(n_producers, per_producer, n_consumers, capacity)` starts the threads,
sends `(producer_id, seq)` items, stops consumers with one `None` sentinel each, and returns
`(sorted(consumed), buffer.max_seen)`.

Examples
--------
>>> b = BoundedBuffer(2); b.put("a"); b.put("b"); b.get(), b.get()
('a', 'b')
>>> BoundedBuffer(1).get(timeout=0.01)
Traceback (most recent call last):
TimeoutError: buffer empty

Constraints
-----------
- capacity >= 1; any number of producer and consumer threads.


Hints
-----
- Always `while not ready: cv.wait()`, never `if`: another thread may take the slot between the
  notify and your wake-up, and spurious wake-ups are allowed.
- `Condition.wait_for(predicate, timeout)` runs that loop for you and returns the predicate.
- Both conditions must share the lock that protects the deque.

Follow-ups
----------
- Add `close()` so blocked getters wake up and see "no more items".
- `queue.Queue` is this design (plus `task_done`/`join`); prefer it in real code.
- asyncio version: `asyncio.Queue(maxsize)` (ex10) uses the same idea without threads.
"""
from __future__ import annotations

import threading
from collections import deque
from typing import Any


class BoundedBuffer:
    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    def put(self, item: Any, timeout: float | None = None) -> None:
        raise NotImplementedError("TODO")

    def get(self, timeout: float | None = None) -> Any:
        raise NotImplementedError("TODO")


def run_pipeline(n_producers: int, per_producer: int, n_consumers: int,
                 capacity: int) -> tuple[list[tuple[int, int]], int]:
    raise NotImplementedError("TODO")


def main() -> None:
    b = BoundedBuffer(2)
    b.put("a")
    b.put("b")
    try:
        b.put("c", timeout=0.01)
    except TimeoutError as exc:
        print("put on full buffer:", exc)
    print("FIFO:", b.get(), b.get())
    try:
        b.get(timeout=0.01)
    except TimeoutError as exc:
        print("get on empty buffer:", exc)
    items, peak = run_pipeline(n_producers=3, per_producer=200, n_consumers=2, capacity=4)
    expected = sorted((p, s) for p in range(3) for s in range(200))
    print("all 600 items consumed exactly once:", items == expected)
    print("size never above capacity 4:", 1 <= peak <= 4)
    items, peak = run_pipeline(1, 50, 1, capacity=1)
    print("capacity 1, 1x1 threads:", len(items), "items, max size", peak)


if __name__ == "__main__":
    main()
