import pytest


@pytest.mark.parametrize("x, expected", [
    (123, 321), (-123, -321), (-120, -21), (0, 0), (5, 5), (1534236469, 0),
    (-2147483412, -2143847412), (2**31 - 1, 0), (-(2**31), 0), (1463847412, 2147483641),
    (10**20, 1),
])
def test_cases(load, x, expected):
    m = load("ex02_reverse_integer")
    assert m.solve(x) == expected
    assert m.brute_force(x) == expected
