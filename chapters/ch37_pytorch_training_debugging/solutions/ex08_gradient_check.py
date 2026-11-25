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

Approach ladder
---------------
1. Eyeball the loss curve — a wrong gradient often still decreases the loss, so this proves
   nothing.
2. Forward differences (f(x + eps) - f(x)) / eps — O(P) evaluations, error O(eps).
3. Optimal check — central differences, error O(eps^2), 2P evaluations, in float64; or
   ``torch.autograd.gradcheck``, which does the same with tolerances. Why move up: each rung
   detects smaller bugs. Autograd itself costs one backward, so the check is only for tests.

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
    x = x.detach().clone()
    grad = torch.zeros_like(x)
    flat, gflat = x.view(-1), grad.view(-1)          # views: writing flat[i] edits x
    for i in range(flat.numel()):
        old = flat[i].item()
        flat[i] = old + eps
        plus = f(x).item()
        flat[i] = old - eps
        minus = f(x).item()
        flat[i] = old
        gflat[i] = (plus - minus) / (2 * eps)
    return grad


def rel_error(a: torch.Tensor, b: torch.Tensor) -> float:
    return ((a - b).norm() / (a.norm() + b.norm()).clamp_min(1e-12)).item()


class Swish(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x * torch.sigmoid(x)

    @staticmethod
    def backward(ctx, grad_out):
        (x,) = ctx.saved_tensors
        s = torch.sigmoid(x)
        return grad_out * (s + x * s * (1 - s))          # chain rule: upstream * local


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
    x = x.detach().to(torch.float64).requires_grad_(True)
    fn(x).sum().backward()
    num = numeric_grad(lambda t: fn(t).sum(), x.detach())
    return rel_error(x.grad, num)


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
