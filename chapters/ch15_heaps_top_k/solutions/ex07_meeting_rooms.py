"""
Exercise 07 — Minimum Meeting Rooms and Room Assignment            [Tier: ★ Core]
Chapter 15 · Pattern: sort by start + min-heap of end times · Target time: 20 min

Problem
-------
Meetings are half-open intervals [start, end) with start < end; a room freed at time t
can host a meeting starting at t.
1. `solve(meetings)` returns the minimum number of rooms so that no room hosts two
   overlapping meetings.
2. `assign_rooms(meetings)` returns, for each meeting in INPUT order, a room number
   0, 1, 2, ...: process meetings by (start, input index) and give each the lowest-numbered
   free room. It uses exactly `solve(meetings)` rooms.

Examples
--------
>>> solve([(0, 30), (5, 10), (15, 20)])
2
>>> solve([(1, 5), (5, 8)])
1
>>> assign_rooms([(0, 30), (5, 10), (15, 20)])
[0, 1, 1]

Constraints
-----------
- 0 <= len(meetings) <= 10^5; ints.

Approach ladder
---------------
1. Brute force — the peak overlap happens at some meeting's start; for each start count
   meetings with s <= start < e: O(n^2) time, O(1) extra space.
2. Optimal (heap) — sort by start; a min-heap holds end times of rooms in use. For each
   meeting, if the earliest end <= start, that room is free: `heapreplace`; otherwise push
   a new room. Answer = heap size. O(n log n) time, O(n) space.
3. Alternative (sweep) — sort starts and ends separately, walk with two pointers
   (→ §17.8, the canonical home of line sweep). Same O(n log n), no heap, but it cannot
   tell you WHICH room a meeting gets.
   Why the heap: it carries a payload (room id), so it answers the assignment follow-up.

Hints
-----
- Ties: an end at t frees a room for a start at t, so test `heap[0] <= start`.
- For assignment keep two heaps: busy (end, room) and free room ids.

Follow-ups
----------
- Rooms have capacities / meetings have sizes: becomes bin packing (heuristics only).
- Count how many meetings each room hosted (Meeting Rooms III style): the assignment
  output gives it directly.
- Online arrivals in start order: the heap version is already online.

Wrong-but-tempting
------------------
- Sorting by END time and counting overlaps with only the previous meeting: that solves
  "maximum non-overlapping meetings" (→ §20.2), not rooms.
- Using `<` instead of `<=` for the free check: back-to-back meetings need 2 rooms.
"""
from __future__ import annotations

import heapq
import random

Meeting = tuple[int, int]


def brute_force(meetings: list[Meeting]) -> int:
    return max((sum(s <= t < e for s, e in meetings) for t, _ in meetings), default=0)


def by_sweep(meetings: list[Meeting]) -> int:
    starts = sorted(s for s, _ in meetings)
    ends = sorted(e for _, e in meetings)
    rooms = best = j = 0
    for s in starts:
        while ends[j] <= s:                           # meetings that ended by s free a room
            rooms -= 1
            j += 1
        rooms += 1
        best = max(best, rooms)
    return best


def solve(meetings: list[Meeting]) -> int:
    ends: list[int] = []                              # end times of rooms in use
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)              # reuse the room that frees first
        else:
            heapq.heappush(ends, end)                 # open a new room
    return len(ends)


def assign_rooms(meetings: list[Meeting]) -> list[int]:
    order = sorted(range(len(meetings)), key=lambda i: (meetings[i][0], i))
    busy: list[tuple[int, int]] = []                  # (end, room)
    free: list[int] = []                              # free room ids (min-heap)
    next_room = 0
    out = [0] * len(meetings)
    for i in order:
        start, end = meetings[i]
        while busy and busy[0][0] <= start:           # release every room free by now
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
        else:
            room, next_room = next_room, next_room + 1
        out[i] = room
        heapq.heappush(busy, (end, room))
    return out


def main() -> None:
    cases = [[(0, 30), (5, 10), (15, 20)], [(1, 5), (5, 8)], [(7, 10), (2, 4)],
             [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)], []]
    for ms in cases:
        n = solve(ms)
        agree = n == brute_force(ms) == by_sweep(ms)
        rooms = assign_rooms(ms)
        print(f"{ms} -> rooms={n} agree={agree} assignment={rooms}")
    rng = random.Random(15)
    ok = True
    for _ in range(300):
        ms = []
        for _ in range(rng.randint(0, 12)):
            s = rng.randint(0, 20)
            ms.append((s, s + rng.randint(1, 6)))
        n = solve(ms)
        rooms = assign_rooms(ms)
        ok &= n == brute_force(ms) == by_sweep(ms) and len(set(rooms)) == n
        for r in set(rooms):                          # no two meetings in one room overlap
            mine = sorted(m for m, rr in zip(ms, rooms) if rr == r)
            ok &= all(a[1] <= b[0] for a, b in zip(mine, mine[1:]))
    print("300 random cases: counts agree, assignment valid and uses that many rooms:", ok)


if __name__ == "__main__":
    main()
