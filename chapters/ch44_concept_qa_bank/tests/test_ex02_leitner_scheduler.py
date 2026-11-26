import pytest


@pytest.fixture
def m(load):
    return load("ex02_leitner_scheduler")


def test_always_right_follows_section_3_4_ladder(m):
    s = m.Leitner(["a"])
    log = s.simulate(40, lambda c, b, d: True)
    assert [d for d, _ in log] == [0, 1, 4, 11, 32]
    assert s.retired == {"a"} and s.cards["a"].reviews == 5


def test_wrong_answer_resets_to_box_0(m):
    s = m.Leitner(["a"])
    s.review("a", 0, True)
    s.review("a", 1, True)
    assert (s.cards["a"].box, s.cards["a"].due) == (2, 4)
    s.review("a", 4, False)
    assert (s.cards["a"].box, s.cards["a"].due, s.cards["a"].lapses) == (0, 5, 1)


def test_late_review_counts_from_review_day(m):
    s = m.Leitner(["a"])
    s.review("a", 3, True)           # overdue card reviewed on day 3
    assert s.cards["a"].due == 4


def test_due_ordering_most_urgent_first(m):
    s = m.Leitner(["c", "a", "b"])
    s.review("b", 0, True)           # b: box 1, due 1
    s.review("c", 0, False)          # c: box 0, due 1
    assert s.due(0) == ["a"]
    assert s.due(1) == ["a", "c", "b"]  # a due 0; then c (box 0) before b (box 1)


def test_cap_picks_by_urgency_then_shuffles(m):
    ids = [f"q{i:02d}" for i in range(30)]
    s = m.Leitner(ids, seed=3, daily_cap=10)
    sess = s.session(0)
    assert sorted(sess) == ids[:10]
    assert sess == m.Leitner(ids, seed=3, daily_cap=10).session(0)
    assert sess != ids[:10]                       # actually shuffled
    assert m.Leitner(ids, seed=4, daily_cap=10).session(0) != sess


def test_same_seed_differs_across_days_with_same_due_set(m):
    ids = [f"q{i:02d}" for i in range(12)]
    s = m.Leitner(ids, seed=5)
    assert sorted(s.due(0)) == sorted(s.due(1)) == ids     # nothing reviewed: same due set
    assert s.session(0) != s.session(1)                    # the day is part of the seed
    assert s.session(1) == m.Leitner(ids, seed=5).session(1)


def test_capped_cards_stay_overdue(m):
    s = m.Leitner(["a", "b", "c"], daily_cap=2)
    log = s.simulate(1, lambda c, b, d: True)
    reviewed = {c for c, _ in log[0][1]}
    assert len(reviewed) == 2
    left = ({"a", "b", "c"} - reviewed).pop()
    assert s.due(1)[0] == left                    # overdue card leads next day


@pytest.mark.parametrize("kwargs", [
    {"ids": ["a", "a"]}, {"ids": [""]}, {"ids": ["a"], "ladder": (3, 1)},
    {"ids": ["a"], "ladder": ()}, {"ids": ["a"], "ladder": (0, 2)},
    {"ids": ["a"], "daily_cap": 0},
])
def test_bad_construction(m, kwargs):
    with pytest.raises(ValueError):
        m.Leitner(**kwargs)


def test_review_errors(m):
    s = m.Leitner(["a"])
    with pytest.raises(KeyError):
        s.review("zz", 0, True)
    s.review("a", 0, True)
    with pytest.raises(ValueError):
        s.review("a", 0, True)                    # not due until day 1
    for day in (1, 4, 11, 32):
        s.review("a", day, True)
    with pytest.raises(ValueError):
        s.review("a", 100, True)                  # retired


def test_simulate_skips_empty_days_and_is_deterministic(m):
    def run():
        import random
        rng = random.Random(1)
        s = m.Leitner(["a", "b", "c"], seed=9)
        return s.simulate(30, lambda c, b, d: rng.random() < 0.7)
    log = run()
    assert log == run()
    assert all(results for _, results in log)
