import pytest


def test_examples(load):
    m = load("ex07_flexible_summary")
    assert m.solve(3, 1, 2) == {"count": 3, "mean": 2.0, "min": 1, "max": 3}
    assert m.solve(1, None, 2, precision=1, unit="ms") == {
        "count": 2, "mean": 1.5, "min": 1, "max": 2, "unit": "ms"}


def test_precision_and_unpacking(load):
    m = load("ex07_flexible_summary")
    assert m.solve(*[1, 2, 2], precision=3)["mean"] == 1.667
    assert m.solve(1, 2, 2, precision=0)["mean"] == 2.0


def test_keyword_only(load):
    m = load("ex07_flexible_summary")
    # a fourth positional value is data, not the precision
    assert m.solve(1, 2, 3, 2)["count"] == 4


@pytest.mark.parametrize("args, kwargs, exc, msg", [
    ((), {}, ValueError, "no values"),
    ((None, None), {}, ValueError, "no values"),
    ((1, None), {"skip_none": False}, TypeError, "None in values"),
    ((1,), {"mean": 3}, ValueError, "label clashes: mean"),
])
def test_errors(load, args, kwargs, exc, msg):
    m = load("ex07_flexible_summary")
    with pytest.raises(exc) as info:
        m.solve(*args, **kwargs)
    assert str(info.value) == msg
