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

Approach ladder
---------------
1. Brute force — for each t, run the model on the prefix tokens[:, :t+1] and keep the last
   row: T forward passes, O(T²·L·D²) for the projections alone. This is exactly what
   generation without a KV cache does (→ ex08).
2. Optimal    — one causal forward over all T positions: O(L·(T·D² + T²·D)) and every
   position's logits at once (that is how training gets T predictions per sequence).
   Tested: rung 1 and rung 2 produce identical logits, which also proves the mask is causal.

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
    B, T, D = x.shape
    split = lambda a: a.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    q, k, v = (split(x @ b[f"W{n}"] + b[f"b{n}"]) for n in "qkv")
    s = q @ k.transpose(0, 1, 3, 2) / math.sqrt(D // H)
    s = np.where(np.tril(np.ones((T, T), bool)), s, -np.inf)       # causal
    w = np.exp(s - s.max(-1, keepdims=True))
    w /= w.sum(-1, keepdims=True)
    return (w @ v).transpose(0, 2, 1, 3).reshape(B, T, D) @ b["Wo"] + b["bo"]


def forward(params: dict, tokens) -> np.ndarray:
    tokens = np.asarray(tokens)
    B, T = tokens.shape
    if T > params["P"].shape[0]:
        raise ValueError(f"sequence length {T} exceeds T_max={params['P'].shape[0]}")
    x = params["E"][tokens] + params["P"][:T]                      # (B, T, D)
    for b in params["blocks"]:
        x = x + attention(layer_norm(x, b["g1"], b["be1"]), b, params["H"])
        x = x + gelu(layer_norm(x, b["g2"], b["be2"]) @ b["W1"] + b["b1"]) @ b["W2"] + b["b2"]
    x = layer_norm(x, params["gf"], params["bf"])
    return x @ params["E"].T                                        # tied head


def forward_prefix_loop(params: dict, tokens) -> np.ndarray:
    """Rung 1: re-run the model on every prefix, keep its last position."""
    tokens = np.asarray(tokens)
    return np.stack([forward(params, tokens[:, :t + 1])[:, -1] for t in range(tokens.shape[1])], axis=1)


def count_params(params: dict) -> int:
    n = params["E"].size + params["P"].size + params["gf"].size + params["bf"].size
    return n + sum(a.size for b in params["blocks"] for a in b.values())


def gpt_param_formula(V: int, T_max: int, D: int, L: int) -> int:
    return V * D + T_max * D + L * (12 * D * D + 13 * D) + 2 * D


def next_token_loss(params: dict, tokens) -> float:
    tokens = np.asarray(tokens)
    z = forward(params, tokens)[:, :-1]
    m = z.max(-1, keepdims=True)
    logp = z - (m + np.log(np.exp(z - m).sum(-1, keepdims=True)))
    tgt = tokens[:, 1:]
    return float(-np.take_along_axis(logp, tgt[..., None], -1).mean())


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
