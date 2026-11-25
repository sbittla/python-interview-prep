import pytest


@pytest.fixture
def m(load):
    return load("ex06_alt_constructors")


@pytest.mark.parametrize("text, rgb", [
    ("#1e90ff", (30, 144, 255)), ("1E90FF", (30, 144, 255)),
    ("#fff", (255, 255, 255)), ("abc", (170, 187, 204)), ("#000000", (0, 0, 0)),
])
def test_from_hex(m, text, rgb):
    assert m.Color.from_hex(text).rgb() == rgb


@pytest.mark.parametrize("text", ["", "#12345", "#ggg", "#1234567", "##fff"])
def test_bad_hex(m, text):
    with pytest.raises(ValueError):
        m.Color.from_hex(text)


def test_from_name_and_repr(m):
    assert repr(m.Color.from_name("TOMATO")) == "Color(255, 99, 71)"
    with pytest.raises(KeyError):
        m.Color.from_name("chartreuse")


def test_to_hex_round_trip(m):
    for rgb in [(0, 0, 0), (1, 2, 3), (255, 128, 15)]:
        c = m.Color(*rgb)
        assert m.Color.from_hex(c.to_hex()) == c and len(c.to_hex()) == 7


def test_blend_is_static(m):
    assert m.Color.blend((255, 0, 0), (0, 0, 255)) == (128, 0, 128)
    assert m.Color(0, 0, 0).blend((1, 1, 1), (2, 2, 2)) == (2, 2, 2)


def test_validation(m):
    for args in [(256, 0, 0), (0, -1, 0)]:
        with pytest.raises(ValueError):
            m.Color(*args)
    with pytest.raises(ValueError):
        m.AlphaColor(0, 0, 0, alpha=300)


def test_subclass_factories_return_subclass(m):
    a = m.AlphaColor.from_hex("#fff")
    assert type(a) is m.AlphaColor and a.alpha == 255
    assert repr(a) == "AlphaColor(255, 255, 255, alpha=255)"
    assert type(m.AlphaColor.from_name("tomato")) is m.AlphaColor
    assert type(m.AlphaColor.static_from_hex("#ffffff")) is m.Color   # the rung-1 trap


def test_unhashable_mutable(m):
    with pytest.raises(TypeError):
        hash(m.Color(0, 0, 0))
