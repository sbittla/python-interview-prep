"""
Exercise 06 — Windowed Iteration and Moving Average            [Tier: ★ Core]
Chapter 23 · Pattern: deque(maxlen) sliding window · Target time: 15 min

Problem
-------
1. ``windowed(iterable, n)`` yields overlapping tuples of n consecutive items. If the input has
   fewer than n items, yield nothing. ``n < 1`` raises ``ValueError``.
2. ``moving_average(iterable, n)`` yields the mean of each window, rounded to 2 decimals,
   using O(1) work per item.

Examples
--------
>>> list(windowed([1, 2, 3, 4], 2))
[(1, 2), (2, 3), (3, 4)]
>>> list(moving_average([1, 2, 3, 4, 5], 3))
[2.0, 3.0, 4.0]

Constraints
-----------
- Input can be any iterable (possibly a generator); memory O(n).

Hints
-----
- ``collections.deque(maxlen=n)`` drops the oldest item automatically on append.
- For the average keep a running sum: add the new item, subtract the one that falls out.

Approach ladder
---------------
1. ``[tuple(seq[i:i+n]) for i in range(len(seq)-n+1)]`` — sequences only; average costs O(n)
   per window by re-summing → O(len * n).
2. ``deque(maxlen=n)`` — any iterable, O(n) per yielded tuple (the tuple copy), O(n) memory.
3. Running sum for the average — O(1) per item.

Follow-ups
----------
- ``itertools.pairwise`` (3.10+) is the n == 2 special case.
- How would you compute a moving *median*? (two heaps with lazy deletion, or a sorted list)
"""
from __future__ import annotations

from collections import deque
from itertools import islice, pairwise
from typing import Iterable, Iterator


def windowed_slicing(seq: list, n: int) -> list[tuple]:
    if n < 1:
        raise ValueError("n must be >= 1")
    return [tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)]


def windowed(iterable: Iterable, n: int) -> Iterator[tuple]:
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    window = deque(islice(it, n), maxlen=n)
    if len(window) < n:
        return
    yield tuple(window)
    for item in it:
        window.append(item)  # oldest item falls off the left
        yield tuple(window)


def moving_average_naive(seq: list[float], n: int) -> list[float]:
    return [round(sum(w) / n, 2) for w in windowed_slicing(seq, n)]


def moving_average(iterable: Iterable[float], n: int) -> Iterator[float]:
    if n < 1:
        raise ValueError("n must be >= 1")
    window: deque = deque()
    total = 0.0
    for x in iterable:
        window.append(x)
        total += x
        if len(window) > n:
            total -= window.popleft()
        if len(window) == n:
            yield round(total / n, 2)


def main() -> None:
    print("slicing :", windowed_slicing([1, 2, 3, 4, 5], 3))
    print("deque   :", list(windowed(range(1, 6), 3)))
    print("too short:", list(windowed([1, 2], 3)))
    print("n == 1  :", list(windowed("abc", 1)))
    print("pairwise equals windowed(...,2):",
          list(pairwise("abcd")) == list(windowed("abcd", 2)))
    prices = [10, 11, 12, 13, 12, 11, 15, 18]
    print("moving avg naive  :", moving_average_naive(prices, 3))
    print("moving avg running:", list(moving_average(prices, 3)))
    gen = (x % 7 for x in range(12))
    print("from generator:", list(moving_average(gen, 4)))


if __name__ == "__main__":
    main()
