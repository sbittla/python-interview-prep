"""
Exercise 03 — Top-K Frequent Words With a Tie-Break                [Tier: ★ Core]
Chapter 15 · Pattern: Counter + size-k heap vs bucket vs sort · Target time: 20 min

Problem
-------
Given a list of words and k, return the k most frequent words, ordered by frequency
(highest first); words with the same frequency are ordered alphabetically.

(Ch 9 ex04 solves the integer version with bucket sort; here the tie-break runs in the
OPPOSITE direction to the count, which is what makes the size-k heap interesting.)

Examples
--------
>>> solve(["b", "a", "c", "a", "b", "d"], 2)
['a', 'b']
>>> solve(["to", "be", "or", "not", "to", "be"], 3)
['be', 'to', 'not']

Constraints
-----------
- 1 <= k <= number of distinct words; n words, d distinct.

Approach ladder
---------------
1. Sort        — Counter, then sort the d distinct words by (-count, word): O(n + d log d).
2. nsmallest   — `heapq.nsmallest(k, counts, key=lambda w: (-counts[w], w))`:
   O(n + d log k). One line; the cleanest interview answer.
3. Size-k heap — hand-rolled min-heap of the k best so far. The ROOT must be the WORST kept
   word: lowest count, and among equal counts the alphabetically LATEST word. Counts ascend
   but words must descend, so wrap the word in a class with a reversed `__lt__`.
   O(n + d log k) time, O(k) extra space — and it works when counts arrive as a stream.
4. Bucket      — bucket[f] = words seen f times, walk f from high to low, sort each bucket.
   O(n) when buckets are small, but the alphabetical sort inside a bucket makes it
   O(n + d log d) in the worst case (all words tie).

Hints
-----
- Negating a count is easy; negating a string is impossible — that's the whole problem.
- A tiny class with `__lt__` returning `self.word > other.word` reverses string order.
- Pop the k kept items (worst first) and reverse.

Follow-ups
----------
- Huge vocabulary, k = 10: heap wins over sort (d log k vs d log d).
- Streaming counts that change: a heap cannot update a key in place; re-push and skip
  stale entries (lazy deletion).
- Distributed: top-k per shard is NOT enough for the global top-k unless you merge full
  counts (a word can be 11th everywhere and 1st overall).

Wrong-but-tempting
------------------
- Heap of `(count, word)` with size k: on ties it evicts the alphabetically SMALLER word,
  the one you wanted to keep.
- Heap of `(-count, word)` with size k popping the root: evicts the MOST frequent word.
"""
from __future__ import annotations

import heapq
import random
from collections import Counter


def by_sort(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    return sorted(counts, key=lambda w: (-counts[w], w))[:k]


def by_nsmallest(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    return heapq.nsmallest(k, counts, key=lambda w: (-counts[w], w))


class _Rev:
    """Wraps a word so that heap order on words is reversed (later word = 'smaller')."""
    __slots__ = ("word",)

    def __init__(self, word: str) -> None:
        self.word = word

    def __lt__(self, other: _Rev) -> bool:
        return self.word > other.word


def by_size_k_heap(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    heap: list[tuple[int, _Rev]] = []                # root = worst kept word
    for word, c in counts.items():
        heapq.heappush(heap, (c, _Rev(word)))
        if len(heap) > k:
            heapq.heappop(heap)                       # evict the current worst
    out = [heapq.heappop(heap)[1].word for _ in range(len(heap))]
    return out[::-1]                                  # worst-first -> best-first


def by_bucket(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    buckets: list[list[str]] = [[] for _ in range(len(words) + 1)]
    for word, c in counts.items():
        buckets[c].append(word)
    out: list[str] = []
    for c in range(len(buckets) - 1, 0, -1):
        for word in sorted(buckets[c]):
            out.append(word)
            if len(out) == k:
                return out
    return out


def solve(words: list[str], k: int) -> list[str]:
    return by_size_k_heap(words, k)


def main() -> None:
    cases = [(["b", "a", "c", "a", "b", "d"], 2),
             (["to", "be", "or", "not", "to", "be"], 3),
             (["x", "y", "z"], 3),
             (["cat"], 1)]
    for words, k in cases:
        ans = solve(words, k)
        agree = ans == by_sort(words, k) == by_nsmallest(words, k) == by_bucket(words, k)
        print(f"k={k} {words} -> {ans}  agree={agree}")

    # The tempting bug: (count, word) tuples evict the wrong word on a tie.
    words = ["b", "b", "a", "a", "c"]
    heap: list[tuple[int, str]] = []
    for w, c in Counter(words).items():
        heapq.heappush(heap, (c, w))
        if len(heap) > 1:
            heapq.heappop(heap)
    print("k=1 tie a/b, naive (count, word) heap keeps:", heap[0][1], "| correct:", solve(words, 1))

    rng = random.Random(15)
    ok = True
    for _ in range(300):
        ws = [rng.choice("abcdefg") * rng.randint(1, 2) for _ in range(rng.randint(1, 25))]
        k = rng.randint(1, len(set(ws)))
        ok &= solve(ws, k) == by_sort(ws, k) == by_nsmallest(ws, k) == by_bucket(ws, k)
    print("300 random tie-heavy cases, all four agree:", ok)


if __name__ == "__main__":
    main()
