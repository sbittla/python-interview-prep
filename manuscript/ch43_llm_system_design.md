# Chapter 43. LLM System-Design Primer

◆ Extended · Tracks M L · Study time ≈ 3 h · Prerequisites: §39.7, Chapter 40, Chapter 42

**Learning objectives**

- Run a 45-minute AI design round.
- Estimate KV memory, TTFT/TPOT, fleet and cost.
- Design a RAG service, an LLM gateway and an eval pipeline, and monitor them.

> **Recognise it.** "Chatbot over our docs"; "a layer in front of three model providers";
> "is the new prompt better?"; "how many GPUs?".

All numbers here are **hypothetical** round values, not facts about any real product.

## 43.1 System-design interview framework for AI systems

| Step | Minutes | Say out loud |
|---|---|---|
| 1. Requirements | 5–8 | QPS (peak, average), p95 TTFT/TPOT, quality bar, freshness, privacy |
| 2. Estimates | 5–8 | tokens per request, KV memory, replicas, cost per 1k requests |
| 3. Architecture | 10 | query path *and* ingestion path |
| 4. Deep dive | 10 | the interviewer's pick: retrieval, serving, evals |
| 5. Trade-offs, failures | 5–8 | what breaks, what you degrade to, 10× load |
| 6. Evals, operations | 3–5 | offline gate, online metrics, feedback loop |

Tokens set latency and cost; quality must be measured. Fix the quality bar first: "cite or
refuse" and "best effort" are different designs. Think aloud (→ §2.3). Exercise 06 scores notes.
→ repo: `chapters/ch43_llm_system_design/solutions/ex06_design_rubric.py`.

## 43.2 Design a RAG service

**Worked design: "Q&A over 2 million internal documents."**

*Requirements:* 50 QPS peak, ~10 average. Cite sources or say "I don't know". Users see
only what their ACL allows. Streamed answers: p95 TTFT < 1 s, TPOT < 25 ms. Edits
visible within an hour.

*Estimates.* Prompt (system + question + 5 chunks) ≈ 3,000 tokens; output ≈ 300. A dense 8B
model is self-hosted on 80 GB accelerators. KV bytes per token = 2 (K and V) · layers · KV
heads · head_dim · bytes (→ §39.7); GQA has fewer KV heads than query heads. A
forward pass costs ≈ 2·N FLOPs per token (dense models; ignores the attention-score term,
which grows with context). **Roofline:** a phase is compute-bound when FLOPs per byte read
exceed the ridge FLOPS/BW = 200 (≈100 at MFU 0.5). Prefill reuses each weight for 3,000
tokens: compute-bound. Decode reads the 2·N weight bytes once per B sequences, ≈ B FLOP/byte:
memory-bound below batch ~100. Batching amortises weight reads, not per-sequence KV reads,
so TPOT rises with batch.

```python
import math

# Hypothetical model and accelerator: round numbers, not real products.
N, LAYERS, KV_HEADS, HEAD_DIM, BYTES = 8e9, 32, 8, 128, 2      # dense 8B, GQA, 16-bit
MEM, BW, FLOPS, MFU = 80e9, 2.0e12, 4.0e14, 0.5                 # bytes, B/s, FLOP/s
QPS, PROMPT, OUT, BATCH, UTIL = 50, 3000, 300, 64, 0.7          # peak load, plan

kv_tok = 2 * LAYERS * KV_HEADS * HEAD_DIM * BYTES               # K and V, every layer
weights = N * BYTES
fits = int((MEM * 0.9 - weights) // ((PROMPT + OUT) * kv_tok))  # 10% reserve
ttft = 2 * N * PROMPT / (FLOPS * MFU)                           # prefill: compute-bound
ctx = PROMPT + OUT // 2
tpot = max((weights + BATCH * ctx * kv_tok) / BW,               # decode: read all weights
           2 * N * BATCH / (FLOPS * MFU))                       # ... or compute, if larger
e2e = ttft + (OUT - 1) * tpot
prefill_pool = math.ceil(QPS * PROMPT / (FLOPS * MFU / (2 * N) * UTIL))
decode_pool = math.ceil(QPS * (OUT - 1) / (BATCH / tpot * UTIL))

print(f"KV {kv_tok / 1024:.0f} KiB/token, {fits} sequences fit next to {weights / 1e9:.0f} GB")
print(f"TTFT {ttft * 1000:.0f} ms, TPOT {tpot * 1000:.1f} ms, end-to-end {e2e:.1f} s")
print(f"replicas: prefill {prefill_pool} + decode {decode_pool} = {prefill_pool + decode_pool}")
print(f"in decode at once (Little's law): {QPS * (OUT - 1) * tpot:.0f} sequences")
```

```text
KV 128 KiB/token, 129 sequences fit next to 16 GB
TTFT 240 ms, TPOT 21.2 ms, end-to-end 6.6 s
replicas: prefill 18 + decode 8 = 26
in decode at once (Little's law): 317 sequences
```

TTFT 240 ms leaves ~750 ms of the SLO for retrieval, rerank and queueing.
**Ladder.** (1) Output tokens only: 5 replicas; misses prefill, which dominates long prompts.
(2) Both phases, 30% headroom: 26. (3) Batch from the TPOT SLO, checked against memory:
25 ms allows 64; 64 ≤ 129 that fit, and 317 decoding ≤ 8 × 64 = 512 slots. For 10 ms, the
largest power-of-two batch is 8 → 44 replicas (repo): latency is paid in hardware.
*Cost* (hypothetical $2.50/accelerator-hour): 26 × 2.50 = $65/h: $0.36 per 1k requests at
50 QPS average, $3.61 at 5. An API at $0.50/$1.50 per 1M input/output tokens costs $1.95 per
1k; break-even is 9.3 QPS average, so at ~10 privacy and control decide.
→ repo: `chapters/ch43_llm_system_design/solutions/ex03_fleet_sizing_cost.py` (ex01, ex02 build the parts).

*Architecture.*

```text
ingest:  sources ─► parse ─► chunk (§40.2) ─► embed ─► index (vectors + BM25 + ACL tags)
                       ▲ change events, re-index within 1 h (new index version)
query:   client ─► gateway (§43.3) ─► cache? key (query, ACL groups, index version), TTL ≤ 1 h
                                         │ miss
                                         ▼
                     retrieve: hybrid + RRF, ACL pre-filter (§40.4–40.5) ─► top 50
                                                                            ▼
          stream ◄─ guardrails ◄─ LLM pool ◄─ assemble prompt (§40.8) ◄─ rerank → 5 (§40.6)
            │
            └─► logs/traces ─► eval set + dashboards (§43.4, §43.5)
```

*Trade-offs.*

| Choice | Option A | Option B | Pick when |
|---|---|---|---|
| Context | 5 chunks (3,000-token prompt) | 2 chunks (1,500) | B: 26 → 14 replicas, but recall@k falls; measure it |
| Index | exact search | ANN (→ §40.7) | ANN at millions of vectors; tune recall vs latency |
| ACL | filter at query time | index per group | A for many groups; with ANN pre-filter (filtered search): post-filtering top-k can starve |
| Model | self-host | API | cost at average load (§42.10), data residency |

*Failure modes.* Retriever timeout: keyword-only, flagged low-confidence. Overload: shed load,
queue with a deadline. Stale index: alert on ingestion lag. Injection in documents (→ §42.11).
ACL leak: filter inside retrieval.

**Wrong-but-tempting:** sizing from parameters alone; no factor 2 for K and V; query heads
instead of KV heads; costing a peak fleet at peak load; a cache keyed on the query alone,
which serves user A's answer to user B and outlives re-indexing. **Edge cases:** empty
retrieval (refuse), question over the context window, deleted document, 3× burst.
**Follow-ups:** multi-turn memory (→ §41.5), prefix caching, 10× documents.

## 43.3 Design an LLM gateway

One entry point for all models: auth, routing, quotas (→ §42.7), caching (→ §42.8),
guardrails (→ §42.11), per-team token and cost accounting (→ §42.10).

The core is the **route**: an ordered backend list per request class, filtered by context
window. **Propagate deadlines**: cap each timeout by the time remaining; skip a backend that
cannot finish in time. Exercise 04 replays an outage (excerpt):

```text
-- fallback, deadline-aware
rid  6 t= 6000 simple  prompt 12000 out  50 -> degraded  3000 ms  fail:large
rid  7 t= 7000 complex prompt  4000 out 400 -> fallback  4150 ms  skip:large ok:small
-- fallback, fixed timeouts
rid  6 t= 6000 simple  prompt 12000 out  50 -> degraded  4000 ms  fail:large  LATE
rid  7 t= 7000 complex prompt  4000 out 400 -> fallback  8150 ms  fail:large ok:small  LATE
```

Fixed timeouts: 17% of requests miss their deadline; deadline-aware: none. Falling back to a
smaller model downgrades *quality*: log and evaluate it.
**Ladder:** one backend (outages = errors) → ordered fallback (slow timeouts blow
deadlines) → deadline-aware. **Edge cases:** prompt too long for every backend, deadline
shorter than any backend, outage starting mid-request. **Follow-ups:** circuit breaker
(→ §42.4); retry only idempotent errors (→ §42.3); key the cache by route or skip fallbacks.
→ repo: `chapters/ch43_llm_system_design/solutions/ex04_gateway_router.py`.

## 43.4 Design an evaluation pipeline

Three loops: **offline**, a versioned golden set in slices gating every change in CI;
**canary** on a small share of traffic; **online** A/B (→ §35.6). Checks go cheap to
expensive: rules (facts, citation, refusal), retrieval metrics (→ §40.9), an LLM judge
(→ §40.10). The harness is built in §40.11.

The gate compares slice by slice; critical slices allow no regressions:

```text
baseline: {'ALL': (9, 12), 'numeric': (3, 4), 'policy': (2, 4), 'unanswerable': (4, 4)}
candidate A: {'ALL': (11, 12), 'numeric': (4, 4), 'policy': (4, 4), 'unanswerable': (3, 4)}
  newly failing ['q10'], newly passing ['q2', 'q4', 'q7'] -> ('BLOCK', ['critical regression: q10'])
```

The average rose, yet A invents an answer it should refuse. With four items per slice, one
flip moves a slice 25 points. Grow the slices, or report a bootstrap interval
(→ §35.5); paired flips suit McNemar's test. **Edge cases:** missing answer = fail, refusal in
capitals, "150" must not match "$1500". **Follow-up:** calibrate the judge on labels.
→ repo: `chapters/ch43_llm_system_design/solutions/ex05_eval_gate.py`.

## 43.5 Observability, monitoring and feedback loops

| Layer | Metrics | Alert on |
|---|---|---|
| Serving | TTFT, TPOT percentiles, queue depth, batch, KV memory | SLO burn rate |
| Gateway | error, fallback, cache-hit, degraded rates; cost per team | spikes vs baseline |
| Retrieval | empty results, ingestion lag | stale index |
| Quality | refusals, citation validity, thumbs, sampled judge score | drift |

A trace per request, a span per stage with token counts, locates slowdowns. Redact PII in
logs. **Feedback loop:** label thumbs-down answers and fallbacks into the golden set, so the
next candidate is gated on them. Exercise 04 computes the gateway row.

## 43.6 Bridge to general system-design interviews

| General concept | LLM-system form |
|---|---|
| Load balancer | gateway routing by model, context length and cost |
| Cache | exact-match / semantic response cache; prefix (KV) cache |
| Rate limiting | tokens per minute, not just requests (→ §29.5) |
| Queue, back-pressure | admission control with deadlines; continuous batching (→ §42.9) |

## Interviewer's view

Rewarded: requirements first, labelled assumptions, arithmetic, trade-offs, eval and
degradation plans. Penalised: product names, unitless estimates, "it scales".

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | GPU memory budget: weights + KV cache | ★ | estimate |
| 02 | Prefill vs decode latency (roofline) | ★ | max(compute, memory) |
| 03 | Fleet size and cost; API break-even | ◆ | per-phase pools |
| 04 | LLM gateway: routing, fallback, deadlines | ★ | deadline propagation |
| 05 | Offline eval with a regression gate | ◆ | slices + flips |
| 06 | Design-doc rubric scorer | ○ | checklist as data |

Index: `chapters/ch43_llm_system_design/README.md`.

## Checkpoint quiz

1. Why is prefill compute-bound but decode memory-bound?
2. 32 query heads, 8 KV heads: how much smaller is the cache?
3. Why does halving the prompt nearly halve this fleet (26 → 14)?
4. Why cap each backend timeout by the remaining deadline?
5. The eval score rose. Why still block the release?

<details><summary>Answers</summary>

1. Intensity vs ridge (~100): prefill ≈ prompt-length FLOP/byte; decode ≈ batch FLOP/byte,
   lowered further by KV reads.
2. 4×. The cache scales with KV heads, not query heads.
3. Prefill (18 of 26) scales with prompt tokens: 18 → 9; decode 8 → 5.
4. Else a slow failure spends the budget before the fallback starts.
5. A critical slice (refusals, safety) regressed, and the average hid it.
</details>

## Summary card

- Requirements → estimates → architecture → deep dive → failures → evals.
- KV bytes/token = 2·L·kv_heads·d_h·bytes; prefill ≈ 2·N·prompt FLOPs; decode reads weights.
- Size prefill and decode separately; the TPOT SLO sets the batch; cost at average load.
- RAG: ACL inside retrieval; cache keyed by ACL and index version. Gateway: propagate deadlines.
- Evals: slices, flips, no critical regressions; feedback grows the golden set.
