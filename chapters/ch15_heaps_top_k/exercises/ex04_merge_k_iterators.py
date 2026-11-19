"""
Exercise 04 — Merge K Sorted Iterators Lazily                      [Tier: ★ Core]
Chapter 15 · Pattern: k-way merge with a heap of heads · Target time: 20 min

Problem
-------
Write a generator `merge_lazy(iterables, key=None)` that yields the items of k sorted
iterables in sorted order. It must be lazy: it pulls at most one item ahead from each
source, so it works on huge files or infinite generators. Equal keys come out in source
order (stable), and items themselves need not be comparable (e.g. dicts with a key).

(Ch 13 ex06 merges linked lists and Ch 6 ex04 merges in-memory lists; this version
handles arbitrary iterators, a key function, and infinite inputs.)

Examples
--------
>>> list(merge_lazy([[1, 4, 7], [2, 5], [], [3, 6, 9]]))
[1, 2, 3, 4, 5, 6, 7, 9]
>>> from itertools import count, islice
>>> list(islice(merge_lazy([count(0, 3), count(0, 5)]), 6))
[0, 0, 3, 5, 6, 9]

Constraints
-----------
- k sources, N items in total; each source is sorted by `key` (ascending).

Hints
-----
- Store the iterator objects in a list; the heap stores only the index.
- `heapq.heapreplace` pops and pushes in one sift when the source has another item.
- `next(it, sentinel)` avoids try/except around StopIteration.

Follow-ups
----------
- External sort: sort chunks that fit in memory, write them out, k-way merge the files.
- Merge descending sources: negate the key (numbers) or use `heapq.merge(..., reverse=True)`.
- Deduplicate while merging: remember the last yielded key.

Wrong-but-tempting
------------------
- Pushing `(item, it)` tuples: on equal items Python compares iterators -> TypeError.
- Calling `list(source)` first "to be safe": loses laziness and hangs on infinite input.
"""
from __future__ import annotations

import heapq
from itertools import chain, count, islice
from typing import Any, Callable, Iterable, Iterator

_DONE = object()


def brute_force(iterables: Iterable[Iterable[Any]], key: Callable | None = None) -> list[Any]:
    raise NotImplementedError("TODO")


def one_by_one(iterables: Iterable[Iterable[Any]], key: Callable | None = None) -> list[Any]:
    raise NotImplementedError("TODO")


def merge_lazy(iterables: Iterable[Iterable[Any]], key: Callable | None = None) -> Iterator[Any]:
    raise NotImplementedError("TODO")


def solve(iterables: Iterable[Iterable[Any]], key: Callable | None = None) -> Iterator[Any]:
    raise NotImplementedError("TODO")


def main() -> None:
    srcs = [[1, 4, 7], [2, 5], [], [3, 6, 9]]
    print("lists      :", list(solve(srcs)))
    print("all agree  :", list(solve(srcs)) == brute_force(srcs) == one_by_one(srcs)
          == list(heapq.merge(*srcs)))
    print("infinite   :", list(islice(solve([count(0, 3), count(0, 5), count(1, 7)]), 10)))

    pulled: list[str] = []

    def noisy(name: str, values: list[int]) -> Iterator[int]:
        for v in values:
            pulled.append(f"{name}{v}")
            yield v

    gen = solve([noisy("a", [1, 5, 9]), noisy("b", [2, 3, 10])])
    first_three = [next(gen) for _ in range(3)]
    print("lazy       :", first_three, "pulled so far:", pulled)

    logs = [[{"t": 1, "msg": "boot"}, {"t": 4, "msg": "ready"}],
            [{"t": 1, "msg": "db up"}, {"t": 2, "msg": "conn"}]]
    merged = list(solve(logs, key=lambda d: d["t"]))
    print("dicts+key  :", [(d["t"], d["msg"]) for d in merged])
    print("stable ties:", merged == brute_force(logs, key=lambda d: d["t"]))
    try:
        heapq.heappush(h := [], (1, {"a": 1}))
        heapq.heappush(h, (1, {"b": 2}))
    except TypeError as e:
        print("without index tie-break ->", type(e).__name__ + ":", e)
    print("empty      :", list(solve([])), list(solve([[], []])))


if __name__ == "__main__":
    main()
