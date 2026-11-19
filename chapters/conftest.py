"""Shared pytest fixtures for every chapter.

Tests call ``load("exKK_name")`` to import a module from the chapter's ``solutions/`` folder.
Set the environment variable ``TARGET=exercises`` to test your own work in ``exercises/`` instead.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

# Cap BLAS threads before any test imports numpy/torch: deterministic and avoids OpenBLAS
# buffer-allocation failures on many-core machines.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")


@pytest.fixture
def load(request):
    target = os.environ.get("TARGET", "solutions")
    chapter_dir = Path(request.path).resolve().parent.parent

    def _load(name: str):
        path = chapter_dir / target / f"{name}.py"
        if not path.exists():
            raise FileNotFoundError(path)
        module_name = f"{chapter_dir.name}.{target}.{name}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # needed for dataclasses / pickling
        # Let a solution import sibling helper modules from its own folder.
        sys.path.insert(0, str(path.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(str(path.parent))
        return module

    return _load
