# Chapter 30. Log, File and Text Processing; SQL for Engineers

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 6–8 hours · **Prerequisites:** §6.7, §6.8,
§23.4, §26.5, §26.6

Regex syntax (→ §26.6), `csv`/`json` (→ §26.5), `datetime` (→ §26.7) and generators (→ §23.4)
are taught elsewhere; this chapter applies them. Analytical SQL with pandas: §34.9.

**Learning objectives**

- Parse messy text line by line, counting rejects.
- Aggregate with counts, top-K and sliding windows, with a stated tie rule.
- Sort or count data larger than memory (runs + k-way merge, hash partitions).
- Write GROUP BY, join, CTE and window SQL; run it safely via `sqlite3`.

> **Recognise it**
>
> | You hear / see | Reach for |
> |---|---|
> | "top 10 endpoints" | `Counter` + `heapq.nsmallest` with a tie key |
> | "more than N requests in any minute" | sort + two-pointer window, not buckets |
> | "some lines are corrupt" | narrow `except`, reasons, error budget |
> | "100 GB file, 1 GB RAM" | sorted runs + `heapq.merge`, or hash partitions |
> | "top per group", "running total" | window functions in a CTE |
> | "rows with no match" | `LEFT JOIN ... IS NULL` or `NOT EXISTS` |

## 30.1 Parsing log files: regex, splitting, streaming large files

Ladder: (1) `line.split()`: O(L), but fields are found by position, so a missing field shifts the
rest and any token passes as an IP; (2) an anchored regex with named groups validates every
field; (3) compile once, `fullmatch`, and yield from a generator: memory stays O(one line).

```python
import re
from datetime import datetime

LINE_RE = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) \S+ \S+ "
    r"\[(?P<ts>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
    r"(?: (?P<latency>\d+\.\d+))?"
)


def iter_records(lines, stats):
    for line in lines:                       # a file object yields one line at a time
        m = LINE_RE.fullmatch(line.rstrip("\r\n"))
        try:
            ts = datetime.strptime(m["ts"], "%d/%b/%Y:%H:%M:%S %z") if m else None
        except ValueError:                   # regex matched, but "Foo" is no month
            ts = None
        stats["bad" if ts is None else "ok"] += 1
        if ts is not None:
            yield m["ip"], int(ts.timestamp()), m["path"], int(m["status"])


lines = ['203.0.113.5 - - [12/Mar/2025:10:00:35 +0000] "GET /health HTTP/1.1" 500 549 0.044\n',
         '192.0.2.10 - - [12/Mar/2025:10:06:01 +0000] "GET /health HTTP/1.1" 2OO 12 0.010\n',
         '203.0.113.9 - - [31/Foo/2025:10:07:00 +0000] "GET /login HTTP/1.1" 200 15 0.020\n',
         "garbage line from a crashed writer\n"]
stats = {"ok": 0, "bad": 0}
print(list(iter_records(lines, stats)), stats)
```

```text
[('203.0.113.5', 1741773635, '/health', 500)] {'ok': 1, 'bad': 3}
```

The regex catches shape errors (`2OO` uses the letter O); `strptime` catches values (`Foo`).
`%b` uses the LC_TIME locale's month names ("C", i.e. English, unless the program calls
`locale.setlocale`); `%z` makes the datetime aware. Report the reject count. `.gz` files:
`gzip.open(path, "rt")`. Pipelines: §23.8. → repo: `chapters/ch30_log_text_processing_sql/solutions/ex01_parse_access_log.py`

## 30.2 Aggregations: counts, top-K, time-window grouping

**Top-K.** A `Counter` pass, O(n), then `heapq.nsmallest(k, counts.items(), key=lambda pc:
(-pc[1], pc[0]))`, O(u log k) for u keys, versus O(u log u) to sort all (→ §6.8).
`Counter.most_common` breaks ties by first-seen order: on `/b /a /b /a` it returns `/b`, the
explicit key `/a`. Percentile: nearest rank, sorted index `ceil(0.95 * n) - 1` (ex02).

**Worked problem (ex03): burst detection.** *Given (ip, ts) hits in any order, report every IP
with more than `limit` requests within some `w`-second window.*

- *Rung 1:* for each event, count events in [t, t + w): O(n²).
- *Rung 2, tumbling buckets:* `Counter(ts // 60)`: O(n), but it answers a different question. A
  burst that straddles a boundary splits, and each half can stay under the limit.
- *Rung 3, sort + two pointers:* some optimal window starts at an event. Sort, then move `left`
  while the window is w or more wide: O(n log n) sort plus an O(n) scan. Run it per IP
  (`defaultdict(list)` first): still O(n log n). Why move up: exact, almost as fast as rung 2.

```python
from collections import Counter


def max_in_window(times, w):
    """Most events in any half-open window [t, t + w). O(n log n)."""
    ts = sorted(times)
    best = left = 0
    for right, t in enumerate(ts):
        while t - ts[left] >= w:          # ts[left] is w or more seconds older
            left += 1
        best = max(best, right - left + 1)
    return best


burst = list(range(50, 70, 2))                          # 10 events in 20 seconds
print("tumbling buckets:", sorted(Counter(t // 60 * 60 for t in burst).items()))
print("sliding peak:    ", max_in_window(burst, 60))
print("edges:", max_in_window([], 60), max_in_window([0, 60], 60), max_in_window([7, 7, 7], 1))
```

```text
tumbling buckets: [(0, 5), (60, 5)]
sliding peak:     10
edges: 0 1 3
```

Edge cases: empty input; events exactly w apart (half-open, so separate); equal timestamps;
unsorted input (merged server logs); `limit` equal to the peak (not flagged). Wrong-but-tempting:
assuming sorted input; buckets for "any 60 seconds". Follow-ups: live events → a deque per IP, the
sliding-log rate limiter (→ §29.5); millions of IPs → fixed-window counters; SQL → `COUNT(*) OVER
(PARTITION BY ip ORDER BY ts RANGE BETWEEN CURRENT ROW AND 59 FOLLOWING)` (SQLite 3.28+).
Window mechanics: §10.5.
→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex03_burst_detection.py`

## 30.3 CSV/JSON transformation tasks

CSV in, grouped nested JSON out (or the reverse). Three planted bugs:

| Bug | Fix |
|---|---|
| `split(",")` on `1001,"Widget, large",2` gives 4 fields | `csv.DictReader`, `newline=""` |
| `int(float("0.29") * 100)` is 28 | `Decimal` or integer cents (→ §7.8) |
| output order varies | `json.dumps(..., sort_keys=True)`; sort lists |

Empty cells arrive as `""`; map them to `None` deliberately. Flattening JSON to dotted keys is a
DFS, O(total nodes); the CSV header is the sorted key union, `DictWriter(restval="")` fills gaps.
→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex04_csv_json_transform.py`

## 30.4 Handling malformed input robustly

Ladder: (1) no handling: the first bad line kills the job; (2) `except Exception: continue`:
hides your own bugs and reports nothing; (3) catch only data errors (`UnicodeDecodeError`,
`json.JSONDecodeError`), validate fields explicitly, record `(line_no, reason)`, and raise past an
error budget: 60 % bad means "wrong file". Decode bytes per line, so one bad byte costs one line.

Checklist (ex05 tests each): truncated JSON; a list, not an object; missing key; `"80"` for 80;
`true` for an int (`isinstance(True, int)` is True); negatives; invalid UTF-8; blank lines; extra
keys (allowed); empty input. Quarantine bad lines for replay. Exceptions: §26.1.
→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex05_robust_ingest.py`

## 30.5 Processing files that don't fit in memory (chunking, generators, external sort)

**Stream** when small state suffices (sums, a size-k heap); **hash-partition** keys into P
files when per-key state is too big; **external sort** for global order.

**Worked problem (ex06): external sort.** *Sort N integers in a file, holding at most M at once.*

- *Rung 1:* `sorted(...)`: O(N log N) time, O(N) memory: fails.
- *Rung 2:* sort runs of M, then merge pairs as in merge sort (→ §11.6): O(N log N), O(M) memory,
  but 1 + ⌈log₂ k⌉ passes over the disk, k = ⌈N/M⌉.
- *Rung 3:* sort runs of M, then one k-way heap merge: O(N log M + N log k) = O(N log N), two
  passes, memory O(M) for runs and O(k) heads for the merge. Why move up: disk passes dominate.

```python
import heapq
import itertools
import random
import tempfile
from pathlib import Path


def read_chunks(lines, chunk):
    it = (int(s) for s in lines if s.strip())
    while batch := list(itertools.islice(it, chunk)):   # at most `chunk` ints in memory
        yield batch


def numbers(path):
    with open(path) as f:
        for line in f:
            yield int(line)


def external_sort(src, dst, chunk, tmpdir):
    runs = []
    with open(src) as f:
        for i, batch in enumerate(read_chunks(f, chunk)):         # pass 1: sorted runs
            batch.sort()
            runs.append(tmpdir / f"run{i:05d}.txt")
            runs[-1].write_text("".join(f"{n}\n" for n in batch))
    with open(dst, "w") as out:                                   # pass 2: k-way merge
        for n in heapq.merge(*(numbers(r) for r in runs)):        # heap holds k heads
            out.write(f"{n}\n")
    return len(runs)


rng = random.Random(30)
nums = [rng.randint(-1000, 1000) for _ in range(10_007)]
with tempfile.TemporaryDirectory() as d:
    tmp = Path(d)
    src, dst = tmp / "in.txt", tmp / "out.txt"
    src.write_text("".join(f"{n}\n" for n in nums))
    for chunk in (1_000, 2_500):
        runs = external_sort(src, dst, chunk, tmp)
        ok = [int(x) for x in dst.read_text().split()] == sorted(nums)
        print(f"chunk={chunk}: runs={runs}, sorted correctly: {ok}")
```

```text
chunk=1000: runs=11, sorted correctly: True
chunk=2500: runs=5, sorted correctly: True
```

Edge cases: empty file (0 runs), N < M, N a multiple of M, duplicates, negatives.
Wrong-but-tempting: `sorted(heapq.merge(...))` (O(N) memory); merging lines as strings
(`"10" < "9"`). Follow-ups: k above the open-file limit → merge F at a time, ⌈log_F k⌉ passes;
partition with a stable hash (`zlib.crc32`; `str` `hash()` is salted per process).
→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex06_external_sort.py`

## 30.6 SQL basics: SELECT, WHERE, GROUP BY, HAVING, ORDER BY

Evaluation order: **FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT**. So WHERE
cannot use aggregates (HAVING can). Standard SQL allows SELECT aliases in ORDER BY, not WHERE
(SQLite tolerates them in WHERE; don't rely on it). The listing doubles as §30.10's demo:

```python
import sqlite3

rows = [("a", "/login", 401, 12), ("a", "/login", 401, 13), ("b", "/api", 200, 150),
        ("b", "/api", 503, 159), ("c", "/api", 200, 120), ("c", "/health", 200, 3)]
conn = sqlite3.connect(":memory:")
conn.execute("""CREATE TABLE hits (ip TEXT, path TEXT,
                status INTEGER CHECK (status BETWEEN 100 AND 599), latency_ms INTEGER)""")
with conn:                                        # commit on success, rollback on error
    conn.executemany("INSERT INTO hits VALUES (?, ?, ?, ?)", rows)
print(conn.execute("""
    SELECT path, COUNT(*) AS n, ROUND(AVG(latency_ms)) AS avg_ms, SUM(status >= 500) AS errors
    FROM hits
    WHERE status <> 401                 -- row filter, before grouping
    GROUP BY path
    HAVING COUNT(*) >= ?                -- group filter, after grouping
    ORDER BY n DESC, path""", (2,)).fetchall())
try:
    with conn:
        conn.executemany("INSERT INTO hits VALUES (?, ?, ?, ?)",
                         [("d", "/ok", 200, 1), ("d", "/bad", 999, 1)])
except sqlite3.IntegrityError as e:
    print("rolled back:", e, "| rows:", conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0])
evil = "x' OR '1'='1"
print("bound:", conn.execute("SELECT COUNT(*) FROM hits WHERE path = ?", (evil,)).fetchone()[0],
      "| f-string:", conn.execute(f"SELECT COUNT(*) FROM hits WHERE path = '{evil}'").fetchone()[0])
conn.close()
```

```text
[('/api', 3, 143.0, 1)]
rolled back: CHECK constraint failed: status BETWEEN 100 AND 599 | rows: 6
bound: 0 | f-string: 6
```

| Trap (SQLite 3.50.4; ex07 prints each) | Result |
|---|---|
| `7 / 2` | `3`, integer division; write `7 / 2.0` |
| `NULL = NULL` | NULL, never true; use `IS NULL` |
| `COUNT(col)` | skips NULLs, as do `SUM`/`AVG`; `COUNT(*)` does not |
| `ROUND(154.5)` | `155.0`, half away from zero; Python's `round` gives 154 (→ §7.9) |
| `SUM(status >= 500)` | comparisons are 0/1 in SQLite; portable: `SUM(CASE WHEN ...)` |

## 30.7 Joins: inner, left, self-joins

INNER keeps matches; LEFT keeps every left row, NULL-padding the right. A self-join aliases one
table twice (`employees e JOIN employees m ON e.manager_id = m.id`: who out-earns their
manager?). Anti-join: LEFT JOIN + `IS NULL`. One schema for §30.7–§30.8:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
    CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER,
                            manager_id INTEGER, salary INTEGER);
    INSERT INTO departments VALUES (1, 'Eng'), (2, 'Sales'), (3, 'Legal');
    INSERT INTO employees VALUES (1, 'Ada', 1, NULL, 200), (2, 'Ben', 1, 1, 150),
        (3, 'Cy', 1, 1, 210), (4, 'Di', 2, 1, 120), (5, 'Ed', 2, 4, 130),
        (6, 'Flo', NULL, 1, 90);
""")
q = """SELECT d.name, {agg} FROM departments d
       LEFT JOIN employees e ON e.dept_id = d.id {extra}
       GROUP BY d.id ORDER BY d.name"""
for agg, extra in [("COUNT(e.id)", ""), ("COUNT(*)", ""),
                   ("COUNT(e.id)", "WHERE e.salary > 125"), ("COUNT(e.id)", "AND e.salary > 125")]:
    print(f"{agg:<11} {extra or '-':<20}", conn.execute(q.format(agg=agg, extra=extra)).fetchall())
print("NOT IN:", conn.execute("""SELECT name FROM employees
    WHERE id NOT IN (SELECT manager_id FROM employees)""").fetchall(),
      "| NOT EXISTS:", conn.execute("""SELECT e.name FROM employees e WHERE NOT EXISTS
    (SELECT 1 FROM employees r WHERE r.manager_id = e.id) ORDER BY e.name""").fetchall())
chain = conn.execute("""
    WITH RECURSIVE chain(name, manager_id, depth) AS (
        SELECT name, manager_id, 0 FROM employees WHERE name = 'Ed'     -- anchor
        UNION ALL
        SELECT m.name, m.manager_id, c.depth + 1                       -- step
        FROM employees m JOIN chain c ON m.id = c.manager_id
    )
    SELECT name FROM chain ORDER BY depth""").fetchall()
print(" -> ".join(name for (name,) in chain))
```

```text
COUNT(e.id) -                    [('Eng', 3), ('Legal', 0), ('Sales', 2)]
COUNT(*)    -                    [('Eng', 3), ('Legal', 1), ('Sales', 2)]
COUNT(e.id) WHERE e.salary > 125 [('Eng', 3), ('Sales', 1)]
COUNT(e.id) AND e.salary > 125   [('Eng', 3), ('Legal', 0), ('Sales', 1)]
NOT IN: [] | NOT EXISTS: [('Ben',), ('Cy',), ('Ed',), ('Flo',)]
Ed -> Di -> Ada
```

Lines 1–4: `COUNT(*)` counts the padded row (empty Legal shows 1); a
right-table filter in WHERE drops padded rows, making it an INNER JOIN, so put it in ON. SQLite
joins by nested loops, probing an inner-table index when it has (or builds) one. A Python hash
join is O(n + m + output) (ex08). RIGHT/FULL OUTER JOIN need SQLite 3.39+. → repo: `chapters/ch30_log_text_processing_sql/solutions/ex08_sql_joins.py`

## 30.8 Subqueries and CTEs

- **Scalar subquery:** `SELECT (SELECT DISTINCT salary ... ORDER BY salary DESC LIMIT 1 OFFSET ?)`
  returns NULL, not zero rows, when there is no n-th salary.
- **Correlated subquery** (`salary > (SELECT AVG(salary) ... WHERE x.dept_id = e.dept_id)`):
  logically per row, O(n²) without an index. A CTE that groups once and joins back is one pass.
- **`NOT IN` trap:** `manager_id` holds a NULL, so `id NOT IN (...)` is never TRUE (line 5 above);
  `NOT EXISTS` is correct.
- **`WITH RECURSIVE`:** anchor `UNION ALL` step, where the step joins the CTE back to the table.
  Cyclic data recurses forever under UNION ALL; use UNION or a depth limit.

→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex09_subqueries_ctes.py`

## 30.9 Window functions: `ROW_NUMBER`, `RANK`, running totals

`f() OVER (PARTITION BY g ORDER BY o [frame])` computes over related rows **without collapsing
them**. Windows run after WHERE, so filter in an outer query or CTE. SQLite 3.25.0+; check
`sqlite3.sqlite_version` (the library), not `sqlite3.version` (deprecated, removed in 3.14).

**Worked problem (ex10): top-N per group.** *Return each region's two largest sales, ties broken by
id.*

- *Rung 1, Python:* sort by (region, −amount, id), `groupby`, take n: O(r log r); every row
  leaves the database.
- *Rung 2, SQL without windows:* keep a row if fewer than n rows of its region beat it (correlated
  `COUNT(*)`): O(r²) without an index.
- *Rung 3:* `ROW_NUMBER()` in a CTE: one partitioned sort, O(r log r), n a parameter.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, region TEXT, day TEXT, amount INTEGER)")
conn.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)", [
    (1, "east", "03-01", 120), (2, "east", "03-02", 80), (3, "east", "03-02", 40),
    (4, "east", "03-03", 120), (5, "east", "03-04", 60), (6, "west", "03-01", 50),
    (7, "west", "03-02", 90), (8, "west", "03-03", 90), (9, "north", "03-01", 70)])

TOP_N = """
    WITH ranked AS (
        SELECT region, day, amount,
               ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC, id) AS rn
        FROM sales
    )
    SELECT region, day, amount FROM ranked
    WHERE rn <= ?                       -- filter outside: windows run after WHERE
    ORDER BY region, rn"""
print(conn.execute(TOP_N, (2,)).fetchall())

for label, order in [("default RANGE:", "day"),
                     ("ROWS frame:   ", "day, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW")]:
    sql = f"""SELECT SUM(amount) OVER (PARTITION BY region ORDER BY {order})
              FROM sales WHERE region = 'east' ORDER BY day, id"""
    print(label, [r[0] for r in conn.execute(sql)])
```

```text
[('east', '03-01', 120), ('east', '03-03', 120), ('north', '03-01', 70), ('west', '03-02', 90), ('west', '03-03', 90)]
default RANGE: [120, 240, 240, 360, 420]
ROWS frame:    [120, 200, 240, 360, 420]
```

On ties (east has two 120s), ROW_NUMBER gives 1, 2; RANK 1, 1, 3; DENSE_RANK 1, 1, 2 (ex10);
say which "top 2" means. Lines 2–3: with ORDER BY and no frame, the default is `RANGE BETWEEN
UNBOUNDED PRECEDING AND CURRENT ROW`, which includes *peers* (equal `day`), so both 03-02 sales
show 240. Use ROWS and a unique ORDER BY. Edge cases: groups smaller than n, n = 0, ties at the
cut. Follow-ups: top N with ties → `RANK() <= n`; moving
average → `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`; day-over-day → `LAG`.
→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex10_window_functions.py`

## 30.10 Using `sqlite3` from Python

- **Bind parameters** (`?`, `:name`): the f-string query matched all 6 rows, the bound one 0.
  Placeholders cannot name tables or columns; whitelist those.
- `with conn:` commits, or rolls back on an exception (the 999 batch left 6 rows). It does
  **not** close; call `conn.close()` or use `contextlib.closing`.
- `conn.row_factory = sqlite3.Row` gives rows by column name.

→ repo: `chapters/ch30_log_text_processing_sql/solutions/ex07_sqlite_log_queries.py`

## 30.11 Timed practical exercises

Protocol: clarify format, order, boundaries → read five real lines → parse, counting rejects →
aggregate → cross-check two methods on random data → state complexity and the 100× breaking point.

Classic: **sessionisation** (ex11), where a session ends when the user's next event is over 30
minutes later. Python: sort by (user, ts), scan, O(n log n). SQL ("gaps and islands"):
`CASE WHEN ts - LAG(ts) OVER w <= 1800 THEN 0 ELSE 1 END` flags starts (a NULL `LAG` falls to ELSE),
then `SUM(flag) OVER (... ROWS UNBOUNDED PRECEDING)` numbers sessions; GROUP BY user, number.

## Interviewer's view

- **Rewarded:** clarifying format, order and ties; streaming; counting rejects; a cross-check.
- **Penalised:** `split(",")` on CSV; float money; bare `except`; buckets for "any window";
  `NOT IN` on a nullable column; LEFT JOIN filters in WHERE; ORDER BY without a tie-breaker.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Parse an access log | ★ | regex + generator |
| 02 | Status mix, top-K paths, p95 | ★ | `Counter` + heap |
| 03 | Burst detection | ★ | sliding window (worked) |
| 04 | CSV to nested JSON and back | ★ | `csv`, `Decimal`, flatten |
| 05 | Ingest malformed JSON lines | ★ | validation + budget |
| 06 | External sort, partitioned counts | ◆ | runs + merge (worked) |
| 07 | Log into SQLite | ★ | GROUP BY, transactions |
| 08 | Joins and a hash join | ★ | inner/left/anti/self |
| 09 | Subqueries, CTEs, org chart | ◆ | `WITH RECURSIVE` |
| 10 | Top-N per group, running totals | ★ | windows (worked) |
| 11 | Sessionise in Python and SQL | ◆ | gaps and islands |

Index and data files: `chapters/ch30_log_text_processing_sql/README.md`.

## Checkpoint quiz

1. Why can per-minute buckets miss 10 requests in 20 seconds with a limit of 6?
2. 50 GB of integers, 1 GB of RAM: how many runs and passes?
3. `LEFT JOIN e ... WHERE e.salary > 100` drops empty departments. Why? Fix?
4. `WHERE id NOT IN (SELECT parent_id FROM t)` returns nothing. Why?
5. Two same-day sales share one running total. Why?

<details><summary>Answers</summary>

1. A burst across a minute boundary splits (5 + 5); neither bucket exceeds 6.
2. About 50 runs; one 50-way merge; two passes.
3. Padded rows have NULL salary and `NULL > 100` is not TRUE. Move the condition into ON.
4. `parent_id` contains NULL, so `id <> NULL` is NULL for every row. Use NOT EXISTS.
5. The default RANGE frame includes ORDER BY peers. Use a ROWS frame and a unique ORDER BY.
</details>

## Summary card

- Stream lines; compiled regex + `fullmatch`; validate values; count rejects.
- Top-K: `Counter` + `nsmallest` with `(-count, key)`. "Any window": sort + two pointers.
- `csv` with `newline=""`; cents/`Decimal`. Bad input: narrow `except`, reasons, budget.
- Too big for RAM: stream, hash-partition, or external sort (two passes).
- FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY. LEFT JOIN filters in ON; no `NOT IN` on NULLs.
- Windows: filter via a CTE; ROWS frames; SQLite 3.25+. Bind `?`; `with conn:` = transaction.
