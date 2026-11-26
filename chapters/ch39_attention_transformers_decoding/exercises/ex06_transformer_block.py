"""
Exercise 06 — Lab: A Transformer Block Forward Pass (Pre-LN and Post-LN)   [Tier: ★ Core]
Chapter 39 · Pattern: x + f(norm(x)), twice · Target time: 35 min

Problem
-------
x has shape (B, T, D). A block has multi-head self-attention (weights as in ex02), an MLP
D -> F -> D with GELU (tanh approximation), and two LayerNorms. Implement

    pre-LN  (norm_first=True):   h = x + MHA(LN1(x));   y = h + MLP(LN2(h))
    post-LN (norm_first=False):  h = LN1(x + MHA(x));   y = LN2(h + MLP(h))

``gelu(z) = 0.5 z (1 + tanh(sqrt(2/pi) (z + 0.044715 z³)))``.
``block_param_count(D, F)`` = 4D² + 4D (attention) + 2DF + F + D (MLP) + 4D (two LNs);
with F = 4D that is 12D² + 13D.

Examples
--------
>>> block_param_count(768, 3072)
7087872

Constraints
-----------
- D % H == 0; mask (optional) broadcastable to (B, H, T, T), True = attend. float64.

Hints
-----
- ``layer_norm`` and ``mha`` (ex02) are given; parameters are in ``init_block``.
- Pre-LN: the norm sits inside each residual branch; Post-LN: after each residual add.
- The per-token rung can call ``mha`` on the whole normalised sequence and keep column t.
- Count: attention 4D² + 4D, MLP 2DF + F + D, two LayerNorms 4D.

Follow-ups
----------
- Why residuals? The identity path gives every layer a direct gradient route; each block
  learns a small update to the "residual stream".
- Pre-LN vs Post-LN: Post-LN (the 2017 original) normalises after the add and is harder to train
  deep without warm-up; Pre-LN keeps an un-normalised residual stream and needs a final LN
  before the output head (§39.6).
- Where do the FLOPs go? Per token per layer ≈ 2·(4D² + 2DF) for the matmuls; with F = 4D the
  MLP is two thirds of it (→ ex12).
- Gated MLPs (SwiGLU-style) use three matrices D×F', often with F' ≈ (2/3)·4D to keep the count.
- Edge cases: T = 1, H = 1, a causal mask, post-LN output has per-token mean 0.
"""
from __future__ import annotations

import math

import numpy as np


def layer_norm(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + eps) * g + b


def gelu(z):
    raise NotImplementedError("TODO")


def mha(x, p, H, mask=None):
    B, T, D = x.shape
    split = lambda a: a.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    q, k, v = (split(x @ p[f"W{n}"] + p[f"b{n}"]) for n in "qkv")
    s = q @ k.transpose(0, 1, 3, 2) / math.sqrt(D // H)
    if mask is not None:
        s = np.where(mask, s, -np.inf)
    w = np.exp(s - s.max(-1, keepdims=True))
    w /= w.sum(-1, keepdims=True)
    return (w @ v).transpose(0, 2, 1, 3).reshape(B, T, D) @ p["Wo"] + p["bo"]


def mlp(x, p):
    raise NotImplementedError("TODO")


def block(x, p, H, mask=None, norm_first: bool = True):
    raise NotImplementedError("TODO")


def block_per_token(x, p, H, mask=None):
    """Rung 1 (pre-LN): output position t recomputed on its own."""
    raise NotImplementedError("TODO")


def init_block(D: int, F: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    p = {f"W{n}": rng.standard_normal((D, D)) / math.sqrt(D) for n in "qkvo"}
    p.update({f"b{n}": 0.02 * rng.standard_normal(D) for n in "qkvo"})
    p.update(W1=rng.standard_normal((D, F)) / math.sqrt(D), b1=0.02 * rng.standard_normal(F),
             W2=rng.standard_normal((F, D)) / math.sqrt(F), b2=0.02 * rng.standard_normal(D),
             g1=1 + 0.1 * rng.standard_normal(D), be1=0.1 * rng.standard_normal(D),
             g2=1 + 0.1 * rng.standard_normal(D), be2=0.1 * rng.standard_normal(D))
    return p


def block_param_count(D: int, F: int) -> int:
    raise NotImplementedError("TODO")


def to_torch(p, D, H, F, norm_first):
    import torch
    import torch.nn.functional as tF
    layer = torch.nn.TransformerEncoderLayer(
        D, H, dim_feedforward=F, dropout=0.0, batch_first=True, norm_first=norm_first,
        activation=lambda z: tF.gelu(z, approximate="tanh"), dtype=torch.float64)
    t = lambda a: torch.from_numpy(np.ascontiguousarray(a))
    with torch.no_grad():
        sa = layer.self_attn
        sa.in_proj_weight.copy_(t(np.concatenate([p["Wq"].T, p["Wk"].T, p["Wv"].T])))
        sa.in_proj_bias.copy_(t(np.concatenate([p["bq"], p["bk"], p["bv"]])))
        sa.out_proj.weight.copy_(t(p["Wo"].T)); sa.out_proj.bias.copy_(t(p["bo"]))
        layer.linear1.weight.copy_(t(p["W1"].T)); layer.linear1.bias.copy_(t(p["b1"]))
        layer.linear2.weight.copy_(t(p["W2"].T)); layer.linear2.bias.copy_(t(p["b2"]))
        layer.norm1.weight.copy_(t(p["g1"])); layer.norm1.bias.copy_(t(p["be1"]))
        layer.norm2.weight.copy_(t(p["g2"])); layer.norm2.bias.copy_(t(p["be2"]))
    return layer.eval()


def main() -> None:
    rng = np.random.default_rng(396)
    B, T, D, H, F = 2, 5, 8, 2, 32
    x = rng.standard_normal((B, T, D))
    p = init_block(D, F, rng)
    causal = np.tril(np.ones((T, T), bool))
    pre = block(x, p, H, causal, norm_first=True)
    post = block(x, p, H, causal, norm_first=False)
    print("pre-LN output shape:", pre.shape, " y[0, 0, :4] =", pre[0, 0, :4].round(4).tolist())
    print("per-token rung == whole sequence:", np.allclose(block_per_token(x, p, H, causal), pre))
    print("post-LN: (y - beta2) / gamma2 has per-token mean 0:", np.allclose(((post - p["be2"]) / p["g2"]).mean(-1), 0, atol=1e-9),
          "| pre-LN is not normalised:", not np.allclose(pre.mean(-1), 0, atol=1e-3))
    print("params D=8, F=32:", block_param_count(8, 32), " D=768, F=3072:", block_param_count(768, 3072),
          " 12D^2+13D:", 12 * 768 ** 2 + 13 * 768)

    try:
        import torch
    except ImportError:
        print("torch not installed: skipping cross-check")
        return
    xt = torch.from_numpy(x)
    blocked = torch.from_numpy(~causal)          # torch convention: True = NOT allowed
    for nf, ours in ((True, pre), (False, post)):
        layer = to_torch(p, D, H, F, nf)
        with torch.no_grad():
            ref = layer(xt, src_mask=blocked).numpy()
        print(f"matches torch TransformerEncoderLayer(norm_first={nf}):", np.allclose(ref, ours),
              "| torch params:", sum(q.numel() for q in layer.parameters()))


if __name__ == "__main__":
    main()
