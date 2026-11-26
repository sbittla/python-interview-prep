"""
Exercise 02 — Fix a Generated Dedupe (Mutable Default, Hidden O(n²)) [Tier: ★ Core]
Chapter 46 · Pattern: probe objects that count work → fix → complexity · Target time: 20 min

Problem
-------
Prompt: "remove duplicates from a list, keep the first occurrence of each,
keep the order". The assistant returned generated_dedupe (below, given). Its
output on a single call is correct, so example-based tests pass. It has two
defects a reviewer must catch: state leaks between calls (the mutable default,
→ §7.1) and `item not in seen` scans a list, so the loop is O(n²) (→ §7.16).

1. leaks_state(fn) -> True if calling fn twice on the same fresh input gives
   a different answer the second time (or a wrong answer at all). Use fresh objects (object()) so the
   result does not depend on what earlier calls left behind.
2. eq_calls(fn, n) -> how many times __eq__ runs when fn dedupes n distinct
   items. Count it with a small probe class whose __eq__ increments a counter
   and whose __hash__ is distinct per item. This measures complexity without
   a stopwatch, so it is deterministic.
3. dedupe(items) -> the fixed function: no shared state, expected O(n).
   COMPLEXITY -> its time and space.

Examples
--------
>>> generated_dedupe([3, 1, 3, 2, 1])
[3, 1, 2]
>>> generated_dedupe([3, 4])          # second call: 3 is "already seen"
[4]
>>> dedupe([3, 1, 3, 2, 1]), dedupe([3, 4])
([3, 1, 2], [3, 4])

Constraints
-----------
- dedupe requires hashable items (the generated version did not). That is a
  real trade-off; say it out loud (exercise 06 scores that explanation).

Approach ladder
---------------
1. Brute force — test one call on one list: passes, both bugs survive.
2. Improved   — call it twice: exposes the leaked state. Time a big input:
   shows "slow" but is noisy and machine-dependent.
3. Optimal    — count __eq__ calls with a probe class: n(n-1)/2 for the list
   scan, 0 for a set (distinct hashes never reach __eq__). Fix with a local
   set (or dict.fromkeys, which also keeps order): O(n) expected time, O(n)
   space.

Follow-ups
----------
- Unhashable items (lists, dicts)? Dedupe on a hashable key (tuple(item)) or
  accept O(n²) and say so.
- Why is the eq count 0 and not n? Set lookup compares stored hashes first
  and only calls __eq__ when the full hashes are equal.
- Adversarial hashes (all equal) push a set back to O(n²): expected, not
  worst-case, O(1) per lookup (→ §6.5).
"""
from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable


# --- given: the generated code (do not edit) -----------------------------------
def generated_dedupe(items, seen=[]):
    """AI-generated: remove duplicates, keeping the first occurrence and the order."""
    result = []
    for item in items:
        if item not in seen:
            seen.append(item)
            result.append(item)
    return result


# --- your bug-finding tools --------------------------------------------------------
def leaks_state(fn: Callable[[list], list]) -> bool:
    a, b = object(), object()
    first = fn([a, b, a])
    second = fn([a, b, a])
    return first != [a, b] or second != [a, b]


class _Probe:
    """Distinct hash and identity per instance; counts every __eq__ call in a box."""

    def __init__(self, key: int, box: list[int]) -> None:
        self.key, self.box = key, box

    def __hash__(self) -> int:
        return self.key

    def __eq__(self, other: object) -> bool:
        self.box[0] += 1
        return self is other      # every probe is distinct, even across calls


def eq_calls(fn: Callable[[list], list], n: int) -> int:
    box = [0]
    fn([_Probe(i, box) for i in range(n)])
    return box[0]


# --- the fix ---------------------------------------------------------------------------
def dedupe(items: Iterable[Hashable]) -> list:
    seen: set = set()             # local: a fresh set on every call
    result = []
    for item in items:
        if item not in seen:      # expected O(1) hash lookup
            seen.add(item)
            result.append(item)
    return result


COMPLEXITY = {"time": "O(n)", "space": "O(n)"}


def main() -> None:
    print("one call looks right:", generated_dedupe([3, 1, 3, 2, 1]))
    print("second call:", generated_dedupe([3, 4]), "(expected [3, 4])")
    print("leaks state: generated", leaks_state(generated_dedupe),
          "| fixed", leaks_state(dedupe))
    fresh = lambda xs: generated_dedupe(xs, [])        # isolate the cost from the leak
    for n in (100, 200, 400):
        print(f"n={n}: __eq__ calls generated={eq_calls(fresh, n)}"
              f" fixed={eq_calls(dedupe, n)}")
    print("fixed:", dedupe([3, 1, 3, 2, 1]), dedupe([3, 4]), dedupe([]))
    print("complexity:", COMPLEXITY)


if __name__ == "__main__":
    main()
