import pytest


def test_compose_and_pipeline(load):
    m = load("ex01_higher_order")
    assert m.compose(str, abs)(-7) == "7"
    assert m.pipeline(abs, str)(-7) == "7"
    inc, dbl = (lambda x: x + 1), (lambda x: x * 2)
    assert m.compose(inc, dbl)(5) == 11          # inc(dbl(5)): right to left
    assert m.pipeline(inc, dbl)(5) == 12         # dbl(inc(5)): left to right
    assert m.compose()(42) == 42 and m.pipeline()("x") == "x"


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 2), (3, 8), (10, 1024)])
def test_apply_n(load, n, expected):
    assert load("ex01_higher_order").apply_n(lambda x: x * 2, n)(1) == expected


def test_apply_n_negative(load):
    with pytest.raises(ValueError):
        load("ex01_higher_order").apply_n(abs, -1)


def test_dispatch(load):
    m = load("ex01_higher_order")
    lines = ["add 2 3", "sub 2 9", "mul -4 5", "neg 4", "abs -6", "pow 2 3"]
    expected = [5, -7, -20, -4, 6, "error: unknown op 'pow'"]
    assert m.run_commands(lines) == expected
    assert m.brute_force_run(lines) == expected
    assert m.run_commands([]) == []
