"""
Exercise 03 — Navigate an Unfamiliar Codebase: Definitions and Call Sites  [Tier: ◆ Extended]
Chapter 32 · Pattern: ast.NodeVisitor index · Target time: 35 min

Problem
-------
Pair-programming rounds often start with "here is our repo, add a feature".
Your first ten minutes go on answering: where is X defined, who calls it, and
what does it call? Build that index for a set of modules given as
{module_name: source}:

- build_index(sources) -> Index with
    definitions: {qualname: [(module, line), ...]}  qualname is "func" or
                 "Class.method"; a list, because the same name can be defined in
                 several modules (or twice in one); sorted by (module, line).
    calls:       list of (caller_qualname, callee_name, module, line), where
                 callee_name is the last part of the call target: foo(), x.foo()
                 and self.foo() all record "foo". Module-level calls use caller "<module>".
- callers_of(index, name) -> sorted unique caller qualnames that call `name`.
- callees_of(index, qualname) -> sorted unique names that `qualname` calls.
- entry_points(index) -> sorted qualnames whose short name is never called
  anywhere (likely the public surface, tests or dead code: ask your pair).
  Dunder methods (__init__, __eq__, ...) are excluded: Python calls them implicitly.

Calls inside a def's decorators, default values and annotations are attributed
to that def (they are children of its ast node), although they run when the
def statement executes. Caller qualnames do not include the module.

Examples
--------
>>> idx = build_index({"m": "def a():\\n    b()\\n\\ndef b():\\n    pass\\n"})
>>> callers_of(idx, "b"), callees_of(idx, "a"), entry_points(idx)
(['a'], ['b'], ['a'])

Constraints
-----------
- Static only: never import or run the code.
- Name-based resolution (no type inference): say so when you use the answer.

Hints
-----
- Subclass ast.NodeVisitor; keep a stack of enclosing class/def names so
  "Class.method" and the caller of every call are known.
- definitions maps a qualname to a LIST of places: setdefault(qual, []).append(...).
- In visit_Call, node.func is ast.Name (foo()) or ast.Attribute (x.foo());
  call self.generic_visit(node) so nested calls are found too.
- Only FunctionDef/AsyncFunctionDef are definitions; classes only add to the stack.
- entry_points: compare each definition's short name with the set of callee names.

Follow-ups
----------
- Resolve imports (from billing import total) to cut false matches across modules.
- Methods with common names (get, run) flood callers_of: filter by module or class.
- In the room, an IDE's "go to definition" and "find usages" do this. Say out
  loud what you are looking for and why; that narration is the signal.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class Index:
    definitions: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    calls: list[tuple[str, str, str, int]] = field(default_factory=list)


class _Visitor(ast.NodeVisitor):
    def __init__(self, module: str, index: Index) -> None:
        self.module = module
        self.index = index
        self.stack: list[str] = []          # enclosing class/def names

    def _scope(self, node: ast.AST, name: str, is_def: bool) -> None:
        raise NotImplementedError("TODO")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope(node, node.name, is_def=False)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scope(node, node.name, is_def=True)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        raise NotImplementedError("TODO")


def build_index(sources: dict[str, str]) -> Index:
    raise NotImplementedError("TODO")


def callers_of(index: Index, name: str) -> list[str]:
    raise NotImplementedError("TODO")


def callees_of(index: Index, qualname: str) -> list[str]:
    raise NotImplementedError("TODO")


def entry_points(index: Index) -> list[str]:
    raise NotImplementedError("TODO")


CODEBASE = {
    "billing": '''
from pricing import unit_price, apply_discount


class Invoice:
    def __init__(self, customer, lines):
        self.customer = customer
        self.lines = lines

    def subtotal(self):
        return sum(unit_price(sku) * qty for sku, qty in self.lines)

    def total(self):
        return apply_discount(self.customer, self.subtotal())


def render(invoice):
    return f"{invoice.customer}: {invoice.total():.2f}"
''',
    "pricing": '''
PRICES = {"pen": 1.5, "pad": 4.0}


def unit_price(sku):
    return PRICES[sku]


def apply_discount(customer, amount):
    if is_vip(customer):
        return amount * 0.9
    return amount


def is_vip(customer):
    return customer.startswith("vip-")


def legacy_rate(sku):
    return unit_price(sku) * 1.2
''',
    "app": '''
from billing import Invoice, render

print(render(Invoice("vip-ada", [("pen", 2), ("pad", 1)])))
''',
}


def main() -> None:
    idx = build_index(CODEBASE)
    print("definitions:")
    for qual, places in sorted(idx.definitions.items()):
        print(f"  {qual:<20} " + ", ".join(f"{mod}:{line}" for mod, line in places))
    for name in ("unit_price", "is_vip", "total"):
        print(f"callers_of({name!r}) = {callers_of(idx, name)}")
    print("callees_of('Invoice.total') =", callees_of(idx, "Invoice.total"))
    print("callees_of('<module>') =", callees_of(idx, "<module>"))
    print("entry_points =", entry_points(idx))
    dup = build_index({"a": "def run():\n    pass\n", "b": "\n\ndef run():\n    pass\n"})
    print("same name in two modules:", dup.definitions)
    empty = build_index({})
    print("empty codebase:", empty.definitions, empty.calls, entry_points(empty))


if __name__ == "__main__":
    main()
