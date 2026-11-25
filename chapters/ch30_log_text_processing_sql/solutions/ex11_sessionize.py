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

Approach ladder
---------------
1. Brute force — for each event, scan every earlier event of the same user to find the
   nearest predecessor: O(n^2).
2. Sort by (user, ts), then one scan: a row starts a session when the user changes or
   ts - previous_ts > gap. O(n log n) time, O(n) space for the sort.
3. Same idea in SQL: `LAG(ts) OVER (PARTITION BY user ORDER BY ts)` marks starts with a
   0/1 flag, `SUM(flag) OVER (... ROWS UNBOUNDED PRECEDING)` numbers the sessions (a
   running total of starts), then GROUP BY (user, session_no). Why: the classic
   "gaps and islands" pattern, and the database does the sort.

Hints
-----
- Decide out loud whether exactly `gap` seconds continues the session (here: yes, it
  must be MORE than gap to split). Tests pin the boundary.
- In the SQL version the running SUM needs a ROWS frame when timestamps repeat (→ ex10).

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
    starts = []
    for i, (u, t) in enumerate(events):
        prev = [t2 for j, (u2, t2) in enumerate(events)
                if u2 == u and (t2 < t or (t2 == t and j < i))]    # O(n) per event
        if not prev or t - max(prev) > gap:
            starts.append((u, t))
    out = []
    for u, s in sorted(set(starts)):
        later = [st for (uu, st) in starts if uu == u and st > s]
        stop = min(later) if later else None
        mine = [t for uu, t in events if uu == u and t >= s and (stop is None or t < stop)]
        out.append((u, s, max(mine), len(mine)))
    return out


def sessions(events: list[Event], gap: int = 1800) -> list[tuple]:
    out: list[list] = []
    prev_user, prev_ts = None, None
    for user, ts in sorted(events):
        if user != prev_user or ts - prev_ts > gap:
            out.append([user, ts, ts, 0])              # new session
        cur = out[-1]
        cur[2] = ts
        cur[3] += 1
        prev_user, prev_ts = user, ts
    return [tuple(s) for s in out]


def sessions_sql(conn: sqlite3.Connection, gap: int = 1800) -> list[tuple]:
    return conn.execute("""
        WITH flagged AS (
            SELECT user, ts,
                   CASE WHEN ts - LAG(ts) OVER (PARTITION BY user ORDER BY ts) <= ?
                        THEN 0 ELSE 1 END AS is_start
            FROM events
        ), numbered AS (
            SELECT user, ts,
                   SUM(is_start) OVER (PARTITION BY user ORDER BY ts
                                       ROWS UNBOUNDED PRECEDING) AS session_no
            FROM flagged
        )
        SELECT user, MIN(ts), MAX(ts), COUNT(*)
        FROM numbered
        GROUP BY user, session_no
        ORDER BY user, MIN(ts)""", (gap,)).fetchall()


def summary(rows: list[tuple]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for user, start, end, _ in rows:
        n, longest = out.get(user, (0, 0))
        out[user] = (n + 1, max(longest, end - start))
    return dict(sorted(out.items()))


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
