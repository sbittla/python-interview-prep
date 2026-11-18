"""
Exercise 05 — Partition Labels                                     [Tier: ★ Core]
Chapter 20 · Pattern: greedy cut at last occurrence · Target time: 15 min

Problem
-------
Split a lowercase string into as many contiguous pieces as possible so that every letter
appears in at most one piece. Return the piece lengths (left to right).

Examples
--------
>>> partition_labels("abacbdefegde")
[5, 7]
>>> partition_labels("abc")
[1, 1, 1]

Constraints
-----------
- 1 <= len(s) <= 500 (the optimal solution is linear, so 10^6 is also fine).

Hints
-----
- Once you see an 'a', the piece containing it must stretch at least to the LAST 'a'.

Follow-ups
----------
- Return the pieces themselves, not just lengths.
- Merge-intervals view: each letter is an interval [first, last]; the answer is the lengths
  of the merged intervals.
"""
from __future__ import annotations


def brute_force(s: str) -> list[int]:
    raise NotImplementedError("TODO")


def partition_labels(s: str, trace: bool = False) -> list[int]:
    raise NotImplementedError("TODO")


def pieces(s: str) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    s = "abacbdefegde"
    print("trace for", s)
    print("sizes:", partition_labels(s, trace=True))
    print("pieces:", pieces(s))
    print()
    for s in ("ababcbacadefegdehijhklij", "abc", "aaaa", "a", "abcba", "eccbbbbdec"):
        print(f"{s!r:<28} -> {partition_labels(s)} (brute {brute_force(s)})")


if __name__ == "__main__":
    main()
