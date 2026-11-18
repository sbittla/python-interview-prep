import random

import pytest

NAME = "ex055_copy_random_list"


def _nodes(head):
    out = []
    while head:
        out.append(head)
        head = head.next
    return out


def test_examples(load):
    m = load(NAME)
    spec = [(7, None), (13, 0), (11, 4), (10, 2), (1, 0)]
    assert m.describe(m.solve(m.build(spec))) == spec
    assert m.describe(m.solve(m.build([(1, 0)]))) == [(1, 0)]
    assert m.solve(None) is None


@pytest.mark.parametrize("fn", ["solve", "brute_force", "interview_version"])
def test_deep_copy_and_original_intact(load, fn):
    m = load(NAME)
    spec = [(3, None), (3, 0), (3, 2), (4, 1)]
    original = m.build(spec)
    clone = getattr(m, fn)(original)
    assert m.describe(clone) == spec
    assert m.describe(original) == spec
    originals = set(_nodes(original))
    for node in _nodes(clone):
        assert node not in originals
        assert node.random is None or node.random not in originals


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(55)
    for _ in range(200):
        n = rng.randint(0, 12)
        spec = [(rng.randint(0, 3), rng.choice([None] + list(range(n)))) for _ in range(n)]
        assert m.describe(m.solve(m.build(spec))) == m.describe(m.brute_force(m.build(spec))) == spec
