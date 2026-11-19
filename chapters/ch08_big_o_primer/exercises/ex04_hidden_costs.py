"""
Exercise 04 — Hidden Costs: list vs set, pop(0) vs deque     [Tier: ◆ Extended]
Chapter 08 · Pattern: one innocent-looking line can be O(n) · Target time: 20 min

Problem
-------
Prove, with deterministic counts rather than raw timings, that three common
lines hide an O(n) cost:

1. ``eq_calls_for_lookups(kind, n, queries)`` — build a container (``"list"`` or
   ``"set"``) of ``Probe(0) .. Probe(n-1)`` and run ``q in container`` for each
   query value; return the total number of ``__eq__`` calls. A list scans
   (up to n calls per miss); a set hashes and compares with at most a few
   candidates.
2. ``slice_copies(n)`` vs ``index_copies(n)`` — recursive "sum of a list". The
   slicing version recurses on ``xs[1:]``; return how many element references
   were copied in total (sum of slice lengths). The index version passes
   ``i + 1`` and copies nothing.
3. ``drain_front(kind, n)`` — empty a queue of n items from the front, with
   ``list.pop(0)`` or ``deque.popleft()``. CPython's ``list.pop(0)`` shifts every
   remaining element left, so the cost model is the sum of shifts. Return that
   modelled shift count; ``main`` confirms the model with a timing *comparison*
   (prints only a boolean).

Examples
--------
>>> eq_calls_for_lookups("list", 100, [-1])     # one miss scans all 100
100
>>> eq_calls_for_lookups("set", 100, [-1])
0
>>> slice_copies(5), index_copies(5)
(10, 0)

Constraints
-----------
- n >= 0. Standard library only. No raw timings in output.

Hints
-----
- Reset Probe.eq_calls after building the container, before the lookups.
- xs[1:] creates a new list of len(xs) - 1 references.
- pop(0) on a list of length L moves L - 1 references; popleft moves none.

Follow-ups
----------
- Why is ``list.pop()`` (from the end) O(1) but ``pop(0)`` O(n)?
- ``s += t`` in a loop over strings: why can it be O(n²), and why is
  ``"".join(parts)`` O(total length)? (→ §22.7)
"""
from __future__ import annotations

import timeit
from collections import deque


class Probe:
    eq_calls = 0

    def __init__(self, v: int) -> None:
        self.v = v

    def __eq__(self, other: object) -> bool:
        Probe.eq_calls += 1
        return isinstance(other, Probe) and self.v == other.v

    def __hash__(self) -> int:
        return hash(self.v)


def eq_calls_for_lookups(kind: str, n: int, queries: list[int]) -> int:
    raise NotImplementedError("TODO")


def slice_copies(n: int) -> int:
    raise NotImplementedError("TODO")


def index_copies(n: int) -> int:
    raise NotImplementedError("TODO")


def drain_front(kind: str, n: int) -> int:
    raise NotImplementedError("TODO")


def deque_faster(n: int = 30_000) -> bool:
    t_list = timeit.timeit(lambda: drain_front("list", n), number=1)
    t_deque = timeit.timeit(lambda: drain_front("deque", n), number=1)
    return t_list > 3 * t_deque


def main() -> None:
    queries = list(range(-500, 500))       # half hits, half misses
    for n in (1_000, 2_000, 4_000):
        lst = eq_calls_for_lookups("list", n, queries)
        st = eq_calls_for_lookups("set", n, queries)
        print(f"n={n:<5} 1000 lookups: list eq-calls={lst:<8} set eq-calls={st}")
    print("list cost doubles with n:",
          eq_calls_for_lookups("list", 4000, [-1]) == 2 * eq_calls_for_lookups("list", 2000, [-1]))
    for n in (10, 100, 400):   # 1000 would hit the recursion limit (ex05)
        print(f"sum via xs[1:] n={n:<4} copied={slice_copies(n):<6} via index copied={index_copies(n)}")
    for n in (1_000, 2_000):
        print(f"drain n={n}: list shifts={drain_front('list', n):<8} deque shifts={drain_front('deque', n)}")
    print("deque.popleft beats list.pop(0) by >3x at n=30000:", deque_faster())


if __name__ == "__main__":
    main()
