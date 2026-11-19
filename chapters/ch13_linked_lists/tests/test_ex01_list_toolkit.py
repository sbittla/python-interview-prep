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
    m = load("ex01_list_toolkit")
    assert to_list(m.insert_at(build([1, 3]), 1, 2)) == [1, 2, 3]
    assert to_list(m.delete_at(build([1, 2, 3]), 0)) == [2, 3]
    assert to_list(m.reverse(build([1, 2, 3]))) == [3, 2, 1]
    assert m.length(build([4, 5])) == 2 and m.length(None) == 0


@pytest.mark.parametrize("vals, i", [([], 1), ([], -1), ([1, 2], 3), ([1], -1)])
def test_insert_out_of_range(load, vals, i):
    with pytest.raises(IndexError):
        load("ex01_list_toolkit").insert_at(build(vals), i, 0)


@pytest.mark.parametrize("vals, i", [([], 0), ([1], 1), ([1, 2], -1), ([1, 2], 5)])
def test_delete_out_of_range(load, vals, i):
    with pytest.raises(IndexError):
        load("ex01_list_toolkit").delete_at(build(vals), i)


def test_random_against_python_list(load):
    m = load("ex01_list_toolkit")
    rng = random.Random(1301)
    for _ in range(300):
        ref = [rng.randint(-9, 9) for _ in range(rng.randint(0, 8))]
        head = build(ref)
        for _ in range(6):
            if ref and rng.random() < 0.5:
                i = rng.randrange(len(ref))
                ref.pop(i)
                head = m.delete_at(head, i)
            else:
                i, v = rng.randint(0, len(ref)), rng.randint(-9, 9)
                ref.insert(i, v)
                head = m.insert_at(head, i, v)
            assert to_list(head) == ref and m.length(head) == len(ref)
        assert to_list(m.brute_force_insert(build(ref), 0, 7)) == [7] + ref


def test_reverse_keeps_nodes_and_tail_none(load):
    m = load("ex01_list_toolkit")
    rng = random.Random(1302)
    for fn in (m.reverse, m.reverse_recursive):
        for n in range(0, 12):
            vals = [rng.randint(0, 5) for _ in range(n)]
            head = build(vals)
            before = nodes(head)
            new = fn(head)
            assert to_list(new, limit=n) == vals[::-1]      # tail is None: no cycle
            assert nodes(new) == before[::-1]


def test_long_list_iterative(load):
    m = load("ex01_list_toolkit")
    assert to_list(m.reverse(build(range(100_000))))[:3] == [99_999, 99_998, 99_997]
