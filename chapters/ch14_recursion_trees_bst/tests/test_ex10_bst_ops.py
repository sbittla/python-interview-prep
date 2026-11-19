import random

import pytest


def test_examples(load):
    m = load("ex10_bst_ops")
    root = m.build([5, 3, 6, 2, 4, None, 7])
    assert m.to_level(m.delete(root, 3)) == [5, 4, 6, 2, None, None, 7]
    assert m.is_valid_bst(m.build([5, 1, 6, None, None, 3, 7])) is False


def test_local_only_check_is_fooled(load):
    m = load("ex10_bst_ops")
    trap = m.build([5, 1, 6, None, None, 3, 7])
    assert m.is_valid_local_only(trap) is True
    assert m.is_valid_bst(trap) is False and m.is_valid_brute(trap) is False


@pytest.mark.parametrize("level, valid", [
    ([], True), ([1], True), ([2, 2], False), ([2, None, 2], False), ([2, 1, 3], True),
    ([-2**31, None, 2**31 - 1], True), ([10, 5, 15, None, None, 6, 20], False),
])
def test_validate_edges(load, level, valid):
    m = load("ex10_bst_ops")
    root = m.build(level)
    assert m.is_valid_bst(root) is valid
    assert m.is_valid_brute(root) is valid


def test_delete_root_and_two_children(load):
    m = load("ex10_bst_ops")
    tn = load("treenode")
    root = m.build([8, 3, 12, None, None, 10, 14, None, 11])    # successor 10 has right child 11
    root = m.delete(root, 8)
    assert root.val == 10 and tn.inorder_values(root) == [3, 10, 11, 12, 14]
    assert m.delete(m.build([1]), 1) is None and m.delete(None, 1) is None


def test_search_insert_delete_random(load):
    m = load("ex10_bst_ops")
    tn = load("treenode")
    rng = random.Random(1410)
    for _ in range(200):
        keys = [rng.randint(0, 40) for _ in range(rng.randint(0, 30))]
        root = None
        for k in keys:
            root = m.insert(root, k)
        present = sorted(set(keys))
        assert tn.inorder_values(root) == present and m.is_valid_bst(root)
        for k in range(-1, 42):
            assert (m.search(root, k) is not None) == (k in present)
        for k in rng.sample(range(-1, 42), 15):
            root = m.delete(root, k)
            if k in present:
                present.remove(k)
            assert tn.inorder_values(root) == present
            assert m.is_valid_bst(root)


def test_validate_random_trees_against_brute(load):
    m = load("ex10_bst_ops")
    tn = load("treenode")
    rng = random.Random(1420)
    for _ in range(400):
        if rng.random() < 0.5:
            root = tn.random_bst(rng, rng.randint(0, 20))
            if root and rng.random() < 0.5:          # corrupt one key deep down
                node = root
                while node.left or node.right:
                    kids = [c for c in (node.left, node.right) if c]
                    node = rng.choice(kids)
                node.val = rng.randint(-5, 105)
        else:
            root = tn.random_tree(rng, rng.randint(0, 12), lo=0, hi=20)
        assert m.is_valid_bst(root) == m.is_valid_brute(root)
