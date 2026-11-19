"""
Exercise 02 — Edge-Case Generator for a Signature          [Tier: ★ Core]
Chapter 02 · Pattern: interview method (examples & testing) · Target time: 20 min

Problem
-------
Given a signature spec (parameter name -> type tag) and one "typical" call,
generate a labelled list of edge-case calls. Vary ONE parameter at a time
while the others keep their typical value, so a failing case points at a
single cause.

Type tags and their edge values (in this order):

    "int"       : zero, one, negative, large (10**9)
    "str"       : empty, single char, repeated char, mixed case, with space
    "list[int]" : empty, single, two equal, all equal, negatives,
                  sorted ascending, sorted descending, contains zero

Write edge_cases(spec, typical) -> list of (label, kwargs) where label is
"<param>=<edge name>" and kwargs is a fresh dict of arguments. Skip a case
whose kwargs equal the typical call or an earlier case.

Also write run_cases(func, cases, reference) -> list of labels where
func(**kwargs) != reference(**kwargs) (or func raises).

Examples
--------
>>> [label for label, _ in edge_cases({"k": "int"}, {"k": 5})]
['k=zero', 'k=one', 'k=negative', 'k=large']

Constraints
-----------
- `typical` must have exactly the keys of `spec` (ValueError otherwise).
- Each kwargs dict is independent: mutating one never affects another.

Hints
-----
- Vary one parameter at a time: start from a deep copy of `typical`, replace
  one value, and skip it if an equal dict was already produced.
- Deep-copy the edge value too, or two cases will share one list.
- In run_cases, an exception raised by func is a failure, not a crash.

Follow-ups
----------
- Add pairwise (all-pairs) combinations for interacting parameters.
- Let the caller add problem-specific edges (e.g. target unreachable).
"""
from __future__ import annotations

import copy
from typing import Any, Callable

EDGES: dict[str, list[tuple[str, Any]]] = {
    "int": [("zero", 0), ("one", 1), ("negative", -3), ("large", 10**9)],
    "str": [("empty", ""), ("single", "a"), ("repeated", "aaaa"),
            ("mixed_case", "aA"), ("with_space", "a b")],
    "list[int]": [
        ("empty", []), ("single", [7]), ("two_equal", [2, 2]),
        ("all_equal", [5, 5, 5, 5]), ("negatives", [-4, -1, -7]),
        ("ascending", [1, 2, 3, 4]), ("descending", [4, 3, 2, 1]),
        ("has_zero", [0, 3, 0]),
    ],
}


def edge_cases(spec: dict[str, str], typical: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    raise NotImplementedError("TODO")


def run_cases(func: Callable[..., Any], cases: list[tuple[str, dict[str, Any]]],
              reference: Callable[..., Any]) -> list[str]:
    raise NotImplementedError("TODO")


def max_gap_reference(nums: list[int], k: int) -> int:
    """Largest nums[j] - nums[i] with i < j <= i + k, or 0 if no such pair."""
    best = 0
    for i in range(len(nums)):
        for j in range(i + 1, min(len(nums), i + k + 1)):
            best = max(best, nums[j] - nums[i])
    return best


def max_gap_buggy(nums: list[int], k: int) -> int:
    """Tempting 'optimisation': assumes k >= 1 and a non-empty list."""
    best = 0
    lo = nums[0]                       # crashes on []
    for j in range(1, len(nums)):
        lo = min(lo, nums[j - 1])      # ignores the window limit k
        best = max(best, nums[j] - lo)
    return best


def main() -> None:
    spec = {"nums": "list[int]", "k": "int"}
    typical = {"nums": [3, 1, 4, 1, 5], "k": 2}
    cases = edge_cases(spec, typical)
    print(f"{len(cases)} one-at-a-time cases (product would be "
          f"{len(EDGES['list[int]']) * len(EDGES['int'])})")
    for label, kwargs in cases:
        print(f"  {label:<20} {kwargs}  ref -> {max_gap_reference(**kwargs)}")
    print(f"\nmax_gap_buggy fails on: {run_cases(max_gap_buggy, cases, max_gap_reference)}")


if __name__ == "__main__":
    main()
