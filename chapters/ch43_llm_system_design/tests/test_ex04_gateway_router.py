import pytest

M = "ex04_gateway_router"


def req(m, t=0, tier="simple", key="k", prompt=500, output=100, deadline=5000, rid=0):
    return m.Request(rid, t, tier, key, prompt, output, deadline)


def test_happy_path_and_cost(load):
    m = load(M)
    r = m.serve(req(m), m.BACKENDS, m.FALLBACK, {})
    assert (r.status, r.served_by, r.latency_ms, r.attempts) == ("ok", "small", 1150, ["ok:small"])
    assert r.cost == pytest.approx((500 * 0.10 + 100 * 0.40) / 1e6)
    assert not r.late


def test_cache_hit_after_success_only(load):
    m = load(M)
    cache = {}
    m.serve(req(m, key="a"), m.BACKENDS, m.FALLBACK, cache)
    hit = m.serve(req(m, key="a"), m.BACKENDS, m.FALLBACK, cache)
    assert (hit.status, hit.latency_ms, hit.cost) == ("cache", m.CACHE_MS, 0.0)
    cache2 = {}
    bad = m.serve(req(m, t=6000, key="b", prompt=12000, output=50, deadline=3000),
                  m.BACKENDS, m.FALLBACK, cache2)
    assert bad.status == "degraded" and cache2 == {}


def test_context_filter_routes_long_prompt_to_large(load):
    m = load(M)
    r = m.serve(req(m, prompt=12000, output=50), m.BACKENDS, m.FALLBACK, {})
    assert (r.status, r.served_by, r.attempts) == ("ok", "large", ["ok:large"])
    too_long = m.serve(req(m, prompt=40000), m.BACKENDS, m.FALLBACK, {})
    assert (too_long.status, too_long.attempts, too_long.latency_ms) == ("degraded", [], 0)


def test_fallback_during_outage_pays_timeout(load):
    m = load(M)
    r = m.serve(req(m, t=5000, tier="complex", prompt=300, output=150, deadline=15000),
                m.BACKENDS, m.FALLBACK, {})
    assert r.status == "fallback" and r.attempts == ["fail:large", "ok:small"]
    assert r.latency_ms == 4000 + 150 + 10 * 150
    assert r.cost == pytest.approx((300 * 0.10 + 150 * 0.40) / 1e6)      # failed call unbilled


def test_outage_window_is_half_open(load):
    m = load(M)
    at_end = m.serve(req(m, t=9000, tier="complex", output=150, deadline=15000),
                     m.BACKENDS, m.FALLBACK, {})
    assert at_end.attempts == ["ok:large"]
    before = m.serve(req(m, t=4999, tier="complex", output=150, deadline=15000),
                     m.BACKENDS, m.FALLBACK, {})
    assert before.attempts == ["ok:large"]


def test_outage_checked_at_attempt_time(load):
    m = load(M)
    backends = {"a": m.Backend("a", 100, 1, 0, 0, 1000, 10_000, outages=((0, 10**9),)),
                "b": m.Backend("b", 100, 1, 0, 0, 1000, 10_000, outages=((0, 1500),))}
    policy = {"simple": ["a", "b"]}
    # b is tried at t + 1000 (after a's timeout): down at 0 + 1000, up again at 600 + 1000
    early = m.serve(req(m, t=0, output=10), backends, policy, {})
    late = m.serve(req(m, t=600, output=10), backends, policy, {})
    assert early.attempts == ["fail:a", "fail:b"] and early.latency_ms == 2000
    assert late.attempts == ["fail:a", "ok:b"] and late.latency_ms == 1110


def test_deadline_aware_caps_timeout_and_skips(load):
    m = load(M)
    long_simple = req(m, t=6000, prompt=12000, output=50, deadline=3000)
    aware = m.serve(long_simple, m.BACKENDS, m.FALLBACK, {})
    fixed = m.serve(long_simple, m.BACKENDS, m.FALLBACK, {}, deadline_aware=False)
    assert (aware.latency_ms, aware.late) == (3000, False)
    assert (fixed.latency_ms, fixed.late) == (4000, True)
    slow = req(m, t=7000, tier="complex", prompt=4000, output=400, deadline=8000)
    r = m.serve(slow, m.BACKENDS, m.FALLBACK, {})
    assert r.attempts == ["skip:large", "ok:small"] and r.status == "fallback"
    assert r.latency_ms == 4150
    f = m.serve(slow, m.BACKENDS, m.FALLBACK, {}, deadline_aware=False)
    assert f.attempts == ["fail:large", "ok:small"] and f.late


def test_deadline_aware_is_never_late(load):
    m = load(M)
    assert not any(r.late for r in m.run(m.FALLBACK, True))
    assert sum(r.late for r in m.run(m.FALLBACK, False)) == 2


def test_percentile_nearest_rank(load):
    m = load(M)
    assert m.percentile([5, 1, 4, 2, 3], 50) == 3
    assert m.percentile(list(range(1, 21)), 95) == 19
    assert m.percentile(list(range(1, 21)), 100) == 20
    assert m.percentile([7], 95) == 7
    assert m.percentile(list(range(1, 101)), 7) == 7          # ceil(7 / 100 * 100) == 8


def test_summarise_policies(load):
    m = load(M)
    single = m.summarise(m.run(m.SINGLE))
    aware = m.summarise(m.run(m.FALLBACK))
    assert single["degraded_rate"] == round(5 / 12, 3)
    assert aware["degraded_rate"] == round(1 / 12, 3) and aware["late_rate"] == 0.0
    assert aware["served_by"] == {"cache": 2, "large": 4, "none": 1, "small": 5}
    assert aware["p50_ms"] == 1650 and aware["p95_ms"] == 10400
    assert aware["n"] == 12
    with pytest.raises(ValueError):
        m.summarise([])


def test_context_filter_counts_output_tokens(load):
    m = load(M)
    r = m.serve(req(m, prompt=7950, output=100), m.BACKENDS, m.FALLBACK, {})   # 8050 > 8000
    assert r.served_by == "large"
    r = m.serve(req(m, prompt=7900, output=100), m.BACKENDS, m.FALLBACK, {})   # exactly 8000
    assert r.served_by == "small"
