import random

import pytest


def test_examples(load):
    m = load("ex02_expression_evaluation")
    assert m.eval_rpn(["2", "1", "+", "3", "*"]) == 9
    assert m.eval_rpn(["4", "13", "5", "/", "+"]) == 6
    assert m.calculate("2 + 3 * (4 - 1)") == 11
    assert m.calculate("-(7) / 2") == -3


@pytest.mark.parametrize("a, b, expected", [(7, 2, 3), (-7, 2, -3), (7, -2, -3), (-7, -2, 3),
                                            (0, 5, 0), (6, 3, 2)])
def test_truncating_division(load, a, b, expected):
    m = load("ex02_expression_evaluation")
    assert m.trunc_div(a, b) == expected
    assert m.eval_rpn([str(a), str(b), "/"]) == expected


@pytest.mark.parametrize("expr, expected", [
    ("42", 42), ("1 - 2 - 3", -4), ("2*3+4", 10), ("2+3*4", 14), ("(2+3)*4", 20),
    ("-(2+3)", -5), ("(-4)*2", -8), ("((((7))))", 7), ("100 / 7 / 2", 7), ("1-(-2)", 3),
])
def test_calculator_cases(load, expr, expected):
    m = load("ex02_expression_evaluation")
    assert m.calculate(expr) == expected
    assert m.calculate_two_pass(expr) == expected


@pytest.mark.parametrize("tokens", [["+"], ["1", "+"], ["1", "2"], []])
def test_malformed_rpn(load, tokens):
    with pytest.raises(ValueError):
        load("ex02_expression_evaluation").eval_rpn(tokens)


@pytest.mark.parametrize("expr", ["2*-3", "1 2", "3 +", "+3", "()", "(1+2", "1+2)", "", "2 (3)",
                                  "(-)", "1 - - 2"])
def test_calculate_rejects_malformed(load, expr):
    m = load("ex02_expression_evaluation")
    with pytest.raises(ValueError):
        m.calculate(expr)
    with pytest.raises(ValueError):
        m.calculate_two_pass(expr)


@pytest.mark.parametrize("expr", ["2 2-", "/1 1", "2(*2)", "1(2)", "(1)2", "(*1)"])
def test_two_pass_rejects_malformed(load, expr):
    m = load("ex02_expression_evaluation")
    for fn in (m.calculate, m.calculate_two_pass):
        with pytest.raises(ValueError):
            fn(expr)


def _outcome(fn, expr):
    try:
        return ("ok", fn(expr))
    except (ValueError, ZeroDivisionError):
        # one pass may hit a zero divisor before a later syntax error, so the
        # exception type can differ; only "both raise" is required
        return ("raise", None)


def test_fuzz_one_pass_and_two_pass_agree(load):
    m = load("ex02_expression_evaluation")
    rng = random.Random(41)
    ok = 0
    for _ in range(5000):
        expr = "".join(rng.choice("0123456789+-*/() ") for _ in range(rng.randint(0, 10)))
        a, b = _outcome(m.calculate, expr), _outcome(m.calculate_two_pass, expr)
        assert a == b, expr
        ok += a[0] == "ok"
    assert ok > 100                             # the fuzz also exercises valid input


def test_bad_character(load):
    with pytest.raises(ValueError):
        load("ex02_expression_evaluation").calculate("2 $ 3")


def _expr(rng, depth, ops):
    if depth == 0 or rng.random() < 0.3:
        return str(rng.randint(0, 9))
    left, right = _expr(rng, depth - 1, ops), _expr(rng, depth - 1, ops)
    text = f"{left}{rng.choice(ops)}{right}"
    return f"({text})" if rng.random() < 0.5 else text


def test_random_against_eval(load):
    m = load("ex02_expression_evaluation")
    rng = random.Random(3)
    for _ in range(300):
        e = _expr(rng, 4, "+-*")
        assert m.calculate(e) == m.calculate_two_pass(e) == eval(e), e


def test_random_division_one_pass_vs_two_pass(load):
    m = load("ex02_expression_evaluation")
    rng = random.Random(4)
    for _ in range(300):
        e = _expr(rng, 4, "+-*/")
        try:
            expected = m.calculate_two_pass(e)
        except ZeroDivisionError:
            with pytest.raises(ZeroDivisionError):
                m.calculate(e)
            continue
        assert m.calculate(e) == expected, e
