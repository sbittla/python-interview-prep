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
nodes = _ln.nodes


def index_of(head, node):
    i = 0
    while head is not node:
        head, i = head.next, i + 1
    return i


def test_examples(load):
    m = load("ex04_cycle_start")
    assert m.solve(m.build_with_cycle([3, 2, 0, -4], 1)).val == 2
    assert m.solve(m.build_with_cycle([1, 2], -1)) is None
    assert m.cycle_length(m.build_with_cycle([3, 2, 0, -4], 1)) == 3


@pytest.mark.parametrize("vals, pos, entry, loop", [
    ([], -1, None, 0), ([1], -1, None, 0), ([1], 0, 0, 1), ([1, 2], 0, 0, 2),
    ([1, 2], 1, 1, 1), ([4, 4, 4], 1, 1, 2),
])
def test_edge_cases(load, vals, pos, entry, loop):
    m = load("ex04_cycle_start")
    head = m.build_with_cycle(vals, pos)
    node = m.solve(head)
    assert (None if node is None else index_of(head, node)) == entry
    assert m.cycle_length(head) == loop


def test_random_against_set_reference(load):
    m = load("ex04_cycle_start")
    rng = random.Random(1305)
    for _ in range(400):
        n = rng.randint(0, 40)
        vals = [rng.randint(0, 2) for _ in range(n)]       # many duplicate values
        pos = rng.randint(-1, n - 1) if n else -1
        head = m.build_with_cycle(vals, pos)
        node = m.solve(head)
        assert node is m.brute_force(head)
        if pos == -1:
            assert node is None and m.cycle_length(head) == 0
        else:
            assert index_of(head, node) == pos and m.cycle_length(head) == n - pos


def test_list_not_modified(load):
    m = load("ex04_cycle_start")
    head = m.build_with_cycle(list(range(8)))
    before = nodes(head)
    m.solve(head)
    assert nodes(head) == before
