import copy


def test_multiplied_rows_alias(load):
    m = load("ex03_shared_mutables")
    assert m.aliases([[0] * 3] * 3) == [("root[0]", "root[1]"), ("root[0]", "root[2]")]


def test_independent_rows(load):
    m = load("ex03_shared_mutables")
    assert m.aliases([[0] * 3 for _ in range(3)]) == []
    assert m.aliases([]) == []
    assert m.aliases(42) == []


def test_equal_but_distinct_is_not_alias(load):
    assert load("ex03_shared_mutables").aliases([[1], [1]]) == []


def test_immutables_may_repeat(load):
    t = (1, 2)
    s = "text"
    assert load("ex03_shared_mutables").aliases([t, t, s, s]) == []


def test_cycle_terminates(load):
    m = load("ex03_shared_mutables")
    a: list = [1]
    a.append(a)
    assert m.aliases(a) == [("root", "root[1]")]
    d: dict = {}
    d["me"] = d
    assert m.aliases(d) == [("root", "root['me']")]


def test_alias_inside_tuple_and_dict(load):
    inner = [0]
    assert load("ex03_shared_mutables").aliases({"x": (inner,), "y": inner}) == [
        ("root['x'][0]", "root['y']")]


def test_shared_between(load):
    m = load("ex03_shared_mutables")
    cfg = {"a": [1], "b": ([2], [3]), "c": 4}
    assert m.shared_between(cfg, copy.copy(cfg)) == ["root['a']", "root['b'][0]", "root['b'][1]"]
    assert m.shared_between(cfg, copy.deepcopy(cfg)) == []
    assert m.shared_between(cfg, cfg) == ["root"]
    grid = [[0], [1]]
    assert m.shared_between(grid, list(grid)) == ["root[0]", "root[1]"]
