# Chapter 24 — OOP, Dataclasses and ABCs

Manuscript: `manuscript/ch24_oop_dataclasses_abcs.md`. Standard library only.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Bank account: state, class attributes, properties | ★ Core | class vs instance attributes, read-only `@property` | 24.1, 24.2, 24.5 |
| ex02 | Money: a hashable, ordered value type | ★ Core | `__eq__`/`__hash__` contract, `NotImplemented`, arithmetic dunders | 24.6 |
| ex03 | Span: rebuild `range()` | ★ Core | sequence protocol, slices via `slice.indices` | 24.6 |
| ex04 | Inheritance, `super()` and the C3 MRO | ★ Core | cooperative `super()`, C3 linearisation | 24.3 |
| ex05 | Audited list and strict stack | ★ Core | composition and delegation vs subclassing `list` | 24.4 |
| ex06 | Alternative constructors | ★ Core | `@classmethod` factories with `cls(...)`, `@staticmethod` helpers | 24.7 |
| ex07 | Inventory with dataclasses | ★ Core | `field`, `frozen`, `order`, `slots`, `__post_init__`, `replace` | 24.8 |
| ex08 | Pluggable storage | ★ Core | ABC + template methods, `runtime_checkable` Protocol | 24.9 |
| ex09 | Order workflow with enums | ★ Core | `Enum` state machine, `IntEnum`, `Flag` | 24.10 |
| ex10 | Singleton, Factory, Strategy, Observer | ◆ Extended | design patterns with Python idioms | 24.11 |
| ex11 | Plugin registry | ○ Reference | metaclass vs `__init_subclass__`, `type(...)` | 24.12 |

## How to run

```bash
.venv/Scripts/python chapters/ch24_oop_dataclasses_abcs/solutions/ex02_money_value_type.py
.venv/Scripts/python -m pytest chapters/ch24_oop_dataclasses_abcs           # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch24_oop_dataclasses_abcs  # your stubs
.venv/Scripts/python tools/run_all.py --chapter 24                          # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder, hints and follow-ups;
`exercises/` holds the same file with the ladder removed and bodies replaced by
`raise NotImplementedError("TODO")`. Methods marked `# given` are provided scaffolding.
Tests named `test_documentation_*` (ex05, ex07) check a standard-library or language fact
quoted in the hints, not your code, so they pass on the stubs too.
Python 3.10+ (ex07 uses `@dataclass(slots=True)`, added in 3.10).
