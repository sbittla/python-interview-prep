"""
Exercise 07 — Lab: Mini GPT Forward Pass                          [Tier: ★ Core]
Chapter 39 · Pattern: embed -> N pre-LN causal blocks -> final LN -> tied head · Target time: 40 min

Problem
-------
Build a decoder-only language model in NumPy.

- ``init_gpt(V, T_max, D, H, L, rng)``: token embedding E (V, D), learned positions P
  (T_max, D), L pre-LN blocks (attention + MLP with F = 4D, as in ex06), a final LayerNorm.
  The output head is *tied*: logits = h @ E^T (no separate (D, V) matrix).
- ``forward(params, tokens)``: tokens (B, T) ints, T <= T_max -> logits (B, T, V). Position t
  sees tokens 0..t only (causal mask). Raise ValueError if T > T_max.
- ``count_params(params)`` and ``gpt_param_formula(V, T_max, D, L)`` =
  V·D + T_max·D + L·(12D² + 13D) + 2D; they must agree.
- ``next_token_loss(params, tokens)``: mean cross-entropy of predicting tokens[:, 1:] from
  logits[:, :-1] (log-softmax → §35.10).

Examples
--------
>>> gpt_param_formula(V=50257, T_max=1024, D=768, L=12)
124439808

Constraints
-----------
- Small sizes only (this is a CPU NumPy model); float64.

Hints
-----
- Embedding lookup is fancy indexing: ``E[tokens]`` has shape (B, T, D); add ``P[:T]``.
- Each block: x = x + attn(LN(x)); x = x + MLP(LN(x)); then a final LN and ``@ E.T``.
- ``np.tril(np.ones((T, T), bool))`` is the causal mask.
- Loss: log-softmax (→ §35.10), then ``np.take_along_axis`` with tokens[:, 1:].

Follow-ups
----------
- Sanity check at init: with small random weights the loss is ≈ ln V (uniform guess).
- Why tie the head? It saves V·D parameters (a large share for small models with big
  vocabularies) and shares meaning between input and output tokens.
- Training this model is a standard PyTorch loop (→ §37.5); tokens come from a tokenizer
  (→ §38.2) and E is an embedding lookup (→ §38.7).
- Edge cases: T = 1, T = T_max, T > T_max (raise), batch of one.
"""
from __future__ import annotations

import math

import numpy as np


def layer_norm(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + eps) * g + b


def gelu(z):
    return 0.5 * z * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (z + 0.044715 * z ** 3)))


def init_gpt(V: int, T_max: int, D: int, H: int, L: int, rng: np.random.Generator) -> dict:
    s = 0.02
    blocks = []
    for _ in range(L):
        b = {f"W{n}": s * rng.standard_normal((D, D)) for n in "qkvo"}
        b.update({f"b{n}": np.zeros(D) for n in "qkvo"})
        b.update(W1=s * rng.standard_normal((D, 4 * D)), b1=np.zeros(4 * D),
                 W2=s * rng.standard_normal((4 * D, D)), b2=np.zeros(D),
                 g1=np.ones(D), be1=np.zeros(D), g2=np.ones(D), be2=np.zeros(D))
        blocks.append(b)
    return {"E": s * rng.standard_normal((V, D)), "P": s * rng.standard_normal((T_max, D)),
            "blocks": blocks, "gf": np.ones(D), "bf": np.zeros(D), "H": H}


def attention(x, b, H):
    raise NotImplementedError("TODO")


def forward(params: dict, tokens) -> np.ndarray:
    raise NotImplementedError("TODO")


def forward_prefix_loop(params: dict, tokens) -> np.ndarray:
    """Rung 1: re-run the model on every prefix, keep its last position."""
    raise NotImplementedError("TODO")


def count_params(params: dict) -> int:
    raise NotImplementedError("TODO")


def gpt_param_formula(V: int, T_max: int, D: int, L: int) -> int:
    raise NotImplementedError("TODO")


def next_token_loss(params: dict, tokens) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    rng = np.random.default_rng(397)
    V, T_max, D, H, L = 50, 16, 32, 4, 2
    params = init_gpt(V, T_max, D, H, L, rng)
    tokens = rng.integers(0, V, size=(2, 10))
    logits = forward(params, tokens)
    print("tokens shape:", tokens.shape, "-> logits shape:", logits.shape)
    print("one pass == prefix-by-prefix:", np.allclose(logits, forward_prefix_loop(params, tokens)))

    changed = tokens.copy()
    changed[:, 6:] = (changed[:, 6:] + 1) % V
    moved = ~np.isclose(forward(params, changed), logits).all(axis=(0, 2))
    print("changing tokens 6..9 moves logits at positions:", np.where(moved)[0].tolist())

    print("params counted:", count_params(params), " formula:", gpt_param_formula(V, T_max, D, L))
    print("GPT-2-small-shaped config (V=50257, T=1024, D=768, L=12):", f"{gpt_param_formula(50257, 1024, 768, 12):,}")
    print(f"loss at init: {next_token_loss(params, tokens):.4f}  ln V = {math.log(V):.4f}")
    print("greedy next token per sequence:", logits[:, -1].argmax(-1).tolist())
    try:
        forward(params, np.zeros((1, 17), int))
    except ValueError as e:
        print("T=17:", e)


if __name__ == "__main__":
    main()
