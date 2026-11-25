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

Approach ladder (fitting a large effective batch)
-------------------------------------------------
1. Shrink the batch until it fits — memory O(B_small) activations, but a different (noisier)
   optimisation; hyper-parameters tuned for the big batch no longer apply.
2. Accumulate k micro-batches of B/k, then one step — same gradient as batch B for mean
   losses (divide each by k); activation memory O(B/k); k forward/backward passes, so about the
   same total compute, less parallelism.
3. Also use mixed precision — bf16/fp16 halves activation memory and speeds up matmuls on
   hardware that supports it; fp16 needs loss scaling, bf16 (fp32's exponent range) usually
   does not. Why move up: rung 2 fixes memory, rung 3 also buys speed.

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
    model.zero_grad()
    _loss(model, X, y).backward()
    return [p.grad.clone() for p in model.parameters()]


def accumulated_grads(model: nn.Module, X, y, micro: int,
                      scale_loss: bool = True) -> list[torch.Tensor]:
    if len(X) % micro:
        raise ValueError("len(X) must be divisible by micro")
    model.zero_grad()                                   # once, before the first chunk
    for xc, yc in zip(X.chunk(micro), y.chunk(micro)):
        loss = _loss(model, xc, yc)
        (loss / micro if scale_loss else loss).backward()   # .grad accumulates (+=)
    return [p.grad.clone() for p in model.parameters()]


def fp16_roundtrip(value: float, scale: float) -> float:
    scaled = torch.tensor(value * scale, dtype=torch.float32).to(torch.float16)
    return (scaled.to(torch.float32) / scale).item()


class DynamicLossScaler:
    def __init__(self, init_scale: float = 2.0**16, growth_interval: int = 3) -> None:
        self.scale = init_scale
        self.growth_interval = growth_interval
        self.good_steps = 0

    def update(self, found_inf: bool) -> bool:
        """Return True if the optimizer step should run."""
        if found_inf:
            self.scale /= 2                             # back off, skip this step
            self.good_steps = 0
            return False
        self.good_steps += 1
        if self.good_steps == self.growth_interval:     # stable for a while: try bigger
            self.scale *= 2
            self.good_steps = 0
        return True


def autocast_dtypes() -> tuple[torch.dtype, torch.dtype, torch.dtype]:
    lin = nn.Linear(4, 1)
    x, y = torch.randn(3, 4), torch.randn(3)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        out = lin(x)                                    # matmul runs in bf16
        loss = ((out.float().squeeze(-1) - y) ** 2).mean()   # loss in fp32
    return out.dtype, lin.weight.dtype, loss.dtype


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
