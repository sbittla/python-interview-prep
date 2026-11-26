"""
Exercise 01 — Lab: Scaled Dot-Product Attention with Masks        [Tier: ★ Core]
Chapter 39 · Pattern: scores -> mask -> stable softmax -> weighted sum · Target time: 25 min

Problem
-------
Q has shape (..., n, d_k), K has shape (..., m, d_k), V has shape (..., m, d_v); leading batch
dimensions broadcast. ``mask`` is an optional boolean array broadcastable to (..., n, m) where
True means "query i may attend to key j". Return ``(out, weights)``:

    scores  = Q K^T / sqrt(d_k)                     (..., n, m)
    weights = softmax(scores with masked entries = -inf, axis=-1)
    out     = weights V                             (..., n, d_v)

A query row whose keys are *all* masked has no defined softmax (0/0). This exercise returns
zero weights and a zero output for such rows, and never NaN.

``attention_large_negative`` is the tempting alternative that fills masked scores with -1e9
instead of -inf; show how it behaves on a fully masked row.

Examples
--------
>>> Q = K = np.eye(2); V = np.array([[1.0, 0.0], [0.0, 1.0]])
>>> out, w = attention(Q, K, V, mask=np.array([[True, False], [True, True]]))
>>> w.round(4).tolist()
[[1.0, 0.0], [0.3302, 0.6698]]

Constraints
-----------
- float64; n, m >= 1; d_k >= 1. Time O(n·m·d), memory O(n·m) for the weights.

Approach ladder
---------------
1. Brute force — a Python loop over queries and keys: n·m dot products of length d_k, then a
   per-row softmax. O(n·m·d) arithmetic, but with interpreter overhead per element.
2. Optimal    — two matmuls and a vectorised, max-shifted softmax (→ §35.10): same
   O(n·m·(d_k + d_v)) arithmetic, O(n·m) memory, works on any batch shape. A fused kernel
   (FlashAttention-style) keeps the arithmetic but streams key blocks with an online softmax,
   so it never stores the n×m matrix.

Why sqrt(d_k)
-------------
If the entries of q and k are independent with mean 0 and variance 1, q·k is a sum of d_k terms
of variance 1, so Var(q·k) = d_k. Without scaling, large d_k gives scores of size ~sqrt(d_k):
the softmax saturates to near one-hot and its gradient (p_i(δ_ij - p_j)) is close to 0.
Dividing by sqrt(d_k) restores unit variance at initialisation.

Follow-ups
----------
- Why mask before the softmax, not after? Zeroing weights after softmax leaves rows that no
  longer sum to 1 (and renormalising is just a slower softmax with -inf).
- -inf vs -1e9: -1e9 gives exp(-1e9 - max) = 0 when at least one key is valid, so the two agree;
  on a fully masked row -1e9 gives a *uniform* average over every (masked) value: silent leak.
  In float16, -1e9 overflows to -inf anyway (max finite ≈ 65504).
- Library behaviour on a fully masked row is path-dependent (torch 2.15 CPU, see ``main``):
  SDPA returned zeros; ``nn.MultiheadAttention`` returned NaN with ``need_weights=True`` and
  zeros with ``need_weights=False``, except its eval-mode no-grad fast path, which gave NaN.
- PyTorch: ``F.scaled_dot_product_attention`` bool mask True = attend; ``nn.MultiheadAttention``
  bool ``attn_mask`` True = *blocked*. Opposite conventions.
- Cross-attention: n != m (decoder queries, encoder keys); the code above already handles it.
- Edge cases: n = 1 query, m = 1 key, fully masked row, mask with broadcast batch dims,
  very large scores (1e3) -> the max shift prevents overflow.
"""
from __future__ import annotations

import math

import numpy as np


def masked_softmax(scores: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Softmax over the last axis; masked entries get weight 0; fully masked rows are all 0."""
    s = np.asarray(scores, dtype=float)
    if mask is not None:
        s = np.where(mask, s, -np.inf)
    m = s.max(axis=-1, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)            # fully masked row: avoid -inf - -inf = NaN
    e = np.exp(s - m)                               # exp(-inf) = 0
    total = e.sum(axis=-1, keepdims=True)
    return np.divide(e, total, out=np.zeros_like(e), where=total > 0)


def attention(Q, K, V, mask=None):
    Q, K, V = (np.asarray(a, dtype=float) for a in (Q, K, V))
    scores = Q @ np.swapaxes(K, -1, -2) / math.sqrt(Q.shape[-1])
    weights = masked_softmax(scores, mask)
    return weights @ V, weights


def attention_loop(Q, K, V, mask=None):
    """Rung 1 for a single (n, d) problem: explicit loops, same policy for masked rows."""
    Q, K, V = (np.asarray(a, dtype=float) for a in (Q, K, V))
    n, m = Q.shape[0], K.shape[0]
    out = np.zeros((n, V.shape[1]))
    weights = np.zeros((n, m))
    scale = 1.0 / math.sqrt(Q.shape[1])
    for i in range(n):
        allowed = [j for j in range(m) if mask is None or mask[i][j]]
        if not allowed:
            continue                                 # fully masked: zero row
        s = {j: float(Q[i] @ K[j]) * scale for j in allowed}
        top = max(s.values())
        exps = {j: math.exp(v - top) for j, v in s.items()}
        z = sum(exps.values())
        for j, e in exps.items():
            weights[i, j] = e / z
            out[i] += weights[i, j] * V[j]
    return out, weights


def attention_large_negative(Q, K, V, mask, fill: float = -1e9):
    """Wrong-but-tempting on fully masked rows: fill with a big negative number."""
    Q, K, V = (np.asarray(a, dtype=float) for a in (Q, K, V))
    scores = Q @ np.swapaxes(K, -1, -2) / math.sqrt(Q.shape[-1])
    s = np.where(mask, scores, fill)
    s = s - s.max(axis=-1, keepdims=True)
    w = np.exp(s)
    w /= w.sum(axis=-1, keepdims=True)
    return w @ V, w


def score_std(d_k: int, scaled: bool, rng: np.random.Generator, samples: int = 4000) -> float:
    q = rng.standard_normal((samples, d_k))
    k = rng.standard_normal((samples, d_k))
    s = (q * k).sum(axis=1)
    return float((s / math.sqrt(d_k) if scaled else s).std())


def mean_max_weight(d_k: int, scaled: bool, rng: np.random.Generator, m: int = 16) -> float:
    """Average largest softmax weight over 200 random query/key sets (1/m = uniform)."""
    q = rng.standard_normal((200, 1, d_k))
    k = rng.standard_normal((200, m, d_k))
    s = (q @ np.swapaxes(k, -1, -2))[:, 0, :]
    if scaled:
        s = s / math.sqrt(d_k)
    return float(masked_softmax(s).max(axis=-1).mean())


def main() -> None:
    Q = K = np.eye(2)
    V = np.array([[1.0, 0.0], [0.0, 1.0]])
    out, w = attention(Q, K, V, mask=np.array([[True, False], [True, True]]))
    print("example weights:", w.round(4).tolist())

    rng = np.random.default_rng(39)
    Q, K, V = rng.standard_normal((4, 8)), rng.standard_normal((5, 8)), rng.standard_normal((5, 3))
    mask = np.array([[1, 1, 0, 0, 1], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0]], bool)
    out, w = attention(Q, K, V, mask)
    out_l, w_l = attention_loop(Q, K, V, mask)
    print("loop == vectorised:", np.allclose(out, out_l) and np.allclose(w, w_l))
    print("row sums:", w.sum(axis=1).round(6).tolist(), " (row 1 fully masked)")
    print("weights:\n", w.round(3))
    print("fully masked row output:", out[1].round(3).tolist(), "any NaN:", bool(np.isnan(out).any()))

    out_n, w_n = attention_large_negative(Q, K, V, mask)
    print("-1e9 fill: rows with a valid key match -inf:", np.allclose(out_n[[0, 2, 3]], out[[0, 2, 3]]))
    print("-1e9 fill: fully masked row weights:", w_n[1].round(3).tolist(), "<- uniform leak")

    big = attention(np.full((1, 4), 1000.0), np.full((3, 4), 1000.0), np.eye(3))[1]
    print("scores ~ 1e6, no overflow:", big.round(4).tolist())

    Qb, Kb, Vb = (rng.standard_normal((2, 3, 6, 4)) for _ in range(3))
    causal = np.tril(np.ones((6, 6), bool))
    print("batched (2, 3, 6, 4) causal output shape:", attention(Qb, Kb, Vb, causal)[0].shape)

    print("\nscore std  d_k   unscaled  scaled   mean max softmax weight (m=16)")
    for d in (4, 64, 512):
        r1, r2 = np.random.default_rng(d), np.random.default_rng(d + 1)
        print(f"          {d:>4}   {score_std(d, False, r1):7.2f}  {score_std(d, True, r1):6.2f}"
              f"   unscaled {mean_max_weight(d, False, r2):.3f}  scaled {mean_max_weight(d, True, r2):.3f}")

    try:
        import torch
        import torch.nn.functional as F
    except ImportError:                              # torch is optional for this file
        print("torch not installed: skipping cross-check")
        return
    t = lambda a: torch.from_numpy(np.ascontiguousarray(a))
    ref = F.scaled_dot_product_attention(t(Qb), t(Kb), t(Vb), attn_mask=t(causal)).numpy()
    print("\nmatches torch SDPA (causal, batched):", np.allclose(ref, attention(Qb, Kb, Vb, causal)[0]))
    ref2 = F.scaled_dot_product_attention(t(Q[None]), t(K[None]), t(V[None]), attn_mask=t(mask)).numpy()[0]
    print("torch SDPA fully masked row:", ref2[1].round(3).tolist(),
          "| valid rows match:", np.allclose(ref2[[0, 2, 3]], out[[0, 2, 3]]))
    print("nn.MultiheadAttention, fully masked row has NaN?")
    for need_weights, training, grad in [(True, True, True), (False, True, True), (False, False, False)]:
        has_nan = torch_mha_masked_row_is_nan(need_weights, training, grad)
        print(f"  need_weights={need_weights!s:<5} train={training!s:<5} grad={grad!s:<5} -> {has_nan}")


def torch_mha_masked_row_is_nan(need_weights: bool, training: bool, grad: bool) -> bool:
    """Does torch's nn.MultiheadAttention give NaN on a fully masked query row? (path-dependent)"""
    import torch
    torch.manual_seed(0)
    x = torch.randn(1, 3, 4, dtype=torch.float64)
    allowed = torch.tensor([[True, True, False], [False, False, False], [True, True, True]])
    mha = torch.nn.MultiheadAttention(4, 2, batch_first=True, dtype=torch.float64).train(training)
    with torch.set_grad_enabled(grad):
        out, _ = mha(x, x, x, attn_mask=~allowed, need_weights=need_weights)   # True = blocked
    return bool(torch.isnan(out[0, 1]).any())


if __name__ == "__main__":
    main()
