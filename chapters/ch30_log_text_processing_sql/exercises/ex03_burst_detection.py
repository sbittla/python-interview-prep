"""
Exercise 03 — Time Windows: Per-Minute Counts and Burst Detection   [Tier: ★ Core]
Chapter 30 · Pattern: tumbling buckets + sliding window (two pointers) · Target time: 25 min

Problem
-------
Hits are (ip, ts) pairs with ts in Unix seconds, NOT necessarily in order (logs merged
from several servers). Write

1. `per_minute(times)` -> [(minute_start, count)] sorted, tumbling 60-second buckets
   aligned to the clock (ts // 60 * 60);
2. `max_in_window(times, w)` -> the largest number of events inside any half-open
   window [t, t + w) — i.e. the most events whose pairwise gap is < w;
3. `flag_bursts(hits, w, limit)` -> [(ip, peak)] for every ip whose peak count in any
   w-second window exceeds `limit`, sorted by ip.

Examples
--------
>>> max_in_window([0, 10, 59, 60, 61], 60)
4
>>> per_minute([61, 0, 59, 125])
[(0, 2), (60, 1), (120, 1)]
>>> flag_bursts([("a", 0), ("a", 5), ("b", 0)], 60, 1)
[('a', 2)]

Constraints
-----------
- n events, w >= 1 seconds. Timestamps are integers and may repeat.

Hints
-----
- The best window can always be chosen to start at an event, so it suffices to look at
  windows anchored on events.
- Group times per ip with defaultdict(list), then run (3) on each group: total O(n log n).

Edge cases
----------
- Empty input (peak 0), all timestamps equal (peak n), events exactly w apart (not in the
  same window: half-open), unsorted input, limit equal to the peak (not flagged: "exceeds").

Follow-ups
----------
- Online version (events arrive in order): keep a deque per ip and pop expired entries —
  that is the sliding-log rate limiter (→ §29.5).
- Millions of IPs: the per-ip deques dominate memory; use fixed-window counters or a
  sliding-window approximation.
- Windows in SQL: `COUNT(*) OVER (PARTITION BY ip ORDER BY ts RANGE BETWEEN CURRENT ROW
  AND 59 FOLLOWING)`; RANGE with a numeric offset needs SQLite 3.28+ (→ ex10).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
HIT_RE = re.compile(r'(\S+) \S+ \S+ \[([^\]]+)\] "[A-Z]+ \S+ [^"]*" \d{3} (?:\d+|-) \d+\.\d+')


def load_ip_times(path: Path = DATA / "access.log") -> list[tuple[str, int]]:
    """(ip, unix seconds) per well-formed line; condensed ex01 parser (given)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HIT_RE.fullmatch(line.rstrip("\r\n"))
            if m:
                try:
                    ts = datetime.strptime(m[2], "%d/%b/%Y:%H:%M:%S %z")
                except ValueError:
                    continue
                out.append((m[1], int(ts.timestamp())))
    return out


def per_minute(times: list[int]) -> list[tuple[int, int]]:
    raise NotImplementedError("TODO")


def brute_max_in_window(times: list[int], w: int) -> int:
    raise NotImplementedError("TODO")


def max_in_window(times: list[int], w: int) -> int:
    raise NotImplementedError("TODO")


def flag_bursts(hits: list[tuple[str, int]], w: int, limit: int) -> list[tuple[str, int]]:
    raise NotImplementedError("TODO")


def hhmm(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%H:%M")


def main() -> None:
    hits = load_ip_times()
    print("per minute:", [(hhmm(t), c) for t, c in per_minute([t for _, t in hits])])
    print("bursts (>5 in 60 s):", flag_bursts(hits, 60, 5))
    print("all peaks:", flag_bursts(hits, 60, 0))
    straddle = [50, 52, 54, 56, 58, 60, 62, 64, 66, 68]        # 10 events in 20 s
    print("straddling burst -> buckets:", per_minute(straddle),
          "| sliding peak:", max_in_window(straddle, 60))
    print("edges:", max_in_window([], 60), max_in_window([7, 7, 7], 1),
          max_in_window([0, 60], 60), max_in_window([60, 0, 59], 60))
    print("matches brute force:", all(
        max_in_window(ts, 60) == brute_max_in_window(ts, 60)
        for ts in ([t for _, t in hits], straddle, [0, 60], [5, 5, 5])))


if __name__ == "__main__":
    main()
