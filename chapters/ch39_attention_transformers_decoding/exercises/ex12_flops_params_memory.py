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

Hints
-----
- A matmul (m, k) @ (k, n) costs 2·m·k·n FLOPs (one multiply + one add per term).
- List the matmuls of one layer: QKV, QK^T, AV, output projection, two MLP matrices.
- ``Counter.mm`` (given) counts FLOPs for any batched matmul shape.
- ``split_flops``: the exact count is a·T² + b·T; evaluate it at T = 1 and T = 2.

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
    raise NotImplementedError("TODO")


def matmul_params(V: int, D: int, L: int, F: int | None = None) -> int:
    """Weights that take part in a matmul per token (head included, biases/LN/positions not)."""
    raise NotImplementedError("TODO")


def forward_matmul_flops(V: int, D: int, L: int, T: int, F: int | None = None) -> int:
    raise NotImplementedError("TODO")


def split_flops(V: int, D: int, L: int, T: int, F: int | None = None) -> tuple[int, int, int]:
    """(attention, dense-without-head, head) FLOPs per token at length T, from the exact count.

    forward_matmul_flops is a·T² + b·T, so a and b come from T = 1 and T = 2.
    """
    raise NotImplementedError("TODO")


def flops_per_token_rule(n_matmul: int, L: int, T: int, D: int) -> int:
    raise NotImplementedError("TODO")


def attention_scores_bytes(B: int, H: int, T: int, bytes_per: int) -> int:
    raise NotImplementedError("TODO")


class Counter:
    def __init__(self):
        self.flops = 0

    def mm(self, a, b):
        self.flops += 2 * math.prod(a.shape[:-1]) * a.shape[-1] * b.shape[-1]
        return a @ b


def count_forward_flops(V: int, D: int, L: int, T: int, H: int, F: int | None = None, seed: int = 0) -> int:
    raise NotImplementedError("TODO")


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
