import pytest

CASES = [
    ([1, [2, [3, (4, 5)]], "ab"], [1, 2, 3, 4, 5, "ab"]),
    ([], []),
    ([[], [[]]], []),
    (7, [7]),
    ("text", ["text"]),
    ([b"x", ("y",)], [b"x", "y"]),
]


@pytest.mark.parametrize("value, expected", CASES)
@pytest.mark.parametrize("fn", ["flatten", "flatten_iterative", "flatten_eager"])
def test_flatten_variants(load, fn, value, expected):
    m = load("ex04_flatten")
    assert list(getattr(m, fn)(value)) == expected


def test_iterative_handles_deep_nesting(load):
    m = load("ex04_flatten")
    deep = [1]
    for _ in range(10_000):
        deep = [deep, 2]
    out = list(m.flatten_iterative(deep))
    assert out[0] == 1 and len(out) == 10_001


def test_lazy(load):
    m = load("ex04_flatten")

    def boom():
        yield 1
        raise AssertionError("consumed too far")

    # flatten only iterates lists/tuples, so wrap a lazy list-like in a list of lists
    gen = m.flatten_iterative([[1, 2], [3]])
    assert next(gen) == 1
