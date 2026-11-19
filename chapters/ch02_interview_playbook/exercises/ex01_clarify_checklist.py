"""
Exercise 01 — Clarifying-Question Checklist Builder        [Tier: ◆ Extended]
Chapter 02 · Pattern: interview method (clarify) · Target time: 20 min

Problem
-------
Before solving, a candidate should ask about input size, types, duplicates,
empty inputs and sortedness. Turn that habit into code.

A problem signature is described as a dict mapping each parameter name to a
type tag. Supported tags:

    "int", "str", "list[int]", "list[str]", "sorted list[int]",
    "matrix[int]", "graph"

Write two functions:

- checklist(spec) -> list of (category, question) pairs, in the order you
  would ask them: first the three universal questions (size, output, may I
  mutate), then per-parameter questions in parameter order. No question text
  appears twice.
- audit(spec, asked) -> sorted list of categories that the checklist covers but
  the candidate's `asked` set does not.

Categories: "size", "output", "mutation", "types", "duplicates", "empty",
"sortedness", "range", "shape", "structure".

Examples
--------
>>> [c for c, _ in checklist({"n": "int"})]
['size', 'output', 'mutation', 'range']
>>> audit({"nums": "list[int]"}, {"size", "empty"})
['duplicates', 'mutation', 'output', 'range', 'sortedness']

Constraints
-----------
- Unknown tags raise ValueError naming the tag.
- Deterministic: the same spec always yields the same list.

Hints
-----
- Keep the rules as data (tag -> list of (category, template)); the code is a
  loop that formats "{p}" with the parameter name.
- Track emitted texts in a set to skip duplicates while keeping list order.
- audit = categories covered by checklist(spec) minus `asked`, sorted.

Follow-ups
----------
- Rank questions by how much they change the algorithm (size and sortedness
  first) and cap the list at k questions for a short round.
- Add a "string" alphabet question (ASCII vs Unicode) only when a str appears.
"""
from __future__ import annotations

UNIVERSAL = [
    ("size", "How large can the input get? (sets the target complexity)"),
    ("output", "What should I return when there is no valid answer?"),
    ("mutation", "May I modify the input in place, or must it stay unchanged?"),
]

RULES: dict[str, list[tuple[str, str]]] = {
    "int": [("range", "Can {p} be zero or negative? What is its maximum?")],
    "str": [
        ("empty", "Can {p} be empty?"),
        ("types", "Is {p} ASCII only, or any Unicode? Is case significant?"),
    ],
    "list[int]": [
        ("empty", "Can {p} be empty or have one element?"),
        ("duplicates", "Can {p} contain duplicates? Do they count separately?"),
        ("range", "Can values in {p} be negative or zero?"),
        ("sortedness", "Is {p} sorted? Does output order matter?"),
    ],
    "list[str]": [
        ("empty", "Can {p} be empty, or contain empty strings?"),
        ("duplicates", "Can {p} contain duplicate strings?"),
        ("types", "Are strings in {p} lowercase ASCII only?"),
    ],
    "sorted list[int]": [
        ("empty", "Can {p} be empty or have one element?"),
        ("sortedness", "Is {p} ascending, and strictly or non-strictly?"),
        ("duplicates", "Can {p} contain duplicates?"),
    ],
    "matrix[int]": [
        ("empty", "Can {p} have zero rows or zero columns?"),
        ("shape", "Is {p} rectangular? Is it always square?"),
        ("range", "Can cells of {p} be negative?"),
    ],
    "graph": [
        ("structure", "Is {p} directed? Can it have cycles or self-loops?"),
        ("structure", "Is {p} connected? Are edges weighted?"),
        ("empty", "Can {p} have zero nodes or isolated nodes?"),
    ],
}


def checklist(spec: dict[str, str]) -> list[tuple[str, str]]:
    raise NotImplementedError("TODO")


def audit(spec: dict[str, str], asked: set[str]) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    spec = {"nums": "list[int]", "target": "int"}
    print("Signature: count_pairs(nums: list[int], target: int)")
    for i, (category, question) in enumerate(checklist(spec), 1):
        print(f"{i}. [{category}] {question}")
    asked = {"size", "duplicates"}
    print(f"\nCandidate asked about {sorted(asked)}")
    print(f"Missed categories: {audit(spec, asked)}")
    try:
        checklist({"x": "tuple"})
    except ValueError as exc:
        print(f"Unknown tag -> ValueError: {exc}")


if __name__ == "__main__":
    main()
