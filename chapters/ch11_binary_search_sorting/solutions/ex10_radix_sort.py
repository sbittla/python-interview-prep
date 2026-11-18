"""
Exercise 10 — Radix Sort (LSD)                                     [Tier: ○ Reference]
Chapter 11 · Pattern: digit-by-digit stable counting sort · Target time: 20 min

Problem
-------
Sort a list of integers (possibly negative) with least-significant-digit radix
sort in base 10, using a stable counting sort per digit. Also sort a list of
equal-length lowercase strings with the same idea (character positions from
right to left).

Examples
--------
>>> solve([170, 45, 75, 90, 802, 24, 2, 66])
[2, 24, 45, 66, 75, 90, 170, 802]
>>> solve([3, -10, 0, -2, 7])
[-10, -2, 0, 3, 7]

Constraints
-----------
- d = number of digits of the largest absolute value; base b = 10.

Approach ladder
---------------
1. Comparison sort — O(n log n).
2. Counting sort on the full value — O(n + range): fails when range is huge.
3. Radix sort — d passes of stable counting sort on one digit each:
   O(d * (n + b)). Wins when d is small relative to log n (e.g. fixed-width ids).
   Why LSD works: after pass t the list is sorted by the last t digits, because
   each pass is STABLE and so preserves the order established by earlier passes.

Follow-ups
----------
- Negative numbers: sort negatives by absolute value and reverse them, then
  append the sorted non-negatives (done here), or add an offset.
- MSD radix sort (most significant first) suits variable-length strings and
  can stop early; it is recursive bucketing.
"""
from __future__ import annotations


def counting_pass(nums: list[int], exp: int, base: int = 10) -> list[int]:
    """Stable sort of non-negative nums by digit (num // exp) % base."""
    counts = [0] * base
    for x in nums:
        counts[(x // exp) % base] += 1
    for d in range(1, base):                 # inclusive prefix sums: end slot of each digit
        counts[d] += counts[d - 1]
    out = [0] * len(nums)
    for x in reversed(nums):                 # right-to-left fill keeps the pass stable
        d = (x // exp) % base
        counts[d] -= 1
        out[counts[d]] = x
    return out


def radix_sort_non_negative(nums: list[int], trace: list[str] | None = None) -> list[int]:
    if not nums:
        return []
    out, exp = list(nums), 1
    while max(nums) // exp > 0:
        out = counting_pass(out, exp)
        if trace is not None:
            trace.append(f"after digit exp={exp:>3}: {out}")
        exp *= 10
    return out


def solve(nums: list[int]) -> list[int]:
    neg = [-x for x in nums if x < 0]
    pos = [x for x in nums if x >= 0]
    neg_sorted = [-x for x in reversed(radix_sort_non_negative(neg))]
    return neg_sorted + radix_sort_non_negative(pos)


def radix_sort_strings(words: list[str]) -> list[str]:
    """LSD radix for equal-length lowercase words."""
    if not words:
        return []
    width = len(words[0])
    out = list(words)
    for pos in range(width - 1, -1, -1):
        buckets: list[list[str]] = [[] for _ in range(26)]
        for w in out:                        # appending in order keeps it stable
            buckets[ord(w[pos]) - ord("a")].append(w)
        out = [w for b in buckets for w in b]
    return out


def main() -> None:
    data = [170, 45, 75, 90, 802, 24, 2, 66]
    trace: list[str] = []
    print("input:", data)
    result = radix_sort_non_negative(data, trace)
    print("\n".join(trace))
    print("result:", result)
    mixed = [3, -10, 0, -2, 7, -100, 55]
    print("with negatives:", solve(mixed), "| ok:", solve(mixed) == sorted(mixed))
    words = ["dab", "cab", "fad", "bad", "dad", "ebb", "ace", "add", "fed", "bed", "fee", "bee"]
    print("strings:", radix_sort_strings(words))
    print("edge cases:", solve([]), solve([0]), solve([5, 5, 0]))


if __name__ == "__main__":
    main()
