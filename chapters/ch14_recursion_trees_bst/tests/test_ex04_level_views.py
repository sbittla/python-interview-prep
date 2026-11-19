import random

import pytest


def test_examples(load):
    m = load("ex04_level_views")
    root = m.build([3, 9, 20, None, None, 15, 7])
    assert m.level_order(root) == [[3], [9, 20], [15, 7]]
    assert m.zigzag(root) == [[3], [20, 9], [15, 7]]
    assert m.right_view(m.build([1, 2, 3, None, 5])) == [1, 3, 5]


@pytest.mark.parametrize("level, view", [
    ([], []), ([1], [1]), ([1, 2, 3, 4], [1, 3, 4]), ([1, 2, None, 3], [1, 2, 3]),
    ([1, 2, 3, None, 5, None, 4], [1, 3, 4]),
])
def test_right_view_edges(load, level, view):
    m = load("ex04_level_views")
    root = m.build(level)
    assert m.right_view(root) == m.right_view_dfs(root) == view


def test_zigzag_four_levels(load):
    m = load("ex04_level_views")
    root = m.build(list(range(1, 16)))
    assert m.zigzag(root) == [[1], [3, 2], [4, 5, 6, 7], [15, 14, 13, 12, 11, 10, 9, 8]]


def test_random_bfs_vs_dfs(load):
    m = load("ex04_level_views")
    tn = load("treenode")
    rng = random.Random(1404)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(0, 40))
        levels = m.level_order(root)
        assert levels == m.level_order_dfs(root)
        assert sum(levels, []) == [v for v in tn.to_level(root) if v is not None]
        assert m.right_view(root) == m.right_view_dfs(root)
        for d, (a, b) in enumerate(zip(m.zigzag(root), levels)):
            assert a == (b if d % 2 == 0 else b[::-1])
