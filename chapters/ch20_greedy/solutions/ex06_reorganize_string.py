"""
Exercise 06 — Reorganise String                                    [Tier: ◆ Extended]
Chapter 20 · Pattern: greedy with a max-heap · Target time: 25 min

Problem
-------
Rearrange the characters of `s` so that no two adjacent characters are equal. Return any
valid arrangement, or "" if impossible. For determinism, break ties between equally frequent
characters alphabetically.

Examples
--------
>>> reorganize("aab")
'aba'
>>> reorganize("aaab")
''

Constraints
-----------
- 1 <= len(s) <= 500, lowercase letters.

Approach ladder
---------------
1. Brute force — try permutations until one is valid. O(n! * n). Only for tiny inputs.
2. Optimal (heap) — always place the most frequent remaining character that differs from the
   previous one. Hold the just-used character out of the heap for one step, then push it
   back. O(n log k) time, k = distinct characters.
3. Alternative O(n) — feasibility test max_count <= (n + 1) // 2, then fill even indices
   with the most frequent character first, then the rest, then odd indices.

Hints
-----
- When is it impossible? Compare the most frequent count with (n + 1) // 2.
- Using the most frequent letter first keeps the "danger" letter from piling up at the end.

Follow-ups
----------
- Rearrange so equal characters are at least k apart (generalise the cooldown queue).
- Count the number of valid arrangements: no longer greedy; inclusion-exclusion / DP.
"""
from __future__ import annotations

import heapq
from collections import Counter
from itertools import permutations


def is_valid(t: str) -> bool:
    return all(a != b for a, b in zip(t, t[1:]))


def brute_force(s: str) -> str:
    for p in sorted(set(permutations(s))):
        if is_valid(p):
            return "".join(p)
    return ""


def reorganize(s: str) -> str:
    counts = Counter(s)
    if counts and max(counts.values()) > (len(s) + 1) // 2:
        return ""
    heap = [(-c, ch) for ch, c in counts.items()]     # (negative count, char): max-heap
    heapq.heapify(heap)
    out: list[str] = []
    held: tuple[int, str] | None = None               # the char used last step
    while heap:
        c, ch = heapq.heappop(heap)
        out.append(ch)
        if held:
            heapq.heappush(heap, held)                # previous char is allowed again
        held = (c + 1, ch) if c + 1 < 0 else None
    return "".join(out) if len(out) == len(s) else ""


def reorganize_even_odd(s: str) -> str:
    counts = Counter(s)
    n = len(s)
    if counts and max(counts.values()) > (n + 1) // 2:
        return ""
    order = sorted(counts, key=lambda ch: (-counts[ch], ch))
    out = [""] * n
    idx = 0
    for ch in order:
        for _ in range(counts[ch]):
            if idx >= n:
                idx = 1                                # switch to odd positions
            out[idx] = ch
            idx += 2
    return "".join(out)


def main() -> None:
    for s in ("aab", "aaab", "aaabbc", "vvvlo", "a", "aa", "abcabc", "aaabb"):
        r = reorganize(s)
        e = reorganize_even_odd(s)
        print(f"{s!r:<9} heap={r!r:<9} valid={is_valid(r) if r else '-'!s:<5} "
              f"even/odd={e!r:<9} brute={brute_force(s)!r}")
    # Tempting but wrong: alternate in sorted order without counting frequencies
    s = "aaabc"
    naive = "".join(sorted(s))
    print("sorted naive for", repr(s), "->", repr(naive), "valid:", is_valid(naive),
          "| heap:", repr(reorganize(s)))


if __name__ == "__main__":
    main()
