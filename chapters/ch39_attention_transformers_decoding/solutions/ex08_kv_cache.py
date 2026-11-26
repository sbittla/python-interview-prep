"""
Exercise 08 — Lab: KV Cache that Matches Full Recompute            [Tier: ★ Core]
Chapter 39 · Pattern: cache K and V per layer; new queries attend to cache + self · Target time: 40 min

Problem
-------
The model (``init_model``, ``full_forward``) is the mini GPT of ex07, given. Implement

- ``KVCache(L, B, H, T_max, d_h)``: preallocated arrays ``k`` and ``v`` of shape
  (L, B, H, T_max, d_h) plus ``length`` (tokens stored so far). Stacked together that is the
  usual (L, 2, B, H, T, d_h) layout.
- ``extend(params, tokens, cache)``: tokens (B, n) are the *next* n tokens. Use positions
  length .. length+n-1, append their K and V to every layer, let the n queries attend to all
  length+n keys with a causal mask offset by ``length`` (→ ex03 ``causal_mask(n, n_k)``), return
  logits (B, n, V). n = prompt length is "prefill"; n = 1 is a decode step. Raise ValueError
  if the cache would overflow T_max.
- ``generate_greedy(params, prompt, steps, use_cache)``: same tokens either way.
- ``kv_cache_bytes(L, B, T, n_kv_heads, d_h, bytes_per_elem)`` = 2·L·B·T·n_kv_heads·d_h·bytes.

Examples
--------
>>> kv_cache_bytes(L=32, B=1, T=4096, n_kv_heads=32, d_h=128, bytes_per_elem=2) / 2**30
2.0

Constraints
-----------
- Logits from the cached path equal ``full_forward`` on the whole prefix (atol 1e-10).

Approach ladder
---------------
1. Brute force — no cache: at every step re-run ``full_forward`` on the whole prefix.
   Step t costs O(L·(t·D² + t²·D)); n generated tokens cost O(L·(n²·D² + n³·D)) overall.
2. Improved   — cache K, V but grow them with ``np.concatenate`` each step: correct, but each
   append copies the whole cache, O(t) bytes per step, O(n²) copying in total.
3. Optimal    — preallocated buffers written in place: step t costs O(L·(D² + t·D)) compute
   and O(1) amortised copying; memory O(L·B·T·H·d_h).

Follow-ups
----------
- Why cache K and V but not Q? The new query is used once; old queries are never needed again.
- Positions: the new token's position is ``cache.length``, not 0 (wrong-but-tempting; tested).
- Grouped-query attention stores n_kv_heads < H heads: the cache shrinks by H / n_kv_heads.
- Sizing at serve time: cache bytes grow linearly in B·T, so long contexts and big batches are
  limited by cache memory, not weights; paged allocation avoids reserving T_max per request.
- Edge cases: empty prompt (raise), chunked prefill (prompt fed in two pieces), T_max reached.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------- given model (as in ex07)
def layer_norm(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + eps) * g + b


def gelu(z):
    return 0.5 * z * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (z + 0.044715 * z ** 3)))


def init_model(V, T_max, D, H, L, rng):
    s = 0.3                                            # large enough that greedy varies
    blocks = []
    for _ in range(L):
        b = {f"W{n}": s * rng.standard_normal((D, D)) for n in "qkvo"}
        b.update(W1=s * rng.standard_normal((D, 4 * D)), W2=s * rng.standard_normal((4 * D, D)))
        blocks.append(b)
    return {"E": rng.standard_normal((V, D)), "P": rng.standard_normal((T_max, D)),
            "blocks": blocks, "H": H}


def _softmax_masked(s, mask):
    s = np.where(mask, s, -np.inf)
    w = np.exp(s - s.max(-1, keepdims=True))
    return w / w.sum(-1, keepdims=True)


def full_forward(params, tokens):
    tokens = np.asarray(tokens)
    B, T = tokens.shape
    H = params["H"]
    x = params["E"][tokens] + params["P"][:T]
    D = x.shape[-1]
    split = lambda a: a.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    for b in params["blocks"]:
        h = layer_norm(x, 1.0, 0.0)
        q, k, v = (split(h @ b[f"W{n}"]) for n in "qkv")
        w = _softmax_masked(q @ k.transpose(0, 1, 3, 2) / math.sqrt(D // H), np.tril(np.ones((T, T), bool)))
        x = x + (w @ v).transpose(0, 2, 1, 3).reshape(B, T, D) @ b["Wo"]
        x = x + gelu(layer_norm(x, 1.0, 0.0) @ b["W1"]) @ b["W2"]
    return layer_norm(x, 1.0, 0.0) @ params["E"].T


# ---------------------------------------------------------------- the exercise
@dataclass
class KVCache:
    L: int
    B: int
    H: int
    T_max: int
    d_h: int
    length: int = 0
    k: np.ndarray = field(init=False, repr=False)
    v: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        self.k = np.zeros((self.L, self.B, self.H, self.T_max, self.d_h))
        self.v = np.zeros_like(self.k)


def new_cache(params, B: int) -> KVCache:
    D = params["E"].shape[1]
    return KVCache(len(params["blocks"]), B, params["H"], params["P"].shape[0], D // params["H"])


def extend(params, tokens, cache: KVCache, *, position_bug: bool = False):
    tokens = np.asarray(tokens)
    B, n = tokens.shape
    if n == 0:
        raise ValueError("need at least one new token")
    start, end = cache.length, cache.length + n
    if end > cache.T_max:
        raise ValueError(f"cache full: {end} > T_max={cache.T_max}")
    H, dh = cache.H, cache.d_h
    pos = np.arange(n) if position_bug else np.arange(start, end)      # bug: restart at 0
    x = params["E"][tokens] + params["P"][pos]
    D = x.shape[-1]
    split = lambda a: a.reshape(B, n, H, dh).transpose(0, 2, 1, 3)    # (B, H, n, d_h)
    mask = np.arange(end)[None, :] <= np.arange(n)[:, None] + start   # causal, offset = start
    for layer, b in enumerate(params["blocks"]):
        h = layer_norm(x, 1.0, 0.0)
        q, k, v = (split(h @ b[f"W{c}"]) for c in "qkv")
        cache.k[layer, :, :, start:end] = k                            # write in place
        cache.v[layer, :, :, start:end] = v
        K, V = cache.k[layer, :, :, :end], cache.v[layer, :, :, :end]
        w = _softmax_masked(q @ K.transpose(0, 1, 3, 2) / math.sqrt(dh), mask)
        x = x + (w @ V).transpose(0, 2, 1, 3).reshape(B, n, D) @ b["Wo"]
        x = x + gelu(layer_norm(x, 1.0, 0.0) @ b["W1"]) @ b["W2"]
    cache.length = end
    return layer_norm(x, 1.0, 0.0) @ params["E"].T


def extend_concat(params, tokens, kv: list):
    """Rung 2: kv is a list of per-layer [K, V] arrays (B, H, t, d_h) grown with concatenate."""
    tokens = np.asarray(tokens)
    B, n = tokens.shape
    H = params["H"]
    start = kv[0][0].shape[2] if kv else 0
    x = params["E"][tokens] + params["P"][start:start + n]
    D = x.shape[-1]
    dh = D // H
    split = lambda a: a.reshape(B, n, H, dh).transpose(0, 2, 1, 3)
    mask = np.arange(start + n)[None, :] <= np.arange(n)[:, None] + start
    for layer, b in enumerate(params["blocks"]):
        h = layer_norm(x, 1.0, 0.0)
        q, k, v = (split(h @ b[f"W{c}"]) for c in "qkv")
        if len(kv) <= layer:
            kv.append([k, v])
        else:                                                          # copies the whole cache
            kv[layer] = [np.concatenate([kv[layer][0], k], axis=2), np.concatenate([kv[layer][1], v], axis=2)]
        K, V = kv[layer]
        w = _softmax_masked(q @ K.transpose(0, 1, 3, 2) / math.sqrt(dh), mask)
        x = x + (w @ V).transpose(0, 2, 1, 3).reshape(B, n, D) @ b["Wo"]
        x = x + gelu(layer_norm(x, 1.0, 0.0) @ b["W1"]) @ b["W2"]
    return layer_norm(x, 1.0, 0.0) @ params["E"].T


def generate_greedy(params, prompt, steps: int, use_cache: bool = True):
    seq = np.asarray(prompt)
    if not use_cache:
        for _ in range(steps):
            nxt = full_forward(params, seq)[:, -1].argmax(-1)
            seq = np.concatenate([seq, nxt[:, None]], axis=1)
        return seq
    cache = new_cache(params, seq.shape[0])
    logits = extend(params, seq, cache)                                # prefill
    for _ in range(steps):
        nxt = logits[:, -1].argmax(-1)
        seq = np.concatenate([seq, nxt[:, None]], axis=1)
        logits = extend(params, nxt[:, None], cache)                   # one decode step
    return seq


def kv_cache_bytes(L: int, B: int, T: int, n_kv_heads: int, d_h: int, bytes_per_elem: int) -> int:
    return 2 * L * B * T * n_kv_heads * d_h * bytes_per_elem


def main() -> None:
    rng = np.random.default_rng(398)
    params = init_model(V=30, T_max=24, D=16, H=4, L=2, rng=rng)
    prompt = rng.integers(0, 30, size=(2, 5))

    no_cache = generate_greedy(params, prompt, 10, use_cache=False)
    cached = generate_greedy(params, prompt, 10, use_cache=True)
    print("generated (no cache):", no_cache[:, 5:].tolist())
    print("identical with cache:", np.array_equal(no_cache, cached))
    kv: list = []
    concat = [extend_concat(params, cached[:, :5], kv)] + [extend_concat(params, cached[:, t:t + 1], kv) for t in range(5, 15)]
    print("concatenate-cache rung matches:", np.allclose(np.concatenate(concat, 1), full_forward(params, cached), atol=1e-10))

    cache = new_cache(params, 2)
    steps = [extend(params, cached[:, :3], cache), extend(params, cached[:, 3:5], cache)]
    steps += [extend(params, cached[:, t:t + 1], cache) for t in range(5, 15)]
    stitched = np.concatenate(steps, axis=1)
    err = np.abs(stitched - full_forward(params, cached)).max()
    print("chunked prefill (3 + 2) then 10 decode steps, max |logit diff| < 1e-10:", bool(err < 1e-10))
    print("cache.k shape:", cache.k.shape, "(L, B, H, T_max, d_h); length =", cache.length)

    bug = new_cache(params, 2)
    extend(params, cached[:, :5], bug)
    wrong = extend(params, cached[:, 5:6], bug, position_bug=True)
    print("position restarted at 0 gives different logits:",
          not np.allclose(wrong[:, 0], full_forward(params, cached[:, :6])[:, -1]))
    try:
        extend(params, cached[:, :10], cache)
    except ValueError as e:
        print("overflow:", e)

    print("\nKV cache sizing (fp16, B=1, T=4096, L=32, d_h=128):")
    for kv in (32, 8, 1):
        print(f"  n_kv_heads={kv:>2}: {kv_cache_bytes(32, 1, 4096, kv, 128, 2) / 2**30:.3f} GiB")
    print("  B=16, n_kv_heads=8:", f"{kv_cache_bytes(32, 16, 4096, 8, 128, 2) / 2**30:.1f} GiB")


if __name__ == "__main__":
    main()
