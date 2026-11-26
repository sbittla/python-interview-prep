import pytest

M = "ex01_kv_memory_budget"


def test_kv_bytes_includes_k_and_v_and_uses_kv_heads(load):
    m = load(M)
    assert m.kv_bytes_per_token(m.M8B) == 2 * 32 * 8 * 128 * 2 == 131072
    assert m.kv_bytes_per_token(m.M8B_MHA) == 4 * m.kv_bytes_per_token(m.M8B)
    assert m.kv_bytes_per_token(m.M8B_MQA) == m.kv_bytes_per_token(m.M8B) / 8
    assert m.kv_bytes_per_token_mha(m.M8B) == m.kv_bytes_per_token(m.M8B_MHA)


def test_kv_bytes_scales_with_dtype_and_layers(load):
    m = load(M)
    spec = m.ModelSpec("x", 1e9, 10, 8, 2, 64, bytes_per_param=2, bytes_per_kv=1)
    assert m.kv_bytes_per_token(spec) == 2 * 10 * 2 * 64 * 1


def test_weight_bytes(load):
    m = load(M)
    assert m.weight_bytes(m.M8B) == 16e9
    assert m.weight_bytes(m.ModelSpec("q4", 8e9, 32, 32, 8, 128, bytes_per_param=0.5)) == 4e9


@pytest.mark.parametrize("ctx, expected", [(4096, 104), (32768, 13), (1, 427246)])
def test_max_sequences_gqa(load, ctx, expected):
    m = load(M)
    # (80e9 * 0.9 - 16e9) // (ctx * 131072)
    assert m.max_sequences(m.M8B, 80e9, ctx) == expected


def test_max_sequences_reserve_and_gpus(load):
    m = load(M)
    assert m.max_sequences(m.M8B, 80e9, 4096, reserve_frac=0.0) == int(64e9 // (4096 * 131072))
    assert m.max_sequences(m.M70B, 80e9, 4096) == 0                  # weights alone do not fit
    assert m.max_sequences(m.M70B, 80e9, 4096, n_gpus=2) == 2
    assert m.max_sequences(m.M70B, 80e9, 4096, n_gpus=4) == 110


def test_exactly_full_memory_is_zero(load):
    m = load(M)
    spec = m.ModelSpec("big", 36e9, 32, 32, 8, 128)                 # 72 GB = 90% of 80 GB
    assert m.max_sequences(spec, 80e9, 1024) == 0


def test_validation(load):
    m = load(M)
    with pytest.raises(ValueError):
        m.kv_bytes_per_token(m.ModelSpec("bad", 1e9, 4, 6, 4, 64))
    with pytest.raises(ValueError):
        m.kv_bytes_per_token(m.ModelSpec("bad", 1e9, 0, 4, 4, 64))
    with pytest.raises(ValueError):
        m.max_sequences(m.M8B, 80e9, 0)
    with pytest.raises(ValueError):
        m.max_sequences(m.M8B, 80e9, 1024, reserve_frac=1.0)
