"""
Exercise 12 — Count Numbers Without Equal Adjacent Digits (digit DP) [Tier: ○ Reference]
Chapter 19 · Pattern: digit DP (position, previous digit, tight, started) · Target time: 30 min

Problem
-------
`count_no_repeat(n)` — how many integers x with 1 <= x <= n have no two adjacent
equal digits (121 counts, 112 does not)? `count_range(lo, hi)` answers the same for
lo <= x <= hi. n <= 0 gives 0.

Examples
--------
>>> count_no_repeat(20), count_no_repeat(100)
(19, 90)
>>> count_range(100, 200)
81

Constraints
-----------
- n up to 10^18 (so looping over every x is out).

Hints
-----
- count_range(lo, hi) = count(hi) - count(lo - 1): solve prefix counts only.
- Only tight states depend on n; with memo on all four fields the tight states are
  visited just once per position anyway.

Follow-ups
----------
- Count numbers whose digit sum is divisible by k: replace prev with (sum mod k).
- Count numbers with all distinct digits: replace prev with a 10-bit mask.
"""
from __future__ import annotations

from functools import cache


def _valid(x: int) -> bool:
    s = str(x)
    return all(a != b for a, b in zip(s, s[1:]))


def count_brute(n: int) -> int:
    raise NotImplementedError("TODO")


def count_recursive(n: int) -> int:
    raise NotImplementedError("TODO")


def count_memo(n: int) -> int:
    raise NotImplementedError("TODO")


def count_no_repeat(n: int) -> int:
    raise NotImplementedError("TODO")


def count_range(lo: int, hi: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for n in (0, 9, 10, 11, 20, 100, 121, 1000, 4455, 98765):
        rungs = (count_brute(n), count_recursive(n), count_memo(n), count_no_repeat(n))
        print(f"count_no_repeat({n}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    print("count_range(100, 200) =", count_range(100, 200))
    big = 10 ** 18
    print(f"count_no_repeat(10**18) = {count_no_repeat(big)}  memo agrees: "
          f"{count_memo(big) == count_no_repeat(big)}")


if __name__ == "__main__":
    main()
