# Chapter 39 — Attention, Transformer Blocks, Decoding and Sampling

Manuscript: `manuscript/ch39_attention_transformers_decoding.md`. NumPy first; PyTorch (CPU) is
used only for optional cross-checks (`pytest.importorskip("torch")`), never for the solutions.

| # | Exercise | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| 01 | [Scaled dot-product attention with masks](solutions/ex01_scaled_dot_product_attention.py) | ★ | scores → mask → stable softmax → weighted sum | Python loops → vectorised; `-1e9` fill shown as the wrong rung; √d_k experiment; torch SDPA check | 39.1 |
| 02 | [Multi-head attention](solutions/ex02_multi_head_attention.py) | ★ | reshape (B,T,H,d_h) + transpose | per-head loop → batched heads; wrong reshape; `nn.MultiheadAttention` check | 39.2 |
| 03 | [Causal and padding masks](solutions/ex03_causal_padding_masks.py) | ★ | broadcast comparisons | double loop → broadcast; offset for cached keys; left-padding NaN rows; perturbation test | 39.3 |
| 04 | [Sinusoidal and rotary positional encodings](solutions/ex04_positional_encodings.py) | ★ | sin/cos tables, pairwise rotation | loop → `np.outer`; RoPE interleaved vs half-split; relative-position property | 39.4 |
| 05 | [LayerNorm vs RMSNorm](solutions/ex05_layernorm_rmsnorm.py) | ★ | per-token normalisation | loop → vectorised; invariances; torch check | 39.5 |
| 06 | [Transformer block forward pass](solutions/ex06_transformer_block.py) | ★ | residual + norm + MHA + MLP | per-token → whole sequence; pre-LN and post-LN; `TransformerEncoderLayer` check | 39.5 |
| 07 | [Mini GPT forward pass](solutions/ex07_mini_gpt_forward.py) | ★ | embed → blocks → final LN → tied head | prefix-by-prefix → one causal pass; param formula; loss ≈ ln V | 39.6 |
| 08 | [KV cache that matches full recompute](solutions/ex08_kv_cache.py) | ★ | cache K, V; offset causal mask | no cache → concatenate cache → preallocated cache; chunked prefill; sizing | 39.7 |
| 09 | [Greedy, temperature, top-k, top-p sampling](solutions/ex09_sampling.py) | ★ | filter logits, inverse-CDF draw | top-p loop → cumsum; wrong `cum <= p`; seeded frequency check | 39.8 |
| 10 | [Beam search with length normalisation](solutions/ex10_beam_search.py) | ◆ | keep k best hypotheses | exhaustive → greedy → beam; length bias with α = 0, 0.6, 1 | 39.8 |
| 11 | [Repetition penalties and stop conditions](solutions/ex11_repetition_stop.py) | ★ | logit processors, streaming hold-back | rescan-everything → hold-back streamer; sign-bug penalty | 39.9 |
| 12 | [Parameter, FLOP and memory calculator](solutions/ex12_flops_params_memory.py) | ◆ | count matmuls, 2·m·k·n | instrumented forward → closed form; 2N + 2LTD rule; score memory | 39.1, 39.7 |

Every solution checks its fast rung against a slow rung (or a full recompute) in `main()`, and the
tests compare them on seeded random inputs. Each test file was mutation-checked: a typical bug
(no √d_k, `-1e9` fill, missing position offset, `cum <= p`, dividing negative logits by θ, ...)
makes it fail.

## How to run

```bash
OPENBLAS_NUM_THREADS=4 .venv/Scripts/python chapters/ch39_attention_transformers_decoding/solutions/ex08_kv_cache.py
.venv/Scripts/python -m pytest chapters/ch39_attention_transformers_decoding            # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch39_attention_transformers_decoding  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 39                                     # regenerate outputs/
```

Work in `exercises/` (stubs raise `NotImplementedError` and carry hints instead of the approach
ladder; given helpers such as `init_*`, the ex08 reference model and the ex10 toy models are complete); compare with `solutions/`; expected
program output is in `outputs/`.
