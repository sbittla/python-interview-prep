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

Approach ladder
---------------
1. Brute force — eyeball the repo the night before; you miss the one
   unannotated helper and the forgotten breakpoint().
2. Improved   — grep / regex: fast, but "def f(" inside a string or a TODO in a
   docstring gives false positives, and multi-line signatures are missed.
3. Optimal    — ast for code facts (annotations, sizes, calls, imports, except
   clauses), tokenize for comments; O(total source size).

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
    shown = [f"{rel}:{line} {what}" if line else f"{rel} {what}"
             for rel, line, what in sorted(problems)]          # numeric line order
    return Finding(check, not problems, "; ".join(shown) or "ok")


def check_readme(root: Path) -> list[Problem]:
    readme = root / "README.md"
    if not readme.exists():
        return [("README.md", 0, "missing")]
    headings, in_fence = [], False
    for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif line.startswith("#") and not in_fence:
            headings.append(line.lstrip("#").strip().lower())
    return [("README.md", 0, f"no '{want}' heading") for want in REQUIRED_HEADINGS
            if not any(want in h for h in headings)]


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
    a = fn.args
    params = a.posonlyargs + a.args + a.kwonlyargs
    params += [p for p in (a.vararg, a.kwarg) if p is not None]
    unannotated = [p for p in params if p.annotation is None and p.arg not in ("self", "cls")]
    return bool(unannotated) or fn.returns is None


def _debug_call(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name) and f.id == "breakpoint":
        return "breakpoint()"
    if (isinstance(f, ast.Attribute) and f.attr == "set_trace"
            and isinstance(f.value, ast.Name) and f.value.id == "pdb"):
        return "pdb.set_trace()"
    return None


def leftovers(tree: ast.AST, source: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _debug_call(node):
            found.append((node.lineno, _debug_call(node)))
        elif isinstance(node, ast.Import) and any(al.name == "pdb" for al in node.names):
            found.append((node.lineno, "import pdb"))
        elif isinstance(node, ast.ImportFrom) and node.module == "pdb":
            found.append((node.lineno, "from pdb import"))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            found.append((node.lineno, "bare except"))
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT and ("TODO" in tok.string or "FIXME" in tok.string):
            found.append((tok.start[0], "TODO comment"))
    return found


def check_project(root: Path, max_func_lines: int = 40) -> list[Finding]:
    unannotated: list[Problem] = []
    too_long: list[Problem] = []
    debris: list[Problem] = []
    has_tests = any((root / "tests").glob("test_*.py"))
    for path in python_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            debris.append((rel, 0, "not UTF-8"))
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            debris.append((rel, exc.lineno or 0, "syntax error"))
            continue
        debris += [(rel, line, what) for line, what in leftovers(tree, source)]
        if is_test_file(rel):
            continue
        for fn in functions(tree):
            if not fn.name.startswith("_") and missing_annotations(fn):
                unannotated.append((rel, fn.lineno, fn.name))
            if fn.end_lineno - fn.lineno + 1 > max_func_lines:
                too_long.append((rel, fn.lineno, fn.name))
    return [
        _finding("readme", check_readme(root)),
        _finding("tests", [] if has_tests else [("tests/", 0, "has no test_*.py")]),
        _finding("annotations", unannotated),
        _finding("func_size", too_long),
        _finding("leftovers", debris),
    ]


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
