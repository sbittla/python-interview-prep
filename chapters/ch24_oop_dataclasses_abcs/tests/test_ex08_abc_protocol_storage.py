import pytest


@pytest.fixture
def m(load):
    return load("ex08_abc_protocol_storage")


@pytest.mark.parametrize("backend", ["MemoryStorage", "LogStorage"])
def test_backends(m, backend):
    s = getattr(m, backend)()
    assert s.get("missing") is None and s.snapshot() == {}
    assert s.put_many([("b", "2"), ("a", "1"), ("b", "3")]) == 3
    assert s.get("b") == "3" and sorted(s.keys()) == ["a", "b"]
    assert list(s.snapshot()) == ["a", "b"] and s.snapshot()["b"] == "3"
    assert s.put_many([]) == 0
    assert isinstance(s, m.Storage)


def test_abstract_enforcement(m):
    with pytest.raises(TypeError):
        m.Storage()

    class Partial(m.Storage):
        def get(self, key):
            return None

        def put(self, key, value):
            pass

    with pytest.raises(TypeError):
        Partial()
    assert Partial.__abstractmethods__ == frozenset({"keys"})
    m.NaiveBase()                              # rung 2: constructs, fails only later
    with pytest.raises(NotImplementedError):
        m.NaiveBase().keys()


def test_migrate_any_to_any(m):
    src, dst = m.LogStorage(), m.MemoryStorage()
    src.put_many([("x", "old"), ("y", "1"), ("x", "new")])
    assert m.migrate(src, dst) == 2 and dst.snapshot() == {"x": "new", "y": "1"}
    back = m.LogStorage()
    assert m.migrate(dst, back) == 2 and back.snapshot() == dst.snapshot()


def test_protocol_structural(m):
    c1, c2 = m.Connection(), m.Connection()
    assert m.close_all([c1, "s", 3, m.MemoryStorage(), c2]) == 2
    assert not c1.open and not c2.open
    assert m.close_all([]) == 0
    assert isinstance(c1, m.Closeable) and not issubclass(m.Connection, m.Storage)

    class WrongSignature:
        def close(self, a, b, c):              # presence-only check: still "matches"
            return 5

    class NotEvenCallable:
        close = "x"

    assert isinstance(WrongSignature(), m.Closeable)
    assert isinstance(NotEvenCallable(), m.Closeable)
