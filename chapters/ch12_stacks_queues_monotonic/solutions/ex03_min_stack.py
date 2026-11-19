"""
Exercise 03 — Min Stack in O(1)                               [Tier: ★ Core]
Chapter 12 · Pattern: augmented stack (store the answer with each entry) · Target time: 15 min

Problem
-------
Design a stack of integers that supports ``push(x)``, ``pop() -> int``, ``top() -> int`` and
``get_min() -> int``, all in O(1) time. ``pop``, ``top`` and ``get_min`` on an empty stack
raise ``IndexError``. Duplicates of the minimum must be handled (push 1, push 1, pop -> min
is still 1).

Examples
--------
>>> s = MinStack(); s.push(5); s.push(2); s.push(7); s.get_min()
2
>>> s.pop(); s.pop(); s.get_min()
7
2
5

Constraints
-----------
- Up to 10**5 operations.

Approach ladder
---------------
1. Brute force — a plain list; ``get_min`` scans it with ``min``. O(1) push/pop, O(n) min.
2. Improved   — keep a second stack of minimums, pushing ``x`` only when ``x <= current
   min`` and popping it when the popped value equals the current min. O(1) everything,
   extra space only for "new minimum" pushes. The ``<=`` (not ``<``) is what makes
   duplicates work.
3. Optimal (simplest to get right) — store ``(value, min_so_far)`` pairs. The minimum of
   the stack below any entry never changes while that entry is on the stack, so caching it
   per entry is always correct. O(1) everything, O(n) extra.
   Why move up: rung 1 fails the O(1) requirement; rung 3 has no ``<=`` vs ``<`` trap.

Wrong-but-tempting
------------------
- One ``self.min`` variable: after popping the minimum you cannot recover the previous one
  without rescanning.
- The two-stack version with ``x < min`` instead of ``x <= min`` breaks on duplicates.

Follow-ups
----------
- Max stack with ``pop_max`` (needs a heap or sorted structure plus lazy deletion).
- O(1) extra space: store ``x - min`` differences and decode on pop (fixed-width trick;
  pointless in Python but a classic follow-up).
"""
from __future__ import annotations


class NaiveMinStack:
    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, x: int) -> None:
        self._items.append(x)

    def pop(self) -> int:
        return self._items.pop()            # list.pop raises IndexError when empty

    def top(self) -> int:
        if not self._items:
            raise IndexError("top from empty stack")
        return self._items[-1]

    def get_min(self) -> int:
        if not self._items:
            raise IndexError("min of empty stack")
        return min(self._items)             # O(n)


class TwoStackMinStack:
    def __init__(self) -> None:
        self._items: list[int] = []
        self._mins: list[int] = []

    def push(self, x: int) -> None:
        self._items.append(x)
        if not self._mins or x <= self._mins[-1]:   # <= keeps duplicate minimums
            self._mins.append(x)

    def pop(self) -> int:
        x = self._items.pop()
        if x == self._mins[-1]:
            self._mins.pop()
        return x

    def top(self) -> int:
        if not self._items:
            raise IndexError("top from empty stack")
        return self._items[-1]

    def get_min(self) -> int:
        if not self._mins:
            raise IndexError("min of empty stack")
        return self._mins[-1]


class MinStack:
    def __init__(self) -> None:
        self._items: list[tuple[int, int]] = []     # (value, min of stack up to here)

    def push(self, x: int) -> None:
        current = min(x, self._items[-1][1]) if self._items else x
        self._items.append((x, current))

    def pop(self) -> int:
        return self._items.pop()[0]

    def top(self) -> int:
        if not self._items:
            raise IndexError("top from empty stack")
        return self._items[-1][0]

    def get_min(self) -> int:
        if not self._items:
            raise IndexError("min of empty stack")
        return self._items[-1][1]

    def __len__(self) -> int:
        return len(self._items)


def main() -> None:
    ops = [("push", 5), ("push", 2), ("push", 7), ("push", 2), ("min",), ("pop",), ("min",),
           ("pop",), ("pop",), ("min",), ("push", -1), ("min",)]
    stacks = [NaiveMinStack(), TwoStackMinStack(), MinStack()]
    for op in ops:
        results = []
        for s in stacks:
            if op[0] == "push":
                s.push(op[1])
                results.append(None)
            elif op[0] == "pop":
                results.append(s.pop())
            else:
                results.append(s.get_min())
        label = " ".join(map(str, op))
        shown = "" if results[0] is None else f" -> {results[0]}"
        print(f"{label:<8}{shown:<6} min={stacks[2].get_min():>2}  agree={len(set(results)) == 1}")
    try:
        MinStack().get_min()
    except IndexError as e:
        print(f"empty get_min -> IndexError: {e}")


if __name__ == "__main__":
    main()
