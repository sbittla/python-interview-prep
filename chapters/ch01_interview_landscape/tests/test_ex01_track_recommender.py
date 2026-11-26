import pytest


def test_examples(load):
    m = load("ex01_track_recommender")
    assert m.recommend_track({"target_role": "Backend Engineer"})["track"] == "S"
    assert m.recommend_track({"target_role": "ML engineer", "interests": ["pandas"]})["track"] == "M"


@pytest.mark.parametrize("profile, track", [
    ({"target_role": "Data Scientist"}, "M"),
    ({"target_role": "LLM engineer"}, "L"),
    ({"target_role": "Engineer"}, "S"),  # no match -> S
    ({"target_role": "ML engineer", "interests": ["rag", "agents", "prompting"]}, "M"),  # tie -> M
    ({"target_role": "backend engineer", "interests": ["rag", "agents", "prompting"]}, "S"),  # S/L tie
    ({"target_role": "engineer", "interests": ["RAG", "Embeddings"]}, "L"),
    ({"target_role": "", "interests": []}, "S"),
])
def test_tracks(load, profile, track):
    m = load("ex01_track_recommender")
    assert m.recommend_track(profile)["track"] == track


def test_fast_track_removes_part_one(load):
    m = load("ex01_track_recommender")
    rec = m.recommend_track({"target_role": "LLM engineer", "skip_python_basics": True})
    assert "I" not in rec["parts"] and rec["parts"][0] == "0"
    assert "I" in m.TRACK_PARTS["L"]  # the shared table must not be mutated


def test_reasons_sorted_and_input_untouched(load):
    m = load("ex01_track_recommender")
    p = {"target_role": "Data Scientist", "interests": ["Statistics", "pandas"]}
    before = {"target_role": "Data Scientist", "interests": ["Statistics", "pandas"]}
    rec = m.recommend_track(p)
    assert rec["reasons"] == ["data", "pandas", "scientist", "statistics"]
    assert p == before


def test_reasons_only_count_scoring_keywords(load):
    m = load("ex01_track_recommender")
    # "ai" is an L *role* keyword; listed as an interest it scores nothing, so it is no reason.
    rec = m.recommend_track({"target_role": "LLM engineer", "interests": ["AI", "embeddings"]})
    assert rec["track"] == "L"
    assert rec["reasons"] == ["embeddings", "llm"]
