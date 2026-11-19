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
    m = load("ex02_remove_value")
    assert to_list(m.solve(build([7, 1, 7, 7, 2, 7]), 7)) == [1, 2]
    assert to_list(m.solve(build([7, 7]), 7)) == []


@pytest.mark.parametrize("vals, x, expected", [
    ([], 1, []), ([1], 1, []), ([1], 2, [1]), ([1, 1, 2, 1, 1], 1, [2]), ([2, 1, 1], 1, [2]),
])
def test_edge_cases(load, vals, x, expected):
    m = load("ex02_remove_value")
    for fn in (m.solve, m.two_loops, m.brute_force):
        assert to_list(fn(build(vals), x)) == expected


def test_random_against_filter(load):
    m = load("ex02_remove_value")
    rng = random.Random(1303)
    for _ in range(500):
        vals = [rng.randint(0, 3) for _ in range(rng.randint(0, 12))]
        x = rng.randint(0, 3)
        head = build(vals)
        keep = [n for n in nodes(head) if n.val != x]
        out = m.solve(head, x)
        assert to_list(out, limit=len(vals)) == [v for v in vals if v != x]
        assert nodes(out) == keep                     # same node objects, same order
