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


def swapped(xs):
    out = list(xs)
    for i in range(0, len(out) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return out


def test_examples(load):
    m = load("ex10_swap_pairs")
    assert to_list(m.solve(build([1, 2, 3, 4]))) == [2, 1, 4, 3]
    assert to_list(m.solve(build([1, 2, 3]))) == [2, 1, 3]


@pytest.mark.parametrize("vals", [[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4, 5, 6]])
def test_edge_cases(load, vals):
    m = load("ex10_swap_pairs")
    for fn in (m.solve, m.recursive):
        assert to_list(fn(build(vals)), limit=len(vals)) == swapped(vals)


def test_random_relinks_nodes(load):
    m = load("ex10_swap_pairs")
    rng = random.Random(1311)
    for _ in range(300):
        vals = [rng.randint(0, 9) for _ in range(rng.randint(0, 15))]
        head = build(vals)
        ns = nodes(head)
        out = m.solve(head)
        assert to_list(out, limit=len(vals)) == swapped(vals)
        assert nodes(out) == swapped(ns)                    # node identity, not values


def test_long_list(load):
    m = load("ex10_swap_pairs")
    assert to_list(m.solve(build(range(100_000))))[:4] == [1, 0, 3, 2]
