import math

import pytest

M = "ex03_fleet_sizing_cost"


def test_rag_plan_batch_64(load):
    m = load(M)
    p = m.size_fleet(m.RAG, m.M8B, m.G80, 64)
    assert (p.prefill_replicas, p.decode_replicas, p.replicas) == (18, 8, 26)
    step = (16e9 + 64 * 3150 * 131072) / 2e12
    assert p.tpot == pytest.approx(step)
    assert p.ttft == pytest.approx(0.24)
    assert p.e2e == pytest.approx(0.24 + 299 * step)
    assert p.in_decode == pytest.approx(50 * 299 * step)          # Little's law


def test_prefill_pool_formula(load):
    m = load(M)
    # 50 qps * 3000 tokens / (12,500 tokens/s * 0.7) = 17.14 -> 18
    assert m.size_fleet(m.RAG, m.M8B, m.G80, 64).prefill_replicas == 18
    assert m.size_fleet(m.RAG, m.M8B, m.G80, 64, target_util=1.0).prefill_replicas == 12
    half = m.Workload(50, 1500, 300)
    assert m.size_fleet(half, m.M8B, m.G80, 64).prefill_replicas == 9


def test_small_batch_costs_more_replicas_but_lower_latency(load):
    m = load(M)
    small, big = m.size_fleet(m.RAG, m.M8B, m.G80, 8), m.size_fleet(m.RAG, m.M8B, m.G80, 64)
    assert small.decode_replicas == 26 and small.replicas > big.replicas
    assert small.e2e < big.e2e


def test_output_one_token_needs_no_decode(load):
    m = load(M)
    p = m.size_fleet(m.Workload(10, 500, 1), m.M8B, m.G80, 16)
    assert p.decode_replicas == 0 and p.e2e == pytest.approx(p.ttft)


def test_rung1_underestimates(load):
    m = load(M)
    assert m.output_tokens_only(m.RAG, m.M8B, m.G80, 64) == 5


def test_fits_and_pick_batch(load):
    m = load(M)
    assert m.fits(m.RAG, m.M8B, m.G80) == int(56e9 // (3300 * 131072)) == 129
    assert m.pick_batch(m.RAG, m.M8B, m.G80, 0.025) == 64
    assert m.pick_batch(m.RAG, m.M8B, m.G80, 0.010) == 8
    assert m.pick_batch(m.RAG, m.M8B, m.G80, 1.0) == 128              # 256 does not fit
    with pytest.raises(ValueError):
        m.pick_batch(m.RAG, m.M8B, m.G80, 0.005)


def test_size_fleet_rejects_batch_over_memory_and_bad_args(load):
    m = load(M)
    with pytest.raises(ValueError, match="exceeds the 129"):
        m.size_fleet(m.RAG, m.M8B, m.G80, 256)
    with pytest.raises(ValueError):
        m.size_fleet(m.RAG, m.ModelSpec("M70B", 70e9, 80, 8, 128), m.G80, 1)
    with pytest.raises(ValueError):
        m.size_fleet(m.Workload(0, 10, 10), m.M8B, m.G80, 1)
    with pytest.raises(ValueError):
        m.size_fleet(m.RAG, m.M8B, m.G80, 8, target_util=0)


def test_costs_and_break_even(load):
    m = load(M)
    p = m.size_fleet(m.RAG, m.M8B, m.G80, 64)
    api = m.api_cost_per_1k(m.RAG, 0.50, 1.50)
    assert api == pytest.approx(1.95)
    assert m.cost_per_1k(p, 2.50, 50) == pytest.approx(26 * 2.5 / (50 * 3600) * 1000)
    assert m.cost_per_1k(p, 2.50, 5) == pytest.approx(10 * m.cost_per_1k(p, 2.50, 50))
    be = m.break_even_avg_qps(p, 2.50, api)
    assert m.cost_per_1k(p, 2.50, be) == pytest.approx(api)
    assert math.isclose(be, 26 * 2.5 / 3.6 / 1.95)
    with pytest.raises(ValueError):
        m.cost_per_1k(p, 2.50, 0)
