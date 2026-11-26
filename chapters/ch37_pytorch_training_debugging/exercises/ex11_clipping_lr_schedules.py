"""
Exercise 11 — Gradient clipping and LR schedules in torch      [Tier: ◆ Extended]
Chapter 37 · Pattern: optimizer hygiene · Target time: 25 min

Problem
-------
The maths is built from scratch in §36.10; here you wire the torch APIs correctly.

1. ``clip_by_norm(grads, max_norm)``: scale *all* gradients by min(1, max_norm / total_norm),
   where total_norm is the L2 norm of every gradient concatenated. Return the pre-clip norm.
   Must match ``torch.nn.utils.clip_grad_norm_``.
2. ``warmup_cosine(step, warmup, total, base_lr)``: linear warm-up from base_lr/warmup to
   base_lr over ``warmup`` steps, then cosine decay reaching 0 at the last step (step total-1),
   so that final update is a no-op by design; use progress = (step - warmup) / (total - warmup)
   if the last step should still move the weights.
3. ``torch_schedule(warmup, total, base_lr)``: the same schedule via ``LambdaLR``; return the LR
   used at each of the ``total`` steps (read it *before* ``scheduler.step()``).
4. ``spike_run(clip)``: SGD on a linear model where one batch contains a huge outlier. Return
   the final loss on the clean data; clipping should keep the spike from wrecking the weights.

Examples
--------
>>> [round(warmup_cosine(s, 2, 6, 1.0), 3) for s in range(6)]
[0.5, 1.0, 0.854, 0.5, 0.146, 0.0]

Constraints
-----------
- 1 <= warmup < total.

Hints
-----
- total_norm = sqrt(sum of squared entries over *all* gradients); scale = min(1, max / total).
- ``LambdaLR`` multiplies the base LR by ``lr_lambda(step)``; read the LR before
  ``sched.step()``.
- Clip after ``backward()``, before ``opt.step()``.

Wrong-but-tempting
------------------
- Clipping each tensor separately to ``max_norm``: the total can be sqrt(k) times larger.
- Scaling up gradients whose norm is already below ``max_norm``.

Follow-ups
----------
- Calling ``scheduler.step()`` before ``optimizer.step()`` makes PyTorch warn and skips the
  first LR value.
- Per-step vs per-epoch schedulers: warm-up schedules are stepped per batch.
- ``clip_grad_norm_`` returns the total norm: log it, since spikes in it are the earliest sign of
  divergence.
"""
from __future__ import annotations

import math
import warnings

import torch
from torch import nn

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def clip_by_norm(grads: list[torch.Tensor], max_norm: float) -> float:
    raise NotImplementedError("TODO")


def warmup_cosine(step: int, warmup: int, total: int, base_lr: float) -> float:
    raise NotImplementedError("TODO")


def torch_schedule(warmup: int, total: int, base_lr: float) -> list[float]:
    raise NotImplementedError("TODO")


def spike_run(clip: float | None, steps: int = 40) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    torch.manual_seed(0)
    a = [torch.randn(3, 4), torch.randn(5)]
    b = [t.clone() for t in a]
    mine = clip_by_norm(a, 1.0)
    params = [nn.Parameter(torch.zeros_like(t)) for t in b]
    for p, t in zip(params, b):
        p.grad = t
    ref = nn.utils.clip_grad_norm_(params, 1.0).item()
    print(f"pre-clip norm {mine:.4f} matches torch: {math.isclose(mine, ref, rel_tol=1e-5)}")
    print("clipped grads match torch:", all(torch.allclose(x, p.grad) for x, p in zip(a, params)))
    print(f"post-clip norm: {math.sqrt(sum(float((t ** 2).sum()) for t in a)):.4f}")

    mine_lrs = [warmup_cosine(s, 2, 6, 0.1) for s in range(6)]
    torch_lrs = torch_schedule(2, 6, 0.1)
    print("warmup+cosine:", [round(v, 4) for v in mine_lrs])
    print("LambdaLR matches:", all(math.isclose(u, v, abs_tol=1e-12) for u, v in zip(mine_lrs, torch_lrs)))

    p = nn.Parameter(torch.zeros(1))
    opt = torch.optim.SGD([p], lr=0.1)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=1, gamma=0.5)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sched.step()                                  # wrong order: before opt.step()
    print("scheduler-before-optimizer warns:", any("optimizer.step()" in str(w.message) for w in caught))

    print(f"spike, no clipping: clean MSE {spike_run(None):.3g}")
    print(f"spike, clip_grad_norm_(1.0): clean MSE {spike_run(1.0):.3g}")


if __name__ == "__main__":
    main()
