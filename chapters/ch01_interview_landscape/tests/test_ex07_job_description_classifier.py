def test_example(load):
    m = load("ex07_job_description_classifier")
    assert m.classify("We build REST APIs and distributed systems in Python.")["track"] == "S"


def test_no_substring_matches(load):
    m = load("ex07_job_description_classifier")
    r = m.classify("Maintain great products; we ragged on models of trains.")
    # "rag" must not match inside "ragged"; "models" is an M term
    assert r["counts"] == {"S": 0, "M": 1, "L": 0}


def test_bigrams_and_ties(load):
    m = load("ex07_job_description_classifier")
    r = m.classify("System design, system design and SQL.")
    assert r["counts"]["S"] == 2 and r["counts"]["M"] == 1
    assert r["top_terms"] == [("system design", 2), ("sql", 1)]


def test_mixed_roles_get_mixed_rounds(load):
    m = load("ex07_job_description_classifier")
    r = m.classify("LLM RAG embeddings with pandas and SQL")
    assert r["track"] == "L"
    assert "ml_coding" in r["likely_rounds"] and "llm_coding" in r["likely_rounds"]


def test_empty(load):
    m = load("ex07_job_description_classifier")
    r = m.classify("")
    assert r == {"counts": {"S": 0, "M": 0, "L": 0}, "track": "S", "likely_rounds": [],
                 "top_terms": []}
