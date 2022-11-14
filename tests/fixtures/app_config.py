import pytest


class AppConfigFixture:
    def __init__(self, monkeypatch: pytest.MonkeyPatch):
        self.monkeypatch = monkeypatch

    def set_is_production(self, prod: bool):
        self.monkeypatch.setenv("STAGE", "prod" if prod else "test")

    is_production = property(fset=set_is_production, doc="Stubs `AppConfig.is_production` so it returns the value given")


@pytest.fixture
def app_config(monkeypatch) -> AppConfigFixture:
    """Returns a class which allows for simpler stubbing of `AppConfig` values.
    Whichever method you want to stub, simply set it. For example:

    `app_config.is_production = True  # stubs AppConfig.is_production() to return True`"""
    return AppConfigFixture(monkeypatch)
