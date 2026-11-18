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

Approach ladder
---------------
1. Simulation — each tick pick the available task with the most remaining copies (max-heap),
   park it in a cooldown queue until it is allowed again. O(T log k) time where T is the
   answer. Produces the schedule.
2. Optimal formula — let f = highest frequency and m = how many letters have it. The most
   frequent letters form f-1 full frames of width n+1 plus a last frame of width m:
   answer = max(len(tasks), (f - 1) * (n + 1) + m). O(len(tasks)) time, O(1) space.

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
    counts = Counter(tasks)
    heap = [(-c, t) for t, c in counts.items()]   # most remaining first, ties alphabetical
    heapq.heapify(heap)
    cooldown: deque[tuple[int, int, str]] = deque()  # (ready_time, -remaining, task)
    out: list[str] = []
    time = 0
    while heap or cooldown:
        while cooldown and cooldown[0][0] <= time:
            _, c, t = cooldown.popleft()
            heapq.heappush(heap, (c, t))
        if heap:
            c, t = heapq.heappop(heap)
            out.append(t)
            if c + 1 < 0:
                cooldown.append((time + n + 1, c + 1, t))
        else:
            out.append("_")
        time += 1
    return "".join(out)


def least_interval(tasks: list[str], n: int) -> int:
    if not tasks:
        return 0
    counts = Counter(tasks)
    f = max(counts.values())
    m = sum(1 for c in counts.values() if c == f)
    return max(len(tasks), (f - 1) * (n + 1) + m)


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
