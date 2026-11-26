"""
Exercise 14 — Encode and Decode a List of Strings         [Tier: ★ Core]
Chapter 09 · Pattern: length-prefix framing · Target time: 15 min

Problem
-------
Design encode(strs) -> str and decode(s) -> list[str] such that
decode(encode(x)) == x for ANY list of strings, including empty strings, strings
containing your delimiter, digits, or any Unicode. Also implement run-length
encoding rle_encode("aaabcc") -> "3a1b2c" and its inverse rle_decode for strings
without digits.

Examples
--------
>>> encode(["hi", "", "a#b"])
'2#hi0#3#a#b'
>>> decode('2#hi0#3#a#b')
['hi', '', 'a#b']

Constraints
-----------
- Total length <= 10**5. No character is forbidden in the input strings.

Hints
-----
- Any delimiter you pick can appear inside a string. What if the decoder never has to search the payload?
- Escaping works too: what must be escaped, and in what order?
- RLE: counts can have more than one digit.

Follow-ups
----------
- Binary-safe framing: fixed 4-byte big-endian length (struct.pack(">I", n)).
- Why must a "#" inside "a#b" not confuse your decoder?
- Bonus: string building — always collect parts in a list and "".join them;
  repeated s += part can be O(n^2).
"""
from __future__ import annotations


def naive_encode(strs: list[str]) -> str:
    return ",".join(strs)


def naive_decode(s: str) -> list[str]:
    return s.split(",")


def escape_encode(strs: list[str]) -> str:
    """Rung 2: escape the delimiter and the escape character."""
    raise NotImplementedError("TODO")


def escape_decode(s: str) -> list[str]:
    raise NotImplementedError("TODO")


def encode(strs: list[str]) -> str:
    raise NotImplementedError("TODO")


def decode(s: str) -> list[str]:
    raise NotImplementedError("TODO")


def solve(strs: list[str]) -> list[str]:
    """Round trip, used by the tests."""
    raise NotImplementedError("TODO")


def rle_encode(s: str) -> str:
    raise NotImplementedError("TODO")


def rle_decode(s: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    samples = [["hi", "", "a#b"], ["12#", "#", "3"], [], [""], ["héllo", "日本語"]]
    for strs in samples:
        enc = encode(strs)
        print(f"{strs!s:<22} -> {enc!r:<22} round-trip ok: {decode(enc) == strs}")
    tricky = ["a,b", "c\\", "", ","]
    print("escaped:", repr(escape_encode(tricky)), "round-trip ok:", escape_decode(escape_encode(tricky)) == tricky)
    print("naive comma join breaks:", naive_decode(naive_encode(["a,b", "c"])), "and [] ->", naive_decode(naive_encode([])))
    for s in ["aaabcc", "abc", "", "aaaaaaaaaaaab"]:
        print(f"rle {s!r:<16} -> {rle_encode(s)!r:<10} back ok: {rle_decode(rle_encode(s)) == s}")


if __name__ == "__main__":
    main()
