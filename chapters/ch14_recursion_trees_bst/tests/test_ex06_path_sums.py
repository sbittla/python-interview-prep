import random

import pytest

EXAMPLE = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]


def test_examples(load):
    m = load("ex06_path_sums")
    t = m.build(EXAMPLE)
    assert m.root_to_leaf_paths(t, 22) == [[5, 4, 11, 2], [5, 8, 4, 5]]
    assert m.count_downward_paths(t, 22) == 3
    assert m.max_path_sum(m.build([-10, 9, 20, None, None, 15, 7])) == 42


@pytest.mark.parametrize("level, best", [
    ([-3], -3), ([-2, -1, -5], -1), ([2, -1, -2], 2), ([1, 2, 3], 6), ([1, -2, 3], 4),
])
def test_max_path_edges(load, level, best):
    m = load("ex06_path_sums")
    assert m.max_path_sum(m.build(level)) == best


def test_root_to_leaf_edges(load):
    m = load("ex06_path_sums")
    assert m.root_to_leaf_paths(None, 0) == []
    assert m.root_to_leaf_paths(m.build([1, 2]), 1) == []        # 1 alone is not a leaf
    assert m.root_to_leaf_paths(m.build([0, 0, 0]), 0) == [[0, 0], [0, 0]]
    assert m.count_downward_paths(None, 0) == 0


def test_random_against_brute(load):
    m = load("ex06_path_sums")
    tn = load("treenode")
    rng = random.Random(1406)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(1, 18), lo=-5, hi=5)
        target = rng.randint(-6, 6)
        assert m.root_to_leaf_paths(root, target) == m.root_to_leaf_paths_brute(root, target)
        assert m.count_downward_paths(root, target) == m.count_downward_brute(root, target)
        assert m.max_path_sum(root) == m.max_path_sum_brute(root)


def test_iterative_max_path_sum(load):
    m = load("ex06_path_sums")
    tn = load("treenode")
    rng = random.Random(1416)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(1, 30), lo=-9, hi=9)
        assert m.max_path_sum_iterative(root) == m.max_path_sum(root)
    assert m.max_path_sum_iterative(m.build([-3])) == -3


def test_deep_chain_iterative_max_path_sum(load):
    m = load("ex06_path_sums")
    tn = load("treenode")
    n = 10_000                                   # recursion would hit the frame limit
    assert m.max_path_sum_iterative(tn.chain([1] * n)) == n
    assert m.max_path_sum_iterative(tn.chain([-1] * n, "left")) == -1
