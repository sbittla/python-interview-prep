import pytest


@pytest.mark.parametrize("name", ["Transaction", "transaction"])
def test_commit_and_rollback(load, name):
    manager = getattr(load("ex10_context_managers"), name)
    store = {"a": 1, "b": 2}
    alias = store
    with manager(store) as s:
        assert s is store
        s["c"] = 3
    assert store == {"a": 1, "b": 2, "c": 3}
    with pytest.raises(KeyError):
        with manager(store) as s:
            s["a"] = 100
            del s["b"]
            s["new"] = 0
            raise KeyError("boom")
    assert alias is store and store == {"a": 1, "b": 2, "c": 3}


@pytest.mark.parametrize("name", ["Transaction", "transaction"])
def test_rollback_on_base_exception(load, name):
    manager = getattr(load("ex10_context_managers"), name)
    store = {"x": 1}
    with pytest.raises(KeyboardInterrupt):
        with manager(store) as s:
            s.clear()
            raise KeyboardInterrupt
    assert store == {"x": 1}


def test_temp_attr_restores_existing_and_missing(load):
    m = load("ex10_context_managers")

    class Cfg:
        pass

    cfg = Cfg()
    cfg.level = 1
    with pytest.raises(RuntimeError):
        with m.temp_attr(cfg, "level", 9):
            assert cfg.level == 9
            raise RuntimeError
    assert cfg.level == 1
    with m.temp_attr(cfg, "extra", "on") as obj:
        assert obj is cfg and cfg.extra == "on"
    assert not hasattr(cfg, "extra")


def test_temp_attr_buggy_leaks(load):
    m = load("ex10_context_managers")

    class Cfg:
        debug = False

    cfg = Cfg()
    with m.temp_attr_buggy(cfg, "debug", True):
        pass
    assert cfg.debug is False                  # fine on the happy path
    with pytest.raises(RuntimeError):
        with m.temp_attr_buggy(cfg, "debug", True):
            raise RuntimeError
    assert cfg.debug is True                   # leaked on error


def test_suppress(load):
    m = load("ex10_context_managers")
    with m.Suppress(LookupError):
        {}["missing"]                          # KeyError is a LookupError
    with m.Suppress(KeyError, IndexError):
        [][0]
    with m.Suppress(KeyError):
        pass
    with pytest.raises(ValueError):
        with m.Suppress(KeyError):
            int("x")
    assert not m.Suppress(KeyError).__exit__(None, None, None)


def test_temp_attr_class_attribute_not_shadowed(load):
    m = load("ex10_context_managers")

    class Cfg:
        debug = False

    cfg = Cfg()
    with m.temp_attr(cfg, "debug", True):
        assert cfg.debug is True and Cfg.debug is False
    assert "debug" not in vars(cfg)            # no instance attribute left behind
    Cfg.debug = "changed"
    assert cfg.debug == "changed"
