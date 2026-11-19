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

Approach ladder
---------------
1. Brute force — a Python list with a length check, ``append`` and ``pop(0)``. Correct, but
   dequeue is O(n) and memory is reallocated as the list grows and shrinks.
2. Head + tail pointers — ``head`` (next to dequeue) and ``tail`` (next free slot), both
   advanced with ``% capacity``. Problem: ``head == tail`` means *both* empty and full.
   The classic fix wastes one slot (allocate ``capacity + 1``).
3. Optimal    — store ``head`` and ``size``; the rear slot is ``(head + size - 1) % cap`` and
   the next free slot is ``(head + size) % cap``. Empty is ``size == 0``, full is
   ``size == cap`` — no ambiguity, no wasted slot. O(1) every operation, O(capacity) space.
   Why move up: rung 3 removes the empty/full ambiguity with a single counter.

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
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._cap = capacity
        self._items: list[Any] = []

    def enqueue(self, x: Any) -> bool:
        if len(self._items) == self._cap:
            return False
        self._items.append(x)
        return True

    def dequeue(self) -> Any:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def front(self) -> Any:
        if not self._items:
            raise IndexError("front of empty queue")
        return self._items[0]

    def rear(self) -> Any:
        if not self._items:
            raise IndexError("rear of empty queue")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def is_full(self) -> bool:
        return len(self._items) == self._cap

    def __len__(self) -> int:
        return len(self._items)


class CircularQueue:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._data: list[Any] = [None] * capacity
        self._head = 0                          # index of the front element
        self._size = 0

    def enqueue(self, x: Any) -> bool:
        if self._size == len(self._data):
            return False
        self._data[(self._head + self._size) % len(self._data)] = x
        self._size += 1
        return True

    def dequeue(self) -> Any:
        if self._size == 0:
            raise IndexError("dequeue from empty queue")
        x = self._data[self._head]
        self._data[self._head] = None           # release the reference
        self._head = (self._head + 1) % len(self._data)
        self._size -= 1
        return x

    def front(self) -> Any:
        if self._size == 0:
            raise IndexError("front of empty queue")
        return self._data[self._head]

    def rear(self) -> Any:
        if self._size == 0:
            raise IndexError("rear of empty queue")
        return self._data[(self._head + self._size - 1) % len(self._data)]

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == len(self._data)

    def __len__(self) -> int:
        return self._size


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
