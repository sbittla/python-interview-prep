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

Approach ladder
---------------
1. Brute force — lock + polling: `while full: release; sleep(0.001); reacquire`. Burns CPU and
   adds up to one sleep of latency per hand-off.
2. Improved   — one `Condition`, wait while full/empty, `notify_all()` after each change:
   correct, but every put also wakes every waiting producer (thundering herd).
3. Optimal    — one lock shared by two conditions, `not_full` and `not_empty`; `put` notifies
   only `not_empty`, `get` only `not_full`. O(1) per operation (deque), one targeted wake-up.

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
        self.capacity = capacity
        self._items: deque[Any] = deque()
        lock = threading.Lock()
        self._not_full = threading.Condition(lock)    # two conditions, one lock
        self._not_empty = threading.Condition(lock)
        self.max_seen = 0

    def put(self, item: Any, timeout: float | None = None) -> None:
        with self._not_full:
            if not self._not_full.wait_for(lambda: len(self._items) < self.capacity, timeout):
                raise TimeoutError("buffer full")
            self._items.append(item)
            self.max_seen = max(self.max_seen, len(self._items))
            self._not_empty.notify()                   # wake one consumer

    def get(self, timeout: float | None = None) -> Any:
        with self._not_empty:
            if not self._not_empty.wait_for(lambda: len(self._items) > 0, timeout):
                raise TimeoutError("buffer empty")
            item = self._items.popleft()
            self._not_full.notify()                    # wake one producer
            return item


def run_pipeline(n_producers: int, per_producer: int, n_consumers: int,
                 capacity: int) -> tuple[list[tuple[int, int]], int]:
    buf = BoundedBuffer(capacity)
    consumed: list[tuple[int, int]] = []
    consumed_lock = threading.Lock()

    def producer(pid: int) -> None:
        for seq in range(per_producer):
            buf.put((pid, seq))

    def consumer() -> None:
        while (item := buf.get()) is not None:
            with consumed_lock:
                consumed.append(item)

    producers = [threading.Thread(target=producer, args=(p,)) for p in range(n_producers)]
    consumers = [threading.Thread(target=consumer) for _ in range(n_consumers)]
    for t in producers + consumers:
        t.start()
    for t in producers:
        t.join()
    for _ in consumers:
        buf.put(None)                                  # sentinel per consumer, after all data
    for t in consumers:
        t.join()
    return sorted(consumed), buf.max_seen


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
