"""
Exercise 02 — Prefill vs Decode Latency with a Roofline Estimate   [Tier: ★ Core]
Chapter 43 · Pattern: max(compute time, memory time) per phase · Target time: 30 min

Problem
-------
Estimate time-to-first-token (TTFT), time per output token (TPOT) and decode throughput for a
dense model on one accelerator. All hardware and model numbers are HYPOTHETICAL.

Assumptions (state them in the interview):
- A forward pass costs about 2 * n_params FLOPs per token (one multiply-add per weight).
  This holds for a dense model (every weight used for every token; not mixture-of-experts)
  and ignores the attention-score term, about 2 * n_layers * ctx * d_model FLOPs per token,
  which is small while ctx is much smaller than 12 * d_model.
- Prefill processes the whole prompt in one batched pass: compute-bound,
  ``prefill_seconds = 2 * N * prompt_tokens / (peak_flops * mfu)``.
- One decode step produces one token for each of ``batch`` sequences and must read every weight
  once plus every sequence's KV cache, so
  ``memory_s = (weight_bytes + batch * ctx * kv_bytes_per_token) / mem_bw`` and
  ``compute_s = 2 * N * batch / (peak_flops * mfu)``; the step takes ``max`` of the two
  (a roofline lower bound; real kernels are slower).
- The first output token comes from prefill, so
  ``e2e = ttft + (output_tokens - 1) * tpot``, with decode context taken as
  ``prompt + output // 2`` (the average over the generation). No queueing.

Implement ``prefill_seconds``, ``decode_step_seconds`` (returns (seconds, "memory"|"compute")),
``latency(m, hw, prompt, output, batch)`` -> Latency(ttft, tpot, e2e, bound) and
``decode_tokens_per_s(m, hw, batch, ctx)``.

Examples
--------
>>> round(prefill_seconds(M8B, G80, 3000), 3)
0.24
>>> s, b = decode_step_seconds(M8B, G80, 1, 3150); (round(s * 1000, 2), b)
(8.21, 'memory')

Constraints
-----------
- batch >= 1, prompt >= 1, output >= 1; ValueError otherwise.

Hints
-----
- Prefill: total FLOPs for the prompt divided by the FLOP/s actually achieved.
- Decode step: compute a memory time and a compute time; the slower one is the step,
  and its name is the bound.
- latency: which phase produces the first output token? How many decode steps remain?

Follow-ups
----------
- Why is prefill compute-bound and decode memory-bound? Prefill reuses each weight for every
  prompt token; decode uses it once per sequence in the batch.
- Continuous batching (→ §42.9) keeps the batch full as requests finish.
- Prompt (prefix) caching skips prefill for a shared system prompt; speculative decoding
  trades extra compute for fewer memory-bound steps.
- Edge cases: output = 1 (e2e = ttft), batch so large the cache does not fit (→ ex01).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:                       # given (as in ex01)
    name: str
    n_params: float
    n_layers: int
    n_kv_heads: int
    head_dim: int
    bytes_per_param: float = 2.0
    bytes_per_kv: float = 2.0

    @property
    def weight_bytes(self) -> float:
        return self.n_params * self.bytes_per_param

    @property
    def kv_bytes_per_token(self) -> float:
        return 2 * self.n_layers * self.n_kv_heads * self.head_dim * self.bytes_per_kv


@dataclass(frozen=True)
class Hardware:
    name: str
    mem_bytes: float
    mem_bw: float          # achievable bytes / s
    peak_flops: float      # dense 16-bit FLOP / s
    mfu: float = 0.5       # model FLOPs utilisation reached in practice


@dataclass(frozen=True)
class Latency:
    ttft: float
    tpot: float
    e2e: float
    bound: str


# Hypothetical numbers, round on purpose.
M8B = ModelSpec("M8B", 8e9, 32, 8, 128)
G80 = Hardware("G80", 80e9, 2.0e12, 4.0e14)


def _check(**kw: int) -> None:
    for k, v in kw.items():
        if v < 1:
            raise ValueError(f"{k} must be >= 1")


def compute_only_tokens_per_s(m: ModelSpec, hw: Hardware) -> float:
    """Rung 1: arithmetic limit only."""
    raise NotImplementedError("TODO")


def prefill_seconds(m: ModelSpec, hw: Hardware, prompt_tokens: int) -> float:
    raise NotImplementedError("TODO")


def decode_step_seconds(m: ModelSpec, hw: Hardware, batch: int, ctx: int) -> tuple[float, str]:
    raise NotImplementedError("TODO")


def latency(m: ModelSpec, hw: Hardware, prompt: int, output: int, batch: int) -> Latency:
    raise NotImplementedError("TODO")


def decode_tokens_per_s(m: ModelSpec, hw: Hardware, batch: int, ctx: int) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    print("hypothetical: M8B dense 8e9 params, GQA 8 KV heads; G80 80 GB, 2 TB/s, 400 TFLOP/s, MFU 0.5")
    print(f"rung 1 compute-only decode: {compute_only_tokens_per_s(M8B, G80):,.0f} tokens/s per sequence")
    s1, _ = decode_step_seconds(M8B, G80, 1, 3150)
    print(f"roofline decode at batch 1:  {1 / s1:,.0f} tokens/s per sequence")
    print(f"prefill 3000 tokens: {prefill_seconds(M8B, G80, 3000) * 1000:.0f} ms")
    print(f"{'batch':>5}{'TPOT ms':>9}{'tokens/s':>10}{'bound':>9}{'e2e s':>7}")
    for b in (1, 8, 32, 64, 128):
        lat = latency(M8B, G80, prompt=3000, output=300, batch=b)
        tps = decode_tokens_per_s(M8B, G80, b, 3150)
        print(f"{b:>5}{lat.tpot * 1000:>9.1f}{tps:>10,.0f}{lat.bound:>9}{lat.e2e:>7.2f}")
    one = latency(M8B, G80, prompt=200, output=1, batch=1)
    print(f"output = 1 token: ttft {one.ttft * 1000:.0f} ms, e2e {one.e2e * 1000:.0f} ms")
    print("short context, batch 512:", decode_step_seconds(M8B, G80, 512, 100)[1], "bound")


if __name__ == "__main__":
    main()
