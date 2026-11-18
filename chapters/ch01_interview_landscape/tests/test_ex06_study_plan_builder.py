import pytest


@pytest.mark.parametrize("args, expected", [
    ((6, 15, True), ("crash-4", False)),
    ((10, 11, False), ("standard-8", False)),
    ((12, 7, False), ("foundations-12", False)),
    ((12, 7, True), ("standard-8", False)),
    ((5, 10, False), ("crash-4", True)),
])
def test_choose(load, args, expected):
    m = load("ex06_study_plan_builder")
    assert m.choose_plan(*args) == expected


def test_not_enough_time(load):
    m = load("ex06_study_plan_builder")
    with pytest.raises(ValueError):
        m.choose_plan(3, 10, True)


def test_build(load):
    m = load("ex06_study_plan_builder")
    plan = m.build_plan("standard-8", "L")
    assert len(plan) == 8 and plan[5] == (6, "Track part 1: Ch. 38-40")
    assert m.build_plan("standard-8", "S")[6] == (7, "Track part 2: Ch. 28, 31-32")
    f = m.build_plan("foundations-12", "M")
    assert len(f) == 12 and f[0][0] == 1 and f[-1][0] == 12
    assert f[9] == (10, "Track part 1: Ch. 33-35")
    assert len(m.build_plan("crash-4", "S")) == 4


@pytest.mark.parametrize("plan, track", [("standard-8", "X"), ("weekend", "S")])
def test_build_errors(load, plan, track):
    m = load("ex06_study_plan_builder")
    with pytest.raises(ValueError):
        m.build_plan(plan, track)
