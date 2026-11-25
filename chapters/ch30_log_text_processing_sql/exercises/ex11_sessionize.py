"""
Exercise 11 — Timed Practical: Sessionise Click Events in Python and SQL   [Tier: ◆ Extended]
Chapter 30 · Pattern: sort + gap scan; LAG + running SUM ("gaps and islands") · Target time: 30 min

Problem
-------
Events are (user, ts) pairs in Unix seconds, unordered. A user's session ends when the
next event of that user comes MORE than `gap` seconds later (default 1800 = 30 min).
Write

1. `sessions(events, gap)` -> [(user, start, end, n_events)] ordered by user, start;
2. `sessions_sql(conn, gap)` -> the same rows from table events(user, ts) in one query;
3. `summary(rows)` -> {user: (n_sessions, longest session in seconds)}.

Examples
--------
>>> sessions([("u", 0), ("u", 1800), ("u", 3601)], 1800)
[('u', 0, 1800, 2), ('u', 3601, 3601, 1)]

Constraints
-----------
- n events, timestamps may repeat (a repeat never starts a session).

Hints
-----
- Decide out loud whether exactly `gap` seconds continues the session (here: yes, it
  must be MORE than gap to split). Tests pin the boundary.
- With repeated timestamps, make ORDER BY unique (ts, rowid) before using a ROWS frame:
  otherwise the two windows may order tied rows differently and split them (→ ex10).

Edge cases
----------
- No events, one event (start == end, duration 0), equal timestamps, gap boundary
  exactly at `gap` and `gap + 1`, interleaved users.

Suggested time box (30 min)
---------------------------
5 clarify (boundary, ordering, output) · 10 Python version + 3 asserts · 10 SQL version ·
5 cross-check on random data and state complexity.

Follow-ups
----------
- Streaming: events arrive in order per user; keep {user: (start, last, n)} and emit a
  session when a gap closes it (memory O(active users)).
- Late events: buffer a watermark (e.g. 5 min) before closing sessions.
"""
from __future__ import annotations

import random
import sqlite3

Event = tuple[str, int]


def brute_sessions(events: list[Event], gap: int = 1800) -> list[tuple]:
    raise NotImplementedError("TODO")


def sessions(events: list[Event], gap: int = 1800) -> list[tuple]:
    raise NotImplementedError("TODO")


def sessions_sql(conn: sqlite3.Connection, gap: int = 1800) -> list[tuple]:
    raise NotImplementedError("TODO")


def summary(rows: list[tuple]) -> dict[str, tuple[int, int]]:
    raise NotImplementedError("TODO")


def make_db(events: list[Event]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE events (user TEXT, ts INTEGER)")
    conn.executemany("INSERT INTO events VALUES (?, ?)", events)
    return conn


def main() -> None:
    events = [("ana", 0), ("ana", 600), ("bo", 100), ("ana", 2400), ("ana", 6000),
              ("bo", 1900), ("bo", 3701), ("ana", 6000), ("cy", 50)]
    rows = sessions(events)
    for r in rows:
        print("  ", r)
    conn = make_db(events)
    print("SQL agrees:", sessions_sql(conn) == rows, "| brute agrees:", brute_sessions(events) == rows)
    print("summary:", summary(rows))
    print("boundary 1800 vs 1801:", len(sessions([("u", 0), ("u", 1800)])),
          len(sessions([("u", 0), ("u", 1801)])))
    rng = random.Random(30)
    ok = True
    for _ in range(50):
        ev = [(rng.choice("xyz"), rng.randint(0, 20_000)) for _ in range(rng.randint(0, 30))]
        ok &= sessions(ev) == sessions_sql(make_db(ev)) == brute_sessions(ev)
    print("random cross-check (50 cases):", ok)
    print("empty:", sessions([]), summary([]))


if __name__ == "__main__":
    main()
