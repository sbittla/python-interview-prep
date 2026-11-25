import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest


def test_examples(load):
    m = load("ex05_executors")
    assert m.split_range(10, 3) == [(0, 4), (4, 7), (7, 10)]
    assert m.parallel_count(100, 4, ThreadPoolExecutor, 2) == 25
    assert m.fetch_all(["a", "bb"], len, 2) == {"a": 1, "bb": 2}


@pytest.mark.parametrize("lo, hi, expected", [(0, 2, 0), (2, 3, 1), (0, 10, 4), (10, 30, 6),
                                              (5, 5, 0), (97, 98, 1)])
def test_count_primes(load, lo, hi, expected):
    assert load("ex05_executors").count_primes(lo, hi) == expected


@pytest.mark.parametrize("n, parts", [(10, 3), (0, 2), (2, 4), (7, 7), (100, 1), (1001, 8)])
def test_split_range_partitions(load, n, parts):
    ranges = load("ex05_executors").split_range(n, parts)
    assert len(ranges) == parts
    assert ranges[0][0] == 0 and ranges[-1][1] == n
    assert all(a[1] == b[0] for a, b in zip(ranges, ranges[1:]))
    sizes = [hi - lo for lo, hi in ranges]
    assert max(sizes) - min(sizes) <= 1


def test_parallel_count_threads_matches_serial(load):
    m = load("ex05_executors")
    for n, parts in [(1, 3), (500, 7), (5000, 4)]:
        assert m.parallel_count(n, parts, ThreadPoolExecutor, 3) == m.count_primes(0, n)


def test_fetch_all_order_and_errors(load):
    m = load("ex05_executors")
    keys = ["bad-1", "zz", "a", "bad-2", "qqq"]
    out = m.fetch_all(keys, m.fake_fetch, 4)
    assert list(out) == keys
    assert out == {"bad-1": "error: ConnectionError", "zz": 2, "a": 1,
                   "bad-2": "error: ConnectionError", "qqq": 3}
    assert m.fetch_all([], len, 2) == {}


@pytest.mark.parametrize("workers", [1, 2, 5])
def test_peak_threads_equals_pool_size(load, workers):
    assert load("ex05_executors").peak_threads(workers, rounds=2) == workers


def test_process_pool_runs_as_script(load):
    # Spawned children must import the worker by module name, so run the file as __main__.
    m = load("ex05_executors")
    proc = subprocess.run([sys.executable, m.__file__], capture_output=True, text=True,
                          timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "process pool agrees: True" in proc.stdout
