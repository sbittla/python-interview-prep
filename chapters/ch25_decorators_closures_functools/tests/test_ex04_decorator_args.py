import pytest


def test_repeat(load):
    m = load("ex04_decorator_args")
    calls = []

    @m.repeat(3)
    def f(x, *, y=0):
        calls.append(x)
        return x + y

    assert f(1, y=2) == [3, 3, 3] and calls == [1, 1, 1]
    assert f.__name__ == "f"
    assert m.repeat(0)(lambda: 1)() == []


def test_repeat_rejects_negative_at_decoration(load):
    with pytest.raises(ValueError):
        load("ex04_decorator_args").repeat(-1)


def test_validate_positional_keyword_and_default(load):
    m = load("ex04_decorator_args")

    @m.validate(qty=lambda q: q > 0, unit=lambda u: u in {"kg", "g"})
    def order(item, qty, unit="kg"):
        return f"{qty}{unit} {item}"

    assert order("rice", 2) == "2kg rice"
    assert order(item="salt", qty=5, unit="g") == "5g salt"
    with pytest.raises(ValueError, match=r"order: invalid qty=0"):
        order("rice", 0)
    with pytest.raises(ValueError, match=r"invalid qty=-1"):
        order("rice", qty=-1)
    with pytest.raises(ValueError, match=r"invalid unit='lb'"):
        order("rice", 1, "lb")


def test_validate_checks_defaults(load):
    m = load("ex04_decorator_args")
    f = m.validate(n=lambda v: v > 0)(lambda n=0: n)
    with pytest.raises(ValueError):
        f()
    assert f(4) == 4


def test_validate_unknown_param(load):
    m = load("ex04_decorator_args")
    with pytest.raises(TypeError):
        m.validate(colour=bool)(lambda size: size)


def test_tag_with_and_without_parens(load):
    m = load("ex04_decorator_args")

    @m.tag
    def a():
        return "hi"

    @m.tag(name="em")
    def b():
        return "hi"

    assert (a(), b()) == ("<span>hi</span>", "<em>hi</em>")
    assert (a.__name__, b.__name__) == ("a", "b")
