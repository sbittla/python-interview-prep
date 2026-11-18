"""
Exercise 16 — A Leaderboard That Crashes on None        [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (sorting) · Target time: 8 min

Problem
-------
`leaderboard(records)` takes dicts like `{"name": "ana", "score": 90}` where
`score` may be `None` (did not finish). Return the names ordered by score
DESCENDING, ties by name ASCENDING, and all `None` scores LAST (themselves in
name order). The buggy version sorts by `r["score"]` with `reverse=True`:
comparing `None` with an int raises TypeError — and `reverse=True` would also
reverse the name tie-break.

Examples
--------
>>> leaderboard([{"name": "cy", "score": None}, {"name": "bo", "score": 90},
...              {"name": "al", "score": 90}, {"name": "di", "score": 75}])
['al', 'bo', 'di', 'cy']

Constraints
-----------
- Scores are ints or None; names are unique strings.

Approach ladder
---------------
1. Buggy  — key returns None for some records; Python 3 refuses to order None vs int.
2. Fixed  — a tuple key `(score is None, -(score or 0), name)`: False sorts before
   True, so real scores come first; negate the number for descending while
   keeping names ascending. O(n log n).
3. Alternative — two stable sorts (by name, then by score with reverse=True),
   relying on Timsort stability; or `functools.cmp_to_key` for comparisons that
   cannot be expressed as a key (rare).

Follow-ups
----------
- Descending by a STRING field and ascending by another? (Negation fails for
  strings: use two stable sorts or cmp_to_key.)
- Is `sorted` stable? (Yes — equal keys keep their input order.)
"""
from __future__ import annotations

from functools import cmp_to_key
from typing import Any

Record = dict[str, Any]


def buggy_leaderboard(records: list[Record]) -> list[str]:
    return [r["name"] for r in sorted(records, key=lambda r: r["score"], reverse=True)]


def leaderboard(records: list[Record]) -> list[str]:
    """Score desc, name asc, None scores last."""
    def key(r: Record) -> tuple[bool, int, str]:
        score = r["score"]
        return (score is None, -(score if score is not None else 0), r["name"])

    return [r["name"] for r in sorted(records, key=key)]


def leaderboard_two_pass(records: list[Record]) -> list[str]:
    """Same ordering via two STABLE sorts (secondary key first)."""
    by_name = sorted(records, key=lambda r: r["name"])
    scored = [r for r in by_name if r["score"] is not None]
    unscored = [r for r in by_name if r["score"] is None]
    scored.sort(key=lambda r: r["score"], reverse=True)   # stable even with reverse=True
    return [r["name"] for r in scored + unscored]


def leaderboard_cmp(records: list[Record]) -> list[str]:
    """Same ordering with an old-style comparator (cmp_to_key)."""
    def cmp(a: Record, b: Record) -> int:
        sa, sb = a["score"], b["score"]
        if (sa is None) != (sb is None):
            return 1 if sa is None else -1
        if sa != sb:
            return -1 if sa > sb else 1
        return (a["name"] > b["name"]) - (a["name"] < b["name"])

    return [r["name"] for r in sorted(records, key=cmp_to_key(cmp))]


def main() -> None:
    records = [
        {"name": "cy", "score": None},
        {"name": "bo", "score": 90},
        {"name": "al", "score": 90},
        {"name": "di", "score": 75},
        {"name": "ab", "score": None},
    ]
    try:
        buggy_leaderboard(records)
    except TypeError as exc:
        print("buggy:", type(exc).__name__, "-", exc)
    print("fixed (tuple key):", leaderboard(records))
    print("fixed (two stable sorts):", leaderboard_two_pass(records))
    print("fixed (cmp_to_key):", leaderboard_cmp(records))
    print("no None, buggy order:", buggy_leaderboard([r for r in records if r["score"] is not None]))


if __name__ == "__main__":
    main()
