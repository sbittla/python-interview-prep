"""
Exercise 05 — Self-Test Harness: Brute Force vs Optimised   [Tier: ★ Core]
Chapter 02 · Pattern: interview method (optimise, then test) · Target time: 25 min

Problem
-------
The brute force you write in step 3 of the method is not wasted: it is a
reference to test your optimised code against. Build a small stress tester.

- stress(candidate, reference, gen, trials=500, seed=0) -> the first argument
  tuple on which candidate(*args) != reference(*args), or None if all trials
  agree. gen(rng) returns an argument tuple from a random.Random.
- shrink(args, fails) -> a smaller argument tuple that still fails. Arguments
  are ints or lists of ints. Repeat until nothing changes: try deleting each
  list element; then try moving each int (and each list element) toward 0,
  first by halving (x // 2 for x > 0, -(-x // 2) for x < 0), then by one.
  Keep a change only if fails(new_args) is still True.

Demo problem (used in the chapter's worked example): count the pairs i < j
with nums[i] + nums[j] == target. Duplicates count separately.

Examples
--------
>>> count_pairs_brute([2, 2, 2], 4), count_pairs_fast([2, 2, 2], 4)
(3, 3)
>>> stress(count_pairs_fast, count_pairs_brute, gen_case) is None
True

Constraints
-----------
- Deterministic for a given seed. Never mutates the generated arguments
  (pass copies to each function).

Hints
-----
- count_pairs_fast: one pass with a dict of counts; look up target - x
  BEFORE adding x, so x never pairs with itself.
- stress: one random.Random(seed); pass deep copies to both functions.
- shrink: generate smaller variants (delete one element, move one value
  toward 0); restart from the first variant that still fails; stop when
  none fails.

Follow-ups
----------
- Generate small values (range 0..5) on purpose: collisions and duplicates
  are where pair-counting bugs live.
- How would you stress a function whose answer is not unique (any valid
  index pair)? Compare with a checker, not with equality.
"""
from __future__ import annotations

import copy
import random
from typing import Any, Callable


def count_pairs_brute(nums: list[int], target: int) -> int:
    n = len(nums)
    return sum(nums[i] + nums[j] == target for i in range(n) for j in range(i + 1, n))


def count_pairs_fast(nums: list[int], target: int) -> int:
    raise NotImplementedError("TODO")


def count_pairs_two_pointer_buggy(nums: list[int], target: int) -> int:
    """Wrong but tempting: sort + two pointers, one pair per match."""
    a = sorted(nums)
    lo, hi, pairs = 0, len(a) - 1, 0
    while lo < hi:
        s = a[lo] + a[hi]
        if s == target:
            pairs += 1
            lo, hi = lo + 1, hi - 1        # skips duplicate partners
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return pairs


def gen_case(rng: random.Random) -> tuple[list[int], int]:
    nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 8))]
    return nums, rng.randint(-6, 6)


def stress(candidate: Callable[..., Any], reference: Callable[..., Any],
           gen: Callable[[random.Random], tuple], trials: int = 500,
           seed: int = 0) -> tuple | None:
    raise NotImplementedError("TODO")


def shrink(args: tuple, fails: Callable[[tuple], bool]) -> tuple:
    raise NotImplementedError("TODO")


def main() -> None:
    ref = count_pairs_brute
    print(f"fast vs brute, 500 random cases: counterexample = "
          f"{stress(count_pairs_fast, ref, gen_case)}")
    bad = stress(count_pairs_two_pointer_buggy, ref, gen_case)
    print(f"two-pointer vs brute: counterexample = {bad}")

    def fails(args: tuple) -> bool:
        return count_pairs_two_pointer_buggy(*copy.deepcopy(args)) != ref(*args)

    small = shrink(bad, fails)
    print(f"shrunk to {small}: buggy -> {count_pairs_two_pointer_buggy(*small)}, "
          f"brute -> {ref(*small)}")


if __name__ == "__main__":
    main()
