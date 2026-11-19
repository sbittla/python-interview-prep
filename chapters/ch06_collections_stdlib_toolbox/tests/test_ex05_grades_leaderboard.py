import random

import pytest


@pytest.mark.parametrize("score, letter", [
    (0, "F"), (59, "F"), (60, "D"), (69, "D"), (70, "C"), (80, "B"), (89, "B"), (90, "A"), (100, "A"),
])
def test_grade_boundaries(load, score, letter):
    m = load("ex05_grades_leaderboard")
    assert m.grade(score) == letter == m.brute_force_grade(score)


def test_examples(load):
    m = load("ex05_grades_leaderboard")
    lb = m.Leaderboard()
    for s in (50, 80, 80, 95):
        lb.add(s)
    assert lb.rank(80) == 2
    assert lb.count_between(60, 90) == 2


def test_empty_leaderboard(load):
    lb = load("ex05_grades_leaderboard").Leaderboard()
    assert lb.rank(10) == 1
    assert lb.count_between(0, 100) == 0
    lb.add(5)
    assert lb.count_between(9, 1) == 0


def test_random_against_scan(load):
    m = load("ex05_grades_leaderboard")
    rng = random.Random(5)
    lb, seen = m.Leaderboard(), []
    for _ in range(300):
        s = rng.randint(0, 30)
        lb.add(s)
        seen.append(s)
        q, lo, hi = rng.randint(-1, 31), rng.randint(0, 30), rng.randint(0, 30)
        assert lb.rank(q) == 1 + sum(x > q for x in seen)
        assert lb.count_between(lo, hi) == sum(lo <= x <= hi for x in seen)
    assert lb.scores == sorted(seen)
