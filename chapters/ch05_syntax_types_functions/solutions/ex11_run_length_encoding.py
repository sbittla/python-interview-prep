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

Approach ladder
---------------
1. Brute force — build the result with ``result += piece`` inside the loop. Correct, but
   repeated string concatenation can be O(n**2) in general because strings are immutable
   (CPython sometimes optimises it in place, but do not rely on that).
2. Optimal    — collect pieces in a list and ``"".join`` them once at the end: O(n) time and
   space. ``itertools.groupby`` (§6.10) turns encoding into a one-liner.

Follow-ups
----------
- Only encode runs longer than 1 ("aaab" -> "a3b")? Then decoding must treat a missing count
  as 1.
- Stream the input and output so the whole string never sits in memory.
"""
from __future__ import annotations


def brute_force(s: str) -> str:
    result = ""
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        result += s[i] + str(j - i)
        i = j
    return result


def solve(s: str) -> str:
    if not s:
        return ""
    parts: list[str] = []
    run_char, run_len = s[0], 1
    for ch in s[1:]:
        if ch == run_char:
            run_len += 1
        else:
            parts.append(f"{run_char}{run_len}")
            run_char, run_len = ch, 1
    parts.append(f"{run_char}{run_len}")    # flush the last run: the classic forgotten step
    return "".join(parts)


def decode(code: str) -> str:
    parts: list[str] = []
    i = 0
    while i < len(code):
        ch = code[i]
        j = i + 1
        while j < len(code) and code[j].isdigit():
            j += 1
        if j == i + 1:
            raise ValueError(f"missing count after {ch!r} at index {i}")
        parts.append(ch * int(code[i + 1:j]))
        i = j
    return "".join(parts)


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
