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


def test_labels_keep_order_and_floats(load):
    m = load("ex07_flexible_summary")
    out = m.solve(0.1, 0.2, b=1, a=2)
    assert list(out) == ["count", "mean", "min", "max", "b", "a"]
    assert out["mean"] == 0.15 and out["min"] == 0.1


def test_precision_is_keyword_only(load):
    import inspect
    m = load("ex07_flexible_summary")
    params = inspect.signature(m.solve).parameters
    assert params["precision"].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["skip_none"].kind is inspect.Parameter.KEYWORD_ONLY
    assert m.solve(1, 2, 4, precision=1)["mean"] == 2.3
