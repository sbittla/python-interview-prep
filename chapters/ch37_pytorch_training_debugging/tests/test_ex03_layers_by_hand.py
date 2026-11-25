import pytest
import torch
import torch.nn.functional as F

D = torch.float64


def test_linear(load):
    m = load("ex03_layers_by_hand")
    torch.manual_seed(0)
    x, W, b = torch.randn(4, 5, dtype=D), torch.randn(3, 5, dtype=D), torch.randn(3, dtype=D)
    assert torch.allclose(m.linear(x, W, b), F.linear(x, W, b))
    assert torch.allclose(m.linear(x, W, None), F.linear(x, W))


@pytest.mark.parametrize("stride, padding, k", [(1, 0, 3), (1, 1, 3), (2, 1, 3), (2, 0, 2), (1, 2, 1)])
def test_conv(load, stride, padding, k):
    m = load("ex03_layers_by_hand")
    torch.manual_seed(stride * 10 + padding + k)
    x = torch.randn(2, 3, 7, 6, dtype=D)          # non-square on purpose
    w, b = torch.randn(4, 3, k, k, dtype=D), torch.randn(4, dtype=D)
    ref = F.conv2d(x, w, b, stride=stride, padding=padding)
    assert torch.allclose(m.conv2d_unfold(x, w, b, stride, padding), ref)
    assert torch.allclose(m.conv2d_loops(x, w, b, stride, padding), ref)


def test_conv_example(load):
    m = load("ex03_layers_by_hand")
    out = m.conv2d_unfold(torch.ones(1, 1, 3, 3), torch.ones(1, 1, 2, 2), torch.zeros(1))
    assert out.tolist() == [[[[4.0, 4.0], [4.0, 4.0]]]]


def test_batch_norm_train_eval_and_buffers(load):
    m = load("ex03_layers_by_hand")
    torch.manual_seed(3)
    bn = torch.nn.BatchNorm1d(3, momentum=0.2).double()
    with torch.no_grad():
        bn.weight.copy_(torch.tensor([1.5, 0.5, 2.0]))
        bn.bias.copy_(torch.tensor([0.1, -0.2, 0.3]))
    g, be = bn.weight.detach().clone(), bn.bias.detach().clone()
    rm, rv = torch.zeros(3, dtype=D), torch.ones(3, dtype=D)
    for _ in range(3):                              # several steps: momentum compounds
        xb = torch.randn(6, 3, dtype=D) * 3 + 2
        assert torch.allclose(m.batch_norm(xb, g, be, rm, rv, True, momentum=0.2), bn(xb))
    assert torch.allclose(rm, bn.running_mean) and torch.allclose(rv, bn.running_var)
    bn.eval()
    xe = torch.randn(4, 3, dtype=D)
    assert torch.allclose(m.batch_norm(xe, g, be, rm, rv, False, momentum=0.2), bn(xe))


def test_batch_norm_single_example_raises(load):
    m = load("ex03_layers_by_hand")
    with pytest.raises(ValueError):
        m.batch_norm(torch.randn(1, 3, dtype=D), torch.ones(3, dtype=D), torch.zeros(3, dtype=D),
                     torch.zeros(3, dtype=D), torch.ones(3, dtype=D), True)


def test_layer_norm(load):
    m = load("ex03_layers_by_hand")
    torch.manual_seed(4)
    x = torch.randn(2, 3, 5, dtype=D)
    g, b = torch.randn(5, dtype=D), torch.randn(5, dtype=D)
    assert torch.allclose(m.layer_norm(x, g, b), F.layer_norm(x, (5,), g, b))


def test_dropout(load):
    m = load("ex03_layers_by_hand")
    x = torch.ones(200_000, dtype=D)
    out = m.dropout(x, 0.4, True, torch.Generator().manual_seed(0))
    kept = out != 0
    assert abs(kept.double().mean().item() - 0.6) < 0.01
    assert torch.allclose(out[kept], torch.full_like(out[kept], 1 / 0.6))
    assert abs(out.mean().item() - 1.0) < 0.02
    assert torch.equal(m.dropout(x, 0.4, False), x)
    assert torch.equal(m.dropout(x, 0.0, True), x)


def test_embedding(load):
    m = load("ex03_layers_by_hand")
    table = torch.arange(12, dtype=D).reshape(6, 2)
    ids = torch.tensor([[0, 5], [5, 2]])
    assert torch.equal(m.embedding(ids, table), F.embedding(ids, table))
