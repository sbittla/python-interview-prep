"""
Exercise 05 — Files with pathlib: text, bytes and encodings    [Tier: ★ Core]
Chapter 26 · Pattern: safe file handling · Target time: 20 min

Problem
-------
Implement four helpers and exercise them inside a ``tempfile.TemporaryDirectory()``:

1. ``byte_lengths(text)`` -> ``{"chars": ..., "utf-8": ..., "utf-16": ..., "latin-1": ...}``
   giving the character count and the encoded size in bytes (``None`` if the text cannot be encoded
   in that codec).
2. ``build_tree(root, files)`` creates every relative path in ``files`` (a dict path -> text) under
   ``root`` (creating parent folders) and returns the sorted list of *relative POSIX* paths of all
   files below ``root``.
3. ``count_lines(path)`` counts lines by *streaming* the file (never ``read()`` the whole file).
4. ``read_text_fallback(path)`` decodes as UTF-8, and if that fails falls back to Latin-1,
   returning ``(text, encoding_used)``.

Examples
--------
>>> byte_lengths("café")
{'chars': 4, 'utf-8': 5, 'utf-16': 10, 'latin-1': 4}

Constraints
-----------
- Always pass ``encoding=`` when opening text files (the platform default differs: Windows may not
  use UTF-8 unless UTF-8 mode is on).
- Never print absolute temp paths (they differ every run).

Approach ladder
---------------
1. Brute force — ``open(path).read().split("\\n")`` to count lines: loads the whole file and relies on
   the platform encoding.
2. Improved   — ``with open(path, encoding="utf-8")`` so the file is closed and decoded predictably.
3. Optimal    — iterate the file object line by line (O(1) memory) and use ``pathlib`` for path
   manipulation instead of string concatenation.

Hints
-----
- ``Path.rglob("*")`` walks recursively; filter with ``p.is_file()``; ``p.relative_to(root)``
  and ``.as_posix()`` give stable, OS-independent strings.
- ``"utf-16"`` adds a 2-byte BOM.
- ``bytes.decode`` raises ``UnicodeDecodeError`` (a ``ValueError`` subclass).

Follow-ups
----------
- What does ``newline=""`` do for CSV files? (Disables newline translation so the csv module can
  handle ``\\r\\n`` itself.)
- How do you write a file atomically? (See exercise 12.)
"""
from __future__ import annotations

import tempfile
from pathlib import Path


def byte_lengths(text: str) -> dict:
    out: dict = {"chars": len(text)}
    for codec in ("utf-8", "utf-16", "latin-1"):
        try:
            out[codec] = len(text.encode(codec))
        except UnicodeEncodeError:
            out[codec] = None
    return out


def build_tree(root: Path, files: dict[str, str]) -> list[str]:
    root = Path(root)
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def count_lines(path: Path) -> int:
    count = 0
    with open(path, encoding="utf-8") as fh:     # file objects iterate lazily, line by line
        for _ in fh:
            count += 1
    return count


def read_text_fallback(path: Path) -> tuple[str, str]:
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("latin-1"), "latin-1"   # latin-1 can decode any byte sequence


def main() -> None:
    print("== byte_lengths ==")
    for text in ["hello", "café", "naïve €5", "日本"]:
        print(f"{text!r:<12} {byte_lengths(text)}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        print("\n== build_tree ==")
        tree = build_tree(root, {
            "notes/todo.txt": "buy milk\nwrite chapter\nship it\n",
            "notes/archive/2025.txt": "old\n",
            "data/readme.md": "# data\n",
        })
        for rel in tree:
            print("  ", rel)

        todo = root / "notes" / "todo.txt"
        print("\n== path anatomy ==")
        print("name:", todo.name, "| stem:", todo.stem, "| suffix:", todo.suffix)
        print("with_suffix:", todo.with_suffix(".md").name)
        print("parent name:", todo.parent.name, "| exists:", todo.exists())
        print("txt files:", sorted(p.name for p in root.rglob("*.txt")))

        print("\n== count_lines (streaming) ==")
        print("todo.txt lines:", count_lines(todo))

        print("\n== binary vs text ==")
        legacy = root / "legacy.txt"
        legacy.write_bytes("café".encode("latin-1"))     # a file from an old system
        print("raw bytes:", legacy.read_bytes())
        print("fallback decode:", read_text_fallback(legacy))
        print("replace errors:", legacy.read_text(encoding="utf-8", errors="replace"))
        modern = root / "modern.txt"
        modern.write_text("café", encoding="utf-8")
        print("raw bytes:", modern.read_bytes())
        print("fallback decode:", read_text_fallback(modern))

        print("\n== newline translation ==")
        crlf = root / "crlf.txt"
        crlf.write_bytes(b"a\r\nb\r\n")
        print("text mode :", repr(crlf.read_text(encoding="utf-8")))
        with open(crlf, encoding="utf-8", newline="") as fh:
            print("newline='':", repr(fh.read()))

        print("\n== missing file ==")
        try:
            (root / "nope.txt").read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            print("FileNotFoundError errno:", exc.errno, "| is OSError:", isinstance(exc, OSError))
    print("temp dir removed:", not root.exists())


if __name__ == "__main__":
    main()
