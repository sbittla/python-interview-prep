import pytest


def test_countdown_is_single_use_iterator(load):
    m = load("ex02_custom_iterators")
    c = m.Countdown(3)
    assert iter(c) is c
    assert list(c) == [3, 2, 1]
    assert list(c) == []
    assert list(m.Countdown(0)) == []
    with pytest.raises(StopIteration):
        next(m.Countdown(0))


def test_steprange_is_reiterable(load):
    m = load("ex02_custom_iterators")
    r = m.StepRange(0, 10, 3)
    assert list(r) == [0, 3, 6, 9]
    assert list(r) == [0, 3, 6, 9]
    assert iter(r) is not iter(r)


@pytest.mark.parametrize("args", [(0, 10, 3), (10, 0, -4), (5, 5, 1), (0, -5, 1),
                                  (-3, 3, 2), (3, -3, -2), (0, 1, 5)])
def test_steprange_matches_range(load, args):
    m = load("ex02_custom_iterators")
    assert list(m.StepRange(*args)) == list(range(*args))
    assert len(m.StepRange(*args)) == len(range(*args))


def test_step_zero(load):
    m = load("ex02_custom_iterators")
    with pytest.raises(ValueError):
        m.StepRange(0, 5, 0)


def test_manual_for(load):
    m = load("ex02_custom_iterators")
    assert m.manual_for("abc") == ["a", "b", "c"]
    assert m.manual_for([]) == []
