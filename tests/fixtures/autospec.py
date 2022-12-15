import copy
from typing import Type, TypeVar, Union
from unittest import mock

import pytest

T = TypeVar("T")


def qualified_name(spec: Type[T]) -> str:
    """Returns the fully qualified name of the given class."""
    module = spec.__module__
    return spec.__qualname__ if module == "builtins" else f"{module}.{spec.__qualname__}"


class AutoSpec:
    def __init__(self):
        self.cache = {}

    def of(self, spec: Union[Type[T], str]) -> T:
        """Returns an autospec'd mock of the class of the given type."""
        name = spec if type(spec) is str else qualified_name(spec)
        if name not in self.cache:
            with mock.patch(name, autospec=True) as instance:
                self.cache[name] = instance
        return copy.deepcopy(self.cache[name])


@pytest.fixture(scope="session")
def autospec() -> AutoSpec:
    """A fixture to cache autospec'd `mock.patch` invocations. Cannot be used with classes that were imported
    using `from X import Y`, only those like `import X; X.Y`"""
    return AutoSpec()
