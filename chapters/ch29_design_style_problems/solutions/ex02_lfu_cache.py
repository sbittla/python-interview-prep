"""
Exercise 02 — LFU Cache                            [Tier: ◆ Extended]
Chapter 29 · Pattern: hash map of frequency buckets · Target time: 35 min

Problem
-------
Design a fixed-capacity cache that evicts the *least frequently used* key. Every
successful `get` and every `put` increments the key's use count. When several keys share
the minimum count, evict the one among them that was used least recently.

    cache = LFUCache(capacity)
    cache.get(key)        -> value, or -1 if absent
    cache.put(key, value) -> None

Examples
--------
>>> c = LFUCache(2)
>>> c.put(1, 1); c.put(2, 2); c.get(1)     # freq(1)=2, freq(2)=1
1
>>> c.put(3, 3)                             # evicts key 2 (lowest frequency)
>>> c.get(2), c.get(3)
(-1, 3)

Constraints
-----------
- 0 <= capacity <= 10**4 (capacity 0 stores nothing).
- get and put must be O(1) average time.

Approach ladder
---------------
1. Brute force — store (value, freq, last_used_tick) per key; on eviction scan all keys
   for min (freq, tick): O(1) get, O(n) evicting put.
2. Improved   — a heap of (freq, tick, key) with lazy deletion: O(log n) per operation,
   plus stale entries to clean up.
3. Optimal    — `key -> (value, freq)` plus `freq -> OrderedDict of keys` (each bucket is
   itself an LRU list) and a `min_freq` integer. Touching a key moves it from bucket f
   to bucket f+1 in O(1); eviction pops the oldest key of bucket `min_freq` in O(1).
   `min_freq` only changes in two easy ways: it becomes 1 on insert of a new key, or
   min_freq+1 when the last key of the min bucket is touched.

Hints
-----
- Write one helper `_touch(key)` that bumps a key's frequency; both get and put use it.
- After a brand-new insert, `min_freq` is always 1.
- Delete empty buckets so `freq -> keys` never holds empty OrderedDicts.

Follow-ups
----------
- How would you age frequencies so a key that was hot last week can be evicted? (Decay
  counters periodically, or use a window-TinyLFU style admission policy.)
- Compare LRU vs LFU hit rate on a scan-heavy workload (LFU resists one-off scans).
"""
from __future__ import annotations

from collections import OrderedDict, defaultdict
from typing import Any, Hashable


class LFUCacheBrute:
    """Rung 1: scan for the (freq, tick) minimum on eviction."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.tick = 0
        self.entries: dict[Hashable, list] = {}     # key -> [value, freq, last_tick]

    def get(self, key: Hashable) -> Any:
        if key not in self.entries:
            return -1
        self.tick += 1
        e = self.entries[key]
        e[1] += 1
        e[2] = self.tick
        return e[0]

    def put(self, key: Hashable, value: Any) -> None:
        if self.capacity == 0:
            return
        self.tick += 1
        if key in self.entries:
            e = self.entries[key]
            e[0], e[1], e[2] = value, e[1] + 1, self.tick
            return
        if len(self.entries) == self.capacity:
            victim = min(self.entries, key=lambda k: (self.entries[k][1], self.entries[k][2]))
            del self.entries[victim]
        self.entries[key] = [value, 1, self.tick]


class LFUCache:
    """Rung 3: O(1) per operation with frequency buckets."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.values: dict[Hashable, Any] = {}
        self.freq: dict[Hashable, int] = {}
        self.buckets: defaultdict[int, OrderedDict] = defaultdict(OrderedDict)
        self.min_freq = 0

    def _touch(self, key: Hashable) -> None:
        f = self.freq[key]
        bucket = self.buckets[f]
        del bucket[key]
        if not bucket:
            del self.buckets[f]
            if self.min_freq == f:
                self.min_freq = f + 1
        self.freq[key] = f + 1
        self.buckets[f + 1][key] = None          # appended = most recent within bucket

    def get(self, key: Hashable) -> Any:
        if key not in self.values:
            return -1
        self._touch(key)
        return self.values[key]

    def put(self, key: Hashable, value: Any) -> None:
        if self.capacity == 0:
            return
        if key in self.values:
            self.values[key] = value
            self._touch(key)
            return
        if len(self.values) == self.capacity:
            bucket = self.buckets[self.min_freq]
            victim, _ = bucket.popitem(last=False)   # oldest among least frequent
            if not bucket:
                del self.buckets[self.min_freq]
            del self.values[victim]
            del self.freq[victim]
        self.values[key] = value
        self.freq[key] = 1
        self.buckets[1][key] = None
        self.min_freq = 1

    def snapshot(self) -> dict[int, list]:
        """freq -> keys (oldest first); handy for tests and debugging."""
        return {f: list(b) for f, b in sorted(self.buckets.items())}


def main() -> None:
    ops = [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2),
           ("get", 3), ("put", 4, 4), ("get", 1), ("get", 3), ("get", 4)]
    for cls in (LFUCacheBrute, LFUCache):
        c = cls(2)
        gets = []
        for op, *args in ops:
            result = getattr(c, op)(*args)
            if op == "get":
                gets.append(result)
        print(f"{cls.__name__:<14} gets={gets}")

    c = LFUCache(3)
    for k in "abc":
        c.put(k, k.upper())
    c.get("a"); c.get("a"); c.get("b")
    print("buckets before insert d:", c.snapshot(), "min_freq =", c.min_freq)
    c.put("d", "D")                        # evicts c (freq 1, the only one)
    print("buckets after insert d: ", c.snapshot(), "min_freq =", c.min_freq)

    zero = LFUCache(0)
    zero.put("x", 1)
    print("capacity 0 get ->", zero.get("x"))


if __name__ == "__main__":
    main()
