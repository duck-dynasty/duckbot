
class MockResponse:
    """A stub implementation for `urllib.request.urlopen`"""
    status: int
    data: bytes

    def __init__(self, *, data: bytes):
        self.data = data

    def read(self):
        self.status = 200 if self.data is not None else 500
        return self.data
    
    def close(self):
        """Nothing to close."""
        pass
