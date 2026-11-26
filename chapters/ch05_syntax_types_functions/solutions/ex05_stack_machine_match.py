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

Approach ladder
---------------
1. Brute force — split each line and dispatch with an if/elif chain that checks both the
   command word and the number of tokens. O(n) time; the length checks are easy to forget.
2. Optimal    — ``match line.split():`` with sequence patterns such as ``case ["push", arg]:``
   checks the shape *and* binds names in one step. Same O(n) time, clearer and harder to get
   wrong. Requires Python 3.10+; mention a dict-of-functions dispatch table as the fallback.

Follow-ups
----------
- Add ``case ["jmp", target] if target.isdecimal():`` — like the ``push`` case, a guard refines
  a pattern; when the guard is false, matching moves on to the next case.
- Why does ``case x:`` (a bare name) match everything? A bare name is a capture pattern, not a
  comparison; compare against constants with dotted names (``Op.ADD``) or literals.
"""
from __future__ import annotations


def _pop2(stack: list[int]) -> tuple[int, int]:
    if len(stack) < 2:
        raise ValueError("stack underflow")
    b = stack.pop()
    a = stack.pop()
    return a, b


def _is_int(arg: str) -> bool:
    # isdecimal, not isdigit: "²".isdigit() is True but int("²") fails
    return arg.removeprefix("-").isdecimal()          # str.removeprefix: 3.9+


def _parse_int(arg: str, line: str) -> int:
    if not _is_int(arg):
        raise ValueError(f"bad command: {line}")
    return int(arg)


def brute_force(program: list[str]) -> list[int]:
    stack: list[int] = []
    out: list[int] = []
    for line in program:
        parts = line.split()
        if len(parts) == 2 and parts[0] == "push":
            stack.append(_parse_int(parts[1], line))
        elif parts == ["pop"]:
            if not stack:
                raise ValueError("stack underflow")
            stack.pop()
        elif parts in (["add"], ["mul"]):
            a, b = _pop2(stack)
            stack.append(a + b if parts[0] == "add" else a * b)
        elif parts in (["dup"], ["print"]):
            if not stack:
                raise ValueError("stack underflow")
            (stack if parts[0] == "dup" else out).append(stack[-1])
        else:
            raise ValueError(f"bad command: {line}")
    return out


def solve(program: list[str]) -> list[int]:
    stack: list[int] = []
    out: list[int] = []
    for line in program:
        match line.split():
            case ["push", arg] if _is_int(arg):         # guard refines the pattern
                stack.append(int(arg))
            case ["pop" | "dup" | "print" as op]:       # OR-pattern with a capture
                if not stack:
                    raise ValueError("stack underflow")
                if op == "pop":
                    stack.pop()
                else:
                    (stack if op == "dup" else out).append(stack[-1])
            case ["add" | "mul" as op]:
                a, b = _pop2(stack)
                stack.append(a + b if op == "add" else a * b)
            case _:                                     # wildcard: nothing else matched
                raise ValueError(f"bad command: {line}")
    return out


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
