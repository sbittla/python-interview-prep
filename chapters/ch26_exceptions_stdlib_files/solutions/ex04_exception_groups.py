"""
Exercise 04 — Exception groups and except*                     [Tier: ◆ Extended]
Chapter 26 · Pattern: report many independent failures at once · Target time: 20 min

REQUIRES PYTHON 3.11+ (ExceptionGroup and the ``except*`` syntax). On 3.10 this file does not
even compile; the backport package ``exceptiongroup`` provides the class but not the syntax.

Problem
-------
A batch import validates many records. Instead of stopping at the first bad record, collect *all*
problems and raise them together:

1. ``validate_records(records)`` checks each dict: it needs an ``"id"`` key (else ``KeyError``) and
   a numeric non-negative ``"amount"`` (else ``ValueError`` / ``TypeError``). Valid records are
   returned as a list; if any record failed, raise ``ExceptionGroup("invalid records", errors)``.
   Use ``err.add_note(f"record #{i}")`` so each error says where it came from.
2. ``triage(records)`` calls ``validate_records`` and uses ``except*`` to bucket the failures. It
   returns ``{"valid": n, "KeyError": [...notes], "ValueError": [...], "TypeError": [...]}``.
3. ``split_demo(group)`` shows the non-syntax API: ``group.split(ValueError)`` returns
   ``(matching, rest)``.

Examples
--------
>>> triage([{"id": 1, "amount": 5}, {"amount": 3}, {"id": 3, "amount": -1}])
{'valid': 0, 'KeyError': ['record #1'], 'ValueError': ['record #2'], 'TypeError': []}

(``valid`` is 0 because the group is raised — no partial result escapes; the caller decides.)

Constraints
-----------
- Every failing record must be reported exactly once.

Approach ladder
---------------
1. Brute force — raise on the first bad record; the user fixes one error per run.
2. Improved   — collect error *strings* in a list and return them; loses exception types, so the
   caller cannot handle categories differently.
3. Optimal    — collect exception objects into an ``ExceptionGroup``; callers use ``except*`` to
   handle each category, and unhandled categories still propagate.

Hints
-----
- Inside ``except* ValueError as eg``, ``eg`` is itself an ``ExceptionGroup`` holding only the
  matching leaves (``eg.exceptions``).
- Several ``except*`` clauses can run for one group; each handles its own subset.
- Notes live in ``exc.__notes__`` (a list of strings).

Follow-ups
----------
- Where else do exception groups appear? (``asyncio.TaskGroup`` raises one when tasks fail.)
- What does ``except*`` do with a plain (non-group) exception? (It wraps it in a group first.)
"""
from __future__ import annotations


def _check(record: dict) -> dict:
    if "id" not in record:
        raise KeyError("id")
    amount = record.get("amount")
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise TypeError(f"amount must be a number, got {type(amount).__name__}")
    if amount < 0:
        raise ValueError(f"amount must be >= 0, got {amount}")
    return record


def validate_records(records: list[dict]) -> list[dict]:
    valid, errors = [], []
    for i, record in enumerate(records):
        try:
            valid.append(_check(record))
        except (KeyError, TypeError, ValueError) as err:
            err.add_note(f"record #{i}")          # 3.11+
            errors.append(err)
    if errors:
        raise ExceptionGroup("invalid records", errors)   # 3.11+
    return valid


def triage(records: list[dict]) -> dict:
    report: dict = {"valid": 0, "KeyError": [], "ValueError": [], "TypeError": []}
    try:
        report["valid"] = len(validate_records(records))
    except* KeyError as eg:                     # 3.11+ syntax
        report["KeyError"] = [e.__notes__[0] for e in eg.exceptions]
    except* ValueError as eg:
        report["ValueError"] = [e.__notes__[0] for e in eg.exceptions]
    except* TypeError as eg:
        report["TypeError"] = [e.__notes__[0] for e in eg.exceptions]
    return report


def split_demo(group: BaseExceptionGroup) -> tuple[list[str], list[str]]:
    matching, rest = group.split(ValueError)
    names = lambda g: [] if g is None else sorted(type(e).__name__ for e in g.exceptions)  # noqa: E731
    return names(matching), names(rest)


def main() -> None:
    good = [{"id": 1, "amount": 5}, {"id": 2, "amount": 0.5}]
    mixed = [
        {"id": 1, "amount": 5},
        {"amount": 3},
        {"id": 3, "amount": -1},
        {"id": 4, "amount": "ten"},
        {"id": 5, "amount": -2},
    ]
    print("all good :", triage(good))
    print("mixed    :", triage(mixed))

    try:
        validate_records(mixed)
    except ExceptionGroup as group:
        print("\ngroup message:", group.message)
        for exc in group.exceptions:
            print(f"  {type(exc).__name__:<10} {exc} | notes={exc.__notes__}")
        print("split(ValueError) ->", split_demo(group))

    print("\nunhandled categories propagate:")
    try:
        try:
            validate_records(mixed)
        except* ValueError:
            print("  handled only the ValueErrors")
    except* (KeyError, TypeError) as rest:
        print("  still raised:", sorted(type(e).__name__ for e in rest.exceptions))


if __name__ == "__main__":
    main()
