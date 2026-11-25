import inspect


def greet(name, punct="!"):
    """Say hello."""
    return f"hi {name}{punct}"


def test_counts_and_forwards(load):
    m = load("ex03_count_calls_wraps")
    g = m.count_calls(greet)
    assert g.calls == 0
    assert g("ann") == "hi ann!" and g(name="bo", punct="?") == "hi bo?"
    assert g.calls == 2


def test_counters_are_per_function(load):
    m = load("ex03_count_calls_wraps")
    a, b = m.count_calls(greet), m.count_calls(len)
    a("x")
    a("y")
    b("abc")
    assert (a.calls, b.calls) == (2, 1)


def test_wraps_keeps_metadata(load):
    m = load("ex03_count_calls_wraps")
    g = m.count_calls(greet)
    assert (g.__name__, g.__doc__) == ("greet", "Say hello.")
    assert g.__wrapped__ is greet and inspect.unwrap(g) is greet
    assert list(inspect.signature(g).parameters) == ["name", "punct"]


def test_naive_loses_metadata(load):
    m = load("ex03_count_calls_wraps")
    n = m.count_calls_naive(greet)
    assert n("z") == "hi z!" and n.calls == 1
    assert n.__name__ == "wrapper" and n.__doc__ is None
    assert not hasattr(n, "__wrapped__")


def test_stacking_order(load):
    m = load("ex03_count_calls_wraps")

    @m.bold
    @m.italic
    def word(w):
        return w

    assert word("x") == "<b><i>x</i></b>"
    assert m.italic(m.bold(lambda: "x"))() == "<i><b>x</b></i>"
    assert word.__name__ == "word"
