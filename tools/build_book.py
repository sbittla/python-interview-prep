"""Concatenate the manuscript into a single BOOK.md with a generated table of contents.

Usage: python tools/build_book.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "manuscript"

PARTS = {
    1: "Part 0 — Orientation and Strategy",
    5: "Part I — Python Essentials (Fast Track)",
    9: "Part II — Core Data Structures and Patterns",
    18: "Part III — Algorithmic Techniques",
    23: "Part IV — Intermediate and Advanced Python",
    29: "Part V — Practical Engineering Rounds",
    33: "Part VI — Data and ML Coding Track",
    38: "Part VII — GenAI and LLM Engineering Track",
    44: "Part VIII — Practice and Assessment",
}


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s+", "-", text.strip())


def main() -> None:
    front = MS / "00_front_matter.md"
    chapters = sorted(MS.glob("ch[0-9][0-9]_*.md"))
    appendices = sorted(MS.glob("appendix_*.md"))

    toc, body = ["# Table of Contents", ""], []
    if front.exists():
        body.append(front.read_text(encoding="utf-8"))
    for ch in chapters:
        num = int(ch.name[2:4])
        if num in PARTS:
            toc.append(f"\n**{PARTS[num]}**\n")
            body.append(f"\n\n---\n\n# {PARTS[num]}\n")
        text = ch.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), ch.stem)
        toc.append(f"- [{title}](#{slugify(title)})")
        body.append("\n\n---\n\n" + text)
    if appendices:
        toc.append("\n**Appendices**\n")
        for ap in appendices:
            text = ap.read_text(encoding="utf-8")
            title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), ap.stem)
            toc.append(f"- [{title}](#{slugify(title)})")
            body.append("\n\n---\n\n" + text)

    out = ROOT / "BOOK.md"
    out.write_text("\n".join(toc) + "\n\n" + "\n".join(body), encoding="utf-8", newline="\n")
    words = len(out.read_text(encoding="utf-8").split())
    print(f"Wrote {out.name}: {len(chapters)} chapters, {len(appendices)} appendices, ~{words:,} words")


if __name__ == "__main__":
    main()
