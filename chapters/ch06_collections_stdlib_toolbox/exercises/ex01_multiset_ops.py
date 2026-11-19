"""
Exercise 01 — Sticker Sheets: Multiset Algebra with Counter      [Tier: ★ Core]
Chapter 06 · Pattern: Counter as a multiset · Target time: 10 min

Problem
-------
A child spells words with letter stickers. A sticker sheet is a string; each
character is one sticker (spaces are ignored). Implement:

1. `can_spell(word, sheet)` — True if every letter of `word` (with
   multiplicity) is available on `sheet`.
2. `shortfall(word, sheet)` — a dict of the letters still needed and how many,
   sorted by letter (empty dict if the word can be spelled).
3. `shared_stickers(a, b)` — the letters two sheets have in common, with
   multiplicity, as a sorted string (multiset intersection).
4. `combined_need(words)` — the smallest sheet (sorted string) that can spell
   ANY ONE of the words on its own (multiset union = per-letter maximum).

Examples
--------
>>> can_spell("noon", "on no")
True
>>> shortfall("banana", "ban")
{'a': 2, 'n': 1}
>>> shared_stickers("aabbc", "abbbd")
'abb'
>>> combined_need(["moon", "mono", "nom"])
'mnoo'

Constraints
-----------
- Lowercase letters and spaces; strings up to 10**5 characters.

Hints
-----
- Counter subtraction keeps only positive counts — exactly "what is missing".
- `&` takes the per-key minimum, `|` the per-key maximum.

Follow-ups
----------
- Unicode letters / case-insensitive matching: normalise with `casefold()`.
- Counter comparison operators need Python 3.10+; on 3.9 use `not (need - have)`.
"""
from __future__ import annotations

from collections import Counter


def _letters(s: str) -> str:
    return s.replace(" ", "")


def brute_force_can_spell(word: str, sheet: str) -> bool:
    raise NotImplementedError("TODO")


def can_spell(word: str, sheet: str) -> bool:
    raise NotImplementedError("TODO")


def shortfall(word: str, sheet: str) -> dict[str, int]:
    raise NotImplementedError("TODO")


def shared_stickers(a: str, b: str) -> str:
    raise NotImplementedError("TODO")


def combined_need(words: list[str]) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for word, sheet in [("noon", "on no"), ("banana", "ban"), ("", "abc"), ("abc", "")]:
        print(f"{word!r:9} from {sheet!r:8} can_spell={can_spell(word, sheet)!s:5} "
              f"brute={brute_force_can_spell(word, sheet)!s:5} shortfall={shortfall(word, sheet)}")
    print("shared_stickers('aabbc', 'abbbd') =", repr(shared_stickers("aabbc", "abbbd")))
    print("combined_need(['moon', 'mono', 'nom']) =", repr(combined_need(["moon", "mono", "nom"])))
    print("Counter('abca').most_common(1) =", Counter("abca").most_common(1))


if __name__ == "__main__":
    main()
