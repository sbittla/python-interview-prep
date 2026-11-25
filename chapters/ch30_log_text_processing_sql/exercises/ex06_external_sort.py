"""
Exercise 06 — External Sort: Sort a File Bigger Than Memory   [Tier: ◆ Extended]
Chapter 30 · Pattern: chunked sorted runs + k-way heap merge · Target time: 30 min

Problem
-------
A text file holds one integer per line, too many to load at once. You may hold at most
`chunk` integers in memory. Write

1. `read_chunks(lines, chunk)` -> generator of lists of at most `chunk` ints;
2. `external_sort(src, dst, chunk, tmpdir)` -> number of sorted runs created; writes the
   sorted integers to `dst`, one per line. Runs go to files inside `tmpdir`;
3. `count_by_key_partitioned(lines, parts, tmpdir)` -> {key: count} for a file of string
   keys, computed by hash-partitioning keys into `parts` files and counting one
   partition at a time (each partition's distinct keys must fit in memory).

Examples
--------
>>> list(read_chunks(["5", "3", "9", "1", "7"], 2))
[[5, 3], [9, 1], [7]]

Constraints
-----------
- N integers, chunk size M, so k = ceil(N / M) runs. Memory O(M + k).

Hints
-----
- `itertools.islice(it, chunk)` takes the next chunk without reading further.
- `heapq.merge(*iterables)` is lazy: it holds one item per input (→ §6.8).
- Write runs as text, read them back with a generator `(int(line) for line in f)`.

Edge cases
----------
- Empty file (0 runs, empty output), N < M (1 run), N an exact multiple of M,
  duplicates, negative numbers, trailing blank line.

Follow-ups
----------
- Too many runs to open at once (OS file-handle limit): merge in groups of F
  ("fan-in"), giving ceil(log_F k) merge passes.
- Distributed version: this is the sort phase of MapReduce; partition by key range so
  each reducer's output is globally ordered.
- Dedupe or count keys bigger than memory: hash-partition (3), then process each
  partition independently — no merge needed.
"""
from __future__ import annotations

import heapq
import itertools
import random
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator
from zlib import crc32


def read_chunks(lines: Iterable[str], chunk: int) -> Iterator[list[int]]:
    raise NotImplementedError("TODO")


def brute_force_sort(src: Path, dst: Path) -> None:
    raise NotImplementedError("TODO")


def _numbers(path: Path) -> Iterator[int]:
    raise NotImplementedError("TODO")


def external_sort(src: Path, dst: Path, chunk: int, tmpdir: Path) -> int:
    raise NotImplementedError("TODO")


def count_by_key_partitioned(lines: Iterable[str], parts: int, tmpdir: Path) -> dict[str, int]:
    raise NotImplementedError("TODO")


def main() -> None:
    rng = random.Random(30)
    nums = [rng.randint(-1000, 1000) for _ in range(10_007)]
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        src, dst, ref = tmp / "in.txt", tmp / "out.txt", tmp / "ref.txt"
        src.write_text("".join(f"{n}\n" for n in nums))
        brute_force_sort(src, ref)
        for chunk in (1_000, 2_500, 20_000):
            runs = external_sort(src, dst, chunk, tmp)
            print(f"N=10007 chunk={chunk:>6}: runs={runs:>2}  "
                  f"same as in-memory sort: {dst.read_text() == ref.read_text()}")
        empty = tmp / "empty.txt"
        empty.write_text("")
        print("empty file -> runs:", external_sort(empty, dst, 10, tmp),
              "| output:", repr(dst.read_text()))
        words = [rng.choice(["GET /a", "GET /b", "POST /c", "GET /d"]) for _ in range(1000)]
        counts = count_by_key_partitioned(words, 3, tmp)
        print("partitioned counts:", counts)
        print("same as Counter:", counts == dict(sorted(Counter(words).items())))


if __name__ == "__main__":
    main()
