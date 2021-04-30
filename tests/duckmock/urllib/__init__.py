from unittest import mock
from .request import MockResponse

URLOPEN = "urllib.request.urlopen"


def patch_urlopen(html):
    return mock.patch(URLOPEN, return_value=MockResponse(data=html))
