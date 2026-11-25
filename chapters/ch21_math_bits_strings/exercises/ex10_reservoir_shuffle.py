"""
Exercise 10 — Reservoir Sampling and Fisher–Yates Shuffle      [Tier: ◆ Extended]
Chapter 21 · Pattern: randomised algorithms with a proof you can check · Target time: 25 min

Problem
-------
1. ``reservoir_sample(stream, k, randbelow)``: one pass over an iterable of unknown length,
   O(k) memory; every k-subset of the n items is equally likely. Fewer than k items -> all
   of them. k < 0 raises ``ValueError``.
2. ``fisher_yates(items, randbelow)``: a uniformly random permutation (returns a new list).
3. ``exact_counts(algorithm, n, ...)``: *deterministic* uniformity check — run the algorithm
   once for every possible sequence of random choices and count each outcome.

``randbelow(b)`` must return an int in [0, b); pass ``random.Random(seed).randrange`` for
reproducible runs, or a scripted chooser for the exact check.

Examples
--------
>>> exact_counts("fisher_yates", 3)          # each of the 3! permutations exactly once
{(0, 1, 2): 1, (0, 2, 1): 1, (1, 0, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1, (2, 1, 0): 1}

Constraints
-----------
- Stream length unknown in advance; may not fit in memory.

Hints
-----
- Reservoir: keep the first k; item i (0-based) picks j = randbelow(i + 1) and replaces
  slot j only if j < k.
- Fisher–Yates: walk i from n - 1 down to 1 and swap a[i] with a[randbelow(i + 1)].
- Exact check: ``itertools.product`` over the ranges of every random call, feeding the
  choices to the algorithm through a scripted ``randbelow``.

Wrong-but-tempting
------------------
- ``randbelow(len(a))`` for every i (the naive shuffle): n**n paths over n! permutations.
- ``randbelow(i)`` instead of ``randbelow(i + 1)``: never leaves an element in place
  (Sattolo's algorithm — only cyclic permutations).
- Replacing with probability 1/(i + 1) instead of k/(i + 1) when k > 1.

Follow-ups
----------
- Weighted reservoir (Efraimidis–Spirakis): key = u ** (1 / w), keep the k largest keys.
- Proof for Algorithm R: item i survives to the end with (k/(i+1)) * prod_{t>i} (1 - 1/(t+1))
  = k/n.
"""
from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable, Iterable
from itertools import product

RandBelow = Callable[[int], int]


def sample_brute(stream: Iterable, k: int, rng: random.Random) -> list:
    raise NotImplementedError("TODO")


def reservoir_sample(stream: Iterable, k: int, randbelow: RandBelow) -> list:
    raise NotImplementedError("TODO")


def shuffle_pick_pop(items: list, randbelow: RandBelow) -> list:
    raise NotImplementedError("TODO")


def fisher_yates(items: list, randbelow: RandBelow) -> list:
    raise NotImplementedError("TODO")


def naive_shuffle(items: list, randbelow: RandBelow) -> list:
    """WRONG: biased for n >= 3."""
    raise NotImplementedError("TODO")


def _scripted(choices: tuple[int, ...]) -> RandBelow:
    it = iter(choices)

    def randbelow(b: int) -> int:
        j = next(it)
        assert 0 <= j < b
        return j
    return randbelow


def exact_counts(algorithm: str, n: int, k: int = 0) -> dict[tuple, int]:
    """Enumerate every random-choice sequence; outcome -> number of sequences."""
    raise NotImplementedError("TODO")


def main() -> None:
    rng = random.Random(21)
    print("reservoir(range(10), 3) =", reservoir_sample(range(10), 3, rng.randrange))
    print("reservoir(range(2), 5)  =", reservoir_sample(range(2), 5, rng.randrange))
    print("fisher_yates('abcde')   =", "".join(fisher_yates(list("abcde"), rng.randrange)))
    print("sample_brute(range(10), 3) =", sample_brute(range(10), 3, rng))

    print("exact fisher_yates n=3:", list(exact_counts("fisher_yates", 3).values()))
    print("exact pick_pop     n=3:", list(exact_counts("pick_pop", 3).values()))
    print("exact naive        n=3:", list(exact_counts("naive", 3).values()), " <- biased")
    fy4 = exact_counts("fisher_yates", 4)
    print("exact fisher_yates n=4: outcomes =", len(fy4), " counts =", set(fy4.values()))
    res = exact_counts("reservoir", 5, k=2)
    print("exact reservoir n=5 k=2: subsets =", len(res), " counts =", set(res.values()))

    # Seeded empirical check (deterministic because the seed is fixed).
    rng = random.Random(2024)
    trials, n, k = 30_000, 6, 2
    hits = Counter(x for _ in range(trials) for x in reservoir_sample(range(n), k, rng.randrange))
    expected = trials * k / n
    worst = max(abs(hits[x] - expected) / expected for x in range(n))
    print(f"empirical reservoir: per-item counts {[hits[x] for x in range(n)]}, "
          f"expected {expected:.0f}, max relative deviation < 3%: {worst < 0.03}")


if __name__ == "__main__":
    main()
