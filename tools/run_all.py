"""Run every solution file and capture its output.

Usage:
    python tools/run_all.py                 # all chapters
    python tools/run_all.py --chapter 09    # one chapter (repeatable: --chapter 09 --chapter 10)
    python tools/run_all.py --check         # fail if any output differs from the saved file

For each ``chapters/chNN_*/solutions/exKK_*.py`` the script runs it with the current interpreter
(cwd = the chapter folder), feeds ``inputs/exKK_*.txt`` to stdin when present, and writes
stdout to ``outputs/exKK_*.txt``. A non-zero exit, a timeout, or any stderr traceback is a failure.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "chapters"
TIMEOUT_S = 120


def chapters(selected: list[str]) -> list[Path]:
    dirs = sorted(p for p in CODE.glob("ch[0-9][0-9]_*") if p.is_dir())
    dirs += sorted(p for p in CODE.glob("appendix_*") if p.is_dir())
    if selected:
        wanted = {s.zfill(2) for s in selected}
        dirs = [d for d in dirs if d.name[2:4] in wanted or d.name in selected]
    return dirs


def run_solution(path: Path) -> tuple[bool, str, str]:
    chapter_dir = path.parent.parent
    stdin_file = chapter_dir / "inputs" / f"{path.stem}.txt"
    stdin = stdin_file.read_text(encoding="utf-8") if stdin_file.exists() else ""
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    env.setdefault("OPENBLAS_NUM_THREADS", "4")  # many-core machines can fail OpenBLAS init
    env.setdefault("OMP_NUM_THREADS", "4")
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            input=stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=chapter_dir,
            env=env,
            timeout=TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return False, "", f"TIMEOUT after {TIMEOUT_S}s"
    ok = proc.returncode == 0
    return ok, proc.stdout.replace("\r\n", "\n"), proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", action="append", default=[])
    parser.add_argument("--check", action="store_true", help="compare with saved outputs")
    args = parser.parse_args()

    total = failed = changed = 0
    for chapter_dir in chapters(args.chapter):
        sols = sorted([*(chapter_dir / "solutions").glob("ex*.py"), *(chapter_dir / "solutions").glob("lab*.py")])
        if not sols:
            continue
        out_dir = chapter_dir / "outputs"
        out_dir.mkdir(exist_ok=True)
        print(f"== {chapter_dir.name} ({len(sols)} solutions)")
        for sol in sols:
            total += 1
            ok, out, err = run_solution(sol)
            out_file = out_dir / f"{sol.stem}.txt"
            if not ok:
                failed += 1
                print(f"   FAIL {sol.name}\n{err.strip()[-2000:]}")
                continue
            if args.check:
                saved = out_file.read_text(encoding="utf-8") if out_file.exists() else None
                if saved != out:
                    changed += 1
                    print(f"   DIFF {sol.name}")
                    continue
            else:
                out_file.write_text(out, encoding="utf-8", newline="\n")
            print(f"   ok   {sol.name}")
    print(f"\n{total} solutions, {failed} failed" + (f", {changed} differ" if args.check else ""))
    return 1 if failed or changed else 0


if __name__ == "__main__":
    sys.exit(main())
