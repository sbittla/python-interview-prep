import random

import pytest

NAME = "ex051_linked_list_cycle"


def test_examples(load):
    m = load(NAME)
    head = m.build([3, 2, 0, -4], 1)
    assert m.entry_index(head, m.solve(head)) == 1
    head = m.build([1, 2], 0)
    assert m.entry_index(head, m.solve(head)) == 0
    assert m.solve(m.build([1, 2, 3], -1)) is None


@pytest.mark.parametrize("values, pos", [([], -1), ([1], -1), ([1], 0), ([1, 1, 1], 2), ([1, 2, 3], 0)])
def test_edge_cases(load, values, pos):
    m = load(NAME)
    head = m.build(values, pos)
    assert m.entry_index(head, m.solve(head)) == pos
    assert m.entry_index(head, m.interview_version(head)) == pos


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(51)
    for _ in range(300):
        n = rng.randint(0, 30)
        pos = rng.randint(-1, n - 1) if n else -1
        head = m.build([rng.randint(0, 3) for _ in range(n)], pos)
        assert m.solve(head) is m.brute_force(head)
