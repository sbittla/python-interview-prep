import importlib.util
import os
import random
from pathlib import Path

# Shared helper loaded by path (tests run with --import-mode=importlib).
_HELPER = Path(__file__).resolve().parents[1] / os.environ.get("TARGET", "solutions") / "listnode.py"
_spec = importlib.util.spec_from_file_location("ch13_listnode_for_tests", _HELPER)
_ln = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ln)
ListNode, build, nodes, to_list = _ln.ListNode, _ln.build, _ln.nodes, _ln.to_list


def test_examples(load):
    m = load("ex06_merge_k_lists")
    heads = [build([1, 4, 5]), build([1, 3, 4]), build([2, 6])]
    assert to_list(m.solve(heads)) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert m.solve([]) is None
    assert m.solve([None, None]) is None


def test_stable_and_reuses_nodes(load):
    m = load("ex06_merge_k_lists")
    for fn in (m.solve, m.one_by_one, m.divide_and_conquer):
        heads = [ListNode(1, ListNode(3)), ListNode(1), ListNode(3)]
        a0, a1 = nodes(heads[0])
        b0, c0 = heads[1], heads[2]
        assert nodes(fn(heads)) == [a0, b0, a1, c0]


def test_random_against_sorted(load):
    m = load("ex06_merge_k_lists")
    rng = random.Random(1307)
    for _ in range(300):
        lists = [sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 6)))
                 for _ in range(rng.randint(0, 6))]
        expected = sorted(v for x in lists for v in x)
        for fn in (m.solve, m.one_by_one, m.divide_and_conquer, m.brute_force):
            out = fn([build(x) for x in lists])
            assert to_list(out, limit=len(expected)) == expected


def test_merge_two_with_empty(load):
    m = load("ex06_merge_k_lists")
    assert to_list(m.merge_two(build([1, 2]), None)) == [1, 2]
    assert to_list(m.merge_two(None, build([3]))) == [3]
    assert m.merge_two(None, None) is None
