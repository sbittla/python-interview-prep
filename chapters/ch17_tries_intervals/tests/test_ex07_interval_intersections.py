import random


def test_examples(load):
    m = load("ex07_interval_intersections")
    a = [[0, 2], [5, 10], [13, 23], [24, 25]]
    b = [[1, 5], [8, 12], [15, 24], [25, 26]]
    assert m.solve(a, b) == [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]


def test_edges(load):
    m = load("ex07_interval_intersections")
    assert m.solve([[1, 3]], [[3, 5]]) == [[3, 3]]          # touching -> one point
    assert m.solve([[1, 3]], []) == [] == m.solve([], [])
    assert m.solve([[1, 3]], [[4, 6]]) == []
    assert m.solve([[1, 10]], [[2, 3], [5, 7], [9, 12]]) == [[2, 3], [5, 7], [9, 10]]
    assert m.solve([[2, 2]], [[2, 2]]) == [[2, 2]]


def _sorted_disjoint(rng):
    out, x = [], rng.randint(0, 2)
    for _ in range(rng.randint(0, 5)):
        s = x + rng.randint(0, 2)
        e = s + rng.randint(0, 3)
        out.append([s, e])
        x = e + 1
    return out


def test_random_against_brute(load):
    m = load("ex07_interval_intersections")
    rng = random.Random(7)
    for _ in range(400):
        a, b = _sorted_disjoint(rng), _sorted_disjoint(rng)
        assert m.solve(a, b) == m.brute_force(a, b), (a, b)
