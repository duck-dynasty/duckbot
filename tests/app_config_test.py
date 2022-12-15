from duckbot import AppConfig


def test_is_production_env_set_to_prod(monkeypatch):
    monkeypatch.setenv("STAGE", "prod")
    assert AppConfig.is_production()


def test_is_production_env_set_to_test(monkeypatch):
    monkeypatch.setenv("STAGE", "test")
    assert not AppConfig.is_production()


def test_is_production_env_not_set():
    assert not AppConfig.is_production()


def test_fixture_is_production_prod(app_config):
    app_config.is_production = True
    assert AppConfig.is_production()


def test_fixture_is_production_not_prod(app_config):
    app_config.is_production = False
    assert not AppConfig.is_production()
