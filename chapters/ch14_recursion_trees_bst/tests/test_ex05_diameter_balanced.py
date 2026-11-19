import random

import pytest


def test_examples(load):
    m = load("ex05_diameter_balanced")
    assert m.diameter_and_balanced(m.build([1, 2, 3, 4, 5])) == (3, True)
    assert m.diameter_and_balanced(m.build([1, 2, None, 3])) == (2, False)


@pytest.mark.parametrize("level, expected", [
    ([], (0, True)), ([1], (0, True)), ([1, 2], (1, True)),
    ([1, 2, None, 3, 4, 5, None, 6], (4, False)),                 # diameter avoids the root
    ([1, 2, 2, 3, None, None, 3, 4, None, None, 4], (6, False)),  # root ok, children not
])
def test_edge_cases(load, level, expected):
    m = load("ex05_diameter_balanced")
    root = m.build(level)
    assert m.diameter_and_balanced(root) == expected
    assert m.diameter_and_balanced_iterative(root) == expected


def test_random_against_brute(load):
    m = load("ex05_diameter_balanced")
    tn = load("treenode")
    rng = random.Random(1405)
    for _ in range(400):
        root = tn.random_tree(rng, rng.randint(0, 30))
        expected = (m.diameter_brute(root), m.balanced_brute(root))
        assert m.diameter_and_balanced(root) == expected
        assert m.diameter_and_balanced_iterative(root) == expected
        assert m.height(root) == m.height_bfs(root)


def test_deep_chain_iterative(load):
    m = load("ex05_diameter_balanced")
    tn = load("treenode")
    assert m.diameter_and_balanced_iterative(tn.chain(list(range(50_000)))) == (49_999, False)
    assert m.height_bfs(tn.chain(list(range(50_000)), "left")) == 50_000


def test_global_variable_version_is_stale(load):
    m = load("ex05_diameter_balanced")
    assert m.diameter_global_bug(m.build([1, 2, 3, 4, 5])) == 3
    assert m.diameter_global_bug(m.build([1])) == 3        # wrong on purpose: should be 0
    assert m.diameter_and_balanced(m.build([1]))[0] == 0
