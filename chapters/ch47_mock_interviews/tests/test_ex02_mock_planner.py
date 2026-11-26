import json
from collections import Counter
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "data" / "mocks.json"


def test_catalogue_valid(load):
    m = load("ex02_mock_planner")
    mocks = m.load_mocks()
    assert [x.id for x in mocks] == ["S1", "S2", "S3", "S4", "M1", "M2", "M3", "L1", "L2", "L3"]
    assert Counter(x.track for x in mocks) == {"SWE": 4, "Data/ML": 3, "GenAI/LLM": 3}
    for x in mocks:
        assert x.strong and x.followups
    assert [x.id for x in mocks if x.rubric == "ai"] == ["L3"]


def test_cross_refs_point_at_existing_problems(load):
    m = load("ex02_mock_planner")
    for x in m.load_mocks():
        for p in x.problems:
            assert (m.ROOT / p["path"]).is_file()
            ref = p["ref"]
            if ref.startswith("Ch. 45 #"):
                assert f"/ex{ref[-3:]}_" in p["path"]
            else:
                chapter = ref.lstrip("§").split(".")[0]
                assert p["path"].startswith(f"chapters/ch{int(chapter):02d}_")


def test_timebox_contiguous(load):
    m = load("ex02_mock_planner")
    for x in m.load_mocks():
        tb = m.timebox(x)
        assert tb[0][1] == 0 and tb[-1][2] == x.minutes
        assert all(a[2] == b[1] for a, b in zip(tb, tb[1:]))
        assert tb[0][0] == "intro" and tb[-1][0] == "closing"
    assert m.timebox(m.by_id(m.load_mocks())["S2"])[1] == ("A: top-k frequent words", 5, 27)


def _write(tmp_path, mutate):
    data = json.loads(SRC.read_text(encoding="utf-8"))
    mutate(data["mocks"])
    path = tmp_path / "mocks.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("mutate", [
    lambda ms: ms[0]["segments"].append(["extra", 1]),
    lambda ms: ms[0]["problems"][0].update(path="chapters/nope.py"),
    lambda ms: ms.pop(),
    lambda ms: ms[1].update(id="S1"),
    lambda ms: ms[0].update(rubric="vibes"),
    lambda ms: ms[0]["problems"][0].update(hints=[]),
    lambda ms: ms[4].update(track="SWE"),
])
def test_invalid_catalogue(load, tmp_path, mutate):
    m = load("ex02_mock_planner")
    with pytest.raises(ValueError):
        m.load_mocks(_write(tmp_path, mutate))


def test_rotation_properties(load):
    m = load("ex02_mock_planner")
    mocks = m.load_mocks()
    track = {x.id: x.track for x in mocks}
    tracks = ["SWE", "Data/ML", "GenAI/LLM"]
    for seed in range(25):
        ids = m.rotation(mocks, tracks, 30, seed)
        assert [track[i] for i in ids] == tracks * 10
        for t in tracks:
            seq = [i for i in ids if track[i] == t]
            pool = sorted(x.id for x in mocks if x.track == t)
            n = len(pool)
            for k in range(0, len(seq) - n + 1, n):      # each cycle uses every mock once
                assert sorted(seq[k:k + n]) == pool
            assert all(a != b for a, b in zip(seq, seq[1:]))   # never back to back


def test_rotation_deterministic_and_seeded(load):
    m = load("ex02_mock_planner")
    mocks = m.load_mocks()
    assert m.rotation(mocks, ["SWE"], 12, seed=3) == m.rotation(mocks, ["SWE"], 12, seed=3)
    assert len({tuple(m.rotation(mocks, ["SWE"], 4, seed=s)) for s in range(10)}) > 1
    assert m.rotation(mocks, ["SWE", "SWE", "Data/ML"], 8, seed=7) == [
        "S4", "S2", "M2", "S1", "S3", "M1", "S2", "S4"]
    assert m.rotation(mocks, ["SWE"], 0) == []


def test_rotation_unknown_track(load):
    m = load("ex02_mock_planner")
    with pytest.raises(ValueError):
        m.rotation(m.load_mocks(), ["Frontend"], 3)


def test_weekly(load):
    m = load("ex02_mock_planner")
    assert m.weekly(list("abcde"), 2) == [["a", "b"], ["c", "d"], ["e"]]
    assert m.weekly([], 3) == []
    with pytest.raises(ValueError):
        m.weekly(["a"], 0)
