import random

import pytest


def test_examples(load):
    m = load("ex01_chunking")
    assert m.fixed_chunks("a b c d e f g", size=4, overlap=2) == ["a b c d", "c d e f", "e f g"]
    assert m.sentence_chunks("One two. Three four five. Six.", max_tokens=3) == [
        "One two.", "Three four five.", "Six."]


@pytest.mark.parametrize("text, size, overlap, expected", [
    ("", 4, 1, []),
    ("a b", 4, 1, ["a b"]),
    ("a b c d", 4, 0, ["a b c d"]),             # exactly one window: no empty tail
    ("a b c d e", 4, 3, ["a b c d", "b c d e"]),
    ("a b c d e f g h", 4, 0, ["a b c d", "e f g h"]),
    ("a b c", 1, 0, ["a", "b", "c"]),
])
def test_fixed_edges(load, text, size, overlap, expected):
    assert load("ex01_chunking").fixed_chunks(text, size, overlap) == expected


@pytest.mark.parametrize("size, overlap", [(0, 0), (3, 3), (3, 4), (3, -1)])
def test_fixed_rejects_bad_params(load, size, overlap):
    with pytest.raises(ValueError):
        load("ex01_chunking").fixed_chunks("a b c", size, overlap)


def test_fixed_random_invariants(load):
    m = load("ex01_chunking")
    rng = random.Random(40)
    for _ in range(300):
        words = [f"w{i}" for i in range(rng.randint(1, 40))]
        size = rng.randint(1, 10)
        overlap = rng.randint(0, size - 1)
        chunks = [c.split() for c in m.fixed_chunks(" ".join(words), size, overlap)]
        assert all(1 <= len(c) <= size for c in chunks)
        assert chunks[0][0] == words[0] and chunks[-1][-1] == words[-1]
        step = size - overlap
        for i, c in enumerate(chunks):
            assert c == words[i * step:i * step + size]
        for a, b in zip(chunks, chunks[1:]):
            assert a[-overlap:] == b[:overlap] if overlap else True
        # no window is contained in the previous one: only the last may be short
        assert all(len(c) == size for c in chunks[:-1])


def test_sentence_chunks_pack_and_hard_split(load):
    m = load("ex01_chunking")
    assert m.sentence_chunks("Short. This sentence has seven words in it.", 3) == [
        "Short.", "This sentence has", "seven words in", "it."]
    assert m.sentence_chunks("A b. C d. E f.", 4) == ["A b. C d.", "E f."]
    assert m.sentence_chunks("", 5) == []
    with pytest.raises(ValueError):
        m.sentence_chunks("a", 0)


def test_sentence_chunks_random_invariants(load):
    m = load("ex01_chunking")
    rng = random.Random(41)
    for _ in range(200):
        sents = [" ".join(f"w{rng.randint(0, 9)}" for _ in range(rng.randint(1, 8))) + "."
                 for _ in range(rng.randint(1, 8))]
        text = " ".join(sents)
        budget = rng.randint(1, 10)
        chunks = m.sentence_chunks(text, budget)
        assert all(len(c.split()) <= budget for c in chunks)
        assert " ".join(chunks).split() == text.split()           # nothing lost or duplicated
        if all(len(s.split()) <= budget for s in sents):
            assert all(c.endswith(".") for c in chunks)            # whole sentences only
            assert len(chunks) == len(m.sentence_chunks(text, budget))


def test_heading_paths(load):
    m = load("ex01_chunking")
    md = "Intro.\n# A\nAlpha one.\n## A1\nDeep.\n# B\n\n### B1\nBee."
    assert m.heading_chunks(md, 10) == [
        {"heading": "", "text": "Intro."},
        {"heading": "A", "text": "Alpha one."},
        {"heading": "A > A1", "text": "Deep."},
        {"heading": "B > B1", "text": "Bee."},
    ]
    # a sibling heading replaces, a shallower one pops the deeper level
    md2 = "# X\n## Y\ny.\n## Z\nz.\n# W\nw."
    assert [c["heading"] for c in m.heading_chunks(md2, 10)] == ["X > Y", "X > Z", "W"]
    assert m.heading_chunks("", 5) == []
    assert m.heading_chunks("#notaheading text.", 5) == [{"heading": "", "text": "#notaheading text."}]


def test_heading_chunks_respect_budget(load):
    m = load("ex01_chunking")
    md = "# T\n" + " ".join(f"Sentence number {i} is here." for i in range(10))
    chunks = m.heading_chunks(md, 12)
    assert all(len(c["text"].split()) <= 12 for c in chunks)
    assert len(chunks) == 5                                       # two 5-word sentences each


def test_char_chunks_cut_words(load):
    m = load("ex01_chunking")
    assert m.char_chunks("hello world", 4) == ["hell", "o wo", "rld"]
