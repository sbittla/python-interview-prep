# Chapter 5. Syntax, Types, Control Flow and Functions

**Tier:** ★ Core · **Tracks:** S, M, L · **Study time:** 4–6 hours · **Prerequisites:** Chapter 4

Skip it if you passed the Chapter 3 diagnostic. Traps live in Chapter 7 and collections in
Chapter 6, so here they get a pointer such as (→ §7.1). Code is 3.10+, and newer features are
flagged.

**Learning objectives**

- Explain assignment as binding a name to an object, and predict what mutation versus rebinding does.
- Use `int`, `float`, `str` correctly: floor division, slicing, f-string format specs.
- Write and call any signature (`/`, `*args`, keyword-only, `**kwargs`); resolve names with LEGB.

> **Recognise it**
>
> | You hear / notice | Reach for |
> |---|---|
> | "parse these commands", "handle each message shape" | `match` (§5.4) |
> | "search, and report if not found" | `for … else` or `next(gen, default)` (§5.5) |
> | "any number of arguments", "optional settings" | `*args`, keyword-only, `**kwargs` (§5.6) |
> | "counter that remembers", "factory" | closure + `nonlocal` (§5.8) |

## 5.1 Variables, dynamic typing and names vs objects

A variable is a **name bound to an object**. The type belongs to the object, so one name can
refer to an `int` and later to a `str`. Assignment never copies. **Mutation** (`b.append(3)`)
changes the shared object. **Rebinding** (`b = b + [4]`) points one name at a new object.
Arguments work the same way (*call by sharing*).

```python
a = [1, 2]
b = a                 # a second name for the same list
b.append(3)           # mutation: visible through a
b = b + [4]           # rebinding: b now names a new list
print(a, b, a is b)

def grow(items):
    items.append("!")     # the caller sees this
    items = ["new"]       # local rebinding: the caller does not

s = ["hi"]
grow(s)
print(s)
```

```text
[1, 2, 3] [1, 2, 3, 4] False
['hi', '!']
```

`is` is identity, `==` is value. Aliasing and copies: → §7.2; small-int caching: → §7.6.

## 5.2 Numeric types: `int` (unbounded), `float`, `bool`

| Type / operator | Interview facts |
|---|---|
| `int` | Arbitrary precision. It never overflows, so check any 32/64-bit limit by hand (→ §7.10) |
| `float` | IEEE-754 double; `0.1 + 0.2 != 0.3` (→ §7.8) |
| `bool` | Subclass of `int`: `True + True == 2` (→ §7.6) |
| `/`, `//`, `%`, `int()` | `/` gives a float. `//` floors towards −∞ and `%` takes the divisor's sign (→ §7.9). `int()` truncates towards 0 |

```python
import math
print(2**100, 7 / 2, -7 // 2, -7 % 2, divmod(-7, 2), int(-3.7))
n = (2**26 + 1) ** 2 - 1
print(int(n ** 0.5), math.isqrt(n))      # the float square root rounds up
```

```text
1267650600228229401496703205376 3.5 -4 1 (-4, 1) -3
67108865 67108864
```

Use `math.isqrt` (3.8+) for exact roots. Since 3.11 (also backported), `str()`/`int()` of an int
with over 4,300 digits raises `ValueError`. Complex numbers
(○): `abs(3 + 4j) == 5.0`.

### Worked problem (ex02): Reverse a signed integer with a 32-bit clamp

Reverse the digits of `x`, keeping the sign. Return 0 if the result is outside [−2³¹, 2³¹ − 1].

- *Rung 1, string:* `int(str(abs(x))[::-1])` with the sign reapplied. O(d) time, O(d) space for d
  digits. This is acceptable in Python interviews.
- *Rung 2, arithmetic:* peel digits with `divmod`. O(d) time, O(1) extra space. Move up when the
  interviewer rules out string conversion.

```python
INT_MIN, INT_MAX = -(2**31), 2**31 - 1

def solve(x: int) -> int:
    sign = -1 if x < 0 else 1
    n, result = abs(x), 0          # work on abs(x): -123 % 10 == 7, not -3
    while n:
        n, digit = divmod(n, 10)
        result = result * 10 + digit
    result *= sign
    return result if INT_MIN <= result <= INT_MAX else 0   # ints never overflow

for x in [123, -120, 0, 1534236469, -2147483412, 10**20]:
    print(f"{x:>22} -> {solve(x):>11}")
```

```text
                   123 ->         321
                  -120 ->         -21
                     0 ->           0
            1534236469 ->           0
           -2147483412 -> -2143847412
 100000000000000000000 ->           1
```

→ repo: `chapters/ch05_syntax_types_functions/solutions/ex02_reverse_integer.py`

- **Edge cases:** 0, trailing zeros (−120 → −21), a result just past `INT_MAX`, `-(2**31)`, and an
  input that is already out of range (10²⁰ → 1).
- **Wrong but tempting:** peeling a negative `x` directly. `-1 // 10 == -1`, so the loop never
  ends. Another is skipping the range check because "Python can't overflow".
- **Follow-ups:** in C or Java, test `result > (INT_MAX - digit) // 10` *before* multiplying.

## 5.3 Strings: indexing, slicing, methods, f-strings, immutability

A `str` is an immutable sequence of code points. `s[i]` raises `IndexError` when out of range,
while slices clamp to the ends. Methods return **new** strings. Build big strings with
`"".join(parts)` (→ §7.17), and see `split()` vs `split(" ")` in → §7.23.

```python
s = "interview"
print(s[0], s[-1], s[2:5], s[::-1], s[5:100], s.find("z"), s.replace("e", "3"))
try:
    s[0] = "I"
except TypeError as exc:
    print("TypeError:", exc)
x, name, n = 3.14159, "ada", 1234567
print(f"{x=:.2f} | {name!r} | {n:,} | {5:08b} | {0.256:.1%} | {'hi':*^6} | {name:>5}|")
```

```text
i w ter weivretni view -1 int3rvi3w
TypeError: 'str' object does not support item assignment
x=3.14 | 'ada' | 1,234,567 | 00000101 | 25.6% | **hi** |   ada|
```

Spec order: `[[fill]align][sign][width][,][.precision][type]`; `{x=}` is 3.8+. Reusing the outer
quote inside an expression (`f"{d["k"]}"`) needs **3.12+** (PEP 701). `find` returns −1, while
`index` raises. ex04 formats a receipt with specs alone.

## 5.4 Conditionals, `match` statement ◆

Falsy: `None`, `False`, `0`, `0.0`, `""`, empty containers. `and`/`or` return an **operand**
(so `word or str(i)` works in ex01). Comparisons chain (`0 <= i < n`). Use
`x is None`, not `not x`, when 0 or `""` are valid values.

**`match` (3.10+, PEP 634)** tests the *shape* of a value and binds names:

| Pattern | Example | Matches |
|---|---|---|
| literal | `case "quit":` | equal value (`None`/`True`/`False` compare with `is`) |
| capture / wildcard | `case x:` / `case _:` | anything (a bare name binds; it never compares) |
| sequence | `case ["push", arg]:` | a list or tuple of length 2 starting with `"push"` (never a `str`) |
| OR / AS | `case "a" \| "b" as op:` | either literal, bound to `op` |
| mapping | `case {"type": "click", "x": x}:` | a dict with these keys (extra keys allowed) |
| class + guard | `case Point(x=0, y=y) if y > 0:` | an `isinstance` check plus attributes plus a condition |

### Worked problem (ex05): A tiny stack machine

Run `push <int>`, `pop`, `add`, `mul`, `dup` and `print` lines against a stack and return what was
printed. Raise `ValueError` on underflow or on a malformed line.

- *Rung 1, if/elif:* split, then test the command word **and** `len(parts)` in every branch. O(n)
  for n lines, but forgotten length checks let `"add 1"` through.
- *Rung 2, `match`:* each case states the whole shape, and anything else falls to `case _`. Same
  O(n). Move up because shape checking and binding happen in one step. Before 3.10, use a dict of
  handler functions.

```python
def _is_int(arg: str) -> bool:
    return arg.removeprefix("-").isdecimal()   # "²".isdigit() is True; int("²") fails

def _pop2(stack: list[int]) -> tuple[int, int]:
    if len(stack) < 2:
        raise ValueError("stack underflow")
    b = stack.pop()
    return stack.pop(), b

def solve(program: list[str]) -> list[int]:
    stack: list[int] = []
    out: list[int] = []
    for line in program:
        match line.split():
            case ["push", arg] if _is_int(arg):       # guard refines the pattern
                stack.append(int(arg))
            case ["pop" | "dup" | "print" as op]:     # OR-pattern with a capture
                if not stack:
                    raise ValueError("stack underflow")
                if op == "pop":
                    stack.pop()
                else:
                    (stack if op == "dup" else out).append(stack[-1])
            case ["add" | "mul" as op]:
                a, b = _pop2(stack)
                stack.append(a + b if op == "add" else a * b)
            case _:                                   # wildcard: nothing else matched
                raise ValueError(f"bad command: {line}")
    return out

print(solve(["push 2", "push 3", "add", "print", "dup", "mul", "print", "push -4", "add", "print"]))
```

```text
[5, 25, 21]
```

→ repo: `chapters/ch05_syntax_types_functions/solutions/ex05_stack_machine_match.py`

- **Edge cases:** an empty program, extra whitespace, `push` with no argument, `push --5`, an empty
  line (`[]` reaches `case _`), and underflow for every command.
- **Wrong but tempting:** `case ADD:` with a module constant `ADD`. It *captures* and matches
  everything. Use `Op.ADD` or a literal. Another is calling `int(arg)` unguarded, which leaks the
  wrong error message.
- **Follow-ups:** add `jmp <n>` (a guard plus an index-based loop). Return all errors instead of
  stopping at the first.

## 5.5 Loops: `for`, `while`, `range`, `enumerate`, `zip`, `for…else`

`for` walks any iterable. `while` suits loops whose end you can't count in advance.
`range(start, stop, step)` is lazy and excludes `stop`. `enumerate(xs, start=1)` gives index-value
pairs. `zip` stops at the shortest input, and `strict=True` (3.10+) raises instead. A loop's
`else` runs only if the loop **ended without `break`**, which is the shape of "search, else report
failure" (ex06; trap quiz → §7.13):

```python
from math import isqrt

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, isqrt(n) + 1, 2):
        if n % d == 0:
            break
    else:
        return True          # no divisor found: loop ended without break
    return False

print([n for n in range(30) if is_prime(n)], is_prime(2**31 - 1))
print(next((x for x in [4, 6, 9, 11, 13] if is_prime(x)), None))
```

```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29] True
11
```

Trial division to √n costs O(√n), not O(n). Never mutate a list you are looping over (→ §7.11).

## 5.6 Functions: positional/keyword args, `*args`, `**kwargs`, defaults, return values

```python
def f(a, /, b, *args, c, d=4, **kw):
    return a, b, args, c, d, kw

print(f(1, 2, 3, c=5, z=6))          # 3 -> args; z -> kw
print(f(1, b=2, c=3))                 # b may be passed by keyword
print(f(*[1, 2, 3, 4], **{"c": 0}))   # unpack at the call site
try:
    f(1, 2, 3)
except TypeError as exc:
    print("TypeError:", exc)
```

```text
(1, 2, (3,), 5, 4, {'z': 6})
(1, 2, (), 3, 4, {})
(1, 2, (3, 4), 0, 4, {})
TypeError: f() missing 1 required keyword-only argument: 'c'
```

| Part | Meaning |
|---|---|
| `a, /` | positional-only (3.8+). With `**kw` present, `a=1` lands in `kw` |
| `*args` / `**kw` | extra positionals go into a **tuple**, extra keywords into a **dict** |
| after `*args` (or a bare `*`) | keyword-only: `c` must be passed as `c=…` |
| `d=4` | evaluated **once** when `def` runs, so never default to `[]` (→ §7.1, ex08) |

`return a, b` returns one tuple. With no `return`, a function returns `None`, and that includes
`list.sort()`. ex07 uses the full signature.

## 5.7 Lambdas and first-class functions

Functions are objects. You can store them (dispatch tables), pass them (`key=`, callbacks) and
return them (factories; decorators are in Chapter 25). `lambda args: expr` holds **one
expression**, with no statements and no annotations.

```python
def pipeline(*funcs):
    def run(x):
        for f in funcs:
            x = f(x)
        return x
    return run

normalise = pipeline(str.strip, str.split, " ".join, str.title)   # methods are functions
names = ["  ada   lovelace ", "GRACE hopper", "\tlinus  torvalds\n"]
print(sorted(map(normalise, names), key=lambda n: n.split()[-1]))
```

```text
['Grace Hopper', 'Ada Lovelace', 'Linus Torvalds']
```

Pass `key=len`, not `key=len()`. Loop lambdas read the variable when they run (→ §7.5). ex09 builds `compose` and `pipeline`.

## 5.8 Scope: LEGB, `global`, `nonlocal`

A name is looked up in **L**ocal, then **E**nclosing functions (innermost first), then
**G**lobal (the module), then **B**uilt-ins. The trap: an assignment *anywhere* in a function makes
the name local for the *whole* function. The compiler decides this, so reading it first raises
`UnboundLocalError`:

```python
def make_counter():
    count = 0
    def bump():
        count += 1            # assignment => count is local to bump
        return count
    return bump

try:
    make_counter()()
except UnboundLocalError as exc:
    print("UnboundLocalError:", exc)
```

```text
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

That is the 3.13 wording. Older versions phrase it differently, so match the exception type, not
the text. `global x` rebinds a module name and `nonlocal x` the nearest enclosing function's name.
Mutating an object (`state["n"] += 1`) needs neither.

### Worked problem (ex10): Counters with closures

`solve(start, step)` returns `(increment, current)`. Counters must be independent, with no class
and no global.

- *Rung 1, global:* `global count`. O(1) per call, but all counters share one variable, so they
  interfere, and so do tests.
- *Rung 2, closure:* the state lives in the factory's scope, and each factory call creates a new
  scope. O(1) time and space per call. Move up for independent instances.

```python
def solve(start: int = 0, step: int = 1):      # returns (increment, current)
    value = start
    def increment() -> int:
        nonlocal value        # rebind the enclosing name instead of creating a local
        value += step
        return value
    def current() -> int:
        return value          # reading an enclosing name needs no declaration
    return increment, current

inc_a, cur_a = solve()
inc_b, cur_b = solve(100, 10)
print("a:", inc_a(), inc_a(), inc_a(), "| b:", inc_b(), inc_b(), "| now", cur_a(), cur_b())
```

```text
a: 1 2 3 | b: 110 120 | now 3 120
```

→ repo: `chapters/ch05_syntax_types_functions/solutions/ex10_closures_nonlocal.py` (it also
contains `make_averager`, a running mean kept in O(1) memory as a total and a count)

- **Edge cases:** `current()` before any increment, two counters from one factory, and a negative
  `step`.
- **Wrong but tempting:** a running mean that stores every value and calls `sum` each time, which
  is O(n) per call. Another is `global` in a nested function, which skips the enclosing scope.
- **Follow-ups:** why does a captured dict work without `nonlocal`? When would you switch to a
  class (several methods, pickling)?

## 5.9 Type hints basics (not enforced at runtime)

Annotations are metadata in `__annotations__`. The interpreter ignores them (→ §7.26), and mypy or
pyright check them statically.

```python
def scale(x: int, factor: int = 2) -> int:
    return x * factor

print(scale("ab"), scale.__annotations__)     # no error: hints are not checked
```

```text
abab {'x': <class 'int'>, 'factor': <class 'int'>, 'return': <class 'int'>}
```

| Syntax | Works from |
|---|---|
| `list[int]`, `dict[str, int]` | 3.9 |
| `int \| None` evaluated at runtime (`Optional[int]` anywhere) | 3.10 |
| `def first[T](xs: list[T]) -> T`, `type Alias = …` (PEP 695) | **3.12+** |

ex12 binds arguments with `inspect.signature`, resolves hints with `typing.get_type_hints` and
reports mismatches. It rejects `True` for `int`.

## 5.10 Comprehensions — one-line preview

`[x * x for x in xs if x % 2]` builds a list in one expression. The set, dict and generator forms
work the same way (full treatment: Chapter 23).

## Interviewer's view

- **Rewarded:** naming edge cases first (negatives, empty input, the 32-bit limit), using
  `is None` deliberately, and flagging `match` as 3.10+.
- **Penalised:** mutable defaults, `//`/`%` on negatives without thought, if/elif ladders that
  miss malformed input, `global` state, and `x = xs.sort()`.

## Exercises

All in `chapters/ch05_syntax_types_functions/` (statements, ladders, hints, tests).

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | FizzBuzz with pluggable rules | ★ | loops, `or` fallback |
| ex02 | Reverse a signed integer | ★ | `divmod`, unbounded `int` |
| ex03 | Palindrome after normalisation | ★ | slicing, two indices |
| ex04 | Aligned receipt with f-strings | ★ | format specs |
| ex05 | Tiny stack machine | ◆ | `match` (3.10+) |
| ex06 | Primality and first prime | ★ | `for … else`, `isqrt` |
| ex07 | Flexible summary function | ★ | `*args`, keyword-only, `**kwargs` |
| ex08 | Fix the mutable default | ★ | `None` sentinel |
| ex09 | Compose a pipeline | ★ | first-class functions |
| ex10 | Counters and running averages | ★ | closures, `nonlocal` |
| ex11 | Run-length encoding | ★ | string scanning, `join` |
| ex12 | Check arguments against hints | ◆ | `inspect`, `get_type_hints` |

## Checkpoint quiz

1. After `a = [1]; b = a; b += [2]; b = b + [3]`, what are `a` and `b`?
2. What do `-7 // 2`, `-7 % 2` and `int(-3.5)` return?
3. With `QUIT = "q"` defined, why does `case QUIT:` match every command?
4. Write a signature where `x` is positional-only, `y` keyword-only, and extra keywords are collected.
5. Why does `count += 1` in a nested function raise `UnboundLocalError`? Give two fixes.

<details>
<summary>Answers</summary>

1. `[1, 2]` and `[1, 2, 3]`: `+=` mutates in place, `b + [3]` rebinds only `b`.
2. `-4`, `1`, `-3`. `//` floors, `%` follows the divisor's sign, `int()` truncates.
3. A bare name is a capture pattern. If cases follow it, compilation fails with "name capture
   'QUIT' makes remaining patterns unreachable". Use `Cmd.QUIT` or `"q"`.
4. `def f(x, /, *, y, **kw): ...`
5. The assignment makes `count` local. Fix it with `nonlocal count`, or mutate a container instead.

</details>

## Summary card

- Names bind to objects. Mutation is shared, rebinding is not (also for arguments).
- `int` is unbounded, so check 32-bit limits yourself. `//` floors, `%` follows the divisor, use
  `math.isqrt`, and `bool` is an `int`.
- `str` is immutable. Slices clamp and indexing raises. `{v:>12,.2f}`, `{x=}` (3.8+); same-quote
  nesting needs 3.12+.
- Falsy: `None`, `0`, `""`, empties. Sentinels use `is None`. In `match` (3.10+), a bare name captures.
- Loop `else` means no `break`. `zip(strict=True)` is 3.10+. Lambdas hold one expression.
- Signature order: `pos_only, /, normal, *args, kw_only, **kwargs`. Defaults are evaluated once.
- LEGB. Assignment makes a name local. `nonlocal` is for an enclosing name, `global` for a module name.
- Hints are not enforced. `X | None` at runtime is 3.10, PEP 695 is 3.12+.
