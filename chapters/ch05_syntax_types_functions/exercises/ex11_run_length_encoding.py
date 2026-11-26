"""
Exercise 11 — Run-Length Encoding and Decoding                [Tier: ★ Core]
Chapter 05 · Pattern: string scanning, building output · Target time: 15 min

Problem
-------
``solve(s)`` encodes a string of letters as runs: every maximal run of a repeated character
becomes the character followed by the run length (``"aaabcc" -> "a3b1c2"``). ``decode(code)``
reverses it; counts may have several digits (``"x12" -> 12 x's``).

Examples
--------
>>> solve("aaabcc")
'a3b1c2'
>>> decode("a3b1c2")
'aaabcc'
>>> decode(solve("z" * 12))
'zzzzzzzzzzzz'

Constraints
-----------
- 0 <= len(s) <= 10**5; s contains no digits (otherwise the code would be ambiguous)

Hints
-----
1. ``brute_force``: scan runs with two indices and grow the result with ``+=``.
2. ``solve``: collect pieces in a list and join once. Do not forget the final run.
3. ``decode``: a count can have several digits; read digits until a non-digit.
4. Which inputs should ``decode`` reject?

Follow-ups
----------
- Only encode runs longer than 1 ("aaab" -> "a3b")? What changes in ``decode``?
- Stream the input and output so the whole string never sits in memory.
"""
from __future__ import annotations


def brute_force(s: str) -> str:
    raise NotImplementedError("TODO")


def solve(s: str) -> str:
    raise NotImplementedError("TODO")


def decode(code: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ["aaabcc", "", "a", "abc", "z" * 12, "wwwwaaadexxxxxx"]:
        enc = solve(s)
        print(f"{s!r:20} -> {enc!r:16} round-trip ok: {decode(enc) == s}, brute agrees: {brute_force(s) == enc}")
    try:
        decode("ab2")
    except ValueError as exc:
        print("ValueError:", exc)


if __name__ == "__main__":
    main()
