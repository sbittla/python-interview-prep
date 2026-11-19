"""
Exercise 06 — Days Until Warmer                               [Tier: ★ Core]
Chapter 12 · Pattern: monotonic stack (distance to next greater) · Target time: 20 min

Problem
-------
Given daily temperatures, return a list where entry ``i`` is how many days you must wait after
day ``i`` for a strictly warmer day, or 0 if no warmer day ever comes.

Examples
--------
>>> days_until_warmer([73, 74, 75, 71, 69, 72, 76, 73])
[1, 1, 4, 2, 1, 1, 0, 0]

Constraints
-----------
- 0 <= len(temps) <= 10**5; 30 <= temps[i] <= 100.

Hints
-----
- Same template as next greater element, but write a distance instead of a value.
- Right-to-left alternative: jump forward using answers you already computed.

Wrong-but-tempting
------------------
- Writing the *temperature* instead of the distance (``out[j] = t`` instead of ``i - j``).
- ``<=`` in the pop condition: an equal temperature is not warmer.
- Breaking out of the while loop after the first pop: several cold days can be resolved by
  one warm day.

Follow-ups
----------
- Return the date of the next warmer day (store indices, map to dates).
- Stream version: answers for a day are only known later, so emit them as days are popped.
"""
from __future__ import annotations


def brute_force(temps: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def jump_back(temps: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def days_until_warmer(temps: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def trace(temps: list[int]) -> list[str]:
    """The stack algorithm again, logging each step (used for the chapter's ASCII trace)."""
    raise NotImplementedError("TODO")


def main() -> None:
    temps = [73, 74, 75, 71, 69, 72, 76, 73]
    print("\n".join(trace(temps)))
    print(f"answer {days_until_warmer(temps)}")
    for case in (temps, [30, 40, 50, 60], [60, 50, 40, 30], [50, 50, 51], []):
        ans = days_until_warmer(case)
        print(f"{case!s:<34} -> {ans}  agree={ans == brute_force(case) == jump_back(case)}")


if __name__ == "__main__":
    main()
