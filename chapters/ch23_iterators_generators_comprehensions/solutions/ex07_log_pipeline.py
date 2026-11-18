"""
Exercise 07 — Generator Pipeline over a Log File               [Tier: ★ Core]
Chapter 23 · Pattern: generator pipeline · Target time: 25 min

Problem
-------
``data/app.log`` holds lines like::

    2024-03-01T10:00:15 ERROR GET /api/payments 500 1203

(timestamp, level, method, path, status, latency in ms). It also contains comment lines starting
with ``#``, blank lines and corrupted lines. Build a pipeline of small generators:

- ``read_lines(path)``         -> stripped lines, lazily, one at a time
- ``parse_records(lines)``     -> dicts with keys ts, level, method, path, status(int), ms(int);
                                  skip blanks, comments and malformed lines
- ``only_level(records, *levels)`` -> records whose level is in ``levels``
- ``slow(records, threshold_ms)``  -> records with ms >= threshold

and two consumers:

- ``count_by(records, key)``   -> dict key-value -> count, sorted by count desc then key
- ``p_latency(records, pct)``  -> the nearest-rank percentile of ``ms``

Examples
--------
>>> recs = parse_records(["2024-03-01T10:00:01 INFO GET /a 200 12", "junk"])
>>> list(recs)
[{'ts': '2024-03-01T10:00:01', 'level': 'INFO', 'method': 'GET', 'path': '/a', 'status': 200, 'ms': 12}]

Constraints
-----------
- Each stage must accept *any* iterable, so stages are testable with plain lists.
- The file is opened once and closed when the pipeline finishes (use ``with`` inside the generator).

Hints
-----
- A generator holding a ``with open(...)`` block closes the file when it is exhausted or closed.
- Validate with ``str.split()`` → 6 fields, and ``str.isdigit()`` on the numeric fields.
- Nearest-rank percentile: sort, then index ``ceil(pct/100 * n) - 1``.

Approach ladder
---------------
1. ``f.readlines()`` then loops building lists per step — O(file) memory per stage.
2. One big function that reads, parses, filters and counts — lazy but untestable and rigid.
3. Composable generator stages — O(1) memory per stage, each stage unit-testable.

Follow-ups
----------
- How would you process a 50 GB log? (this design already streams; add ``chunked`` writes)
- How would you follow a growing file (``tail -f``)? (loop on ``readline`` with a sleep)
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator

LOG = Path(__file__).resolve().parent.parent / "data" / "app.log"
FIELDS = ("ts", "level", "method", "path", "status", "ms")


def read_lines(path: Path) -> Iterator[str]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()


def parse_records(lines: Iterable[str]) -> Iterator[dict]:
    for line in lines:
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 6 or not (parts[4].isdigit() and parts[5].isdigit()):
            continue
        rec = dict(zip(FIELDS, parts))
        rec["status"] = int(rec["status"])
        rec["ms"] = int(rec["ms"])
        yield rec


def only_level(records: Iterable[dict], *levels: str) -> Iterator[dict]:
    wanted = set(levels)
    return (r for r in records if r["level"] in wanted)


def slow(records: Iterable[dict], threshold_ms: int) -> Iterator[dict]:
    return (r for r in records if r["ms"] >= threshold_ms)


def count_by(records: Iterable[dict], key: str) -> dict:
    counts = Counter(r[key] for r in records)
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def p_latency(records: Iterable[dict], pct: float) -> int:
    values = sorted(r["ms"] for r in records)
    if not values:
        raise ValueError("no records")
    rank = max(1, math.ceil(pct / 100 * len(values)))
    return values[rank - 1]


def main() -> None:
    records = parse_records(read_lines(LOG))
    print("first record:", next(records))
    records.close()  # runs the generator's cleanup: the `with` block closes the file now

    print("valid records:", sum(1 for _ in parse_records(read_lines(LOG))))
    print("by level:", count_by(parse_records(read_lines(LOG)), "level"))
    errors = only_level(parse_records(read_lines(LOG)), "ERROR")
    print("errors by path:", count_by(errors, "path"))
    problems = only_level(parse_records(read_lines(LOG)), "WARN", "ERROR")
    print("warn+error by status:", count_by(problems, "status"))
    print("slow (>=1000ms) paths:",
          [r["path"] for r in slow(parse_records(read_lines(LOG)), 1000)])
    for pct in (50, 90, 99):
        print(f"p{pct} latency ms:", p_latency(parse_records(read_lines(LOG)), pct))

    # Each stage works on plain lists too -- this is what makes it testable.
    sample = ["", "# c", "2024-01-01T00:00:00 INFO GET /x 200 5", "bad line"]
    print("parsed sample:", list(parse_records(sample)))


if __name__ == "__main__":
    main()
