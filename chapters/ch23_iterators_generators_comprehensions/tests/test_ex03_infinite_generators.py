import types


def test_examples(load):
    m = load("ex03_infinite_generators")
    assert m.take(7, m.fibonacci()) == [0, 1, 1, 2, 3, 5, 8]
    assert m.take(5, m.primes()) == [2, 3, 5, 7, 11]


def test_are_generators(load):
    m = load("ex03_infinite_generators")
    assert isinstance(m.fibonacci(), types.GeneratorType)
    assert isinstance(m.primes(), types.GeneratorType)


def test_take_edges(load):
    m = load("ex03_infinite_generators")
    assert m.take(0, m.fibonacci()) == []
    assert m.take(-3, m.fibonacci()) == []
    assert m.take(10, [1, 2]) == [1, 2]


def test_primes_against_brute_force(load):
    m = load("ex03_infinite_generators")
    brute = [n for n in range(2, 600) if all(n % d for d in range(2, n))]
    assert m.take(len(brute), m.primes()) == brute
    assert m.take(len(brute), m.primes_sieve()) == brute


def test_nth(load):
    m = load("ex03_infinite_generators")
    assert m.nth(m.fibonacci(), 10) == 55
    assert m.nth([1, 2], 5, "x") == "x"
