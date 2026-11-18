"""Chapter 31 helper (not an exercise): run a file's embedded pytest suite in-process.

Several Chapter 31 solutions contain their own pytest test functions. Their ``main()`` calls
``run_embedded_tests(__file__)``, which runs real pytest on that file with the terminal reporter
switched off, records each test outcome with a tiny plugin, and returns deterministic
``(test_id, outcome)`` pairs. No timings, paths or memory addresses are printed.
"""
from __future__ import annotations

from pathlib import Path

import pytest


class _Recorder:
    """A minimal pytest plugin: remember the outcome of every test, in run order."""

    def __init__(self) -> None:
        self.results: list[tuple[str, str]] = []

    def pytest_collectreport(self, report) -> None:  # noqa: ANN001 - pytest hook
        if report.failed:
            self.results.append((f"<collection of {Path(str(report.nodeid)).name}>", "error"))

    def pytest_runtest_logreport(self, report) -> None:  # noqa: ANN001 - pytest hook
        name = report.nodeid.split("::", 1)[-1]
        if report.when == "call":
            self.results.append((name, report.outcome))
        elif report.when == "setup" and report.outcome == "skipped":
            self.results.append((name, "skipped"))
        elif report.failed:  # an error inside a fixture's setup or teardown
            self.results.append((name, f"error in {report.when}"))


def run_embedded_tests(path: str | Path, *extra_args: str) -> list[tuple[str, str]]:
    recorder = _Recorder()
    pytest.main(
        [str(path), "-o", "addopts=", "--import-mode=importlib", "-p", "no:terminal",
         "-p", "no:cacheprovider", *extra_args],
        plugins=[recorder],
    )
    return recorder.results


LABELS = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}


def print_results(results: list[tuple[str, str]], title: str = "Embedded test suite") -> None:
    print(f"{title}:")
    for name, outcome in results:
        print(f"  {LABELS.get(outcome, 'ERROR')}  {name}")
    passed = sum(outcome == "passed" for _, outcome in results)
    print(f"  {passed}/{len(results)} passed")
