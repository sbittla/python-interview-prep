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

Approach ladder
---------------
1. Brute force — keep only the brackets (with their indices) and repeatedly delete adjacent
   matching pairs until nothing changes. What survives is the error: the first surviving
   closer, else the first surviving opener. O(n^2) time (up to n/2 passes of O(n)).
2. Optimal    — one left-to-right scan with a stack of opener *indices*. A closer must match
   the top; if it does not (or the stack is empty) its index is the answer. At the end a
   non-empty stack means unclosed openers; ``stack[0]`` is the leftmost. O(n) time, O(n) space.
   Why move up: each character is pushed and popped at most once instead of being rescanned
   on every pass.

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
    items = [(i, ch) for i, ch in enumerate(s) if ch in OPENERS or ch in PAIRS]
    changed = True
    while changed:
        changed = False
        for k in range(len(items) - 1):
            if items[k + 1][1] in PAIRS and PAIRS[items[k + 1][1]] == items[k][1]:
                del items[k:k + 2]
                changed = True
                break
    for i, ch in items:
        if ch in PAIRS:
            return i
    return items[0][0] if items else -1


def first_error(s: str) -> int:
    stack: list[int] = []                      # indices of unmatched openers
    for i, ch in enumerate(s):
        if ch in OPENERS:
            stack.append(i)
        elif ch in PAIRS:
            if not stack or s[stack[-1]] != PAIRS[ch]:
                return i                       # stray or wrong-kind closer
            stack.pop()
    return stack[0] if stack else -1           # leftmost unclosed opener


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
