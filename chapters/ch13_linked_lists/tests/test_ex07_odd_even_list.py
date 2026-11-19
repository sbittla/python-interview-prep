import importlib.util
import os
import random
from pathlib import Path

import pytest

# Shared helper loaded by path (tests run with --import-mode=importlib).
_HELPER = Path(__file__).resolve().parents[1] / os.environ.get("TARGET", "solutions") / "listnode.py"
_spec = importlib.util.spec_from_file_location("ch13_listnode_for_tests", _HELPER)
_ln = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ln)
build, nodes, to_list = _ln.build, _ln.nodes, _ln.to_list


def test_examples(load):
    m = load("ex07_odd_even_list")
    assert to_list(m.solve(build([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
    assert to_list(m.solve(build([2, 1, 3, 5, 6, 4, 7]))) == [2, 3, 6, 7, 1, 5, 4]


@pytest.mark.parametrize("vals", [[], [1], [1, 2], [1, 2, 3], [2, 4, 6, 8]])
def test_edge_cases(load, vals):
    m = load("ex07_odd_even_list")
    assert to_list(m.solve(build(vals)), limit=len(vals)) == vals[0::2] + vals[1::2]


def test_random_against_slicing(load):
    m = load("ex07_odd_even_list")
    rng = random.Random(1308)
    for _ in range(300):
        vals = [rng.randint(0, 9) for _ in range(rng.randint(0, 15))]
        head = build(vals)
        ns = nodes(head)
        out = m.solve(head)
        assert to_list(out, limit=len(vals)) == to_list(m.brute_force(build(vals)))
        assert nodes(out) == ns[0::2] + ns[1::2]
