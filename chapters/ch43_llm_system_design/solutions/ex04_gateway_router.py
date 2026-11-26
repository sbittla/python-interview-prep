"""
Exercise 04 — LLM Gateway: Routing, Fallback and Deadlines         [Tier: ★ Core]
Chapter 43 · Pattern: ordered candidates + deadline propagation + metrics · Target time: 40 min

Problem
-------
An LLM gateway sits between product teams and model backends. Simulate one, deterministically,
with two HYPOTHETICAL backends ("small": cheap, fast, short context; "large": better, slower,
pricier). Latencies, prices and the outage window are made-up round numbers; no network.

``serve(req, backends, policy, cache)`` -> Result:

1. Exact-match cache (→ §42.8): if ``req.key`` is in ``cache``, return status "cache",
   latency CACHE_MS, cost 0, served_by "cache".
2. Candidates = ``policy[req.tier]`` (names in preference order), dropping any backend whose
   ``max_ctx < prompt + output`` tokens.
3. Walk the candidates with ``elapsed = 0``. Let ``remaining = req.deadline_ms - elapsed``.
   Skip a backend (record "skip:<name>") if its predicted latency
   ``base_ms + ms_per_token * output`` exceeds ``remaining``. Otherwise call it with
   ``timeout = min(backend.timeout_ms, remaining)``: during an outage (``req.t_ms + elapsed``
   inside a [start, end) window) the call fails after ``timeout`` ms (record "fail:<name>");
   otherwise it succeeds after the predicted latency (record "ok:<name>").
4. Success: status "ok" on the first candidate, "fallback" on a later one; cost =
   (prompt * price_in + output * price_out) / 1e6; store the key in ``cache``. Failed calls
   are not billed (an assumption: say it).
5. Nothing succeeded: status "degraded" (a canned "try again" answer), cost 0, latency = elapsed.

``summarise(results)`` -> dict with n, rate of each status, p50/p95 latency, total cost and
requests served per backend. ``percentile`` is nearest rank: the ceil(p * n / 100)-th smallest.
Multiply before dividing: 7 / 100 * 100 is 7.000000000000001 in floating point, so
ceil(p / 100 * n) would pick the 8th value instead of the 7th.

Examples
--------
>>> r = serve(Request(0, 0, "simple", "k", 500, 100, 3000), BACKENDS, FALLBACK, {})
>>> r.status, r.served_by, r.latency_ms, r.attempts
('ok', 'small', 1150, ['ok:small'])

Constraints
-----------
- Deterministic: requests come from the fixed ``SCRIPT``; no clocks, no randomness.

Approach ladder
---------------
1. One backend, no fallback — every outage becomes user-visible errors.
2. Ordered fallback list — survives outages, but a slow failure (full timeout) can blow the
   caller's deadline before the fallback even starts.
3. Deadline-aware fallback — cap each timeout by the remaining budget and skip backends that
   cannot finish in time; add a response cache. O(#candidates) per request.

Follow-ups
----------
- A circuit breaker (→ §42.4) would stop paying the timeout on every request during the outage.
- Retries with backoff (→ §42.3) on the *same* backend only for idempotent, retryable errors.
- Per-team quotas (→ §42.7 and the token bucket in §29.5) and per-team cost accounting (→ §42.10).
- A semantic cache trades hit rate for the risk of serving a wrong near-duplicate answer.
- The cache key ignores the route: a degraded fallback answer is cached and later served
  as if from the preferred model. Key by (prompt, route) or skip caching fallbacks.
- Edge cases: prompt too long for every backend (degraded with no attempts), deadline shorter
  than any backend, empty request list in summarise (ValueError).
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

CACHE_MS = 5


@dataclass(frozen=True)
class Backend:
    name: str
    base_ms: int
    ms_per_token: int
    price_in: float            # hypothetical $ per 1M prompt tokens
    price_out: float           # hypothetical $ per 1M output tokens
    timeout_ms: int
    max_ctx: int
    outages: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class Request:
    rid: int
    t_ms: int
    tier: str                  # "simple" | "complex"
    key: str                   # cache key (normalised prompt hash in real life)
    prompt: int
    output: int
    deadline_ms: int


@dataclass
class Result:
    rid: int
    status: str
    served_by: str | None
    latency_ms: int
    cost: float
    attempts: list[str] = field(default_factory=list)
    late: bool = False             # finished after the caller's deadline


BACKENDS = {
    "small": Backend("small", 150, 10, 0.10, 0.40, 2000, 8_000),
    "large": Backend("large", 400, 25, 1.00, 4.00, 4000, 32_000, outages=((5_000, 9_000),)),
}
SINGLE = {"simple": ["large"], "complex": ["large"]}
FALLBACK = {"simple": ["small", "large"], "complex": ["large", "small"]}


def predicted_ms(b: Backend, req: Request) -> int:
    return b.base_ms + b.ms_per_token * req.output


def _down(b: Backend, t: int) -> bool:
    return any(start <= t < end for start, end in b.outages)


def serve(req: Request, backends: dict[str, Backend], policy: dict[str, list[str]],
          cache: dict[str, str], deadline_aware: bool = True) -> Result:
    if req.key in cache:
        return Result(req.rid, "cache", "cache", CACHE_MS, 0.0, ["hit"])
    names = [n for n in policy[req.tier] if backends[n].max_ctx >= req.prompt + req.output]
    elapsed, attempts = 0, []
    for i, name in enumerate(names):
        b = backends[name]
        remaining = req.deadline_ms - elapsed
        if deadline_aware and predicted_ms(b, req) > remaining:
            attempts.append(f"skip:{name}")
            continue
        if _down(b, req.t_ms + elapsed):
            elapsed += min(b.timeout_ms, remaining) if deadline_aware else b.timeout_ms
            attempts.append(f"fail:{name}")
            continue
        elapsed += predicted_ms(b, req)
        attempts.append(f"ok:{name}")
        cache[req.key] = name
        cost = (req.prompt * b.price_in + req.output * b.price_out) / 1e6
        status = "ok" if i == 0 else "fallback"
        return Result(req.rid, status, name, elapsed, cost, attempts, elapsed > req.deadline_ms)
    return Result(req.rid, "degraded", None, elapsed, 0.0, attempts, elapsed > req.deadline_ms)


def percentile(values: list[int], p: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p * len(ordered) / 100) - 1)]


def summarise(results: list[Result]) -> dict:
    if not results:
        raise ValueError("no results")
    n = len(results)
    status = Counter(r.status for r in results)
    lat = [r.latency_ms for r in results]
    return {
        "n": n,
        **{f"{s}_rate": round(status[s] / n, 3) for s in ("ok", "fallback", "cache", "degraded")},
        "late_rate": round(sum(r.late for r in results) / n, 3),
        "p50_ms": percentile(lat, 50),
        "p95_ms": percentile(lat, 95),
        "cost": round(sum(r.cost for r in results), 6),
        "served_by": dict(sorted(Counter(r.served_by or "none" for r in results).items())),
    }


# (t_ms, tier, key, prompt, output, deadline_ms); a repeated key is the same prompt.
SCRIPT = [
    (0, "complex", "c1", 1500, 400, 15000),
    (1000, "simple", "s1", 300, 50, 5000),
    (2000, "simple", "s1", 300, 50, 5000),
    (3000, "simple", "s2", 12000, 50, 5000),     # too long for "small"
    (5000, "complex", "c2", 300, 150, 15000),    # outage of "large" starts
    (5500, "simple", "s3", 1500, 150, 5000),
    (6000, "simple", "s4", 12000, 50, 3000),     # only "large" fits, and it is down
    (7000, "complex", "c3", 4000, 400, 8000),    # "large" cannot finish in 8 s anyway
    (8000, "complex", "c2", 300, 150, 15000),
    (9500, "complex", "c4", 300, 150, 15000),    # outage over
    (10000, "complex", "c5", 12000, 400, 15000),
    (10500, "simple", "s5", 4000, 50, 5000),
]


def make_requests() -> list[Request]:
    return [Request(rid, *row) for rid, row in enumerate(SCRIPT)]


def run(policy: dict[str, list[str]], deadline_aware: bool = True) -> list[Result]:
    cache: dict[str, str] = {}
    return [serve(r, BACKENDS, policy, cache, deadline_aware) for r in make_requests()]


def main() -> None:
    print("hypothetical backends; 'large' is down for t in [5000, 9000) ms")
    reqs = make_requests()
    for label, policy, aware in [("fallback, deadline-aware", FALLBACK, True),
                                 ("fallback, fixed timeouts", FALLBACK, False)]:
        print(f"-- {label}")
        for req, r in zip(reqs, run(policy, aware)):
            print(f"rid {r.rid:>2} t={req.t_ms:>5} {req.tier:<7} prompt {req.prompt:>5} "
                  f"out {req.output:>3} -> {r.status:<8} {r.latency_ms:>5} ms  "
                  f"{' '.join(r.attempts)}{'  LATE' if r.late else ''}")
    for label, policy, aware in [("large only", SINGLE, True),
                                 ("fallback, fixed timeouts", FALLBACK, False),
                                 ("fallback, deadline-aware", FALLBACK, True)]:
        print(f"{label}: {summarise(run(policy, aware))}")
    try:
        summarise([])
    except ValueError as exc:
        print("summarise([]):", exc)


if __name__ == "__main__":
    main()
