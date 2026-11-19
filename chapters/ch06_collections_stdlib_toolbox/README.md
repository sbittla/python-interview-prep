# Chapter 06 — Built-in Collections, Idioms and the Stdlib Toolbox

Manuscript: `manuscript/ch06_collections_stdlib_toolbox.md`. Standard library only.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Sticker sheets: multiset algebra | ★ Core | `Counter` `<=`, `-`, `&`, `\|` | 6.7 |
| ex02 | Inverted index | ★ Core | `defaultdict(set)` + set algebra | 6.3, 6.7 |
| ex03 | Recent-items windows | ★ Core | `deque` window, `OrderedDict` recency | 6.7 |
| ex04 | Merge sorted feeds, running k-th largest | ★ Core | `heapq` k-way merge, size-k heap | 6.8 |
| ex05 | Grade bands and a sorted leaderboard | ★ Core | `bisect_left/right`, `insort` | 6.9 |
| ex06 | Uptime and budget reports | ◆ Extended | `groupby`, `accumulate`, `combinations`, `product` | 6.10 |
| ex07 | Largest concatenated number | ★ Core | `functools.cmp_to_key`, `reduce` | 6.11, 6.12 |
| ex08 | Multi-key stable sorting | ★ Core | tuple keys, stable multi-pass sort, `namedtuple` | 6.2, 6.12 |
| ex09 | Build a tiny dict (open addressing) | ◆ Extended | hash table internals | 6.5 |
| ex10 | Choosing the right built-in | ◆ Extended | complexity-driven choice, boolean benchmark | 6.14 |
| ex11 | Character toolbox | ★ Core | `ord`/`chr`, `Counter`, `join`, `translate` | 6.6 |

## How to run

```bash
.venv/Scripts/python chapters/ch06_collections_stdlib_toolbox/solutions/ex09_open_addressing_map.py
.venv/Scripts/python -m pytest chapters/ch06_collections_stdlib_toolbox           # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch06_collections_stdlib_toolbox  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 06                                # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder, hints and follow-ups;
`exercises/` holds the same file with the ladder removed and bodies replaced by
`raise NotImplementedError("TODO")`. Python 3.10+ (ex01 uses `Counter` comparisons, added in 3.10).
