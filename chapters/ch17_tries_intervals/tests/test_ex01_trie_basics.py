import random


def test_examples(load):
    m = load("ex01_trie_basics")
    t = m.Trie()
    for w in ["apple", "app", "apply"]:
        t.insert(w)
    assert (t.search("app"), t.search("ap"), t.starts_with("ap"), t.node_count()) == (True, False, True, 7)
    assert t.delete("apple") and t.node_count() == 6 and t.search("apply")
    assert not t.search("apple") and t.starts_with("appl")


def test_delete_absent_and_prefix(load):
    t = load("ex01_trie_basics").Trie()
    t.insert("abc")
    assert t.delete("ab") is False and t.delete("abcd") is False and t.delete("x") is False
    assert t.node_count() == 4
    assert t.delete("abc") is True and t.delete("abc") is False
    assert t.node_count() == 1 and not t.starts_with("a")


def test_duplicate_insert_is_idempotent(load):
    t = load("ex01_trie_basics").Trie()
    t.insert("ab")
    t.insert("ab")
    assert t.delete("ab") and not t.search("ab") and t.node_count() == 1


def test_random_against_set_and_pruning_invariant(load):
    m = load("ex01_trie_basics")
    rng = random.Random(17)
    for _ in range(60):
        t, base = m.Trie(), m.SetBaseline()
        for _ in range(60):
            w = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
            op = rng.random()
            if op < 0.5:
                t.insert(w)
                base.insert(w)
            elif op < 0.8:
                assert t.delete(w) == base.delete(w)
            else:
                assert t.search(w) == base.search(w)
                assert t.starts_with(w) == base.starts_with(w)
        prefixes = {w[:k] for w in base.words for k in range(1, len(w) + 1)}
        assert t.node_count() == 1 + len(prefixes)        # pruning leaves no dead nodes
        assert t.words() == sorted(base.words)
        for p in ["a", "b", "ab", "abc", "ca"]:
            assert t.starts_with(p) == base.starts_with(p)


def test_array_trie_matches(load):
    m = load("ex01_trie_basics")
    rng = random.Random(3)
    t, a = m.Trie(), m.ArrayTrie()
    for _ in range(200):
        w = "".join(rng.choice("xyz") for _ in range(rng.randint(1, 5)))
        t.insert(w)
        a.insert(w)
    for _ in range(200):
        q = "".join(rng.choice("xyz") for _ in range(rng.randint(1, 6)))
        assert t.search(q) == a.search(q) and t.starts_with(q) == a.starts_with(q)
