"""
Exercise 09 — Removing Items While Looping              [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (iteration) · Target time: 8 min

Problem
-------
1. `remove_evens(nums)` must remove every even number from `nums` IN PLACE and
   return the same list. The buggy version calls `nums.remove(x)` inside
   `for x in nums`, which shifts later items left so the loop skips some.
2. `drop_zero_counts(counts)` must delete every key whose value is 0 from the
   dict IN PLACE. The buggy version deletes while iterating over the dict, which
   raises `RuntimeError: dictionary changed size during iteration`.

Examples
--------
>>> remove_evens([2, 4, 6, 1])
[1]
>>> drop_zero_counts({"a": 0, "b": 2, "c": 0})
{'b': 2}

Constraints
-----------
- 0 <= len(nums) <= 10**5

Approach ladder
---------------
1. Buggy  — mutate the container you are iterating over.
2. Fixed  — build the kept items and assign back with slice assignment
   (`nums[:] = [...]`, keeps the same list object, O(n)); for dicts, iterate over
   a snapshot `list(counts)` of the keys.
3. Alternative — iterate backwards by index when deleting from a list
   (`for i in range(len(nums) - 1, -1, -1)`), but each `del` is O(n) → O(n^2) worst case.

Follow-ups
----------
- Why does `nums.remove(x)` inside the loop skip elements? (The list iterator
  keeps an index; deleting shifts the next element into the current index.)
- Is modifying VALUES (not keys) while iterating a dict safe? (Yes.)
"""
from __future__ import annotations


def buggy_remove_evens(nums: list[int]) -> list[int]:
    for x in nums:
        if x % 2 == 0:
            nums.remove(x)
    return nums


def buggy_drop_zero_counts(counts: dict[str, int]) -> dict[str, int]:
    for key in counts:
        if counts[key] == 0:
            del counts[key]
    return counts


def remove_evens(nums: list[int]) -> list[int]:
    """Keep odd numbers; same list object; O(n)."""
    nums[:] = [x for x in nums if x % 2 != 0]
    return nums


def drop_zero_counts(counts: dict[str, int]) -> dict[str, int]:
    """Delete zero-valued keys in place by iterating over a snapshot of keys."""
    for key in list(counts):
        if counts[key] == 0:
            del counts[key]
    return counts


def main() -> None:
    print("buggy remove_evens([2, 4, 6, 1]):", buggy_remove_evens([2, 4, 6, 1]))
    print("fixed remove_evens([2, 4, 6, 1]):", remove_evens([2, 4, 6, 1]))
    try:
        buggy_drop_zero_counts({"a": 0, "b": 2, "c": 0})
    except RuntimeError as exc:
        print("buggy drop_zero_counts:", type(exc).__name__, "-", exc)
    print("fixed drop_zero_counts:", drop_zero_counts({"a": 0, "b": 2, "c": 0}))


if __name__ == "__main__":
    main()
