import pytest


def test_examples(load):
    m = load("ex02_dynamic_array")
    assert m.total_copies(8, m.double) == 7
    assert m.total_copies(8, m.add_k(2)) == 16
    assert m.accounting_min_balance(1000, 3) >= 0


@pytest.mark.parametrize("n, expected", [(0, 0), (1, 0), (2, 1), (3, 3), (5, 7), (9, 15),
                                         (1024, 1023), (1025, 2047)])
def test_doubling_copies(load, n, expected):
    m = load("ex02_dynamic_array")
    assert m.total_copies(n, m.double) == expected


def test_doubling_linear_and_add_k_quadratic(load):
    m = load("ex02_dynamic_array")
    assert all(m.total_copies(n, m.double) < 2 * n for n in range(1, 600))
    assert m.total_copies(2000, m.add_k(1)) == 2000 * 1999 // 2
    ratio = m.total_copies(4000, m.add_k(10)) / m.total_copies(2000, m.add_k(10))
    assert 3.9 < ratio < 4.1


def test_array_behaviour(load):
    m = load("ex02_dynamic_array")
    arr = m.DynamicArray()
    moved = [arr.append(i * i) for i in range(9)]
    assert moved == [0, 1, 2, 0, 4, 0, 0, 0, 8]
    assert len(arr) == 9 and arr.capacity == 16 and arr.resizes == 4
    assert [arr[i] for i in range(9)] == [i * i for i in range(9)]
    with pytest.raises(IndexError):
        arr[9]


def test_bad_growth(load):
    m = load("ex02_dynamic_array")
    arr = m.DynamicArray(lambda cap: cap)
    arr.append(1)
    with pytest.raises(ValueError):
        arr.append(2)


def test_accounting(load):
    m = load("ex02_dynamic_array")
    assert m.accounting_min_balance(100_000, 3) == 0
    assert m.accounting_min_balance(5000, 2) < 0
    assert m.accounting_min_balance(0, 3) == 0
