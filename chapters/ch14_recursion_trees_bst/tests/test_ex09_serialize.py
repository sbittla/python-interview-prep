import random

import pytest


def test_examples(load):
    m = load("ex09_serialize")
    t = m.build([1, 2, 3, None, None, 4, 5])
    assert m.serialize(t) == "1,2,#,#,3,4,#,#,5,#,#"
    assert m.serialize_bfs(t) == "1,2,3,#,#,4,5"
    assert m.to_level(m.deserialize("1,2,#,#,3,4,#,#,5,#,#")) == [1, 2, 3, None, None, 4, 5]


@pytest.mark.parametrize("level", [[], [-7], [10, -20, None, 300], [1, 1, 1], [0, None, 0, 0]])
def test_edge_round_trips(load, level):
    m = load("ex09_serialize")
    root = m.build(level)
    assert m.to_level(m.deserialize(m.serialize(root))) == level
    assert m.to_level(m.deserialize_bfs(m.serialize_bfs(root))) == level


def test_empty_tree_strings(load):
    m = load("ex09_serialize")
    assert m.serialize(None) == "#" and m.deserialize("#") is None
    assert m.serialize_bfs(None) == "" and m.deserialize_bfs("") is None


def test_markers_remove_ambiguity(load):
    m = load("ex09_serialize")
    a, b = m.build([1, 2]), m.build([1, None, 2])
    assert m.preorder_no_markers(a) == m.preorder_no_markers(b)
    assert m.serialize(a) != m.serialize(b)


def test_random_round_trips(load):
    m = load("ex09_serialize")
    tn = load("treenode")
    rng = random.Random(1409)
    for _ in range(300):
        root = tn.random_tree(rng, rng.randint(0, 40), lo=-999, hi=999)
        level = tn.to_level(root)
        assert m.to_level(m.deserialize(m.serialize(root))) == level
        assert m.to_level(m.deserialize_bfs(m.serialize_bfs(root))) == level


def test_bfs_codec_deep_chain(load):
    m = load("ex09_serialize")
    tn = load("treenode")
    long = tn.chain(list(range(30_000)), side="left")
    s = m.serialize_bfs(long)
    assert m.serialize_bfs(m.deserialize_bfs(s)) == s
    assert m.serialize(long).count("#") == 30_001       # iterative serialize: any depth
