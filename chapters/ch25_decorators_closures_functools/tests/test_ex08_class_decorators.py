import pytest


def test_register_returns_unchanged(load):
    m = load("ex08_class_decorators")
    reg = {}

    class A:
        pass

    assert m.register(reg)(A) is A
    assert m.register(reg, name="b")(len) is len
    assert reg == {"A": A, "b": len}
    with pytest.raises(KeyError):
        m.register(reg)(A)


def test_auto_repr(load):
    m = load("ex08_class_decorators")

    @m.auto_repr
    class Point:
        def __init__(self, x, y=0):
            self.x, self.y = x, y

    assert isinstance(Point(1), Point)
    assert repr(Point(1, "a")) == "Point(x=1, y='a')"
    assert repr(Point(3)) == "Point(x=3, y=0)"


def test_count_calls_on_function_and_method(load):
    m = load("ex08_class_decorators")

    @m.CountCalls
    def double(x):
        """Double it."""
        return 2 * x

    assert double(4) == 8 and double.calls == 1
    assert (double.__name__, double.__doc__) == ("double", "Double it.")

    class Cart:
        def __init__(self):
            self.items = []

        @m.CountCalls
        def add(self, item):
            self.items.append(item)
            return len(self.items)

    c1, c2 = Cart(), Cart()
    assert c1.add("a") == 1 and c1.add("b") == 2 and c2.add("z") == 1
    assert Cart.add.calls == 3 and c1.items == ["a", "b"]
    assert isinstance(Cart.__dict__["add"], m.CountCalls)


def test_no_get_breaks_methods(load):
    m = load("ex08_class_decorators")

    class C:
        @m.CountCallsNoGet
        def f(self, x):
            return x

    with pytest.raises(TypeError):
        C().f(1)
