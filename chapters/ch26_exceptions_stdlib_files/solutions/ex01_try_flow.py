"""
Exercise 01 — Trace try/except/else/finally                    [Tier: ★ Core]
Chapter 26 · Pattern: control flow of exceptions · Target time: 15 min

Problem
-------
Interviewers love asking "what runs, and in which order?" Write small functions that make the
order of ``try`` / ``except`` / ``else`` / ``finally`` observable:

1. ``run_steps(value, divisor)`` divides ``value`` by ``divisor`` and returns a list of the
   block names that executed, followed by ``"result=<result>"``. A ``ZeroDivisionError`` or a
   ``TypeError`` must be caught and the result reported as ``None``.
2. ``parse_int_or_default(text, default)`` returns ``int(text)`` or ``default`` when the text is
   not a valid integer. Catch only the exception you expect.
3. ``exception_lineage(exc)`` returns the names of the classes in ``type(exc).__mro__``, so you can
   see where a built-in exception sits in the hierarchy.
4. ``return_then_finally(log)`` returns ``"from try"`` from inside ``try`` while the ``finally``
   block appends ``"finally ran"`` to ``log``; it shows that ``finally`` runs even on ``return``.

Examples
--------
>>> run_steps(10, 2)
['try', 'else', 'finally', 'result=5.0']
>>> run_steps(10, 0)
['try', 'except ZeroDivisionError', 'finally', 'result=None']
>>> parse_int_or_default("x", -1)
-1
>>> exception_lineage(KeyError("k"))
['KeyError', 'LookupError', 'Exception', 'BaseException', 'object']

Constraints
-----------
- Never use a bare ``except:``; never catch ``BaseException``.
- Keep the ``try`` block as small as possible.

Approach ladder
---------------
1. Brute force — wrap everything in ``try: ... except Exception: pass``. It "works" but hides bugs
   (a typo becomes a silent ``None``) and swallows errors you did not anticipate.
2. Improved   — catch specific exception types; still put follow-up work inside ``try``.
3. Optimal    — tiny ``try`` that contains only the risky call, specific ``except`` clauses, success
   work in ``else`` (so its own errors are not mistaken for the guarded failure), cleanup in
   ``finally``. Each rung reduces the set of errors you accidentally catch.

Hints
-----
- ``else`` runs only when the ``try`` block raised nothing.
- ``finally`` runs on success, on a caught exception, on an uncaught exception and on ``return``.
- ``int("3.5")`` raises ``ValueError``; ``int(None)`` raises ``TypeError``.

Follow-ups
----------
- What happens if ``finally`` itself raises? (It replaces the in-flight exception.)
- Why is ``return`` inside ``finally`` a bad idea? (It silently discards exceptions; Python 3.14
  emits a ``SyntaxWarning`` for it — PEP 765.)
"""
from __future__ import annotations


def run_steps(value, divisor) -> list[str]:
    trace: list[str] = []
    result = None
    try:
        trace.append("try")
        result = value / divisor          # the only line that can fail
    except ZeroDivisionError:
        trace.append("except ZeroDivisionError")
    except TypeError:
        trace.append("except TypeError")
    else:
        trace.append("else")              # runs only when try succeeded
    finally:
        trace.append("finally")           # always runs
    trace.append(f"result={result}")
    return trace


def parse_int_or_default(text, default: int) -> int:
    try:
        return int(text)
    except (ValueError, TypeError):       # only the failures we expect
        return default


def exception_lineage(exc: BaseException) -> list[str]:
    return [cls.__name__ for cls in type(exc).__mro__]


def return_then_finally(log: list[str]) -> str:
    try:
        log.append("try body")
        return "from try"
    finally:
        log.append("finally ran")         # executes before the caller receives the value


def main() -> None:
    print("== run_steps ==")
    for args in [(10, 2), (10, 0), (10, "2")]:
        print(f"{args!r:>12} -> {run_steps(*args)}")

    print("\n== parse_int_or_default ==")
    for text in ["42", "-7", "3.5", "", None]:
        print(f"{text!r:>6} -> {parse_int_or_default(text, -1)}")

    print("\n== exception_lineage ==")
    for exc in [KeyError("k"), ZeroDivisionError(), FileNotFoundError(), KeyboardInterrupt()]:
        print(" -> ".join(exception_lineage(exc)))

    print("\n== return_then_finally ==")
    log: list[str] = []
    value = return_then_finally(log)
    print("returned:", value)
    print("log:", log)


if __name__ == "__main__":
    main()
