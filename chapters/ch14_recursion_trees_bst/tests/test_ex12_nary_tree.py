import random
from collections import deque

SPEC = (1, [(3, [(5, []), (6, [])]), (2, []), (4, [])])


def random_spec(rng, n):
    nodes = [(0, [])]
    for v in range(1, n):
        child = (v, [])
        rng.choice(nodes)[1].append(child)
        nodes.append(child)
    return nodes[0]


def ref_preorder(spec):
    return [spec[0]] + [v for c in spec[1] for v in ref_preorder(c)]


def ref_postorder(spec):
    return [v for c in spec[1] for v in ref_postorder(c)] + [spec[0]]


def ref_levels(spec):
    levels, queue = [], deque([spec])
    while queue:
        levels.append([s[0] for s in queue])
        queue = deque(c for s in queue for c in s[1])
    return levels


def test_examples(load):
    m = load("ex12_nary_tree")
    t = m.from_nested(SPEC)
    assert (m.max_depth(t), m.level_order(t)) == (3, [[1], [3, 2, 4], [5, 6]])
    assert (m.preorder(t), m.postorder(t)) == ([1, 3, 5, 6, 2, 4], [5, 6, 3, 2, 4, 1])


def test_empty_and_single(load):
    m = load("ex12_nary_tree")
    assert (m.max_depth(None), m.level_order(None), m.preorder(None), m.postorder(None)) == (0, [], [], [])
    one = m.Node(7)
    assert (m.max_depth(one), m.level_order(one), m.preorder(one)) == (1, [[7]], [7])
    assert m.from_binary(m.to_binary(None)) is None


def test_random_against_references(load):
    m = load("ex12_nary_tree")
    rng = random.Random(1412)
    for _ in range(300):
        spec = random_spec(rng, rng.randint(1, 40))
        t = m.from_nested(spec)
        assert m.to_nested(t) == spec
        assert m.preorder(t) == ref_preorder(spec)
        assert m.postorder(t) == ref_postorder(spec)
        assert m.level_order(t) == ref_levels(spec)
        assert m.max_depth(t) == m.max_depth_bfs(t) == len(ref_levels(spec))
        assert m.to_nested(m.from_binary(m.to_binary(t))) == spec
