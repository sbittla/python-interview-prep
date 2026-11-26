def test_order(load):
    m = load("ex09_compose_pipeline")
    inc = lambda x: x + 1  # noqa: E731
    dbl = lambda x: x * 2  # noqa: E731
    assert m.compose(inc, dbl)(5) == 11
    assert m.solve(inc, dbl)(5) == 12
    assert m.compose(str, inc, dbl)(5) == "11"


def test_identity(load):
    m = load("ex09_compose_pipeline")
    sentinel = object()
    assert m.solve()(sentinel) is sentinel
    assert m.compose()(sentinel) is sentinel


def test_reusable_and_methods(load):
    m = load("ex09_compose_pipeline")
    normalise = m.solve(str.strip, str.split, " ".join, str.title)
    assert normalise("  ada   lovelace ") == "Ada Lovelace"
    assert normalise("x") == "X"
    assert m.brute_force_normalise("  ada   lovelace ") == "Ada Lovelace"


def test_pipeline_is_reusable_and_lazy(load):
    m = load("ex09_compose_pipeline")
    calls = []

    def spy(x):
        calls.append(x)
        return x + 1
    p = m.solve(spy, spy)
    assert calls == []                  # building the pipeline applies nothing
    assert p(0) == 2 and p(10) == 12    # reusable: no state leaks between calls
    assert calls == [0, 1, 10, 11]
    assert m.compose(len, str.split)("a b c") == 3
