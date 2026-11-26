from contextlib import closing
import random
import sqlite3

import pandas as pd


def ev(rows):
    return pd.DataFrame({"user_id": [r[0] for r in rows], "ts": pd.to_datetime([r[1] for r in rows]),
                         "event": [r[2] for r in rows]})


def test_order_matters(load):
    m = load("ex10_funnel_conversion")
    events = ev([(1, "2026-01-01 09:00", "purchase"), (1, "2026-01-01 09:05", "view"),
                 (2, "2026-01-01 09:00", "view"), (2, "2026-01-01 09:00", "cart"),   # same time counts
                 (2, "2026-01-01 09:10", "checkout"), (2, "2026-01-01 09:20", "purchase"),
                 (3, "2026-01-01 08:00", "cart"), (3, "2026-01-01 09:00", "view")])
    f = m.ordered_funnel(events, m.STEPS)
    assert f["users"].tolist() == [3, 1, 1, 1]
    assert f["step_conv"].tolist() == [1.0, 0.333, 1.0, 1.0]
    assert f["overall"].tolist() == [1.0, 0.333, 0.333, 0.333]
    assert m.unordered_counts(events, m.STEPS) == {"view": 3, "cart": 2, "checkout": 1, "purchase": 2}


def test_first_time_shortcut_is_wrong(load):
    m = load("ex10_funnel_conversion")
    events = ev([(1, "2026-01-01 09:00", "cart"), (1, "2026-01-01 09:05", "view"),
                 (1, "2026-01-01 09:10", "cart")])
    assert m.reached_per_step(events, m.STEPS[:2]) == [1, 1]
    assert m.first_time_funnel(events, m.STEPS[:2]) == [1, 0]


def test_repeated_mid_step_uses_earliest_qualifying_time(load):
    m = load("ex10_funnel_conversion")
    events = ev([(1, "2026-01-01 09:00", "view"), (1, "2026-01-01 09:01", "cart"),
                 (1, "2026-01-01 09:10", "cart"), (1, "2026-01-01 09:05", "checkout")])
    assert m.reached_per_step(events, m.STEPS[:3]) == [1, 1, 1]      # cart at 09:01, checkout after it
    assert m.brute_force_funnel(events, m.STEPS[:3]) == [1, 1, 1]


def test_random_vs_brute_and_sql(load):
    m = load("ex10_funnel_conversion")
    rng = random.Random(10)
    for _ in range(30):
        rows = [(rng.randint(1, 6), f"2026-01-01 09:{rng.randint(0, 59):02d}", rng.choice(m.STEPS))
                for _ in range(rng.randint(1, 25))]
        events = ev(rows)
        expected = m.brute_force_funnel(events, m.STEPS)
        assert m.reached_per_step(events, m.STEPS) == expected
        with closing(sqlite3.connect(":memory:")) as conn:
            events.assign(ts=events["ts"].dt.strftime("%Y-%m-%d %H:%M:%S")).to_sql("events", conn, index=False)
            assert m.sql_ordered_funnel(conn) == expected


def test_real_data_and_empty(load):
    m = load("ex10_funnel_conversion")
    events = m.load_events()
    f = m.ordered_funnel(events, m.STEPS)
    assert f["users"].tolist() == m.brute_force_funnel(events, m.STEPS)
    assert f["users"].is_monotonic_decreasing
    assert f["users"].iloc[-1] < m.unordered_counts(events, m.STEPS)["purchase"]
    assert m.ordered_funnel(events.iloc[0:0], m.STEPS)["users"].tolist() == [0, 0, 0, 0]
