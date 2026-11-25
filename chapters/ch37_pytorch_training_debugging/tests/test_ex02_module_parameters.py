import pytest
import torch
from torch import nn


@pytest.mark.parametrize("sizes", [[4, 8, 3], [2, 2], [5, 7, 7, 1]])
def test_counts(load, sizes):
    m = load("ex02_module_parameters")
    model = m.MLP(sizes)
    assert m.count_params(model) == m.expected_mlp_params(sizes)
    assert m.count_params(model) == sum(p.numel() for p in model.parameters())
    assert len([x for x in model.modules() if isinstance(x, nn.Linear)]) == len(sizes) - 1


def test_expected_formula(load):
    assert load("ex02_module_parameters").expected_mlp_params([4, 8, 3]) == 4 * 8 + 8 + 8 * 3 + 3


def test_no_activation_after_last_layer(load):
    m = load("ex02_module_parameters")
    torch.manual_seed(0)
    model = m.MLP([3, 4, 2])
    out = model(torch.randn(50, 3))
    assert (out < 0).any()                       # ReLU after the last layer would forbid this


def test_list_mlp_hides_params(load):
    m = load("ex02_module_parameters")
    bad = m.ListMLP([4, 8, 3])
    assert m.count_params(bad) == 0 and len(bad.state_dict()) == 0
    with pytest.raises(ValueError):
        torch.optim.SGD(bad.parameters(), lr=0.1)


def test_freeze_and_trainable_count(load):
    m = load("ex02_module_parameters")
    model = m.MLP([4, 8, 3])
    m.freeze(model.layers[0])
    assert m.count_params(model, trainable_only=True) == 8 * 3 + 3
    assert m.count_params(model) == 67
    assert all(not p.requires_grad for p in model.layers[0].parameters())


def test_buffers(load):
    m = load("ex02_module_parameters")
    s = m.Standardise(torch.tensor([1.0, 2.0]), torch.tensor([2.0, 4.0]))
    assert sorted(s.state_dict()) == ["mean", "std"]
    assert m.count_params(s) == 0
    assert s(torch.tensor([[3.0, 6.0]])).tolist() == [[1.0, 1.0]]
