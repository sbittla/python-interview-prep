import random


def test_examples(load):
    m = load("ex07_lca")
    t = m.build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    assert m.lca(t, m.find(t, 5), m.find(t, 4)).val == 5
    assert m.lca(t, m.find(t, 5), m.find(t, 1)).val == 3
    b = m.build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    assert m.lca_bst(b, m.find(b, 2), m.find(b, 8)).val == 6
    assert m.lca_bst(b, m.find(b, 2), m.find(b, 4)).val == 2


def test_identity_with_repeated_values(load):
    m = load("ex07_lca")
    t = m.build([1, 1, 1, 1])          # four nodes, same value
    a, b = t.left.left, t.right
    assert m.lca(t, a, b) is t
    assert m.lca(t, a, t.left) is t.left
    assert m.lca_parent_map(t, a, b) is t


def test_random_against_parent_map(load):
    m = load("ex07_lca")
    tn = load("treenode")
    rng = random.Random(1407)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(2, 40), lo=0, hi=60, distinct=True)
        vals = [v for v in tn.to_level(root) if v is not None]
        a, b = rng.sample(vals, 2)
        p, q = m.find(root, a), m.find(root, b)
        assert m.lca(root, p, q) is m.lca_parent_map(root, p, q)


def test_bst_random(load):
    m = load("ex07_lca")
    tn = load("treenode")
    rng = random.Random(1417)
    for _ in range(300):
        root = tn.random_bst(rng, rng.randint(2, 40))
        a, b = rng.sample(tn.inorder_values(root), 2)
        p, q = m.find(root, a), m.find(root, b)
        assert m.lca_bst(root, p, q) is m.lca(root, p, q)
