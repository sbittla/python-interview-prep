"""
Exercise 01 — Fix a Generated Binary Search (Wrong Boundary)       [Tier: ★ Core]
Chapter 46 · Pattern: oracle + seeded random cases → fix → complexity · Target time: 20 min

Problem
-------
You asked an assistant for "the index of the first element >= x in a sorted
list (len(a) if there is none)". It produced generated_first_ge (below, given).
It passes the three examples you tried by hand. Do not trust it; prove it.

1. oracle(a, x) -> the answer by the obvious linear scan. Slow is fine: the
   oracle's only job is to be obviously right.
2. random_case(rng) -> (a, x): a sorted list of 0..6 small ints WITH
   duplicates, and an x that may lie below, inside or above the values.
3. find_counterexample(candidate, trials=300, seed=0) -> the smallest (a, x)
   on which candidate disagrees with oracle, or None. Generate `trials` cases
   with random.Random(seed), sort them by len(a) (a cheap "shrink": the first
   failure you report is a small one), and check them in that order.
4. EDGE_CASES: hand-picked ((a, x), expected) pairs a reviewer would ask
   about. At least one must make generated_first_ge fail.
5. first_ge(a, x) -> the fixed function. COMPLEXITY -> its time and space.

Examples
--------
>>> generated_first_ge([1, 3, 5], 3), generated_first_ge([1, 3, 5], 9)
(1, 2)
>>> first_ge([1, 3, 5], 9)
3

Constraints
-----------
- a is sorted ascending and may contain duplicates; it may be empty.
- first_ge must stay O(log n): a linear scan "fix" is a regression.

Approach ladder
---------------
1. Brute force — eyeball the code and try a few examples: the generated code
   passes typical inputs, which is why it looked right.
2. Improved   — hand-written edge cases (empty, x below all, x above all,
   duplicates): finds the bug if you think of "x above all".
3. Optimal    — a property check against a brute-force oracle on hundreds of
   seeded random small inputs: finds it whether or not you thought of it, and
   keeps guarding the fix. The fix itself is one token: the search range is
   [0, len(a)], not [0, len(a) - 1], because len(a) is a legal answer.

Follow-ups
----------
- Why is the empty list handled "by accident"? (lo = 0, hi = -1: the loop
  never runs and 0 happens to be right.)
- Compare against bisect.bisect_left (→ §11.2); in an AI-allowed round, say
  you would ship bisect and keep the hand-rolled version only if asked.
- What breaks if the list is not sorted? (Nothing raises; the answer is
  silently meaningless: state the precondition.)
"""
from __future__ import annotations

import bisect
import random

Case = tuple[list[int], int]


# --- given: the generated code (do not edit) -----------------------------------
def generated_first_ge(a: list[int], x: int) -> int:
    """AI-generated: index of the first element >= x in sorted a, else len(a)."""
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


# --- your bug-finding tools --------------------------------------------------------
def oracle(a: list[int], x: int) -> int:
    return next((i for i, v in enumerate(a) if v >= x), len(a))


def random_case(rng: random.Random) -> Case:
    a = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 6)))
    return a, rng.randint(-1, 6)


def find_counterexample(candidate, trials: int = 300, seed: int = 0) -> Case | None:
    rng = random.Random(seed)
    cases = sorted((random_case(rng) for _ in range(trials)), key=lambda c: len(c[0]))
    for a, x in cases:
        if candidate(list(a), x) != oracle(a, x):
            return a, x
    return None


EDGE_CASES: list[tuple[Case, int]] = [
    (([], 3), 0),                 # empty
    (([5], 1), 0),                # x below everything
    (([5], 9), 1),                # x above everything: the bug
    (([1, 3, 5], 5), 2),          # x equals the last element
    (([2, 2, 2], 2), 0),          # duplicates: the FIRST one
    (([1, 2, 2, 4], 3), 3),       # x between values
]


# --- the fix ---------------------------------------------------------------------------
def first_ge(a: list[int], x: int) -> int:
    lo, hi = 0, len(a)            # len(a) is a legal answer, so it must be in range
    while lo < hi:                # invariant: answer in [lo, hi]
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


COMPLEXITY = {"time": "O(log n)", "space": "O(1)"}


def main() -> None:
    print("generated on typical inputs:",
          [generated_first_ge([1, 3, 5], x) for x in (0, 3, 4)])
    bad = find_counterexample(generated_first_ge)
    print("counterexample:", bad, "-> generated", generated_first_ge(*bad),
          "oracle", oracle(*bad))
    failing = [case for case, want in EDGE_CASES if generated_first_ge(*case) != want]
    print("edge cases the generated code fails:", failing)
    print("fixed: counterexample =", find_counterexample(first_ge),
          "| edge cases pass:", all(first_ge(*c) == w for c, w in EDGE_CASES))
    rng = random.Random(1)
    agree = all(first_ge(a, x) == bisect.bisect_left(a, x)
                for a, x in (random_case(rng) for _ in range(1000)))
    print("fixed agrees with bisect_left on 1000 cases:", agree)
    print("complexity:", COMPLEXITY)


if __name__ == "__main__":
    main()
