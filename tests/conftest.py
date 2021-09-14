import logging

# load fixtures from our test suite
pytest_plugins = (
    "tests.fixtures",
    "tests.fixtures.discord",
)


def pytest_configure(config):
    # flake8 logs a ton, suppress it
    logging.getLogger("flake8").setLevel(logging.ERROR)
