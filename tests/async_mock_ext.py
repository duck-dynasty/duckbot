async def async_value(value):
    """A wrapper for methods that return an async value."""
    return value


async def list_as_async_generator(lst: list):
    """A wrapper for a list that converts it into an async generator."""
    for x in lst:
        yield x
