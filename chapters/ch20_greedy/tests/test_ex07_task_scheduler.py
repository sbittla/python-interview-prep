import random

import pytest


def test_examples(load):
    m = load("ex07_task_scheduler")
    assert m.least_interval(list("AAABBB"), 2) == 8
    assert m.least_interval(list("AAABBB"), 0) == 6


@pytest.mark.parametrize("tasks, n, expected", [
    ("A", 5, 1), ("AAA", 3, 9), ("AAAAAABCDEFG", 2, 16), ("AAABBBCCD", 2, 9), ("", 2, 0),
])
def test_edge_cases(load, tasks, n, expected):
    assert load("ex07_task_scheduler").least_interval(list(tasks), n) == expected


def _valid(schedule, n):
    last = {}
    for t, ch in enumerate(schedule):
        if ch == "_":
            continue
        if ch in last and t - last[ch] <= n:
            return False
        last[ch] = t
    return True


def test_simulation_matches_formula(load):
    m = load("ex07_task_scheduler")
    rng = random.Random(7)
    for _ in range(200):
        tasks = [rng.choice("ABCD") for _ in range(rng.randint(1, 12))]
        n = rng.randint(0, 4)
        sched = m.schedule(tasks, n)
        assert _valid(sched, n)
        assert sorted(sched.replace("_", "")) == sorted(tasks)
        assert len(sched) == m.least_interval(tasks, n)
