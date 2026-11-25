"""
Exercise 10 — Ordered Conversion Funnel                              [Tier: ◆ Extended]
Chapter 34 · Pattern: first-time-per-step chain (merge + filter + min) · Target time: 30 min

Problem
-------
`data/events.csv` has (user_id, ts, event) with event in
view -> cart -> checkout -> purchase; events can repeat and arrive out of
order. A user REACHES step i if they reached step i-1 at time t and have an
event of step i at a time >= t (the time of step i is the earliest such
event). Step 0 (view) is reached at the user's first view.
1. `ordered_funnel(events, steps)` — DataFrame with columns step, users,
   step_conv (users / users of the previous step; 1.0 for the first step),
   overall (users / users of step 0); conversions rounded to 3 dp.
2. `unordered_counts(events, steps)` — {step: distinct users with that event
   at all}, the naive count that ignores time.
3. `brute_force_funnel(events, steps)` — per-user scan in Python.
4. `sql_ordered_funnel(conn)` — users per step from SQLite with chained CTEs.
5. `first_time_funnel(events, steps)` — the tempting shortcut (rung 2 below),
   kept so tests can show where it is wrong.

Examples
--------
>>> ordered_funnel(events, STEPS)["users"].tolist()[0] == events.query("event == 'view'").user_id.nunique()
True

Constraints
-----------
- n events, S steps; users who never viewed are never in the funnel.

Approach ladder
---------------
1. Brute force — per user, sort their events and walk the steps with a
   pointer: O(n log n) total, but a Python loop per user.
2. Improved   — pivot first-time-per-step per user (groupby + min + unstack)
   and require t_view <= t_cart <= ...: WRONG when a user's FIRST cart is
   before their first view but a later cart is after it. Fast, not correct.
3. Optimal    — for step i, merge step-i events onto (user, t_prev), keep
   ts >= t_prev, groupby(user).ts.min() -> t_i: O(n) hash work per step,
   O(S * n) total. Same shape in SQL: one CTE per step.
   Why move up: rung 3 is vectorised AND respects "after the previous step".

Hints
-----
- Compare timestamps, not strings, in pandas (parse_dates=["ts"]).
- "Same timestamp" counts as after (>=) — state the tie rule out loud.
- Users who skip a step (purchase without cart) stop at the skipped step.

Follow-ups
----------
- Time-boxed funnel: each step within 30 minutes of the previous.
- Funnel by segment (country, plan): add the key to every groupby/join.
- Median time between steps: subtract the step timestamps.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)
STEPS = ["view", "cart", "checkout", "purchase"]


def load_events() -> pd.DataFrame:
    return pd.read_csv(DATA / "events.csv", parse_dates=["ts"])


def reached_per_step(events: pd.DataFrame, steps: list[str]) -> list[int]:
    reached = (events[events["event"] == steps[0]].groupby("user_id")["ts"].min()
               .rename("t_prev").reset_index())
    counts = [len(reached)]
    for step in steps[1:]:
        cand = events.loc[events["event"] == step, ["user_id", "ts"]].merge(reached, on="user_id")
        cand = cand[cand["ts"] >= cand["t_prev"]]
        reached = cand.groupby("user_id")["ts"].min().rename("t_prev").reset_index()
        counts.append(len(reached))
    return counts


def to_funnel(steps: list[str], counts: list[int]) -> pd.DataFrame:
    df = pd.DataFrame({"step": steps, "users": counts})
    prev = df["users"].shift(1).fillna(df["users"].iloc[0] if counts else 0)
    df["step_conv"] = (df["users"] / prev).fillna(0.0).round(3)
    df["overall"] = (df["users"] / (counts[0] if counts and counts[0] else 1)).round(3)
    return df


def ordered_funnel(events: pd.DataFrame, steps: list[str]) -> pd.DataFrame:
    return to_funnel(steps, reached_per_step(events, steps))


def unordered_counts(events: pd.DataFrame, steps: list[str]) -> dict[str, int]:
    n = events.groupby("event")["user_id"].nunique()
    return {s: int(n.get(s, 0)) for s in steps}


def first_time_funnel(events: pd.DataFrame, steps: list[str]) -> list[int]:
    """Wrong-but-tempting: first time of each step, then require t0 <= t1 <= ..."""
    first = events.groupby(["user_id", "event"])["ts"].min().unstack()
    first = first.reindex(columns=steps)
    ok = first[steps[0]].notna()
    counts = [int(ok.sum())]
    for a, b in zip(steps, steps[1:]):
        ok &= first[b] >= first[a]
        counts.append(int(ok.sum()))
    return counts


def brute_force_funnel(events: pd.DataFrame, steps: list[str]) -> list[int]:
    by_user: dict[int, list] = {}
    for r in events.itertuples(index=False):
        by_user.setdefault(r.user_id, []).append((r.ts, r.event))
    counts = [0] * len(steps)
    for evs in by_user.values():
        t = None
        for i, step in enumerate(steps):
            times = [ts for ts, e in evs if e == step and (t is None or ts >= t)]
            if not times:
                break
            t = min(times)
            counts[i] += 1
    return counts


SQL_FUNNEL = """
WITH s0 AS (SELECT user_id, MIN(ts) AS t FROM events WHERE event = 'view' GROUP BY user_id),
s1 AS (SELECT e.user_id, MIN(e.ts) AS t FROM events e JOIN s0 ON s0.user_id = e.user_id
       WHERE e.event = 'cart' AND e.ts >= s0.t GROUP BY e.user_id),
s2 AS (SELECT e.user_id, MIN(e.ts) AS t FROM events e JOIN s1 ON s1.user_id = e.user_id
       WHERE e.event = 'checkout' AND e.ts >= s1.t GROUP BY e.user_id),
s3 AS (SELECT e.user_id, MIN(e.ts) AS t FROM events e JOIN s2 ON s2.user_id = e.user_id
       WHERE e.event = 'purchase' AND e.ts >= s2.t GROUP BY e.user_id)
SELECT (SELECT COUNT(*) FROM s0), (SELECT COUNT(*) FROM s1),
       (SELECT COUNT(*) FROM s2), (SELECT COUNT(*) FROM s3)
"""


def sql_ordered_funnel(conn: sqlite3.Connection) -> list[int]:
    return list(conn.execute(SQL_FUNNEL).fetchone())


def main() -> None:
    events = load_events()
    funnel = ordered_funnel(events, STEPS)
    print(funnel.to_string(index=False))
    print("unordered distinct users per event:", unordered_counts(events, STEPS))
    print("brute force agrees:", brute_force_funnel(events, STEPS) == funnel["users"].tolist())
    with closing(sqlite3.connect(":memory:")) as conn:
        events.assign(ts=events["ts"].dt.strftime("%Y-%m-%d %H:%M:%S")).to_sql("events", conn, index=False)
        print("SQL agrees:", sql_ordered_funnel(conn) == funnel["users"].tolist())
    odd = events[events["user_id"].isin([5, 18])].assign(ts=lambda d: d["ts"].dt.strftime("%H:%M"))
    print("users 5 and 18 purchase BEFORE viewing:")
    print(odd.sort_values(["user_id", "ts"]).to_string(index=False))
    tricky = pd.DataFrame({"user_id": [1, 1, 1], "event": ["cart", "view", "cart"],
                           "ts": pd.to_datetime(["2026-01-01 09:00", "2026-01-01 09:05", "2026-01-01 09:10"])})
    print("cart, view, cart: ordered", reached_per_step(tricky, STEPS[:2]),
          "| first-time shortcut", first_time_funnel(tricky, STEPS[:2]))
    print("empty events ->", ordered_funnel(events.iloc[0:0], STEPS)["users"].tolist())


if __name__ == "__main__":
    main()
