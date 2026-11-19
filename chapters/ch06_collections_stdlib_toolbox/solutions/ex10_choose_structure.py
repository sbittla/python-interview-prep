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

Approach ladder
---------------
1. Guess — "a list works for everything". It does, slowly: `x in list` is O(n),
   `list.pop(0)` is O(n), finding a rank by scanning is O(n).
2. Reason — compare per-operation costs from the complexity table (§6.14).
3. Prove — time the two candidates on the same work with `time.perf_counter`
   and report only the comparison (deterministic output, honest evidence).

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
    try:
        return TABLE[need]
    except KeyError:
        raise ValueError(f"unknown need: {need!r}") from None


def _best_time(fn: Callable[[], object], repeats: int = 3) -> float:
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def race(n: int) -> dict[str, bool]:
    data = list(range(n))
    as_set = set(data)
    probes = list(range(0, 2 * n, max(1, 2 * n // 500)))     # ~500 lookups, half miss

    t_list = _best_time(lambda: [p in data for p in probes])
    t_set = _best_time(lambda: [p in as_set for p in probes])

    def drain_list() -> None:
        q = list(data)
        while q:
            q.pop(0)                                        # O(n) shift each time

    def drain_deque() -> None:
        q = deque(data)
        while q:
            q.popleft()                                     # O(1)

    t_pop_list = _best_time(drain_list, repeats=1)
    t_pop_deque = _best_time(drain_deque, repeats=1)

    t_scan = _best_time(lambda: [sum(1 for x in data if x < p) for p in probes[:50]])
    t_bisect = _best_time(lambda: [bisect_left(data, p) for p in probes[:50]])

    return {
        "set beats list for membership": t_set < t_list,
        "deque beats list for popleft": t_pop_deque < t_pop_list,
        "bisect beats linear scan for rank": t_bisect < t_scan,
    }


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
