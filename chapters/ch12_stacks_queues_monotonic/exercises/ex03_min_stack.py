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

Hints
-----
- What is the minimum of the stack *below* an entry while that entry is on the stack?
- Either store it next to each value, or keep a second stack of minimums (mind duplicates).

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
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def top(self) -> int:
        raise NotImplementedError("TODO")

    def get_min(self) -> int:
        raise NotImplementedError("TODO")


class TwoStackMinStack:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def top(self) -> int:
        raise NotImplementedError("TODO")

    def get_min(self) -> int:
        raise NotImplementedError("TODO")


class MinStack:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> int:
        raise NotImplementedError("TODO")

    def top(self) -> int:
        raise NotImplementedError("TODO")

    def get_min(self) -> int:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")


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
