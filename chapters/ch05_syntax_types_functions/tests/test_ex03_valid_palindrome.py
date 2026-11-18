import pytest


@pytest.mark.parametrize("s, expected", [
    ("A man, a plan, a canal: Panama", True), ("race a car", False), ("", True), (" ", True),
    (".,", True), ("0P", False), ("ab_a", True), ("No 'x' in Nixon", True), ("abca", False),
])
def test_cases(load, s, expected):
    m = load("ex03_valid_palindrome")
    assert m.solve(s) is expected
    assert m.brute_force(s) is expected
