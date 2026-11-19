# Chapter 8 — Big-O Primer (code)

Manuscript: `manuscript/ch08_big_o_primer.md`. Full treatment of recurrences, amortisation and
profiling is in Chapter 22.

Every exercise measures cost by **counting operations**, never by printing timings, so outputs are
deterministic. `ex03` imports `fit_growth` from `ex01`: solve ex01 first.

| # | File | Title | Tier | Pattern |
|---|---|---|---|---|
| 01 | `ex01_op_counter.py` | Operation counter and growth fitter | ★ Core | count steps at several n, fit the class |
| 02 | `ex02_constraint_advisor.py` | Constraint-to-complexity advisor | ★ Core | input size → acceptable complexity |
| 03 | `ex03_classify_snippets.py` | Classify ten snippets, then prove it | ★ Core | loop/recursion shape → growth class |
| 04 | `ex04_hidden_costs.py` | Hidden costs: list vs set, pop(0) vs deque | ◆ Extended | one innocent line can be O(n) |
| 05 | `ex05_call_stack_space.py` | Space on the call stack | ★ Core | recursion depth = stack space |

## How to run

```bash
.venv/Scripts/python chapters/ch08_big_o_primer/solutions/ex01_op_counter.py   # one solution
.venv/Scripts/python tools/run_all.py --chapter 08                              # regenerate outputs/
.venv/Scripts/python -m pytest chapters/ch08_big_o_primer                       # test solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch08_big_o_primer      # test your stubs
```
