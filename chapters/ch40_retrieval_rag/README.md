# Chapter 40 — Retrieval and RAG

Manuscript: `manuscript/ch40_retrieval_rag.md`. NumPy + standard library only. No network, no API
keys, no model downloads: embeddings come from a deterministic feature-hashing embedder and the
"LLM" is a deterministic extractive mock (`ragkit.MockLLM`).

| ID | Title | Tier | Pattern | Rungs implemented | Section |
|---|---|---|---|---|---|
| ex01 | [Chunking: fixed windows, sentences, headings](solutions/ex01_chunking.py) | ★ | sliding window + greedy packing | char slices → word windows with overlap → heading → sentence → word | 40.2 |
| ex02 | [BM25 from scratch with an inverted index](solutions/ex02_bm25.py) | ★ | inverted index, term-at-a-time | term overlap → TF-IDF → BM25 scan → BM25 index | 40.3 |
| ex03 | [Dense top-k, normalisation, metadata filters](solutions/ex03_dense_topk_filter.py) | ★ | matrix-vector + partial selection | per-row loop + sort → normalised `M @ q` + tie-safe `np.partition`; pre- vs post-filter | 40.4 |
| ex04 | [Hybrid retrieval with reciprocal rank fusion](solutions/ex04_rrf_hybrid.py) | ★ | rank fusion | raw score sum → min-max fusion → RRF (k = 60) | 40.4, 40.5 |
| ex05 | [Second-stage reranking and MMR](solutions/ex05_rerank_mmr.py) | ★ (MMR ◆) | retrieve-then-rerank, greedy diversity | score all → rerank top-n; min-window proximity; MMR | 40.6 |
| ex06 | [Approximate nearest neighbours with IVF](solutions/ex06_ivf_ann.py) | ◆ | coarse clustering + probing | brute force → spherical k-means IVF; recall@10 vs fraction scanned | 40.7 |
| ex07 | [Prompt assembly under a context budget](solutions/ex07_prompt_assembly.py) | ★ | greedy packing + citation map | concatenate → truncate → dedupe + whole-chunk skip-and-continue; edge ordering | 40.8 |
| ex08 | [Retrieval evaluation harness](solutions/ex08_retrieval_eval.py) | ★ | offline eval + regression gate | Recall@K, MRR, chunk → doc mapping, per-query rows, baseline gate | 40.9, 40.11 |
| ex09 | [Groundedness and citation checks](solutions/ex09_groundedness.py) | ★ | claim splitting + evidence matching | any citation → valid citations → per-claim lexical support | 40.9 |
| ex10 | [LLM-as-judge pitfalls](solutions/ex10_llm_judge.py) | ★ | evaluate the evaluator | single order → swap-consistency; Cohen's kappa vs labels | 40.10 |
| ex11 | [End-to-end RAG pipeline with filters and cache](solutions/ex11_rag_pipeline_cache.py) | ★ | pipeline + versioned LRU cache | no cache → raw-string cache → scope-aware, versioned LRU | 40.1, 40.11 |

Shared helper (not an exercise, identical in `solutions/` and `exercises/`):
`ragkit.py`. It provides the corpus/query loaders, `tokenize`/`content_terms`, `count_tokens`
(whitespace words), the hashed `embed`, two baseline rankers, `format_prompt` and `MockLLM`
(modes `extractive`, `hallucinate`, `miscite`).

Data (`data/`), about a fictional object-storage service:
- `corpus.jsonl`: 16 help-centre documents (id, title, area, access, year, Markdown text).
- `queries.json`: 12 labelled queries (relevant document ids).
- `judge_pairs.json`: 10 answer pairs with gold preferences for ex10.

## How to run

```bash
OPENBLAS_NUM_THREADS=4 .venv/Scripts/python chapters/ch40_retrieval_rag/solutions/ex02_bm25.py
.venv/Scripts/python -m pytest chapters/ch40_retrieval_rag                   # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch40_retrieval_rag  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 40                           # regenerate outputs/
.venv/Scripts/python tools/run_all.py --chapter 40 --check                   # determinism check
```

Work in `exercises/`: the stubs raise `NotImplementedError` and carry hints and
wrong-but-tempting answers in place of the approach ladder. Compare with `solutions/`. The
expected program output is in `outputs/`.

## Determinism

Scores are rounded before ranking, and ties always go to the smaller id. The embedder hashes with
`zlib.crc32` (Python's `hash()` is salted per process). Every random draw uses a fixed seed.
Speed claims are shown as work counts (vectors scanned, scorer calls, LLM calls), never as timings.
