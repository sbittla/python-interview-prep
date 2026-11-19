"""
Exercise 02 — RPN Evaluation and a Basic Calculator          [Tier: ★ Core]
Chapter 12 · Pattern: operand stack / operator precedence · Target time: 30 min

Problem
-------
Part A. ``eval_rpn(tokens)`` evaluates a list of tokens in Reverse Polish Notation (postfix):
integers and the operators ``+ - * /``. Division truncates toward zero (C/Java semantics,
so ``-7 / 2 == -3``). Raise ``ValueError`` for a malformed expression.

Part B. ``calculate(expr)`` evaluates an infix string of non-negative integers, ``+ - * /``,
parentheses and spaces with the usual precedence (``*`` and ``/`` bind tighter, all four are
left-associative). A unary minus may appear at the very start or right after ``(``, e.g.
``"-(2+3)"``. Division truncates toward zero. ``eval`` is not allowed. Raise ``ValueError``
for malformed input: two adjacent operators (``"2*-3"``), two adjacent operands (``"1 2"``),
a dangling operator, empty parentheses or unbalanced parentheses.

Examples
--------
>>> eval_rpn(["2", "1", "+", "3", "*"])
9
>>> eval_rpn(["4", "13", "5", "/", "+"])
6
>>> calculate("2 + 3 * (4 - 1)")
11
>>> calculate("-(7) / 2")
-3

Constraints
-----------
- 1 <= number of tokens <= 10**4; no division by zero in valid inputs.

Hints
-----
- RPN: an operand stack; an operator pops b first, then a.
- Truncating division: compute on absolute values, then fix the sign.
- Two-pass: shunting-yard to RPN (operator stack, precedence, '(' blocks popping).
- One-pass: a stack of terms to sum; * and / combine with the top; '(' recurses.

Wrong-but-tempting
------------------
- ``a // b`` for division: Python floors, so ``-7 // 2 == -4``, not ``-3``. ``int(a / b)``
  truncates but goes through a float and is wrong for large ints; use exact integer logic.
- Popping operands in the wrong order: for ``a b -`` the *second* pop is ``a``.
- Evaluating strictly left to right ignores precedence: ``2+3*4`` would give 20.
- Treating every ``-`` as binary breaks ``-(2+3)``; insert an implicit 0 or flip a sign.

Follow-ups
----------
- Add ``^`` (right-associative): pop only while the top has strictly greater precedence.
- Support variables via a dict lookup when tokenizing.
- Report the position of a syntax error (combine with exercise 01).
"""
from __future__ import annotations

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def trunc_div(a: int, b: int) -> int:
    """Integer division rounding toward zero, exact for big ints."""
    raise NotImplementedError("TODO")


def apply(op: str, a: int, b: int) -> int:
    raise NotImplementedError("TODO")


def eval_rpn(tokens: list[str]) -> int:
    raise NotImplementedError("TODO")


def tokenize(expr: str) -> list[int | str]:
    raise NotImplementedError("TODO")


def to_rpn(expr: str) -> list[str]:
    """Shunting-yard. A unary minus (at start or after '(') becomes '0 -'.

    Raises ValueError on malformed input, with the same rules as ``calculate``.
    """
    raise NotImplementedError("TODO")


def calculate_two_pass(expr: str) -> int:
    raise NotImplementedError("TODO")


def calculate(expr: str) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for tokens in (["2", "1", "+", "3", "*"], ["4", "13", "5", "/", "+"], ["-7", "2", "/"]):
        print(f"eval_rpn({' '.join(tokens)}) = {eval_rpn(tokens)}")
    print(f"python -7 // 2 = {-7 // 2}   trunc_div(-7, 2) = {trunc_div(-7, 2)}")
    for expr in ["2 + 3 * (4 - 1)", "-(7) / 2", "1 - 2 - 3", "2*(3+4)*5", "(1+(4+5+2)-3)+(6+8)",
                 "14 / 3 * 3", "-(2+3)*2"]:
        rpn = " ".join(to_rpn(expr))
        print(f"{expr:<22} rpn: {rpn:<26} = {calculate(expr):>4}  "
              f"agree={calculate(expr) == calculate_two_pass(expr)}")
    for bad in (["1", "+"], ["1", "2"]):
        try:
            eval_rpn(bad)
        except ValueError as e:
            print(f"eval_rpn({bad}) -> ValueError: {e}")
    for bad in ("2*-3", "1 2", "3 +", "()", "(1+2", "1+2)"):
        try:
            calculate(bad)
        except ValueError as e:
            print(f"calculate({bad!r}) -> ValueError: {e}")


if __name__ == "__main__":
    main()
