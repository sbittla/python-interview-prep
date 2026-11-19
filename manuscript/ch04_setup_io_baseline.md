# Chapter 4. Setup, I/O and Python Version Baseline

**Tier:** ★ Core · **Tracks:** S M L · **Study time:** 2–3 hours · **Prerequisites:** none

**Learning objectives**

- Set up a venv, editor and `pytest` you can trust.
- Write 3.10+ code and check a judge's Python version.
- Read stdin fast and robustly, including stray `\r\n` line endings.
- Parse matrices, grids and the four multi-test-case framings.
- Print exactly the required format with one write.

> **Recognise it.** "The first line contains T…", "read until end of file", "input ends with
> 0 0", "N ≤ 2·10⁵" on an online judge → bulk read + token iterator, build output, write once.
> A shared editor with no stdin → skip parsing; write a function and call it.

## 4.1 Environment setup: interpreter, venv, editor, `pytest`

Use one interpreter per project and isolate packages in a virtual environment:

| Step | Command (Windows Git Bash shown; macOS/Linux use `bin/` instead of `Scripts/`) |
|---|---|
| Create | `python -m venv .venv` |
| Use | `.venv/Scripts/python …` (or activate it: `source .venv/Scripts/activate`) |
| Install | `.venv/Scripts/python -m pip install -r requirements.txt` |
| Test | `.venv/Scripts/python -m pytest path/to/tests` |

Running `-m pip` and `-m pytest` through the venv's interpreter keeps installs and tests in one
environment. Point your editor at `.venv` too. Also practise without autocomplete: many interview
editors have none.

## 4.2 Python version baseline (3.10+) and checking the judge's version

This book writes portable **3.10+** code: `match`, `X | Y` unions and `zip(strict=True)` are
allowed; anything newer is flagged. Judges can lag behind, so check first: submit
`import sys; print(sys.version)` on a scratch problem or read the judge's language page.
Compare tuples, never strings:

```python
import sys

print(sys.version_info >= (3, 10))      # tuple comparison: correct
print("3.9" > "3.10", (3, 9) > (3, 10))  # string comparison: wrong
```

```text
True
True False
```

A runtime `if sys.version_info >= (3, 10):` cannot protect *new syntax*: the parser rejects the
whole file on an old interpreter before any line runs. Probe syntax with `compile()` on a string
and probe library names with `getattr(module, "name", None)`, falling back when missing.
Exercise 05 builds this table and checks it against live probes (output abridged):

```text
feature                               3.9   3.10  3.11  3.12  3.13  3.14
match statement (PEP 634)             -     yes   yes   yes   yes   yes
X | Y unions at runtime (PEP 604)     -     yes   yes   yes   yes   yes
zip(strict=True) (PEP 618)            -     yes   yes   yes   yes   yes
ExceptionGroup / except* (PEP 654)    -     -     yes   yes   yes   yes
tomllib module (PEP 680)              -     -     yes   yes   yes   yes
type-parameter syntax (PEP 695)       -     -     -     yes   yes   yes
itertools.batched                     -     -     -     yes   yes   yes
template strings t'' (PEP 750)        -     -     -     -     -     yes
...
this interpreter meets the 3.10 baseline: True
runtime probes agree with the table: True
```

## 4.3 stdin/stdout handling: `input()`, `sys.stdin.readline`, fast bulk reads

Three readers, from slowest to fastest:

| Reader | Returns | Notes |
|---|---|---|
| `input()` | line without `\n` | Simple; per-call overhead; raises `EOFError` at end |
| `sys.stdin.readline()` | line *with* `\n` (`""` at EOF) | Faster; strip or `split()` it |
| `sys.stdin.buffer.read().split()` | list of `bytes` tokens | One read; ignores line layout |

On 10⁶ integers the bulk reader is several times faster than an `input()` loop. Use `input()`
for small input; switch when N reaches about 10⁵.

**Worked problem (ex01).** T test cases; each is n followed by n integers that may wrap across
lines. Print `Case #k: <sum> <max>` (`-` when n = 0).

- *Rung 1 — `input()` per line.* O(total input), but the largest per-call overhead; correct only
  if every case is on one line.
- *Rung 2 — `sys.stdin.readline`.* Also O(total input), with less overhead per call, but still
  breaks when a case wraps. **Why move up:**
  the problem promises nothing about line breaks, and the readline version cannot see that.
- *Rung 3 — bulk tokens.* `split()` with no argument treats spaces, tabs, `\n` and `\r\n` alike,
  so layout stops mattering. O(total) time and memory.

```python
def tokens(data: bytes) -> Iterator[bytes]:
    return iter(data.split())

def _case_line(k: int, nums: list[int]) -> str:
    return f"Case #{k}: {sum(nums)} {max(nums) if nums else '-'}"

def solve(data: bytes) -> str:
    it = tokens(data)
    t = int(next(it, b"0"))                       # empty input -> zero cases
    out = []
    for k in range(1, t + 1):
        n = int(next(it))
        nums = [int(next(it)) for _ in range(n)]  # int() accepts bytes
        out.append(_case_line(k, nums))
    return "\n".join(out)

def main() -> None:
    data = sys.stdin.buffer.read()
    sys.stdout.write(solve(data) + "\n")
    ...  # the repo demo also runs the line-based reader on the same input
```

```text
Case #1: 6 3
Case #2: -5 -5
Case #3: 0 -
Case #4: 25 10
line-based reader agrees: True
wrapped case, bulk reader: Case #1: 10 4
wrapped case, line reader: ValueError: case 1: expected 4 numbers on one line, got 1
```

→ repo: `chapters/ch04_setup_io_baseline/solutions/ex01_bulk_token_reader.py`

**Pitfalls.** Text-mode `sys.stdin` turns `\r\n` into `\n` on Windows, but CRLF test files on a
Linux judge, and raw `sys.stdin.buffer` bytes, keep the `\r`. Then `line[:-1]` leaves a `\r`, and
on a final line without a newline it deletes a real character. `line.split(" ")` produces
empty tokens on double spaces. Bytes tokens are not strings: `b"YES" == "YES"` is `False`, so
`decode()` tokens you compare with text.

## 4.4 Parsing common input formats: lines, matrices, multiple test cases

Make every parser take its input source as a parameter (bytes, a `readline` function, or an
iterable of lines): production passes `sys.stdin`, tests pass `io.StringIO(text)`. Exercise 02
reads a matrix and then a grid from one stream:

```python
def read_grid(readline: Readline) -> list[str]:
    h, w = map(int, readline().split())
    grid = []
    for i in range(h):
        row = readline().strip()          # removes "\n", "\r\n", or nothing
        if len(row) != w:
            raise ValueError(f"grid row {i}: expected width {w}, got {len(row)}")
        grid.append(row)
    return grid
```

```text
strip() reader on CRLF text: ['.#.', '##.']
[:-1] reader on CRLF text:   ['.#.\r', '##']
```

The four framings for "many test cases":

| Framing | Signal in the statement | Loop |
|---|---|---|
| Count first | "first line contains T" | `for _ in range(T)` (ex01) |
| Sentinel | "input ends with 0 0" | `break` on the sentinel; also stop at EOF |
| Until EOF | "read until end of file" | `for line in sys.stdin:` (skip blank lines) |
| Blank-line blocks | "groups separated by an empty line" | buffer + flush (below) |

```python
def read_blocks(lines: Iterable[str]) -> list[list[list[int]]]:
    blocks: list[list[list[int]]] = []
    current: list[list[int]] = []
    for line in lines:
        if line.strip():
            current.append(list(map(int, line.split())))
        elif current:                      # blank line closes a non-empty block
            blocks.append(current)
            current = []
    if current:                            # the final flush everyone forgets
        blocks.append(current)
    return blocks
```

The tempting `text.split("\n\n")` never sees the boundary in `\r\n` input:

```text
blocks (CRLF): [[[1, 2], [3]], [[4]]]
naive split on CRLF: [[[1, 2], [3], [], [4]]]
```

Matrices: `[list(map(int, readline().split())) for _ in range(r)]`; columns: `zip(*matrix)`.
Never pre-allocate with `[[0] * c] * r` (→ §7.3).

## 4.5 Output formatting and fast printing

Judges compare output text, usually ignoring trailing whitespace only. Know what each form prints:

```python
nums = [3, 1, 2]
print(nums)                  # list repr: brackets and commas
print(*nums)                 # unpacked: 3 1 2
print(" ".join(map(str, nums)))
print(f"{2 / 3:.3f}", f"{-0.0001:.2f}", 0.1 + 0.2)
```

```text
[3, 1, 2]
3 1 2
3 1 2
0.667 -0.00 0.30000000000000004
```

Two traps: raw floats print every digit, and fixed-point formatting can print `-0.00` (ex04
normalises it). For speed, build all lines and write once; `print()` per line on 10⁵+ lines can
cost more than the algorithm.

```python
def write_lines(lines: Iterable[str], out: TextIO) -> None:
    text = "\n".join(lines)
    if text:                           # no answers -> write nothing, not "\n"
        out.write(text + "\n")
```

```text
join output equals print-loop output: True
no answers writes: ''
```

Exception: **interactive** problems need `print(..., flush=True)` after each answer; stdout to a
pipe is buffered, so otherwise your program and the judge wait on each other until timeout.

## 4.6 Using the companion repository and running tests

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # see its note on CPU-only torch
.venv/Scripts/python tools/run_all.py --chapter 04           # run solutions, write outputs/
.venv/Scripts/python -m pytest chapters/ch04_setup_io_baseline
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch04_setup_io_baseline
```

Tests load `solutions/` by default; `TARGET=exercises` runs them against your stubs, and
`run_all.py` feeds `inputs/` files to stdin (layout: the chapter `README.md`).

## 4.7 What's new in 3.12–3.14 (not required for interviews) ○

| Version | Feature | Status |
|---|---|---|
| 3.12 | Type-parameter syntax `def first[T](xs: list[T]) -> T`, `type Alias = …` (PEP 695) | Standard |
| 3.12 | f-strings may reuse the outer quote, contain backslashes and span lines (PEP 701) | Standard |
| 3.13 | New interactive REPL: multi-line editing, colour, paste mode | Standard |
| 3.13 | Free-threaded build without the GIL, `python3.13t` (PEP 703) | Experimental, separate build |
| 3.13 | JIT compiler (PEP 744) | Experimental, off by default |
| 3.14 | Free-threaded build officially supported (PEP 779) | Supported, still optional |
| 3.14 | Template strings `t"…"` → `Template` objects (PEP 750) | Standard |
| 3.14 | Annotations evaluated lazily, on access (PEP 649/749) | Standard |

## Interviewer's view

- On an online judge the output checker is the grader: a correct algorithm that prints a list
  repr or drops the final block still fails. Read the format section twice.
- Separating parsing from logic (`solve(data)` plus a thin `main`) shows testability: you can
  call `solve` on hand-made cases.
- "N is 2·10⁵, so I'll read stdin in bulk" signals experience; so does asking the platform's
  Python version before using a 3.11+ feature.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Bulk token reader for multiple test cases | ★ | `buffer.read().split()` + `next(it)` |
| ex02 | Matrix and character-grid reader | ★ | injected `readline`, `strip()` |
| ex03 | Sentinel, EOF and blank-line framings | ◆ | input framing, final flush |
| ex04 | Output formatting and fast writing | ★ | `"\n".join`, one write, no `-0.00` |
| ex05 | Version baseline and feature checker | ◆ | version tuples, feature probes, fallback |

Code, inputs and tests: `chapters/ch04_setup_io_baseline/README.md`.

## Checkpoint quiz

1. Why can't `if sys.version_info >= (3, 10):` guard a `match` statement in the same file?
2. Grid rows read with `sys.stdin.readline()[:-1]` have length W+1 on a Linux judge, and the last row
   has W−1. Explain both.
3. What does `sys.stdin.buffer.read().split()` return, and how do you turn a token into an `int`?
4. Your blank-line-block parser loses the last block. What line is missing?
5. When is batching all output into one write the *wrong* choice?

<details>
<summary>Answers</summary>

1. Syntax is checked when the file is compiled, before any code runs; a 3.9 parser rejects the
   whole file. Put new syntax in a separate module or probe it with `compile()`.
2. The judge's test files have CRLF line endings, and Linux text-mode stdin keeps the `\r`, so
   slicing leaves it (W+1); a last line without a
   newline loses a real character (W−1). Use `strip()` or `split()`.
3. A list of `bytes` tokens split on any whitespace; `int(tok)` accepts bytes directly.
4. The flush after the loop: `if current: blocks.append(current)`.
5. Interactive problems, where the judge replies to each answer: flush after every line.

</details>

## Summary card

- One venv per project; run `-m pip` / `-m pytest` through its interpreter.
- Baseline 3.10+; compare `sys.version_info` with tuples; probe new syntax with `compile()`.
- Small input: `input()`. ~10⁵+: `sys.stdin.readline`, or `sys.stdin.buffer.read().split()` with
  `it = iter(...)` and `int(next(it))`.
- `split()` and `strip()` absorb `\r\n`; `split(" ")` and `[:-1]` do not.
- Framings: count, sentinel (also stop at EOF), until EOF, blank-line blocks (flush at the end).
- Parsers take bytes / `readline` / lines as parameters; tests pass `io.StringIO`.
- Output: `" ".join(map(str, row))`, `"\n".join(lines)`, one write; `f"{x:.6f}"`, no `-0.000000`.
- Interactive judges: `flush=True` after each answer.
