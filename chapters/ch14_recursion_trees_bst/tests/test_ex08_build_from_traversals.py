import random

import pytest


def pre_and_post(root):
    pre, rev_post = [], []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        pre.append(node.val)
        stack += [c for c in (node.right, node.left) if c]
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        rev_post.append(node.val)
        stack += [c for c in (node.left, node.right) if c]
    return pre, rev_post[::-1]


def test_examples(load):
    m = load("ex08_build_from_traversals")
    expected = [3, 9, 20, None, None, 15, 7]
    assert m.to_level(m.build_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])) == expected
    assert m.to_level(m.build_post_in([9, 15, 7, 20, 3], [9, 3, 15, 20, 7])) == expected


@pytest.mark.parametrize("pre, ino, level", [
    ([], [], []), ([1], [1], [1]), ([1, 2, 3], [3, 2, 1], [1, 2, None, 3]),
    ([1, 2, 3], [1, 2, 3], [1, None, 2, None, 3]),
])
def test_edge_cases(load, pre, ino, level):
    m = load("ex08_build_from_traversals")
    assert m.to_level(m.build_pre_in(pre, ino)) == level
    assert m.to_level(m.build_slicing(pre, ino)) == level


def test_random_round_trip(load):
    m = load("ex08_build_from_traversals")
    tn = load("treenode")
    rng = random.Random(1408)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(0, 40), lo=-50, hi=50, distinct=True)
        pre, post = pre_and_post(root)
        ino = tn.inorder_values(root)
        level = tn.to_level(root)
        assert m.to_level(m.build_pre_in(pre, ino)) == level
        assert m.to_level(m.build_slicing(pre, ino)) == level
        assert m.to_level(m.build_post_in(post, ino)) == level
