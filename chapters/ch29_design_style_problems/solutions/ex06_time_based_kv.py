"""
Exercise 06 — Time-Based Key-Value Store           [Tier: ★ Core]
Chapter 29 · Pattern: hash map of sorted lists + binary search · Target time: 20 min

Problem
-------
Build a store that keeps every version of a key:

    tm = TimeMap()
    tm.set(key, value, timestamp)   -> None
    tm.get(key, timestamp)          -> the value set at the largest timestamp_prev <= timestamp,
                                       or "" if there is none

Calls to `set` for the same key arrive with strictly increasing timestamps (the common
interview assumption). Extension: `set_any_order` accepts out-of-order timestamps, and
`history(key, t1, t2)` lists every (timestamp, value) with t1 <= timestamp <= t2.

Examples
--------
>>> tm = TimeMap()
>>> tm.set("cfg", "v1", 10); tm.set("cfg", "v2", 20)
>>> tm.get("cfg", 5), tm.get("cfg", 10), tm.get("cfg", 15), tm.get("cfg", 99)
('', 'v1', 'v1', 'v2')

Constraints
-----------
- Up to 2 * 10**5 calls; timestamps are positive integers.

Approach ladder
---------------
1. Brute force — key -> list of (ts, value); get scans the whole list. O(n) per get.
2. Improved   — scan backwards from the newest version and stop early: still O(n) worst.
3. Optimal    — the per-key list is already sorted (timestamps increase), so get is a
   `bisect_right` on the timestamps: O(log n). Keep timestamps and values in two parallel
   lists so bisect compares plain ints.

Hints
-----
- `i = bisect_right(times, t)`; the answer is `values[i - 1]` when i > 0.
- For out-of-order inserts use `bisect.insort` (O(n) insert) or note that a balanced tree
  / skip list would make it O(log n).

Follow-ups
----------
- Memory limits: keep only the last N versions, or versions newer than a TTL.
- This is exactly how MVCC databases answer "read as of snapshot time T".
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import defaultdict


class TimeMapBrute:
    def __init__(self) -> None:
        self.data: defaultdict[str, list[tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.data[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        best_t, best_v = -1, ""
        for t, v in self.data.get(key, []):
            if best_t < t <= timestamp:
                best_t, best_v = t, v
        return best_v


class TimeMap:
    def __init__(self) -> None:
        self.times: defaultdict[str, list[int]] = defaultdict(list)
        self.values: defaultdict[str, list[str]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        times = self.times[key]
        if times and timestamp <= times[-1]:
            raise ValueError("timestamps must increase; use set_any_order")
        times.append(timestamp)
        self.values[key].append(value)

    def set_any_order(self, key: str, value: str, timestamp: int) -> None:
        times, values = self.times[key], self.values[key]
        i = bisect_left(times, timestamp)
        if i < len(times) and times[i] == timestamp:
            values[i] = value                       # overwrite same timestamp
        else:
            times.insert(i, timestamp)
            values.insert(i, value)

    def get(self, key: str, timestamp: int) -> str:
        times = self.times.get(key)
        if not times:
            return ""
        i = bisect_right(times, timestamp)
        return self.values[key][i - 1] if i else ""

    def history(self, key: str, t1: int, t2: int) -> list[tuple[int, str]]:
        times = self.times.get(key, [])
        lo, hi = bisect_left(times, t1), bisect_right(times, t2)
        return list(zip(times[lo:hi], self.values[key][lo:hi]))


def main() -> None:
    for cls in (TimeMapBrute, TimeMap):
        tm = cls()
        tm.set("cfg", "v1", 10)
        tm.set("cfg", "v2", 20)
        tm.set("cfg", "v3", 30)
        print(f"{cls.__name__:<13}", [tm.get("cfg", t) for t in (5, 10, 15, 20, 29, 30, 99)],
              "missing key ->", repr(tm.get("nope", 10)))

    tm = TimeMap()
    for t, v in [(5, "a"), (1, "b"), (3, "c"), (3, "C")]:
        tm.set_any_order("k", v, t)
    print("out-of-order inserts -> versions:", tm.history("k", 0, 100))
    print("history(k, 2, 4):", tm.history("k", 2, 4))
    try:
        tm.set("k", "late", 4)
    except ValueError as exc:
        print("strict set rejects old timestamp:", exc)


if __name__ == "__main__":
    main()
