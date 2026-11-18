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

Approach ladder
---------------
1. Naive delimiter — ",".join(strs). Breaks as soon as a string contains ",",
   and cannot tell [] from [""].
2. Escaping — escape the delimiter and the escape char ("\\," and "\\\\").
   Correct but fiddly; decode must scan char by char.
3. Optimal    — length prefix: for each string write len(s), a "#", then s.
   The decoder reads digits up to "#", then jumps exactly len characters, so
   the content is never interpreted. O(total length) both ways.

Follow-ups
----------
- Binary-safe framing: fixed 4-byte big-endian length (struct.pack(">I", n)).
- Why does the "#" inside "a#b" not confuse the decoder? It is skipped by the
  length jump, never searched for.
- Bonus: string building — always collect parts in a list and "".join them;
  repeated s += part can be O(n^2).
"""
from __future__ import annotations


def naive_encode(strs: list[str]) -> str:
    return ",".join(strs)


def naive_decode(s: str) -> list[str]:
    return s.split(",")


def encode(strs: list[str]) -> str:
    parts = []
    for s in strs:
        parts.append(f"{len(s)}#")
        parts.append(s)
    return "".join(parts)


def decode(s: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(s):
        j = s.index("#", i)            # end of the length field
        length = int(s[i:j])
        start = j + 1
        out.append(s[start:start + length])
        i = start + length             # jump over the payload
    return out


def solve(strs: list[str]) -> list[str]:
    """Round trip, used by the tests."""
    return decode(encode(strs))


def rle_encode(s: str) -> str:
    parts = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        parts.append(f"{j - i}{s[i]}")
        i = j
    return "".join(parts)


def rle_decode(s: str) -> str:
    parts = []
    count = 0
    for ch in s:
        if ch.isdigit():
            count = count * 10 + int(ch)   # multi-digit counts like "12a"
        else:
            parts.append(ch * count)
            count = 0
    return "".join(parts)


def main() -> None:
    samples = [["hi", "", "a#b"], ["12#", "#", "3"], [], [""], ["héllo", "日本語"]]
    for strs in samples:
        enc = encode(strs)
        print(f"{strs!s:<22} -> {enc!r:<22} round-trip ok: {decode(enc) == strs}")
    print("naive comma join breaks:", naive_decode(naive_encode(["a,b", "c"])), "and [] ->", naive_decode(naive_encode([])))
    for s in ["aaabcc", "abc", "", "aaaaaaaaaaaab"]:
        print(f"rle {s!r:<16} -> {rle_encode(s)!r:<10} back ok: {rle_decode(rle_encode(s)) == s}")


if __name__ == "__main__":
    main()
