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
    m = load("ex08_partition_list")
    assert to_list(m.solve(build([1, 4, 3, 2, 5, 2]), 3)) == [1, 2, 2, 4, 3, 5]


@pytest.mark.parametrize("vals, x", [([], 0), ([1], 0), ([1], 5), ([3, 1], 2), ([5, 5, 5], 5)])
def test_edge_cases(load, vals, x):
    m = load("ex08_partition_list")
    expected = [v for v in vals if v < x] + [v for v in vals if v >= x]
    assert to_list(m.solve(build(vals), x), limit=len(vals)) == expected


def test_buggy_version_makes_cycle(load):
    m = load("ex08_partition_list")
    with pytest.raises(ValueError):
        to_list(m.forgot_terminator(build([3, 1]), 2), limit=100)


def test_random_stable_partition(load):
    m = load("ex08_partition_list")
    rng = random.Random(1309)
    for _ in range(400):
        vals = [rng.randint(-4, 4) for _ in range(rng.randint(0, 12))]
        x = rng.randint(-5, 5)
        head = build(vals)
        ns = nodes(head)
        out = m.solve(head, x)
        assert to_list(m.brute_force(build(vals), x)) == to_list(out, limit=len(vals))
        assert nodes(out) == [n for n in ns if n.val < x] + [n for n in ns if n.val >= x]
