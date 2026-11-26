"""
Exercise 02 — Fix a Generated Dedupe (Mutable Default, Hidden O(n²)) [Tier: ★ Core]
Chapter 46 · Pattern: probe objects that count work → fix → complexity · Target time: 20 min

Problem
-------
Prompt: "remove duplicates from a list, keep the first occurrence of each,
keep the order". The assistant returned generated_dedupe (below, given). Its
output on a single call is correct, so example-based tests pass. It has two
defects a reviewer must catch: one about state, one about cost (→ §7.1,
→ §7.16 if you need a nudge).

1. leaks_state(fn) -> True if calling fn twice on the same fresh input gives
   a different answer the second time (or a wrong answer at all). Use fresh
   objects (object()) so the result does not depend on earlier calls.
2. eq_calls(fn, n) -> how many times __eq__ runs when fn dedupes n distinct
   items. This measures complexity without a stopwatch, so it is
   deterministic.
3. dedupe(items) -> the fixed function: no shared state, expected O(n).
   COMPLEXITY -> its time and space.

Examples
--------
>>> generated_dedupe([3, 1, 3, 2, 1])
[3, 1, 2]
>>> generated_dedupe([3, 4])          # second call: is this right?
[4]
>>> dedupe([3, 1, 3, 2, 1]), dedupe([3, 4])
([3, 1, 2], [3, 4])

Constraints
-----------
- Your dedupe may require hashable items. Note what that costs you
  (exercise 06 scores the explanation).

Hints
-----
- When is a default argument value created: per call, or once?
- eq_calls: write a tiny probe class with a distinct __hash__ per instance
  and an __eq__ that increments a shared counter (a one-element list works)
  and compares by identity, so probes from different calls never match.
- To see the per-call cost of the generated code without its leaked state,
  pass it a fresh second argument from a lambda.
- What does `in` cost on a list? On a set? Which one calls __eq__?

Follow-ups
----------
- Unhashable items (lists, dicts)? What are your options?
- Why is the eq count for a set 0 and not n?
- What do adversarial hashes (all equal) do to a set lookup (→ §6.5)?
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
    raise NotImplementedError("TODO")


def eq_calls(fn: Callable[[list], list], n: int) -> int:
    raise NotImplementedError("TODO")


# --- the fix ---------------------------------------------------------------------------
def dedupe(items: Iterable[Hashable]) -> list:
    raise NotImplementedError("TODO")


COMPLEXITY: dict[str, str] = {}   # TODO


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
