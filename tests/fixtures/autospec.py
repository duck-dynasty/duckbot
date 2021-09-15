import copy
from unittest import mock

import pytest


class AutoSpec:
    def __init__(self):
        self.cache = {}

    def of(self, spec: str):
        if spec not in self.cache:
            with mock.patch(spec, autospec=True) as instance:
                self.cache[spec] = instance
        return copy.deepcopy(self.cache[spec])


@pytest.fixture(scope="session")
def autospec() -> AutoSpec:
    return AutoSpec()
