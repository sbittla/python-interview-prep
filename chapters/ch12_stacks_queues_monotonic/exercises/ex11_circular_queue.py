"""
Exercise 11 — Fixed-Capacity Circular Queue                   [Tier: ◆ Extended]
Chapter 12 · Pattern: ring buffer with modular indices · Target time: 20 min

Problem
-------
Design ``CircularQueue(capacity)`` backed by a pre-allocated list of length ``capacity``:

- ``enqueue(x) -> bool``  add at the rear; return ``False`` (and change nothing) if full
- ``dequeue() -> x``      remove and return the front; ``IndexError`` if empty
- ``front()`` / ``rear()`` peek at either end; ``IndexError`` if empty
- ``is_empty()``, ``is_full()``, ``__len__``

All operations O(1); no list growth or shifting after construction. ``capacity >= 1``.

Examples
--------
>>> q = CircularQueue(2); q.enqueue(1), q.enqueue(2), q.enqueue(3)
(True, True, False)
>>> q.dequeue(), q.enqueue(3), q.front(), q.rear()
(1, True, 2, 3)

Constraints
-----------
- 1 <= capacity <= 10**5; up to 10**5 operations.

Hints
-----
- Keep head and size instead of head and tail; derive the other end with % capacity.
- Empty is size == 0, full is size == capacity.

Wrong-but-tempting
------------------
- ``rear`` as ``data[tail - 1]`` without wrapping: Python's negative index happens to work
  for ``tail == 0``, which hides the bug in languages without negative indexing.
- ``collections.deque(maxlen=cap)``: when full it silently *drops the oldest* item instead
  of rejecting the new one.
- Not clearing the dequeued slot: harmless for ints, but keeps large objects alive.

Follow-ups
----------
- Circular deque (insert/delete at both ends): decrement ``head`` with ``(head - 1) % cap``.
- Overwrite-oldest mode (a log ring buffer): when full, advance ``head`` before writing.
- Thread-safe bounded queue: ``queue.Queue(maxsize)`` blocks instead of returning False.
"""
from __future__ import annotations

from typing import Any


class NaiveBoundedQueue:
    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    def enqueue(self, x: Any) -> bool:
        raise NotImplementedError("TODO")

    def dequeue(self) -> Any:
        raise NotImplementedError("TODO")

    def front(self) -> Any:
        raise NotImplementedError("TODO")

    def rear(self) -> Any:
        raise NotImplementedError("TODO")

    def is_empty(self) -> bool:
        raise NotImplementedError("TODO")

    def is_full(self) -> bool:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


class CircularQueue:
    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    def enqueue(self, x: Any) -> bool:
        raise NotImplementedError("TODO")

    def dequeue(self) -> Any:
        raise NotImplementedError("TODO")

    def front(self) -> Any:
        raise NotImplementedError("TODO")

    def rear(self) -> Any:
        raise NotImplementedError("TODO")

    def is_empty(self) -> bool:
        raise NotImplementedError("TODO")

    def is_full(self) -> bool:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


def main() -> None:
    q = CircularQueue(3)
    script = [("enqueue", 1), ("enqueue", 2), ("enqueue", 3), ("enqueue", 4), ("dequeue",),
              ("enqueue", 4), ("rear",), ("dequeue",), ("dequeue",), ("enqueue", 5), ("front",)]
    for op in script:
        result = getattr(q, op[0])(*op[1:])
        label = f"{op[0]}({', '.join(map(str, op[1:]))})"
        print(f"{label:<12} -> {result!s:<5} slots={q._data} head={q._head} size={len(q)}")
    print(f"full={q.is_full()} empty={q.is_empty()}")
    from collections import deque
    d = deque([1, 2, 3], maxlen=3)
    d.append(4)
    print(f"deque(maxlen=3) after append(4): {list(d)}  (oldest silently dropped)")


if __name__ == "__main__":
    main()
