"""
Exercise 09 — Debugging shape errors and NaNs                  [Tier: ★ Core]
Chapter 37 · Pattern: instrument with hooks, assert shapes, localise the first bad value
Target time: 30 min

Problem
-------
1. ``shape_trace(model, x)``: register a forward hook on every leaf module, run ``model(x)``,
   remove the hooks, and return ``[(name, output_shape_tuple), ...]`` in execution order.
2. ``first_nonfinite(model, x)``: same hooks; return the name of the first leaf module whose
   output contains NaN or inf, or ``None`` if every output is finite.
3. ``checked_mse(pred, target)``: raise ``ValueError`` when the shapes differ (instead of letting
   broadcasting turn (N, 1) vs (N,) into an (N, N) loss); otherwise return the MSE.
4. ``naive_cross_entropy(logits, y)``: -log(softmax(logits))[range(N), y].mean(), written the
   naive way (exp, divide, log). ``stable_cross_entropy`` uses ``log_softmax`` (log-sum-exp,
   -> §35.10). Show the naive one returns inf/NaN for large logits.
5. ``diverges(lr, steps)``: gradient descent on f(w) = w**2 from w = 1; return True if w becomes
   non-finite within ``steps`` (lr > 1 makes |w| grow by |1 - 2 lr| per step).

Examples
--------
>>> shape_trace(nn.Sequential(nn.Linear(4, 3), nn.ReLU()), torch.randn(2, 4))
[('0', (2, 3)), ('1', (2, 3))]

Constraints
-----------
- Hooks must be removed even if the forward raises (use ``try/finally``).

Approach ladder
---------------
1. Print statements inside ``forward`` — edits the model code, easy to leave behind.
2. Forward hooks on every leaf — no code change, O(L) hooks, one forward pass, finds the first
   bad layer; ``torch.autograd.set_detect_anomaly(True)`` does the same for the *backward*
   pass (slow: debugging only).
3. Prevent rather than find — assert shapes at the loss, use fused stable losses
   (``cross_entropy`` on logits), clip gradients, lower the LR. Why move up: rungs 1-2 find
   the bug once; rung 3 stops the next one.

Follow-ups
----------
- ``x.view`` fails on non-contiguous tensors (after ``transpose``); ``reshape`` copies if needed.
- Common NaN sources: log(0), sqrt at 0 in backward, division by a zero std, fp16 overflow,
  exploding LR. Check the inputs too: one NaN in the data spreads to every weight it touches.
- ``nn.MSELoss`` only *warns* on mismatched shapes; ``cross_entropy`` raises on a float target
  of the wrong shape. Do not rely on either.
"""
from __future__ import annotations

import warnings

import torch
import torch.nn.functional as F
from torch import nn

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def _leaves(model: nn.Module):
    return [(n, m) for n, m in model.named_modules() if not list(m.children())]


def shape_trace(model: nn.Module, x: torch.Tensor) -> list[tuple[str, tuple[int, ...]]]:
    trace = []
    handles = [m.register_forward_hook(
        lambda mod, inp, out, name=name: trace.append((name, tuple(out.shape))))
        for name, m in _leaves(model)]
    try:
        model(x)
    finally:
        for h in handles:
            h.remove()
    return trace


def first_nonfinite(model: nn.Module, x: torch.Tensor) -> str | None:
    bad: list[str] = []

    def hook(name):
        def fn(mod, inp, out):
            if not bad and not torch.isfinite(out).all():
                bad.append(name)
        return fn

    handles = [m.register_forward_hook(hook(name)) for name, m in _leaves(model)]
    try:
        with torch.no_grad():
            model(x)
    finally:
        for h in handles:
            h.remove()
    return bad[0] if bad else None


def checked_mse(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    if pred.shape != target.shape:
        raise ValueError(f"shape mismatch: pred {tuple(pred.shape)} vs target {tuple(target.shape)}")
    return ((pred - target) ** 2).mean()


def naive_cross_entropy(logits: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    p = logits.exp() / logits.exp().sum(dim=1, keepdim=True)   # exp(1000) = inf -> inf/inf = nan
    return -p.log()[torch.arange(len(y)), y].mean()


def stable_cross_entropy(logits: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    return -F.log_softmax(logits, dim=1)[torch.arange(len(y)), y].mean()


def diverges(lr: float, steps: int = 2000) -> bool:
    w = torch.tensor(1.0, requires_grad=True)
    for _ in range(steps):
        loss = w ** 2
        (g,) = torch.autograd.grad(loss, w)
        with torch.no_grad():
            w -= lr * g
        if not torch.isfinite(w):
            return True
    return False


class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.body = nn.Sequential(nn.Linear(4, 8), nn.ReLU())
        self.head = nn.Linear(8, 1)

    def forward(self, x):
        return self.head(self.body(x))


def main() -> None:
    torch.manual_seed(0)
    net = Net()
    print("shape trace:", shape_trace(net, torch.randn(5, 4)))
    print("first non-finite (clean input):", first_nonfinite(net, torch.randn(5, 4)))
    with torch.no_grad():
        net.head.weight[0, 0] = float("inf")
    print("first non-finite (inf weight in head):", first_nonfinite(net, torch.ones(5, 4)))

    pred, target = torch.randn(6, 1), torch.randn(6)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        silent = F.mse_loss(pred, target)
    print("broadcast (6,1)-(6,) ->", tuple((pred - target).shape),
          "| mse_loss warned:", any("target size" in str(w.message) for w in caught),
          "| equals correct loss:", torch.allclose(silent, F.mse_loss(pred.squeeze(1), target)))
    try:
        checked_mse(pred, target)
    except ValueError as e:
        print("checked_mse:", e)
    print("checked_mse after squeeze(1) ok:", torch.allclose(checked_mse(pred.squeeze(1), target),
                                                            F.mse_loss(pred.squeeze(1), target)))

    logits, y = torch.tensor([[1000.0, 0.0], [0.0, 1000.0]]), torch.tensor([0, 1])
    print("naive CE on large logits:", naive_cross_entropy(logits, y).item(),
          " stable:", stable_cross_entropy(logits, y).item(),
          " F.cross_entropy:", F.cross_entropy(logits, y).item())
    small = torch.randn(4, 3)
    yy = torch.tensor([0, 2, 1, 0])
    print("stable == F.cross_entropy on small logits:",
          torch.allclose(stable_cross_entropy(small, yy), F.cross_entropy(small, yy)))
    print("diverges: lr=0.4", diverges(0.4), " lr=0.9", diverges(0.9), " lr=1.1", diverges(1.1))

    x = torch.tensor([0.0, 4.0], requires_grad=True)
    try:
        with torch.autograd.set_detect_anomaly(True):
            (torch.sqrt(x) * 0).sum().backward()      # d sqrt at 0 is inf; inf * 0 = nan
    except RuntimeError as e:
        print("anomaly mode names the op:", "SqrtBackward0" in str(e))
    t = torch.randn(2, 3).T
    try:
        t.view(6)
    except RuntimeError:
        print("view on transposed tensor -> RuntimeError; reshape gives", tuple(t.reshape(6).shape))


if __name__ == "__main__":
    main()
