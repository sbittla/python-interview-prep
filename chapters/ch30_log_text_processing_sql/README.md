# Chapter 30 — Log, File and Text Processing; SQL for Engineers

Manuscript: `manuscript/ch30_log_text_processing_sql.md`. Standard library only (`re`, `csv`,
`json`, `heapq`, `sqlite3` in memory). The venv's SQLite is 3.50.4; window functions need 3.25+.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Parse an access log, one line at a time | ★ Core | compiled regex, named groups, generator | 30.1 |
| ex02 | Status mix, top-K paths, p95 latency | ★ Core | `Counter` + `heapq.nsmallest`, nearest-rank percentile | 30.2 |
| ex03 | Per-minute counts and burst detection | ★ Core | tumbling buckets vs sliding window (two pointers) | 30.2 |
| ex04 | CSV to nested JSON and back | ★ Core | `csv.DictReader`, `Decimal` cents, recursive flatten | 30.3 |
| ex05 | Ingest malformed JSON lines | ★ Core | narrow `except`, explicit validation, error budget | 30.4 |
| ex06 | External sort and hash-partitioned counts | ◆ Extended | sorted runs + `heapq.merge`, partition to disk | 30.5 |
| ex07 | Load a log into SQLite and query it | ★ Core | `GROUP BY`/`HAVING`, parameters, transactions | 30.6, 30.10 |
| ex08 | Joins: inner, left, anti, self; hash join | ★ Core | `LEFT JOIN ... IS NULL`, self-join | 30.7 |
| ex09 | Subqueries, CTEs, recursive org chart | ◆ Extended | correlated subquery, `WITH RECURSIVE`, `NOT IN` + NULL | 30.8 |
| ex10 | Top-N per group, ranks, running totals | ★ Core | `ROW_NUMBER`, `RANK`, `SUM() OVER`, `LAG` | 30.9 |
| ex11 | Timed practical: sessionise events in Python and SQL | ◆ Extended | gaps and islands | 30.11 |

Data files (`data/`): `access.log` (44 lines, 5 malformed), `orders.csv` (quoted fields),
`payments.jsonl` (17 lines: 1 blank, 7 bad incl. one invalid UTF-8 byte). Timestamps are fixed (March 2025).

## How to run

```bash
.venv/Scripts/python chapters/ch30_log_text_processing_sql/solutions/ex03_burst_detection.py
.venv/Scripts/python -m pytest chapters/ch30_log_text_processing_sql                  # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch30_log_text_processing_sql # your stubs
.venv/Scripts/python tools/run_all.py --chapter 30                                    # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder, hints, edge cases and
follow-ups; `exercises/` holds the same file with the ladder removed and bodies replaced by
`raise NotImplementedError("TODO")`. Python 3.10+.
