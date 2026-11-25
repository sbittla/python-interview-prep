"""
Exercise 06 — Alternative Constructors: @classmethod vs @staticmethod  [Tier: ★ Core]
Chapter 24 · Pattern: classmethod factories that respect subclasses · Target time: 20 min

Problem
-------
Write `Color(r, g, b)` (ints 0..255, else `ValueError`) with:

- `Color.from_hex("#1e90ff")` — also accepts `"1E90FF"` and 3-digit `"#fff"` shorthand.
- `Color.from_name("tomato")` — looks the name up (case-insensitive) in a class-level
  table `NAMED`; unknown -> `KeyError`.
- `Color.blend(a, b)` — a STATIC helper that averages two `(r, g, b)` tuples channel by
  channel (rounding halves up) and returns a tuple; it needs neither `self` nor `cls`.
- `c.to_hex()` -> `"#1e90ff"`; `repr` -> `Color(30, 144, 255)`; `==` by channels.

Then `AlphaColor(Color)` adds `alpha` (default 255). Because the factories are
classmethods that build `cls(...)`, `AlphaColor.from_hex("#fff")` must return an
`AlphaColor`, with no code repeated in the subclass. Its repr is
`AlphaColor(255, 255, 255, alpha=255)`.

Examples
--------
>>> Color.from_hex("#fff")
Color(255, 255, 255)
>>> type(AlphaColor.from_name("tomato")).__name__
'AlphaColor'

Constraints
-----------
- All operations O(1).

Approach ladder
---------------
1. Brute force — a module function or `@staticmethod` factory that hard-codes
   `return Color(...)`: O(1), but `AlphaColor.static_from_hex(...)` returns a plain
   `Color` (shown in `main`), so every subclass must rewrite every factory.
2. Optimal    — `@classmethod` factories that call `cls(...)`: subclasses inherit working
   constructors for free. Keep `@staticmethod` for helpers that use neither.

Hints
-----
- Expand 3-digit shorthand by doubling each character: `"fff"` -> `"ffffff"`.
- `int(s[i:i+2], 16)` parses one channel.
- `repr` should use `type(self).__name__` so subclasses print their own name.

Follow-ups
----------
- `dict.fromkeys`, `datetime.fromisoformat` and `int.from_bytes` are classmethods in the
  standard library; check that `class MyDict(dict)` gets `MyDict.fromkeys(...)` back.
- How would you keep a registry of every subclass? (`__init_subclass__`, → §24.12)
"""
from __future__ import annotations


class Color:
    NAMED: dict[str, tuple[int, int, int]] = {
        "black": (0, 0, 0), "white": (255, 255, 255),
        "tomato": (255, 99, 71), "dodgerblue": (30, 144, 255),
    }

    def __init__(self, r: int, g: int, b: int) -> None:
        for v in (r, g, b):
            if not 0 <= v <= 255:
                raise ValueError(f"channel {v} out of range 0..255")
        self.r, self.g, self.b = r, g, b

    @classmethod
    def from_hex(cls, text: str) -> Color:
        h = text.removeprefix("#").lower()          # str.removeprefix: 3.9+
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) != 6 or any(ch not in "0123456789abcdef" for ch in h):
            raise ValueError(f"bad hex colour {text!r}")
        return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))   # cls, not Color

    @classmethod
    def from_name(cls, name: str) -> Color:
        return cls(*cls.NAMED[name.lower()])

    @staticmethod
    def blend(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
        return tuple((x + y + 1) // 2 for x, y in zip(a, b))   # no self, no cls

    @staticmethod
    def static_from_hex(text: str) -> Color:
        """Rung 1: a staticmethod factory hard-codes the class."""
        h = text.removeprefix("#")
        return Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self.rgb())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.rgb() == other.rgb()

    __hash__ = None                                 # mutable: explicitly unhashable

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.r}, {self.g}, {self.b})"


class AlphaColor(Color):
    def __init__(self, r: int, g: int, b: int, alpha: int = 255) -> None:
        super().__init__(r, g, b)
        if not 0 <= alpha <= 255:
            raise ValueError(f"alpha {alpha} out of range 0..255")
        self.alpha = alpha

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AlphaColor):
            return NotImplemented
        return self.rgb() == other.rgb() and self.alpha == other.alpha

    __hash__ = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.r}, {self.g}, {self.b}, alpha={self.alpha})"


def main() -> None:
    print(Color.from_hex("#1E90FF"), Color.from_hex("fff"), Color.from_name("Tomato"))
    print("to_hex:", Color(30, 144, 255).to_hex(),
          "| round trip:", Color.from_hex(Color(1, 2, 3).to_hex()) == Color(1, 2, 3))
    print("blend:", Color.blend((255, 0, 0), (0, 0, 255)),
          "| via instance:", Color(0, 0, 0).blend((0, 0, 0), (1, 1, 1)))
    print("AlphaColor.from_hex:", AlphaColor.from_hex("#fff"),
          "| from_name:", AlphaColor.from_name("dodgerblue"))
    print("staticmethod factory on subclass ->",
          type(AlphaColor.static_from_hex("#ffffff")).__name__)
    print("dict subclass fromkeys ->", type(type("MyDict", (dict,), {}).fromkeys("ab")).__name__)
    for bad in (lambda: Color.from_hex("#12345"), lambda: Color(0, 0, 256)):
        try:
            bad()
        except ValueError as exc:
            print("ValueError:", exc)
    try:
        Color.from_name("chartreuse")
    except KeyError as exc:
        print("KeyError:", exc)


if __name__ == "__main__":
    main()
