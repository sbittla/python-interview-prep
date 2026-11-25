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
    raise NotImplementedError("TODO")


def to_funnel(steps: list[str], counts: list[int]) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def ordered_funnel(events: pd.DataFrame, steps: list[str]) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def unordered_counts(events: pd.DataFrame, steps: list[str]) -> dict[str, int]:
    raise NotImplementedError("TODO")


def first_time_funnel(events: pd.DataFrame, steps: list[str]) -> list[int]:
    """Wrong-but-tempting: first time of each step, then require t0 <= t1 <= ..."""
    raise NotImplementedError("TODO")


def brute_force_funnel(events: pd.DataFrame, steps: list[str]) -> list[int]:
    raise NotImplementedError("TODO")


SQL_FUNNEL = """
-- TODO: write the query
"""


def sql_ordered_funnel(conn: sqlite3.Connection) -> list[int]:
    raise NotImplementedError("TODO")


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
