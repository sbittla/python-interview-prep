import pytest


def test_examples(load):
    m = load("ex12_flops_params_memory")
    assert m.forward_matmul_flops(10, 4, 1, 3) == 1536
    assert m.gpt_params(50257, 1024, 768, 12) == 124439808
    assert m.matmul_params(50257, 768, 12) == 12 * 12 * 768 ** 2 + 768 * 50257


@pytest.mark.parametrize("V, D, L, T, H, F", [
    (50, 16, 2, 8, 4, None), (37, 24, 3, 5, 2, None), (11, 8, 1, 1, 1, None), (9, 12, 2, 6, 3, 20),
])
def test_formula_matches_instrumented_forward(load, V, D, L, T, H, F):
    m = load("ex12_flops_params_memory")
    assert m.count_forward_flops(V, D, L, T, H, F) == m.forward_matmul_flops(V, D, L, T, F)


def test_attention_term_is_quadratic(load):
    m = load("ex12_flops_params_memory")
    f = lambda T: m.forward_matmul_flops(100, 32, 2, T)
    # second difference of a quadratic a*T^2 + b*T is 2a; a = 4*L*D
    assert f(10) - 2 * f(9) + f(8) == 2 * 4 * 2 * 32
    assert m.flops_per_token_rule(1000, 2, 10, 4) == 2 * 1000 + 2 * 2 * 10 * 4


def test_params_with_custom_f(load):
    m = load("ex12_flops_params_memory")
    D, F = 10, 7
    per = 4 * D * D + 4 * D + 2 * D * F + F + D + 4 * D
    assert m.gpt_params(5, 3, D, 2, F) == 5 * D + 3 * D + 2 * per + 2 * D


def test_memory(load):
    m = load("ex12_flops_params_memory")
    assert m.attention_scores_bytes(1, 32, 8192, 4) == 8 * 2**30
    assert m.attention_scores_bytes(2, 3, 5, 2) == 2 * 3 * 25 * 2


def test_against_torch_count(load):
    torch = pytest.importorskip("torch")
    m = load("ex12_flops_params_memory")
    D, L, V, T = 32, 2, 50, 16
    layers = [torch.nn.TransformerEncoderLayer(D, 4, 4 * D, batch_first=True) for _ in range(L)]
    mods = [torch.nn.Embedding(V, D), torch.nn.Embedding(T, D), *layers, torch.nn.LayerNorm(D)]
    assert sum(p.numel() for mod in mods for p in mod.parameters()) == m.gpt_params(V, T, D, L)


@pytest.mark.parametrize("V, D, L", [(50257, 768, 12), (100, 16, 3)])
def test_split_flops_crossover(load, V, D, L):
    m = load("ex12_flops_params_memory")
    for T in (1, 7, 6 * D):
        att, dense, head = m.split_flops(V, D, L, T)
        assert att + dense + head == m.forward_matmul_flops(V, D, L, T) // T
        assert att == 4 * L * T * D and dense == 24 * L * D * D and head == 2 * D * V
    assert m.split_flops(V, D, L, 6 * D)[0] == m.split_flops(V, D, L, 6 * D)[1]
    assert m.split_flops(V, D, L, 12 * D)[0] // 2 == m.split_flops(V, D, L, 12 * D)[1]
