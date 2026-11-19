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


def rotated(vals, k):
    if not vals:
        return []
    k %= len(vals)
    return vals[-k:] + vals[:-k] if k else list(vals)


def test_examples(load):
    m = load("ex09_rotate_list")
    assert to_list(m.solve(build([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
    assert to_list(m.solve(build([0, 1, 2]), 4)) == [2, 0, 1]


@pytest.mark.parametrize("vals, k", [([], 0), ([], 7), ([1], 99), ([1, 2], 0), ([1, 2, 3], 3),
                                     ([1, 2, 3], 2 * 10**9 + 1)])
def test_edge_cases(load, vals, k):
    out = load("ex09_rotate_list").solve(build(vals), k)
    assert to_list(out, limit=len(vals)) == rotated(vals, k)


def test_random_against_slicing(load):
    m = load("ex09_rotate_list")
    rng = random.Random(1310)
    for _ in range(400):
        vals = [rng.randint(0, 9) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 30)
        head = build(vals)
        ns = nodes(head)
        out = m.solve(head, k)
        expect = rotated(vals, k)
        assert to_list(out, limit=len(vals)) == expect
        assert sorted(map(id, nodes(out))) == sorted(map(id, ns))        # nodes reused
        assert to_list(m.improved(build(vals), k), limit=len(vals)) == expect
