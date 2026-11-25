import functools

import pytest


def test_parsers(load):
    p = load("ex09_functools_toolkit").make_parsers()
    assert p["bin"]("101") == 5 and p["hex"]("ff") == 255 and p["hex"]("0") == 0
    assert isinstance(p["bin"], functools.partial)
    assert p["bin"].func is int and p["bin"].keywords == {"base": 2}


@pytest.mark.parametrize("obj, expected", [
    (5, "int 5"), (True, "bool True"), (False, "bool False"), ("abc", "str of length 3"),
    ([], "list []"), ([1, "a", [False]], "list [int 1, str of length 1, list [bool False]]"),
    ({"b": 1, "a": 2}, "dict with keys ['a', 'b']"), ({}, "dict with keys []"),
    (2.5, "object of type float"), (None, "object of type NoneType"),
])
def test_describe(load, obj, expected):
    assert load("ex09_functools_toolkit").describe(obj) == expected


def test_describe_dispatches_on_subclass(load):
    m = load("ex09_functools_toolkit")

    class MyList(list):
        pass

    assert m.describe(MyList([1])) == "list [int 1]"


def test_version_ordering(load):
    V = load("ex09_functools_toolkit").Version
    assert V("1.10") > V("1.9.9") and V("1.9.9") < V("1.10")
    assert V("1.2") == V("1.2.0") and V("1.2") >= V("1.2.0") and V("1.2") <= V("1.2.0")
    assert not V("1.2") < V("1.2.0")
    assert V("0") == V("0.0") and hash(V("0")) == hash(V("0.0"))
    texts = ["1.10", "1.9.9", "1.2.0", "0.9", "2"]
    assert [v.text for v in sorted(map(V, texts))] == ["0.9", "1.2.0", "1.9.9", "1.10", "2"]
    assert len({V("1.2"), V("1.2.0"), V("1.3")}) == 2


def test_version_foreign_types(load):
    V = load("ex09_functools_toolkit").Version
    assert V("1") != "1"
    assert V("1").__eq__("1") is NotImplemented
    with pytest.raises(TypeError):
        V("1") < "2"
