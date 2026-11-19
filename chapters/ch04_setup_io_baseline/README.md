# Chapter 4 — Setup, I/O and Python Version Baseline

Manuscript: `manuscript/ch04_setup_io_baseline.md`

| ID | Title | Tier | Pattern | stdin file |
|---|---|---|---|---|
| ex01 | Bulk token reader for multiple test cases | ★ Core | `sys.stdin.buffer.read().split()` + `next(it)` | `inputs/ex01_bulk_token_reader.txt` |
| ex02 | Matrix and character-grid reader | ★ Core | injected `readline`, `strip()` vs `[:-1]`, `zip(*m)` | `inputs/ex02_matrix_reader.txt` |
| ex03 | Sentinel, EOF and blank-line framings | ◆ Extended | input framing, ragged lines, final flush | `inputs/ex03_case_framings.txt` |
| ex04 | Output formatting and fast writing | ★ Core | `"\n".join`, one `write`, fixed decimals, no `-0.00` | — |
| ex05 | Version baseline and feature checker | ◆ Extended | `sys.version_info` tuples, feature probes, fallback | — |

## How to run

```bash
# from the repository root
.venv/Scripts/python chapters/ch04_setup_io_baseline/solutions/ex01_bulk_token_reader.py \
    < chapters/ch04_setup_io_baseline/inputs/ex01_bulk_token_reader.txt
.venv/Scripts/python tools/run_all.py --chapter 04             # regenerate outputs/
.venv/Scripts/python -m pytest chapters/ch04_setup_io_baseline   # test the solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch04_setup_io_baseline   # test your stubs
```

Tests never touch real stdin: every parser takes bytes, a `readline` function or an
iterable of lines, so tests pass strings or `io.StringIO`. Lines can still end in `\r\n`
when a judge on Linux reads CRLF test files, or when you read raw `sys.stdin.buffer` bytes
(text-mode `sys.stdin` on Windows translates them to `\n`); every reader here handles both.
