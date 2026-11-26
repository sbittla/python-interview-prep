# Chapter 44. Concept Q&A Bank

★ Core · Tracks S M L · Study time ≈ 3 h, then 15 min a day · Prerequisites: the chapters each
answer cites

**Learning objectives**

- Answer conceptual questions in one to three crisp sentences.
- Follow each (→ §N.k) back to the section that teaches it.
- Drill with spaced repetition; check "predict the output" answers by running them.

> **How to use this bank.** Cover the answer, say yours aloud in under 30 seconds, compare, and
> after a miss reread the cited section. The full bank (102 entries; `book`
> marks the 56 printed here) is `chapters/ch44_concept_qa_bank/data/qa_bank.json`.

**Drilling the bank.**

1. **Day 0:** answer one section cold and log each miss by id (`py05`).
2. **Schedule (ex02):** Leitner boxes on the §3.4 ladder. A right answer moves the card up a box, due
   1, 3, 7, then 21 days later; five in a row retire it. A miss sends it to box 0, due tomorrow.
3. **Mix (ex03):** deal questions round-robin across sections; keyword grading only triages.
4. **Predict the output (ex04):** commit to an answer, then run it. The tests re-execute every
   snippet, so the key matches real Python.

## 44.1 Python language and internals

**py01. Why is a mutable default argument a bug?** The default is evaluated once, at `def` time, so every call that omits it shares one object. Default to `None` and create the list inside. (→ §7.1)

**py02. `is` or `==`?** `==` compares values through `__eq__`; `is` compares identity. Use `is` only for singletons such as `None`; small-int caching is a CPython detail. (→ §7.6)

**py03. Why does `[[0] * 3] * 3` misbehave?** The outer `* 3` repeats one reference, so every row is the same list. Build rows with `[[0] * 3 for _ in range(3)]`. (→ §7.3)

**py05. What is late binding in closures?** A closure reads a variable when called, not when created, so loop lambdas all see the final value. Bind early: `lambda i=i: i`. (→ §7.5)

**py06. When do you need `nonlocal`?** Assigning to a name anywhere in a function makes it local there, so `x += 1` on an outer `x` raises `UnboundLocalError`. Declare `nonlocal x` (or `global x`). (→ §5.8)

**py08. What if a class defines `__eq__` but not `__hash__`?** Python sets `__hash__` to `None`, so instances are unhashable. Hash the same immutable fields that `__eq__` compares. (→ §24.6)

**py10. What does `functools.wraps` do?** It copies `__name__`, `__doc__` and other metadata onto the wrapper and sets `__wrapped__`, so `help()` and `inspect.signature` describe the original. (→ §25.3)

**py11. How does CPython free memory?** Reference counting frees an object when its count hits zero; a generational cycle collector (`gc`) reclaims groups that only reference each other. (→ §27.2)

**Predict the output** (four of the 18 snippets in `data/predict_output.json`):

```python
def add(x, bucket=[]):
    bucket.append(x)
    return bucket

print(add(1), add(2))

fs = [lambda: i for i in range(3)]
print([f() for f in fs])

print(-7 // 2, -7 % 2, round(2.5), round(3.5))

squares = (n * n for n in range(4))
print(sum(squares), sum(squares))
```

<details><summary>Output</summary>

```text
[1, 2] [1, 2]
[2, 2, 2]
-4 1 2 4
14 0
```

(1) One shared list, printed after both calls (→ §7.1). (2) Late binding (→ §7.5). (3) `//` floors
toward −∞; `round` sends halves to even (→ §7.9). (4) The generator is spent after one `sum` (→ §7.12).
</details>

## 44.2 Data structures and complexity

**ds01. What does a dict lookup cost?** O(1) on average, O(n) in the worst case when many keys collide. (→ §6.5)

**ds02. Why is `list.append` O(1) if lists must grow?** Lists over-allocate in proportion to their size, so n appends copy O(n) elements in total: O(1) amortised, a worst-case bound on the total, not an average. (→ §22.3)

**ds03. Why use `deque` instead of `list.pop(0)`?** `pop(0)` shifts every remaining element, O(n); a `deque` pops either end in O(1), though indexing its middle is O(n). (→ §7.15)

**ds05. How do you get a max-heap from `heapq`?** `heapq` is a min-heap (push and pop O(log n), `heapify` O(n)). Push negated keys, or wrap items in a class with reversed `__lt__`. (→ §15.2)

**ds06. Why avoid `s += piece` in a loop?** Strings are immutable, so each `+=` may copy everything: O(n²) in the worst case. `"".join(parts)` is reliably linear. (→ §7.17)

**ds08. Big-O or Big-Θ?** Big-O is an upper bound, Big-Θ a tight one. "Binary search is O(n)" is true but useless, so give the tight bound. (→ §8.2)

**ds09. What space does a recursive tree DFS use?** O(h) for the call stack: O(log n) if balanced, O(n) if path-shaped. Deep inputs can hit CPython's default recursion limit of 1000. (→ §8.5)

**ds10. Given n ≤ 10⁵, what complexity should you aim for?** O(n log n) or better: about 1.7·10⁶ basic steps, whereas O(n²) is 10¹⁰. (→ §8.7)

## 44.3 Algorithms and patterns

**al01. Which signals point to a sliding window?** A contiguous subarray or substring, a longest, shortest or at-most-k goal, and a condition monotone in window size. Each index enters and leaves once: O(n). (→ §10.5)

**al02. Why prefix sums, not a window, for "count subarrays summing to k"?** Negative numbers break the window's shrink rule. Count earlier prefix sums equal to `prefix - k` in a dict: O(n). (→ §10.9)

**al03. When does binary search on the answer apply?** When feasibility is monotone: if x works, so does every larger x (or every smaller). Search for the boundary in O(log(range) × cost of a check). (→ §11.4)

**al04. Why BFS for shortest paths in an unweighted graph?** BFS reaches nodes in order of distance, so the first visit is along a shortest path. DFS finds a path, not necessarily the shortest. (→ §16.3)

**al05. When does Dijkstra's algorithm fail?** With negative edge weights: it finalises a node when popped, assuming no later path is shorter. Use Bellman-Ford, O(VE), which also detects negative cycles. (→ §16.10)

**al07. What two properties signal dynamic programming?** Overlapping subproblems (the same subproblem recurs) and optimal substructure (an optimal answer combines optimal answers to subproblems). Then write the state, transition and base case. (→ §19.1)

**al08. Greedy or DP?** Greedy needs an exchange argument proving the local choice safe. A counterexample (coins 1, 3, 4 and amount 6: greedy uses 3 coins, the optimum 2) means DP. (→ §20.7)

**al10. What does a monotonic stack solve?** Next-greater and next-smaller questions in O(n): each index is pushed once and popped at most once, when the current item answers it. (→ §12.4)

## 44.4 Concurrency and performance

**cc01. What does the GIL limit?** In default CPython one thread runs bytecode at a time, so CPU-bound threads do not run in parallel. It does not make code thread-safe: `x += 1` can lose updates. (→ §27.5)

**cc02. Threads, processes or asyncio for CPU-bound pure Python?** Processes, such as `ProcessPoolExecutor`: one GIL each on the default build. Threads suit blocking I/O; asyncio suits thousands of sockets. (→ §27.7)

**cc03. What is the status of free-threaded Python?** Experimental in 3.13 (PEP 703); officially supported in 3.14 (PEP 779) but still opt-in, with single-thread overhead and C extensions that must declare support. (→ §27.6)

**cc04. Concurrency or parallelism?** Concurrency is tasks in progress over the same period, taking turns. Parallelism is tasks executing at the same instant on different cores. (→ §28.1)

**cc06. What if you call a coroutine function without `await`?** You get a coroutine object that never runs, plus a "never awaited" warning. Await it, or wrap it in a Task. (→ §28.5)

**cc07. Why is `time.sleep` inside `async def` a bug?** It blocks the event loop's thread, so every task stalls. Use `await asyncio.sleep(...)`, or run blocking work via `asyncio.to_thread`. (→ §28.9)

**cc08. `gather` or `TaskGroup` when a task fails?** `gather` propagates the first exception but leaves the siblings running; `TaskGroup` (3.11+) cancels them and raises an `ExceptionGroup`. (→ §28.6)

**cc10. Why must you re-raise `CancelledError`?** Swallowing it breaks timeouts, `TaskGroup` and shutdown. Clean up in `finally` and let it propagate. (→ §28.7)

## 44.5 Testing and engineering practice

**te01. Fixture or parametrize?** A fixture supplies setup, and teardown after `yield`, to each test that names it; `@pytest.mark.parametrize` runs one test body over many cases. (→ §31.1)

**te02. Which test cases should every function get?** The happy path, edges (empty, one item, duplicates, extremes), errors that must raise, and a property check against a brute-force oracle. (→ §31.2)

**te03. Where do you point `unittest.mock.patch`?** At the name where it is looked up, not where it is defined: if `app.py` does `from api import fetch`, patch `app.fetch`. (→ §31.3)

**te04. What is the debugging-round loop?** Reproduce with a failing test, isolate the smallest failing case, fix the cause, then verify with that test plus the existing suite. (→ §31.4)

**te05. How do you read a traceback fast?** Read the last line first (type and message), then walk up to the deepest frame in your own code. Chained exceptions print the original one first. (→ §31.6)

**te07. How do you build an O(1) LRU cache?** A dict maps keys to nodes of a doubly linked list in recency order: `get` moves a node to the front, `put` evicts the tail. Or use `OrderedDict`. (→ §29.2)

**te08. Fixed-window or token-bucket rate limiter?** A fixed window can admit twice the limit in a burst across a boundary. A token bucket refills steadily up to a capacity: bounded bursts, smooth average. (→ §29.5)

**te10. WHERE or HAVING?** WHERE filters rows before grouping and cannot use aggregates; HAVING filters groups after GROUP BY and can. (→ §30.6)

## 44.6 ML and statistics

**ml01. Precision or recall?** Precision = TP/(TP+FP), the flagged items that are right; recall = TP/(TP+FN), the positives found. Favour recall when misses cost most. (→ §35.7)

**ml02. Why can 99 % accuracy be useless?** With 1 % positives, always predicting negative scores 99 %. Report precision, recall or average precision instead. (→ §35.7)

**ml03. What does ROC-AUC measure?** The chance that a random positive scores above a random negative, ties counting half. It is threshold-free but flatters rare-positive models; check average precision too. (→ §35.7)

**ml05. What does a p-value mean?** Assuming the null hypothesis is true, the probability of a result at least as extreme as the one observed. It is not the probability that the null is true. (→ §35.6)

**ml06. What is a classic cross-validation leakage bug?** Fitting a scaler, imputer or feature selector on all the data before splitting. Fit preprocessing inside each fold. (→ §35.11)

**ml07. Why subtract the max logit before softmax?** Large logits overflow `exp`; softmax ignores a constant shift, so subtracting the max keeps every exponent at most 0. Log-sum-exp applies the same trick to cross-entropy. (→ §35.10)

**ml08. MSE or MAE?** MSE squares errors, so outliers dominate and the best constant prediction is the mean. MAE is more robust to outliers, and its best constant is the median. (→ §35.8)

**ml11. What does `model.eval()` change in PyTorch?** Dropout turns off and batch norm uses its running statistics. Gradients are still tracked, so wrap inference in `torch.no_grad()`. (→ §37.5)

## 44.7 GenAI and LLM engineering

**ai01. Why scale attention scores by 1/√d_k?** With independent zero-mean, unit-variance components, a query–key dot product has variance d_k; large scores saturate softmax and shrink gradients. Scaling restores a variance of about 1. (→ §39.1)

**ai02. What does a causal mask do?** It sets future positions' scores to −∞ before softmax, so position t attends only to positions up to t. Training then predicts every next token in parallel. (→ §39.3)

**ai03. What does a KV cache save, and what does it cost?** It keeps each layer's past keys and values, so a new token computes only its own. Memory ≈ 2 × layers × kv_heads × head_dim × tokens × bytes, per sequence. (→ §39.7)

**ai04. What do temperature, top-k and top-p do?** Temperature divides the logits (below 1 sharpens, above 1 flattens). Top-k keeps the k likeliest tokens; top-p the smallest set whose total probability reaches p. (→ §39.8)

**ai08. How does reciprocal rank fusion score a document?** It sums 1 / (k + rank) over the ranked lists, commonly with k = 60. Only ranks matter, so the retrievers' scores need no calibration. (→ §40.5)

**ai10. Retrieval recall or faithfulness?** Measure both: Recall@K checks that the right chunks were retrieved; faithfulness checks that the answer's claims are supported by them. Either can fail alone. (→ §40.9)

**ai14. Why exponential backoff with jitter?** Backoff lets an overloaded service recover; jitter stops clients retrying in synchronised waves. Retry only idempotent (or idempotency-keyed) requests. (→ §42.3)

**ai15. What is prompt injection?** Instructions in untrusted content (web pages, documents, tool output) that the model may obey. Treat that content as data, give tools least privilege, confirm side effects. (→ §42.11)

## Keeping the answer key honest

A written key goes stale silently. Ex04's core runs each snippet in a fresh namespace and compares
its output:

```python
import contextlib
import io


def run_snippet(code: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):            # restored even on errors
        try:
            exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
        except Exception as exc:                     # type only: messages vary
            print(f"raises {type(exc).__name__}")
    return buf.getvalue()


def check(items):
    return [(it["id"], it["expected"], got) for it in items
            if (got := run_snippet(it["code"])) != it["expected"]]


items = [{"id": "po12", "code": 'd = {"a": 1}\nfor k in d:\n    d[k + "!"] = 2',
          "expected": "raises RuntimeError\n"},
         {"id": "stale", "code": "print(0.1 + 0.2 == 0.3)", "expected": "True\n"}]
print(check(items))
```

```text
[('stale', 'True\n', 'False\n')]
```

Catching `Exception`, not `BaseException`, lets `KeyboardInterrupt` through; `exec` is for
trusted snippets only. Ex01 does the same for cross-references: any `xref` missing from the parsed
`COURSE_OUTLINE.md` fails.
→ repo: `chapters/ch44_concept_qa_bank/solutions/ex04_predict_output.py`.

## Interviewer's view

Conceptual questions are quick probes. The rubric rewards a direct first sentence, the mechanism
("evaluated once, at `def` time") and the caveat a practitioner adds. "I'd check X" beats a
confident wrong answer.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Q&A bank loader and validator | ★ | schema + xref validation |
| 02 | Seeded Leitner scheduler | ★ | spaced repetition |
| 03 | Quiz runner over scripted answers | ◆ | stratified sampling, grading |
| 04 | "Predict the output" sets, verified by execution | ★ | executable answer key |
| 05 | Section, tag and chapter coverage report | ○ | group-and-count |

Index: `chapters/ch44_concept_qa_bank/README.md`.

## Checkpoint quiz

1. A card is answered right on days 0, 1 and 4, then wrong on day 11. When is it next due, and in
   which box?
2. Why does ex04 print only the exception's type, not its message?
3. What does `print({1: "a", True: "b"})` print?
4. Why should the quiz grader match `rank` as a whole word?
5. A bank entry cites §7.31. Which check catches it?

<details><summary>Answers</summary>

1. Day 12, in box 0. A wrong answer resets the card to box 0, due `ladder[0]` = 1 day later.
2. Messages are reworded between versions; exception types are documented behaviour and change
   far more rarely.
3. `{1: 'b'}`: `True == 1` with equal hashes, so key `1` stays and its value is replaced (→ §7.6).
4. So that "ranking" is not a hit: normalise both sides, then match `" rank "`.
5. Ex01's outline check: Chapter 7 lists only §7.1–§7.28.
</details>

## Summary card

- Answer in 1–3 sentences (claim, mechanism, caveat), then cite the teaching section.
- Leitner on the §3.4 ladder (+1, +3, +7, +21 days; a miss resets to box 0); cap and shuffle.
- Commit to a "predict the output" answer before running it; keep the answer key executable.
- Validate the bank in CI (schema, sentence count, keywords, xrefs against the outline); reread the
  sections with the most misses first (ex05).
