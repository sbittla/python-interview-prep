import pytest
import torch


def test_poly_grad(load):
    m = load("ex01_tensors_autograd")
    assert m.poly_grad([0.0, 1.0, -2.0]) == [2.0, 5.0, 14.0]
    xs = [0.5, -1.5, 3.0]
    assert m.poly_grad(xs) == pytest.approx([3 * x * x + 2 for x in xs])


def test_mse_grad_matches_closed_form_and_leaves_input(load):
    m = load("ex01_tensors_autograd")
    torch.manual_seed(1)
    X = torch.randn(10, 4, dtype=torch.float64)
    y = torch.randn(10, dtype=torch.float64)
    w = torch.randn(4, dtype=torch.float64)
    g = m.mse_grad(X, y, w)
    assert torch.allclose(g, m.closed_form_mse_grad(X, y, w))
    assert torch.allclose(g, 2 / 10 * X.T @ (X @ w - y))
    assert w.grad is None and not w.requires_grad


@pytest.mark.parametrize("x0, times, expected", [(3.0, 3, [6.0, 12.0, 18.0]), (-1.0, 1, [-2.0]),
                                                 (0.0, 2, [0.0, 0.0])])
def test_accumulation(load, x0, times, expected):
    assert load("ex01_tensors_autograd").accumulated_grads(x0, times) == expected


def test_pick_device(load):
    m = load("ex01_tensors_autograd")
    assert m.pick_device("cpu") == torch.device("cpu")
    expected = "cuda" if torch.cuda.is_available() else "cpu"
    assert m.pick_device("cuda").type == expected
