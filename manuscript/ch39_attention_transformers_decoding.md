# Chapter 39. Attention, Transformer Blocks, Decoding and Sampling

★ Core · Track L (M optional) · Study time ≈ 8 h · Prerequisites: Ch. 33 (NumPy), §35.10 (stable softmax), Ch. 38 (tokens, embeddings)

**Learning objectives**

- Write masked multi-head attention, a pre-LN block and a mini GPT in NumPy; count their cost.
- Build a KV cache equal to full recompute; size it in bytes.
- Implement greedy, temperature, top-k/p, beam search, penalties and stop strings.

> **Recognise it**
>
> | Signal | Reach for |
> |---|---|
> | "why √d", "NaN with padding", "(B, T, D) to heads" | §39.1–§39.3 |
> | "generation is slow", "how much GPU memory" | KV cache (§39.7) |
> | "more/less random", "nucleus", "repeats itself" | §39.8, §39.9 |

Softmax: → §35.10. Tokens, embedding lookup: → §38.2, §38.7. Training: → §37.5.

## 39.1 Scaled dot-product attention (lab)

Each query scores every key; the softmaxed scores weight the values: Attention(Q, K, V) = softmax(QKᵀ / √d_k + mask) V, with Q (n, d_k),
K (m, d_k), V (m, d_v).

**Why √d_k.** With independent mean-0, variance-1 entries, Var(q·k) = d_k: large scores make the
softmax nearly one-hot, its gradient p_i(δ_ij − p_j) near 0. Dividing restores unit variance
(repo run, 16 keys):

```text
score std  d_k   unscaled  scaled   mean max softmax weight (m=16)
             4      1.99    1.01   unscaled 0.415  scaled 0.238
           512     22.41    1.00   unscaled 0.935  scaled 0.242
```

**Worked problem 1 — Masked attention.** Rung 1 loops over queries and keys: O(n·m·d),
interpreter-bound. Rung 2, two matmuls and a vectorised softmax: same O(n·m·(d_k + d_v)) time,
O(n·m) memory, any batch shape. Fused (FlashAttention-style) kernels stream key blocks with an
online softmax and never store n×m.

```python
import math
import numpy as np

def masked_softmax(s, mask=None):
    if mask is not None:
        s = np.where(mask, s, -np.inf)               # mask BEFORE the softmax
    m = s.max(axis=-1, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)             # fully masked row: no -inf - -inf
    e = np.exp(s - m)
    z = e.sum(axis=-1, keepdims=True)
    return np.divide(e, z, out=np.zeros_like(e), where=z > 0)   # that row -> all 0

def attention(Q, K, V, mask=None):                    # (..., n, d), (..., m, d), (..., m, dv)
    scores = Q @ np.swapaxes(K, -1, -2) / math.sqrt(Q.shape[-1])
    w = masked_softmax(scores, mask)
    return w @ V, w

rng = np.random.default_rng(39)
Q, K, V = rng.standard_normal((3, 8)), rng.standard_normal((4, 8)), rng.standard_normal((4, 2))
mask = np.array([[1, 1, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1]], bool)
out, w = attention(Q, K, V, mask)
print(w.round(3).tolist())
print(out[1].tolist(), np.isnan(out).any())
big = np.where(mask, Q @ K.T / math.sqrt(8), -1e9)  # the "-1e9" shortcut
print(masked_softmax(big)[1].tolist())
```

```text
[[0.654, 0.346, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.138, 0.302, 0.374, 0.186]]
[0.0, 0.0] False
[0.25, 0.25, 0.25, 0.25]
```

**−inf vs −1e9.** With one valid key or more, both give masked keys 0 weight. On a *fully*
masked row, −inf gives 0/0 = NaN unless handled (we return zeros); −1e9 silently averages the
masked values (line 3) and is −inf in float16 anyway. Libraries differ by path: in torch 2.15
(CPU) SDPA returned zeros; `nn.MultiheadAttention` returned NaN with `need_weights=True`, zeros
with `need_weights=False`, but NaN on its eval-mode no-grad fast path (repo). Handle it yourself. Bool masks are opposite:
SDPA `True` = attend, `nn.MultiheadAttention` `True` = blocked.

**Wrong but tempting:** zeroing weights *after* the softmax (rows no longer sum to 1); no max
shift (exp overflows past ≈ 709.8 in float64, ≈ 88.7 in float32). **Edge cases:** n = 1, m = 1, fully masked row, scores ≈ 10⁶, batch
dims. **Follow-up:** cross-attention (n ≠ m).
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex01_scaled_dot_product_attention.py`

## 39.2 Multi-head attention (lab)

H heads attend in parallel on d_h = D/H features each; Wo mixes them. FLOPs equal one head of
width D. Parameters (Wq, Wk, Wv, Wo + biases): 4D² + 4D.

**Worked problem 2 — Split heads.** Rung 1 loops over heads slicing columns; rung 2 reshapes
once and batches over (B, H): both O(B·T·D² + B·T²·D). Merging is the inverse transpose and
reshape.

```python
import numpy as np

def split_heads(x, H):                       # (B, T, D) -> (B, H, T, D/H)
    B, T, D = x.shape
    if D % H:
        raise ValueError("D must be divisible by H")
    return x.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)

x = np.arange(8.0).reshape(1, 2, 4)          # 2 tokens, D = 4
print(split_heads(x, 2)[0].tolist())
print(x.reshape(1, 2, 2, 2)[0].tolist())     # wrong: reshape straight to (B, H, T, d_h)
```

```text
[[[0.0, 1.0], [4.0, 5.0]], [[2.0, 3.0], [6.0, 7.0]]]
[[[0.0, 1.0], [2.0, 3.0]], [[4.0, 5.0], [6.0, 7.0]]]
```

Head 0 must hold features 0–1 of *both* tokens; the direct reshape makes "head 0" token 0 cut
in two, and it runs without error. **Edge cases:** H = 1, H = D, D % H ≠ 0. **Follow-ups:**
grouped-query attention shares each K/V head across H/n_kv query heads, shrinking the KV cache
(§39.7); the repo cross-checks `nn.MultiheadAttention`.
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex02_multi_head_attention.py`

## 39.3 Causal masking

Query i may see key j only if j ≤ i. When n_q new queries follow cached keys (§39.7) they sit
at positions offset … n_k − 1, so the rule is j ≤ i + (n_k − n_q).

```python
import numpy as np

def causal_mask(n_q, n_k=None):              # True = may attend
    n_k = n_q if n_k is None else n_k
    offset = n_k - n_q                       # queries are the last n_q positions
    return np.arange(n_k)[None, :] <= np.arange(n_q)[:, None] + offset

def padding_mask(lengths, T, side="right"):
    pos, L = np.arange(T)[None, :], np.asarray(lengths)[:, None]
    return pos < L if side == "right" else pos >= T - L

print(causal_mask(3).astype(int).tolist(), causal_mask(2, 4).astype(int).tolist())
for side in ("right", "left"):
    m = causal_mask(4)[None] & padding_mask([2], 4, side)[:, None, :]
    print(side, "fully masked query rows:", np.where(~m[0].any(-1))[0].tolist())
```

```text
[[1, 0, 0], [1, 1, 0], [1, 1, 1]] [[1, 1, 1, 0], [1, 1, 1, 1]]
right fully masked query rows: []
left fully masked query rows: [0, 1]
```

**Left padding + causal** (common in batched generation) leaves pad queries with no key: NaN
rows without §39.1's guard. **Test causality:** change token t and assert earlier outputs do not move (every repo
model test does).
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex03_causal_padding_masks.py`

## 39.4 Positional encodings: sinusoidal and rotary (RoPE)

Without positions attention is permutation-equivariant: shuffle tokens, outputs shuffle too.
With w_i = 10000^(−2i/d):

| | Sinusoidal | Learned | RoPE |
|---|---|---|---|
| How | add sin(p·w_i), cos(p·w_i) | add a (T_max, D) table | rotate q, k pair i by p·w_i |
| Property | PE[p+k] = rotation of PE[p] | undefined past T_max | q_m·k_n depends on m − n only |

```python
import numpy as np

def freqs(d, base=10000.0):
    return base ** (-np.arange(0, d, 2) / d)            # w_i = base^(-2i/d)

def rope(x, positions):                                  # x: (..., T, d), rotate pairs
    ang = np.outer(positions, freqs(x.shape[-1]))
    c, s = np.cos(ang), np.sin(ang)
    out = np.empty_like(x)
    out[..., 0::2] = x[..., 0::2] * c - x[..., 1::2] * s
    out[..., 1::2] = x[..., 0::2] * s + x[..., 1::2] * c
    return out

rng = np.random.default_rng(4)
q, k = rng.standard_normal((1, 8)), rng.standard_normal((1, 8))
score = lambda m, n: (rope(q, [m]) @ rope(k, [n]).T).item()
print([round(score(m, n), 6) for m, n in [(5, 2), (103, 100), (2, 5)]])
```

```text
[1.752276, 1.752276, 0.475668]
```

Offset 3 gives the same score twice; −3 differs (the sinusoidal table uses the same `freqs` with
sin on even, cos on odd columns; repo). Rotations preserve norms; V is not rotated;
quality still degrades past the trained length. **Pitfall:** this pairs (2i, 2i+1); "half-split"
code pairs i with i + d/2, a fixed permutation, so mixing them is a silent bug. O(T·d).
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex04_positional_encodings.py`

## 39.5 Full transformer block: attention + MLP + residual + layer norm

Pre-LN: h = x + MHA(LN₁(x)); y = h + MLP(LN₂(h)), MLP = W₂·GELU(W₁x), width F = 4D; it needs a
final LN before the head. Post-LN (2017 original): h = LN₁(x + MHA(x)); y = LN₂(h + MLP(h)),
harder to train deep without warm-up. Residuals give every layer a direct gradient path. Per block: 4D² + 4D (attention) + 8D² + 5D (MLP) + 4D (two LNs) = **12D² + 13D**.

| | LayerNorm | RMSNorm |
|---|---|---|
| Formula | (x − μ)/√(σ² + ε)·γ + β | x/√(mean(x²) + ε)·γ |
| Params | 2D | D |
| Invariant to | shift and scale of x | scale only |

Both normalise each token over its features (population σ²), unlike BatchNorm (§37.3). **Wrong
but tempting:** `ddof=1`; the batch axis; ε outside the root. The repo block and norms match
torch (`nn.TransformerEncoderLayer`, whose `src_mask` `True` = blocked).
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex05_layernorm_rmsnorm.py`,
`chapters/ch39_attention_transformers_decoding/solutions/ex06_transformer_block.py`

## 39.6 Mini GPT forward pass (lab)

Head *tied* to E (saves V·D); params V·D + T_max·D + L(12D² + 13D) + 2D (124,439,808 for the
GPT-2-small shape, repo). One causal pass gives T predictions; the brute rung (each prefix
alone, i.e. generation without a cache) must match it. Initial loss ≈ ln V:

```python
import numpy as np

def ln(x):                                         # LayerNorm, gamma = 1, beta = 0
    return (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + 1e-5)

def gpt_forward(p, tokens):                        # (B, T) ints -> logits (B, T, V)
    T, D = tokens.shape[1], p["E"].shape[1]
    x = p["E"][tokens] + p["P"][:T]                # token + position
    causal = np.tril(np.ones((T, T), bool))
    for b in p["blocks"]:                          # pre-LN, twice
        h = ln(x)
        s = (h @ b["Wq"]) @ (h @ b["Wk"]).transpose(0, 2, 1) / np.sqrt(D)
        s = np.where(causal, s, -np.inf)               # mask first
        w = np.exp(s - s.max(-1, keepdims=True))
        x = x + (w / w.sum(-1, keepdims=True)) @ (h @ b["Wv"]) @ b["Wo"]   # one head
        x = x + np.maximum(ln(x) @ b["W1"], 0) @ b["W2"]                   # ReLU MLP
    return ln(x) @ p["E"].T                        # final LN, tied head

rng = np.random.default_rng(0)
V, T_max, D = 50, 16, 32
shapes = dict(Wq=(D, D), Wk=(D, D), Wv=(D, D), Wo=(D, D), W1=(D, 4 * D), W2=(4 * D, D))
p = {"E": 0.02 * rng.standard_normal((V, D)), "P": 0.02 * rng.standard_normal((T_max, D)),
     "blocks": [{k: 0.02 * rng.standard_normal(v) for k, v in shapes.items()} for _ in range(2)]}
tokens = rng.integers(0, V, (2, 10))
z = gpt_forward(p, tokens)
z = z - z.max(-1, keepdims=True)
logp = z - np.log(np.exp(z).sum(-1, keepdims=True))             # log-softmax (§35.10)
loss = -np.take_along_axis(logp[:, :-1], tokens[:, 1:, None], -1).mean()
print(z.shape, round(float(loss), 4), round(float(np.log(V)), 4))
```

```text
(2, 10, 50) 3.9184 3.912
```

The repo adds heads, GELU and biases. → repo: `chapters/ch39_attention_transformers_decoding/solutions/ex07_mini_gpt_forward.py`

## 39.7 KV cache mechanics and memory sizing

**Worked problem 3 — Incremental decoding equal to full recompute.** Rung 1 re-runs the prefix:
O(L(t·D² + t²·D)) at step t. Past K, V never change, so cache them: rung 2 concatenates (O(t)
copying per step); rung 3 preallocates, O(L(D² + t·D)) per step. Q is used once: not cached.

```python
import math
import numpy as np

rng = np.random.default_rng(7)
T, d = 6, 4
X = rng.standard_normal((T, d))                          # embedded tokens
Wq, Wk, Wv = (rng.standard_normal((d, d)) for _ in range(3))

def softmax_rows(s):
    e = np.exp(s - s.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)

def full(X):                                             # recompute every position
    q, k, v = X @ Wq, X @ Wk, X @ Wv
    s = np.where(np.tril(np.ones((len(X), len(X)), bool)), q @ k.T / math.sqrt(d), -np.inf)
    return softmax_rows(s) @ v

K = np.zeros((T, d)); V = np.zeros((T, d)); n = 0        # preallocated cache
outs = []
for t in range(T):                                       # one decode step per token
    x = X[t:t + 1]
    K[n], V[n] = x @ Wk, x @ Wv                          # append this token's k, v
    n += 1
    q = x @ Wq                                           # the new query only
    outs.append(softmax_rows(q @ K[:n].T / math.sqrt(d)) @ V[:n])
print(np.abs(np.vstack(outs) - full(X)).max() < 1e-12)
```

```text
True
```

The repo GPT keeps k and v buffers, each (L, B, H, T_max, d_h); a prefill chunk uses
`causal_mask(n, length + n)` (§39.3), new tokens take positions `length …` (restarting at 0 is
the classic bug). **Edge cases:** chunked prefill, batch > 1, cache full, empty input.
**Follow-ups:** GQA/MQA (n_kv < H heads); beams reorder cache rows by parent (→ ex10);
sliding-window or paged caches; prefill is compute-bound, decode memory-bandwidth-bound.

**Sizing:** bytes = 2 (K and V) · L · B · T · n_kv_heads · d_h · bytes_per_element. For a
hypothetical L = 32, d_h = 128, T = 4096, B = 1, fp16 model the repo prints 2.000 GiB with 32 KV
heads and 0.500 GiB with 8. Linear in B·T, the cache can exceed the weights at long context or large batch (weights + KV
cache: → §42.12; batching: → §42.9).

**Cost** (2·m·k·n per matmul; repo-verified): with N = 12LD² + DV matmul weights, a forward is
2N + 4LTD FLOPs/token with full scores (≈ 2N + 2LTD for the causal half); training ≈ 6N.
Full-score attention (4LTD) equals the per-layer dense FLOPs (24LD², head excluded) at T = 6D,
or at 12D counting the causal half. Stored scores: B·H·T²·bytes per layer (8 GiB at B = 1,
H = 32, T = 8192, fp32).
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex08_kv_cache.py`,
`chapters/ch39_attention_transformers_decoding/solutions/ex12_flops_params_memory.py`

## 39.8 Decoding: greedy, temperature, top-k, top-p (nucleus), beam search (labs)

Greedy takes the argmax (can loop). Temperature divides logits by T (T → 0: greedy; T > 1:
flatter). Top-k keeps the k largest logits; top-p the smallest set with mass ≥ p.

**Worked problem 4 — A seeded nucleus sampler.** Sort probabilities descending (stable); keep a
token iff the mass *strictly before it* is < p: the crossing token stays, and so does ≥ 1 token. Rung 1 loops over the sorted list; rung 2 is a cumsum: both
O(V log V). With `argpartition` top-k first, it is O(V + k log k).

```python
import numpy as np

def top_p_filter(logits, p):
    probs = np.exp(logits - logits.max()); probs /= probs.sum()
    order = np.argsort(-probs, kind="stable")
    before = np.cumsum(probs[order]) - probs[order]      # mass strictly before each token
    keep = np.zeros(len(logits), bool)
    keep[order[before < p]] = True                       # includes the token that crosses p
    return np.where(keep, logits, -np.inf)

def sample(logits, rng, temperature=1.0, top_p=1.0):
    z = top_p_filter(logits / temperature, top_p)        # temperature first, then filter
    probs = np.exp(z - z.max()); probs /= probs.sum()
    cdf = np.cumsum(probs)
    return min(int(np.searchsorted(cdf, rng.random() * cdf[-1], side="right")), len(z) - 1)

lg = np.log(np.array([0.5, 0.25, 0.125, 0.125]))
for p in (0.5, 0.6, 0.75, 0.9):
    print(p, np.isfinite(top_p_filter(lg, p)).astype(int).tolist())
rng = np.random.default_rng(0)
draws = [sample(lg, rng, top_p=0.6) for _ in range(10000)]
print((np.bincount(draws, minlength=4) / 10000).tolist())
```

```text
0.5 [1, 0, 0, 0]
0.6 [1, 1, 0, 0]
0.75 [1, 1, 0, 0]
0.9 [1, 1, 1, 1]
[0.6649, 0.3351, 0.0, 0.0]
```

**Wrong but tempting:** inclusive cumsum ≤ p
(p = 0.6 keeps only 0.5 of the mass); filtering before temperature; T = 0 as a division.
**Edge cases:** V = 1, ties (repo top-k keeps every tie; top-p's stable sort breaks a boundary
tie by index), p = 1, −inf logits. **Follow-ups:**
min-p; one seeded generator per stream.

**Beam search** (exhaustive is O(V^len)) keeps the k best unfinished hypotheses and moves EOS
expansions to a finished pool: O(len·k) model calls, O(len·kV log kV) ranking. On the repo toy
model greedy ends at "a a a a" (p = 0.015); k = 2 finds "b ⟨eos⟩" (0.405). Raw sums favour short
outputs, so score = Σ log p / len^α, len = generated tokens incl. EOS. Hypotheses cut at max_len
compete too; on a random bigram model (max_len = 6) α ≥ 0.6 already prefers one:

```text
  alpha=0.0: [4, 0] score=-1.245; [4, 3, 0] score=-2.204; [4, 1, 1, 1, 1, 1] score=-2.210
  alpha=0.6: [4, 1, 1, 1, 1, 1] score=-0.754; [4, 0] score=-0.821; [4, 3, 0] score=-1.140
```

Beam search can lose to greedy; chat usually samples.
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex09_sampling.py`,
`chapters/ch39_attention_transformers_decoding/solutions/ex10_beam_search.py`

## 39.9 Repetition penalties and stop conditions

| Processor | Rule |
|---|---|
| Repetition penalty θ ≥ 1 | seen token: logit/θ if > 0, logit·θ otherwise |
| Frequency / presence | logit −= f·count + p·[count > 0] |
| No-repeat n-gram | ban tokens completing a seen n-gram |

Stop on EOS (by id), `max_new_tokens` (always set it), or a stop string. Stop strings can span
tokens, so a streamer **holds back** the longest pending suffix that is a prefix of a stop
(streaming parsers: → §42.5). With S stops of length ≤ m, rescanning all N characters is O(S·N)
per token and cannot stream; the hold-back below scans < m + |piece| pending characters,
O(S·m·(m + |piece|)) per piece. Aho–Corasick (KMP for one stop) gives O(1) amortised per character.

```python
def holdback(text, stops):     # longest suffix of text that could still start a stop string
    return max((L for s in stops for L in range(1, len(s)) if text.endswith(s[:L])), default=0)

def stream(pieces, stops):
    pending, out = "", []
    for piece in pieces:
        pending += piece
        hits = [pending.find(s) for s in stops if s in pending]
        if hits:
            return [c for c in out + [pending[:min(hits)]] if c], "stop"
        keep = holdback(pending, stops)
        out.append(pending[:len(pending) - keep]); pending = pending[len(pending) - keep:]
    return [c for c in out + [pending] if c], "end"

print(stream(["Hel", "lo\n", "\nUs", "er:", " hi"], ["\n\nUser:"]))
```

```text
(['Hel', 'lo'], 'stop')
```

**Wrong but tempting:** dividing every seen logit by θ (−2 → −1 instead of −4: the repeat gets
likelier); emitting `"\n"` before knowing whether `"\n\nUser:"` follows. **Edge cases:** θ = 1,
stop inside one piece, a released near-miss, no EOS ever. The repo adds EOS/length reasons.
→ repo: `chapters/ch39_attention_transformers_decoding/solutions/ex11_repetition_stop.py`

## Interviewer's view

- **Say the shapes**; mask before the softmax; handle empty rows.
- **Prove equivalence:** cache vs recompute, fused vs loop, causality by perturbation.
- **Know the numbers** (12D², 2N, KV bytes) and the exact top-p boundary.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Scaled dot-product attention, masks | ★ | masked softmax |
| ex02 | Multi-head attention | ★ | reshape + transpose |
| ex03 | Causal and padding masks | ★ | broadcast masks |
| ex04 | Sinusoidal and rotary encodings | ★ | rotation |
| ex05 | LayerNorm vs RMSNorm | ★ | per-token norm |
| ex06 | Transformer block forward | ★ | residual + norm |
| ex07 | Mini GPT forward | ★ | causal LM |
| ex08 | KV cache = full recompute | ★ | incremental decoding |
| ex09 | Greedy, temperature, top-k, top-p | ★ | logit filtering |
| ex10 | Beam search, length normalisation | ◆ | k-best search |
| ex11 | Repetition penalties, stop strings | ★ | streaming |
| ex12 | Parameter, FLOP, memory calculator | ◆ | cost model |

Index: `chapters/ch39_attention_transformers_decoding/README.md`.

## Checkpoint quiz

1. Why divide scores by √d_k?
2. Why can a left-padded causal batch produce NaN?
3. Why is `x.reshape(B, H, T, d_h)` wrong for splitting heads?
4. KV cache bytes? Why is Q not cached?
5. Probabilities [0.5, 0.25, 0.125, 0.125], p = 0.6: which tokens does top-p keep?

<details>
<summary>Answers</summary>

1. Var(q·k) = d_k; unscaled scores saturate the softmax and kill its gradient.
2. Pad queries come before every real key, so their whole row is masked: 0/0.
3. It cuts the flattened (T, D) block; reshape to (B, T, H, d_h), transpose.
4. 2·L·B·T·n_kv·d_h·bytes; a query is used once, past K and V every step.
5. The first two: mass before token 3 is 0.75 ≥ 0.6.

</details>

## Summary card

- **Attention:** softmax(QKᵀ/√d_k + mask)V, O(n·m·d); −inf first; guard empty rows; j ≤ i + n_k − n_q.
- **Heads/positions:** reshape (B, T, H, d_h) → transpose; RoPE makes scores depend on m − n.
- **Block/GPT:** pre-LN, 12D² + 13D per block; loss at init ≈ ln V; ≈ 2N + 2LTD FLOPs/token.
- **KV cache:** 2·L·B·T·n_kv·d_h·bytes; positions start at `length`.
- **Decoding:** temperature → top-k → top-p (mass before < p) → seeded draw; beam len^α; cap tokens.
