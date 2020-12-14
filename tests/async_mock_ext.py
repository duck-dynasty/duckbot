import pytest
import mock

def async_mock(func):
    async def async_magic():
        pass

    async def async_wrap(*args, **kwargs):
        mock.MagicMock.__await__ = lambda x: async_magic().__await__()
        await func(*args, **kwargs)
    return async_wrap
