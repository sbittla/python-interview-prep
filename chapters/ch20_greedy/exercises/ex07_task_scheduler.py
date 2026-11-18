"""
Exercise 07 — Task Scheduler with Cooldown                         [Tier: ◆ Extended]
Chapter 20 · Pattern: greedy with heap + cooldown queue, counting formula · Target time: 25 min

Problem
-------
A CPU runs one unit-time task per tick, or idles. Tasks are letters; two runs of the same
letter must be separated by at least `n` ticks (n idle-or-other ticks in between). Return the
minimum number of ticks to finish all tasks, and (for the simulation) one optimal schedule
with '_' for idle ticks.

Examples
--------
>>> least_interval(list("AAABBB"), 2)
8
>>> least_interval(list("AAABBB"), 0)
6

Constraints
-----------
- 1 <= len(tasks) <= 10^4, 0 <= n <= 100.

Hints
-----
- Draw the most frequent letter first: A _ _ A _ _ A. The gaps are the only place other
  tasks can go.
- If there are more tasks than gap slots, no idling is needed at all.

Follow-ups
----------
- Tasks must run in the given order (no reordering): simulate with a dict of next-allowed
  time; this is not a greedy-choice problem any more.
- Return the schedule itself (the simulation does this).
"""
from __future__ import annotations

import heapq
from collections import Counter, deque


def schedule(tasks: list[str], n: int) -> str:
    raise NotImplementedError("TODO")


def least_interval(tasks: list[str], n: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [("AAABBB", 2), ("AAABBB", 0), ("AAAAAABCDEFG", 2), ("AAABBBCCD", 2), ("A", 5), ("AAA", 3)]
    for s, n in cases:
        sched = schedule(list(s), n)
        print(f"tasks={s:<13} n={n}  formula={least_interval(list(s), n):>2}  "
              f"simulation={len(sched):>2}  schedule={sched}")
    print()
    print("frame picture for AAABBB, n=2 (f=3, m=2):")
    print("  [A B _] [A B _] [A B]  -> (3-1)*(2+1) + 2 = 8")


if __name__ == "__main__":
    main()
