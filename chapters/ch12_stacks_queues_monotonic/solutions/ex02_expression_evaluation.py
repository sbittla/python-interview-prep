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

Approach ladder
---------------
1. Two passes — shunting-yard converts infix to RPN with an operator stack (pop while the top
   has precedence >= the incoming operator; ``(`` blocks popping), then ``eval_rpn`` folds
   the RPN with an operand stack. O(n) time, O(n) space. Easy to reason about, two
   data structures.
2. One pass   — keep a stack of *terms* that will be summed. ``+x`` pushes ``x``, ``-x``
   pushes ``-x``, ``*x`` / ``/x`` replace the top with ``top*x`` / ``trunc(top/x)``. A
   ``(`` recurses and returns the parenthesised value as one operand. O(n) time, O(depth)
   recursion. Why move up: one scan, no intermediate token list, and it is the version
   interviewers expect for "basic calculator".

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
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def apply(op: str, a: int, b: int) -> int:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    return trunc_div(a, b)


def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    for tok in tokens:
        if tok in PREC:
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {tok!r}")
            b = stack.pop()                    # right operand comes off first
            a = stack.pop()
            stack.append(apply(tok, a, b))
        else:
            stack.append(int(tok))
    if len(stack) != 1:
        raise ValueError("malformed expression")
    return stack[0]


def tokenize(expr: str) -> list[int | str]:
    tokens: list[int | str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
            continue
        if ch in PREC or ch in "()":
            tokens.append(ch)
        elif not ch.isspace():
            raise ValueError(f"bad character {ch!r} at {i}")
        i += 1
    return tokens


def to_rpn(expr: str) -> list[str]:
    """Shunting-yard. A unary minus (at start or after '(') becomes '0 -'.

    Raises ValueError on malformed input, with the same rules as ``calculate``.
    """
    out: list[str] = []
    ops: list[str] = []
    prev: int | str | None = None
    expect_operand = True                      # a number or '(' must come next
    for tok in tokenize(expr):
        if isinstance(tok, int) or tok == "(":
            if not expect_operand:
                raise ValueError("missing operator between operands")
            if tok == "(":
                ops.append(tok)
            else:
                out.append(str(tok))
                expect_operand = False
        elif tok == ")":
            if expect_operand:
                raise ValueError("unexpected ')'")
            while ops and ops[-1] != "(":
                out.append(ops.pop())
            if not ops:
                raise ValueError("unmatched ')'")
            ops.pop()
        else:
            if expect_operand:
                if not (tok == "-" and (prev is None or prev == "(")):
                    raise ValueError(f"unexpected operator {tok!r}")
                out.append("0")                # unary minus: 0 - x
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[tok]:
                out.append(ops.pop())
            ops.append(tok)
            expect_operand = True
        prev = tok
    if expect_operand:
        raise ValueError("expression ends without an operand")
    while ops:
        if ops[-1] == "(":
            raise ValueError("unmatched '('")
        out.append(ops.pop())
    return out


def calculate_two_pass(expr: str) -> int:
    return eval_rpn(to_rpn(expr))


def calculate(expr: str) -> int:
    tokens = tokenize(expr)
    pos = 0

    def parse(nested: bool) -> int:            # evaluates until ')' or end
        nonlocal pos
        terms: list[int] = []                  # the answer is sum(terms)
        op = "+"
        expect_operand = True
        at_start = True                        # a unary minus is allowed only here
        while pos < len(tokens):
            tok = tokens[pos]
            pos += 1
            if tok == ")":
                if not nested:
                    raise ValueError("unmatched ')'")
                break
            if isinstance(tok, str) and tok in PREC:
                if expect_operand and not (at_start and tok == "-"):
                    raise ValueError(f"unexpected operator {tok!r}")
                op, at_start, expect_operand = tok, False, True
                continue
            if not expect_operand:
                raise ValueError("missing operator between operands")
            x = parse(True) if tok == "(" else tok
            at_start, expect_operand = False, False
            if op == "+":
                terms.append(x)
            elif op == "-":
                terms.append(-x)
            elif op == "*":
                terms.append(terms.pop() * x)
            else:
                terms.append(trunc_div(terms.pop(), x))
        else:
            if nested:
                raise ValueError("unmatched '('")
        if expect_operand:
            raise ValueError("expression ends without an operand")
        return sum(terms)

    return parse(False)


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
