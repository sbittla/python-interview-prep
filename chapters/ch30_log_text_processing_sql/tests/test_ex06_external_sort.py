import random
from collections import Counter

import pytest


def test_read_chunks(load):
    m = load("ex06_external_sort")
    assert list(m.read_chunks(["5", "3", "9", "1", "7"], 2)) == [[5, 3], [9, 1], [7]]
    assert list(m.read_chunks([], 3)) == []
    assert list(m.read_chunks(["1\n", "\n", "2\n"], 5)) == [[1, 2]]


def test_read_chunks_is_lazy(load):
    m = load("ex06_external_sort")
    pulled = []

    def src():
        for i in range(10):
            pulled.append(i)
            yield str(i)

    gen = m.read_chunks(src(), 3)
    assert next(gen) == [0, 1, 2] and len(pulled) <= 4


@pytest.mark.parametrize("n, chunk, runs", [(0, 4, 0), (3, 4, 1), (8, 4, 2), (9, 4, 3), (50, 7, 8)])
def test_external_sort(load, tmp_path, n, chunk, runs):
    m = load("ex06_external_sort")
    rng = random.Random(n)
    nums = [rng.randint(-50, 50) for _ in range(n)]
    src, dst = tmp_path / "in.txt", tmp_path / "out.txt"
    src.write_text("".join(f"{x}\n" for x in nums))
    work = tmp_path / "work"
    work.mkdir()
    assert m.external_sort(src, dst, chunk, work) == runs
    assert [int(x) for x in dst.read_text().split()] == sorted(nums)


def test_runs_respect_chunk_size(load, tmp_path):
    m = load("ex06_external_sort")
    src, dst = tmp_path / "in.txt", tmp_path / "out.txt"
    src.write_text("".join(f"{x}\n" for x in range(23, 0, -1)))
    work = tmp_path / "work"
    work.mkdir()
    assert m.external_sort(src, dst, 5, work) == 5
    sizes = sorted(len(p.read_text().split()) for p in work.iterdir())
    assert sizes == [3, 5, 5, 5, 5]


def test_partitioned_counts(load, tmp_path):
    m = load("ex06_external_sort")
    rng = random.Random(6)
    keys = [rng.choice(["a", "b", "c d", "é"]) for _ in range(300)] + ["", "  "]
    for parts in (1, 2, 5):
        d = tmp_path / str(parts)
        d.mkdir()
        got = m.count_by_key_partitioned(keys, parts, d)
        assert got == dict(sorted(Counter(k.strip() for k in keys if k.strip()).items()))
        assert len(list(d.iterdir())) == parts
