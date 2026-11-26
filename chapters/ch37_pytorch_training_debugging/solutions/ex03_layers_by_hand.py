"""
Exercise 03 — Core layers by hand                              [Tier: ★ Core]
Chapter 37 · Pattern: re-implement and cross-check against torch · Target time: 40 min

Problem
-------
Using only tensor arithmetic (no ``torch.nn.functional`` layer calls), implement and match
PyTorch to 1e-6 in float64:

- ``linear(x, W, b)``: y = x W^T + b, W of shape (out, in) — PyTorch's layout.
- ``conv2d_loops`` and ``conv2d_unfold(x, w, b, stride=1, padding=0)``: x (N, C, H, W),
  w (F, C, k, k) -> (N, F, H', W') with H' = (H + 2p - k) // s + 1 (cross-correlation, like
  ``F.conv2d``; no kernel flip). ``F.pad`` and ``F.unfold`` are allowed: they only move data.
- ``batch_norm(x, gamma, beta, running_mean, running_var, training, momentum=0.1, eps=1e-5)``
  for x (N, C): training normalises with batch statistics (biased variance) and updates the
  running buffers *in place* with the *unbiased* variance:
  running = (1 - momentum) * running + momentum * batch_stat. Eval uses the running buffers.
- ``layer_norm(x, gamma, beta, eps=1e-5)``: normalise each row over its last dimension.
- ``dropout(x, p, training, generator)``: inverted dropout; keep with probability 1 - p and
  scale survivors by 1 / (1 - p); identity in eval mode or when p == 0.
- ``embedding(ids, table)``: row lookup, table[ids].

Examples
--------
>>> conv2d_unfold(torch.ones(1, 1, 3, 3), torch.ones(1, 1, 2, 2), torch.zeros(1)).tolist()
[[[[4.0, 4.0], [4.0, 4.0]]]]

Constraints
-----------
- 0 <= p < 1; N >= 2 for batch norm in training mode (PyTorch also raises for one value
  per channel).

Approach ladder (convolution)
-----------------------------
1. Nested Python loops over (n, f, i, j), each a C*k*k patch product — O(N F H' W' C k^2)
   multiply-adds, but N F H' W' Python-level tensor ops: correct, very slow.
2. Optimal — im2col: ``unfold`` copies every k x k patch into a column (N, C k^2, H' W'),
   then one matmul with w reshaped to (F, C k^2). Same FLOPs, one vectorised call; costs
   O(N C k^2 H' W') extra memory. Why move up: Python loop overhead dominates rung 1.

Approach ladder (batch norm)
----------------------------
1. Loop over channels computing mean/var per column — O(N C) work, C Python iterations.
2. Optimal — reduce over dim 0 in one call: O(N C) work, vectorised; update buffers under
   ``no_grad``. Why move up: C Python iterations dominate for wide layers, and in-graph buffer
   updates would leak state into autograd.

Follow-ups
----------
- Why the *unbiased* variance in the running buffer but the biased one to normalise?
  (PyTorch's documented convention; matters only for small N.)
- BatchNorm vs LayerNorm: batch norm couples examples in a batch and needs train/eval modes;
  layer norm is per-example, the same in train and eval — the transformer choice (-> §39.5).
- Why inverted dropout? Scaling during training keeps E[output] equal to the input, so eval
  needs no rescale.
- Embedding gradients: only looked-up rows get non-zero gradient (-> §38.7).
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def linear(x: torch.Tensor, W: torch.Tensor, b: torch.Tensor | None) -> torch.Tensor:
    y = x @ W.T
    return y + b if b is not None else y


def conv2d_loops(x, w, b, stride: int = 1, padding: int = 0) -> torch.Tensor:
    x = F.pad(x, (padding,) * 4)                     # zero-pad H and W on both sides
    N, C, H, W = x.shape
    Fo, _, k, _ = w.shape
    Ho, Wo = (H - k) // stride + 1, (W - k) // stride + 1
    out = torch.zeros(N, Fo, Ho, Wo, dtype=x.dtype)
    for n in range(N):
        for f in range(Fo):
            for i in range(Ho):
                for j in range(Wo):
                    patch = x[n, :, i * stride:i * stride + k, j * stride:j * stride + k]
                    out[n, f, i, j] = (patch * w[f]).sum() + b[f]   # C*k*k multiply-adds
    return out


def conv2d_unfold(x, w, b, stride: int = 1, padding: int = 0) -> torch.Tensor:
    N, C, H, W = x.shape
    Fo, _, k, _ = w.shape
    Ho, Wo = (H + 2 * padding - k) // stride + 1, (W + 2 * padding - k) // stride + 1
    cols = F.unfold(x, k, padding=padding, stride=stride)       # (N, C*k*k, Ho*Wo)
    out = w.reshape(Fo, -1) @ cols + b.reshape(1, Fo, 1)        # (N, F, Ho*Wo)
    return out.reshape(N, Fo, Ho, Wo)


def batch_norm(x, gamma, beta, running_mean, running_var, training: bool,
               momentum: float = 0.1, eps: float = 1e-5) -> torch.Tensor:
    if training:
        if x.shape[0] < 2:
            raise ValueError("batch norm in training mode needs more than 1 value per channel")
        mean = x.mean(dim=0)
        var = x.var(dim=0, unbiased=False)               # biased: used to normalise
        with torch.no_grad():                            # buffers are state, not graph
            running_mean.mul_(1 - momentum).add_(momentum * mean)
            running_var.mul_(1 - momentum).add_(momentum * x.var(dim=0, unbiased=True))
    else:
        mean, var = running_mean, running_var
    return gamma * (x - mean) / torch.sqrt(var + eps) + beta


def layer_norm(x, gamma, beta, eps: float = 1e-5) -> torch.Tensor:
    mean = x.mean(dim=-1, keepdim=True)
    var = x.var(dim=-1, unbiased=False, keepdim=True)
    return gamma * (x - mean) / torch.sqrt(var + eps) + beta


def dropout(x: torch.Tensor, p: float, training: bool,
            generator: torch.Generator | None = None) -> torch.Tensor:
    if not training or p == 0.0:
        return x
    keep = torch.rand(x.shape, generator=generator, dtype=x.dtype) >= p   # P(keep) = 1 - p
    return x * keep / (1 - p)


def embedding(ids: torch.Tensor, table: torch.Tensor) -> torch.Tensor:
    return table[ids]


def main() -> None:
    torch.manual_seed(0)
    d = torch.float64
    x, W, b = torch.randn(4, 5, dtype=d), torch.randn(3, 5, dtype=d), torch.randn(3, dtype=d)
    print("linear matches F.linear:", torch.allclose(linear(x, W, b), F.linear(x, W, b)))

    xi = torch.randn(2, 3, 6, 6, dtype=d)
    wk, bk = torch.randn(4, 3, 3, 3, dtype=d), torch.randn(4, dtype=d)
    for s, p in [(1, 0), (1, 1), (2, 1)]:
        ref = F.conv2d(xi, wk, bk, stride=s, padding=p)
        print(f"conv stride={s} pad={p}: shape {tuple(ref.shape)} loops ok:",
              torch.allclose(conv2d_loops(xi, wk, bk, s, p), ref),
              " unfold ok:", torch.allclose(conv2d_unfold(xi, wk, bk, s, p), ref))

    xb = torch.randn(8, 3, dtype=d) * 2 + 1
    bn = torch.nn.BatchNorm1d(3).double()
    rm, rv = torch.zeros(3, dtype=d), torch.ones(3, dtype=d)
    g, be = torch.ones(3, dtype=d), torch.zeros(3, dtype=d)
    print("batch_norm train matches:", torch.allclose(batch_norm(xb, g, be, rm, rv, True), bn(xb)))
    print("running buffers match:", torch.allclose(rm, bn.running_mean),
          torch.allclose(rv, bn.running_var))
    bn.eval()
    print("batch_norm eval matches:", torch.allclose(batch_norm(xb, g, be, rm, rv, False), bn(xb)))
    try:
        batch_norm(xb[:1], g, be, rm, rv, True)
    except ValueError:
        print("batch of 1 in training mode -> ValueError")

    gl, bl = torch.randn(5, dtype=d), torch.randn(5, dtype=d)
    print("layer_norm matches:", torch.allclose(layer_norm(x, gl, bl), F.layer_norm(x, (5,), gl, bl)))

    gen = torch.Generator().manual_seed(1)
    big = torch.ones(100_000, dtype=d)
    out = dropout(big, 0.25, True, gen)
    print("dropout keep rate ~0.75:", round((out != 0).double().mean().item(), 2),
          " survivors scaled to:", round(out.max().item(), 4), " mean ~1:", round(out.mean().item(), 2))
    print("dropout eval is identity:", torch.equal(dropout(big, 0.25, False), big))

    table, ids = torch.randn(10, 4, dtype=d), torch.tensor([[1, 3], [3, 9]])
    print("embedding matches:", torch.equal(embedding(ids, table), F.embedding(ids, table)),
          " shape:", tuple(embedding(ids, table).shape))


if __name__ == "__main__":
    main()
