"""
Exercise 08 — itertools Recipes                               [Tier: ◆ Extended]
Chapter 23 · Pattern: itertools composition · Target time: 25 min

Problem
-------
Implement each with itertools building blocks (no index arithmetic):

1. ``run_length_encode(s)``     -> list of (char, count) for consecutive runs.
2. ``run_length_decode(pairs)`` -> the original string.
3. ``running_max(nums)``        -> list of the maximum so far at each position.
4. ``unique_everseen(it, key=None)`` -> items in first-seen order, deduplicated (by key).
5. ``roundrobin(*iterables)``   -> one item from each iterable in turn until all are exhausted.
6. ``powerset(items)``          -> all subsets as tuples, smallest first.

Examples
--------
>>> run_length_encode("aaabccdd")
[('a', 3), ('b', 1), ('c', 2), ('d', 2)]
>>> running_max([3, 1, 4, 1, 5])
[3, 3, 4, 4, 5]
>>> list(roundrobin("ABC", "D", "EF"))
['A', 'D', 'E', 'B', 'F', 'C']

Constraints
-----------
- Lazy where the result can be infinite (``unique_everseen``, ``roundrobin``).

Hints
-----
- ``groupby`` groups *consecutive* equal keys — exactly run-length encoding.
- ``accumulate(nums, max)`` gives running maxima; ``accumulate`` defaults to running sums.
- ``roundrobin``: keep a deque of iterators; pop left, take one item, push back if not exhausted.
- ``powerset``: ``chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))``.

Approach ladder
---------------
1. Index-based loops with manual counters — easy to get off-by-one, eager.
2. itertools building blocks — each recipe is O(n) and lazy where possible; the C-implemented
   tools are also faster than equivalent Python loops.

Follow-ups
----------
- Why must you sort before ``groupby`` when grouping *all* equal keys (not just runs)?
- ``product``, ``permutations``, ``combinations``, ``combinations_with_replacement``: give the count
  formula for each.
"""
from __future__ import annotations

from collections import deque
from itertools import (accumulate, chain, combinations, combinations_with_replacement,
                       compress, dropwhile, groupby, permutations, product, repeat, starmap,
                       takewhile)
from typing import Callable, Iterable, Iterator


def run_length_encode(s: str) -> list[tuple[str, int]]:
    return [(ch, sum(1 for _ in grp)) for ch, grp in groupby(s)]


def run_length_decode(pairs: Iterable[tuple[str, int]]) -> str:
    return "".join(chain.from_iterable(starmap(repeat, pairs)))


def running_max(nums: Iterable[int]) -> list[int]:
    return list(accumulate(nums, max))


def unique_everseen(iterable: Iterable, key: Callable | None = None) -> Iterator:
    seen = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item


def roundrobin(*iterables: Iterable) -> Iterator:
    queue = deque(iter(it) for it in iterables)
    while queue:
        it = queue.popleft()
        try:
            item = next(it)
        except StopIteration:
            continue
        yield item
        queue.append(it)


def powerset(items: Iterable) -> list[tuple]:
    s = list(items)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


def main() -> None:
    enc = run_length_encode("aaabccdd")
    print("rle encode:", enc)
    print("rle decode:", run_length_decode(enc))
    print("running max:", running_max([3, 1, 4, 1, 5, 9, 2, 6]))
    print("running sum:", list(accumulate([1, 2, 3, 4])))
    print("unique_everseen:", list(unique_everseen("AAAABBBCCDAABBB")))
    print("unique by lower:", list(unique_everseen("aAbBcCa", key=str.lower)))
    print("roundrobin:", list(roundrobin("ABC", "D", "EF")))
    print("powerset:", powerset("abc"))

    # Tour of the combinatoric iterators (counts match the formulas in the chapter).
    s = "ABC"
    print("product(AB, repeat=2):", ["".join(p) for p in product("AB", repeat=2)])
    print("permutations(ABC, 2):", ["".join(p) for p in permutations(s, 2)])
    print("combinations(ABC, 2):", ["".join(p) for p in combinations(s, 2)])
    print("combos w/ replacement:",
          ["".join(p) for p in combinations_with_replacement(s, 2)])
    print("compress:", list(compress("ABCDEF", [1, 0, 1, 0, 1, 1])))
    print("takewhile <5:", list(takewhile(lambda x: x < 5, [1, 4, 6, 3])))
    print("dropwhile <5:", list(dropwhile(lambda x: x < 5, [1, 4, 6, 3])))

    # groupby gotcha: unsorted input splits groups.
    words = ["apple", "bob", "avocado", "banana"]
    unsorted = [(k, list(g)) for k, g in groupby(words, key=lambda w: w[0])]
    by_letter = [(k, list(g)) for k, g in groupby(sorted(words), key=lambda w: w[0])]
    print("groupby unsorted:", unsorted)
    print("groupby sorted  :", by_letter)


if __name__ == "__main__":
    main()
