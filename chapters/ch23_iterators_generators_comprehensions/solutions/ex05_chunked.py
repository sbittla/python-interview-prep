"""
Exercise 05 — Chunked Iteration                               [Tier: ★ Core]
Chapter 23 · Pattern: islice batching · Target time: 10 min

Problem
-------
``chunked(iterable, n)`` yields consecutive lists of length ``n``; the final chunk may be shorter.
It must work on any iterable, including generators and infinite streams. ``n < 1`` raises
``ValueError``.

Examples
--------
>>> list(chunked(range(7), 3))
[[0, 1, 2], [3, 4, 5], [6]]
>>> list(chunked([], 3))
[]

Constraints
-----------
- Memory O(n): never materialise the whole input.
- ``itertools.batched`` (Python 3.12+, yields tuples) is the built-in answer; write your own so
  the code runs on 3.10.

Hints
-----
- Call ``iter()`` once, then repeatedly ``list(islice(it, n))`` until you get an empty list.
- The walrus operator ``:=`` makes this loop a one-liner condition.

Approach ladder
---------------
1. Slicing ``seq[i:i+n]`` — fast, but needs a sequence (``len`` + indexing), fails on generators.
2. Manual counter + buffer list — works on any iterable, more code and an easy off-by-one.
3. ``islice`` on a shared iterator — any iterable, O(n) memory, 3 lines.

Follow-ups
----------
- Pad the last chunk with a fill value (``zip_longest(*[it] * n, fillvalue=...)``).
- Why does ``zip(*[iter(xs)] * n)`` work, and why does it drop the tail?
"""
from __future__ import annotations

from itertools import count, islice, zip_longest
from typing import Iterable, Iterator


def chunked_slicing(seq: list, n: int) -> list[list]:
    """Rung 1: sequences only."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return [list(seq[i:i + n]) for i in range(0, len(seq), n)]


def chunked_manual(iterable: Iterable, n: int) -> Iterator[list]:
    """Rung 2: buffer and counter."""
    if n < 1:
        raise ValueError("n must be >= 1")
    buf: list = []
    for item in iterable:
        buf.append(item)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf


def chunked(iterable: Iterable, n: int) -> Iterator[list]:
    """Rung 3: islice on one shared iterator."""
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk


def chunked_padded(iterable: Iterable, n: int, fill=None) -> list[tuple]:
    """Follow-up: the 'grouper' recipe — n references to the SAME iterator."""
    return list(zip_longest(*[iter(iterable)] * n, fillvalue=fill))


def main() -> None:
    print("slicing :", chunked_slicing(list(range(7)), 3))
    print("manual  :", list(chunked_manual(range(7), 3)))
    print("islice  :", list(chunked(range(7), 3)))
    print("exact   :", list(chunked("abcdef", 2)))
    print("empty   :", list(chunked([], 3)))
    print("padded  :", chunked_padded("abcdefg", 3, "-"))
    print("zip trick drops tail:", list(zip(*[iter(range(7))] * 3)))
    gen = (x * x for x in range(10))
    print("from generator:", list(chunked(gen, 4)))
    stream = chunked(count(), 5)  # infinite input, still fine
    print("infinite stream, first two chunks:", next(stream), next(stream))
    try:
        list(chunked([1], 0))
    except ValueError as exc:
        print("ValueError:", exc)


if __name__ == "__main__":
    main()
