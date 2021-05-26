from discord.http import Route

from duckbot.slash.route import Route8


def test_base_discordv8():
    assert Route8.BASE == "https://discord.com/api/v8"


def test_eq_equals():
    assert Route8("PUT", "/app") == Route8("PUT", "/app")


def test_eq_different_class():
    assert Route8("PUT", "/application") != Route("PUT", "/application")


def test_eq_different_method():
    assert Route8("PUT", "/moo") != Route8("DELETE", "/moo")


def test_eq_different_path():
    assert Route8("PUT", "/application") != Route8("PUT", "/app")


def test_str_returns_method_and_url():
    assert str(Route8("PUT", "/cow")) == "PUT https://discord.com/api/v8/cow"


def test_repr_returns_method_and_url():
    assert repr(Route8("PUT", "/pi")) == "PUT https://discord.com/api/v8/pi"
