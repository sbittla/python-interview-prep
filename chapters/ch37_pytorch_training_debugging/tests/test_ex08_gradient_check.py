import pytest
import torch


def test_numeric_grad_matches_known_derivatives(load):
    m = load("ex08_gradient_check")
    x = torch.tensor([[1.0, -2.0], [0.5, 3.0]], dtype=torch.float64)
    g = m.numeric_grad(lambda t: (t ** 3).sum(), x)
    assert g.shape == x.shape
    assert torch.allclose(g, 3 * x ** 2, atol=1e-6)
    g2 = m.numeric_grad(lambda t: (t[0, 0] * t[1, 1]), x)   # mixed: only two non-zero entries
    assert torch.allclose(g2, torch.tensor([[3.0, 0.0], [0.0, 1.0]], dtype=torch.float64), atol=1e-6)
    assert torch.equal(x, torch.tensor([[1.0, -2.0], [0.5, 3.0]], dtype=torch.float64))  # restored


def test_rel_error(load):
    m = load("ex08_gradient_check")
    assert m.rel_error(torch.tensor([1.0, 2.0]), torch.tensor([1.0, 2.0])) == 0.0
    assert m.rel_error(torch.tensor([1.0]), torch.tensor([3.0])) == pytest.approx(0.5)
    assert m.rel_error(torch.zeros(2), torch.zeros(2)) == 0.0


def test_swish_forward_and_backward(load):
    m = load("ex08_gradient_check")
    torch.manual_seed(1)
    x = torch.randn(5, 4, dtype=torch.float64) * 3
    assert torch.allclose(m.Swish.apply(x), torch.nn.functional.silu(x))
    xa = x.clone().requires_grad_(True)
    m.Swish.apply(xa).sum().backward()
    xb = x.clone().requires_grad_(True)
    torch.nn.functional.silu(xb).sum().backward()
    assert torch.allclose(xa.grad, xb.grad)
    assert m.check(m.Swish.apply, x) < 1e-7
    assert torch.autograd.gradcheck(m.Swish.apply, (x.clone().requires_grad_(True),))


def test_check_catches_buggy_backward(load):
    m = load("ex08_gradient_check")
    torch.manual_seed(2)
    x = torch.randn(6, dtype=torch.float64)
    assert m.check(m.BuggySwish.apply, x) > 1e-3


def test_numeric_grad_restores_each_coordinate(load):
    m = load("ex08_gradient_check")
    x = torch.tensor([2.0, 5.0], dtype=torch.float64)
    g = m.numeric_grad(lambda t: t[0] * t[1], x, eps=1e-3)   # bilinear: central diff is exact
    assert torch.allclose(g, torch.tensor([5.0, 2.0], dtype=torch.float64), atol=1e-9)
