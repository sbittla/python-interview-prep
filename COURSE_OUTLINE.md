# The Complete Python Coding Interview Course
### From Python Fundamentals to DSA, Practical Engineering Rounds, and AI/ML/LLM Coding Interviews

> Built from the revised architecture in *Course Outline Review and Improvement Plan* (18 Nov 2026).
> **9 parts (0–VIII) · 48 chapters · 8 appendices · 150-problem bank + 30 AI labs + ~120 in-chapter exercises**
> Python baseline: write portable **3.10+** code; features needing 3.12–3.14 are flagged.

---

## How to use this course

### Tracks
| Code | Track | Who it is for | Parts |
|---|---|---|---|
| **S** | Software Engineering | General SWE / backend loops | 0, I, II, III, IV, V, VIII |
| **M** | Data / ML | Data scientist, ML engineer | 0, I, II, III, V, VI, VIII (IV optional) |
| **L** | GenAI / LLM | AI / LLM engineer | 0, I, II, III, IV, V, VII, VIII (VI optional) |

### Tier tags (every section is tagged)
| Tag | Tier | Meaning |
|---|---|---|
| ★ | **Core** | Asked often. Must master. |
| ◆ | **Extended** | Asked in harder rounds or specific roles. Learn after Core. |
| ○ | **Reference** | Rare. Skim, know it exists, look up when needed. |

### Chapter template (v2) — every teaching chapter follows this
1. Learning objectives and prerequisites (3–5 bullets)
2. Frequency/tier tag and typical interview level
3. **"Recognise it" box** — signal words and constraints that point to this pattern
4. Concept and syntax
5. Simple → intermediate → advanced examples
6. **Approach ladder** for each key problem: brute force → improved → optimal (with "why we move up a rung")
7. Follow-up questions the interviewer asks next
8. Edge-case checklist and test cases
9. Common mistakes and wrong-but-tempting solutions
10. Interviewer's view: what the rubric rewards
11. Checkpoint quiz (5 questions)
12. One-page summary card

---

## PART 0 — Orientation and Strategy `S M L`

### Chapter 1. The Interview Landscape ★
1.1 Interview loop anatomy: screen, online assessment, coding, practical, design, behavioural
1.2 Round formats: whiteboard, shared editor, online judge, take-home, pair programming
1.3 Platforms and environments (online judges, CoderPad-style editors, notebooks)
1.4 AI-free vs AI-allowed rounds — how to verify a company's current policy
1.5 What SWE, Data/ML and GenAI/LLM loops test differently
1.6 How you are scored: signals interviewers look for
1.7 Choosing your track and study plan

### Chapter 2. Interview Playbook (Short Form) ★
2.1 The 6-step method: clarify → examples → brute force → optimise → code → test
2.2 Clarifying questions checklist (input size, types, duplicates, empties, sortedness)
2.3 Thinking aloud: communication scripts and phrases
2.4 Stating complexity before and after coding
2.5 When stuck: hints, simplifying the problem, working small cases
2.6 Testing your own code: dry runs and edge-case walkthroughs
2.7 Time management in 45- and 60-minute rounds
2.8 Recovering from mistakes gracefully

### Chapter 3. Diagnostic Test and Track Selection ★
3.1 30-question diagnostic: Python behaviour, complexity reasoning, two coding problems
3.2 Scoring and placement: fast track vs full path
3.3 Mapping results to tracks and weekly plans
3.4 Setting up a spaced-repetition log (revisit at 1, 3, 7, 21 days)

### Chapter 4. Setup, I/O and Python Version Baseline ★
4.1 Environment setup: interpreter, venv, editor, `pytest`
4.2 Python version baseline (3.10+) and checking the judge's version
4.3 stdin/stdout handling: `input()`, `sys.stdin.readline`, fast bulk reads
4.4 Parsing common input formats: lines, matrices, multiple test cases
4.5 Output formatting and fast printing
4.6 Using the companion repository and running tests
4.7 What's new in 3.12–3.14 (not required for interviews) ○

---

## PART I — Python Essentials (Fast Track) `S M L`
> Gate: skip Chapters 5–6 if you pass the diagnostic. Do **not** skip Chapters 7–8.

### Chapter 5. Syntax, Types, Control Flow and Functions ★
5.1 Variables, dynamic typing and names vs objects
5.2 Numeric types: `int` (unbounded), `float`, `bool` (complex numbers ○ — one line)
5.3 Strings: indexing, slicing, methods, f-strings, immutability
5.4 Conditionals, `match` statement ◆
5.5 Loops: `for`, `while`, `range`, `enumerate`, `zip`, `for…else`
5.6 Functions: positional/keyword args, `*args`, `**kwargs`, defaults, return values
5.7 Lambdas and first-class functions
5.8 Scope: LEGB, `global`, `nonlocal`
5.9 Type hints basics (not enforced at runtime)
5.10 Comprehensions — one-line preview (full treatment in Ch. 23)

### Chapter 6. Built-in Collections, Idioms and the Stdlib Toolbox ★
6.1 Lists: operations, slicing, complexity of each operation
6.2 Tuples, unpacking, named tuples
6.3 Sets and frozensets: membership, set algebra
6.4 Dictionaries: methods, iteration order, dict views
6.5 Hashing and collisions — how dict/set work internally (canonical home)
6.6 Strings as sequences: `join`, `split`, `ord`/`chr`, character counting
6.7 `collections`: `Counter`, `defaultdict`, `deque`, `OrderedDict`, `namedtuple` (canonical home)
6.8 `heapq` toolbox: `heappush`, `heappop`, `heapify`, `nlargest`, `nsmallest` (canonical home)
6.9 `bisect` toolbox: `bisect_left`, `bisect_right`, `insort` (canonical home)
6.10 `itertools` essentials: `accumulate`, `product`, `permutations`, `combinations`, `groupby`
6.11 `functools` essentials: `lru_cache`, `cache`, `cmp_to_key`, `reduce`
6.12 Sorting: `sorted` vs `.sort()`, `key=`, stability, multi-key sorts
6.13 Pythonic idioms: swapping, `any`/`all`, `min`/`max` with key, `enumerate`
6.14 Choosing the right built-in: complexity table
6.15 `array` module ○ — one-line mention

### Chapter 7. Python Gotchas and Interview Traps ★
Each trap has a "predict the output" quiz.
7.1 **References:** mutable default arguments
7.2 **References:** aliasing (`a = b = []`), shallow vs deep copy (canonical home)
7.3 **References:** `[[0] * n] * m` shares rows
7.4 **References:** mutable class variables shared across instances
7.5 **Scope:** late binding in closures and loop lambdas; `nonlocal`
7.6 **Equality:** `is` vs `==`, small-integer caching, `bool` subclasses `int`
7.7 **Equality:** `__eq__` without `__hash__`
7.8 **Numbers:** floating-point error; `math.isclose`, `Decimal`, `Fraction`
7.9 **Numbers:** `//` and `%` with negatives; banker's rounding in `round()`
7.10 **Numbers:** unbounded ints, `float('inf')`, overflow assumptions from other languages
7.11 **Iteration:** mutating a list/dict while iterating
7.12 **Iteration:** exhausted generators; `zip`/`map` return iterators
7.13 **Iteration:** `for … else` semantics
7.14 **Collections:** `defaultdict` creates keys on read; `Counter` subtraction drops ≤0
7.15 **Collections:** `list.pop(0)` / `insert(0, x)` are O(n) — use `deque`
7.16 **Collections:** `x in list` O(n) vs set/dict O(1)
7.17 **Collections:** slicing copies; string `+=` in loops O(n²)
7.18 **Collections:** `deque` middle indexing is O(n)
7.19 **Sorting:** stability, `key` vs `cmp_to_key`, mixed types and `None`
7.20 **Heaps:** min-only (negate for max); tuple tie-breaks compare next field
7.21 **Recursion:** ~1000 default limit, no tail-call optimisation, `sys.setrecursionlimit`
7.22 **Caching:** `lru_cache` needs hashable args; unbounded `cache` memory growth
7.23 **Strings:** `split()` vs `split(' ')`; immutability; Unicode vs bytes
7.24 **Concurrency:** GIL and optional free-threaded build; threads vs processes vs asyncio
7.25 **Concurrency:** forgetting `await`, blocking calls in async, unbounded `gather`
7.26 **Typing:** hints are not enforced at runtime
7.27 **Serialisation:** `pickle` is unsafe on untrusted data
7.28 Gotchas cumulative quiz

### Chapter 8. Big-O Primer ★
8.1 Why complexity matters in interviews
8.2 Big-O, Big-Θ, Big-Ω in plain language
8.3 Counting operations: loops, nested loops, halving
8.4 Common classes: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ), O(n!)
8.5 Space complexity and the call stack
8.6 Complexity of Python built-in operations (cheat table)
8.7 Reading constraints: input size → acceptable complexity
8.8 Quick quiz: estimate complexity of 10 snippets

---

## PART II — Core Data Structures and Patterns `S M L`

### Chapter 9. Arrays, Strings and Hashing ★
9.1 Array traversal patterns and in-place updates
9.2 Frequency counting with dicts and `Counter`
9.3 Two-sum family with hash maps
9.4 Grouping (anagrams, keys by signature)
9.5 String building, palindromes, reversal
9.6 Matrix traversal: rows, columns, diagonals, spiral, rotation
9.7 Cyclic sort and in-place index tricks (missing/duplicate numbers) ◆
9.8 Set-based deduplication and membership problems
9.9 Encoding/decoding strings
9.10 Practice set

### Chapter 10. Two Pointers, Sliding Window and Prefix Sums ★
10.1 Opposite-direction two pointers (sorted pair/triple sum)
10.2 Same-direction pointers (remove duplicates, partitioning)
10.3 Fast and slow pointers
10.4 Fixed-size sliding window
10.5 Variable-size sliding window (longest/shortest with condition)
10.6 Window with hash map (distinct characters, anagram windows)
10.7 Sliding window maximum → links to monotonic deque (Ch. 12)
10.8 Prefix sums: 1D and 2D
10.9 Prefix sum + hash map (count subarrays with sum k)
10.10 Difference arrays for range updates ◆
10.11 Practice set

### Chapter 11. Binary Search and Sorting ★
11.1 Classic binary search and loop invariants
11.2 Lower/upper bound, first/last occurrence (`bisect`)
11.3 Rotated sorted arrays
11.4 Binary search on the answer (monotonic feasibility)
11.5 Binary search on 2D matrices
11.6 Merge sort (and counting inversions)
11.7 Quick sort and partition schemes
11.8 Heap sort
11.9 Counting sort and bucket sort ◆
11.10 Radix sort ○
11.11 "Know these" page: bubble, selection, insertion sort ○
11.12 Sort-based patterns: custom comparators, sorting then scanning
11.13 Quickselect (Kth element) ◆
11.14 Practice set

### Chapter 12. Stacks, Queues and Monotonic Structures ★
12.1 Stack with a list; queue with `deque`
12.2 Balanced parentheses and expression evaluation
12.3 Min stack and stack design problems
12.4 Monotonic stack: next greater/smaller element, stock span
12.5 Largest rectangle in histogram; trapping rain water
12.6 Monotonic deque: sliding window maximum (canonical home)
12.7 Queue via stacks, stack via queues
12.8 Circular queue design
12.9 Practice set

### Chapter 13. Linked Lists ★
13.1 Node class, building and printing lists
13.2 Traversal, insertion, deletion; dummy head technique
13.3 Reversal: iterative and recursive; reverse in k-groups ◆
13.4 Fast/slow pointers: middle, cycle detection (Floyd), cycle start
13.5 Merge two sorted lists; merge k lists (→ heaps)
13.6 Remove nth from end, intersection, palindrome list
13.7 Doubly linked lists
13.8 Copy list with random pointer ◆
13.9 Practice set
> LRU cache is built in Ch. 29 (canonical home) using this chapter's doubly linked list.

### Chapter 14. Recursion, Trees and BST ★
14.1 Recursion fundamentals: base case, recursive case, call stack
14.2 Recursion → iteration with an explicit stack
14.3 Memoisation preview (→ DP)
14.4 Binary tree basics and representations
14.5 DFS traversals: preorder, inorder, postorder (recursive and iterative)
14.6 BFS / level-order traversal and variants (zigzag, right view)
14.7 Height, depth, diameter, balanced check
14.8 Path problems: path sum, max path sum ◆
14.9 Lowest common ancestor
14.10 Construct tree from traversals ◆
14.11 Serialize / deserialize ◆
14.12 Binary search trees: search, insert, delete, validate
14.13 BST inorder properties: kth smallest, successor
14.14 N-ary trees
14.15 Practice set

### Chapter 15. Heaps and Top-K ★
15.1 Heap property and array representation
15.2 `heapq` in practice (max-heap by negation, tuples, tie-breakers)
15.3 Kth largest / smallest element
15.4 Top-K frequent: heap vs bucket sort vs sort trade-offs
15.5 Quickselect as the Top-K follow-up ◆
15.6 Merge K sorted lists/arrays
15.7 Two heaps: streaming median
15.8 Scheduling with heaps: task scheduler, meeting rooms
15.9 K closest points
15.10 Practice set

### Chapter 16. Graphs ★
16.1 Representations: adjacency list, matrix, edge list, implicit grids
16.2 DFS: recursive and iterative; connected components
16.3 BFS and shortest path in unweighted graphs
16.4 **Grid BFS/DFS**: flood fill, number of islands
16.5 Multi-source BFS (rotting oranges, distance to nearest) 
16.6 Bipartite check / graph colouring
16.7 Cycle detection: undirected and directed
16.8 Topological sort: Kahn's algorithm and DFS (course schedule)
16.9 Union-Find / DSU with path compression and union by rank (canonical home)
16.10 Dijkstra's algorithm with `heapq`
16.11 0-1 BFS ◆
16.12 Bidirectional BFS ◆
16.13 Clone graph, word ladder ◆
16.14 Bellman-Ford ○
16.15 Floyd-Warshall ○
16.16 Minimum spanning tree: Kruskal and Prim ○
16.17 Practice set

### Chapter 17. Tries and Intervals ★
17.1 Trie node design; insert, search, startsWith
17.2 Word dictionary with wildcards
17.3 Autocomplete / prefix counting
17.4 Word search II (trie + backtracking) ◆
17.5 Interval basics: sorting by start
17.6 Merge intervals, insert interval
17.7 Interval intersection and non-overlapping intervals
17.8 Meeting rooms with heaps (line-sweep scheduling)
17.9 Line sweep technique ◆
17.10 Practice set

---

## PART III — Algorithmic Techniques `S M L`

### Chapter 18. Backtracking ★
18.1 The backtracking template: choose → explore → unchoose
18.2 Subsets (with and without duplicates)
18.3 Permutations (with and without duplicates)
18.4 Combinations and combination sum
18.5 Palindrome partitioning; generate parentheses
18.6 Grid search: word search
18.7 N-Queens (the canonical constraint template)
18.8 Pruning strategies and complexity
18.9 Sudoku solver — Extended exercise ○
18.10 Practice set

### Chapter 19. Dynamic Programming ★
19.1 Recognising DP: overlapping subproblems and optimal substructure
19.2 Top-down (memoisation with `lru_cache`) vs bottom-up
19.3 Defining state, transition, base case — the DP recipe
19.4 1D DP: climbing stairs, house robber, decode ways
19.5 2D grid DP: unique paths, min path sum
19.6 0/1 knapsack and unbounded knapsack (coin change)
19.7 Subsequences: LIS (O(n²) and O(n log n)), LCS
19.8 Edit distance
19.9 String DP: palindromic substrings, word break
19.10 Interval DP ◆
19.11 State machine DP (stock problems) ◆
19.12 DP on trees ◆
19.13 Bitmask DP ◆
19.14 Digit DP ○
19.15 Space optimisation (rolling arrays)
19.16 Practice set

### Chapter 20. Greedy ★
20.1 When greedy works: exchange argument intuition
20.2 Interval scheduling and activity selection
20.3 Jump game I/II
20.4 Gas station, candy distribution
20.5 Partition labels
20.6 Greedy with heaps (reorganise string, task scheduler)
20.7 Greedy vs DP: how to tell
20.8 Huffman coding ○
20.9 Practice set

### Chapter 21. Math, Bits and String Algorithms ◆
21.1 GCD/LCM (`math.gcd`, `math.lcm`)
21.2 Primes: sieve of Eratosthenes, `math.isqrt`
21.3 Modular arithmetic and fast exponentiation (`pow(a, b, m)`)
21.4 Combinatorics (`math.comb`, `math.perm`), Pascal's triangle
21.5 Bit basics: AND, OR, XOR, shifts, masks
21.6 Bit tricks: single number (XOR), count bits, power of two, subsets via bitmask
21.7 String matching: KMP
21.8 Rabin-Karp rolling hash (and deduplication use)
21.9 Z-function ○
21.10 Randomised algorithms: reservoir sampling, shuffle ◆
21.11 Practice set

### Chapter 22. Full Complexity Analysis ◆
22.1 Recap of the Big-O primer
22.2 Recurrence relations and the Master Theorem
22.3 Amortised analysis (dynamic arrays, union-find)
22.4 Complexity of recursion and backtracking trees
22.5 DP complexity: states × transitions
22.6 Space trade-offs and in-place algorithms
22.7 Python-specific costs: hidden O(n) operations
22.8 Profiling and timing (`timeit`, `cProfile`)
22.9 Segment trees and Fenwick trees (overview) ○

---

## PART IV — Intermediate and Advanced Python `S L (M optional)`

### Chapter 23. Iterators, Generators and Comprehensions ★
23.1 List, dict, set comprehensions (canonical home)
23.2 Nested comprehensions and readability limits
23.3 Iterator protocol: `__iter__`, `__next__`
23.4 Generators and `yield`; generator expressions
23.5 `yield from` and generator pipelines
23.6 Lazy evaluation and memory efficiency
23.7 `itertools` deep dive ◆
23.8 Building a streaming data pipeline

### Chapter 24. OOP, Dataclasses and ABCs ★
24.1 Classes, instances, attributes, methods
24.2 `__init__`, `self`, class vs instance attributes
24.3 Inheritance, `super()`, MRO
24.4 Composition over inheritance
24.5 Encapsulation, properties (`@property`)
24.6 Magic/dunder methods: `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__len__`, `__getitem__`
24.7 `@classmethod` and `@staticmethod`
24.8 Dataclasses: `field`, `frozen`, `order`, `slots`
24.9 Abstract base classes and protocols
24.10 Enums
24.11 Design patterns, one runnable example each: Singleton, Factory, Strategy, Observer ◆
24.12 Metaclasses ○

### Chapter 25. Decorators, Closures and functools ★
25.1 Functions as objects; higher-order functions
25.2 Closures and captured variables
25.3 Writing decorators; `functools.wraps`
25.4 Decorators with arguments
25.5 Practical decorators: timing, retry, logging, memoise
25.6 Class decorators ◆
25.7 `functools`: `partial`, `lru_cache`, `cache`, `singledispatch`, `total_ordering`
25.8 Context managers: `with`, `__enter__`/`__exit__`, `contextlib.contextmanager`

### Chapter 26. Exceptions, Stdlib Tour and File Handling ★
26.1 `try/except/else/finally`; exception hierarchy
26.2 Raising, re-raising, custom exceptions, exception chaining
26.3 Exception groups (`except*`) ◆
26.4 File I/O: text vs binary, encodings, `pathlib`
26.5 CSV and JSON handling
26.6 `re` regular expressions for interviews
26.7 `datetime`, `time`, `zoneinfo`
26.8 `logging` basics
26.9 `pickle` (security warning) and `shelve` ○
26.10 Modules, packages, `__name__ == "__main__"`, imports

### Chapter 27. Memory Model, GIL, Free-Threading and Performance ◆
27.1 Everything is an object: identity, type, value
27.2 Reference counting and garbage collection
27.3 Mutability and the memory model (copy semantics recap → Ch. 7)
27.4 `__slots__` and memory savings
27.5 The GIL in the default build: what it limits
27.6 Free-threaded Python (3.14, PEP 779): supported but opt-in, compatibility caveats
27.7 CPU-bound vs I/O-bound: choosing processes, threads or asyncio
27.8 Performance tactics: built-ins, local variables, avoiding hidden copies
27.9 Profiling: `cProfile`, `timeit`, `tracemalloc`
27.10 Interview-ready answer: "Explain the GIL in 2026"

### Chapter 28. Concurrency and asyncio ◆
28.1 Concurrency vs parallelism
28.2 `threading`: threads, locks, race conditions
28.3 Thread-safe queues and producer–consumer
28.4 `multiprocessing` and `concurrent.futures` (`ThreadPoolExecutor`, `ProcessPoolExecutor`)
28.5 asyncio fundamentals: event loop, coroutines, `await`
28.6 Tasks, `gather`, `TaskGroup`, `as_completed`
28.7 Timeouts and cancellation
28.8 Limiting concurrency with `asyncio.Semaphore`
28.9 Blocking calls in async code and `to_thread`
28.10 Async producer–consumer with `asyncio.Queue`
28.11 Common concurrency interview problems (print in order, bounded buffer)

---

## PART V — Practical Engineering Rounds `S M L`

### Chapter 29. Design-Style Problems (Low-Level Design) ★
29.1 Approach for design-style coding rounds: API first, then data structures
29.2 LRU cache: `OrderedDict` and hash map + doubly linked list (canonical home)
29.3 LFU cache ◆
29.4 Insert / delete / getRandom in O(1)
29.5 Rate limiter: fixed window, sliding log, token bucket (canonical home)
29.6 Hit counter
29.7 Time-based key-value store
29.8 In-memory key-value database with transactions ◆
29.9 Task scheduler / job queue
29.10 Autocomplete system (trie-based)
29.11 Probabilistic structures: Bloom filter, count-min sketch, HyperLogLog ◆
29.12 Consistent hashing ◆
29.13 Practice set

### Chapter 30. Log, File and Text Processing; SQL for Engineers ★
30.1 Parsing log files: regex, splitting, streaming large files
30.2 Aggregations: counts, top-K, time-window grouping
30.3 CSV/JSON transformation tasks
30.4 Handling malformed input robustly
30.5 Processing files that don't fit in memory (chunking, generators, external sort)
30.6 SQL basics: SELECT, WHERE, GROUP BY, HAVING, ORDER BY
30.7 Joins: inner, left, self-joins
30.8 Subqueries and CTEs
30.9 Window functions: `ROW_NUMBER`, `RANK`, running totals
30.10 Using `sqlite3` from Python
30.11 Timed practical exercises

### Chapter 31. Testing, Debugging and Code Review Rounds ★
31.1 Writing tests with `pytest`: fixtures, parametrisation
31.2 Designing test cases: happy path, edge, error, property-style
31.3 Mocking and dependency injection (`unittest.mock`)
31.4 Debugging round format: reproduce → isolate → fix → verify
31.5 Using `pdb`, `breakpoint()`, logging and assertions
31.6 Reading stack traces fast
31.7 "Fix the bug" timed exercises
31.8 Code review round: what to look for (correctness, complexity, readability, safety)
31.9 Giving review feedback constructively
31.10 "Review this PR" timed exercises

### Chapter 32. Take-Home and Pair-Programming Workflow ◆
32.1 Take-home: scoping, time-boxing, README, assumptions
32.2 Project structure, typing, linting, tests
32.3 What reviewers grade in take-homes
32.4 Pair programming: collaboration signals, navigating an unfamiliar codebase
32.5 Incremental delivery and refactoring live
32.6 Follow-up discussion: extensions and trade-offs
32.7 Sample take-home with model solution

---

## PART VI — Data and ML Coding Track `M L`

### Chapter 33. NumPy and Vectorisation ★
33.1 Arrays, dtypes, shapes, creation functions
33.2 Indexing, slicing, boolean and fancy indexing
33.3 Broadcasting rules
33.4 Vectorising loops
33.5 Aggregations along axes
33.6 Linear algebra: dot, matmul, norms, inverse, solve
33.7 Reshape, transpose, stack, concatenate
33.8 Random numbers and seeding
33.9 Implementing distance matrices and similarity in NumPy
33.10 Practice set

### Chapter 34. Pandas and SQL for Analysis ★
34.1 Series and DataFrames; reading data
34.2 Selection: `loc`, `iloc`, boolean filters
34.3 Missing data handling
34.4 `groupby`, aggregation, `transform`
34.5 Merge, join, concat (SQL equivalents)
34.6 Pivot tables and reshaping (`melt`, `pivot`)
34.7 Time series basics
34.8 Window/rolling operations
34.9 Analytical SQL interview questions (cohorts, retention, funnels)
34.10 Practice set

### Chapter 35. ML Math, Statistics and Metrics ★
35.1 Linear algebra refresher for ML
35.2 Calculus refresher: gradients, chain rule
35.3 Probability: Bayes' rule problems
35.4 Distributions, sampling, sampling bias
35.5 Bootstrap and confidence intervals
35.6 A/B testing and significance
35.7 Classification metrics: accuracy, precision, recall, F1, ROC-AUC, calibration
35.8 Regression metrics: MSE, MAE, R²
35.9 Ranking/retrieval metrics: Precision@K, Recall@K, MRR, MAP, NDCG
35.10 Numerical stability: log-sum-exp, stable softmax and cross-entropy (lab)
35.11 Data leakage, cross-validation, class imbalance, feature engineering

### Chapter 36. Classical ML from Scratch ★
36.1 Linear regression (closed form and gradient descent)
36.2 Logistic regression and softmax regression
36.3 k-nearest neighbours
36.4 k-means clustering
36.5 Decision tree with information gain / Gini
36.6 Random forest basics ◆
36.7 Naive Bayes
36.8 PCA via SVD
36.9 Optimisers from scratch: SGD, momentum, RMSprop, Adam
36.10 Regularisation (L1/L2), learning-rate schedules, gradient clipping
36.11 Practice set

### Chapter 37. PyTorch Training and Debugging ◆
37.1 Tensors, autograd, devices
37.2 `nn.Module`, layers, parameters
37.3 Core layers by hand: linear, convolution, batch norm, layer norm, dropout, embedding
37.4 Custom `Dataset` and `DataLoader`
37.5 The training loop: forward, loss, backward, step, eval mode
37.6 Mixed precision and gradient accumulation
37.7 Checkpointing and reproducibility (seeds)
37.8 Debugging shape errors and NaNs
37.9 "Debug this broken training loop" exercises
37.10 Practice set

---

## PART VII — GenAI and LLM Engineering Track `L (M optional)`

### Chapter 38. Tokenisation and Embeddings ★
38.1 Why tokenisation matters; characters vs words vs subwords
38.2 Byte-pair encoding: train a BPE tokeniser from scratch (lab)
38.3 Token budgeting and truncation strategies
38.4 Embeddings: what they represent
38.5 Cosine similarity, dot product, normalisation (lab)
38.6 Top-K similarity search with NumPy (lab)
38.7 Embedding layer implementation

### Chapter 39. Attention, Transformer Blocks, Decoding and Sampling ★
39.1 Scaled dot-product attention (lab)
39.2 Multi-head attention (lab)
39.3 Causal masking
39.4 Positional encodings: sinusoidal and rotary (RoPE)
39.5 Full transformer block: attention + MLP + residual + layer norm
39.6 Mini GPT forward pass (lab)
39.7 KV cache mechanics and memory sizing
39.8 Decoding: greedy, temperature, top-k, top-p (nucleus), beam search (labs)
39.9 Repetition penalties and stop conditions

### Chapter 40. Retrieval and RAG ★
40.1 RAG pipeline overview
40.2 Chunking strategies: fixed, recursive, semantic
40.3 Sparse retrieval: BM25 (lab)
40.4 Dense retrieval and hybrid search
40.5 Reciprocal rank fusion (lab)
40.6 Reranking
40.7 Approximate nearest neighbour: HNSW, IVF, product quantisation; FAISS-style trade-offs ◆
40.8 Prompt assembly and context-window management
40.9 RAG evaluation: Recall@K, faithfulness, groundedness
40.10 LLM-as-judge pitfalls
40.11 Building a small evaluation harness (lab)

### Chapter 41. Agents, Tool Calling and Structured Outputs ★
41.1 Function-calling loop (lab, with a deterministic mock LLM)
41.2 ReAct-style loop with step limits
41.3 Tool error handling and retries
41.4 Structured outputs with schema validation
41.5 Conversation memory and state
41.6 Model Context Protocol (MCP) basics ◆
41.7 Building a mini agent end-to-end (lab)

### Chapter 42. Production Patterns for LLM Systems ★
42.1 Async API calls: timeouts, cancellation (→ Ch. 28)
42.2 Concurrency limits with `asyncio.Semaphore`; `gather(return_exceptions=True)`
42.3 Exponential backoff with jitter; idempotency
42.4 Circuit breaker
42.5 Streaming responses and streaming parsers
42.6 Partial-failure handling
42.7 API quota handling (→ rate limiter in Ch. 29)
42.8 Caching: TTL cache and semantic cache (→ LRU in Ch. 29)
42.9 Batching: static vs continuous
42.10 Token and cost accounting; latency budgets
42.11 Safety: prompt-injection basics, PII redaction, output guardrails
42.12 Inference systems: GPU memory estimation (weights + KV cache), quantisation basics, LoRA and parameter counts ◆

### Chapter 43. LLM System-Design Primer ◆
43.1 System-design interview framework for AI systems
43.2 Design a RAG service
43.3 Design an LLM gateway
43.4 Design an evaluation pipeline
43.5 Observability, monitoring and feedback loops
43.6 Bridge to general system-design interviews

---

## PART VIII — Practice and Assessment `S M L`

### Chapter 44. Concept Q&A Bank ★
Conceptual Q&A only (cross-referenced, not repeated from chapters).
44.1 Python language and internals
44.2 Data structures and complexity
44.3 Algorithms and patterns
44.4 Concurrency and performance
44.5 Testing and engineering practice
44.6 ML and statistics
44.7 GenAI and LLM engineering

### Chapter 45. 150-Problem Bank with Pattern Map ★
Each problem: tier tag, pattern tag, target time, examples, constraints, hidden edge cases, approach ladder, complexity, follow-ups, common wrong answers; tested solution + "minimal interview version".

| Category | Beginner | Intermediate | Advanced | Total |
|---|---|---|---|---|
| Arrays and strings | 6 | 6 | 2 | 14 |
| Hash maps and sets | 5 | 4 | 1 | 10 |
| Two pointers | 4 | 3 | 1 | 8 |
| Sliding window | 2 | 4 | 2 | 8 |
| Binary search | 2 | 4 | 2 | 8 |
| Linked lists | 3 | 4 | 1 | 8 |
| Stacks and queues | 3 | 5 | 2 | 10 |
| Trees | 3 | 6 | 3 | 12 |
| Graphs | 1 | 6 | 5 | 12 |
| Heaps | 1 | 4 | 3 | 8 |
| Recursion and backtracking | 1 | 4 | 3 | 8 |
| Dynamic programming | 1 | 7 | 6 | 14 |
| Greedy and intervals | 1 | 4 | 2 | 7 |
| Bit manipulation and math | 2 | 2 | 1 | 5 |
| Design-style problems | 0 | 3 | 3 | 6 |
| Matrix, tensor and AI/ML implementation | 5 | 4 | 3 | 12 |
| **Total** | **40** | **70** | **40** | **150** |

45.1 How to use the bank: timed solving and spaced repetition
45.2–45.17 Problems by category (table above)
45.18 AI engineering lab bank (30 challenges: tokenisation, retrieval, decoding, evaluation, reliability)

**Practice total:** 150 bank problems + 30 AI labs + ~120 in-chapter exercises ≈ 300.

### Chapter 46. AI-Assisted Round Practice ◆
46.1 How AI-allowed rounds differ: larger tasks, existing codebases, grading how you direct and verify AI
46.2 Workflow: decompose → precise prompts with context → tests first → review diffs line by line → run and probe edge cases → explain every line you keep
46.3 Failure modes: plausible-but-wrong code, off-by-one and complexity errors, over-reliance, inability to explain
46.4 Exercises: fix subtly wrong AI-generated solutions
46.5 Exercises: review and optimise a generated solution
46.6 Exercises: explain trade-offs aloud
46.7 Switching back to AI-free mode

### Chapter 47. Mock Interviews with Rubrics ★
47.1 Running a mock: solo, peer, recorded
47.2 Ten mock interviews (SWE ×4, Data/ML ×3, GenAI/LLM ×3)
47.3 Standard coding-round rubric

| Criterion | Weight |
|---|---|
| Clarifying requirements and constraints | 10 |
| Approach and trade-off reasoning | 20 |
| Correctness on tests and edge cases | 25 |
| Code quality and Pythonic style | 15 |
| Complexity analysis | 10 |
| Testing and debugging | 10 |
| Communication | 10 |
| **Total** | **100** |

47.4 AI-assisted round rubric

| Criterion | Weight |
|---|---|
| Problem decomposition and planning | 20 |
| Prompting and context management | 15 |
| Verifying and critiquing AI output | 30 |
| Integration and code quality | 20 |
| Explaining and owning the final code | 15 |
| **Total** | **100** |

47.5 Self-review and turning scores into a study plan

### Chapter 48. Final Preparation Roadmap ★
48.1 The last two weeks: weak-area repair
48.2 Final 48 hours checklist
48.3 Interview-day routine
48.4 Long-form playbook revision (timings per phase)
48.5 After the interview: notes and follow-ups

---

## Appendices
| # | Appendix |
|---|---|
| A | Python syntax and built-ins (one page) |
| B | Collections and stdlib reference |
| C | Complexity cheat sheet |
| D | Algorithm and data-structure templates |
| E | NumPy / Pandas / PyTorch quick reference |
| F | Python gotchas list |
| G | Pattern recognition guide + 50 coding patterns |
| H | Glossary, roadmaps and 100 rapid-fire questions (indexed to chapters) |

### Pattern recognition guide (Appendix G excerpt)
| If the problem says… | Try first | Typical complexity |
|---|---|---|
| Sorted input, find pair or triple | Two pointers | O(n) or O(n²) |
| Longest/shortest contiguous subarray/substring with a condition | Sliding window | O(n) |
| Count/find subarrays with a given sum | Prefix sum + hash map | O(n) |
| Minimise/maximise a value, feasibility is monotonic | Binary search on the answer | O(n log range) |
| Next greater/smaller element, span, histogram | Monotonic stack | O(n) |
| Kth largest, top K, merge K lists, streaming median | Heap / two heaps / quickselect | O(n log k) |
| Shortest path in an unweighted grid or graph | BFS (multi-source if several starts) | O(V+E) |
| Dependencies, ordering, cycle in directed graph | Topological sort | O(V+E) |
| Connected groups, merge sets dynamically | Union-Find | ~O(α(n)) per op |
| All combinations/permutations/subsets, constraint search | Backtracking with pruning | Exponential |
| Overlapping subproblems, count ways, min cost | Dynamic programming | States × transitions |
| Prefix queries, autocomplete, word dictionary | Trie | O(L) per word |

---

## Study Plans

### Standard 8-week plan (10–12 h/week)
| Week | Focus | Chapters | Problems | Checkpoint |
|---|---|---|---|---|
| 1 | Playbook, Big-O, Python essentials, gotchas, arrays/strings/hashing | 1–9 | 15 | Diagnostic retake; gotchas quiz |
| 2 | Two pointers, sliding window, prefix sums, binary search, sorting | 10–11 | 18 | 3 problems in 60 min |
| 3 | Stacks, queues, linked lists, recursion and trees | 12–14 | 18 | Pattern-recognition drill |
| 4 | Heaps, top-K, graphs | 15–17 | 18 | Mock #1 (rubric-scored) |
| 5 | Backtracking, DP, greedy, intervals | 18–21 | 18 | Spaced revisit of weeks 1–3 |
| 6 | Track part 1 — S: Ch. 29–30 · M: Ch. 33–35 · L: Ch. 38–40 | — | 10 + labs | Mini project |
| 7 | Track part 2 — S: Ch. 28, 31–32 · M: Ch. 36–37 · L: Ch. 41–43 | — | 10 + labs | AI-assisted round practice |
| 8 | Two full mocks, weak-area repair, cheat-sheet revision | 44–48 | 12 targeted | 90-min final assessment |

### Alternative plans
| Plan | For | Shape |
|---|---|---|
| 4-week crash (~15 h/wk) | Experienced engineers, interview soon | Skip Part I via diagnostic · W1 patterns & hashing · W2 trees, graphs, heaps · W3 DP, backtracking, role track · W4 mocks |
| 12-week foundations (6–8 h/wk) | Beginners / career changers | 4 weeks Python essentials + basic DSA, then the 8-week plan |
| 6-week role add-on | Strong DSA, moving to ML/LLM | Parts VI and VII + Part V + two mocks |

---

## Capstone Projects
1. **Mini RAG Q&A system** with hybrid retrieval, reranking and an evaluation harness (Ch. 38, 40, 42)
2. **Mini GPT forward pass** with sampling strategies and a KV cache (Ch. 39)

## Companion Repository Plan
- One folder per chapter: solutions, `pytest` tests, README
- CI runs the full suite + linter/formatter on Python 3.10–3.14
- AI/LLM labs run without API keys or GPUs (deterministic mock LLM, tiny/precomputed embeddings)
- Random seeds fixed in all ML code
