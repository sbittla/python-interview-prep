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

Approach ladder
---------------
1. Brute force — for each day scan forward to the first warmer day. O(n^2) worst case
   (a cooling streak), O(1) extra.
2. Improved   — scan right to left and *jump*: to find the next warmer day after ``i``,
   start at ``j = i + 1`` and follow ``j += answer[j]`` past days that are not warmer.
   O(n) amortised, O(1) extra beyond the output. Clever, but harder to justify on a
   whiteboard.
3. Optimal    — left to right with a stack of indices still waiting for a warmer day
   (temperatures non-increasing bottom→top). Today pops every colder day and writes
   ``today - that_day``. Each index pushed once, popped at most once: O(n) time, O(n) space.
   Why move up: rung 3 is the standard monotonic-stack template; the same loop answers next
   greater value, distance, or index with a one-line change.

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
    n = len(temps)
    out = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temps[j] > temps[i]:
                out[i] = j - i
                break
    return out


def jump_back(temps: list[int]) -> list[int]:
    n = len(temps)
    out = [0] * n
    for i in range(n - 2, -1, -1):
        j = i + 1
        while temps[j] <= temps[i] and out[j] > 0:
            j += out[j]                        # skip a block that is not warmer
        if temps[j] > temps[i]:
            out[i] = j - i
    return out


def days_until_warmer(temps: list[int]) -> list[int]:
    out = [0] * len(temps)
    stack: list[int] = []                      # indices waiting for a warmer day
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out


def trace(temps: list[int]) -> list[str]:
    """The stack algorithm again, logging each step (used for the chapter's ASCII trace)."""
    lines = [f"{'i':>2} {'t':>3}  {'popped (day:wait)':<20} stack after (temps)"]
    out = [0] * len(temps)
    stack: list[int] = []
    for i, t in enumerate(temps):
        popped = []
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
            popped.append(f"{j}:{out[j]}")
        stack.append(i)
        lines.append(f"{i:>2} {t:>3}  {' '.join(popped) or '-':<20} {[temps[k] for k in stack]}")
    return lines


def main() -> None:
    temps = [73, 74, 75, 71, 69, 72, 76, 73]
    print("\n".join(trace(temps)))
    print(f"answer {days_until_warmer(temps)}")
    for case in (temps, [30, 40, 50, 60], [60, 50, 40, 30], [50, 50, 51], []):
        ans = days_until_warmer(case)
        print(f"{case!s:<34} -> {ans}  agree={ans == brute_force(case) == jump_back(case)}")


if __name__ == "__main__":
    main()
