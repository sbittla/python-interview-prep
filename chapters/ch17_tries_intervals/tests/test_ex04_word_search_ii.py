import random


def grid(rows):
    return [list(r) for r in rows]


def test_examples(load):
    m = load("ex04_word_search_ii")
    board = grid(["oaan", "etae", "ihkr", "iflv"])
    assert m.solve(board, ["oath", "pea", "eat", "rain"]) == ["eat", "oath"]
    assert board == grid(["oaan", "etae", "ihkr", "iflv"])


def test_cell_used_once_and_duplicates(load):
    m = load("ex04_word_search_ii")
    assert m.solve(grid(["ab"]), ["aba", "ab", "ab", "ba", "abb"]) == ["ab", "ba"]
    assert m.solve(grid(["a"]), ["a", "aa"]) == ["a"]
    assert m.solve(grid(["ab", "cd"]), ["abdc", "acdb", "ad"]) == ["abdc", "acdb"]


def test_word_and_its_extension(load):
    m = load("ex04_word_search_ii")
    assert m.solve(grid(["oath", "xxxs"]), ["oath", "oaths", "oat"]) == ["oat", "oath", "oaths"]


def test_random_against_brute(load):
    m = load("ex04_word_search_ii")
    rng = random.Random(11)
    for _ in range(80):
        r, c = rng.randint(1, 3), rng.randint(1, 4)
        board = [[rng.choice("ab") for _ in range(c)] for _ in range(r)]
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
                 for _ in range(rng.randint(0, 10))]
        expected = m.brute_force([row[:] for row in board], words)
        assert m.solve([row[:] for row in board], words) == expected
        assert m.solve([row[:] for row in board], words, prune=False) == expected


def test_pruning_reduces_calls(load):
    m = load("ex04_word_search_ii")
    board = [["a"] * 4 for _ in range(4)]
    words = ["a" * k for k in range(1, 7)]
    s1, s2 = {}, {}
    m.solve([row[:] for row in board], words, prune=False, stats=s1)
    m.solve([row[:] for row in board], words, prune=True, stats=s2)
    assert s2["calls"] < s1["calls"]
