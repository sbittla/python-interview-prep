import random

import pytest


def test_examples(load):
    m = load("ex09_open_addressing_map")
    d = m.CompactDict()
    d["a"] = 1
    d["b"] = 2
    d["a"] = 3
    del d["b"]
    assert (d.items(), len(d), "b" in d) == ([("a", 3)], 1, False)
    assert m.probe_sequence(8, 8, 4) == [0, 1, 6, 7]


def test_probe_visits_every_slot(load):
    m = load("ex09_open_addressing_map")
    for h in (0, 5, 12345, -7, 2**63 + 11):
        assert set(m.probe_sequence(h, 16, 200)) == set(range(16))


def test_missing_key_errors(load):
    m = load("ex09_open_addressing_map")
    d = m.CompactDict()
    with pytest.raises(KeyError):
        d["x"]
    with pytest.raises(KeyError):
        del d["x"]
    assert len(d) == 0 and d.keys() == []


def test_collision_chain_survives_delete(load):
    m = load("ex09_open_addressing_map")
    d = m.CompactDict()
    for k in (0, 8, 16, 24):          # same start slot in a table of 8
        d[k] = k
    del d[8]
    assert d[16] == 16 and d[24] == 24 and 8 not in d
    d[8] = "new"
    assert d.keys() == [0, 16, 24, 8]


def test_equal_keys_of_different_types(load):
    d = load("ex09_open_addressing_map").CompactDict()
    d[1] = "int"
    d[1.0] = "float"                  # 1 == 1.0 and hash(1) == hash(1.0)
    assert len(d) == 1 and d[True] == "float"


def test_random_against_dict(load):
    m = load("ex09_open_addressing_map")
    rng = random.Random(9)
    ours, ref = m.CompactDict(), {}
    for _ in range(3000):
        k = rng.choice([rng.randint(-40, 40), str(rng.randint(0, 30))])
        op = rng.random()
        if op < 0.6:
            ours[k] = ref[k] = rng.randint(0, 9)
        elif op < 0.85 and k in ref:
            del ours[k]
            del ref[k]
        else:
            assert (k in ours) == (k in ref)
        assert len(ours) == len(ref)
    assert ours.items() == list(ref.items())     # same insertion order as dict
    size = ours.table_size()
    assert size & (size - 1) == 0


def test_growth_points(load):
    m = load("ex09_open_addressing_map")
    d = m.CompactDict()
    points = []
    for i in range(100):
        before = d.table_size()
        d[i] = i
        if d.table_size() != before:
            points.append(len(d))
    assert points == [6, 11, 22, 43, 86]


def test_assoc_list(load):
    m = load("ex09_open_addressing_map")
    a = m.AssocList()
    a["x"] = 1
    a["x"] = 2
    assert a["x"] == 2
    with pytest.raises(KeyError):
        a["y"]
