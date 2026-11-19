"""
Exercise 01 — The 30-Question Diagnostic and Its Auto-Grader      [Tier: ★ Core]
Chapter 03 · Pattern: data-driven grading / exec + redirect_stdout · Target time: 30 min

Take the diagnostic in the book (Section 3.1) BEFORE opening this file: the question bank
below is the test itself.

Problem
-------
The diagnostic has 30 questions in four areas:

    Q1-8    core      predict the output (syntax, types, collections)      1 point each
    Q9-16   gotchas   predict the output (aliasing, scope, late binding)   1 point each
    Q17-28  complexity pick the tightest listed Big-O (letters A-F)        1 point each
    Q29-30  coding    two small problems scored 0-4 by hidden tests        4 points each

Maximum = 8 + 8 + 12 + 8 = 36 points.

Write:
1. ``run_snippet(code)`` -> the text the snippet prints, with surrounding whitespace stripped.
   The answer key for every "predict the output" question is produced by *executing* the
   snippet, so the key can never disagree with the interpreter.
2. ``answer_key()`` -> {question_id: expected_answer} for Q1-28 (executed output for
   "predict" questions, the stored letter for "choice" questions).
3. ``grade(sheet, coding_points)`` -> {"core": n, "gotchas": n, "complexity": n, "coding": n,
   "total": n, "missed": [ids]}. ``sheet`` maps question id -> the candidate's answer text.
   Comparison ignores runs of whitespace and, for letters, case. Missing answers score 0.
   ``coding_points`` maps 29 and 30 to 0-4 (see ex03 / ex04); out-of-range values raise
   ValueError.

Examples
--------
>>> run_snippet("print(7 // -2, -7 % 3)")
'-4 2'
>>> grade({1: "-4 2"}, {29: 4, 30: 0})["total"]
5

Constraints
-----------
- Standard library only; deterministic (no ids, addresses or set ordering in any snippet).
- Each snippet runs in a fresh namespace so questions cannot leak state into each other.

Hints
-----
- contextlib.redirect_stdout(io.StringIO()) captures print() output.
- exec(code, {}) gives every snippet a fresh namespace.
- Normalise with ' '.join(text.split()); compare letters with .upper().
- Coding questions add their 0-4 points; anything below 4 counts as missed.

Follow-ups
----------
- Run snippets with ``warnings`` turned into errors so a SyntaxWarning in a snippet fails CI.
- Accept equivalent answers (e.g. ``(1, 2)`` vs ``(1,2)``) by comparing ``ast.literal_eval``
  results when both sides parse as literals.
- Randomise question order per candidate but keep ids stable for grading.
"""
from __future__ import annotations

import contextlib
import io

AREAS = {"core": range(1, 9), "gotchas": range(9, 17), "complexity": range(17, 29),
         "coding": range(29, 31)}
MAX_POINTS = {"core": 8, "gotchas": 8, "complexity": 12, "coding": 8}
CODING_MAX = 4  # points per coding problem

COMPLEXITY_OPTIONS = {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)",
                      "E": "O(n^2)", "F": "O(2^n)"}

# Q1-16: "What does this print?"  The answer is NOT stored: it is produced by running the code.
PREDICT = {
    1: "print(7 // -2, -7 % 3)",
    2: "print(round(2.5), round(3.5))",
    3: "x = [1, 2, 3]\nprint(x[::-1][1:], x[-5:2])",
    4: "print(0.1 + 0.2 == 0.3, abs(0.1 + 0.2 - 0.3) < 1e-9)",
    5: 'd = {"a": 1}\nd.setdefault("a", 5)\nd.setdefault("b", 7)\nprint(d)',
    6: 'from collections import Counter\nprint(Counter("banana").most_common(2))',
    7: 'print(sorted(["bb", "a", "ccc", "dd"], key=len))',
    8: "a, *b, c = range(5)\nprint(a, b, c)",
    9: "def f(x, acc=[]):\n    acc.append(x)\n    return acc\nf(1)\nprint(f(2))",
    10: "grid = [[0] * 2] * 2\ngrid[0][0] = 1\nprint(grid)",
    11: "fs = [lambda: i for i in range(3)]\nprint([f() for f in fs])",
    12: 'print(True + True, bool("False"), bool(""))',
    13: "g = (x * x for x in range(3))\nprint(sum(g), sum(g))",
    14: ("t = (1, [2])\ntry:\n    t[1] += [3]\nexcept TypeError:\n"
         "    print('TypeError', t)"),
    15: ("x = 1\ndef f():\n    print(x)\n    x = 2\ntry:\n    f()\n"
         "except Exception as e:\n    print(type(e).__name__)"),
    16: "a = [1, 2, 3]\nb = a\na += [4]\nc = a\na = a + [5]\nprint(b, c is b, a)",
}

# Q17-28: "Tightest listed worst-case time (or space) bound, unless stated?"  Letters refer to COMPLEXITY_OPTIONS.
CHOICE = {
    17: ("`x in lst` for a list of n items", "C"),
    18: ("`x in st` for a set of n items (average case)", "A"),
    19: ("`lst.pop(0)` on a list of n items", "C"),
    20: ("`dq.popleft()` on a collections.deque of n items", "A"),
    21: ("`sorted(lst)` on n items", "D"),
    22: ("`bisect.bisect_left(lst, x)` on a sorted list of n items", "B"),
    23: ("`for i in range(n): for j in range(i): total += 1`", "E"),
    24: ("`heapq.heappush(h, x)` on a heap of n items", "B"),
    25: ("naive recursive `fib(n) = fib(n-1) + fib(n-2)`", "F"),
    26: ("`i = 1; while i < n: i *= 2`", "B"),
    27: ("`for i in range(n): total += sum(lst[i:])`", "E"),
    28: ("extra SPACE of recursive DFS on a path-shaped tree of n nodes", "C"),
}

CODING = {
    29: "first_unique(ids): first value that occurs exactly once, else None (ex03)",
    30: "merge(intervals): merge overlapping/touching closed intervals (ex04)",
}


def run_snippet(code: str) -> str:
    """Execute ``code`` in a fresh namespace and return what it printed (stripped)."""
    raise NotImplementedError("TODO")


def answer_key() -> dict[int, str]:
    raise NotImplementedError("TODO")


def _norm(text: str) -> str:
    return " ".join(str(text).split())


def area_of(qid: int) -> str:
    for area, ids in AREAS.items():
        if qid in ids:
            return area
    raise ValueError(f"no question {qid}")


def grade(sheet: dict[int, str], coding_points: dict[int, int]) -> dict:
    raise NotImplementedError("TODO")


# A plausible sheet from a candidate who knows Python basics but not the traps.
SAMPLE_SHEET = {
    1: "-4 2", 2: "3 4", 3: "[2, 1] [1, 2]", 4: "False True", 5: "{'a': 1, 'b': 7}",
    6: "[('a', 3), ('n', 2)]", 7: "['a', 'bb', 'dd', 'ccc']", 8: "0 [1, 2, 3] 4",
    9: "[2]", 10: "[[1, 0], [1, 0]]", 11: "[0, 1, 2]", 12: "2 True False",
    13: "5 5", 14: "TypeError (1, [2])", 15: "UnboundLocalError", 16: "[1, 2, 3, 4] True [1, 2, 3, 4, 5]",
    17: "C", 18: "a", 19: "A", 20: "A", 21: "D", 22: "B", 23: "E", 24: "B", 25: "F",
    26: "B", 27: "C", 28: "B",
}
SAMPLE_CODING = {29: 4, 30: 2}


def main() -> None:
    key = answer_key()
    print("Answer key, Q1-16 (produced by executing each snippet):")
    for qid in PREDICT:
        print(f"  Q{qid:<2} {area_of(qid):<8} {key[qid]}")
    print("Answer key, Q17-28:")
    print("  " + "  ".join(f"Q{q}={key[q]}" for q in CHOICE))
    print()
    result = grade(SAMPLE_SHEET, SAMPLE_CODING)
    print("Sample sheet:")
    for area in AREAS:
        print(f"  {area:<10} {result[area]:>2}/{MAX_POINTS[area]}")
    print(f"  {'total':<10} {result['total']:>2}/{sum(MAX_POINTS.values())}")
    print(f"  missed: {result['missed']}")
    try:
        grade({}, {29: 5})
    except ValueError as exc:
        print("Bad coding points ->", exc)


if __name__ == "__main__":
    main()
