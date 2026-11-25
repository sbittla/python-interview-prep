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

Follow-ups
----------
- Can one person attend all? Sort by start; check each start >= previous end.
- Rooms with capacities, or meetings that must keep the same room for a series.
"""
from __future__ import annotations

import heapq


def min_rooms_brute(meetings: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_rooms_heap(meetings: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_rooms_two_pointers(meetings: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def events(meetings: list[list[int]]) -> list[tuple[int, int]]:
    raise NotImplementedError("TODO")


def min_rooms(meetings: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def busiest(meetings: list[list[int]]) -> tuple[int, int | None]:
    raise NotImplementedError("TODO")


def sweep_wrong_tie(meetings: list[list[int]]) -> int:
    """WRONG for half-open meetings: starts are processed before ends at equal times."""
    raise NotImplementedError("TODO")


def assign_rooms(meetings: list[list[int]]) -> list[int]:
    raise NotImplementedError("TODO")


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
