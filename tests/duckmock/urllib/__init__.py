from unittest import mock

from .request import MockResponse

URLOPEN = "urllib.request.urlopen"


def patch_urlopen(html):
    if type(html) == list:
        return mock.patch(URLOPEN, side_effect=[MockResponse(data=x) for x in html])
    else:
        return mock.patch(URLOPEN, return_value=MockResponse(data=html))
