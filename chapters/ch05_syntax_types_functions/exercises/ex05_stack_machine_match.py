"""
Exercise 05 — A Tiny Stack Machine With `match`              [Tier: ◆ Extended]
Chapter 05 · Pattern: structural pattern matching (3.10+) · Target time: 20 min

Problem
-------
Execute a list of text commands against an integer stack and return everything printed.

    push <int>   push the integer
    pop          discard the top value
    add | mul    pop b, pop a, push a + b (or a * b)
    dup          push a copy of the top value
    print        append the top value (without popping) to the output list

Raise ``ValueError("stack underflow")`` when a command needs more values than the stack holds
and ``ValueError("bad command: <text>")`` for anything unrecognised (including ``push`` with a
missing or non-integer argument; an integer is an optional ``-`` followed by decimal digits).

Examples
--------
>>> solve(["push 2", "push 3", "add", "print", "dup", "mul", "print"])
[5, 25]

Constraints
-----------
- 0 <= len(program) <= 10**4; tokens are separated by whitespace

Hints
-----
1. ``brute_force``: split each line into tokens and dispatch on the first token *and* on the
   number of tokens. Keep underflow checks in a small helper.
2. ``solve``: a ``match`` statement on the token list can test the shape of the list and bind
   its parts at the same time. Which pattern catches everything else?
3. Watch the operand order when you pop two values.
4. Python 3.10+ only: name the fallback you would use on older versions.

Follow-ups
----------
- Add a ``jmp <target>`` command that only matches a numeric target. Which ``match`` feature
  refines a pattern with a condition?
- Why does ``case x:`` (a bare name) match everything? How do you match a named constant?
"""
from __future__ import annotations


def _pop2(stack: list[int]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def _is_int(arg: str) -> bool:
    raise NotImplementedError("TODO")


def _parse_int(arg: str, line: str) -> int:
    raise NotImplementedError("TODO")


def brute_force(program: list[str]) -> list[int]:
    raise NotImplementedError("TODO")


def solve(program: list[str]) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    program = ["push 2", "push 3", "add", "print", "dup", "mul", "print", "push -4", "add", "print"]
    print("output      :", solve(program))
    print("brute agrees:", brute_force(program) == solve(program))
    for bad in (["add"], ["push"], ["push x"], ["jump 3"]):
        try:
            solve(bad)
        except ValueError as exc:
            print(f"{bad!s:12}-> ValueError: {exc}")


if __name__ == "__main__":
    main()
