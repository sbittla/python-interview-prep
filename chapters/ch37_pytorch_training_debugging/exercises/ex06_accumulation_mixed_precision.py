"""
Exercise 06 — Gradient accumulation and mixed precision        [Tier: ◆ Extended]
Chapter 37 · Pattern: micro-batches, loss scaling · Target time: 30 min

Problem
-------
1. ``full_batch_grads(model, X, y)``: gradients (list of tensors, one per parameter) of the
   mean-squared error over the whole batch.
2. ``accumulated_grads(model, X, y, micro, scale_loss=True)``: split X into ``micro`` equal
   chunks, call ``backward`` on each chunk's loss *without* zeroing in between, and return the
   accumulated gradients. With ``scale_loss=True`` each chunk loss is divided by ``micro`` so the
   result equals ``full_batch_grads``; with False it is ``micro`` times too large (the bug).
3. ``fp16_roundtrip(value, scale)``: cast ``value * scale`` to float16 and back, divide by
   ``scale``; returns the float32 result. Shows underflow (small gradients become 0) and
   overflow (inf) — the reason fp16 training multiplies the loss by a scale factor.
4. ``DynamicLossScaler``: the GradScaler policy without CUDA. ``update(found_inf)`` halves the
   scale (and the caller skips the step) on inf/NaN gradients; after ``growth_interval``
   consecutive good steps it doubles the scale.
5. ``autocast_dtypes()``: under ``torch.autocast("cpu", dtype=torch.bfloat16)`` report the
   dtypes of a Linear layer's output, its weight, and the loss computed after casting back.

Examples
--------
>>> fp16_roundtrip(1e-8, 1.0), fp16_roundtrip(1e-8, 2.0**16) > 0
(0.0, True)

Constraints
-----------
- len(X) divisible by ``micro``; the model has no batch norm (batch statistics would differ
  per micro-batch, so accumulation would not be exact).

Hints
-----
- ``X.chunk(micro)`` splits along dim 0; zero the gradients once, before the loop.
- With mean losses, each chunk's loss divided by ``micro`` sums to the full-batch loss.
- ``torch.tensor(v).to(torch.float16)`` rounds to fp16; values below ~6e-8 become 0.
- Scaler: inf -> halve and reset the streak; ``growth_interval`` good steps -> double.

Wrong-but-tempting
------------------
- Not dividing by ``micro``: gradients ``micro`` times too large (an effective LR change).
- Calling ``zero_grad`` inside the chunk loop: only the last chunk's gradient survives.

Follow-ups
----------
- Where does gradient clipping go with accumulation? After the last micro-batch, right before
  ``step``; with a GradScaler call ``scaler.unscale_(opt)`` first so the norm is in real units.
- Unequal last chunk: weight each chunk loss by its size / B instead of 1/k.
- Why are master weights kept in fp32? Updates lr * g are often below fp16/bf16 resolution of
  the weight and would round to no change.
"""
from __future__ import annotations

import torch
from torch import nn

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def _loss(model: nn.Module, X: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    return ((model(X).squeeze(-1) - y) ** 2).mean()


def full_batch_grads(model: nn.Module, X, y) -> list[torch.Tensor]:
    raise NotImplementedError("TODO")


def accumulated_grads(model: nn.Module, X, y, micro: int,
                      scale_loss: bool = True) -> list[torch.Tensor]:
    raise NotImplementedError("TODO")


def fp16_roundtrip(value: float, scale: float) -> float:
    raise NotImplementedError("TODO")


class DynamicLossScaler:
    def __init__(self, init_scale: float = 2.0**16, growth_interval: int = 3) -> None:
        raise NotImplementedError("TODO")

    def update(self, found_inf: bool) -> bool:
        """Return True if the optimizer step should run."""
        raise NotImplementedError("TODO")


def autocast_dtypes() -> tuple[torch.dtype, torch.dtype, torch.dtype]:
    raise NotImplementedError("TODO")


def main() -> None:
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(3, 8), nn.Tanh(), nn.Linear(8, 1)).double()
    X, y = torch.randn(12, 3, dtype=torch.float64), torch.randn(12, dtype=torch.float64)
    full = full_batch_grads(model, X, y)
    for k in (1, 3, 4):
        acc = accumulated_grads(model, X, y, k)
        print(f"micro={k}: accumulated == full batch:",
              all(torch.allclose(a, f) for a, f in zip(acc, full)))
    bad = accumulated_grads(model, X, y, 4, scale_loss=False)
    ratio = (bad[0].norm() / full[0].norm()).item()
    print(f"forgot to divide by micro=4: grad norm ratio = {ratio:.2f}")

    print("fp16 max:", torch.finfo(torch.float16).max, " bf16 max ~", f"{torch.finfo(torch.bfloat16).max:.2e}")
    for v, s in [(1e-8, 1.0), (1e-8, 2.0**16), (1e-3, 1.0), (1e-3, 2.0**27)]:
        print(f"fp16_roundtrip({v:g}, scale={s:g}) -> {fp16_roundtrip(v, s):.3g}")

    scaler = DynamicLossScaler(init_scale=1024.0, growth_interval=3)
    trace = []
    for found_inf in [False, False, False, True, False, True, False]:
        stepped = scaler.update(found_inf)
        trace.append(f"{'inf' if found_inf else 'ok'}:{'step' if stepped else 'skip'}:{scaler.scale:g}")
    print("scaler trace:", " ".join(trace))

    out_dt, w_dt, loss_dt = autocast_dtypes()
    print("autocast cpu bf16 -> linear out:", out_dt, " weight:", w_dt, " loss:", loss_dt)


if __name__ == "__main__":
    main()
