import random


def test_examples(load):
    m = load("ex03_prefix_suggestions")
    pc = m.PrefixCounter()
    for w in ["car", "card", "care", "cat", "dog"]:
        assert pc.insert(w) is True
    assert pc.insert("car") is False
    assert [pc.count_prefix(p) for p in ["car", "ca", "x", "", "card", "cards"]] == [3, 4, 0, 5, 1, 0]
    products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
    assert m.suggestions(products, "mou") == [
        ["mobile", "moneypot", "monitor"], ["mobile", "moneypot", "monitor"], ["mouse", "mousepad"]]


def test_miss_stays_empty(load):
    m = load("ex03_prefix_suggestions")
    assert m.suggestions(["abc"], "xab") == [[], [], []]
    assert m.suggestions([], "a") == [[]]
    assert m.suggestions(["a"], "") == []


def test_random_against_brute(load):
    m = load("ex03_prefix_suggestions")
    rng = random.Random(5)
    for _ in range(100):
        words = sorted({"".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
                        for _ in range(rng.randint(0, 12))})
        rng.shuffle(words)
        typed = "".join(rng.choice("abc") for _ in range(rng.randint(1, 5)))
        expected = m.suggestions_brute(words, typed)
        assert m.suggestions(words, typed) == expected == m.suggestions_bisect(words, typed)
        pc = m.PrefixCounter()
        for w in words + words[:3]:
            pc.insert(w)
        for k in range(len(typed) + 1):
            assert pc.count_prefix(typed[:k]) == m.count_prefix_brute(words, typed[:k])
