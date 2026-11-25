import pytest

M = "ex02_submission_checker"


def project(m, tmp_path, **overrides):
    files = dict(m.CLEAN)
    files.update(overrides)
    files = {k: v for k, v in files.items() if v is not None}
    return m.check_project(m.build(tmp_path, files))


def failing(findings):
    return {f.check: f.detail for f in findings if not f.passed}


def test_clean_project_passes_everything(load, tmp_path):
    m = load(M)
    findings = project(m, tmp_path)
    assert [f.check for f in findings] == ["readme", "tests", "annotations", "func_size",
                                           "leftovers"]
    assert all(f.passed and f.detail == "ok" for f in findings)


@pytest.mark.parametrize("overrides, check, detail", [
    ({"README.md": None}, "readme", "README.md missing"),
    ({"README.md": "# T\n## how to RUN\n### Assumptions\n"}, "readme",
     "README.md no 'trade-offs' heading"),
    ({"README.md": "# T\n## How to run\n```bash\n# Assumptions\n# Trade-offs\n```\n"},
     "readme", "README.md no 'assumptions' heading; README.md no 'trade-offs' heading"),
    ({"tests/test_core.py": None}, "tests", "tests/ has no test_*.py"),
    ({"tool/x.py": "def f(a: int, b) -> int:\n    return a\n"}, "annotations", "tool/x.py:1 f"),
    ({"tool/x.py": "class C:\n    def m(self, a: int):\n        return a\n"}, "annotations",
     "tool/x.py:2 m"),
    ({"tool/x.py": "def f(*args) -> None:\n    pass\n"}, "annotations", "tool/x.py:1 f"),
    ({"tool/x.py": "def f(a: int, /, *, b) -> None:\n    pass\n"}, "annotations",
     "tool/x.py:1 f"),
    ({"tool/x.py": "def f() -> None:\n    breakpoint()\n"}, "leftovers",
     "tool/x.py:2 breakpoint()"),
    ({"tool/x.py": "import os, pdb\n"}, "leftovers", "tool/x.py:1 import pdb"),
    ({"tool/x.py": "from pdb import set_trace\n"}, "leftovers", "tool/x.py:1 from pdb import"),
    ({"tool/x.py": "import pdb\npdb.set_trace()\n"}, "leftovers",
     "tool/x.py:1 import pdb; tool/x.py:2 pdb.set_trace()"),
    ({"tool/x.py": "try:\n    pass\nexcept:\n    pass\n"}, "leftovers", "tool/x.py:3 bare except"),
    ({"tool/x.py": "x = 1  # FIXME later\n"}, "leftovers", "tool/x.py:1 TODO comment"),
    ({"tool/x.py": "# TODO: tidy\nx = 1\n"}, "leftovers", "tool/x.py:1 TODO comment"),
    ({"tool/x.py": "def f(:\n"}, "leftovers", "tool/x.py:1 syntax error"),
])
def test_each_flaw_fails_exactly_its_check(load, tmp_path, overrides, check, detail):
    m = load(M)
    assert failing(project(m, tmp_path, **overrides)) == {check: detail}


def test_not_fooled_by_strings_private_or_test_code(load, tmp_path):
    m = load(M)
    findings = project(m, tmp_path, **{
        "tool/x.py": 's = "TODO breakpoint() import pdb"\n\n\ndef _p(a):\n    return a\n',
        "tests/test_more.py": "def helper(a):\n    return a\n",
    })
    assert failing(findings) == {}


def test_valid_code_is_not_flagged(load, tmp_path):
    m = load(M)
    src = ("class C:\n    def m(self, a: int) -> int:\n        try:\n            return a\n"
           "        except ValueError:\n            return 0\n")
    assert failing(project(m, tmp_path, **{"tool/x.py": src})) == {}


def test_problems_sort_by_line_number_not_text(load, tmp_path):
    m = load(M)
    src = "def b(x):\n    pass\n" + "\n" * 6 + "def a(y):\n    pass\n" + "\n" * 2 + "def c(z):\n    pass\n"
    findings = project(m, tmp_path, **{"tool/z.py": src})
    assert failing(findings) == {"annotations": "tool/z.py:1 b; tool/z.py:9 a; tool/z.py:13 c"}


def test_skipped_dirs_and_non_utf8(load, tmp_path):
    m = load(M)
    root = m.build(tmp_path, dict(m.CLEAN, **{".venv/x.py": "breakpoint()\n",
                                               "build/lib/y.py": "def f(x):\n    pass\n"}))
    assert failing(m.check_project(root)) == {}
    (root / "tool" / "latin1.py").write_bytes(b"name = '\xe9'\n")
    assert failing(m.check_project(root)) == {"leftovers": "tool/latin1.py not UTF-8"}


def test_func_size_limit(load, tmp_path):
    m = load(M)
    body = "def f() -> int:\n" + "    x = 1\n" * 4 + "    return x\n"     # 6 lines
    root = m.build(tmp_path, dict(m.CLEAN, **{"tool/x.py": body}))
    assert failing(m.check_project(root, max_func_lines=6)) == {}
    assert failing(m.check_project(root, max_func_lines=5)) == {"func_size": "tool/x.py:1 f"}
