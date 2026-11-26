from dataclasses import replace

import pytest


def test_checkpoints(load):
    m = load("ex05_peer_script")
    mocks = m.by_id(m.load_mocks())
    assert m.checkpoints(mocks["S1"]) == [
        (0, "intro"), (5, "A: merge two sorted lists"),
        (10, "checkpoint A: no plan stated yet? offer hint A1"),
        (18, "B: longest substring without repeats"),
        (26, "checkpoint B: no plan stated yet? offer hint B1"), (40, "closing")]
    s3 = [t for _, t in m.checkpoints(mocks["S3"])]
    assert "API and requirements" in s3
    assert sum(t.startswith("checkpoint") for t in s3) == 2      # only problem segments


def test_every_mock_scripts(load):
    m = load("ex05_peer_script")
    for mock in m.load_mocks():
        lines = m.script(mock)
        text = "\n".join(lines)
        assert lines[0].startswith(f"Mock {mock.id}:")
        for p in mock.problems:
            assert p["path"] in text and p["prompt"] in text
            for i, h in enumerate(p["hints"], 1):
                assert f"{p['label']}{i}. {h}" in text
        for f in mock.followups + mock.strong:
            assert f in text
        stamps = [int(line[2:4]) for line in lines if line[:2] == "  " and line[2:4].isdigit()
                  and line[4:7] == ":00"]
        assert stamps == sorted(stamps) and stamps[0] == 0 and stamps[-1] < mock.minutes


def test_rubric_choice(load):
    m = load("ex05_peer_script")
    mocks = m.by_id(m.load_mocks())
    s2 = "\n".join(m.script(mocks["S2"]))
    l3 = "\n".join(m.script(mocks["L3"]))
    assert "§47.3" in s2 and "Correctness on tests and edge cases (25)" in s2
    assert "Verifying" not in s2
    assert "§47.4" in l3 and "Verifying and critiquing AI output (30)" in l3
    assert "Correctness on tests" not in l3


def test_unknown_rubric(load):
    m = load("ex05_peer_script")
    mock = replace(m.by_id(m.load_mocks())["S1"], rubric="essay")
    with pytest.raises(ValueError):
        m.script(mock)
