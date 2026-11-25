"""
Exercise 01 — Tensors, autograd and devices                    [Tier: ★ Core]
Chapter 37 · Pattern: reverse-mode autodiff · Target time: 20 min

Problem
-------
Warm-up on the four autograd facts interviewers probe:

1. ``poly_grad(xs)``: for f(x) = x**3 + 2x evaluated element-wise at ``xs`` (a list of floats),
   return df/dx at each point using autograd (sum the outputs, call ``backward`` once).
2. ``mse_grad(X, y, w)``: gradient of the mean-squared error ``mean((X @ w - y) ** 2)`` with
   respect to ``w`` via autograd; ``closed_form_mse_grad`` returns 2/N * X^T (X w - y).
3. ``accumulated_grads(x0, times)``: call ``backward`` on y = x**2 ``times`` times (rebuilding
   the graph each time, never zeroing) and return the list of ``x.grad`` values after each call.
   Gradients *add up* in ``.grad``: this is why training loops call ``zero_grad``.
4. ``pick_device(prefer)``: return ``torch.device("cuda")`` when ``prefer == "cuda"`` and CUDA
   is available, else ``torch.device("cpu")``.

Examples
--------
>>> poly_grad([0.0, 1.0, -2.0])
[2.0, 5.0, 14.0]
>>> accumulated_grads(3.0, 3)
[6.0, 12.0, 18.0]

Constraints
-----------
- Inputs are small (<= 1000 elements); use float64 for exact comparisons in tests.

Approach ladder
---------------
1. Derive by hand — exact, but every model change means new algebra; error-prone.
2. Finite differences — 2 evaluations per parameter, O(P) forward passes for P parameters;
   approximate (truncation vs round-off error). Kept for *checking* (Exercise 08).
3. Optimal — reverse-mode autograd: one forward that records the graph, one backward that
   costs a small constant times the forward, O(1) passes for any P. Why move up: P is
   millions in a real model.

Follow-ups
----------
- Why is ``x.grad`` None for a non-leaf tensor? (Only leaves keep ``.grad``; call
  ``retain_grad()`` on an intermediate to keep it.)
- What does ``torch.no_grad()`` change? (No graph is recorded: lower memory, outputs have
  ``requires_grad=False``.) ``detach()`` returns a tensor cut from the graph but sharing storage.
- Why does a second ``backward`` on the same graph fail? (Saved tensors are freed; pass
  ``retain_graph=True`` only when you really need it.)
"""
from __future__ import annotations

import torch

torch.set_num_threads(1)


def poly_grad(xs: list[float]) -> list[float]:
    x = torch.tensor(xs, dtype=torch.float64, requires_grad=True)
    y = x**3 + 2 * x
    y.sum().backward()               # d(sum)/dx_i = f'(x_i): elements are independent
    return x.grad.tolist()


def mse_grad(X: torch.Tensor, y: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    w = w.detach().clone().requires_grad_(True)   # fresh leaf; never mutate the caller's tensor
    loss = ((X @ w - y) ** 2).mean()
    loss.backward()
    return w.grad


def closed_form_mse_grad(X: torch.Tensor, y: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    return 2.0 / X.shape[0] * X.T @ (X @ w - y)


def accumulated_grads(x0: float, times: int) -> list[float]:
    x = torch.tensor(x0, dtype=torch.float64, requires_grad=True)
    seen = []
    for _ in range(times):
        (x**2).backward()            # new graph each time; .grad is NOT reset
        seen.append(x.grad.item())
    return seen


def pick_device(prefer: str = "cuda") -> torch.device:
    if prefer == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main() -> None:
    print("poly_grad([0, 1, -2]) =", poly_grad([0.0, 1.0, -2.0]))
    torch.manual_seed(0)
    X = torch.randn(8, 3, dtype=torch.float64)
    y = torch.randn(8, dtype=torch.float64)
    w = torch.zeros(3, dtype=torch.float64)
    g = mse_grad(X, y, w)
    print("autograd == closed form:", torch.allclose(g, closed_form_mse_grad(X, y, w)))
    print("caller's w untouched:", w.requires_grad is False and w.grad is None)
    print("accumulated_grads(3.0, 3) =", accumulated_grads(3.0, 3))

    a = torch.tensor([1.0, 2.0], requires_grad=True)
    b = a * 2                                   # non-leaf
    b.retain_grad()
    (b ** 2).sum().backward()
    print("leaf a.grad:", a.grad.tolist(), " retained b.grad:", b.grad.tolist())
    with torch.no_grad():
        c = a * 2
    print("under no_grad requires_grad:", c.requires_grad, " detach shares storage:",
          a.detach().data_ptr() == a.data_ptr())
    x = torch.tensor(2.0, requires_grad=True)
    z = x.exp()
    z.backward()
    try:
        z.backward()
    except RuntimeError as e:
        print("second backward raises RuntimeError:", "second time" in str(e))
    print("broadcast (3,1) + (4,) ->", tuple((torch.ones(3, 1) + torch.ones(4)).shape))
    print("pick_device('cpu') ->", pick_device("cpu").type,
          "| pick_device('cuda') in {cpu, cuda}:", pick_device("cuda").type in {"cpu", "cuda"})


if __name__ == "__main__":
    main()
