"""
Exercise 01 — LRU Cache (two implementations)       [Tier: ★ Core]
Chapter 29 · Pattern: hash map + doubly linked list · Target time: 25 min

Problem
-------
Design a fixed-capacity cache that evicts the *least recently used* entry when it is
full. Both reading a key (`get`) and writing a key (`put`) count as a "use".

    cache = LRUCache(capacity)
    cache.get(key)        -> value, or -1 if the key is absent
    cache.put(key, value) -> None; inserts or updates, evicting the LRU key if over capacity

Implement it twice:
1. `LRUCacheOrdered`  — on top of `collections.OrderedDict` (what you would ship).
2. `LRUCache`         — a hash map plus a hand-written doubly linked list with sentinel
                        nodes (what many interviewers ask for, to see the mechanics).

Both classes also expose `keys_lru_to_mru()` so tests can inspect the recency order.

Examples
--------
>>> c = LRUCache(2)
>>> c.put(1, "a"); c.put(2, "b"); c.get(1)
'a'
>>> c.put(3, "c")      # evicts key 2 (least recently used)
>>> c.get(2)
-1

Constraints
-----------
- 1 <= capacity <= 10**5; get and put must each be O(1) average time.
- Keys are hashable; values are arbitrary.


Hints
-----
- Sentinel `head` and `tail` nodes remove every "is the list empty?" special case.
- Write two private helpers first: `_unlink(node)` and `_append(node)`.
- With OrderedDict: `move_to_end(key)` and `popitem(last=False)` are all you need.

Follow-ups
----------
- Make it thread-safe (one `threading.Lock` around each public method).
- Add a per-entry TTL (store expiry time in the node; treat expired as absent).
- What does `functools.lru_cache` use internally? (A dict + circular doubly linked list.)
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Hashable


class LRUCacheBrute:
    """Rung 1: list ordered from LRU (index 0) to MRU (index -1). O(n) per operation."""

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    def get(self, key: Hashable) -> Any:
        raise NotImplementedError("TODO")

    def put(self, key: Hashable, value: Any) -> None:
        raise NotImplementedError("TODO")

    def keys_lru_to_mru(self) -> list[Hashable]:
        raise NotImplementedError("TODO")


class LRUCacheOrdered:
    """Production version: OrderedDict keeps insertion order and can move keys in O(1)."""

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    def get(self, key: Hashable) -> Any:
        raise NotImplementedError("TODO")

    def put(self, key: Hashable, value: Any) -> None:
        raise NotImplementedError("TODO")

    def keys_lru_to_mru(self) -> list[Hashable]:
        raise NotImplementedError("TODO")


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Hashable = None, value: Any = None) -> None:
        raise NotImplementedError("TODO")


class LRUCache:
    """Interview version: dict[key] -> node; list order head(LRU) ... tail(MRU)."""

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("TODO")

    # -- linked-list helpers (all O(1)) ---------------------------------------
    def _unlink(self, node: _Node) -> None:
        raise NotImplementedError("TODO")

    def _append(self, node: _Node) -> None:
        """Insert just before the tail sentinel (= most recently used)."""
        raise NotImplementedError("TODO")

    # -- public API -----------------------------------------------------------
    def get(self, key: Hashable) -> Any:
        raise NotImplementedError("TODO")

    def put(self, key: Hashable, value: Any) -> None:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def keys_lru_to_mru(self) -> list[Hashable]:
        raise NotImplementedError("TODO")


def main() -> None:
    script = [("put", 1, "a"), ("put", 2, "b"), ("get", 1), ("put", 3, "c"),
              ("get", 2), ("put", 1, "A"), ("put", 4, "d"), ("get", 3), ("get", 1), ("get", 4)]
    for cls in (LRUCacheBrute, LRUCacheOrdered, LRUCache):
        cache = cls(2)
        results = []
        for op, *args in script:
            r = getattr(cache, op)(*args)
            if op == "get":
                results.append(r)
        print(f"{cls.__name__:<16} gets={results} order={cache.keys_lru_to_mru()}")

    # Edge cases
    one = LRUCache(1)
    one.put("x", 1)
    one.put("y", 2)
    print("capacity 1 keeps only last key:", one.keys_lru_to_mru(), "get(x) =", one.get("x"))
    upd = LRUCache(2)
    upd.put("k", 1)
    upd.put("k", 2)
    print("updating a key does not grow size:", len(upd), "value =", upd.get("k"))
    try:
        LRUCache(0)
    except ValueError as exc:
        print("capacity 0 ->", exc)


if __name__ == "__main__":
    main()
