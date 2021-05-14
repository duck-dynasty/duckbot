class MockResponse:
    """A stub implementation for `urllib.request.urlopen`"""

    status: int
    data: bytes

    def __init__(self, *, data: bytes):
        self.data = data
        self.num = 0
        self.lines = data.decode().splitlines() if isinstance(data, bytes) else data.splitlines()

    def read(self):
        self.status = 200 if self.data is not None else 500
        return self.data

    def __iter__(self):
        return self

    def __next__(self):
        if self.num < len(self.lines):
            line = self.lines[self.num].encode()
            self.num += 1
            return line
        else:
            raise StopIteration

    def close(self):
        """Nothing to close."""
        pass
