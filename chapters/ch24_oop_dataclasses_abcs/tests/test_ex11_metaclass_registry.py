import pytest


@pytest.fixture
def m(load):
    return load("ex11_metaclass_registry")      # fresh module => fresh registries


@pytest.mark.parametrize("base_name, registry_owner", [
    ("MetaPlugin", "PluginMeta"), ("HookPlugin", "HookPlugin")])
def test_registration(m, base_name, registry_owner):
    base = getattr(m, base_name)
    registry = getattr(m, registry_owner).registry
    assert registry == {}

    class Upper(base):
        name = "upper"

        def run(self, x):
            return x.upper()

    m.make_plugin_class(base, "double", lambda x: x * 2)
    assert sorted(registry) == ["double", "upper"] and registry["upper"] is Upper
    assert m.run_all(registry, "ab") == {"double": "abab", "upper": "AB"}
    assert list(m.run_all(registry, "x")) == ["double", "upper"]


@pytest.mark.parametrize("base_name", ["MetaPlugin", "HookPlugin"])
@pytest.mark.parametrize("ns", [{}, {"name": ""}, {"name": 3}])
def test_missing_name_rejected_at_definition(m, base_name, ns):
    base = getattr(m, base_name)
    with pytest.raises(TypeError):
        type(base)("Bad", (base,), dict(ns))


@pytest.mark.parametrize("base_name", ["MetaPlugin", "HookPlugin"])
def test_duplicate_rejected(m, base_name):
    base = getattr(m, base_name)
    m.make_plugin_class(base, "same", str)
    with pytest.raises(TypeError, match="duplicate"):
        m.make_plugin_class(base, "same", str)


@pytest.mark.parametrize("base_name", ["MetaPlugin", "HookPlugin"])
def test_inherited_name_is_not_enough(m, base_name):
    base = getattr(m, base_name)
    A = m.make_plugin_class(base, "a", str)
    # B inherits name "a" but declares none: the error must be "must define", not "duplicate"
    with pytest.raises(TypeError, match="must define"):
        type(base)("B", (A,), {})


def test_types(m):
    P = m.make_plugin_class(m.MetaPlugin, "p", str)
    H = m.make_plugin_class(m.HookPlugin, "h", str)
    assert type(P) is m.PluginMeta and type(H) is type
    assert P.__name__ == "PPlugin" and issubclass(H, m.HookPlugin)


def test_decorator_rung_is_opt_in(m):
    @m.register_plugin
    class Plain:
        name = "plain"

    class Forgotten:
        name = "forgotten"

    assert sorted(m.DECORATED) == ["plain"]
