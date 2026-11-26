"""
Exercise 01 — GPU Memory Budget: Weights + KV Cache                [Tier: ★ Core]
Chapter 43 · Pattern: back-of-envelope estimate with stated assumptions · Target time: 20 min

Problem
-------
In a design round you are asked "how many concurrent conversations fit on one GPU?".
Answer it with arithmetic, not intuition. A model is described by ``ModelSpec`` (all numbers
in this chapter are HYPOTHETICAL, chosen to be round, not taken from any real product).

- ``weight_bytes(m)`` = n_params * bytes_per_param.
- ``kv_bytes_per_token(m)`` = 2 * n_layers * n_kv_heads * head_dim * bytes_per_kv.
  The 2 is one K and one V vector per layer per KV head. With grouped-query attention (GQA)
  ``n_kv_heads < n_heads`` and the cache shrinks by ``n_heads / n_kv_heads``; MQA has 1 KV head.
- ``max_sequences(m, gpu_bytes, ctx_tokens, n_gpus=1, reserve_frac=0.10)``: usable memory is
  ``n_gpus * gpu_bytes * (1 - reserve_frac)`` (activations, fragmentation, runtime); subtract
  the weights; divide what is left by the KV bytes of one sequence of ``ctx_tokens`` tokens;
  floor. Return 0 if the weights alone do not fit.

Examples
--------
>>> kv_bytes_per_token(M8B)                     # 2 * 32 * 8 * 128 * 2
131072.0
>>> max_sequences(M8B, 80e9, 4096)              # (72 GB - 16 GB) / (4096 * 131072 B)
104

Constraints
-----------
- Positive sizes; ``n_heads`` divisible by ``n_kv_heads``; ValueError otherwise.
- Decimal units: 1 GB = 1e9 bytes (say which you use; GiB = 2**30 is 7% larger).

Approach ladder
---------------
1. Weights only — "16 GB fits on 80 GB, so it fits". Ignores the KV cache, which dominates
   at long context or large batch. O(1).
2. KV with ``n_heads`` — counts a cache per query head: correct for multi-head attention,
   but overestimates a GQA model's cache by ``n_heads / n_kv_heads`` (4x for M8B). O(1).
3. Full budget — reserve, weights, then ``2 * L * n_kv_heads * d_h * bytes`` per token per
   sequence. O(1). Move up because each rung changes the answer by a large factor.

Follow-ups
----------
- 8-bit KV cache (bytes_per_kv=1) doubles the sequence count; quality must be re-evaluated.
- A model too big for one GPU is sharded (tensor parallel): memory adds up across GPUs but
  each step now pays for inter-GPU communication. This file only does the memory sum.
- Paged KV allocation avoids reserving ``ctx_max`` per sequence; budget by *average* context.
- Edge cases: weights exceed memory (0 sequences), reserve_frac in [0, 1), ctx_tokens = 0.
"""
from __future__ import annotations

from dataclasses import dataclass

GB = 1e9


@dataclass(frozen=True)
class ModelSpec:
    name: str
    n_params: float
    n_layers: int
    n_heads: int
    n_kv_heads: int
    head_dim: int
    bytes_per_param: float = 2.0      # 16-bit weights
    bytes_per_kv: float = 2.0         # 16-bit KV cache


# Hypothetical models: round numbers for practice, not descriptions of real products.
M8B = ModelSpec("M8B (GQA 32q/8kv)", 8e9, 32, 32, 8, 128)
M8B_MHA = ModelSpec("M8B-MHA (32kv)", 8e9, 32, 32, 32, 128)
M8B_MQA = ModelSpec("M8B-MQA (1kv)", 8e9, 32, 32, 1, 128)
M70B = ModelSpec("M70B (GQA 64q/8kv)", 70e9, 80, 64, 8, 128)


def _validate(m: ModelSpec) -> None:
    for field_name in ("n_params", "n_layers", "n_heads", "n_kv_heads", "head_dim",
                       "bytes_per_param", "bytes_per_kv"):
        if getattr(m, field_name) <= 0:
            raise ValueError(f"{field_name} must be positive")
    if m.n_heads % m.n_kv_heads:
        raise ValueError("n_heads must be a multiple of n_kv_heads")


def weight_bytes(m: ModelSpec) -> float:
    _validate(m)
    return m.n_params * m.bytes_per_param


def kv_bytes_per_token_mha(m: ModelSpec) -> float:
    """Rung 2: one K/V pair per *query* head. Wrong for GQA/MQA models."""
    _validate(m)
    return 2 * m.n_layers * m.n_heads * m.head_dim * m.bytes_per_kv


def kv_bytes_per_token(m: ModelSpec) -> float:
    _validate(m)
    return 2 * m.n_layers * m.n_kv_heads * m.head_dim * m.bytes_per_kv


def max_sequences(m: ModelSpec, gpu_bytes: float, ctx_tokens: int,
                  n_gpus: int = 1, reserve_frac: float = 0.10) -> int:
    if gpu_bytes <= 0 or n_gpus < 1 or ctx_tokens <= 0:
        raise ValueError("gpu_bytes, n_gpus and ctx_tokens must be positive")
    if not 0 <= reserve_frac < 1:
        raise ValueError("reserve_frac must be in [0, 1)")
    free = n_gpus * gpu_bytes * (1 - reserve_frac) - weight_bytes(m)
    if free <= 0:
        return 0
    return int(free // (ctx_tokens * kv_bytes_per_token(m)))


def main() -> None:
    gpu = 80 * GB                                  # hypothetical 80 GB accelerator
    print("assumptions: 16-bit weights and KV, 10% reserve, 1 GB = 1e9 B, hypothetical models")
    print(f"{'model':<20}{'weights GB':>11}{'KV KiB/token':>13}{'seqs @4k':>9}{'seqs @32k':>10}")
    for m in (M8B_MHA, M8B, M8B_MQA):
        print(f"{m.name:<20}{weight_bytes(m) / GB:>11.1f}{kv_bytes_per_token(m) / 1024:>13.0f}"
              f"{max_sequences(m, gpu, 4096):>9}{max_sequences(m, gpu, 32768):>10}")
    naive = kv_bytes_per_token_mha(M8B) / kv_bytes_per_token(M8B)
    print(f"rung 2 (count query heads) overestimates M8B's cache by {naive:.0f}x")
    print(f"rung 1 (weights only) says M8B fits: {weight_bytes(M8B) < gpu}; "
          f"but one 32k sequence needs {32768 * kv_bytes_per_token(M8B) / GB:.1f} GB of cache")
    kv8 = ModelSpec("M8B kv8", 8e9, 32, 32, 8, 128, bytes_per_kv=1.0)
    print("8-bit KV cache, 4k context:", max_sequences(kv8, gpu, 4096))
    print("M70B on 1 GPU:", max_sequences(M70B, gpu, 4096),
          "| on 2 GPUs:", max_sequences(M70B, gpu, 4096, n_gpus=2),
          "| on 4 GPUs:", max_sequences(M70B, gpu, 4096, n_gpus=4))
    try:
        max_sequences(ModelSpec("bad", 1e9, 4, 6, 4, 64), gpu, 1024)
    except ValueError as exc:
        print("6 query heads / 4 KV heads ->", exc)


if __name__ == "__main__":
    main()
