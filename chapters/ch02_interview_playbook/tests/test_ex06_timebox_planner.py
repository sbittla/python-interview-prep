import pytest


def test_example_45(load):
    m = load("ex06_timebox_planner")
    assert m.plan(45)[1:5] == [("clarify+examples", 5, 10), ("brute+optimise", 10, 19),
                               ("code", 19, 33), ("test", 33, 40)]


def test_60(load):
    m = load("ex06_timebox_planner")
    assert [e - s for _, s, e in m.plan(60)] == [5, 8, 12, 20, 10, 5]


@pytest.mark.parametrize("total, intro, closing", [
    (45, 5, 5), (60, 5, 5), (50, 3, 7), (61, 0, 0), (14, 5, 5), (90, 15, 5),
])
def test_contiguous_and_exact(load, total, intro, closing):
    m = load("ex06_timebox_planner")
    sched = m.plan(total, intro, closing)
    assert sched[0] == ("intro", 0, intro)
    assert sched[-1][0] == "closing" and sched[-1][2] == total
    for (_, _, end), (_, start, _) in zip(sched, sched[1:]):
        assert end == start
    assert all(e - s >= 0 for _, s, e in sched)


def test_too_short(load):
    m = load("ex06_timebox_planner")
    with pytest.raises(ValueError):
        m.plan(12)


def test_checkpoint(load):
    m = load("ex06_timebox_planner")
    s = m.plan(45)
    assert m.checkpoint(s, 10, "clarify+examples") == "on track"
    msg = m.checkpoint(s, 14, "clarify+examples")
    assert msg.startswith("4 min behind") and "assumptions" in msg
    assert "stub" in m.checkpoint(s, 36, "code")
    with pytest.raises(ValueError):
        m.checkpoint(s, 1, "lunch")


def test_tie_break_non_standard_total(load):
    m = load("ex06_timebox_planner")
    # work = 40: shares 6 / 10 / 16 / 8 exactly
    assert [e - s for _, s, e in m.plan(50, 3, 7)] == [3, 6, 10, 16, 8, 7]
    # work = 42: floors 6/10/16/8 = 40, remainders 30/50/80/40 -> extra minutes to code, brute
    assert [e - s for _, s, e in m.plan(52, 5, 5)] == [5, 6, 11, 17, 8, 5]
    # work = 50: floors 7/12/20/10, remainders 50/50/0/0 -> tie goes to the earlier phase
    assert [e - s for _, s, e in m.plan(60)][1:5] == [8, 12, 20, 10]
