"""
Exercise 09 — Build a Tiny dict: Open Addressing, Compact Layout  [Tier: ◆ Extended]
Chapter 06 · Pattern: hash table internals · Target time: 35 min

Problem
-------
Implement `CompactDict`, a hash map that mirrors how CPython's dict works:

- An INDEX table of size 2**k holding EMPTY (-1), DUMMY (-2, a deleted slot)
  or an integer position into an ENTRIES list.
- The ENTRIES list stores [hash, key, value] in insertion order (None marks a
  deleted entry), so iteration order is insertion order for free.
- Collisions are resolved by OPEN ADDRESSING with CPython's perturbed probe:
      perturb = hash (as unsigned 64-bit);  i = perturb & mask
      repeat: perturb >>= 5;  i = (5*i + perturb + 1) & mask
- Keys match if they are the same object, or have equal hashes and compare ==.
- The entries list may hold at most 2/3 of the index size (live + deleted).
  When a NEW key would not fit, rebuild: new index size = the smallest power
  of two >= 3 * live items (minimum 8), dropping deleted entries.

Support `d[k] = v`, `d[k]`, `del d[k]`, `k in d`, `len(d)`, `keys()`,
`items()`, and raise KeyError for missing keys.

Examples
--------
>>> d = CompactDict(); d["a"] = 1; d["b"] = 2; d["a"] = 3; del d["b"]
>>> d.items(), len(d), "b" in d
([('a', 3)], 1, False)
>>> probe_sequence(8, 8, 4)          # hash 8 in a table of 8 slots
[0, 1, 6, 7]

Constraints
-----------
- Keys are hashable; operations amortised O(1) on average.

Approach ladder
---------------
1. Brute force — association list of (key, value) pairs: O(n) per lookup.
2. Improved   — separate chaining: bucket = hash % m holds a small list; O(1)
   average, but every bucket is its own list (pointer chasing, extra memory).
3. Optimal    — open addressing over one flat table; probing with "perturb"
   mixes in the high bits of the hash so keys that share low bits diverge
   quickly. The compact split (small index array + dense entries) saves memory
   and gives ordered iteration. Deletion must leave a DUMMY, not EMPTY, or
   later keys in the same probe chain become unreachable.

Hints
-----
- Lookup stops at the first EMPTY slot; it walks over DUMMY slots.
- Insert reuses the first slot that is EMPTY or DUMMY on the key's chain
  (only after confirming the key is not already present).

Follow-ups
----------
- Why must equal objects have equal hashes? (Lookup compares hashes first.)
- CPython's set uses the same probing idea but no separate entries array, and
  probes a few neighbouring slots linearly before perturbing.
"""
from __future__ import annotations

import platform
import sys
from typing import Any, Hashable, Iterator

EMPTY, DUMMY = -1, -2
PERTURB_SHIFT = 5
MASK64 = (1 << 64) - 1
MIN_SIZE = 8


def probe_sequence(h: int, size: int, n: int) -> list[int]:
    """First n slots visited for hash h in a table of `size` (a power of two)."""
    mask = size - 1
    perturb = h & MASK64
    i = perturb & mask
    out = [i]
    while len(out) < n:
        perturb >>= PERTURB_SHIFT
        i = (5 * i + perturb + 1) & mask
        out.append(i)
    return out


class AssocList:
    """Rung 1: O(n) lookups."""

    def __init__(self) -> None:
        self.pairs: list[list[Any]] = []

    def __setitem__(self, key: Hashable, value: Any) -> None:
        for pair in self.pairs:
            if pair[0] == key:
                pair[1] = value
                return
        self.pairs.append([key, value])

    def __getitem__(self, key: Hashable) -> Any:
        for k, v in self.pairs:
            if k == key:
                return v
        raise KeyError(key)


class CompactDict:
    def __init__(self) -> None:
        self._indices = [EMPTY] * MIN_SIZE
        self._entries: list[list[Any] | None] = []
        self._used = 0                 # live keys
        self.collisions = 0            # extra probes caused by occupied slots
        self.resizes: list[int] = []   # len(self) when each rebuild happened

    # -- core probing -------------------------------------------------------
    def _find(self, key: Hashable, h: int) -> tuple[int, int]:
        """Return (slot, entry_index); entry_index is -1 if the key is absent,
        and then slot is the first reusable (EMPTY or DUMMY) slot on the chain."""
        mask = len(self._indices) - 1
        perturb = h & MASK64
        i = perturb & mask
        free = -1
        while True:
            ix = self._indices[i]
            if ix == EMPTY:
                return (i if free < 0 else free), -1
            if ix == DUMMY:
                if free < 0:
                    free = i
            else:
                eh, ek, _ = self._entries[ix]
                if ek is key or (eh == h and ek == key):
                    return i, ix
            self.collisions += 1
            perturb >>= PERTURB_SHIFT
            i = (5 * i + perturb + 1) & mask

    def _resize(self) -> None:
        self.resizes.append(self._used)
        size = MIN_SIZE
        while size < 3 * self._used:
            size *= 2
        live = [e for e in self._entries if e is not None]
        self._indices = [EMPTY] * size
        self._entries = []
        for h, k, v in live:                      # re-insert in original order
            slot, _ = self._find(k, h)
            self._indices[slot] = len(self._entries)
            self._entries.append([h, k, v])

    # -- public API -----------------------------------------------------------
    def __setitem__(self, key: Hashable, value: Any) -> None:
        h = hash(key)
        slot, ix = self._find(key, h)
        if ix >= 0:
            self._entries[ix][2] = value          # update keeps the old position
            return
        if len(self._entries) >= len(self._indices) * 2 // 3:   # usable space full
            self._resize()
            slot, _ = self._find(key, h)
        self._indices[slot] = len(self._entries)
        self._entries.append([h, key, value])
        self._used += 1

    def __getitem__(self, key: Hashable) -> Any:
        _, ix = self._find(key, hash(key))
        if ix < 0:
            raise KeyError(key)
        return self._entries[ix][2]

    def __delitem__(self, key: Hashable) -> None:
        slot, ix = self._find(key, hash(key))
        if ix < 0:
            raise KeyError(key)
        self._indices[slot] = DUMMY               # NOT EMPTY: keep chains intact
        self._entries[ix] = None
        self._used -= 1

    def __contains__(self, key: Hashable) -> bool:
        return self._find(key, hash(key))[1] >= 0

    def __len__(self) -> int:
        return self._used

    def __iter__(self) -> Iterator[Hashable]:
        return (e[1] for e in self._entries if e is not None)

    def keys(self) -> list[Hashable]:
        return list(self)

    def items(self) -> list[tuple[Hashable, Any]]:
        return [(e[1], e[2]) for e in self._entries if e is not None]

    def table_size(self) -> int:
        return len(self._indices)


def real_dict_growth_points(n: int) -> list[int]:
    """len() values at which a real dict's allocation grew (CPython 3.7+ only;
    returns [] elsewhere, e.g. PyPy, where getsizeof may raise TypeError)."""
    if platform.python_implementation() != "CPython":
        return []
    d: dict[int, int] = {}
    prev, points = sys.getsizeof(d), []
    for i in range(n):
        d[i] = i
        size = sys.getsizeof(d)
        if size != prev:
            points.append(len(d))
            prev = size
    return points


def main() -> None:
    print("probe slots, table of 8:")
    for h in (0, 8, 16, 13):
        print(f"  hash {h:2} -> {probe_sequence(h, 8, 6)}")
    d = CompactDict()
    for k in (0, 8, 16):                       # all three start at slot 0
        d[k] = f"v{k}"
    print("indices:", d._indices)
    print("entries:", [e[1] for e in d._entries], "| collisions so far:", d.collisions)
    del d[8]
    print("after del 8 -> indices:", d._indices, "| 16 still found:", d[16] == "v16")
    d[8] = "again"
    print("re-insert 8 reuses the DUMMY slot -> indices:", d._indices)
    print("iteration (insertion order):", d.keys())

    big = CompactDict()
    model_points = []
    for i in range(100):
        before = big.table_size()
        big[i] = i
        if big.table_size() != before:
            model_points.append(len(big))
    print("model grew at len:", model_points, "| final table size:", big.table_size())
    real = real_dict_growth_points(100)     # real[0] == 1: first insert allocates the table
    if real:
        print("real dict grew at len:", real[1:], "| matches model:", real[1:] == model_points)
    else:
        print("real dict growth: not CPython, skipped")
    words = CompactDict()
    for w in "the quick brown fox jumps over the lazy dog".split():
        words[w] = words[w] + 1 if w in words else 1
    print("word counts:", words.items())
    print("hash(-1) =", hash(-1), "| hash(1) == hash(1.0) == hash(True):", hash(1) == hash(1.0) == hash(True))
    try:
        d["missing"]
    except KeyError as exc:
        print("KeyError:", exc)


if __name__ == "__main__":
    main()
