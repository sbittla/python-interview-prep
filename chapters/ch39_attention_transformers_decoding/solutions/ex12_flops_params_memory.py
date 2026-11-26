"""
Exercise 12 — Parameter, FLOP and Memory Calculator for a GPT-style Model   [Tier: ◆ Extended]
Chapter 39 · Pattern: count matmuls (2·m·k·n FLOPs each) and tensor sizes · Target time: 25 min

Problem
-------
For a decoder-only model with vocabulary V, width D, L pre-LN layers, MLP width F (default 4D),
learned positions T_max, tied output head, implement

- ``gpt_params(V, T_max, D, L, F=None)`` = V·D + T_max·D + L·(4D² + 4D + 2DF + F + D + 4D) + 2D.
- ``forward_matmul_flops(V, D, L, T, F=None)``: exact matmul FLOPs (2·m·k·n per (m,k)@(k,n))
  of one forward pass over T tokens with the *full* T×T score matrix (no skipping of masked
  entries): per layer 2T·D·3D (QKV) + 2T²D (QK^T) + 2T²D (AV) + 2T·D² (out) + 4T·D·F (MLP),
  plus 2T·D·V for the head. Elementwise work (softmax, LN, GELU) is ignored.
- ``count_forward_flops(...)``: run a real NumPy forward with a counting matmul and return the
  total; it must equal ``forward_matmul_flops``.
- ``flops_per_token_rule(N_matmul, L, T, D)`` = 2·N_matmul + 2·L·T·D, the usual estimate
  (2 FLOPs per weight per token, plus attention with the causal half of the scores);
  training ≈ 3× forward ≈ 6·N_matmul per token (backward ≈ 2× forward).
- ``attention_scores_bytes(B, H, T, bytes_per)`` = B·H·T²·bytes for one layer's score matrix
  if it is materialised.

Examples
--------
>>> forward_matmul_flops(V=10, D=4, L=1, T=3) // 3      # per token, F = 16
512

Constraints
-----------
- Integers only; F defaults to 4·D.

Approach ladder
---------------
1. Brute force — instrument a real forward pass and add up every matmul (``count_forward_flops``):
   exact, but costs a forward pass and only works at toy sizes.
2. Optimal    — closed form per layer: O(1) to evaluate for any size; verified against rung 1.
   Per token: 2·(12·L·D² + D·V) + 4·L·T·D (full scores). The full-score attention FLOPs
   (4·L·T·D) equal the per-layer dense FLOPs (24·L·D², head excluded) at T = 6D; counting only
   the causal half (2·L·T·D) they are equal at T = 12D. ``split_flops`` recovers both terms
   from ``forward_matmul_flops`` alone.

Follow-ups
----------
- Attention is O(T²·D) compute and, if the scores are stored, O(B·H·T²) memory per layer;
  fused attention kernels stream over key blocks with an online softmax so the extra memory
  is O(T) per head, but the compute stays O(T²·D).
- Inference memory = weights (N·bytes) + KV cache (→ ex08) + activations; at long context
  the cache can exceed the weights.
- A decode step reads every weight once to do 2N FLOPs for one token per sequence, so small
  batches are memory-bandwidth bound; batching raises FLOPs per byte read.
- Edge cases: F != 4D, T = 1 (decode step: attention term 4·L·D·t with the cache length t),
  untied head (+V·D parameters, same FLOPs).
"""
from __future__ import annotations

import math

import numpy as np


def gpt_params(V: int, T_max: int, D: int, L: int, F: int | None = None) -> int:
    F = 4 * D if F is None else F
    per_layer = (4 * D * D + 4 * D) + (2 * D * F + F + D) + 4 * D
    return V * D + T_max * D + L * per_layer + 2 * D


def matmul_params(V: int, D: int, L: int, F: int | None = None) -> int:
    """Weights that take part in a matmul per token (head included, biases/LN/positions not)."""
    F = 4 * D if F is None else F
    return L * (4 * D * D + 2 * D * F) + D * V


def forward_matmul_flops(V: int, D: int, L: int, T: int, F: int | None = None) -> int:
    F = 4 * D if F is None else F
    per_layer = 2 * T * D * 3 * D + 2 * T * T * D + 2 * T * T * D + 2 * T * D * D + 2 * 2 * T * D * F
    return L * per_layer + 2 * T * D * V


def split_flops(V: int, D: int, L: int, T: int, F: int | None = None) -> tuple[int, int, int]:
    """(attention, dense-without-head, head) FLOPs per token at length T, from the exact count.

    forward_matmul_flops is a·T² + b·T, so a and b come from T = 1 and T = 2.
    """
    f1, f2 = forward_matmul_flops(V, D, L, 1, F), forward_matmul_flops(V, D, L, 2, F)
    a = (f2 - 2 * f1) // 2
    head = 2 * D * V
    return a * T, f1 - a - head, head


def flops_per_token_rule(n_matmul: int, L: int, T: int, D: int) -> int:
    return 2 * n_matmul + 2 * L * T * D


def attention_scores_bytes(B: int, H: int, T: int, bytes_per: int) -> int:
    return B * H * T * T * bytes_per


class Counter:
    def __init__(self):
        self.flops = 0

    def mm(self, a, b):
        self.flops += 2 * math.prod(a.shape[:-1]) * a.shape[-1] * b.shape[-1]
        return a @ b


def count_forward_flops(V: int, D: int, L: int, T: int, H: int, F: int | None = None, seed: int = 0) -> int:
    F = 4 * D if F is None else F
    rng = np.random.default_rng(seed)
    c = Counter()
    E = rng.standard_normal((V, D)) * 0.1
    x = E[rng.integers(0, V, T)][None]                               # (1, T, D)
    ln = lambda z: (z - z.mean(-1, keepdims=True)) / np.sqrt(z.var(-1, keepdims=True) + 1e-5)
    for _ in range(L):
        W = {n: rng.standard_normal(s) * 0.1 for n, s in
             dict(qkv=(D, 3 * D), o=(D, D), w1=(D, F), w2=(F, D)).items()}
        q, k, v = np.split(c.mm(ln(x), W["qkv"]), 3, axis=-1)
        split = lambda a: a.reshape(1, T, H, D // H).transpose(0, 2, 1, 3)
        q, k, v = split(q), split(k), split(v)
        s = c.mm(q, k.transpose(0, 1, 3, 2)) / math.sqrt(D // H)
        s = np.where(np.tril(np.ones((T, T), bool)), s, -np.inf)
        w = np.exp(s - s.max(-1, keepdims=True))
        w /= w.sum(-1, keepdims=True)
        a = c.mm(w, v).transpose(0, 2, 1, 3).reshape(1, T, D)
        x = x + c.mm(a, W["o"])
        x = x + c.mm(np.maximum(c.mm(ln(x), W["w1"]), 0), W["w2"])
    c.mm(ln(x), E.T)
    return c.flops


def gib(n: float) -> str:
    return f"{n / 2**30:.2f} GiB"


def main() -> None:
    print("per-token FLOPs, V=10 D=4 L=1 T=3:", forward_matmul_flops(10, 4, 1, 3) // 3)
    for args in [(50, 16, 2, 8, 4), (37, 24, 3, 5, 2), (11, 8, 1, 1, 1)]:
        V, D, L, T, H = args
        print(f"V={V} D={D} L={L} T={T}: counted={count_forward_flops(V, D, L, T, H)} "
              f"formula={forward_matmul_flops(V, D, L, T)}")

    V, T_max, D, L = 50257, 1024, 768, 12            # a GPT-2-small-shaped config
    n_mm = matmul_params(V, D, L)
    print(f"\nconfig V={V} T_max={T_max} D={D} L={L}")
    print(f"  total params {gpt_params(V, T_max, D, L):,}; matmul params {n_mm:,}")
    for T in (128, 1024):
        exact = forward_matmul_flops(V, D, L, T) / T
        rule = flops_per_token_rule(n_mm, L, T, D)
        print(f"  T={T:>4}: exact full-score forward {exact / 1e6:.1f} MFLOP/token, "
              f"rule 2N+2LTD {rule / 1e6:.1f}, training ~6N {6 * n_mm / 1e6:.1f}")
    for T in (6 * D, 12 * D):
        att, dense, head = split_flops(V, D, L, T)
        print(f"  T={T:>5}: attention {att / 1e6:.1f}, causal half {att / 2e6:.1f}, "
              f"dense (no head) {dense / 1e6:.1f}, head {head / 1e6:.1f} MFLOP/token")

    print("\nscore-matrix memory per layer (H=32, B=1, fp32):")
    for T in (2048, 8192, 32768):
        print(f"  T={T:>5}: {gib(attention_scores_bytes(1, 32, T, 4))}")

    try:
        import torch
    except ImportError:
        print("torch not installed: skipping cross-check")
        return
    D, L, V, T_max = 64, 3, 100, 32
    layers = [torch.nn.TransformerEncoderLayer(D, 4, 4 * D, batch_first=True, norm_first=True) for _ in range(L)]
    modules = [torch.nn.Embedding(V, D), torch.nn.Embedding(T_max, D), *layers, torch.nn.LayerNorm(D)]
    n_torch = sum(p.numel() for m in modules for p in m.parameters())
    print(f"\ntorch module count (tied head) {n_torch} == formula {gpt_params(V, T_max, D, L)}:",
          n_torch == gpt_params(V, T_max, D, L))


if __name__ == "__main__":
    main()
