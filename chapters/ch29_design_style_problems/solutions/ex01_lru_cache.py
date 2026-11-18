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

Approach ladder
---------------
1. Brute force — a list of (key, value) pairs ordered by recency; every get/put scans
   and moves an element: O(n) per operation.
2. Improved   — dict for values + a "last used" timestamp per key; eviction scans all
   timestamps for the minimum: O(1) get, O(n) evicting put.
3. Optimal    — dict key -> node, nodes in a doubly linked list ordered by recency.
   Moving a node to the tail and popping the head are O(1) pointer updates.
   We move up because every operation must be O(1), and only a linked list gives O(1)
   removal from the middle once you hold a pointer to the node.

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
        self.capacity = capacity
        self.items: list[tuple[Hashable, Any]] = []

    def get(self, key: Hashable) -> Any:
        for i, (k, v) in enumerate(self.items):
            if k == key:
                self.items.append(self.items.pop(i))
                return v
        return -1

    def put(self, key: Hashable, value: Any) -> None:
        for i, (k, _) in enumerate(self.items):
            if k == key:
                self.items.pop(i)
                break
        self.items.append((key, value))
        if len(self.items) > self.capacity:
            self.items.pop(0)

    def keys_lru_to_mru(self) -> list[Hashable]:
        return [k for k, _ in self.items]


class LRUCacheOrdered:
    """Production version: OrderedDict keeps insertion order and can move keys in O(1)."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.data: OrderedDict[Hashable, Any] = OrderedDict()

    def get(self, key: Hashable) -> Any:
        if key not in self.data:
            return -1
        self.data.move_to_end(key)          # mark as most recently used
        return self.data[key]

    def put(self, key: Hashable, value: Any) -> None:
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)   # evict the least recently used

    def keys_lru_to_mru(self) -> list[Hashable]:
        return list(self.data)


# provided
class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Hashable = None, value: Any = None) -> None:
        self.key = key
        self.value = value
        self.prev: _Node | None = None
        self.next: _Node | None = None


class LRUCache:
    """Interview version: dict[key] -> node; list order head(LRU) ... tail(MRU)."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.map: dict[Hashable, _Node] = {}
        self.head = _Node()                 # sentinel before the LRU node
        self.tail = _Node()                 # sentinel after the MRU node
        self.head.next = self.tail
        self.tail.prev = self.head

    # -- linked-list helpers (all O(1)) ---------------------------------------
    def _unlink(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append(self, node: _Node) -> None:
        """Insert just before the tail sentinel (= most recently used)."""
        last = self.tail.prev
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    # -- public API -----------------------------------------------------------
    def get(self, key: Hashable) -> Any:
        node = self.map.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._append(node)
        return node.value

    def put(self, key: Hashable, value: Any) -> None:
        node = self.map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._append(node)
            return
        node = _Node(key, value)
        self.map[key] = node
        self._append(node)
        if len(self.map) > self.capacity:
            lru = self.head.next
            self._unlink(lru)
            del self.map[lru.key]           # the node stores its key for exactly this

    def __len__(self) -> int:
        return len(self.map)

    def keys_lru_to_mru(self) -> list[Hashable]:
        out, node = [], self.head.next
        while node is not self.tail:
            out.append(node.key)
            node = node.next
        return out


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
