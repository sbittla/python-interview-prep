import random


def make(m, rows):
    return [m.Employee(*r) for r in rows]


def test_examples(load):
    m = load("ex08_multi_key_sort")
    rows = make(m, [("Bo", "eng", 90, 30), ("Al", "eng", 90, 41), ("Cy", "art", 70, 25)])
    assert [e.name for e in m.payroll_order(rows)] == ["Cy", "Al", "Bo"]
    assert [e.name for e in m.multi_sort(rows, [("dept", False), ("name", True)])] == ["Cy", "Bo", "Al"]


def test_does_not_mutate_and_handles_empty(load):
    m = load("ex08_multi_key_sort")
    rows = make(m, [("B", "x", 1, 1), ("A", "x", 1, 1)])
    copy = list(rows)
    m.multi_sort(rows, [("name", False)])
    m.payroll_order(rows)
    assert rows == copy
    assert m.multi_sort([], [("name", True)]) == []
    assert m.multi_sort(rows, []) == rows


def test_stability_on_full_ties(load):
    m = load("ex08_multi_key_sort")
    rows = make(m, [("Z", "a", 1, 9), ("Y", "a", 1, 8), ("X", "a", 1, 7)])
    out = m.multi_sort(rows, [("dept", True), ("salary", True)])
    assert [e.name for e in out] == ["Z", "Y", "X"]


def test_random_against_comparator(load):
    m = load("ex08_multi_key_sort")
    rng = random.Random(8)
    fields = ["name", "dept", "salary", "age"]
    for _ in range(200):
        rows = make(m, [(rng.choice("ABC"), rng.choice("xy"), rng.randint(1, 3), rng.randint(20, 22))
                        for _ in range(rng.randint(0, 10))])
        spec = [(f, rng.random() < 0.5) for f in rng.sample(fields, rng.randint(1, 4))]
        assert m.multi_sort(rows, spec) == m.by_comparator(rows, spec)
    rows = make(m, [(rng.choice("ABC"), rng.choice("xy"), rng.randint(1, 3), 1) for _ in range(30)])
    expected = m.by_comparator(rows, [("dept", False), ("salary", True), ("name", False)])
    assert m.payroll_order(rows) == expected
