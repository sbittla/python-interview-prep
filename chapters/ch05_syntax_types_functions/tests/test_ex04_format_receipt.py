def test_example(load):
    m = load("ex04_format_receipt")
    assert m.solve([("apple", 3, 0.5), ("laptop", 1, 1299.99)]) == [
        "Item          Qty      Amount",
        "apple           3        1.50",
        "laptop          1    1,299.99",
        "TOTAL                1,301.49",
    ]


def test_truncation_and_widths(load):
    m = load("ex04_format_receipt")
    lines = m.solve([("extra-long-product-name", 2, 2.25), ("big", 1000, 1234.5)])
    assert lines[1].startswith("extra-long-p ")
    assert lines[2].endswith("1,234,500.00")
    assert all(len(line) == 29 for line in lines)


def test_empty_and_brute(load):
    m = load("ex04_format_receipt")
    assert m.solve([]) == ["Item          Qty      Amount", "TOTAL                    0.00"]
    items = [("tea", 7, 3.333), ("cake", 0, 9.99), ("x" * 20, 12, 1000.0)]
    assert m.brute_force(items) == m.solve(items)
