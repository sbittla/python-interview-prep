import random

import pytest


@pytest.fixture
def m(load):
    return load("ex04_mro_c3")


def test_init_order(m):
    assert m.init_order() == ["Child", "Left", "Right", "Base"]


def test_diamond(m):
    d = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    assert m.c3_linearize("D", d) == ["D", "B", "C", "A"]
    assert m.dfs_first_visit("D", d) == ["D", "B", "A", "C"]
    assert m.dfs_last_visit("D", d) == ["D", "B", "C", "A"]


def test_root_and_single_chain(m):
    assert m.c3_linearize("A", {"A": []}) == ["A"]
    assert m.c3_linearize("C", {"A": [], "B": ["A"], "C": ["B"]}) == ["C", "B", "A"]


def test_classic_example_and_last_visit_differs(m):
    wiki = {"O": [], "A": ["O"], "B": ["O"], "C": ["O"], "D": ["O"], "E": ["O"],
            "K1": ["A", "B", "C"], "K2": ["D", "B", "E"], "K3": ["D", "A"],
            "Z": ["K1", "K2", "K3"]}
    expected = ["Z", "K1", "K2", "K3", "D", "A", "B", "C", "E", "O"]
    assert m.c3_linearize("Z", wiki) == expected == m.python_mro("Z", wiki)
    assert m.dfs_last_visit("Z", wiki) != expected


def test_inconsistent(m):
    bad = {"X": [], "Y": ["X"], "Z": ["X", "Y"]}
    with pytest.raises(ValueError):
        m.c3_linearize("Z", bad)
    with pytest.raises(TypeError):
        m.python_mro("Z", bad)


def test_random_hierarchies_match_python(m):
    rng = random.Random(7)
    checked = 0
    for _ in range(300):
        n = rng.randint(1, 9)
        names = [f"C{i}" for i in range(n)]
        bases = {name: rng.sample(names[:i], rng.randint(0, min(3, i)))
                 for i, name in enumerate(names)}
        target = names[-1]
        try:
            want = m.python_mro(target, bases)
        except TypeError:
            with pytest.raises(ValueError):
                m.c3_linearize(target, bases)
            continue
        assert m.c3_linearize(target, bases) == want
        checked += 1
    assert checked > 50
