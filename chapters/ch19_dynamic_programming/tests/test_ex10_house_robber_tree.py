import random

import pytest

M = "ex10_house_robber_tree"


def test_examples(load):
    m = load(M)
    assert m.rob_tree(m.build([3, 2, 3, None, 3, None, 1])) == 7
    assert m.rob_tree(m.build([3, 4, 5, 1, 3, None, 1])) == 9
    assert m.rob_tree(None) == 0


@pytest.mark.parametrize("values, expected", [
    ([], 0), ([5], 5), ([1, 9], 9), ([9, 1, 1], 9), ([4, 1, None, 2, None, 3], 7),
    ([0, 0, 0], 0),
])
def test_edges(load, values, expected):
    m = load(M)
    root = m.build(values)
    assert m.rob_tree(root) == m.rob_tree_pair(root) == m.rob_tree_memo(root) == expected
    assert m.rob_tree_brute(root) == expected


def _brute_subsets(m, root):
    """Independent check: try every subset of nodes, reject parent-child pairs."""
    nodes, parent = [], {}
    stack = [(root, None)] if root else []
    while stack:
        node, par = stack.pop()
        parent[node] = par
        nodes.append(node)
        stack.extend((c, node) for c in (node.left, node.right) if c)
    best = 0
    for mask in range(1 << len(nodes)):
        chosen = {nodes[i] for i in range(len(nodes)) if mask >> i & 1}
        if any(parent[n] in chosen for n in chosen):
            continue
        best = max(best, sum(n.val for n in chosen))
    return best


def test_random_trees_against_subsets(load):
    m = load(M)
    rng = random.Random(37)
    for _ in range(150):
        values = [rng.choice([None, rng.randint(0, 9)]) if i else rng.randint(0, 9)
                  for i in range(rng.randint(0, 11))]
        root = m.build(values)
        expected = _brute_subsets(m, root)
        assert m.rob_tree(root) == m.rob_tree_pair(root) == m.rob_tree_memo(root) == expected


def test_deep_chain_iterative(load):
    m = load(M)
    deep = m.chain(10_000)                     # values 1..10000 down one side
    assert m.rob_tree(deep) == sum(range(2, 10_001, 2))
