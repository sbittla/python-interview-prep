"""
Exercise 02 — Pre-Submission Checker for a Take-Home               [Tier: ◆ Extended]
Chapter 32 · Pattern: static checks with ast + tokenize · Target time: 40 min

Problem
-------
Reviewers skim a take-home for the same things before they read any logic.
Write check_project(root, max_func_lines=40) that inspects a project folder and
returns one Finding(check, passed, detail) per check, in this fixed order:

1. readme      README.md exists and has headings (any level, case-insensitive)
               containing "how to run", "assumptions" and "trade-offs".
               Lines inside ``` code fences are not headings.
2. tests       at least one tests/test_*.py file exists.
3. annotations every public function (name not starting with "_") in a non-test
               .py file annotates all parameters except self/cls, and its return.
4. func_size   no function in a non-test .py file is longer than max_func_lines
               (end_lineno - lineno + 1, decorators excluded).
5. leftovers   no breakpoint() or pdb.set_trace() call, no `import pdb` or
               `from pdb import ...`, no bare `except:`, no "TODO"/"FIXME"
               comment, no syntax error and no non-UTF-8 file, in any .py file.

Each problem is a (path, line, what) triple; line 0 means "whole file". detail
is "ok" when passed, otherwise the problems sorted by (path, line, what) and
shown as "path:line what" (or "path what" for line 0), joined by "; ". Paths
are relative to root, with "/". Folders named .git, .venv, venv, build, dist,
__pycache__ or node_modules are skipped.

Examples
--------
>>> [f.check for f in check_project(Path("."))][:2]   # doctest: +SKIP
['readme', 'tests']

Constraints
-----------
- Never import or execute the submitted code: parse it with ast.
- Deterministic: walk files in sorted order.

Hints
-----
- ast.parse each file; ast.walk finds FunctionDef / AsyncFunctionDef, Call
  (breakpoint() and pdb.set_trace()), Import, ImportFrom (module == "pdb") and
  ExceptHandler (type is None for a bare except).
- Comments are not in the AST: use tokenize.generate_tokens and look at
  COMMENT tokens.
- Keep problems as (path, line, what) tuples and sort the TUPLES: sorting the
  formatted strings puts "x.py:11" before "x.py:9".
- README: toggle an in_fence flag on lines starting with ``` .
- read_text(encoding="utf-8") raises UnicodeDecodeError on other encodings.
- Function length: node.end_lineno - node.lineno + 1.

Follow-ups
----------
- These are the checks a linter/type-checker (ruff, mypy) would do better in
  a real project; why still useful? (zero setup, one command, explains itself)
- Limits: aliases (`import pdb as p; p.set_trace()` is caught only as the
  import), Setext README headings (underlined with ===) and nested
  ~~~ fences are not recognised.
- Make each check a function in a registry so new checks need no edits to the core.
"""
from __future__ import annotations

import ast
import io
import tempfile
import tokenize
from dataclasses import dataclass
from pathlib import Path

REQUIRED_HEADINGS = ("how to run", "assumptions", "trade-offs")
SKIP_DIRS = {".git", ".venv", "venv", "build", "dist", "__pycache__", "node_modules"}
Problem = tuple[str, int, str]          # (relative path, line or 0, what)


@dataclass(frozen=True)
class Finding:
    check: str
    passed: bool
    detail: str


def _finding(check: str, problems: list[Problem]) -> Finding:
    raise NotImplementedError("TODO")


def check_readme(root: Path) -> list[Problem]:
    raise NotImplementedError("TODO")


def is_test_file(rel: str) -> bool:
    return rel.startswith("tests/") or Path(rel).name.startswith("test_")


def python_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py")
                  if not SKIP_DIRS.intersection(p.relative_to(root).parts[:-1]))


def functions(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def missing_annotations(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    raise NotImplementedError("TODO")


def _debug_call(node: ast.Call) -> str | None:
    raise NotImplementedError("TODO")


def leftovers(tree: ast.AST, source: str) -> list[tuple[int, str]]:
    raise NotImplementedError("TODO")


def check_project(root: Path, max_func_lines: int = 40) -> list[Finding]:
    raise NotImplementedError("TODO")


# --- demo projects -------------------------------------------------------------
CLEAN = {
    "README.md": "# Tool\n## How to run\n`python -m tool`\n## Assumptions\n- UTF-8\n"
                 "## Trade-offs\n- in-memory\n",
    "tool/core.py": "def total(xs: list[int]) -> int:\n    return sum(xs)\n\n\n"
                    "def _helper(x):\n    return x\n",
    "tests/test_core.py": "from tool.core import total\n\n\ndef test_total():\n"
                          "    assert total([1, 2]) == 3\n",
}
SLOPPY = {
    "README.md": "# Tool\nRun it.\n## Assumptions\n- none\n",
    "tool/core.py": ("import pdb\n\n\ndef total(xs):\n    # TODO handle None\n"
                     "    try:\n        return sum(xs)\n    except:\n        return 0\n\n\n"
                     "def long_one(n: int) -> int:\n" + "    n += 1\n" * 45 + "    return n\n"),
    ".venv/lib/site.py": "def vendored(x):\n    breakpoint()\n",       # skipped
}


def build(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def report(name: str, findings: list[Finding]) -> None:
    passed = sum(f.passed for f in findings)
    print(f"{name}: {passed}/{len(findings)} checks pass")
    for f in findings:
        print(f"  [{'x' if f.passed else ' '}] {f.check:<11} {f.detail}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        report("clean", check_project(build(Path(tmp) / "clean", CLEAN)))
        report("sloppy", check_project(build(Path(tmp) / "sloppy", SLOPPY)))
        broken = build(Path(tmp) / "broken", {"tool/bad.py": "def f(:\n    pass\n"})
        (broken / "tool" / "latin1.py").write_bytes(b"name = '\xe9'\n")
        report("broken", check_project(broken))


if __name__ == "__main__":
    main()
