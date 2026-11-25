# Chapter 25 — Decorators, Closures and functools

Manuscript: `manuscript/ch25_decorators_closures_functools.md`. Standard library only.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Functions as values: compose, apply_n, dispatch table | ★ Core | higher-order functions, dict dispatch | 25.1 |
| ex02 | Closures: running average and shared cells | ★ Core | closure state, `nonlocal`, `__closure__` | 25.2 |
| ex03 | First decorator: count_calls and `functools.wraps` | ★ Core | wrapper + `wraps`, stacking order | 25.3 |
| ex04 | Decorators with arguments: repeat, validate, optional parens | ★ Core | decorator factory, `inspect.signature` | 25.4 |
| ex05 | Retry with exponential backoff (injectable sleep) | ★ Core | decorator factory + dependency injection | 25.4, 25.5 |
| ex06 | Timing and logging decorators (injectable clock) | ★ Core | cross-cutting concerns, `try/finally` | 25.5 |
| ex07 | Build memoize from scratch (match `lru_cache`) | ★ Core | stateful decorator, cache keys | 25.5, 25.7 |
| ex08 | Class decorators and decorator classes | ◆ Extended | registry, `auto_repr`, `__get__` binding | 25.6 |
| ex09 | functools toolkit: partial, singledispatch, total_ordering | ★ Core | stdlib higher-order tools | 25.7 |
| ex10 | Context managers: Transaction, temp_attr, Suppress | ★ Core | `__enter__`/`__exit__`, `@contextmanager` | 25.8 |

## How to run

```bash
.venv/Scripts/python chapters/ch25_decorators_closures_functools/solutions/ex05_retry_backoff.py
.venv/Scripts/python -m pytest chapters/ch25_decorators_closures_functools           # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch25_decorators_closures_functools  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 25                                   # regenerate outputs/
```

With `TARGET=exercises`, four tests pass from the start because they check the provided buggy
helpers (`test_naive_loses_metadata`, `test_buggy_recomputes_falsy`, `test_no_get_breaks_methods`,
`test_temp_attr_buggy_leaks`); do not count them as progress.

Each solution docstring holds the full statement, approach ladder, hints and follow-ups;
`exercises/` holds the same file with the ladder removed and bodies replaced by
`raise NotImplementedError("TODO")`. The deliberately buggy helpers (`count_calls_naive`,
`memoize_buggy`, `CountCallsNoGet`, `temp_attr_buggy`) and the `Flaky` test double are kept in
the stubs so you can compare against them. Decorated demo functions live inside `main()`, so the
stubs import cleanly. No exercise sleeps or reads a real clock in its printed output: ex05 injects
`sleep`, ex06 injects `clock`. Python 3.10+.
