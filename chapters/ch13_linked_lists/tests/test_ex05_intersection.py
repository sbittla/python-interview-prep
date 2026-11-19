import importlib.util
import os
import random
from pathlib import Path

# Shared helper loaded by path (tests run with --import-mode=importlib).
_HELPER = Path(__file__).resolve().parents[1] / os.environ.get("TARGET", "solutions") / "listnode.py"
_spec = importlib.util.spec_from_file_location("ch13_listnode_for_tests", _HELPER)
_ln = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ln)
build, nodes = _ln.build, _ln.nodes


def test_examples(load):
    m = load("ex05_intersection")
    a, b = m.build_y([4, 1], [5, 6, 1], [8, 4, 5])
    assert m.solve(a, b).val == 8
    assert m.solve(build([1, 2]), build([1, 2])) is None   # equal values, distinct nodes


def test_edge_cases(load):
    m = load("ex05_intersection")
    assert m.solve(None, None) is None
    assert m.solve(build([1]), None) is None
    a, b = m.build_y([], [], [3, 4])
    assert m.solve(a, b) is a                                # same list
    a, b = m.build_y([], [1, 2, 3], [9])
    assert m.solve(a, b) is a


def test_random_all_rungs(load):
    m = load("ex05_intersection")
    rng = random.Random(1306)
    for _ in range(400):
        pa = [rng.randint(0, 3) for _ in range(rng.randint(0, 7))]
        pb = [rng.randint(0, 3) for _ in range(rng.randint(0, 7))]
        sh = [rng.randint(0, 3) for _ in range(rng.randint(0, 5))]
        a, b = m.build_y(pa, pb, sh)
        expected = nodes(a)[len(pa)] if sh else None
        assert m.solve(a, b) is expected
        assert m.with_set(a, b) is expected
        assert m.brute_force(a, b) is expected
        assert len(nodes(a)) == len(pa) + len(sh)              # lists untouched
