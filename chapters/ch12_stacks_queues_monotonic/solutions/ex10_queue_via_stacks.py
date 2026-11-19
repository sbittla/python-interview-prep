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

Approach ladder
---------------
1. Brute force — one list with ``pop(0)``. Correct but ``pop(0)`` shifts every element:
   O(n) per dequeue (and it is not a stack operation).
2. Eager two stacks — on every push, pour ``out`` back into ``in``, push, pour back. O(n) per
   push.
3. Optimal    — lazy two stacks: push onto ``inbox``; on pop/peek, if ``outbox`` is empty,
   pour *all* of ``inbox`` into ``outbox`` (reversing the order) and pop from ``outbox``.
   Each element is moved at most once in its life (inbox → outbox), so n operations cost
   O(n) total: amortised O(1), worst case O(n) for a single pop.
   Why move up: the lazy version only pays to reverse when it must, and never moves an
   element twice.

Part B ladder: a single deque; after appending ``x``, rotate the older ``len-1`` elements
behind it (``popleft`` + ``append``) so ``x`` is at the front. Push O(n), pop/top O(1). (Making
pop O(n) instead is equally valid; in the standard constructions one side always pays O(n).)

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
        self._items: list[int] = []

    def push(self, x: int) -> None:
        self._items.append(x)

    def pop(self) -> int:
        if not self._items:
            raise IndexError("pop from empty queue")
        return self._items.pop(0)               # O(n) shift

    def peek(self) -> int:
        if not self._items:
            raise IndexError("peek from empty queue")
        return self._items[0]

    def __len__(self) -> int:
        return len(self._items)


class StackQueue:
    def __init__(self) -> None:
        self._inbox: list[int] = []
        self._outbox: list[int] = []
        self.moves = 0

    def push(self, x: int) -> None:
        self._inbox.append(x)

    def _shift(self) -> None:
        if not self._outbox:                    # only refill when empty
            while self._inbox:
                self._outbox.append(self._inbox.pop())
                self.moves += 1
        if not self._outbox:
            raise IndexError("queue is empty")

    def pop(self) -> int:
        self._shift()
        return self._outbox.pop()

    def peek(self) -> int:
        self._shift()
        return self._outbox[-1]

    def __len__(self) -> int:
        return len(self._inbox) + len(self._outbox)


class QueueStack:
    def __init__(self) -> None:
        self._q: deque[int] = deque()

    def push(self, x: int) -> None:
        self._q.append(x)
        for _ in range(len(self._q) - 1):       # rotate older items behind x
            self._q.append(self._q.popleft())

    def pop(self) -> int:
        if not self._q:
            raise IndexError("pop from empty stack")
        return self._q.popleft()

    def top(self) -> int:
        if not self._q:
            raise IndexError("top from empty stack")
        return self._q[0]

    def __len__(self) -> int:
        return len(self._q)


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
