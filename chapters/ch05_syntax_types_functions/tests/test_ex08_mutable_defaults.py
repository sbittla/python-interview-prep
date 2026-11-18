def test_independent_defaults(load):
    m = load("ex08_mutable_defaults")
    assert m.solve("ada") == ["ada"]
    assert m.solve("grace") == ["grace"]
    assert m.solve.__defaults__ == (None,)


def test_passed_registry_is_mutated_even_if_empty(load):
    m = load("ex08_mutable_defaults")
    empty = []
    assert m.solve("x", empty) is empty
    assert empty == ["x"]


def test_buggy_version_leaks(load):
    m = load("ex08_mutable_defaults")
    m.buggy_register("a")
    assert m.buggy_register("b")[-2:] == ["a", "b"]


def test_tag_counts(load):
    m = load("ex08_mutable_defaults")
    assert m.tag_counts(["a", "b", "a"]) == {"a": 2, "b": 1}
    assert m.tag_counts(["c"]) == {"c": 1}
    existing = {"a": 5}
    assert m.tag_counts(["a"], existing) is existing
    assert existing == {"a": 6}
    assert m.tag_counts([]) == {}
