import pytest


def test_examples(load):
    m = load("ex03_first_unique")
    assert m.first_unique(["ann", "bob", "ann", "cy", "bob"]) == "cy"
    assert m.first_unique(["a", "a"]) is None


@pytest.mark.parametrize("ids, expected", [
    ([], None), (["solo"], "solo"), ([0, 0, 0, 7], 7), (["", "x", "x"], ""),
    (["b", "a", "b", "a", "b"], None), (list(range(300)) * 2 + [5000], 5000),
])
def test_edge_cases(load, ids, expected):
    m = load("ex03_first_unique")
    assert m.first_unique(ids) == expected
    assert m.brute_force(ids) == expected


def test_input_not_mutated(load):
    m = load("ex03_first_unique")
    ids = ["x", "y", "x"]
    m.first_unique(ids)
    assert ids == ["x", "y", "x"]


def test_scoring(load):
    m = load("ex03_first_unique")
    assert m.score_submission(m.first_unique) == 4
    assert m.score_submission(m.tempting_least_frequent) == 3
    assert m.score_submission(lambda ids: 1 / 0) == 0          # crashes score 0, never raise


def test_scoring_isolates_mutation(load):
    m = load("ex03_first_unique")

    def destructive(ids):
        answer = m.first_unique(ids)
        ids.clear()
        return answer

    assert m.score_submission(destructive) == 4
    assert m.CASES[0][0] == ["ann", "bob", "ann", "cy", "bob"]
