"""
Exercise 06 — LCS and Edit Distance with Reconstruction             [Tier: ★ Core]
Chapter 19 · Pattern: two-sequence DP table · Target time: 40 min

Problem
-------
1. `lcs(a, b)` — return one longest common subsequence of strings a and b (the
   characters appear in both, in order, not necessarily adjacent). `lcs_length` returns
   its length; `lcs_table` returns the full (len(a)+1) x (len(b)+1) table.
2. `edit_distance(a, b)` — the fewest single-character inserts, deletes and
   substitutions that turn a into b (Levenshtein distance).
3. `edit_ops(a, b)` — one optimal script as a list of (op, src, dst) tuples where op
   is "keep", "sub", "ins" or "del"; `apply_ops` replays a script to check it.

Examples
--------
>>> lcs("ABCBDAB", "BDCABA"), lcs_length("abc", "def")
('BCBA', 0)
>>> edit_distance("horse", "ros"), edit_distance("", "abc")
(3, 3)
>>> [op for op in edit_ops("cat", "cut") if op[0] != "keep"]
[('sub', 'a', 'u')]

Constraints
-----------
- 0 <= len(a), len(b) <= 2000.

Hints
-----
- Reconstruct LCS from (m, n): on a match take the character and go diagonally,
  otherwise move toward the larger neighbour.
- For edit ops, re-derive which of the three neighbours produced D(i, j).
- If only inserts and deletes are allowed, distance = m + n - 2 * LCS(a, b).

Follow-ups
----------
- Shortest common supersequence: length m + n - LCS; build it from the LCS walk.
- Longest common SUBSTRING (contiguous): reset to 0 on a mismatch, answer is the max cell.
- Weighted edits: replace the 1s with costs; nothing else changes.
"""
from __future__ import annotations

from functools import cache


# ---------------------------------------------------------------- LCS
def lcs_brute(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def lcs_memo(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def lcs_table(a: str, b: str) -> list[list[int]]:
    raise NotImplementedError("TODO")


def lcs(a: str, b: str) -> str:
    raise NotImplementedError("TODO")


def lcs_length(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def render_table(a: str, b: str) -> str:
    L = lcs_table(a, b)
    lines = ["     " + "".join(f"{ch:>3}" for ch in b)]
    for i, row in enumerate(L):
        label = a[i - 1] if i else ""
        lines.append(f"{label:<2}" + "".join(f"{v:>3}" for v in row))
    return "\n".join(lines)


# ---------------------------------------------------------------- edit distance
def edit_brute(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def edit_memo(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def edit_table(a: str, b: str) -> list[list[int]]:
    raise NotImplementedError("TODO")


def edit_distance(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def edit_ops(a: str, b: str) -> list[tuple[str, str, str]]:
    raise NotImplementedError("TODO")


def apply_ops(a: str, ops: list[tuple[str, str, str]]) -> str:
    """Replay a script; checks that it consumes exactly a and returns the output."""
    assert "".join(src for _, src, _ in ops) == a, "script does not consume a"
    return "".join(dst for _, _, dst in ops)


def main() -> None:
    a, b = "ABCBDAB", "BDCABA"
    print(f"LCS table for a={a!r} (rows), b={b!r} (columns):")
    print(render_table(a, b))
    for x, y in ((a, b), ("abcde", "ace"), ("abc", "def"), ("", "abc")):
        rungs = (lcs_brute(x, y), lcs_memo(x, y), lcs_table(x, y)[-1][-1], lcs_length(x, y))
        print(f"lcs({x!r}, {y!r}) = {lcs(x, y)!r}  rungs agree: {len(set(rungs)) == 1}")
    for x, y in (("horse", "ros"), ("intention", "execution"), ("kitten", "sitting"),
                 ("", "abc"), ("same", "same")):
        rungs = (edit_brute(x, y), edit_memo(x, y), edit_table(x, y)[-1][-1], edit_distance(x, y))
        ops = edit_ops(x, y)
        script = " ".join(f"{op}:{s}>{d}" if op == "sub" else f"{op}:{s or d}"
                          for op, s, d in ops if op != "keep")
        print(f"edit({x!r}, {y!r}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}  "
              f"replay ok: {apply_ops(x, ops) == y}  ops: {script or '-'}")
    x, y = "sunday", "saturday"
    print("insert/delete-only distance via LCS:", len(x) + len(y) - 2 * lcs_length(x, y))


if __name__ == "__main__":
    main()
