import pytest

FREQS = {"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}


def test_examples(load):
    m = load("ex09_huffman")
    assert m.cost(FREQS) == 224
    assert m.cost({"x": 7}) == 7


def test_codes_are_prefix_free_and_optimal(load):
    m = load("ex09_huffman")
    codes = m.huffman_codes(FREQS)
    words = list(codes.values())
    for a in words:
        for b in words:
            if a != b:
                assert not b.startswith(a)
    assert sum(FREQS[s] * len(codes[s]) for s in FREQS) == m.cost(FREQS)


@pytest.mark.parametrize("text", ["abacabadf", "f", "fffff", "edcba"])
def test_round_trip(load, text):
    m = load("ex09_huffman")
    codes = m.huffman_codes(FREQS)
    assert m.decode(m.encode(text, codes), codes) == text


def test_single_symbol(load):
    assert load("ex09_huffman").huffman_codes({"z": 4}) == {"z": "0"}
