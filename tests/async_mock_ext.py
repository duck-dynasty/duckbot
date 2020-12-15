import pytest
import mock

def patch_async_mock(func):
    """A decorator to allow @mock.patch to work for async methods"""
    async def async_magic():
        pass

    async def async_wrap(*args, **kwargs):
        mock.MagicMock.__await__ = lambda x: async_magic().__await__()
        await func(*args, **kwargs)
    return async_wrap
