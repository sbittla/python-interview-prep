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
    m = load("ex03_palindrome_list")
    assert m.middle(build([1, 2, 3, 4, 5])).val == 3
    assert m.middle(build([1, 2, 3, 4])).val == 3
    assert m.middle(None) is None
    assert m.is_palindrome(build([1, 2, 2, 1])) is True
    assert m.is_palindrome(build([1, 2, 3])) is False


@pytest.mark.parametrize("vals, expected", [
    ([], True), ([5], True), ([1, 1], True), ([1, 2], False), ([1, 2, 1], True), ([1, 1, 2], False),
])
def test_edge_cases(load, vals, expected):
    assert load("ex03_palindrome_list").is_palindrome(build(vals)) is expected


def test_random_against_reference_and_restored(load):
    m = load("ex03_palindrome_list")
    rng = random.Random(1304)
    for _ in range(500):
        half = [rng.randint(0, 2) for _ in range(rng.randint(0, 6))]
        vals = rng.choice([half + half[::-1], half + [9] + half[::-1],
                           [rng.randint(0, 2) for _ in range(rng.randint(0, 9))]])
        head = build(vals)
        before = nodes(head)
        assert m.is_palindrome(head) == (vals == vals[::-1]) == m.brute_force(build(vals))
        assert to_list(head, limit=len(vals)) == vals and nodes(head) == before
        if vals:
            assert m.middle(head) is before[len(vals) // 2]
