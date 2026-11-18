"""
Exercise 05 — Hit Counter                          [Tier: ★ Core]
Chapter 29 · Pattern: queue / circular buckets · Target time: 20 min

Problem
-------
Count hits received in the last 300 seconds.

    hc = HitCounter(window=300)
    hc.hit(timestamp)           -> None   (timestamps in whole seconds, non-decreasing)
    hc.get_hits(timestamp)      -> int    hits with  timestamp - window < t <= timestamp

Implement a queue version (exact, memory grows with traffic) and a bucketed version
(`window` fixed-size buckets, memory O(window) no matter how many hits per second).

Examples
--------
>>> hc = HitCounterBuckets()
>>> for t in (1, 2, 3): hc.hit(t)
>>> hc.get_hits(4), hc.get_hits(300), hc.get_hits(301), hc.get_hits(302)
(3, 3, 2, 1)

Constraints
-----------
- 1 <= timestamp <= 2 * 10**9; calls arrive in chronological order.
- Possibly many hits in the same second (think: 10**6 hits/s).

Approach ladder
---------------
1. Brute force — store every timestamp in a list; get_hits counts with a full scan. O(n).
2. Improved   — deque; pop expired timestamps from the left, return len. Amortised O(1),
   but O(hits in window) memory: a million hits per second means 300 million entries.
3. Optimal for bursty traffic — two arrays of size `window`: `times[i]` and `counts[i]`
   for slot i = t % window. A hit resets a slot whose stored time is stale. get_hits sums
   the slots whose time is still inside the window: O(window) = O(1) w.r.t. traffic.

Hints
-----
- In the bucket version, a slot is "live" if `timestamp - times[i] < window`.
- A compressed deque of (second, count) pairs is a nice middle ground.

Follow-ups
----------
- Concurrent hits: lock per slot, or per-thread counters summed on read.
- Hits per minute/hour/day at once (multiple ring buffers at different resolutions).
"""
from __future__ import annotations

from collections import deque


class HitCounterBrute:
    def __init__(self, window: int = 300) -> None:
        self.window = window
        self.hits: list[int] = []

    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def get_hits(self, timestamp: int) -> int:
        return sum(1 for t in self.hits if timestamp - self.window < t <= timestamp)


class HitCounterQueue:
    """Deque of (second, count) pairs: exact, and compact when many hits share a second."""

    def __init__(self, window: int = 300) -> None:
        self.window = window
        self.q: deque[list[int]] = deque()
        self.total = 0

    def _evict(self, timestamp: int) -> None:
        while self.q and self.q[0][0] <= timestamp - self.window:
            self.total -= self.q.popleft()[1]

    def hit(self, timestamp: int) -> None:
        if self.q and self.q[-1][0] == timestamp:
            self.q[-1][1] += 1
        else:
            self.q.append([timestamp, 1])
        self.total += 1
        self._evict(timestamp)

    def get_hits(self, timestamp: int) -> int:
        self._evict(timestamp)
        return self.total


class HitCounterBuckets:
    def __init__(self, window: int = 300) -> None:
        self.window = window
        self.times = [0] * window
        self.counts = [0] * window

    def hit(self, timestamp: int) -> None:
        i = timestamp % self.window
        if self.times[i] != timestamp:      # slot holds an old second: recycle it
            self.times[i] = timestamp
            self.counts[i] = 0
        self.counts[i] += 1

    def get_hits(self, timestamp: int) -> int:
        return sum(c for t, c in zip(self.times, self.counts)
                   if timestamp - t < self.window)


def main() -> None:
    hits = [1, 2, 3, 3, 3, 300, 301, 450, 600]
    queries = [3, 4, 300, 301, 302, 450, 600, 601, 899, 900, 1000]
    for cls in (HitCounterBrute, HitCounterQueue, HitCounterBuckets):
        hc = cls()
        answers = []
        hi = 0
        for q in queries:
            while hi < len(hits) and hits[hi] <= q:
                hc.hit(hits[hi])
                hi += 1
            answers.append(hc.get_hits(q))
        print(f"{cls.__name__:<17} {answers}")

    # Burst: one million hits in one second costs the bucket version no extra memory.
    hc = HitCounterBuckets(window=60)
    for _ in range(1_000_000):
        hc.hit(10)
    print("burst of 1e6 hits at t=10 -> get_hits(69) =", hc.get_hits(69),
          " get_hits(70) =", hc.get_hits(70), " slots used:", len(hc.counts))


if __name__ == "__main__":
    main()
