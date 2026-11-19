import random

import pytest

FUNCS = ["brute_force", "prefix_max", "trap", "trap_stack"]


def test_examples(load):
    m = load("ex08_trapping_rain_water")
    assert m.trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert m.trap([4, 2, 0, 3, 2, 5]) == 9


@pytest.mark.parametrize("fn", FUNCS)
@pytest.mark.parametrize("heights, expected", [
    ([], 0), ([3], 0), ([3, 3], 0), ([1, 2, 3], 0), ([3, 2, 1], 0), ([3, 0, 3], 3),
    ([5, 0, 0, 0, 1], 3), ([2, 0, 2, 0, 2], 4), ([0, 0, 0], 0),
])
def test_edge_cases(load, fn, heights, expected):
    assert getattr(load("ex08_trapping_rain_water"), fn)(heights) == expected


def test_random_all_rungs_agree(load):
    m = load("ex08_trapping_rain_water")
    rng = random.Random(19)
    for _ in range(500):
        h = [rng.randint(0, 6) for _ in range(rng.randint(0, 14))]
        answers = {getattr(m, fn)(h) for fn in FUNCS}
        assert len(answers) == 1, h
