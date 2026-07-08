import inspect
from typing import Type, TypeVar
from unittest import mock

import pytest

T = TypeVar("T")


class SpecMock(mock.MagicMock):
    """A spec'd mock whose children are created lazily. Method children enforce the real method's signature."""

    def _get_child_mock(self, /, **kw):
        name = kw.get("name")
        spec = self._spec_class
        if spec is not None and isinstance(name, str) and not name.startswith("__"):
            attr = inspect.getattr_static(spec, name, None)
            if inspect.isfunction(attr):
                return mock.create_autospec(attr.__get__(mock.sentinel.self_), name=name)
        return super()._get_child_mock(**kw)


class AutoSpec:
    def of(self, spec: Type[T]) -> T:
        """Returns a spec'd mock of the given class."""
        return SpecMock(spec=spec)


@pytest.fixture(scope="session")
def autospec() -> AutoSpec:
    """A fixture to create spec'd mocks of classes."""
    return AutoSpec()
