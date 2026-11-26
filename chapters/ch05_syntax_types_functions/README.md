# Chapter 05 — Syntax, Types, Control Flow and Functions

Manuscript: `manuscript/ch05_syntax_types_functions.md`. Standard library only.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | FizzBuzz with pluggable rules | ★ Core | loops, conditionals, rules as data | 5.4, 5.5 |
| ex02 | Reverse a signed integer with a 32-bit clamp | ★ Core | `divmod`, unbounded `int`, floor division | 5.2 |
| ex03 | Palindrome after normalisation | ★ Core | slicing, `isalnum`, two indices | 5.3 |
| ex04 | Aligned receipt with f-strings | ★ Core | format mini-language | 5.3 |
| ex05 | Tiny stack machine with `match` | ◆ Extended | structural pattern matching (3.10+) | 5.4 |
| ex06 | Primality and first prime with `for … else` | ★ Core | early exit, `math.isqrt` | 5.5 |
| ex07 | Flexible summary function | ★ Core | `*args`, keyword-only, `**kwargs` | 5.6 |
| ex08 | Fix the mutable default argument | ★ Core | `None` sentinel | 5.6 |
| ex09 | Compose functions into a pipeline | ★ Core | first-class functions, lambdas | 5.7 |
| ex10 | Counters and running averages with closures | ★ Core | LEGB, `nonlocal` | 5.8 |
| ex11 | Run-length encoding and decoding | ★ Core | string scanning, `"".join` | 5.3, 5.5 |
| ex12 | Check arguments against type hints | ◆ Extended | `inspect.signature`, `get_type_hints` | 5.9 |

## How to run

```bash
.venv/Scripts/python chapters/ch05_syntax_types_functions/solutions/ex05_stack_machine_match.py
.venv/Scripts/python -m pytest chapters/ch05_syntax_types_functions           # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch05_syntax_types_functions  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 05                                # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder (with complexity per rung) and
follow-ups. `exercises/` holds the same file with the ladder replaced by **Hints**, follow-up
answers removed, and function bodies replaced by `raise NotImplementedError("TODO")`; `main()` is
kept so you can run your stub. Given code (`buggy_register` in ex08, the sample functions in ex12)
is left intact.

Python 3.10+: ex05 uses `match` (3.10). ex10's `UnboundLocalError` message in `outputs/` is the
3.11+ wording (3.10 prints "local variable 'count' referenced before assignment").
