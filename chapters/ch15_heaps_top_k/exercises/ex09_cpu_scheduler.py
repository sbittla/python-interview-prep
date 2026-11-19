"""
Exercise 09 — Single-CPU Job Scheduler (Shortest Job First)        [Tier: ★ Core]
Chapter 15 · Pattern: event simulation with arrival queue + ready heap · Target time: 25 min

Problem
-------
Jobs are (arrival_time, duration) pairs, job i is the i-th pair. One CPU runs one job at a
time to completion. Whenever the CPU is free it picks, among jobs that have ARRIVED
(arrival <= now), the one with the shortest duration, ties broken by smaller index. If no
job has arrived it idles until the next arrival. Return the order in which job indices run.

(The cooldown "task scheduler" — same letter must wait n ticks — is taught in §20.6 with a
heap plus a cooldown queue; this exercise is the arrival-time sibling of that simulation.)

Examples
--------
>>> solve([(1, 2), (2, 4), (3, 2), (4, 1)])
[0, 2, 3, 1]
>>> solve([(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)])
[4, 3, 2, 0, 1]

Constraints
-----------
- 0 <= n <= 10^5; arrival >= 0, duration >= 1; ints.

Hints
-----
- Two structures, two jobs: the queue answers "who arrives next?", the heap answers
  "who runs next?".
- Do not advance time one tick at a time; durations can be 10^9.

Follow-ups
----------
- Preemptive version (shortest REMAINING time first): push the running job back with its
  remaining time when a shorter one arrives.
- k CPUs: add a heap of (free_at, cpu_id), like the meeting-room assignment (ex07).
- Average waiting time: record start - arrival per job.

Wrong-but-tempting
------------------
- Sorting all jobs by duration up front: ignores that a short job may not have arrived.
- Ticking time by 1: correct but O(total time), which can be astronomically large.
"""
from __future__ import annotations

import heapq
import random
from collections import deque

Job = tuple[int, int]


def brute_force(jobs: list[Job]) -> list[int]:
    raise NotImplementedError("TODO")


def solve(jobs: list[Job]) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[(1, 2), (2, 4), (3, 2), (4, 1)],
             [(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)],
             [(0, 5), (100, 1), (1, 3), (1, 3)],
             [(5, 1)], []]
    for jobs in cases:
        ans = solve(jobs)
        print(f"{jobs} -> {ans}  agree={ans == brute_force(jobs)}")
    rng = random.Random(15)
    ok = True
    for _ in range(300):
        jobs = [(rng.randint(0, 15), rng.randint(1, 4)) for _ in range(rng.randint(0, 12))]
        ok &= solve(jobs) == brute_force(jobs)
    print("300 random cases (many equal durations/arrivals) agree:", ok)
    huge = [(0, 10**9), (1, 1), (2 * 10**9, 3)]
    print("huge times, no tick loop:", solve(huge))


if __name__ == "__main__":
    main()
