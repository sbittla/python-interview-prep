import math

import pytest
import torch
import torch.nn.functional as F
from torch import nn


def test_shape_trace(load):
    m = load("ex09_shapes_and_nans")
    net = nn.Sequential(nn.Linear(4, 3), nn.ReLU())
    assert m.shape_trace(net, torch.randn(2, 4)) == [("0", (2, 3)), ("1", (2, 3))]
    torch.manual_seed(0)
    assert m.shape_trace(m.Net(), torch.randn(5, 4)) == [("body.0", (5, 8)), ("body.1", (5, 8)),
                                                         ("head", (5, 1))]


def test_hooks_removed_even_on_error(load):
    m = load("ex09_shapes_and_nans")
    net = nn.Sequential(nn.Linear(4, 3), nn.Linear(5, 1))      # second layer: wrong in-features
    with pytest.raises(RuntimeError):
        m.shape_trace(net, torch.randn(2, 4))
    assert all(len(mod._forward_hooks) == 0 for mod in net.modules())
    m.first_nonfinite(nn.Sequential(nn.Linear(2, 2)), torch.randn(1, 2))


def test_first_nonfinite(load):
    m = load("ex09_shapes_and_nans")
    torch.manual_seed(0)
    net = m.Net()
    assert m.first_nonfinite(net, torch.randn(3, 4)) is None
    with torch.no_grad():
        net.body[0].bias[0] = float("nan")
    assert m.first_nonfinite(net, torch.randn(3, 4)) == "body.0"   # the first, not the last
    assert m.first_nonfinite(m.Net(), torch.full((2, 4), float("inf"))) == "body.0"


def test_checked_mse(load):
    m = load("ex09_shapes_and_nans")
    with pytest.raises(ValueError):
        m.checked_mse(torch.randn(6, 1), torch.randn(6))
    a, b = torch.randn(6), torch.randn(6)
    assert torch.allclose(m.checked_mse(a, b), F.mse_loss(a, b))


def test_cross_entropies(load):
    m = load("ex09_shapes_and_nans")
    big, y = torch.tensor([[1000.0, 0.0], [0.0, 1000.0]]), torch.tensor([0, 1])
    assert not math.isfinite(m.naive_cross_entropy(big, y).item())
    assert m.stable_cross_entropy(big, y).item() == pytest.approx(0.0, abs=1e-6)
    wrong = torch.tensor([[0.0, 1000.0]])
    assert m.stable_cross_entropy(wrong, torch.tensor([0])).item() == pytest.approx(1000.0)
    torch.manual_seed(1)
    small, yy = torch.randn(5, 4), torch.tensor([0, 3, 1, 2, 0])
    assert torch.allclose(m.naive_cross_entropy(small, yy), F.cross_entropy(small, yy))
    assert torch.allclose(m.stable_cross_entropy(small, yy), F.cross_entropy(small, yy))


@pytest.mark.parametrize("lr, expected", [(0.1, False), (0.9, False), (0.99, False), (1.1, True), (3.0, True)])
def test_diverges(load, lr, expected):
    assert load("ex09_shapes_and_nans").diverges(lr) is expected
