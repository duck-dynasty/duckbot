import copy
from unittest import mock

import pytest


class AutoSpec:
    def __init__(self):
        self.cache = {}

    def of(self, spec: str):
        """Returns an autospec'd mock of the class of the given type."""
        if spec not in self.cache:
            with mock.patch(spec, autospec=True) as instance:
                self.cache[spec] = instance
        return copy.deepcopy(self.cache[spec])


@pytest.fixture(scope="session")
def autospec() -> AutoSpec:
    """A fixture to cache autospec'd `mock.patch` invocations. Cannot be used with classes that were imported
    using `from X import Y`, only those like `import X; X.Y`"""
    return AutoSpec()
