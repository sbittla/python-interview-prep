"""
Exercise 10 — Choosing the Right Built-in (and Proving It)     [Tier: ◆ Extended]
Chapter 06 · Pattern: complexity-driven data-structure choice · Target time: 20 min

Problem
-------
1. `recommend(need)` — map an access-pattern description to the best built-in
   tool. Supported needs (exact strings):
     "membership"        -> "set"
     "fifo queue"        -> "collections.deque"
     "count items"       -> "collections.Counter"
     "group by key"      -> "collections.defaultdict"
     "repeated min"      -> "heapq"
     "sorted inserts"    -> "bisect.insort"
     "index access"      -> "list"
     "lru order"         -> "collections.OrderedDict"
   Unknown needs raise ValueError.
2. `race(n)` — run three timing races at size n and return a dict of booleans:
     "set beats list for membership", "deque beats list for popleft",
     "bisect beats linear scan for rank".
   Print only these booleans, never raw timings.

Examples
--------
>>> recommend("fifo queue")
'collections.deque'

Constraints
-----------
- `race(10_000)` finishes in a fraction of a second.

Hints
-----
- Use the best of a few repeats to reduce noise.
- Pick sizes where the asymptotic gap is huge (O(n) vs O(1) at n = 10,000),
  so the boolean is stable on any machine.

Follow-ups
----------
- When is a list still the right answer for membership? (Tiny n, one lookup:
  building the set costs O(n) itself.)
- Which of these change under PyPy? (Constant factors, not the big-O.)
"""
from __future__ import annotations

import time
from bisect import bisect_left
from collections import deque
from typing import Callable

TABLE = {
    "membership": "set",
    "fifo queue": "collections.deque",
    "count items": "collections.Counter",
    "group by key": "collections.defaultdict",
    "repeated min": "heapq",
    "sorted inserts": "bisect.insort",
    "index access": "list",
    "lru order": "collections.OrderedDict",
}


def recommend(need: str) -> str:
    raise NotImplementedError("TODO")


def _best_time(fn: Callable[[], object], repeats: int = 3) -> float:
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def race(n: int) -> dict[str, bool]:
    raise NotImplementedError("TODO")


def main() -> None:
    for need in TABLE:
        print(f"{need:15} -> {recommend(need)}")
    try:
        recommend("teleport")
    except ValueError as exc:
        print("ValueError:", exc)
    for claim, ok in race(10_000).items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
