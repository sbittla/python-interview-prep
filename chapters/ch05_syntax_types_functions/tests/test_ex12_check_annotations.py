from __future__ import annotations

from typing import Any, Literal, Optional

import pytest


def area(w: int, h: int = 1, label: str | None = None) -> int:
    return w * h


def mixed(xs: list[int], scale: float, name, flag: Optional[bool] = None, *, extra: dict[str, int] | None = None):
    return None


def test_examples(load):
    m = load("ex12_check_annotations")
    assert m.solve(area, 3, "4") == ["h: expected int, got str"]
    assert m.solve(area, 3, 4, label=None) == []


def test_bool_is_not_int_and_unions(load):
    m = load("ex12_check_annotations")
    assert m.solve(area, True, 2.5, label=7) == [
        "h: expected int, got float", "label: expected str | None, got int", "w: expected int, got bool"]


def test_generics_float_and_unannotated(load):
    m = load("ex12_check_annotations")
    assert m.solve(mixed, [1], 2, object()) == []      # an int is accepted for float
    errors = m.solve(mixed, (1,), "s", 1, flag=1, extra=[])
    assert [e.split(":")[0] for e in errors] == ["extra", "flag", "scale", "xs"]
    assert "scale: expected float, got str" in errors
    assert "xs: expected list[int], got tuple" in errors


def test_binding_errors(load):
    m = load("ex12_check_annotations")
    with pytest.raises(TypeError):
        m.solve(area, 1, 2, 3, 4)
    with pytest.raises(TypeError):
        m.solve(area)


def tagged(*names: str, mode: Literal["a", "w"] = "a", **meta: int) -> None:
    return None


def test_varargs_checked_per_element(load):
    m = load("ex12_check_annotations")
    assert m.solve(tagged, "x", "y", size=3) == []
    assert m.solve(tagged, "x", 3, flag=True) == [
        "meta['flag']: expected int, got bool", "names[1]: expected str, got int"]


def test_literal_and_special_forms(load):
    m = load("ex12_check_annotations")
    assert m.solve(tagged, mode="w") == []
    assert m.solve(tagged, mode="r") == ["mode: expected Literal['a', 'w'], got str"]

    def one(x: Literal[1]) -> None:
        return None
    assert m.solve(one, True) == ["x: expected Literal[1], got bool"]   # True == 1 but not a 1

    def anything(x: Any, y) -> None:
        return None
    assert m.solve(anything, object(), 5) == []
