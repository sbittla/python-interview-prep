"""
Exercise 02 — Designing Test Cases that Catch Real Bugs   [Tier: ★ Core]
Chapter 31 · Pattern: happy / edge / error cases + mutation check · Target time: 25 min

Problem
-------
``chunk(items, size)`` splits a sequence into consecutive lists of length ``size``; the last
list may be shorter. ``size`` must be an int >= 1 (``ValueError`` otherwise; ``TypeError`` for a
non-int such as 2.0 or True). The input must not be modified.

Implement ``chunk`` and design three tables of test cases — HAPPY, EDGE and ERROR. Then
prove the tables are good: run them against five deliberately broken "mutants" of ``chunk``
and report which category kills each mutant. A suite that only kills mutants with HAPPY cases
is too weak.

Examples
--------
>>> chunk([1, 2, 3, 4, 5], 2)
[[1, 2], [3, 4], [5]]
>>> chunk([], 3)
[]

Constraints
-----------
- ``items`` is any sequence (list, tuple, str, range).

Approach ladder
---------------
1. Brute force — a single example test ("it works on my input"); kills almost nothing.
2. Improved   — happy-path table with several sizes; still misses empty input and size < 1.
3. Optimal    — boundary-value analysis: empty, size == len, size > len, size == 1, uneven
   split, size 0 vs negative, wrong types, plus "input not mutated". Then mutation-check the
   suite. Each case is O(n); the whole check is O(cases x mutants x n).

Follow-ups
----------
- What does a surviving mutant tell you? (A missing test, or an equivalent mutant.)
- Real tools: mutmut / cosmic-ray automate this; here we do it by hand with the stdlib.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import pytest


def chunk(items: Sequence[Any], size: int) -> list[list[Any]]:
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("size must be an int")
    if size < 1:
        raise ValueError("size must be >= 1")
    return [list(items[i:i + size]) for i in range(0, len(items), size)]


def solve(items: Sequence[Any], size: int) -> list[list[Any]]:
    return chunk(items, size)


# ------------------------------------------------------------------ test-case tables
# (case id, items, size, expected result OR expected exception type)
HAPPY = [
    ("even-split", [1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
    ("uneven-split", [1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
    ("string-input", "abcdefg", 3, [["a", "b", "c"], ["d", "e", "f"], ["g"]]),
]
EDGE = [
    ("empty-input", [], 3, []),
    ("size-one", [7, 8], 1, [[7], [8]]),
    ("size-equals-len", [1, 2, 3], 3, [[1, 2, 3]]),
    ("size-exceeds-len", [1, 2], 5, [[1, 2]]),
    ("tuple-input", (1, 2, 3), 2, [[1, 2], [3]]),
]
ERROR = [
    ("size-zero", [1, 2], 0, ValueError),
    ("size-negative", [1, 2], -1, ValueError),
    ("size-float", [1, 2], 2.0, TypeError),
    ("size-bool", [1, 2], True, TypeError),
]
CATEGORIES = {"happy": HAPPY, "edge": EDGE, "error": ERROR}


def case_passes(impl: Callable, items: Any, size: Any, expected: Any) -> bool:
    """Run one table row against ``impl``; True if the implementation behaves as specified."""
    original = list(items) if isinstance(items, list) else items
    try:
        result = impl(items, size)
    except Exception as exc:  # noqa: BLE001 - we are classifying behaviour
        return isinstance(expected, type) and isinstance(exc, expected)
    if isinstance(expected, type):
        return False
    return result == expected and (not isinstance(items, list) or items == original)


# ------------------------------------------------------------------ mutants (planted bugs)
def mutant_drop_last_chunk(items, size):  # off-by-one in range()
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError
    if size < 1:
        raise ValueError
    return [list(items[i:i + size]) for i in range(0, len(items) - size, size)]


def mutant_no_validation(items, size):  # forgot the guards
    # size=0 still raises ValueError -- but only by accident, from range(); size=-1 returns [].
    return [list(items[i:i + size]) for i in range(0, len(items), size)]


def mutant_drop_partial(items, size):  # silently loses the remainder
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError
    if size < 1:
        raise ValueError
    full = len(items) - len(items) % size
    return [list(items[i:i + size]) for i in range(0, full, size)]


def mutant_short_input_shortcut(items, size):  # "optimisation" that breaks empty input
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError
    if size < 1:
        raise ValueError
    if len(items) <= size:
        return [list(items)]
    return [list(items[i:i + size]) for i in range(0, len(items), size)]


def mutant_accepts_floats(items, size):  # int(size) hides a type error
    size = int(size)
    if size < 1:
        raise ValueError
    return [list(items[i:i + size]) for i in range(0, len(items), size)]


MUTANTS = {
    "drop_last_chunk": mutant_drop_last_chunk,
    "no_validation": mutant_no_validation,
    "drop_partial": mutant_drop_partial,
    "short_input_shortcut": mutant_short_input_shortcut,
    "accepts_floats": mutant_accepts_floats,
}


def mutation_report() -> dict[str, list[str]]:
    """For each mutant, the categories whose cases detect (kill) it."""
    report: dict[str, list[str]] = {}
    for name, impl in MUTANTS.items():
        report[name] = [
            category
            for category, table in CATEGORIES.items()
            if any(not case_passes(impl, items, size, exp) for _, items, size, exp in table)
        ]
    return report


# ------------------------------------------------------------------ embedded pytest suite
def _params(table):
    return [pytest.param(items, size, exp, id=case_id) for case_id, items, size, exp in table]


@pytest.mark.parametrize("items, size, expected", _params(HAPPY) + _params(EDGE))
def test_results(items, size, expected):
    assert chunk(items, size) == expected


@pytest.mark.parametrize("items, size, error", _params(ERROR))
def test_errors(items, size, error):
    with pytest.raises(error):
        chunk(items, size)


def test_input_not_mutated():
    data = [1, 2, 3]
    chunk(data, 2)
    assert data == [1, 2, 3]


def test_every_mutant_is_killed():
    assert all(mutation_report().values())


def main() -> None:
    print("chunk([1, 2, 3, 4, 5], 2) =", chunk([1, 2, 3, 4, 5], 2))
    print("chunk('abcdefg', 3)      =", chunk("abcdefg", 3))
    print("chunk([], 3)             =", chunk([], 3))
    print()
    print("Mutation check (which test category kills each planted bug):")
    for name, killers in mutation_report().items():
        status = "killed by " + ", ".join(killers) if killers else "SURVIVED"
        print(f"  {name:<22} {status}")
    happy_only = sum("happy" in k for k in mutation_report().values())
    print(f"  a happy-path-only suite would kill {happy_only}/{len(MUTANTS)} mutants")
    print()
    from ch31_testkit import print_results, run_embedded_tests

    print_results(run_embedded_tests(__file__))


if __name__ == "__main__":
    main()
