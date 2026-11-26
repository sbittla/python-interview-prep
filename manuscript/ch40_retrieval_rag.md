# Chapter 40. Retrieval and RAG

★ Core · Track L (M optional) · Study time ≈ 7 h · Prerequisites: §38.3–§38.6, §35.9, §29.2

**Learning objectives**

- Locate each failure in the RAG pipeline.
- Implement chunking, BM25, RRF and budgeted prompts.
- Evaluate retrieval, answers, ANN recall and the judge.

> **Recognise it**
>
> | You hear | Reach for |
> |---|---|
> | "answer questions over our docs" | RAG pipeline |
> | error codes, ids, product names | BM25 (alone or hybrid) |
> | "users paraphrase" | dense retrieval + RRF |
> | "10⁸ vectors" | ANN, measured by recall@K |
> | "the model makes things up" | citations, groundedness, abstention |

The repo's `ragkit.py` holds a fictional 16-document corpus with 12 labelled queries, a hashed
embedder (→ §38.4; surface overlap only) and `MockLLM`, which copies the best-matching source
sentences with `[n]` citations.

## 40.1 RAG pipeline overview

```text
index:  documents -> chunk -> embed / inverted index -> ANN
query:  query -> cache? -> filter -> retrieve top-n -> rerank to k -> budgeted prompt
        -> LLM -> answer + [n] citations -> groundedness check -> log
```

Fetched text gives fresh facts, citations and document-level access control. Debug each stage
alone: a missed chunk cannot be answered, overflow cuts evidence, an ignored context
hallucinates. In ex11 the permission filter runs *before* ranking, the LRU cache (→ §29.2) keys on
query, filter and index version, and an empty candidate set abstains without a model call:

```text
[public] Who handles a P1 ticket at night? cached=False retrieved=['d01#1', 'd01#0', 'd03#1']
  I don't know.
[staff] Who handles a P1 ticket at night? cached=False retrieved=['d01#1', 'd12#1', 'd01#0']
```

The public "I don't know" is the model abstaining over retrieved public chunks, not the
empty-candidate path. Without the filter in the key, whichever scope asks second gets the first
one's answer; had staff asked first, a public user would get internal text. Semantic cache:
§42.8; service design: §43.2.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex11_rag_pipeline_cache.py`

## 40.2 Chunking strategies: fixed, recursive, semantic

| Strategy | Split | Trade-off |
|---|---|---|
| Fixed + overlap | windows, step `size − overlap` | simple; cuts sentences; index × size/step |
| Recursive | headings → sentences → words, finer only if too big | coherent; heading path |
| Semantic | cut where neighbouring sentence embeddings diverge | topical; embeds every sentence |

```python
def fixed_chunks(text: str, size: int, overlap: int = 0) -> list[str]:
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    words, chunks = text.split(), []
    for start in range(0, len(words), size - overlap):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):          # this window reached the end: stop
            break
    return chunks

print(fixed_chunks("a b c d e f g", 4, 2), fixed_chunks("a b c d", 4, 1), fixed_chunks("", 4))
```

```text
['a b c d', 'c d e f', 'e f g'] ['a b c d'] []
```

Edge cases: `overlap ≥ size` (step ≤ 0 loops forever); without the `break`, a one-window text
emits a contained tail; hard-split, never drop, an over-budget sentence; stable ids (`d06#1`).
→ repo: `chapters/ch40_retrieval_rag/solutions/ex01_chunking.py`

## 40.3 Sparse retrieval: BM25 (lab)

**Worked problem 1 — BM25 from scratch.** For each *distinct* query term t:
score += idf(t)·tf·(k1 + 1) / (tf + k1·(1 − b + b·|d|/avgdl)), where
idf(t) = ln(1 + (N − df + 0.5)/(df + 0.5)).
This is Lucene's "+1 inside the log" variant. The classic Robertson–Spärck Jones
ln((N − df + 0.5)/(df + 0.5)) goes negative when df > N/2: −1.2238 against +0.2578 for N = 10,
df = 8. **k1** saturates tf (k1 = 0 ignores tf); **b** normalises length (b = 0 means none).
Defaults: k1 = 1.2, b = 0.75.

- *Rung 1, count shared terms:* O(N·L). "bucket" weighs as much as the rare "e409".
- *Rung 2, TF-IDF:* rarity-weighted, but linear tf rewards stuffing and long documents.
- *Rung 3, BM25 over an inverted index:* query cost O(Σ postings of the query terms) +
  O(m log k) for m scored documents; build cost O(total tokens). Why move up: it fixes rarity,
  saturation and length in one formula.

```python
import heapq
import math
import re
from collections import Counter, defaultdict

terms = lambda text: re.findall(r"[a-z0-9]+", text.lower())

class BM25:
    def __init__(self, docs: list[tuple[str, str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b, self.ids = k1, b, [d for d, _ in docs]
        self.lens = [len(terms(text)) for _, text in docs]
        self.postings = defaultdict(list)                 # term -> [(doc index, tf)]
        for i, (_, text) in enumerate(docs):
            for t, tf in Counter(terms(text)).items():
                self.postings[t].append((i, tf))
        self.n, self.avgdl = len(docs), sum(self.lens) / max(len(docs), 1)

    def idf(self, t: str) -> float:                       # "+1 inside the log": never negative
        df = len(self.postings.get(t, ()))
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        acc = defaultdict(float)
        for t in set(terms(query)):                       # distinct query terms
            idf = self.idf(t)
            for i, tf in self.postings.get(t, ()):         # only docs containing t
                norm = 1 - self.b + self.b * self.lens[i] / self.avgdl
                acc[self.ids[i]] += idf * tf * (self.k1 + 1) / (tf + self.k1 * norm)
        pairs = [(d, round(s, 4)) for d, s in acc.items()]
        return heapq.nsmallest(k, pairs, key=lambda p: (-p[1], p[0]))

docs = [("short", "bucket error e409"), ("long", "bucket error e409 " + "note " * 30),
        ("spam", "e409 " * 8 + "bucket"), ("other", "pricing per gb")]
for k1, b in [(1.2, 0.75), (1.2, 0.0), (0.0, 0.75)]:
    print(k1, b, BM25(docs, k1, b).search("e409 bucket", 3))
```

```text
1.2 0.75 [('spam', 1.0967), ('short', 1.0291), ('long', 0.4157)]
1.2 0.0 [('spam', 1.039), ('long', 0.7133), ('short', 0.7133)]
0.0 0.75 [('long', 0.7133), ('short', 0.7133), ('spam', 0.7133)]
```

Stuffing "e409" eight times raises the total only 7 % (TF-IDF totals: 4.5×, 3.2101 vs 0.7133);
b = 0 ties short and long; k1 = 0 ignores tf. **Edge-case checklist:** empty corpus, empty or
unknown query, repeated query terms, ties by id, a term in every document. **Wrong but
tempting:** the negative IDF; putting b on tf instead of on |d|/avgdl. **Follow-ups:**
tombstoned deletes, positional postings for phrases, BM25F.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex02_bm25.py`

## 40.4 Dense retrieval and hybrid search

Dense retrieval ranks by cosine (→ §38.5, top-K → §38.6). Two traps. First, raw count vectors make the dot product grow with length (long text: 4.0 vs 2.0; cosine:
0.47 vs 0.63).
Second, `np.argpartition(...)[:k]` returns an arbitrary member of a tie at the k-th place. Normalise
rows once, and keep every candidate scoring at least the k-th value (`np.partition`, O(N)) before
sorting them by (−score, id).

```text
  where year == 2025, post-filter: [('d15#0', 0.2125), ('d12#1', 0.1567)]
  where year == 2025, pre-filter: [('d15#0', 0.2125), ('d12#1', 0.1567), ('d03#1', 0.14)]
```

A post-filter (rank, cut to k, then filter) comes up short. A pre-filter fills k but may admit weak
matches, so add a score threshold. Permission filters must be pre-filters: restricted text must
never reach ranking, prompts or the cache. **Hybrid search** runs
sparse and dense retrieval and fuses the results. Sparse wins on exact tokens and dense on
paraphrase; they fail on different queries.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex03_dense_topk_filter.py`

## 40.5 Reciprocal rank fusion (lab)

**Worked problem 2.** RRF(d) = Σ over lists of 1/(k + rank(d)), with 1-based ranks and k = 60
(Cormack, Clarke and Büttcher, SIGIR 2009). A list that omits d adds 0.

- *Rung 1, add raw scores, O(total):* BM25 is unbounded and cosine is not, so one decides.
- *Rung 2, min-max then weight, O(total):* outlier-sensitive; weights need tuning.
- *Rung 3, RRF:* ranks only; O(total length) + O(u log u) for u ids. Why move up: scores are
  not comparable across retrievers, ranks are, and nothing needs tuning.

```python
from collections import defaultdict

def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores = defaultdict(float)
    for ranking in rankings:
        seen = set()
        for rank, doc in enumerate(ranking, start=1):     # ranks are 1-based
            if doc not in seen:                          # a repeat keeps its first rank
                seen.add(doc)
                scores[doc] += 1 / (k + rank)
    return sorted(((d, round(s, 6)) for d, s in scores.items()), key=lambda p: (-p[1], p[0]))

sparse, dense = ["a", "b", "c", "d"], ["c", "b", "d", "a"]
print("k=1 :", rrf([sparse, dense], k=1))
print("k=60:", rrf([sparse, dense]))
```

```text
k=1 : [('c', 0.75), ('a', 0.7), ('b', 0.666667), ('d', 0.45)]
k=60: [('c', 0.032266), ('b', 0.032258), ('a', 0.032018), ('d', 0.031498)]
```

A small k lets a single first place (`a`) dominate; k = 60 rewards `b`, second in both lists. On
the 12 queries, fusing a weak keyword ranker with the dense one gave this (repo):

```text
MRR: {'keyword': 0.7917, 'dense': 0.9167, 'hybrid': 0.8333}
hybrid below both retrievers on any query: False
```

RRF is usually robust, but it can rank a document below its place in every list: in `[a, r, b]`
and `[b, r, a]`, r is second in both and third after fusion (0.032258 vs 0.032266). Here the hybrid
was never below both but was below the stronger, so measure it (§40.11). **Wrong but tempting:**
0-based ranks. **Edge cases:** an id missing from one list, duplicates in a list, empty lists,
ties, k ≤ 0 (reject). **Follow-ups:** weighted RRF, list depth.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex04_rrf_hybrid.py`

## 40.6 Reranking

A cross-encoder reads query and passage together: more accurate than a bi-encoder's separate
vectors, but one call per pair, so rerank only the top-n (often 50–200); first-stage recall@n
caps the result. The repo's mock cross-encoder (IDF-weighted term coverage plus a shortest-window
proximity bonus, O(L) by sliding window, → §10.5) reranks the dense top-5:

```text
MRR: {'dense': 0.9167, 'rerank': 0.9583} scorer calls: 60 (vs 192 to score every doc)
```

Two queries improved and one got worse: report per-query changes. **MMR** reranks for
diversity: greedily take argmax λ·sim(q, d) − (1 − λ)·max over selected s of sim(d, s). Each pick
costs O(k·n) look-ups, after an O(n²d) similarity matrix. In the repo, λ = 0.5 skips a
near-duplicate (identical embedding) that λ = 1 keeps.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex05_rerank_mmr.py`

## 40.7 Approximate nearest neighbour: HNSW, IVF, product quantisation; FAISS-style trade-offs ◆

| Index | Idea | Knob | Risk |
|---|---|---|---|
| IVF | k-means into `nlist` lists; scan the `nprobe` nearest | `nprobe` | boundary misses, stale centroids |
| HNSW | greedy search on a layered proximity graph | `ef` | graph memory; awkward deletes |
| PQ | m sub-vectors, one 1-byte code each | m | lossy distances |

Libraries such as FAISS compose these (IVF + PQ). Storing 10⁸ × 768 float32
values takes ≈ 307 GB; with m = 96 one-byte codes it is 96 B per vector, 32× less. The repo's IVF
(spherical k-means, → §36.4) over 4,000 vectors with `nlist = 64`:

```text
nprobe recall@10 scanned/N
     1     0.522     0.019
     4     0.794     0.065
    16     0.949     0.251
    64     1.000     1.000
```

Report recall@K against brute force, not latency alone.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex06_ivf_ann.py`

## 40.8 Prompt assembly and context-window management

**Worked problem 3.** The prompt plus the tokens reserved for the answer must fit the budget
(→ §38.3). *Rung 1*, concatenate all, O(total): overflows. *Rung 2*, cut at the budget, O(total): halves a chunk and,
in the repo run, drops the question. *Rung 3*, the code below: dedupe on normalised text, go by
score (ties by id), add whole chunks, skip a chunk that does not fit and keep trying smaller ones,
then number them. O(n log n + total tokens). Why move up: the budget goes to distinct, complete,
relevant evidence and the question always survives. Exact packing is 0/1 knapsack (→ §19.6).

```python
HEAD = "Answer only from the sources; cite [n]; else say: I don't know."

def assemble(question: str, chunks: list[dict], budget: int, reserve: int):
    n_tok = lambda s: len(s.split())                  # stand-in for the model's tokenizer
    used = n_tok(HEAD) + n_tok("Question: " + question) + reserve
    if used > budget:
        raise ValueError("instructions + question + reserve exceed the budget")
    lines, sources, dropped, seen = [], {}, [], set()
    for c in sorted(chunks, key=lambda c: (-c["score"], c["id"])):
        key = " ".join(c["text"].lower().split())
        line = f"[{len(lines) + 1}] ({c['id']}) {c['text']}"
        if key in seen or used + n_tok(line) > budget:
            dropped.append((c["id"], "duplicate" if key in seen else "budget"))
            continue                                  # skip, keep trying smaller chunks
        seen.add(key)
        used += n_tok(line)
        lines.append(line)
        sources[len(lines)] = c["id"]
    return "\n".join([HEAD, *lines, "Question: " + question]), sources, dropped

chunks = [{"id": "d08#1", "score": 0.61, "text": "E409 BucketNotEmpty: delete every version first."},
          {"id": "d08#9", "score": 0.61, "text": "e409 BucketNotEmpty:  DELETE every version first."},
          {"id": "d14#0", "score": 0.55, "text": "A bucket must be empty before deletion. " * 4},
          {"id": "d02#1", "score": 0.30, "text": "Deleting an object adds a delete marker."}]
prompt, sources, dropped = assemble("Why does deleting my bucket fail with E409?", chunks, 53, 15)
print(prompt, sources, dropped, len(prompt.split()) + 15 <= 53, sep="\n")
```

```text
Answer only from the sources; cite [n]; else say: I don't know.
[1] (d08#1) E409 BucketNotEmpty: delete every version first.
[2] (d02#1) Deleting an object adds a delete marker.
Question: Why does deleting my bucket fail with E409?
{1: 'd08#1', 2: 'd02#1'}
[('d08#9', 'duplicate'), ('d14#0', 'budget')]
True
```

**Edge-case checklist:** the question alone overflows (raise); nothing fits (the model must
abstain); re-ingested duplicates; a chunk exactly at the budget; deterministic order, which prompt
caching needs. **Wrong but tempting:** `break` at the first misfit; forgetting the reserve.
**Follow-ups:** "Lost in the Middle" (Liu et al., 2023) → best chunks at both ends
(`edge_order`); context may carry injected instructions (→ §42.11).
→ repo: `chapters/ch40_retrieval_rag/solutions/ex07_prompt_assembly.py`

## 40.9 RAG evaluation: Recall@K, faithfulness, groundedness

**Retrieval:** Recall@K, MRR, nDCG for graded labels (→ §35.9), on deduped ids, chunks mapped to
labelled documents.
**Generation:** faithfulness (groundedness) means every claim follows from the cited context; it
is neither correctness nor answer relevance. The repo checks each sentence's `[n]`, then lexical
support from the *cited* sources only:

```text
'Plain HTTP requests are not rejected [1].'     -> [('supported', 0.8)]
mode         grounded cites ok abstain  (mean over 12 queries, top-3 chunks)
extractive     1.0000   1.0000       3
hallucinate    0.6945   1.0000       3
miscite        0.2917   0.9167       3
```

Wrong-source citations fail even for true claims. The negation passes: overlap cannot see "not";
an NLI model or judge per claim can. Report abstentions: "I don't know" is always grounded.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex09_groundedness.py`

## 40.10 LLM-as-judge pitfalls

The repo's mock judge has the two most reported biases: it favours the first and the longer answer.

```text
judge             mode     accuracy coverage flip rate
position 0.3      single     0.9000   1.0000    0.4000
position 0.3      swap       1.0000   0.6000    0.4000
length 0.02/word  swap       0.8000   1.0000    0.0000
```

Accuracy 0.9 hid 40 % order flips. Swapping and abstaining on disagreement fixes position bias but
costs 2× the calls and coverage (0.6: 40 % of items get no verdict); it does not fix length bias. Add a reference and rubric, a judge from another model family
(self-preference) and Cohen's κ against human labels: 90 % raw agreement can be κ = 0.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex10_llm_judge.py`

## 40.11 Building a small evaluation harness (lab)

The harness skips unlabelled queries (not scored 0), keeps per-query rows and fails when a metric
falls more than a tolerance below the baseline:

```text
retriever                 R@1    R@3    R@5    MRR   n  skipped
dense (docs)           0.7500 1.0000 1.0000 0.9167  12  ['q13']
dense (chunks->docs)   0.6667 0.9167 1.0000 0.8542  12  ['q13']
```

The gate flags the chunk retriever (MRR, R@1, R@3): a document's terms are spread over its sections. One of 12 queries moves MRR
by up to 1/12, so bootstrap (→ §35.5) and grow the set from production logs.
→ repo: `chapters/ch40_retrieval_rag/solutions/ex08_retrieval_eval.py`

## Interviewer's view

- Name the failing stage and its metric; state conventions (IDF variant, k1, b, RRF k = 60).
- Raise ties and empty/overflow cases unprompted; measure instead of asserting.
- Security: permission pre-filters, scope-aware cache keys, untrusted context.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Chunking | ★ | window, packing |
| ex02 | BM25 index | ★ | postings |
| ex03 | Dense top-k, filters | ★ | partial selection |
| ex04 | Hybrid RRF | ★ | rank fusion |
| ex05 | Rerank, MMR | ★ | two-stage |
| ex06 | IVF ANN | ◆ | clustering |
| ex07 | Prompt budget | ★ | greedy packing |
| ex08 | Eval harness | ★ | regression gate |
| ex09 | Groundedness | ★ | claim checks |
| ex10 | Judge pitfalls | ★ | swap, κ |
| ex11 | Pipeline + cache | ★ | versioned LRU |

Index: `chapters/ch40_retrieval_rag/README.md`.

## Checkpoint quiz

1. What breaks with ln((N − df + 0.5)/(df + 0.5)) when df = 0.8·N?
2. Why can `np.argpartition(-s, k)[:k]` give the wrong top-k?
3. Why does RRF fuse ranks, and what does a larger k do?
4. Why is the permission filter part of the cache key?
5. A judge is 90 % accurate but flips 40 % of verdicts on swapping. What next?

<details>
<summary>Answers</summary>

1. The IDF is negative, so matching a common term lowers the score.
2. With a tie at the k-th score it returns an arbitrary subset; keep every candidate ≥ the k-th
   score, then sort.
3. Scores are not comparable across retrievers; a larger k rewards consistency across lists.
4. Otherwise internal-document answers reach users without access.
5. Judge both orders and abstain on disagreement; check length bias and κ against human labels.

</details>

## Summary card

- BM25: idf = ln(1 + (N − df + .5)/(df + .5)); k1 saturates tf, b normalises length.
- Dense: normalise; tie-safe top-K; pre-filter permissions. RRF: Σ 1/(60 + rank).
- Rerank the top-n only. ANN: report recall@K.
- Prompt: reserve, dedupe, whole chunks, skip-and-continue, `[n]` → id.
- Eval: Recall@K, MRR, groundedness + abstention; validate the judge.
