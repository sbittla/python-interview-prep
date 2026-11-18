"""
Exercise 09 — Lazy vs Eager: Count the Work                    [Tier: ★ Core]
Chapter 23 · Pattern: short-circuiting with next()/any() · Target time: 15 min

Problem
-------
1. ``first(iterable, pred, default=None)`` returns the first item satisfying ``pred`` (or
   ``default``) and stops consuming the input as soon as it finds it.
2. ``Probe`` wraps an iterable and counts how many items have been pulled through it
   (``probe.pulled``). Use it to prove how much work eager and lazy code does.
3. ``eager_first_square_over(nums, limit)`` and ``lazy_first_square_over(nums, limit)`` both return
   the first n*n > limit; the eager one builds the full list of squares first, the lazy one uses a
   generator expression.

Examples
--------
>>> first([1, 4, 9, 16], lambda x: x > 5)
9
>>> first([], lambda x: True, "none")
'none'

Constraints
-----------
- ``first`` must work on infinite iterators.

Hints
-----
- ``next((x for x in it if pred(x)), default)`` is the idiom.
- ``Probe`` is an iterator class: ``__next__`` increments a counter then delegates.
- ``sys.getsizeof`` of a generator is constant; of a list it grows with n.

Approach ladder
---------------
1. Build a filtered list then take ``[0]`` — O(n) time and memory even if the answer is first.
2. Explicit loop with ``return`` — lazy, O(k) where k is the answer position.
3. ``next()`` over a generator expression — same O(k), one line, default handled.

Follow-ups
----------
- Do ``any()`` and ``all()`` short-circuit? (yes — demonstrate with ``Probe``)
- When is eager better? (you need the data more than once, need ``len``, or random access)
"""
from __future__ import annotations

import sys
from itertools import count
from typing import Callable, Iterable


def first(iterable: Iterable, pred: Callable, default=None):
    return next((x for x in iterable if pred(x)), default)


class Probe:
    """Iterator wrapper that counts how many items were pulled."""

    def __init__(self, iterable: Iterable) -> None:
        self._it = iter(iterable)
        self.pulled = 0

    def __iter__(self) -> "Probe":
        return self

    def __next__(self):
        item = next(self._it)  # StopIteration propagates, ending the loop
        self.pulled += 1
        return item


def eager_first_square_over(nums: Iterable[int], limit: int):
    squares = [n * n for n in nums]
    over = [s for s in squares if s > limit]
    return over[0] if over else None


def lazy_first_square_over(nums: Iterable[int], limit: int):
    return first((n * n for n in nums), lambda s: s > limit)


def main() -> None:
    p = Probe(range(1_000_000))
    print("eager result:", eager_first_square_over(p, 50), "| items pulled:", p.pulled)
    p = Probe(range(1_000_000))
    print("lazy result :", lazy_first_square_over(p, 50), "| items pulled:", p.pulled)

    p = Probe([2, 4, 5, 6, 8])
    print("all even?", all(x % 2 == 0 for x in p), "| pulled:", p.pulled)
    p = Probe([1, 3, 4, 5])
    print("any even?", any(x % 2 == 0 for x in p), "| pulled:", p.pulled)

    print("first on infinite count():", first(count(1), lambda n: n % 97 == 0))
    print("first with default:", first([], bool, "nothing"))

    gen = (x for x in range(1_000_000))
    lst = [x for x in range(1_000_000)]
    print("generator object smaller than list:", sys.getsizeof(gen) < sys.getsizeof(lst))
    print("generator size independent of n:",
          sys.getsizeof(x for x in range(10)) == sys.getsizeof(x for x in range(10**9)))

    # A generator is single-use: the second sum sees an exhausted generator.
    squares = (x * x for x in range(4))
    print("sum twice:", sum(squares), sum(squares))


if __name__ == "__main__":
    main()
