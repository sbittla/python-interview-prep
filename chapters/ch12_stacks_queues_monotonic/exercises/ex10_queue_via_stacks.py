"""
Exercise 10 — Queue via Two Stacks (and Stack via a Queue)   [Tier: ★ Core]
Chapter 12 · Pattern: amortised analysis / adapter design · Target time: 20 min

Problem
-------
Part A. Implement a FIFO ``StackQueue`` using only stack operations on Python lists
(``append``, ``pop()`` from the end, ``[-1]``, ``len``): ``push(x)``, ``pop() -> x``,
``peek() -> x``, ``__len__``. ``pop``/``peek`` on an empty queue raise ``IndexError``. Every
operation must be amortised O(1). Count how many element moves between stacks you perform in
``moves``.

Part B. Implement a LIFO ``QueueStack`` using only queue operations on a ``deque``
(``append``, ``popleft``, ``[0]``, ``len``): ``push``, ``pop``, ``top``, ``__len__``.

Examples
--------
>>> q = StackQueue(); q.push(1); q.push(2); q.pop(); q.push(3); q.pop(), q.pop()
1
(2, 3)

Constraints
-----------
- Up to 10**5 mixed operations.

Hints
-----
- Push onto one stack; pop from the other.
- Only refill the out-stack when it is empty — why does that keep FIFO order?
- Stack via queue: after appending, rotate the older items behind the new one.

Wrong-but-tempting
------------------
- Pouring ``inbox`` into ``outbox`` while ``outbox`` still holds elements: the order breaks.
- Claiming O(1) worst case: one pop after n pushes moves n elements.
- Using ``collections.deque`` for Part A defeats the exercise (it is already a queue).

Follow-ups
----------
- Where is this used? Purely functional (immutable) queues are built from two lists the
  same way.
- Add ``get_min`` to the queue: build it from two min-stacks (exercise 03).
"""
from __future__ import annotations

from collections import deque


class NaiveQueue:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def peek(self) -> int:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


class StackQueue:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def _shift(self) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def peek(self) -> int:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


class QueueStack:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def top(self) -> int:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


def main() -> None:
    q, naive = StackQueue(), NaiveQueue()
    script = [("push", 1), ("push", 2), ("push", 3), ("pop",), ("push", 4), ("pop",), ("pop",),
              ("peek",), ("pop",)]
    for op in script:
        if op[0] == "push":
            q.push(op[1])
            naive.push(op[1])
            print(f"push {op[1]}  inbox={q._inbox} outbox={q._outbox}")
        else:
            a, b = getattr(q, op[0])(), getattr(naive, op[0])()
            print(f"{op[0]:<6} -> {a}  inbox={q._inbox} outbox={q._outbox}  agree={a == b}")
    big = StackQueue()
    for i in range(1000):
        big.push(i)
        if i % 3 == 0:
            big.pop()
    while len(big):
        big.pop()
    print(f"1000 pushes -> moves={big.moves} (each element moved at most once: {big.moves <= 1000})")
    s = QueueStack()
    for x in (1, 2, 3):
        s.push(x)
    print(f"QueueStack pops: {[s.pop() for _ in range(3)]}")
    try:
        StackQueue().pop()
    except IndexError as e:
        print(f"empty pop -> IndexError: {e}")


if __name__ == "__main__":
    main()
