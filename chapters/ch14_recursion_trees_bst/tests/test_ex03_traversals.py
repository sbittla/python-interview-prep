import random

import pytest


def test_examples(load):
    m = load("ex03_traversals")
    root = m.build([1, 2, 3, 4, 5])
    assert m.preorder_iterative(root) == [1, 2, 4, 5, 3]
    assert m.inorder_iterative(root) == [4, 2, 5, 1, 3]
    assert m.postorder_iterative(root) == [4, 5, 2, 3, 1]


@pytest.mark.parametrize("level", [[], [1], [1, 2], [1, None, 2], [1, 2, None, 3],
                                   [1, None, 2, None, 3]])
def test_edge_shapes(load, level):
    m = load("ex03_traversals")
    root = m.build(level)
    assert m.preorder_iterative(root) == m.preorder_recursive(root)
    assert m.inorder_iterative(root) == m.inorder_recursive(root)
    assert m.postorder_iterative(root) == m.postorder_recursive(root)


def test_random_recursive_vs_iterative(load):
    m = load("ex03_traversals")
    tn = load("treenode")
    rng = random.Random(1403)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(0, 30))
        pre, ino, post = (m.preorder_recursive(root), m.inorder_recursive(root),
                          m.postorder_recursive(root))
        assert m.preorder_iterative(root) == pre == m.traverse_unified(root, "pre")
        assert m.inorder_iterative(root) == ino == m.traverse_unified(root, "in")
        assert m.postorder_iterative(root) == post == m.traverse_unified(root, "post")
        assert m.postorder_two_stack(root) == post


def test_deep_chain_iterative(load):
    m = load("ex03_traversals")
    tn = load("treenode")
    n = 50_000
    left = tn.chain(list(range(n)), side="left")
    assert m.inorder_iterative(left) == list(range(n - 1, -1, -1))
    assert m.postorder_iterative(left) == list(range(n - 1, -1, -1))
    assert m.preorder_iterative(left) == list(range(n))
    with pytest.raises(RecursionError):
        m.inorder_recursive(left)
