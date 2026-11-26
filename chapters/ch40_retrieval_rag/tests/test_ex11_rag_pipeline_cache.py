import pytest


@pytest.fixture
def env(load):
    m = load("ex11_rag_pipeline_cache")
    from ragkit import MockLLM, load_chunks
    llm = MockLLM()
    return m, llm, m.RAGPipeline(load_chunks(), llm, k=3)


def test_examples(load):
    m = load("ex11_rag_pipeline_cache")
    assert m.normalize_query("  How often, rotate KEYS?? ") == "how often rotate keys"


@pytest.mark.parametrize("raw, norm", [("", ""), ("?!", ""), ("E409", "e409"), ("a\tb\nc", "a b c")])
def test_normalize_edges(load, raw, norm):
    assert load("ex11_rag_pipeline_cache").normalize_query(raw) == norm


def test_cache_hit_on_variant(env):
    m, llm, rag = env
    a = rag.answer("How often should I rotate access keys?", {"access": "public"})
    b = rag.answer("how often should i ROTATE access keys", {"access": "public"})
    assert not a["cached"] and b["cached"] and llm.calls == 1
    assert a["answer"] == b["answer"] and a["citations"] == {1: "d06#1", 2: "d06#0"}
    assert rag.stats["hit"] == 1 and rag.stats["miss"] == 1


def test_filter_is_part_of_the_key(env):
    m, llm, rag = env
    q = "Who handles a P1 ticket at night?"
    staff = rag.answer(q, {"access": {"public", "internal"}})
    assert "d12#1" in staff["retrieved"] and "d12#1" in staff["citations"].values()
    public = rag.answer(q, {"access": "public"})
    assert not public["cached"]                                      # not served the staff answer
    assert all(not r.startswith(("d12", "d13")) for r in public["retrieved"])
    # same filter written differently -> same key
    again = rag.answer(q, {"access": ["internal", "public"]})
    assert again["cached"]


def test_no_candidates_skips_llm(env):
    m, llm, rag = env
    from ragkit import ABSTAIN
    r = rag.answer("rotate access keys", {"area": "billing"})
    assert r["answer"] == ABSTAIN and r["retrieved"] == [] and r["citations"] == {} and llm.calls == 0
    strict = m.RAGPipeline(rag.chunks, llm, min_score=0.99)
    assert strict.answer("rotate access keys")["answer"] == ABSTAIN and llm.calls == 0


def test_add_chunks_invalidates(env):
    m, llm, rag = env
    q = "How often should I rotate access keys?"
    before = rag.answer(q)
    rag.add_chunks([{"id": "d17#0", "doc": "d17", "area": "security", "access": "public", "year": 2026,
                     "text": "Access keys / Policy update: rotate access keys every 30 days."}])
    after = rag.answer(q)
    assert rag.version == 1 and not after["cached"] and llm.calls == 2
    assert "d17#0" in after["retrieved"] and after["answer"] != before["answer"]


def test_lru_eviction(load):
    m = load("ex11_rag_pipeline_cache")
    from ragkit import MockLLM, load_chunks
    rag = m.RAGPipeline(load_chunks(), MockLLM(), cache_size=2)
    for q in ["rotate keys", "encryption at rest", "rotate keys", "multipart upload", "encryption at rest"]:
        rag.answer(q)
    # "rotate keys" was refreshed by its hit, so "encryption at rest" was the LRU victim
    assert dict(rag.stats) == {"miss": 4, "hit": 1, "evicted": 2} and rag.llm.calls == 4
    assert len(rag.cache) == 2


def test_citations_only_cited_and_valid(env):
    m, llm, rag = env
    r = rag.answer("is my data encrypted at rest")
    assert set(r["citations"].values()) <= set(r["retrieved"])
    for n, cid in r["citations"].items():
        assert f"[{n}]" in r["answer"] and r["retrieved"][n - 1] == cid


def test_empty_query_raises(env):
    m, llm, rag = env
    with pytest.raises(ValueError):
        rag.answer(" ?! ")
