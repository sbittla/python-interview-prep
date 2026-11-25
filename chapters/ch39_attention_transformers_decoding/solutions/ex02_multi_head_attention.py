"""
Exercise 02 — Lab: Multi-Head Attention (reshape, transpose, merge)   [Tier: ★ Core]
Chapter 39 · Pattern: (B, T, D) -> (B, H, T, D/H) -> attend -> merge · Target time: 30 min

Problem
-------
x has shape (B, T, D); H divides D; d_h = D // H. Parameters are a dict with weight matrices
``Wq, Wk, Wv, Wo`` of shape (D, D) and biases ``bq, bk, bv, bo`` of shape (D,), used as
``x @ W + b``. Implement

- ``split_heads(x, H)``: (B, T, D) -> (B, H, T, d_h); head h owns feature columns
  [h·d_h, (h+1)·d_h).
- ``merge_heads(x)``: the exact inverse, (B, H, T, d_h) -> (B, T, D).
- ``mha(x, params, H, mask=None)``: project, split, scaled dot-product attention per head
  (mask broadcastable to (B, H, T, T), True = attend), merge, output projection.
- ``mha_param_count(D)`` = 4·D² + 4·D.

Examples
--------
>>> split_heads(np.arange(8.0).reshape(1, 2, 4), 2)[0].tolist()
[[[0.0, 1.0], [4.0, 5.0]], [[2.0, 3.0], [6.0, 7.0]]]

Constraints
-----------
- D % H == 0 (raise ValueError otherwise). float64.

Approach ladder
---------------
1. Brute force — loop over heads: slice columns of Q, K, V, call single-head attention, then
   concatenate. Same O(B·T²·D + B·T·D²) arithmetic, H Python iterations.
2. Optimal    — one reshape + transpose to (B, H, T, d_h) and a single batched matmul. No
   copies beyond the transpose; the H heads run as one batched GEMM. Time
   O(B·T·D²) for projections + O(B·T²·D) for attention; memory O(B·H·T²) for the weights.

Follow-ups
----------
- Why not ``x.reshape(B, H, T, d_h)`` directly? It slices the *flattened* (T, D) block, so a
  "head" mixes features of different tokens. Reshape to (B, T, H, d_h) first, then transpose.
- Cost of H heads vs 1 head of width D: the same FLOPs; heads only partition the features.
- Grouped-query attention: n_kv_heads < H; each K/V head is shared by H / n_kv_heads query heads
  (``np.repeat`` along the head axis). Multi-query attention is n_kv_heads = 1.
- PyTorch ``nn.MultiheadAttention`` packs Wq, Wk, Wv in ``in_proj_weight`` (3D, D) and computes
  ``x @ W.T``, so its rows are our columns.
- Edge cases: H = 1 (plain attention), H = D (d_h = 1), T = 1, D % H != 0.
"""
from __future__ import annotations

import math

import numpy as np


def masked_softmax(s: np.ndarray, mask=None) -> np.ndarray:
    if mask is not None:
        s = np.where(mask, s, -np.inf)
    m = s.max(axis=-1, keepdims=True)
    e = np.exp(s - np.where(np.isfinite(m), m, 0.0))
    z = e.sum(axis=-1, keepdims=True)
    return np.divide(e, z, out=np.zeros_like(e), where=z > 0)


def attention(q, k, v, mask=None):
    s = q @ np.swapaxes(k, -1, -2) / math.sqrt(q.shape[-1])
    return masked_softmax(s, mask) @ v


def init_params(D: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    p = {f"W{n}": rng.standard_normal((D, D)) / math.sqrt(D) for n in "qkvo"}
    p.update({f"b{n}": 0.1 * rng.standard_normal(D) for n in "qkvo"})
    return p


def split_heads(x: np.ndarray, H: int) -> np.ndarray:
    B, T, D = x.shape
    if D % H:
        raise ValueError(f"D={D} is not divisible by H={H}")
    return x.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)


def merge_heads(x: np.ndarray) -> np.ndarray:
    B, H, T, dh = x.shape
    return x.transpose(0, 2, 1, 3).reshape(B, T, H * dh)


def split_heads_wrong(x: np.ndarray, H: int) -> np.ndarray:
    """Wrong-but-tempting: reshape straight to (B, H, T, d_h)."""
    B, T, D = x.shape
    return x.reshape(B, H, T, D // H)


def mha(x, params, H: int, mask=None, splitter=split_heads):
    q = splitter(x @ params["Wq"] + params["bq"], H)
    k = splitter(x @ params["Wk"] + params["bk"], H)
    v = splitter(x @ params["Wv"] + params["bv"], H)
    return merge_heads(attention(q, k, v, mask)) @ params["Wo"] + params["bo"]


def mha_loop(x, params, H: int, mask=None):
    """Rung 1: one head at a time on column slices."""
    D = x.shape[-1]
    if D % H:
        raise ValueError(f"D={D} is not divisible by H={H}")
    dh = D // H
    q, k, v = (x @ params[f"W{n}"] + params[f"b{n}"] for n in "qkv")
    heads = [attention(q[..., h * dh:(h + 1) * dh], k[..., h * dh:(h + 1) * dh],
                       v[..., h * dh:(h + 1) * dh], mask) for h in range(H)]
    return np.concatenate(heads, axis=-1) @ params["Wo"] + params["bo"]


def mha_param_count(D: int) -> int:
    return 4 * D * D + 4 * D


def main() -> None:
    x = np.arange(8.0).reshape(1, 2, 4)
    print("split_heads example:", split_heads(x, 2)[0].tolist())
    print("wrong reshape      :", split_heads_wrong(x, 2)[0].tolist(), "<- token 0 and 1 mixed")

    rng = np.random.default_rng(392)
    B, T, D, H = 2, 5, 8, 2
    x = rng.standard_normal((B, T, D))
    p = init_params(D, rng)
    causal = np.tril(np.ones((T, T), bool))
    y = mha(x, p, H, causal)
    print("output shape:", y.shape, " merge(split(x)) == x:", np.array_equal(merge_heads(split_heads(x, H)), x))
    print("fused == per-head loop:", np.allclose(y, mha_loop(x, p, H, causal)))
    print("wrong split differs   :", not np.allclose(y, mha(x, p, H, causal, split_heads_wrong)))
    print("H=1 equals single attention:",
          np.allclose(mha(x, p, 1), attention(*(x @ p[f"W{n}"] + p[f"b{n}"] for n in "qkv")) @ p["Wo"] + p["bo"]))
    print("y[0, :2] =", y[0, :2].round(3).tolist())
    print("param count D=8:", mha_param_count(8), " D=768:", mha_param_count(768))
    try:
        split_heads(x, 3)
    except ValueError as e:
        print("H=3:", e)

    try:
        import torch
    except ImportError:
        print("torch not installed: skipping cross-check")
        return
    ref = torch.nn.MultiheadAttention(D, H, batch_first=True, dtype=torch.float64)
    with torch.no_grad():
        ref.in_proj_weight.copy_(torch.from_numpy(np.concatenate([p["Wq"].T, p["Wk"].T, p["Wv"].T])))
        ref.in_proj_bias.copy_(torch.from_numpy(np.concatenate([p["bq"], p["bk"], p["bv"]])))
        ref.out_proj.weight.copy_(torch.from_numpy(p["Wo"].T))
        ref.out_proj.bias.copy_(torch.from_numpy(p["bo"]))
        xt = torch.from_numpy(x)
        # nn.MultiheadAttention: bool attn_mask True = NOT allowed, the opposite of our mask.
        out, _ = ref(xt, xt, xt, attn_mask=torch.from_numpy(~causal), need_weights=False)
    print("matches torch nn.MultiheadAttention:", np.allclose(out.numpy(), y),
          "| torch param count:", sum(t.numel() for t in ref.parameters()))


if __name__ == "__main__":
    main()
