"""
Exercise 02 — Tool Registry from Signatures and Type Hints          [Tier: ★ Core]
Chapter 41 · Pattern: introspection / registry · Target time: 30 min

Problem
-------
LLM APIs describe tools with JSON-Schema-like dictionaries. Writing them by hand duplicates the
function signature and drifts out of date. Generate them from the Python function instead:

``function_to_schema(fn)`` returns::

    {"name": fn.__name__,
     "description": <first paragraph of the docstring>,
     "parameters": {"type": "object",
                    "properties": {<param>: {<type schema>, "description": ...}},
                    "required": [<params without defaults>],
                    "additionalProperties": False}}

Type mapping: ``str``->string, ``int``->integer, ``float``->number, ``bool``->boolean,
``list[X]``->array with ``items``, ``dict``->object, ``Literal["a","b"]``->string enum,
``X | None`` / ``Optional[X]`` -> schema of X (and the parameter is not required if it has a
default). Parameter descriptions come from an ``Args:`` section in the docstring.

``ToolRegistry`` registers functions (usable as a decorator), lists schemas sorted by name, and
``call(name, arguments)`` validates arguments against the schema (unknown tool, missing required,
unexpected argument, wrong type — ``bool`` is not an ``integer``; an ``int`` is an acceptable
``number``) before invoking the function.

Examples
--------
>>> def add(a: int, b: int = 0) -> int:
...     "Add two integers."
...     return a + b
>>> function_to_schema(add)["parameters"]["required"]
['a']

Constraints
-----------
- Works with ``from __future__ import annotations`` (annotations are strings — use
  ``typing.get_type_hints``).

Approach ladder
---------------
1. Brute force — hand-written schema dicts per tool: fast to start, silently drift from code.
2. Improved   — ``inspect.signature`` + ``param.annotation``: breaks when annotations are strings.
3. Optimal    — ``typing.get_type_hints`` + ``get_origin``/``get_args`` recursion; one source of
   truth. O(p) per function for p parameters.

Hints
-----
- ``typing.get_origin(list[int]) is list``; ``get_args(list[int]) == (int,)``.
- ``X | None`` has origin ``types.UnionType``; ``Optional[X]`` has origin ``typing.Union``.
- Check ``bool`` before ``int`` — ``isinstance(True, int)`` is ``True``.

Follow-ups
----------
- How would you support nested dataclass / TypedDict parameters? (Recurse over fields.)
- Should validation coerce ``"3"`` to ``3``? (Usually no: report the error so the model learns.)
"""
from __future__ import annotations

import inspect
import types
import typing
from typing import Any, Callable, Literal, Optional

_PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object"}


class ToolError(Exception):
    """Base class for tool-dispatch errors (reported back to the model, not crashed on)."""


class ToolNotFound(ToolError):
    pass


class ToolArgumentError(ToolError):
    pass


def type_to_schema(tp: Any) -> dict:
    origin, args = typing.get_origin(tp), typing.get_args(tp)
    if tp in _PRIMITIVES:
        return {"type": _PRIMITIVES[tp]}
    if origin in (typing.Union, types.UnionType):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return type_to_schema(non_none[0])
        return {"anyOf": [type_to_schema(a) for a in non_none]}
    if origin is Literal:
        base = _PRIMITIVES.get(type(args[0]), "string")
        return {"type": base, "enum": list(args)}
    if origin is list:
        return {"type": "array", "items": type_to_schema(args[0]) if args else {}}
    if origin is dict:
        return {"type": "object"}
    raise TypeError(f"unsupported annotation: {tp!r}")


def parse_docstring(doc: str | None) -> tuple[str, dict[str, str]]:
    """Return (description, {param: description}) from a Google-style docstring."""
    if not doc:
        return "", {}
    doc = inspect.cleandoc(doc)
    description = doc.split("\n\n")[0].replace("\n", " ").strip()
    params: dict[str, str] = {}
    in_args = False
    for line in doc.splitlines():
        if line.strip() in ("Args:", "Arguments:"):
            in_args = True
            continue
        if in_args:
            if not line.startswith((" ", "\t")) and line.strip():
                break  # next section
            name, sep, text = line.strip().partition(":")
            if sep:
                params[name.split("(")[0].strip()] = text.strip()
    return description, params


def function_to_schema(fn: Callable) -> dict:
    hints = typing.get_type_hints(fn)
    description, param_docs = parse_docstring(fn.__doc__)
    properties: dict[str, dict] = {}
    required: list[str] = []
    for name, param in inspect.signature(fn).parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            raise TypeError("*args/**kwargs cannot be described to a model")
        if name not in hints:
            raise TypeError(f"parameter {name!r} of {fn.__name__} needs a type hint")
        prop = type_to_schema(hints[name])
        if name in param_docs:
            prop["description"] = param_docs[name]
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default
        properties[name] = prop
    return {
        "name": fn.__name__,
        "description": description,
        "parameters": {"type": "object", "properties": properties,
                       "required": required, "additionalProperties": False},
    }


def matches_type(value: Any, schema: dict) -> bool:
    if "anyOf" in schema:
        return any(matches_type(value, s) for s in schema["anyOf"])
    kind = schema.get("type")
    if kind == "string":
        ok = isinstance(value, str)
    elif kind == "boolean":
        ok = isinstance(value, bool)
    elif kind == "integer":
        ok = isinstance(value, int) and not isinstance(value, bool)
    elif kind == "number":
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
    elif kind == "object":
        ok = isinstance(value, dict)
    elif kind == "array":
        ok = isinstance(value, list) and all(matches_type(v, schema.get("items", {})) for v in value)
    else:
        ok = True
    if ok and "enum" in schema:
        ok = value in schema["enum"]
    return ok


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[Callable, dict]] = {}

    def register(self, fn: Callable) -> Callable:
        schema = function_to_schema(fn)
        if schema["name"] in self._tools:
            raise ValueError(f"duplicate tool {schema['name']!r}")
        self._tools[schema["name"]] = (fn, schema)
        return fn  # usable as a decorator

    def schemas(self) -> list[dict]:
        return [self._tools[n][1] for n in sorted(self._tools)]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def validate(self, name: str, arguments: dict) -> None:
        if name not in self._tools:
            raise ToolNotFound(f"unknown tool {name!r}; available: {self.names()}")
        params = self._tools[name][1]["parameters"]
        missing = [p for p in params["required"] if p not in arguments]
        if missing:
            raise ToolArgumentError(f"{name}: missing required argument(s) {missing}")
        extra = sorted(set(arguments) - set(params["properties"]))
        if extra:
            raise ToolArgumentError(f"{name}: unexpected argument(s) {extra}")
        for arg, value in arguments.items():
            schema = params["properties"][arg]
            if not matches_type(value, schema):
                want = schema.get("enum") or schema.get("type") or "anyOf"
                raise ToolArgumentError(f"{name}: argument {arg!r}={value!r} is not {want}")

    def call(self, name: str, arguments: dict) -> Any:
        self.validate(name, arguments)
        return self._tools[name][0](**arguments)


# ---- demo tools -------------------------------------------------------------------------------
def get_weather(city: str, unit: Literal["celsius", "fahrenheit"] = "celsius") -> dict:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "Oslo".
        unit: Temperature unit for the answer.
    """
    temps_c = {"Oslo": 4.0, "Lisbon": 19.0}
    t = temps_c.get(city, 15.0)
    return {"city": city, "temp": t if unit == "celsius" else round(t * 9 / 5 + 32, 1), "unit": unit}


def search_docs(query: str, tags: list[str], limit: Optional[int] = 3) -> list[str]:
    """Search internal documentation.

    Args:
        query: Free-text query.
        tags: Restrict results to these tags.
        limit: Maximum number of results.
    """
    return [f"doc:{query}:{t}" for t in sorted(tags)][: limit or 3]


def build_demo_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(get_weather)
    registry.register(search_docs)
    return registry


def main() -> None:
    import json

    registry = build_demo_registry()

    print("== generated schemas")
    for schema in registry.schemas():
        print(json.dumps(schema, indent=2))
    print("== calls")
    cases = [
        ("get_weather", {"city": "Oslo"}),
        ("get_weather", {"city": "Lisbon", "unit": "fahrenheit"}),
        ("search_docs", {"query": "retry", "tags": ["sre", "api"], "limit": 1}),
        ("get_weather", {}),
        ("get_weather", {"city": "Oslo", "unit": "kelvin"}),
        ("get_weather", {"city": "Oslo", "country": "NO"}),
        ("search_docs", {"query": "x", "tags": ["a"], "limit": True}),
        ("send_email", {"to": "a@b.c"}),
    ]
    for name, args in cases:
        try:
            print(f"  {name}({args}) -> {registry.call(name, args)}")
        except ToolError as exc:
            print(f"  {name}({args}) -> {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
