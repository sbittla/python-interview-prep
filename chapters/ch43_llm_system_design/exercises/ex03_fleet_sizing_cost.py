"""
Exercise 03 — Fleet Size and Cost for a Target QPS                 [Tier: ◆ Extended]
Chapter 43 · Pattern: size each phase separately; batch from the latency SLO · Target time: 35 min

Problem
-------
"Serve 50 requests/s at peak, 3,000 prompt tokens and 300 output tokens each, with time per
output token (TPOT) under 25 ms. How many accelerators, and is self-hosting cheaper than a
pay-per-token API?" Every price, model and hardware number is HYPOTHETICAL.

Model (state it): prefill and decode are sized as two pools of one-model-per-accelerator
replicas. A combined fleet that mixes prefill chunks into decode steps needs about the same
total and can do a little better, so this is a conservative estimate.

- ``fits(w, m, hw)`` = sequences whose KV cache (prompt + output tokens) fits next to the
  weights after a 10% reserve (→ ex01).
- ``pick_batch(w, m, hw, tpot_slo, candidates)`` = the largest candidate batch that fits in
  memory and whose decode step (→ ex02, ctx = prompt + output // 2) is <= tpot_slo;
  ValueError if none qualifies.
- ``size_fleet(w, m, hw, batch, target_util=0.7) -> FleetPlan``:
  prefill_replicas = ceil(peak_qps * prompt / (prefill tokens/s per replica * target_util)),
  decode_replicas  = ceil(peak_qps * (output - 1) / (batch / step * target_util))
  (the first output token comes from prefill). ttft, tpot, e2e = ttft + (output - 1) * tpot,
  and ``in_decode = peak_qps * (output - 1) * tpot`` sequences decoding at once (Little's law,
  L = lambda * W): the number whose KV caches must be resident across the decode pool.
  ValueError if ``batch`` exceeds ``fits``.
- ``cost_per_1k(plan, price_per_gpu_hour, avg_qps)``: a fleet sized for the peak is paid for
  every hour, so divide by the *average* load. ``api_cost_per_1k(w, in_price, out_price)`` uses
  per-million-token prices; ``break_even_avg_qps`` is the average load where they are equal.

Examples
--------
>>> p = size_fleet(RAG, M8B, G80, batch=64)
>>> p.prefill_replicas, p.decode_replicas, p.replicas
(18, 8, 26)

Constraints
-----------
- peak_qps > 0, batch >= 1, 0 < target_util <= 1, avg_qps > 0; ValueError otherwise.

Hints
-----
- Prefill tokens/s per replica = achieved FLOP/s / FLOPs per token.
- Decode tokens/s per replica = batch / step time.
- Replicas = ceil(demand / (capacity per replica * target_util)), per pool.
- Cost per request = fleet cost per hour / requests per hour at the AVERAGE load.

Follow-ups
----------
- Halving retrieved context (3,000 -> 1,500 prompt tokens) removes almost half the prefill pool.
- Prefix caching of a shared system prompt removes its prefill cost.
- Autoscaling closes the peak/average gap, but cold starts (loading weights) take minutes.
- Edge cases: model does not fit (ValueError), SLO too tight for any batch, output = 1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------- given (from ex01 / ex02)
@dataclass(frozen=True)
class ModelSpec:
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
    mem_bw: float
    peak_flops: float
    mfu: float = 0.5


def prefill_seconds(m: ModelSpec, hw: Hardware, prompt: int) -> float:
    return 2 * m.n_params * prompt / (hw.peak_flops * hw.mfu)


def decode_step_seconds(m: ModelSpec, hw: Hardware, batch: int, ctx: int) -> float:
    memory_s = (m.weight_bytes + batch * ctx * m.kv_bytes_per_token) / hw.mem_bw
    compute_s = 2 * m.n_params * batch / (hw.peak_flops * hw.mfu)
    return max(memory_s, compute_s)


# ---------------------------------------------------------------- this exercise
@dataclass(frozen=True)
class Workload:
    peak_qps: float
    prompt: int
    output: int


@dataclass(frozen=True)
class FleetPlan:
    batch: int
    ttft: float
    tpot: float
    e2e: float
    in_decode: float
    prefill_replicas: int
    decode_replicas: int
    replicas: int


M8B = ModelSpec("M8B", 8e9, 32, 8, 128)
G80 = Hardware("G80", 80e9, 2.0e12, 4.0e14)
RAG = Workload(peak_qps=50, prompt=3000, output=300)
GPU_HOUR = 2.50                         # hypothetical $ per accelerator-hour
API_IN, API_OUT = 0.50, 1.50            # hypothetical $ per 1M input / output tokens


def _ctx(w: Workload) -> int:
    return w.prompt + w.output // 2


def output_tokens_only(w: Workload, m: ModelSpec, hw: Hardware, batch: int) -> int:
    """Rung 1: decode tokens only, no headroom."""
    raise NotImplementedError("TODO")


def fits(w: Workload, m: ModelSpec, hw: Hardware, reserve_frac: float = 0.10) -> int:
    raise NotImplementedError("TODO")


def pick_batch(w: Workload, m: ModelSpec, hw: Hardware, tpot_slo: float,
               candidates: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256)) -> int:
    raise NotImplementedError("TODO")


def size_fleet(w: Workload, m: ModelSpec, hw: Hardware, batch: int,
               target_util: float = 0.7) -> FleetPlan:
    raise NotImplementedError("TODO")


def cost_per_1k(plan: FleetPlan, price_per_gpu_hour: float, avg_qps: float) -> float:
    raise NotImplementedError("TODO")


def api_cost_per_1k(w: Workload, in_price: float, out_price: float) -> float:
    raise NotImplementedError("TODO")


def break_even_avg_qps(plan: FleetPlan, price_per_gpu_hour: float, api_per_1k: float) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    print("all numbers hypothetical: M8B on G80, $2.50/accelerator-hour, API $0.50/$1.50 per 1M tokens")
    print("rung 1 (output tokens only, batch 64):", output_tokens_only(RAG, M8B, G80, 64), "replicas")
    print(f"KV fits {fits(RAG, M8B, G80)} sequences; batch for TPOT <= 25 ms:",
          pick_batch(RAG, M8B, G80, 0.025), "| <= 10 ms:", pick_batch(RAG, M8B, G80, 0.010))
    print(f"{'prompt':>6}{'batch':>6}{'TPOT ms':>8}{'e2e s':>7}{'in_decode':>10}"
          f"{'prefill':>8}{'decode':>7}{'total':>6}")
    for w, batch in [(RAG, 8), (RAG, 64), (Workload(50, 1500, 300), 64),
                     (Workload(50, 300, 300), 64)]:
        p = size_fleet(w, M8B, G80, batch)
        print(f"{w.prompt:>6}{batch:>6}{p.tpot * 1000:>8.1f}{p.e2e:>7.2f}{p.in_decode:>10.0f}"
              f"{p.prefill_replicas:>8}{p.decode_replicas:>7}{p.replicas:>6}")
    p = size_fleet(RAG, M8B, G80, 64)
    api = api_cost_per_1k(RAG, API_IN, API_OUT)
    print(f"API: ${api:.2f} per 1k requests")
    for avg in (50, 20, 5):
        print(f"self-host, {p.replicas} replicas, avg {avg:>2} QPS: "
              f"${cost_per_1k(p, GPU_HOUR, avg):.2f} per 1k requests")
    print(f"break-even average load: {break_even_avg_qps(p, GPU_HOUR, api):.1f} QPS")
    m70 = ModelSpec("M70B", 70e9, 80, 8, 128)
    for label, call in [("TPOT <= 5 ms", lambda: pick_batch(RAG, M8B, G80, 0.005)),
                        ("batch 256", lambda: size_fleet(RAG, M8B, G80, 256)),
                        ("M70B on one G80", lambda: size_fleet(RAG, m70, G80, 1))]:
        try:
            call()
        except ValueError as exc:
            print(f"{label}: {exc}")


if __name__ == "__main__":
    main()
