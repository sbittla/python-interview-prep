# Chapter 24. OOP, Dataclasses and ABCs

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 5–7 hours · **Prerequisites:** Chapters 5–7

Interviews ask you to *build* classes: a value type for a set, a slicing container, a plugin
API. Shared class attributes (→ §7.4) and `__eq__` without `__hash__` (→ §7.7) live in Chapter 7.

**Learning objectives**

- Predict attribute lookup and what `super()` calls, using the MRO.
- Write a value class whose `==`, `hash`, ordering and arithmetic follow Python's protocols.
- Choose among a class, `@dataclass`, `Enum`, ABC and `Protocol`.

> **Recognise it**
>
> | You hear / see | Reach for |
> |---|---|
> | "use as a dict key", "dedupe these objects", "sort them" | `__eq__` + `__hash__` + `__lt__`, or a frozen, ordered dataclass |
> | "record with fields", "config object" | `@dataclass` |
> | "pluggable backend", "every X must implement Y" | ABC or `Protocol` |
> | "fixed set of states", "permissions" | `Enum`, `Flag` |

## 24.1 Classes, instances, attributes, methods

Calling `Dog("Rex")` runs `__new__` (allocate) and then `__init__` (initialise). A method is a
function stored on the class, which is why methods take `self`.

```python
class Dog:
    species = "canis"                    # class attribute: one object, shared
    def __init__(self, name):
        self.name = name                 # instance attribute: one per object
    def speak(self):
        return f"{self.name} says woof"

a, b = Dog("Rex"), Dog("Ivy")
b.species = "lupus"                      # creates an instance attribute on b only
print(a.speak(), "|", Dog.speak(a))      # the same call
print(a.species, b.species, Dog.species, sorted(vars(b)))
```

```text
Rex says woof | Rex says woof
canis lupus canis ['name', 'species']
```

## 24.2 `__init__`, `self`, class vs instance attributes

Reading `obj.x` checks the instance `__dict__`, then the class and its bases in MRO order;
assignment writes to the instance. (A data descriptor on the class, e.g. a `@property`, takes
precedence for both reads and writes.) So `b.species` *shadows* the class value, and a shared
counter must be bumped through the class (`Account._next += 1`): `self._next += 1` creates a
per-instance copy. Create mutable state in `__init__` (→ §7.4) and validate there (ex01).

## 24.3 Inheritance, `super()`, MRO

A subclass inherits whatever it does not override. Because `self.method()` is looked up at
runtime, a base-class method automatically calls the subclass's override. With multiple bases,
Python orders classes by the **MRO** (`Cls.__mro__`). `super()` does not mean "my parent". It
means "the next class after this one in `type(self).__mro__`". In a diamond, that makes each
`__init__` run exactly once:

```python
class Base:
    def __init__(self, log):
        log.append("Base")
class Left(Base):
    def __init__(self, log):
        log.append("Left")
        super().__init__(log)            # next class in type(self).__mro__
class Right(Base):
    def __init__(self, log):
        log.append("Right")
        super().__init__(log)
class Child(Left, Right):
    def __init__(self, log):
        log.append("Child")
        super().__init__(log)

log = []
Child(log)
print(log, [k.__name__ for k in Child.__mro__])
```

```text
['Child', 'Left', 'Right', 'Base'] ['Child', 'Left', 'Right', 'Base', 'object']
```

`Left`'s `super()` reaches `Right`, a class it has never heard of, so cooperative methods
forward `**kwargs`. If each class calls its parent explicitly, `Base` runs twice.

### Worked problem 1 — compute the MRO yourself (C3)

*Given each class's direct bases, return Python's MRO, or report that none exists.* (ex04)

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| 1 | DFS left-to-right, keep first visit | O(V + E) | diamond gives D, B, **A**, C: `C` overrides are skipped |
| 2 | DFS, keep **last** visit | O(V + E) | breaks declared base order on some hierarchies; never detects inconsistency |
| 3 | C3 merge, memoised | O(k²·L²) per class (k bases, MRO length L) | — |

C3: `L[C] = C + merge(L[B1], …, L[Bn], [B1, …, Bn])`. The merge repeatedly takes the first list
head that appears in no list's *tail*. That guarantees three things: children come before
parents, declared base order is kept, and every parent's MRO is a subsequence of the child's.

```python
def c3_linearize(cls: str, bases: dict[str, list[str]], memo=None) -> list[str]:
    memo = {} if memo is None else memo
    if cls in memo:
        return memo[cls]
    seqs = [list(c3_linearize(b, bases, memo)) for b in bases[cls]] + [list(bases[cls])]
    result = [cls]
    while any(seqs):
        seqs = [s for s in seqs if s]
        for s in seqs:                   # first head that sits in no other list's tail
            head = s[0]
            if not any(head in other[1:] for other in seqs):
                break
        else:
            raise ValueError(f"inconsistent hierarchy: cannot order {seqs}")
        result.append(head)
        for s in seqs:
            if s[0] == head:
                del s[0]
    memo[cls] = result
    return result

print(c3_linearize("D", {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}))
```

```text
['D', 'B', 'C', 'A']
```

For `class Z(X, Y)` with `Y(X)` the merge gets stuck: `ValueError` here, `TypeError` in Python.
Tests compare it with real `__mro__` on random hierarchies.
→ repo: `chapters/ch24_oop_dataclasses_abcs/solutions/ex04_mro_c3.py`

**Edge cases:** root class; single chain; diamond; a base listed before its own subclass
(inconsistent); deep hierarchies (memoise). **Wrong-but-tempting:** "the MRO is depth-first"
(only for Python 2 classic classes); "`super()` is the parent". **Follow-ups:** why
`**kwargs` in cooperative `__init__`? What does the explicit `super(Left, self)` mean?

## 24.4 Composition over inheritance

Inherit only for a real "is-a" relation with a base *designed* for extension (an ABC,
`Exception`). Otherwise hold the object and delegate to it. Subclassing a built-in is the
classic trap:

```python
class CountingList(list):                # inherit: the tempting rung
    def __init__(self):
        super().__init__()
        self.added = 0
    def append(self, x):
        self.added += 1
        super().append(x)

c = CountingList()
c.append(1)
c.extend([2, 3])                         # list's C code never calls our append
c += [4]
print(len(c), c.added)
```

```text
4 1
```

ex05's `AuditedList` *holds* a list and exposes only the methods it counts. If every mutation
must pass through your hooks, subclass `collections.abc.MutableSequence`: its mixin `append`,
`extend` and `+=` call your `insert`. `UserList.extend` bypasses an overridden `append`.

## 24.5 Encapsulation, properties (`@property`)

Python has no `private`. `_x` means "internal" by convention, and `__x` is name-mangled to
`_Cls__x` to avoid subclass clashes (it is not security). Start with plain attributes. Switch to
`@property` when you need validation or a computed value; callers still write `obj.x`.

```python
class Thermostat:
    def __init__(self, celsius):
        self.celsius = celsius           # runs the setter: one validation point
    @property
    def celsius(self):
        return self._celsius
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value
    @property
    def fahrenheit(self):                # computed and read-only
        return self._celsius * 9 / 5 + 32

t = Thermostat(25)
try:
    t.fahrenheit = 0
except AttributeError:
    print(t.celsius, t.fahrenheit, "| fahrenheit is read-only")
```

```text
25 77.0 | fahrenheit is read-only
```

For a costly value computed once, use `functools.cached_property`.

## 24.6 Magic/dunder methods: `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__len__`, `__getitem__`

Syntax calls dunder methods on the type: `len(x)` becomes `type(x).__len__(x)`.

| Syntax | Method | Rule |
|---|---|---|
| `repr(x)`, `len(x)` | `__repr__`, `__len__` | write `__repr__` first; `bool(x)` falls back to `len` |
| `a == b`, `hash(a)` | `__eq__`, `__hash__` | defining `__eq__` sets `__hash__ = None`; equal ⇒ same hash |
| `a < b` | `__lt__` | `functools.total_ordering` adds the rest (→ §25.7) |
| `a + b`, `0 + a` | `__add__`, `__radd__` | `__radd__` makes `sum()` work |
| `x[i]`, `x[a:b]` | `__getitem__` | gets an `int` **or** a `slice` |
| `v in x`, `for v in x` | `__contains__`, `__iter__` | both fall back to `__getitem__(0, 1, …)` (→ §23.3) |

Returning `NotImplemented` tells Python to try the reflected method (`b.__radd__(a)`). If both
sides decline, `==` falls back to identity and `+` raises `TypeError`. ex03 rebuilds `range` (slicing via
`slice.indices(n)`).

### Worked problem 2 — `Money`, a value type that behaves

*`Money(cents, currency)`: equal values must be interchangeable in sets and dicts; same-currency
amounts sort and add; `sum()` works; mixing currencies is an error.* (ex02)

| Rung | Idea | Cost | Why move up |
|---|---|---|---|
| 1 | `("USD", 19.99)` tuple | O(1) per op | `0.1 + 0.2 != 0.3`; tuples compare USD with EUR |
| 2 | class with `__eq__` only | O(1) | `__hash__` is `None`: `{m}` raises `TypeError` |
| 3 | int cents; `__eq__`/`__hash__` on the same fields; `__lt__`; arithmetic | O(1) | — |

```python
from functools import total_ordering
@total_ordering                          # derives <=, >, >= from == and < (→ §25.7)
class Money:
    def __init__(self, cents: int, currency: str) -> None:
        self._cents, self._currency = cents, currency
    def __repr__(self):
        return f"Money({self._cents}, {self._currency!r})"
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented        # not False, not raise: Python tries the other side
        return (self._cents, self._currency) == (other._cents, other._currency)
    def __hash__(self):                  # exactly the fields __eq__ compares
        return hash((self._cents, self._currency))
    def _same(self, other):
        if self._currency != other._currency:
            raise TypeError(f"currency mismatch: {self._currency} vs {other._currency}")
    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._same(other)
        return self._cents < other._cents
    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._same(other)
        return Money(self._cents + other._cents, self._currency)
    def __radd__(self, other):           # sum() starts with 0 + first_item
        return self if other == 0 else NotImplemented
a, b = Money(1999, "USD"), Money(1, "USD")
print(a + b, sum([a, b]), a >= b, len({Money(5, "EUR"), Money(5, "EUR")}), a == 1999)
for expr in (lambda: a < Money(1, "EUR"), lambda: a + 1):
    try:
        expr()
    except TypeError as exc:
        print("TypeError:", exc)
```

```text
Money(2000, 'USD') Money(2000, 'USD') True 1 False
TypeError: currency mismatch: USD vs EUR
TypeError: unsupported operand type(s) for +: 'Money' and 'int'
```

The repo adds validation, more operators and `allocate(ratios)`, which splits $10.00 as
3.34/3.33/3.33: floor each share, then hand out the leftover cents.
→ repo: `chapters/ch24_oop_dataclasses_abcs/solutions/ex02_money_value_type.py`

**Edge cases:** `Money == int` (False, no crash); `sum([])` is `0`, so pass a start value;
negative amounts in `str`; `True` as cents (a `bool` is an `int`); mixed-currency comparison.
**Wrong-but-tempting:** returning `False` instead of `NotImplemented`; hashing a mutable field;
`@dataclass(order=True)`, which would sort EUR before USD instead of raising.
**Follow-up:** currency conversion (rate table outside the class, → §24.4).

## 24.7 `@classmethod` and `@staticmethod`

A `classmethod` gets the class, so an **alternative constructor** calling `cls(...)` builds the
subclass. A `staticmethod` gets neither `self` nor `cls`: a function namespaced in the class.

```python
from datetime import date

class Event:
    def __init__(self, title, day):
        self.title, self.day = title, day
    @classmethod
    def from_iso(cls, title, text):      # alternative constructor: builds cls
        return cls(title, date.fromisoformat(text))
    @staticmethod
    def is_weekend(day):                 # helper: needs neither self nor cls
        return day.weekday() >= 5

class Holiday(Event):
    pass

h = Holiday.from_iso("New Year", "2026-01-01")
print(type(h).__name__, h.day, Event.is_weekend(h.day))
```

```text
Holiday 2026-01-01 False
```

A staticmethod factory that hard-codes `Event(...)` returns the wrong type for subclasses (ex06).

## 24.8 Dataclasses: `field`, `frozen`, `order`, `slots`

`@dataclass` reads the annotations and writes `__init__`, `__repr__` and `__eq__`. It adds
comparisons with `order=True` and `__hash__` with `frozen=True` (and the default `eq=True`).

```python
from dataclasses import FrozenInstanceError, asdict, dataclass, field, replace

@dataclass(frozen=True, order=True)      # order: compare as (major, minor, patch)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

@dataclass(slots=True)                   # slots=True needs Python 3.10+
class Cart:
    owner: str
    items: list[str] = field(default_factory=list)       # fresh list per Cart
    def __post_init__(self):
        if not self.owner:
            raise ValueError("owner required")

v = Version(1, 10)
print(sorted([v, Version(1, 9)]), {Version(1): "ok"}[Version(1, 0, 0)])
print(replace(v, patch=3))
try:
    v.major = 2
except FrozenInstanceError as exc:
    print("FrozenInstanceError:", exc)
a = Cart("ada")
a.items.append("pen")
print(a, Cart("bob").items, asdict(a), Cart.__hash__ is None)
```

```text
[Version(major=1, minor=9, patch=0), Version(major=1, minor=10, patch=0)] ok
Version(major=1, minor=10, patch=3)
FrozenInstanceError: cannot assign to field 'major'
Cart(owner='ada', items=['pen']) [] {'owner': 'ada', 'items': ['pen']} True
```

| Option | Effect | Gotcha |
|---|---|---|
| `field(default_factory=list)` | new default per instance | `items: list = []` raises `ValueError` at class definition |
| `frozen=True` | hashable; assignment raises `FrozenInstanceError` | shallow: a frozen object's list still mutates |
| `order=True` | compares field tuples in declaration order | requires `eq=True`; put the sort key first |
| `eq` / `frozen` / `unsafe_hash` | `eq=True, frozen=False` → `__hash__ = None` | `unsafe_hash=True` forces a hash; `eq=False` keeps identity hashing |
| `slots=True`, `kw_only=True` (3.10+) | `__slots__` (→ §27.4); keyword-only fields | no new attributes at runtime |

`replace` re-runs `__post_init__`; `asdict` recurses. Use `NamedTuple` (→ §6.2) when the record
must *be* a tuple (ex07).

## 24.9 Abstract base classes and protocols

An **ABC** is nominal: implementers inherit, and an unimplemented `@abstractmethod` blocks
instantiation. A **Protocol** (`typing`, 3.8+) is structural: any class
with the right methods matches, checked by type checkers. `@runtime_checkable` enables
`isinstance`, which checks method names exist, not signatures.

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

class Blob(Shape):                       # forgot area()
    pass

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class Socket:                            # never mentions Closeable
    def close(self):
        pass

print(Square(1.5).area(), isinstance(Socket(), Closeable), isinstance(Square(1), Closeable))
try:
    Blob()
except TypeError:
    print("Blob() -> TypeError; abstract:", sorted(Blob.__abstractmethods__))
```

```text
2.25 True False
Blob() -> TypeError; abstract: ['area']
```

Concrete ABC methods may call abstract ones (template methods). `collections.abc.Sized` and
`Iterable` recognise any class with the right dunder; `Shape.register(X)` makes `isinstance`
true without checking anything. Prefer a Protocol for third-party plugin APIs (ex08).

## 24.10 Enums

An `Enum` is a closed set of named singletons. Use one instead of magic strings or ints.

```python
from enum import Enum, Flag, auto

class Status(Enum):
    PENDING = "pending"
    PAID = "paid"

class Perm(Flag):
    READ = auto()
    WRITE = auto()

s = Status("paid")                       # by value; Status["PAID"] by name
print(s, s.name, s.value, s is Status.PAID, Status.PAID == "paid")
rw = Perm.READ | Perm.WRITE
print(Perm.WRITE in rw, rw.value, [m.name for m in Status])
try:
    Status("refunded")
except ValueError as exc:
    print("ValueError:", exc)
```

```text
Status.PAID PAID paid True False
True 3 ['PENDING', 'PAID']
ValueError: 'refunded' is not a valid Status
```

Members are hashable singletons: ideal transition-table keys (ex09). `IntEnum` members equal
plain ints, which is handy but leaky. Since 3.11, `str()` of an `IntEnum` member is the number
(`'3'`), matching f-strings, which already were; `StrEnum` is 3.11+. `@enum.unique` forbids
aliases.

## 24.11 Design patterns, one runnable example each: Singleton, Factory, Strategy, Observer ◆

First-class functions shrink most patterns to a few lines:

```python
from collections import defaultdict

class Config:                            # Singleton (a module is the simpler one)
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

SHAPES = {"square": lambda s: s * s, "cube": lambda s: s ** 3}
def make_area(kind, size):               # Factory: registry lookup, no if-chain
    return SHAPES[kind](size)

def percent_off(p):                      # Strategy: any callable fits
    return lambda total: total * (100 - p) // 100

class EventBus:                          # Observer
    def __init__(self):
        self.handlers = defaultdict(list)
    def subscribe(self, event, fn):
        self.handlers[event].append(fn)
    def publish(self, event, payload):
        for fn in self.handlers[event]:
            fn(payload)

print(Config() is Config(), make_area("square", 3), percent_off(10)(2000))
bus = EventBus()
bus.subscribe("paid", lambda order: print("email receipt for", order))
bus.subscribe("paid", lambda order: print("reserve stock for", order))
bus.publish("paid", "A17")
```

```text
True 9 1800
email receipt for A17
reserve stock for A17
```

Caveats: a Singleton is hidden global state (`__init__` reruns on each call); fill factory
registries with a decorator (→ §25.6). Full versions: ex10.

## 24.12 Metaclasses ○

`type(name, bases, ns)` builds a class; `type` is the class of classes. A metaclass subclasses
`type` to hook class creation. `__init_subclass__` (3.6+, PEP 487) covers most needs:

```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, **kwargs):     # runs once per subclass definition
        super().__init_subclass__(**kwargs)
        Plugin.registry[cls.__name__.lower()] = cls

class Upper(Plugin):
    def run(self, s): return s.upper()

Reverse = type("Reverse", (Plugin,), {"run": lambda self, s: s[::-1]})  # classes are objects
print(sorted(Plugin.registry), type(Upper).__name__, type(type).__name__)
```

```text
['reverse', 'upper'] type type
```

Use a real metaclass only to control the class object itself, as `ABCMeta` does (ex11).

## Interviewer's view

- **Rewarded:** `__repr__` first; `__eq__` and `__hash__` together; `NotImplemented` for foreign
  types; validation in one place; a reason for each tool choice.
- **Penalised:** subclassing `list`/`dict`; mutable class attributes; Java-style getters;
  deep hierarchies; Singleton by reflex.

## Exercises

All in `chapters/ch24_oop_dataclasses_abcs/` (statements, ladders, tests in the repo).

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Bank account | ★ | class attributes, `@property` |
| ex02 | Money (worked problem 2) | ★ | eq/hash, `NotImplemented` |
| ex03 | Span: rebuild `range()` | ★ | sequence protocol |
| ex04 | C3 MRO (worked problem 1) | ★ | `super()`, C3 |
| ex05 | Audited list, strict stack | ★ | composition |
| ex06 | Alternative constructors | ★ | `@classmethod` |
| ex07 | Dataclass inventory | ★ | `field`, `frozen`, `order`, `slots` |
| ex08 | Pluggable storage | ★ | ABC, `Protocol` |
| ex09 | Order workflow | ★ | `Enum`, `Flag` |
| ex10 | Four design patterns | ◆ | patterns |
| ex11 | Plugin registry | ○ | metaclass |

## Checkpoint quiz

1. After `b.species = "lupus"`, what do `Dog.species` and other dogs read?
2. In `class Child(Left, Right)`, which method does `super()` inside `Left` call?
3. You define `__eq__` and put instances in a set. What happens?
4. Why should `__add__` return `NotImplemented` rather than raise?
5. Why is a plain `@dataclass` unhashable?

<details>
<summary>Answers</summary>

1. `"canis"`: only `b` got an instance attribute.
2. `Right.__init__`, the next class after `Left` in `Child.__mro__`.
3. `TypeError: unhashable type`. `__eq__` set `__hash__ = None`, so add a `__hash__` over the
   same immutable fields.
4. So Python can try the other operand's `__radd__`; `TypeError` comes only if both decline.
5. Mutable fields would change its hash while it sits in a dict, so `__hash__ = None`.

</details>

## Summary card

- Lookup: instance → class → `__mro__`; assignment writes to the instance, unless a property/descriptor intercepts.
- `super()` = next class in `type(self).__mro__`; C3 keeps children first and base order.
- `__eq__` + `__hash__` together; `NotImplemented` for unknown types; `__radd__` for `sum`.
- `@dataclass`: `default_factory`, `frozen` → hashable, `order` → field tuples, `slots`/`kw_only` 3.10+.
- ABC = nominal, fails at construction; Protocol = structural; `runtime_checkable` checks names.
- `Enum` closed sets; `Flag` bit sets; prefer `__init_subclass__` to metaclasses.
