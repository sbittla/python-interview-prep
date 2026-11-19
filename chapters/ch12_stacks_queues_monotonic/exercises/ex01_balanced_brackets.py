"""
Exercise 01 — Balanced Brackets With Error Position          [Tier: ★ Core]
Chapter 12 · Pattern: stack matching · Target time: 15 min

Problem
-------
A code editor wants to underline the first bracket problem in a line. Given a string that may
contain ``()[]{}`` mixed with any other characters, return ``-1`` if every bracket is matched
and correctly nested. Otherwise return the index of the offending character:

- the first closing bracket that has no opener or closes the wrong kind, or
- if the scan reaches the end with openers still waiting, the leftmost unclosed opener.

Non-bracket characters are ignored.

Examples
--------
>>> first_error("f(a[i]) + {b}")
-1
>>> first_error("(]")
1
>>> first_error("x = (a + [b)")
11
>>> first_error("((a)")
0

Constraints
-----------
- 0 <= len(s) <= 10**5

Hints
-----
- Brute force: delete adjacent matching pairs until nothing changes; inspect what is left.
- Optimal: push opener *indices*; a closer must match the top of the stack.
- Do not forget the end-of-string check — which unclosed opener is the leftmost?

Wrong-but-tempting
------------------
- Counting: ``s.count("(") == s.count(")")`` accepts ``")("`` and ``"([)]"``.
- One counter per bracket kind still accepts ``"([)]"`` — nesting needs a stack.
- Storing characters instead of indices: you then cannot report *where* the error is.
- Forgetting the end-of-string check: ``"(("`` would be reported as balanced.

Follow-ups
----------
- Minimum number of insertions to balance a string of ``(`` and ``)`` only (counter suffices).
- Longest valid parentheses substring (stack of indices with a base sentinel ``-1``).
- Ignore brackets inside string literals: add a small state machine around the scan.
"""
from __future__ import annotations

PAIRS = {")": "(", "]": "[", "}": "{"}
OPENERS = set(PAIRS.values())


def brute_force(s: str) -> int:
    raise NotImplementedError("TODO")


def first_error(s: str) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = ["f(a[i]) + {b}", "(]", "x = (a + [b)", "((a)", ")(", "([)]", "", "no brackets",
             "{[()()]}", "(()", "a)b"]
    for s in cases:
        pos = first_error(s)
        marker = "" if pos < 0 else " " * (pos + 1) + "^"
        print(f"{s!r:<17} -> {pos:>2}  agree={pos == brute_force(s)}")
        if marker:
            print(marker)


if __name__ == "__main__":
    main()
