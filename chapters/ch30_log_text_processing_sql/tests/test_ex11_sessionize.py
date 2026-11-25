import random

import pytest


def test_example(load):
    m = load("ex11_sessionize")
    assert m.sessions([("u", 0), ("u", 1800), ("u", 3601)], 1800) == [
        ("u", 0, 1800, 2), ("u", 3601, 3601, 1)]


@pytest.mark.parametrize("events, expected", [
    ([], []),
    ([("u", 5)], [("u", 5, 5, 1)]),
    ([("u", 5), ("u", 5)], [("u", 5, 5, 2)]),
    ([("u", 0), ("u", 1801)], [("u", 0, 0, 1), ("u", 1801, 1801, 1)]),
    ([("b", 0), ("a", 10), ("b", 20)], [("a", 10, 10, 1), ("b", 0, 20, 2)]),
])
def test_edges(load, events, expected):
    m = load("ex11_sessionize")
    assert m.sessions(events) == expected
    assert m.sessions_sql(m.make_db(events)) == expected


def test_custom_gap(load):
    m = load("ex11_sessionize")
    ev = [("u", 0), ("u", 10), ("u", 25)]
    assert len(m.sessions(ev, 10)) == 2 and len(m.sessions(ev, 15)) == 1
    assert len(m.sessions_sql(m.make_db(ev), 10)) == 2


def test_summary(load):
    m = load("ex11_sessionize")
    rows = [("a", 0, 100, 3), ("a", 5000, 5050, 2), ("b", 7, 7, 1)]
    assert m.summary(rows) == {"a": (2, 100), "b": (1, 0)}
    assert m.summary([]) == {}


def test_random_three_ways(load):
    m = load("ex11_sessionize")
    rng = random.Random(11)
    for _ in range(60):
        ev = [(rng.choice("xy"), rng.randint(0, 9000)) for _ in range(rng.randint(0, 20))]
        assert m.sessions(ev) == m.sessions_sql(m.make_db(ev)) == m.brute_sessions(ev)


def test_sql_with_many_tied_timestamps(load):
    m = load("ex11_sessionize")
    rng = random.Random(111)
    for _ in range(100):
        # few distinct timestamps, many repeats, gaps around the 1800 s boundary
        ev = [(rng.choice("xy"), rng.choice([0, 0, 1800, 1801, 1801, 3700, 3700]))
              for _ in range(rng.randint(1, 25))]
        rng.shuffle(ev)
        assert m.sessions_sql(m.make_db(ev)) == m.sessions(ev)
