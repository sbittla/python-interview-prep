import random

import pytest

NAME = "ex049_reverse_linked_list"


def test_examples(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build([1, 2, 3, 4]))) == [4, 3, 2, 1]
    assert m.to_list(m.solve(m.build([7]))) == [7]
    assert m.solve(m.build([])) is None


@pytest.mark.parametrize("values", [[], [1], [1, 2], [2, 1, 2], [0, -1, -1, 0]])
def test_edge_cases(load, values):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(values))) == values[::-1]
    assert m.to_list(m.interview_version(m.build(values))) == values[::-1]


def test_reuses_nodes(load):
    m = load(NAME)
    head = m.build([1, 2, 3])
    nodes = [head, head.next, head.next.next]
    new_head = m.solve(head)
    assert new_head is nodes[2] and nodes[0].next is None


def test_long_list(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(list(range(100_000)))))[0] == 99_999


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(49)
    for _ in range(200):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(0, 20))]
        assert m.to_list(m.solve(m.build(values))) == m.to_list(m.brute_force(m.build(values)))
