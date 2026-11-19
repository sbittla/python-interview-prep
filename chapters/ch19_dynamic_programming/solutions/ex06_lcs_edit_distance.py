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

Approach ladder
---------------
LCS recipe — state: L(i, j) = LCS length of a[:i] and b[:j]; transition: if
a[i-1] == b[j-1] then L(i-1, j-1) + 1 else max(L(i-1, j), L(i, j-1)); base: row 0 and
column 0 are 0; order: rows top to bottom, left to right; answer: L(m, n).
Edit distance recipe — state: D(i, j) = edits turning a[:i] into b[:j]; transition:
D(i-1, j-1) if the last characters match, else 1 + min(D(i-1, j) [delete],
D(i, j-1) [insert], D(i-1, j-1) [substitute]); base: D(i, 0) = i, D(0, j) = j;
same order; answer D(m, n).
1. Plain recursion — two or three branches per step: O(3^(m+n)) worst case.
2. Memoised on (i, j) — O(mn) time and space, recursion depth m+n.
3. Bottom-up table — O(mn) time and space; walk it backwards to reconstruct.
4. Two rows — each row reads only the previous one: O(mn) time, O(min(m, n)) space
   (put the shorter string on the columns). Length only; reconstruction needs the table
   (or Hirschberg's divide-and-conquer, O(n) space — mention, don't code).

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
    def best(i: int, j: int) -> int:            # LCS of a[i:] and b[j:]
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + best(i + 1, j + 1)
        return max(best(i + 1, j), best(i, j + 1))

    return best(0, 0)


def lcs_memo(a: str, b: str) -> int:
    @cache
    def best(i: int, j: int) -> int:
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + best(i + 1, j + 1)
        return max(best(i + 1, j), best(i, j + 1))

    return best(0, 0)


def lcs_table(a: str, b: str) -> list[list[int]]:
    m, n = len(a), len(b)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L


def lcs(a: str, b: str) -> str:
    L = lcs_table(a, b)
    i, j, out = len(a), len(b), []
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))


def lcs_length(a: str, b: str) -> int:
    if len(b) > len(a):
        a, b = b, a                             # shorter string on the columns
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0]
        for j, other in enumerate(b, start=1):
            cur.append(prev[j - 1] + 1 if ch == other else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def render_table(a: str, b: str) -> str:
    L = lcs_table(a, b)
    lines = ["     " + "".join(f"{ch:>3}" for ch in b)]
    for i, row in enumerate(L):
        label = a[i - 1] if i else ""
        lines.append(f"{label:<2}" + "".join(f"{v:>3}" for v in row))
    return "\n".join(lines)


# ---------------------------------------------------------------- edit distance
def edit_brute(a: str, b: str) -> int:
    def dist(i: int, j: int) -> int:            # turn a[i:] into b[j:]
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return dist(i + 1, j + 1)
        return 1 + min(dist(i + 1, j), dist(i, j + 1), dist(i + 1, j + 1))

    return dist(0, 0)


def edit_memo(a: str, b: str) -> int:
    @cache
    def dist(i: int, j: int) -> int:
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return dist(i + 1, j + 1)
        return 1 + min(dist(i + 1, j), dist(i, j + 1), dist(i + 1, j + 1))

    return dist(0, 0)


def edit_table(a: str, b: str) -> list[list[int]]:
    m, n = len(a), len(b)
    D = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        D[i][0] = i
    for j in range(n + 1):
        D[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                D[i][j] = 1 + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
    return D


def edit_distance(a: str, b: str) -> int:
    if len(b) > len(a):
        a, b = b, a                             # distance is symmetric
    prev = list(range(len(b) + 1))
    for i, ch in enumerate(a, start=1):
        cur = [i]
        for j, other in enumerate(b, start=1):
            if ch == other:
                cur.append(prev[j - 1])
            else:
                cur.append(1 + min(prev[j], cur[j - 1], prev[j - 1]))
        prev = cur
    return prev[-1]


def edit_ops(a: str, b: str) -> list[tuple[str, str, str]]:
    D = edit_table(a, b)
    i, j, ops = len(a), len(b), []
    while i or j:
        if i and j and a[i - 1] == b[j - 1] and D[i][j] == D[i - 1][j - 1]:
            ops.append(("keep", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and j and D[i][j] == D[i - 1][j - 1] + 1:
            ops.append(("sub", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            ops.append(("del", a[i - 1], ""))
            i -= 1
        else:
            ops.append(("ins", "", b[j - 1]))
            j -= 1
    return ops[::-1]


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
