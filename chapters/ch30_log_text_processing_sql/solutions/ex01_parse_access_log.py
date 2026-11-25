"""
Exercise 01 — Parse an Access Log, One Line at a Time       [Tier: ★ Core]
Chapter 30 · Pattern: compiled regex + named groups + generator · Target time: 20 min

Problem
-------
Each line of `data/access.log` looks like

    203.0.113.5 - - [12/Mar/2025:10:00:35 +0000] "GET /api/users HTTP/1.1" 200 549 0.044

(client IP, two unused fields, timestamp, quoted request line, status, response bytes or "-",
latency in seconds). Write

1. `parse_line(line)` -> a `Record` (ip, ts as an aware `datetime`, method, path, status:int,
   size:int with "-" meaning 0, latency_ms:int) or `None` if the line is malformed;
2. `iter_records(lines)` -> a generator of records that skips malformed lines and counts them
   in a `stats` dict passed by the caller (`{"ok": n, "bad": m}`). Blank lines count as
   malformed here (a log writer never emits them; contrast ex05, which skips them);
3. `parse_split(line)` -> the same result using only `str.split`, for comparison.

Examples
--------
>>> r = parse_line('1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044')
>>> (r.ip, r.path, r.status, r.size, r.latency_ms, r.ts.isoformat())
('1.2.3.4', '/a', 200, 5, 44, '2025-03-12T10:00:35+00:00')
>>> parse_line("garbage") is None
True

Constraints
-----------
- Files may be larger than memory: never call `readlines()` / `read()`.
- A line is malformed if the regex misses OR the timestamp does not parse.

Approach ladder
---------------
1. `str.split()` on whitespace — O(L) per line, but the request is three tokens inside
   quotes and the timestamp is two; indexing by position accepts any token in any slot
   (e.g. "unknown" as the IP) and shifts every field when one is missing or a path
   contains a space. Fine for a 2-minute answer, fragile in production.
2. `re.match(pattern, line)` each time — anchored, validates the shape of every field
   (values like IP octets <= 255 need a second check); the `re` module
   caches compiled patterns, so the cost is a cache lookup per call.
3. Compile once, `fullmatch` with named groups, wrap in a generator: O(L) per line,
   O(1) extra memory beyond one line, and `match.group("status")` documents itself.
   Why move up: rung 3 rejects malformed lines instead of silently mis-assigning fields.

Hints
-----
- `\\S+` = run of non-spaces; `[^\\]]+` = everything up to the closing bracket.
- `datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z")` returns an aware datetime; `%b` uses the
  month names of the current LC_TIME locale, which is "C" (English) unless the program
  calls `locale.setlocale`.
- Iterate the file object itself; it yields one line at a time.

Edge cases
----------
- Empty line, truncated line, non-numeric status ("2OO"), impossible month ("Foo"),
  size "-" (304 responses), trailing "\\n" or "\\r\\n".

Follow-ups
----------
- Gzipped logs: `gzip.open(path, "rt")` is a drop-in iterator.
- Older lines without the latency field: make that group optional `(?: ...)?`.
- Multi-line entries (stack traces): group lines that do not start with an IP.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple

DATA = Path(__file__).resolve().parent.parent / "data"

LINE_RE = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) \S+ \S+ "
    r"\[(?P<ts>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
    r"(?: (?P<latency>\d+\.\d+))?"
)
TS_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


class Record(NamedTuple):
    ip: str
    ts: datetime
    method: str
    path: str
    status: int
    size: int
    latency_ms: int


def _build(ip, ts, method, path, status, size, latency) -> Record | None:
    try:
        when = datetime.strptime(ts, TS_FORMAT)
    except ValueError:                      # "31/Foo/2025..." matches the regex but is no date
        return None
    ms = round(float(latency) * 1000) if latency else 0
    return Record(ip, when, method, path, int(status), 0 if size == "-" else int(size), ms)


def parse_line(line: str) -> Record | None:
    m = LINE_RE.fullmatch(line.rstrip("\r\n"))
    if m is None:
        return None
    return _build(*m.group("ip", "ts", "method", "path", "status", "size", "latency"))


def parse_split(line: str) -> Record | None:
    """Rung 1: positional split. Works on well-formed lines only by luck of layout."""
    parts = line.split()
    if len(parts) not in (10, 11):
        return None
    ip, _, _, day, zone, method, path, _proto, status, size, *rest = parts
    if not status.isdigit():
        return None
    return _build(ip, f"{day[1:]} {zone[:-1]}", method[1:], path, status, size,
                  rest[0] if rest else None)


def iter_records(lines: Iterable[str], stats: dict[str, int] | None = None) -> Iterator[Record]:
    if stats is not None:
        stats.setdefault("ok", 0)
        stats.setdefault("bad", 0)
    for line in lines:
        rec = parse_line(line)
        if stats is not None:
            stats["ok" if rec else "bad"] += 1
        if rec is not None:
            yield rec


def main() -> None:
    stats: dict[str, int] = {}
    with open(DATA / "access.log", encoding="utf-8") as f:   # streamed, never read whole
        records = list(iter_records(f, stats))
    print("parsed:", stats)
    first = records[0]
    print("first:", first.ip, first.ts.isoformat(), first.method, first.path,
          first.status, first.size, first.latency_ms)
    print("statuses:", sorted({r.status for r in records}))
    print("ips:", sorted({r.ip for r in records}))
    with open(DATA / "access.log", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if parse_line(line) is None:
                print(f"  bad line {n}: {line.rstrip()[:50]!r}")
    with open(DATA / "access.log", encoding="utf-8") as f:
        same = all(parse_split(line) == parse_line(line) for line in f)
    print("split agrees on this file:", same)
    tricky = 'unknown - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044'
    print("no IP -> regex:", parse_line(tricky), "| split ip:", parse_split(tricky).ip)


if __name__ == "__main__":
    main()
