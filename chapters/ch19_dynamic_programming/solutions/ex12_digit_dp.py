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

Approach ladder
---------------
Recipe — state: (pos, prev, tight, started): the digit index, the previous digit
placed, whether the prefix equals n's prefix (then the next digit is capped by n's
digit), and whether a non-zero digit has been placed (leading zeros are not digits
of the number, so they cannot clash); transition: try every allowed digit d != prev;
base: past the last digit, count 1 if started; order: top-down on pos; answer:
f(0, -1, True, False).
1. Brute force — test every x: O(n * digits). Fine for n <= 10^6, hopeless at 10^18.
2. Plain digit recursion — enumerates every digit string: O(10^digits), no better.
3. Memoised — states: 19 positions * 11 prev * 2 * 2, 10 digits each: about 8,000
   steps for any n <= 10^18 (O(D * 10 * 10) for D digits).
4. Closed-form counting (bottom-up flavour) — a k-digit valid number has 9 choices for
   the first digit and 9 for each later one: 9^k. Add 9^k for every shorter length, then
   walk n's digits: at position i, every allowed digit below n[i] frees the remaining
   L-i-1 positions (9 choices each); stop if n's own prefix repeats a digit. O(D * 10).

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
    return sum(_valid(x) for x in range(1, n + 1))


def count_recursive(n: int) -> int:
    if n <= 0:
        return 0
    digits = str(n)

    def f(pos: int, prev: int, tight: bool, started: bool) -> int:
        if pos == len(digits):
            return 1 if started else 0
        limit = int(digits[pos]) if tight else 9
        total = 0
        for d in range(limit + 1):
            if started and d == prev:
                continue
            now = started or d != 0
            total += f(pos + 1, d if now else -1, tight and d == limit, now)
        return total

    return f(0, -1, True, False)


def count_memo(n: int) -> int:
    if n <= 0:
        return 0
    digits = str(n)

    @cache
    def f(pos: int, prev: int, tight: bool, started: bool) -> int:
        if pos == len(digits):
            return 1 if started else 0
        limit = int(digits[pos]) if tight else 9
        total = 0
        for d in range(limit + 1):
            if started and d == prev:
                continue
            now = started or d != 0
            total += f(pos + 1, d if now else -1, tight and d == limit, now)
        return total

    return f(0, -1, True, False)


def count_no_repeat(n: int) -> int:
    if n <= 0:
        return 0
    s = str(n)
    length = len(s)
    total = sum(9 ** k for k in range(1, length))           # all shorter numbers
    for i, ch in enumerate(s):
        for d in range(1 if i == 0 else 0, int(ch)):        # digits below n's digit
            if i and d == int(s[i - 1]):
                continue
            total += 9 ** (length - i - 1)
        if i and ch == s[i - 1]:
            return total                                    # n's prefix is itself invalid
    return total + 1                                        # n itself is valid


def count_range(lo: int, hi: int) -> int:
    return count_no_repeat(hi) - count_no_repeat(lo - 1) if hi >= lo else 0


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
