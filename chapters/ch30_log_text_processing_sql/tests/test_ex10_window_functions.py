import random

import pytest


def test_example(load):
    m = load("ex10_window_functions")
    assert m.top_n_per_region(m.make_db(), 1) == [
        ("east", "2025-03-01", 120), ("north", "2025-03-01", 70), ("west", "2025-03-02", 90)]


@pytest.mark.parametrize("n", [0, 1, 2, 3, 9])
def test_top_n_three_ways(load, n):
    m = load("ex10_window_functions")
    conn = m.make_db()
    got = m.top_n_per_region(conn, n)
    assert got == m.top_n_correlated(conn, n) == m.top_n_python(m.SALES, n)
    assert len(got) == sum(min(n, c) for c in (5, 4, 1))


def test_top_n_random(load):
    m = load("ex10_window_functions")
    rng = random.Random(10)
    for _ in range(40):
        rows = [(i, rng.choice("ab"), f"2025-03-0{rng.randint(1, 5)}", rng.randint(1, 4))
                for i in range(1, rng.randint(1, 15))]
        n = rng.randint(0, 4)
        assert m.top_n_per_region(m.make_db(rows), n) == m.top_n_python(rows, n)


def test_rank_styles(load):
    m = load("ex10_window_functions")
    assert m.rank_styles(m.make_db(), "east") == [
        (120, 1, 1, 1), (120, 2, 1, 1), (80, 3, 3, 2), (60, 4, 4, 3), (40, 5, 5, 4)]


def test_running_totals_rows_frame(load):
    m = load("ex10_window_functions")
    conn = m.make_db()
    rows = m.running_totals(conn)
    east = [r[-1] for r in rows if r[0] == "east"]
    assert east == [120, 200, 240, 360, 420]
    assert [r[-1] for r in m.running_totals_default_frame(conn) if r[0] == "east"] == [
        120, 240, 240, 360, 420]
    for region in ("east", "west", "north"):              # last running value = region total
        mine = [r for r in rows if r[0] == region]
        assert mine[-1][-1] == sum(r[3] for r in mine)


def test_daily_change(load):
    m = load("ex10_window_functions")
    rows = m.daily_change(m.make_db())
    assert [r[2:] for r in rows if r[0] == "east"] == [(120, None), (120, 0), (120, 0), (60, -60)]
    assert [r for r in rows if r[0] == "north"] == [("north", "2025-03-01", 70, None)]
