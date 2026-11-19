import pytest

CATALAN = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]


def test_examples(load):
    m = load("ex02_count_bst_shapes")
    assert m.count_memo(3) == 5
    assert len(m.generate(3)) == 5


@pytest.mark.parametrize("n", range(11))
def test_three_counts_agree(load, n):
    m = load("ex02_count_bst_shapes")
    assert m.count_memo(n) == m.count_bottom_up(n) == CATALAN[n]
    if n <= 8:
        assert m.count_naive(n) == CATALAN[n]


def test_naive_call_count_and_memo(load):
    m = load("ex02_count_bst_shapes")
    calls = [0]
    m.count_naive(10, calls)
    assert calls[0] == 5 * 3 ** 8
    m.count_memo.cache_clear()
    m.count_memo(10)
    assert m.count_memo.cache_info().misses == 11
    assert m.count_bottom_up(19) == 1_767_263_190


@pytest.mark.parametrize("n", range(0, 7))
def test_generate_valid_distinct(load, n):
    m = load("ex02_count_bst_shapes")
    tn = load("treenode")
    trees = m.generate(n)
    assert len(trees) == CATALAN[n]
    shapes = {tuple(tn.to_level(t)) for t in trees}
    assert len(shapes) == CATALAN[n]
    for t in trees:
        assert tn.inorder_values(t) == list(range(1, n + 1))
