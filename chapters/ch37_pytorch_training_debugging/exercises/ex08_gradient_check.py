"""
Exercise 08 — Gradient check against finite differences        [Tier: ◆ Extended]
Chapter 37 · Pattern: numeric vs analytic gradients · Target time: 30 min

Problem
-------
1. ``numeric_grad(f, x, eps=1e-6)``: central differences, (f(x + eps e_i) - f(x - eps e_i)) / 2eps
   for every element i of ``x`` (any shape); ``f`` returns a scalar tensor.
2. ``rel_error(a, b)``: ||a - b|| / max(||a|| + ||b||, 1e-12) with L2 norms, as a float.
   (Element-wise ratios blow up where the true gradient is ~0, e.g. swish at x = -11.)
3. ``Swish`` — a custom ``torch.autograd.Function`` for f(x) = x * sigmoid(x) with a
   hand-written ``backward``: f'(x) = s + x s (1 - s), s = sigmoid(x).
   ``BuggySwish`` (provided) forgets the x s (1 - s) term.
4. ``check(fn, x)``: compare autograd (through ``fn``) with ``numeric_grad`` on ``fn(x).sum()``
   in float64; return the relative error.

Examples
--------
>>> check(Swish.apply, x) < 1e-7, check(BuggySwish.apply, x) > 1e-3
(True, True)

Constraints
-----------
- Check in float64: in float32, round-off (~1e-7 / eps) swamps the result.
- x has at most a few hundred elements (the check costs 2 evaluations per element).

Hints
-----
- Work on a detached clone; ``x.view(-1)`` lets you perturb one element at a time and restore it.
- In ``backward`` return ``grad_out * local_derivative``; get x from ``ctx.saved_tensors``.
- Check in float64.

Wrong-but-tempting
------------------
- Forgetting to restore the element after perturbing it: later coordinates are evaluated at
  the wrong point.
- Dividing the central difference by eps instead of 2 eps: every gradient doubles.

Follow-ups
----------
- Why not use finite differences to *train*? 2P forward passes per step vs one backward.
- Kinks (ReLU at 0, max ties): numeric and analytic gradients legitimately disagree there;
  pick points away from kinks.
- ``ctx.save_for_backward`` vs storing tensors on ``ctx`` directly: the former lets autograd
  detect in-place modification of saved tensors.
"""
from __future__ import annotations

import torch

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def numeric_grad(f, x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    raise NotImplementedError("TODO")


def rel_error(a: torch.Tensor, b: torch.Tensor) -> float:
    raise NotImplementedError("TODO")


class Swish(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        raise NotImplementedError("TODO")

    @staticmethod
    def backward(ctx, grad_out):
        raise NotImplementedError("TODO")


class BuggySwish(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x * torch.sigmoid(x)

    @staticmethod
    def backward(ctx, grad_out):
        (x,) = ctx.saved_tensors
        return grad_out * torch.sigmoid(x)               # BUG: drops x * s * (1 - s)


def check(fn, x: torch.Tensor) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    torch.manual_seed(0)
    x = torch.randn(4, 3, dtype=torch.float64)
    print("Swish rel error < 1e-7:", check(Swish.apply, x) < 1e-7)
    print("BuggySwish rel error > 1e-3:", check(BuggySwish.apply, x) > 1e-3)
    print("Swish matches F.silu:", torch.allclose(Swish.apply(x), torch.nn.functional.silu(x)))
    xg = x.clone().requires_grad_(True)
    print("gradcheck(Swish):", torch.autograd.gradcheck(Swish.apply, (xg,)))
    print("gradcheck(BuggySwish):",
          torch.autograd.gradcheck(BuggySwish.apply, (xg,), raise_exception=False))

    f = lambda t: (t ** 3).sum()
    x0 = torch.tensor([1.5], dtype=torch.float64)
    exact = 3 * 1.5 ** 2
    for eps in (1e-2, 1e-4):
        fwd = ((f(x0 + eps) - f(x0)) / eps).item()
        cen = numeric_grad(f, x0, eps).item()
        print(f"eps={eps:g}: forward-diff error {abs(fwd - exact):.1e}  central error {abs(cen - exact):.1e}")
    x32 = torch.randn(4, 3, dtype=torch.float32)
    err32 = rel_error(numeric_grad(lambda t: torch.nn.functional.silu(t).sum(), x32, 1e-6),
                      numeric_grad(lambda t: torch.nn.functional.silu(t).sum(), x32.double(), 1e-6).float())
    print("central diff in float32 with eps=1e-6 is unreliable (rel err > 1e-3):", err32 > 1e-3)


if __name__ == "__main__":
    main()
