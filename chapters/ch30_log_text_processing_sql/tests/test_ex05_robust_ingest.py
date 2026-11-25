from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.mark.parametrize("obj, reason", [
    ({"user": "a", "amount": 3, "ts": 1}, None),
    ({"user": "a", "amount": 0, "ts": 1, "extra": [1]}, None),
    ({"user": "a", "amount": True, "ts": 1}, "amount must be int"),
    ({"user": "a", "amount": "3", "ts": 1}, "amount must be int"),
    ({"user": "a", "amount": 3.0, "ts": 1}, "amount must be int"),
    ({"user": 7, "amount": 3, "ts": 1}, "user must be str"),
    ({"amount": 3, "ts": 1}, "missing user"),
    ({"user": "a", "amount": -1, "ts": 1}, "amount < 0"),
    ([1, 2], "not an object"),
    ("text", "not an object"),
    (None, "not an object"),
])
def test_validate(load, obj, reason):
    assert load("ex05_robust_ingest").validate(obj) == reason


def test_example(load):
    m = load("ex05_robust_ingest")
    assert m.ingest([b'{"user": "a", "amount": 1, "ts": 2}', b"{oops"], 0.5) == (
        [{"user": "a", "amount": 1, "ts": 2}], [(2, "bad json")])


def test_utf8_blank_and_whitespace(load):
    m = load("ex05_robust_ingest")
    good, bad = m.ingest([b"\n", b'  {"user": "a", "amount": 1, "ts": 2}  \r\n',
                          b'{"user": "\xff", "amount": 1, "ts": 2}'], 0.9)
    assert good == [{"user": "a", "amount": 1, "ts": 2}] and bad == [(3, "bad utf-8")]


def test_error_budget(load):
    m = load("ex05_robust_ingest")
    lines = [b'{"user": "a", "amount": 1, "ts": 2}', b"x", b"y"]
    with pytest.raises(m.TooManyErrors):
        m.ingest(lines, 0.5)                    # 2 of 3 bad
    good, bad = m.ingest(lines, 0.7)
    assert len(good) == 1 and [n for n, _ in bad] == [2, 3]
    assert m.ingest([], 0.0) == ([], [])        # no division by zero
    assert m.ingest([b"   "], 0.0) == ([], [])  # blank lines do not count


def test_data_file(load):
    m = load("ex05_robust_ingest")
    with open(DATA / "payments.jsonl", "rb") as f:
        good, bad = m.ingest(f, 0.5)
    assert len(good) == 9 and sum(g["amount"] for g in good) == 440
    assert bad == [(3, "amount must be int"), (4, "bad json"), (6, "missing amount"),
                   (7, "amount must be int"), (8, "amount < 0"), (9, "not an object"),
                   (10, "bad utf-8")]
