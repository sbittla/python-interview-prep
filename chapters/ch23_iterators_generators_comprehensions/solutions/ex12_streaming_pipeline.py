"""
Exercise 12 — A Composable Streaming Pipeline                  [Tier: ◆ Extended]
Chapter 23 · Pattern: lazy method-chained stages · Target time: 35 min

Problem
-------
Build a small ``Stream`` class that wraps any iterable and offers lazy, chainable stages:

- ``map(fn)``, ``filter(pred)``, ``take(n)``, ``batch(n)`` (lists of up to n), ``window(n)``
  (overlapping tuples) — each returns a *new* ``Stream`` and does no work yet;
- terminal operations ``to_list()``, ``count()``, ``group_count(key)`` (dict sorted by key) that
  actually pull data.

Each ``Stream`` records how many items its stage has emitted in ``self.emitted`` so you can prove
laziness. Then use it on ``data/app.log`` to compute, per minute, ``(total, errors)`` and the first
two slow requests (>= 500 ms), reading no more lines than necessary.

Examples
--------
>>> Stream(range(10)).map(lambda x: x * x).filter(lambda x: x % 2).take(3).to_list()
[1, 9, 25]

Constraints
-----------
- No stage may call ``list()`` on its upstream (``batch``/``window`` buffer at most n items).

Hints
-----
- Store a generator in ``self._source``; each stage method builds a new generator over it.
- Increment ``emitted`` inside a wrapper generator: ``for x in gen: self.emitted += 1; yield x``.
- ``take`` = ``itertools.islice``; ``batch`` and ``window`` are Exercises 05 and 06.

Approach ladder
---------------
1. Lists between steps — simple, but O(N) memory per step and reads the whole file even when you
   need two records.
2. Nested generator expressions — lazy but unreadable beyond three stages.
3. A fluent ``Stream`` object — lazy, readable left-to-right, every stage instrumentable.

Follow-ups
----------
- How would you add a ``tee`` (fan-out to two consumers)? What does ``itertools.tee`` buffer?
- How would this become parallel? (``concurrent.futures`` map per batch — Chapter 28)
"""
from __future__ import annotations

from collections import Counter, deque
from itertools import islice
from pathlib import Path
from typing import Callable, Iterable, Iterator

LOG = Path(__file__).resolve().parent.parent / "data" / "app.log"


class Stream:
    def __init__(self, source: Iterable) -> None:
        self._source = iter(source)
        self.emitted = 0

    def __iter__(self) -> Iterator:
        for item in self._source:
            self.emitted += 1
            yield item

    def map(self, fn: Callable) -> "Stream":
        return Stream(fn(x) for x in self)

    def filter(self, pred: Callable) -> "Stream":
        return Stream(x for x in self if pred(x))

    def take(self, n: int) -> "Stream":
        return Stream(islice(self, n))

    def batch(self, n: int) -> "Stream":
        def gen():
            it = iter(self)
            while chunk := list(islice(it, n)):
                yield chunk
        return Stream(gen())

    def window(self, n: int) -> "Stream":
        def gen():
            buf: deque = deque(maxlen=n)
            for x in self:
                buf.append(x)
                if len(buf) == n:
                    yield tuple(buf)
        return Stream(gen())

    def to_list(self) -> list:
        return list(self)

    def count(self) -> int:
        return sum(1 for _ in self)

    def group_count(self, key: Callable) -> dict:
        return dict(sorted(Counter(key(x) for x in self).items()))


def parse(line: str) -> dict | None:
    parts = line.split()
    if len(parts) != 6 or not parts[5].isdigit():
        return None
    ts, level, method, path, status, ms = parts
    return {"minute": ts[11:16], "level": level, "path": path, "ms": int(ms)}


def log_records(path: Path = LOG) -> Stream:
    def lines():
        with open(path, encoding="utf-8") as f:
            yield from f
    return (Stream(lines())
            .filter(lambda s: s.strip() and not s.startswith("#"))
            .map(parse)
            .filter(lambda r: r is not None))


def per_minute(path: Path = LOG) -> dict[str, tuple[int, int]]:
    totals: dict[str, list[int]] = {}
    for r in log_records(path):
        t = totals.setdefault(r["minute"], [0, 0])
        t[0] += 1
        t[1] += r["level"] == "ERROR"
    return {m: (t[0], t[1]) for m, t in sorted(totals.items())}


def main() -> None:
    src = Stream(range(10))
    squares = src.map(lambda x: x * x)
    odd = squares.filter(lambda x: x % 2)
    first3 = odd.take(3)
    print("nothing pulled yet:", src.emitted, squares.emitted, odd.emitted)
    print("result:", first3.to_list())
    print("pulled from source:", src.emitted, "| squares:", squares.emitted,
          "| odd:", odd.emitted)

    print("batches:", Stream("abcdefg").batch(3).to_list())
    print("windows:", Stream([1, 2, 3, 4]).window(3).to_list())
    print("count:", Stream(range(100)).filter(lambda x: x % 7 == 0).count())

    print("per minute (total, errors):", per_minute())
    print("levels:", log_records().group_count(lambda r: r["level"]))

    # Laziness on a real file: stop after the first two slow requests.
    raw = Stream(open(LOG, encoding="utf-8"))
    recs = raw.map(parse).filter(lambda r: r is not None)
    slow2 = recs.filter(lambda r: r["ms"] >= 500).take(2).to_list()
    raw._source.close()
    print("first two slow:", [(r["minute"], r["path"], r["ms"]) for r in slow2])
    print("lines read to find them:", raw.emitted, "of 26")


if __name__ == "__main__":
    main()
