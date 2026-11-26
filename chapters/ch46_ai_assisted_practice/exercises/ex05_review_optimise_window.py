"""
Exercise 05 — Review and Optimise a Generated Sliding-Window Sum   [Tier: ◆ Extended]
Chapter 46 · Pattern: review notes → edge cases → count reads → O(n) rewrite · Target time: 30 min

Problem
-------
Spec: max_window_sum(nums, k) -> the largest sum of k consecutive elements of
nums. Values may be negative. 1 <= k <= len(nums), otherwise ValueError.

The assistant produced generated_max_window_sum (below, given). Your pair
asks you to review it as if it were a pull request (→ §31.8), then ship a
version you can defend.

1. REVIEW: a list of (category, comment) review notes. Categories come from
   CATEGORIES. A complete review has at least one "correctness", one
   "complexity" and one "edge case" note, each a full sentence that points at
   the code (the line or expression) and says what to do instead.
2. EDGE_CASES: ((nums, k), expected) pairs; expected may be ValueError (the
   class). The generated code must get at least one wrong.
3. reads(fn, nums, k) -> how many elements fn reads from nums, counted by
   wrapping nums in the given CountingSeq. Deterministic evidence for the
   complexity note, instead of a timing.
4. max_window_sum(nums, k) -> the fix: O(n) time, O(1) extra space, reading
   each element at most twice. COMPLEXITY.

Examples
--------
>>> generated_max_window_sum([1, 2, 3], 3)          # misses the only window
0
>>> max_window_sum([1, 2, 3], 3), max_window_sum([-4, -1, -3], 2)
(6, -4)

Constraints
-----------
- Index nums (nums[i]); do not copy it. The tests pass a CountingSeq.

Hints
-----
- How many windows of size k does a list of length n have? How many does
  the generated loop visit?
- What does the generated code return when every number is negative?
- What should happen for k = 0, k > len(nums), an empty list?
- Moving the window one step changes its sum by two elements.
- Include a case where the best window is the LAST one.

Follow-ups
----------
- Max AVERAGE window: what changes?
- Variable-length windows with a constraint (→ §10.5).
- Float inputs: what happens to a running sum over a long input?
"""
from __future__ import annotations

import random
from collections.abc import Sequence

CATEGORIES = ("correctness", "complexity", "edge case", "readability")


# --- given: the generated code (do not edit) -----------------------------------
def generated_max_window_sum(nums, k):
    """AI-generated: largest sum of k consecutive elements."""
    best = 0
    for i in range(len(nums) - k):
        best = max(best, sum(nums[i:i + k]))
    return best


class CountingSeq(Sequence):
    """Wraps a list and counts element reads (a slice of length m counts m)."""

    def __init__(self, data: list[int]) -> None:
        self.data, self.count = list(data), 0

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index):
        result = self.data[index]
        self.count += len(result) if isinstance(index, slice) else 1
        return result


# --- your review and tools ---------------------------------------------------------
REVIEW: list[tuple[str, str]] = []   # TODO: (category, comment) notes

EDGE_CASES: list[tuple[tuple[list[int], int], object]] = []   # TODO


def reads(fn, nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


# --- the fix ---------------------------------------------------------------------------
def max_window_sum(nums: Sequence[int], k: int) -> int:
    raise NotImplementedError("TODO")


COMPLEXITY: dict[str, str] = {}   # TODO


def check(fn, case, expected) -> bool:
    try:
        return fn(*case) == expected
    except ValueError:
        return expected is ValueError


def main() -> None:
    print("review categories:", sorted({c for c, _ in REVIEW}))
    print("generated fails:", [c for c, want in EDGE_CASES
                               if not check(generated_max_window_sum, c, want)])
    print("fixed passes all edge cases:",
          all(check(max_window_sum, c, want) for c, want in EDGE_CASES))
    rng = random.Random(0)
    agree = True
    for _ in range(500):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 10))]
        k = rng.randint(1, len(nums))
        brute = max(sum(nums[s:s + k]) for s in range(len(nums) - k + 1))
        agree &= max_window_sum(nums, k) == brute
    print("fixed == brute force on 500 random cases:", agree)
    for n in (1000, 2000):
        k = n // 2
        nums = [rng.randint(-9, 9) for _ in range(n)]
        print(f"n={n}, k={k}: reads generated={reads(generated_max_window_sum, nums, k)}"
              f" fixed={reads(max_window_sum, nums, k)}")
    print("complexity:", COMPLEXITY)


if __name__ == "__main__":
    main()
