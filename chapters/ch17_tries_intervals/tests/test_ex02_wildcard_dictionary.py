import random

import pytest


@pytest.mark.parametrize("pattern, expected", [
    ("pad", False), ("bad", True), (".ad", True), ("b..", True), ("b.", False),
    ("...", True), ("....", False), ("ba", False), ("bads", False), ("..d", True), ("z..", False),
])
def test_examples(load, pattern, expected):
    d = load("ex02_wildcard_dictionary").WordDictionary()
    for w in ["bad", "dad", "mad"]:
        d.add_word(w)
    assert d.search(pattern) is expected


def test_empty_dictionary(load):
    d = load("ex02_wildcard_dictionary").WordDictionary()
    assert d.search("a") is False and d.search(".") is False


def test_random_rungs_agree(load):
    m = load("ex02_wildcard_dictionary")
    rng = random.Random(42)
    for _ in range(50):
        dicts = [m.WordDictionary(), m.BruteDictionary(), m.LengthBucketDictionary()]
        for _ in range(rng.randint(0, 15)):
            w = "".join(rng.choice("ab") for _ in range(rng.randint(1, 4)))
            for d in dicts:
                d.add_word(w)
        for _ in range(30):
            p = "".join(rng.choice("ab.") for _ in range(rng.randint(1, 5)))
            answers = {d.search(p) for d in dicts}
            assert len(answers) == 1, p
