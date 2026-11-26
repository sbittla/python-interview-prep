import pytest

M = "ex02_latency_roofline"


def test_prefill_uses_2n_flops_and_mfu(load):
    m = load(M)
    assert m.prefill_seconds(m.M8B, m.G80, 3000) == pytest.approx(0.24)
    hw = m.Hardware("h", 80e9, 2e12, 4e14, mfu=1.0)
    assert m.prefill_seconds(m.M8B, hw, 1000) == pytest.approx(2 * 8e9 * 1000 / 4e14)


def test_decode_step_memory_bound_includes_kv_reads(load):
    m = load(M)
    s, bound = m.decode_step_seconds(m.M8B, m.G80, 64, 3150)
    assert bound == "memory"
    assert s == pytest.approx((16e9 + 64 * 3150 * 131072) / 2e12)
    s1, _ = m.decode_step_seconds(m.M8B, m.G80, 1, 3150)
    assert s1 == pytest.approx((16e9 + 3150 * 131072) / 2e12)


def test_decode_step_compute_bound_at_large_batch_short_ctx(load):
    m = load(M)
    s, bound = m.decode_step_seconds(m.M8B, m.G80, 512, 100)
    assert bound == "compute"
    assert s == pytest.approx(2 * 8e9 * 512 / (4e14 * 0.5))


def test_latency_first_token_from_prefill(load):
    m = load(M)
    lat = m.latency(m.M8B, m.G80, prompt=3000, output=300, batch=64)
    step, _ = m.decode_step_seconds(m.M8B, m.G80, 64, 3150)
    assert lat.ttft == pytest.approx(0.24)
    assert lat.tpot == pytest.approx(step)
    assert lat.e2e == pytest.approx(0.24 + 299 * step)
    one = m.latency(m.M8B, m.G80, prompt=200, output=1, batch=1)
    assert one.e2e == pytest.approx(one.ttft)


def test_decode_ctx_is_prompt_plus_half_output(load):
    m = load(M)
    lat = m.latency(m.M8B, m.G80, prompt=1000, output=2001, batch=8)
    assert lat.tpot == pytest.approx(m.decode_step_seconds(m.M8B, m.G80, 8, 2000)[0])


def test_throughput_grows_with_batch_but_sublinearly(load):
    m = load(M)
    t1 = m.decode_tokens_per_s(m.M8B, m.G80, 1, 3150)
    t64 = m.decode_tokens_per_s(m.M8B, m.G80, 64, 3150)
    assert 20 * t1 < t64 < 64 * t1
    assert m.compute_only_tokens_per_s(m.M8B, m.G80) == pytest.approx(12500)


@pytest.mark.parametrize("args", [(0, 10, 1), (10, 0, 1), (10, 10, 0)])
def test_validation(load, args):
    m = load(M)
    with pytest.raises(ValueError):
        m.latency(m.M8B, m.G80, *args)
