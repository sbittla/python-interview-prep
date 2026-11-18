import pytest


def test_examples(load):
    m = load("ex01_fizzbuzz_rules")
    assert m.solve(5) == ["1", "2", "Fizz", "4", "Buzz"]
    assert m.solve(15)[-1] == "FizzBuzz"
    assert m.solve(7, rules=((7, "Bazz"),))[-1] == "Bazz"


@pytest.mark.parametrize("n", [0, 1, 3, 15, 31, 100])
def test_matches_brute_force(load, n):
    m = load("ex01_fizzbuzz_rules")
    assert m.solve(n) == m.brute_force(n)


def test_rule_order_and_empty_rules(load):
    m = load("ex01_fizzbuzz_rules")
    assert m.solve(15, rules=((5, "Buzz"), (3, "Fizz")))[-1] == "BuzzFizz"
    assert m.solve(3, rules=()) == ["1", "2", "3"]
    assert m.solve(0) == []
