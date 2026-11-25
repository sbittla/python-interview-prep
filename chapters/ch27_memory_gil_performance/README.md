# Chapter 27 — Memory Model, GIL, Free-Threading and Performance

Manuscript: `manuscript/ch27_memory_gil_performance.md`. Standard library only.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Identity, type, value | ★ Core | `is` vs `==`, small-int cache, interning | 27.1 |
| ex02 | When is an object freed? Refcounts vs the cycle GC | ★ Core | `weakref.finalize` lifetime log | 27.2 |
| ex03 | Find hidden aliasing in a nested structure | ◆ Extended | identity-aware DFS | 27.3 |
| ex04 | `__slots__`: measure the saving, know the cost | ★ Core | comparative tracemalloc peak | 27.4 |
| ex05 | See the GIL: CPU-bound vs I/O-bound threads | ★ Core | boolean benchmark tied to the build | 27.5, 27.6 |
| ex06 | Processes, threads or asyncio? | ★ Core | workload classification + overlap demo | 27.7 |
| ex07 | Hidden copies: prove them with tracemalloc | ★ Core | generator, memoryview, index loop; list over-allocation | 27.8, 27.9 |
| ex08 | Let C do the loop: built-ins vs hand-written loops | ◆ Extended | rewrite + equivalence + boolean race | 27.8 |
| ex09 | Profile without timings: call counts and allocation sites | ◆ Extended | cProfile `ncalls`, tracemalloc snapshot | 27.9 |
| ex10 | The GIL is not thread safety: lost updates | ★ Core | deterministic interleaving model + `Lock` | 27.5, 27.10 |

## How to run

```bash
.venv/Scripts/python chapters/ch27_memory_gil_performance/solutions/ex02_refcount_gc.py
.venv/Scripts/python -m pytest chapters/ch27_memory_gil_performance           # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch27_memory_gil_performance  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 27                            # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder, hints and follow-ups;
`exercises/` holds the same file with the ladder removed and bodies replaced by
`raise NotImplementedError("TODO")`. Python 3.10+ (ex04 uses `dataclass(slots=True)`, new in 3.10;
ex05 uses `sys._is_gil_enabled()` when present, 3.13+).

Determinism: performance demos print only booleans (`slots smaller: True`), never timings, byte
counts, `id()` values or refcounts. Small-int caching and interning results (ex01) are CPython
implementation details, verified on CPython 3.12 and 3.13; their tests skip on other interpreters.
Every timing threshold sits far from the boundary (≥ 2× for sleeps, better big-O for races), and
no test asserts on an unlocked multi-threaded run.
