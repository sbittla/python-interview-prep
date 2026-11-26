import pytest


def test_example(load):
    m = load("ex05_stack_machine_match")
    prog = ["push 2", "push 3", "add", "print", "dup", "mul", "print"]
    assert m.solve(prog) == [5, 25]
    assert m.brute_force(prog) == [5, 25]


def test_order_of_operands_and_pop(load):
    m = load("ex05_stack_machine_match")
    assert m.solve(["push 1", "push 2", "pop", "print", "push -3", "mul", "print"]) == [1, -3]
    assert m.solve([]) == []
    assert m.solve(["  push   7 ", "print"]) == [7]


@pytest.mark.parametrize("prog, message", [
    (["add"], "stack underflow"), (["push 1", "mul"], "stack underflow"), (["pop"], "stack underflow"),
    (["print"], "stack underflow"), (["push"], "bad command: push"), (["push x"], "bad command: push x"),
    (["jump 3"], "bad command: jump 3"), (["push --5"], "bad command: push --5"),
    (["push 1_000"], "bad command: push 1_000"), (["push ²"], "bad command: push ²"),
    (["push -"], "bad command: push -"), (["add 1"], "bad command: add 1"), ([""], "bad command: "),
])
def test_errors(load, prog, message):
    m = load("ex05_stack_machine_match")
    for fn in (m.solve, m.brute_force):
        with pytest.raises(ValueError) as info:
            fn(prog)
        assert str(info.value) == message
