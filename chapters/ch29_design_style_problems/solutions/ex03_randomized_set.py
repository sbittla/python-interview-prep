"""
Exercise 03 — Insert / Delete / GetRandom in O(1)  [Tier: ★ Core]
Chapter 29 · Pattern: array + index map (swap-with-last) · Target time: 20 min

Problem
-------
Design a set of integers supporting, each in O(1) average time:

    s = RandomizedSet(seed=0)
    s.insert(x)     -> True if x was absent (and is now added), else False
    s.remove(x)     -> True if x was present (and is now removed), else False
    s.get_random()  -> a uniformly random element (the set is non-empty)

The random source is injected (`seed` or an `random.Random` instance) so that runs are
reproducible. Follow-up class `RandomizedMultiset` allows duplicates; `get_random` then
returns each *copy* with equal probability.

Examples
--------
>>> s = RandomizedSet(seed=1)
>>> s.insert(10), s.insert(10), s.insert(20), s.remove(10), s.remove(99)
(True, False, True, True, False)
>>> s.get_random()
20

Constraints
-----------
- Up to 2 * 10**5 operations; get_random is only called on a non-empty set.

Approach ladder
---------------
1. Brute force — a Python `set`; `random.choice(list(s))` is O(n) per get_random.
2. Improved   — a list only: O(1) get_random, but O(n) membership test and removal.
3. Optimal    — list `items` + dict `pos[value] = index`. To remove x, copy the last
   element into x's slot, update its index, then pop the tail: O(1). The list keeps
   elements contiguous so `rng.randrange(len(items))` is a uniform O(1) pick.

Hints
-----
- Removal order: read idx = pos[x]; last = items[-1]; items[idx] = last; pos[last] = idx;
  items.pop(); del pos[x]. Check that this also works when x *is* the last element.
- For the multiset, map value -> set of indices.

Follow-ups
----------
- Weighted random pick (prefix sums + binary search, or the alias method).
- Thread safety; iterating while mutating.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict


class RandomizedSetBrute:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)
        self.items: set[int] = set()

    def insert(self, x: int) -> bool:
        if x in self.items:
            return False
        self.items.add(x)
        return True

    def remove(self, x: int) -> bool:
        if x not in self.items:
            return False
        self.items.remove(x)
        return True

    def get_random(self) -> int:
        return self.rng.choice(sorted(self.items))      # O(n log n): sorted for determinism


class RandomizedSet:
    def __init__(self, seed: int | random.Random = 0) -> None:
        self.rng = seed if isinstance(seed, random.Random) else random.Random(seed)
        self.items: list[int] = []
        self.pos: dict[int, int] = {}

    def insert(self, x: int) -> bool:
        if x in self.pos:
            return False
        self.pos[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x: int) -> bool:
        idx = self.pos.get(x)
        if idx is None:
            return False
        last = self.items[-1]
        self.items[idx] = last        # move last element into the hole
        self.pos[last] = idx
        self.items.pop()
        del self.pos[x]               # after updating pos[last] (x may equal last)
        return True

    def get_random(self) -> int:
        if not self.items:
            raise IndexError("get_random from empty set")
        return self.items[self.rng.randrange(len(self.items))]

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, x: int) -> bool:
        return x in self.pos


class RandomizedMultiset:
    """Duplicates allowed: value -> set of indices into `items`."""

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)
        self.items: list[int] = []
        self.idx: defaultdict[int, set[int]] = defaultdict(set)

    def insert(self, x: int) -> bool:
        """Return True if x was not present before this insert."""
        fresh = not self.idx[x]
        self.idx[x].add(len(self.items))
        self.items.append(x)
        return fresh

    def remove(self, x: int) -> bool:
        if not self.idx.get(x):
            return False
        i = self.idx[x].pop()
        last_i = len(self.items) - 1
        last = self.items[last_i]
        self.items[i] = last
        self.idx[last].add(i)
        self.idx[last].discard(last_i)
        self.items.pop()
        if not self.idx[x]:
            del self.idx[x]
        return True

    def get_random(self) -> int:
        return self.items[self.rng.randrange(len(self.items))]


def main() -> None:
    s = RandomizedSet(seed=1)
    print("insert 10, 10, 20:", s.insert(10), s.insert(10), s.insert(20))
    print("remove 10, 99:   ", s.remove(10), s.remove(99))
    print("only element left -> get_random:", s.get_random())

    s = RandomizedSet(seed=42)
    for v in range(5):
        s.insert(v)
    s.remove(2)                       # middle element
    s.remove(4)                       # current last element
    print("after removing 2 and 4: items =", s.items, "pos =", dict(sorted(s.pos.items())))
    counts = Counter(s.get_random() for _ in range(30_000))
    print("30k draws (should be ~10k each):", dict(sorted(counts.items())))
    print("roughly uniform:", all(9_000 < c < 11_000 for c in counts.values()))

    m = RandomizedMultiset(seed=7)
    for v in [1, 1, 1, 2]:
        m.insert(v)
    counts = Counter(m.get_random() for _ in range(40_000))
    print("multiset [1,1,1,2] draws:", dict(sorted(counts.items())), "(expect ~3:1)")
    print("remove 1 ->", m.remove(1), "sorted items =", sorted(m.items))

    try:
        RandomizedSet().get_random()
    except IndexError as exc:
        print("empty ->", exc)


if __name__ == "__main__":
    main()
