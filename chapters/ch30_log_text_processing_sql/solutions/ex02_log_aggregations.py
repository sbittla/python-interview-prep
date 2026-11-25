"""
Exercise 02 — Log Aggregations: Status Mix, Top-K Paths, p95 Latency   [Tier: ★ Core]
Chapter 30 · Pattern: Counter / defaultdict + heap top-K · Target time: 20 min

Problem
-------
Given parsed hits (ip, ts, method, path, status, latency_ms), write

1. `status_classes(hits)` -> {"2xx": n, "3xx": n, ...}, only classes that occur;
2. `top_k_paths(hits, k)` -> [(path, count)], count descending, ties by path ascending;
3. `p95_latency(hits)` -> {path: p95 latency in ms} using the nearest-rank percentile
   (sort the n values, take the ceil(0.95 * n)-th smallest);
4. `error_rates(hits)` -> {path: (5xx count, total)} for paths with at least one 5xx.

Examples
--------
>>> hits = [Hit("a", 0, "GET", "/x", 200, 10), Hit("b", 1, "GET", "/y", 500, 30),
...         Hit("a", 2, "GET", "/y", 200, 20)]
>>> top_k_paths(hits, 1)
[('/y', 2)]
>>> status_classes(hits)
{'2xx': 2, '5xx': 1}

Constraints
-----------
- n hits, u distinct paths, k <= u. One pass over the hits.

Approach ladder
---------------
Top-K:
1. Brute force — for each distinct path, rescan all hits to count it: O(n·u).
2. Improved   — one Counter pass, then sort all u items: O(n + u log u).
3. Optimal    — Counter pass, then `heapq.nsmallest(k, ..., key=(-count, path))`:
   O(n + u log k). Why move up: u can be millions of distinct URLs while k = 10.
p95: group latencies per path in one pass (defaultdict(list)), sort each group:
O(n log n) total. A streaming answer (t-digest, histogram buckets) is a follow-up.

Hints
-----
- `Counter.most_common(k)` breaks ties by first-seen order, not alphabetically —
  deterministic, but it depends on log order. State the tie rule and encode it in the key.
- Nearest rank: index `math.ceil(0.95 * n) - 1` into the sorted list; never 0.95 * n.
- Status class: `f"{status // 100}xx"`.

Edge cases
----------
- No hits (empty dicts / list), k larger than u, a path with a single hit (p95 = that
  value), ties in counts.

Follow-ups
----------
- Top-K over a stream that does not fit in memory: Count-Min Sketch + heap, or
  hash-partition by path to disk and count each partition (→ ex06).
- Percentiles over a stream: fixed histogram buckets (Prometheus style) or t-digest.
"""
from __future__ import annotations

import heapq
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

DATA = Path(__file__).resolve().parent.parent / "data"


class Hit(NamedTuple):
    ip: str
    ts: int            # Unix seconds
    method: str
    path: str
    status: int
    latency_ms: int


HIT_RE = re.compile(r'(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) (\S+) [^"]*" (\d{3}) (?:\d+|-) (\d+\.\d+)')


def load_hits(path: Path = DATA / "access.log") -> list[Hit]:
    """Condensed version of ex01's parser (given; not part of the exercise)."""
    hits = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HIT_RE.fullmatch(line.rstrip("\r\n"))
            if not m:
                continue
            try:
                ts = datetime.strptime(m[2], "%d/%b/%Y:%H:%M:%S %z")
            except ValueError:
                continue
            hits.append(Hit(m[1], int(ts.timestamp()), m[3], m[4], int(m[5]),
                            round(float(m[6]) * 1000)))
    return hits


def status_classes(hits: list[Hit]) -> dict[str, int]:
    counts = Counter(f"{h.status // 100}xx" for h in hits)
    return dict(sorted(counts.items()))


def brute_top_k(hits: list[Hit], k: int) -> list[tuple[str, int]]:
    paths = sorted({h.path for h in hits})
    counted = [(p, sum(1 for h in hits if h.path == p)) for p in paths]   # O(n·u)
    return sorted(counted, key=lambda pc: (-pc[1], pc[0]))[:k]


def top_k_paths(hits: list[Hit], k: int) -> list[tuple[str, int]]:
    counts = Counter(h.path for h in hits)                                  # O(n)
    return heapq.nsmallest(k, counts.items(), key=lambda pc: (-pc[1], pc[0]))  # O(u log k)


def p95_latency(hits: list[Hit]) -> dict[str, int]:
    by_path: defaultdict[str, list[int]] = defaultdict(list)
    for h in hits:
        by_path[h.path].append(h.latency_ms)
    out = {}
    for path in sorted(by_path):
        values = sorted(by_path[path])
        out[path] = values[math.ceil(0.95 * len(values)) - 1]
    return out


def error_rates(hits: list[Hit]) -> dict[str, tuple[int, int]]:
    total: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    for h in hits:
        total[h.path] += 1
        if h.status >= 500:
            errors[h.path] += 1
    return {p: (errors[p], total[p]) for p in sorted(errors)}


def main() -> None:
    hits = load_hits()
    print("hits:", len(hits))
    print("status classes:", status_classes(hits))
    print("top 3 paths:", top_k_paths(hits, 3))
    print("matches brute force:", top_k_paths(hits, 3) == brute_top_k(hits, 3))
    print("p95 latency ms:", p95_latency(hits))
    print("5xx (errors, total):", error_rates(hits))
    tie = [Hit("a", 0, "GET", p, 200, 1) for p in ["/b", "/a", "/b", "/a"]]
    print("tie -> most_common:", Counter(h.path for h in tie).most_common(1),
          "| top_k_paths:", top_k_paths(tie, 1))
    print("empty:", status_classes([]), top_k_paths([], 3), p95_latency([]))


if __name__ == "__main__":
    main()
