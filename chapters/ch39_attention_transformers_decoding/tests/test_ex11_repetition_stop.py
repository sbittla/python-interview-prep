import random

import numpy as np
import pytest


def test_repetition_penalty_signs(load):
    m = load("ex11_repetition_stop")
    z = np.array([2.0, -2.0, 1.0, 0.0])
    assert m.repetition_penalty(z, [0, 1, 1, 3], 2.0).tolist() == [1.0, -4.0, 1.0, 0.0]
    assert m.repetition_penalty(z, [], 2.0).tolist() == z.tolist()
    assert m.repetition_penalty(z, [0, 1], 1.0).tolist() == z.tolist()
    assert z.tolist() == [2.0, -2.0, 1.0, 0.0]                      # input untouched
    assert m.repetition_penalty_wrong(z, [1], 2.0)[1] == -1.0
    with pytest.raises(ValueError):
        m.repetition_penalty(z, [0], 0.5)


def test_frequency_presence(load):
    m = load("ex11_repetition_stop")
    z = np.zeros(4)
    assert m.frequency_presence(z, [0, 0, 2], 0.5, 1.0).tolist() == [-2.0, 0.0, -1.5, 0.0]
    assert m.frequency_presence(z, [], 0.5, 1.0).tolist() == [0.0] * 4


def test_no_repeat_ngram(load):
    m = load("ex11_repetition_stop")
    banned = lambda h, n: np.where(np.isinf(m.no_repeat_ngram(np.zeros(6), h, n)))[0].tolist()
    assert banned([5, 1, 2, 5, 1, 3, 5, 1], 3) == [2, 3]
    assert banned([5, 1, 2, 5, 1, 3, 5, 1], 2) == [2, 3]
    assert banned([1, 2, 3], 1) == [1, 2, 3]
    assert banned([1, 2, 3], 4) == []
    assert banned([1], 3) == []


@pytest.mark.parametrize("pieces, stops, eos, mx, text, reason", [
    (["Hel", "lo\n", "\nUs", "er:", " hi"], ["\n\nUser:"], None, 10, "Hello", "stop"),
    (["The", " end", "<eos>", "junk"], ["STOP"], "<eos>", 10, "The end", "eos"),
    (["a", "b", "c", "d"], [], None, 3, "abc", "length"),
    (["a", "b", "c"], [], None, 3, "abc", "end"),
    (["x STOP y"], ["STOP"], None, 5, "x ", "stop"),
    (["S", "T", "O", "x"], ["STOP"], None, 9, "STOx", "end"),
    (["ab", "cd"], ["cd", "bc"], None, 9, "a", "stop"),
    ([], ["X"], None, 3, "", "end"),
    (["a"], ["X"], None, 0, "", "length"),
])
def test_stream_cases(load, pieces, stops, eos, mx, text, reason):
    m = load("ex11_repetition_stop")
    chunks, got, why = m.stream_with_stops(pieces, stops, eos, mx)
    assert (got, why) == (text, reason)
    assert "".join(chunks) == got


def test_never_emits_partial_stop(load):
    m = load("ex11_repetition_stop")
    chunks, _, _ = m.stream_with_stops(["ok", "\n", "\n", "Us"], ["\n\nUser:"], None, 10)
    assert chunks[0] == "ok" and all("\n" not in c for c in chunks[:1])
    released = ""
    for c in chunks[:-1]:                                            # all but the final flush
        released += c
        assert not any(released.endswith("\n\nUser:"[:k]) for k in range(1, 7))


def test_random_against_brute(load):
    m = load("ex11_repetition_stop")
    rng = random.Random(0)
    for _ in range(400):
        pieces = ["".join(rng.choice("ab#") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(0, 6))]
        stops = ["".join(rng.choice("ab#") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(0, 2))]
        mx = rng.randint(0, 7)
        chunks, text, reason = m.stream_with_stops(pieces, stops, None, mx)
        assert (text, reason) == m.stops_brute(pieces, stops, None, mx)
        assert "".join(chunks) == text
