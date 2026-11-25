"""
Exercise 09 — Meeting rooms: heap vs line sweep                  [Tier: ★ Core]
Chapter 17 · Pattern: min-heap of end times; sweep over +1/-1 events · Target time: 25 min

Problem
-------
Meetings are half-open intervals [start, end) with start < end: a meeting ending at 10 frees
its room for one starting at 10.
1. min_rooms(meetings)      the fewest rooms needed to hold all meetings.
2. busiest(meetings)        (count, time): the maximum number of simultaneous meetings and
                            the earliest time at which it is reached ((0, None) if empty).
3. assign_rooms(meetings)   a room number (0, 1, ...) for each meeting, in input order, using
                            min_rooms rooms; a freed room with the lowest number is reused.

Examples
--------
>>> min_rooms([[0, 30], [5, 10], [15, 20]]), min_rooms([[1, 2], [2, 3]])
(2, 1)
>>> busiest([[1, 5], [2, 6], [4, 8], [6, 9]])
(3, 4)
>>> assign_rooms([[0, 30], [5, 10], [15, 20]])
[0, 1, 1]

Constraints
-----------
- 0 <= n <= 10^5; integers.

Hints
-----
- Heap: sort by start; the heap holds end times of meetings in progress. Before placing a
  meeting, pop every end <= its start (those rooms are free).
- Two pointers: sort starts and ends separately; before counting a start, release every
  end <= it (half-open). No heap needed when you only want the count.
- Sweep: one event (time, +1) per start and (time, -1) per end. Sort, then keep a running sum.
  At equal times the END must be processed first — with tuples, -1 sorts before +1 for free.

Approach ladder
---------------
1. Brute force — the maximum overlap is reached at some start time; for each start count the
   meetings that contain it. O(n^2).
2. Heap       — sort by start, min-heap of end times. O(n log n) time, O(n) heap. Also yields
   the room assignment if the heap stores (end, room).
2b. Two pointers — sort starts and ends separately; walk the starts, releasing every end
   <= the current start first. O(n log n) for the sorts, O(n) extra. Counts rooms but
   cannot say which meeting uses which room.
3. Line sweep — 2n sorted events, running count. O(n log n) time, O(n) events; no heap, and
   the same loop answers "when is it busiest" and generalises to weighted loads.
   Why move between rungs: brute force re-scans every meeting per start; sorting once lets a
   single pass see each change in occupancy exactly once.

Wrong-but-tempting
------------------
- Sweep with starts before ends at equal times (see sweep_wrong_tie): [1, 2), [2, 3) needs 2
  rooms instead of 1. For CLOSED intervals that order is the right one — the tie rule
  encodes the convention.
- Heap version with `ends[0] < s`: back-to-back meetings are treated as overlapping, which
  is the closed convention, not the half-open one the problem states.
- Counting overlaps pairwise ("how many meetings does each meeting overlap") — overlap is not
  transitive, so the maximum pairwise degree overestimates rooms.

Follow-ups
----------
- Can one person attend all? Sort by start; check each start >= previous end.
- Rooms with capacities, or meetings that must keep the same room for a series.
"""
from __future__ import annotations

import heapq


def min_rooms_brute(meetings: list[list[int]]) -> int:
    return max((sum(s <= t < e for s, e in meetings) for t, _ in meetings), default=0)


def min_rooms_heap(meetings: list[list[int]]) -> int:
    rooms, ends = 0, []                        # ends: min-heap of meetings in progress
    for s, e in sorted(meetings):
        while ends and ends[0] <= s:           # half-open: ending at s frees the room
            heapq.heappop(ends)
        heapq.heappush(ends, e)
        rooms = max(rooms, len(ends))
    return rooms


def min_rooms_two_pointers(meetings: list[list[int]]) -> int:
    starts = sorted(s for s, _ in meetings)
    ends = sorted(e for _, e in meetings)
    rooms = best = j = 0
    for s in starts:                           # next event is a start...
        while ends[j] <= s:                    # ...after every end at or before it
            rooms -= 1
            j += 1
        rooms += 1
        best = max(best, rooms)
    return best


def events(meetings: list[list[int]]) -> list[tuple[int, int]]:
    return sorted([(s, +1) for s, _ in meetings] + [(e, -1) for _, e in meetings])


def min_rooms(meetings: list[list[int]]) -> int:
    best = cur = 0
    for _, delta in events(meetings):          # at equal times -1 (end) sorts first
        cur += delta
        best = max(best, cur)
    return best


def busiest(meetings: list[list[int]]) -> tuple[int, int | None]:
    best, when, cur = 0, None, 0
    for t, delta in events(meetings):
        cur += delta
        if cur > best:
            best, when = cur, t
    return best, when


def sweep_wrong_tie(meetings: list[list[int]]) -> int:
    """WRONG for half-open meetings: starts are processed before ends at equal times."""
    evs = sorted([(s, 0) for s, _ in meetings] + [(e, 1) for _, e in meetings])
    best = cur = 0
    for _, kind in evs:
        cur += 1 if kind == 0 else -1
        best = max(best, cur)
    return best


def assign_rooms(meetings: list[list[int]]) -> list[int]:
    room_of = [0] * len(meetings)
    busy: list[tuple[int, int]] = []           # (end, room) of meetings in progress
    free: list[int] = []                       # released room numbers, smallest first
    next_room = 0
    for i in sorted(range(len(meetings)), key=lambda k: meetings[k]):
        s, e = meetings[i]
        while busy and busy[0][0] <= s:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
        else:
            room, next_room = next_room, next_room + 1
        room_of[i] = room
        heapq.heappush(busy, (e, room))
    return room_of


def main() -> None:
    cases = [[[0, 30], [5, 10], [15, 20]], [[1, 2], [2, 3]], [[1, 5], [2, 6], [4, 8], [6, 9]], []]
    for m in cases:
        print(f"{str(m):34} rooms: brute={min_rooms_brute(m)} heap={min_rooms_heap(m)} "
              f"two_ptr={min_rooms_two_pointers(m)} sweep={min_rooms(m)} | busiest={busiest(m)}")
    print("events for [[1, 2], [2, 3]]:", events([[1, 2], [2, 3]]))
    print("wrong tie rule on [[1, 2], [2, 3]]:", sweep_wrong_tie([[1, 2], [2, 3]]))
    m = [[0, 30], [5, 10], [15, 20], [10, 15], [30, 40]]
    print("assign_rooms", m, "->", assign_rooms(m))


if __name__ == "__main__":
    main()
