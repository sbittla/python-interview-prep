import random

import pytest


def test_examples(load):
    m = load("ex11_bst_kth_successor")
    root = m.build([5, 3, 6, 2, 4, None, None, 1])
    assert m.kth_smallest(root, 3) == 3
    assert (m.successor(root, 4), m.successor(root, 6), m.successor(root, 0)) == (5, None, 1)


@pytest.mark.parametrize("x, expected", [(-100, 1), (1, 2), (3, 4), (4, 5), (4.5, 5),
                                         (6, None), (99, None)])
def test_successor_edges(load, x, expected):
    m = load("ex11_bst_kth_successor")
    root = m.build([5, 3, 6, 2, 4, None, None, 1])
    assert m.successor(root, x) == expected


def test_kth_bounds(load):
    m = load("ex11_bst_kth_successor")
    root = m.build([5, 3, 6, 2, 4, None, None, 1])
    assert m.kth_smallest(root, 1) == 1 and m.kth_smallest(root, 6) == 6
    with pytest.raises(ValueError):
        m.kth_smallest(root, 7)
    assert m.successor(None, 3) is None


def test_random_against_brute(load):
    m = load("ex11_bst_kth_successor")
    tn = load("treenode")
    rng = random.Random(1411)
    for _ in range(300):
        n = rng.randint(1, 40)
        root = tn.random_bst(rng, n)
        for k in range(1, n + 1):
            assert m.kth_smallest(root, k) == m.kth_smallest_brute(root, k)
        for x in range(-2, 102, 7):
            assert m.successor(root, x) == m.successor_brute(root, x)
