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

Approach ladder
---------------
1. Brute force — for each candidate cut position test whether the left and right parts share
   a letter (set intersection), cutting greedily at the first valid position. O(n^2).
2. Optimal — precompute the last index of each letter. Sweep, extending the current piece's
   end to the last occurrence of every letter seen; when i reaches that end, cut. O(n) time,
   O(alphabet) space. Cutting as early as possible is safe: any later cut could be split
   here without breaking the rule (exchange argument).

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
    sizes: list[int] = []
    start = 0
    while start < len(s):
        for cut in range(start + 1, len(s) + 1):
            if not set(s[start:cut]) & set(s[cut:]):
                sizes.append(cut - start)
                start = cut
                break
    return sizes


def partition_labels(s: str, trace: bool = False) -> list[int]:
    last = {ch: i for i, ch in enumerate(s)}      # later indices overwrite earlier ones
    sizes: list[int] = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if trace:
            print(f"  i={i:>2} ch={ch} last={last[ch]:>2} piece_end={end:>2}" + ("  <- cut" if i == end else ""))
        if i == end:
            sizes.append(end - start + 1)
            start = i + 1
    return sizes


def pieces(s: str) -> list[str]:
    out, i = [], 0
    for size in partition_labels(s):
        out.append(s[i:i + size])
        i += size
    return out


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
