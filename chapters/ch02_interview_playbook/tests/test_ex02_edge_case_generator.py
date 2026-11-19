import pytest


def test_example(load):
    m = load("ex02_edge_case_generator")
    labels = [label for label, _ in m.edge_cases({"k": "int"}, {"k": 5})]
    assert labels == ["k=zero", "k=one", "k=negative", "k=large"]


def test_one_at_a_time(load):
    m = load("ex02_edge_case_generator")
    typical = {"nums": [3, 1, 4], "k": 2}
    cases = m.edge_cases({"nums": "list[int]", "k": "int"}, typical)
    assert len(cases) == 12
    for label, kwargs in cases:
        name = label.split("=")[0]
        assert all(kwargs[p] == typical[p] for p in typical if p != name)


def test_skips_case_equal_to_typical(load):
    m = load("ex02_edge_case_generator")
    cases = m.edge_cases({"k": "int"}, {"k": 0})
    assert [label for label, _ in cases] == ["k=one", "k=negative", "k=large"]


def test_cases_are_independent(load):
    m = load("ex02_edge_case_generator")
    typical = {"nums": [1, 2]}
    cases = m.edge_cases({"nums": "list[int]"}, typical)
    cases[0][1]["nums"].append(99)
    cases[1][1]["nums"].append(99)
    again = m.edge_cases({"nums": "list[int]"}, typical)
    assert again[0][1]["nums"] == [] and again[1][1]["nums"] == [7]
    assert typical == {"nums": [1, 2]}


def test_str_edges(load):
    m = load("ex02_edge_case_generator")
    vals = [kw["s"] for _, kw in m.edge_cases({"s": "str"}, {"s": "hello"})]
    assert vals == ["", "a", "aaaa", "aA", "a b"]


@pytest.mark.parametrize("spec, typical", [
    ({"k": "int"}, {}),
    ({"k": "int"}, {"k": 1, "extra": 2}),
    ({"t": "tuple"}, {"t": ()}),
])
def test_bad_input(load, spec, typical):
    m = load("ex02_edge_case_generator")
    with pytest.raises(ValueError):
        m.edge_cases(spec, typical)


def test_run_cases_finds_buggy(load):
    m = load("ex02_edge_case_generator")
    cases = m.edge_cases({"nums": "list[int]", "k": "int"}, {"nums": [3, 1, 4, 1, 5], "k": 2})
    assert m.run_cases(m.max_gap_reference, cases, m.max_gap_reference) == []
    failing = m.run_cases(m.max_gap_buggy, cases, m.max_gap_reference)
    assert "nums=empty" in failing          # a crash counts as a failure
    assert "k=zero" in failing


def test_reference(load):
    m = load("ex02_edge_case_generator")
    assert m.max_gap_reference([5, 1, 9], 1) == 8
    assert m.max_gap_reference([1, 5, 9], 1) == 4
    assert m.max_gap_reference([9, 1], 3) == 0
