M = "ex03_code_navigator"


def test_demo_codebase(load):
    m = load(M)
    idx = m.build_index(m.CODEBASE)
    assert idx.definitions["Invoice.total"] == [("billing", 13)]
    assert idx.definitions["is_vip"] == [("pricing", 15)]
    assert "Invoice" not in idx.definitions                 # classes are scopes only
    assert m.callers_of(idx, "unit_price") == ["Invoice.subtotal", "legacy_rate"]
    assert m.callers_of(idx, "total") == ["render"]          # call inside an f-string
    assert m.callees_of(idx, "Invoice.total") == ["apply_discount", "subtotal"]
    assert m.callees_of(idx, "<module>") == ["Invoice", "print", "render"]
    assert m.entry_points(idx) == ["legacy_rate"]


def test_nested_functions_and_nested_calls(load):
    m = load(M)
    src = ("def outer():\n    def inner():\n        return f(g(1))\n    return inner()\n"
           "\nasync def run():\n    await outer()\n")
    idx = m.build_index({"m": src})
    assert idx.definitions == {"outer": [("m", 1)], "outer.inner": [("m", 2)], "run": [("m", 6)]}
    assert m.callees_of(idx, "outer.inner") == ["f", "g"]
    assert m.callees_of(idx, "outer") == ["inner"]
    assert m.callers_of(idx, "outer") == ["run"]
    assert m.entry_points(idx) == ["run"]
    assert sorted(line for _, callee, _, line in idx.calls if callee in ("f", "g")) == [3, 3]


def test_calls_on_expressions_and_empty(load):
    m = load(M)
    idx = m.build_index({"m": "x = (lambda: 1)()\nfuncs[0]()\nobj.a.b()\n"})
    assert [c[1] for c in idx.calls] == ["b"]               # unnamed targets are skipped
    empty = m.build_index({})
    assert m.entry_points(empty) == [] and m.callers_of(empty, "x") == []


def test_dunders_never_entry_points(load):
    m = load(M)
    idx = m.build_index({"m": "class P:\n    def __eq__(self, o):\n        return True\n"})
    assert m.entry_points(idx) == []


def test_same_name_in_two_modules_is_kept(load):
    m = load(M)
    idx = m.build_index({"b": "def run():\n    helper()\n",
                         "a": "\n\ndef run():\n    pass\n\n\ndef run():\n    pass\n"})
    assert idx.definitions["run"] == [("a", 3), ("a", 7), ("b", 1)]
    assert m.callers_of(idx, "helper") == ["run"]


def test_decorator_and_default_calls_belong_to_the_def(load):
    m = load(M)
    idx = m.build_index({"m": "@register(1)\ndef f(x=default()):\n    pass\n"})
    assert m.callees_of(idx, "f") == ["default", "register"]
    assert m.callees_of(idx, "<module>") == []


