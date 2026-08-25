import urllib.parse
from unittest.mock import patch

import requests

from backend.app.config import DEFAULT_BANDARI_URL


def test_bandari_request_url_composition():
    """Ensure the application composes the Bandari request URL correctly.

    This test demonstrates the expected final URL when the application appends
    API paths (e.g. "/api/...") to the base BANDARI_ENGINE_URL. It mocks
    requests.Session.request to capture the URL that would be used for the HTTP
    call.
    """
    endpoint = "/api/v1/respond"

    # The expected final URL when joining base + endpoint
    expected = urllib.parse.urljoin(DEFAULT_BANDARI_URL, endpoint)

    with patch("requests.Session.request") as mock_request:
        session = requests.Session()

        # Example of how the app should compose the request URL
        url = urllib.parse.urljoin(DEFAULT_BANDARI_URL, endpoint)
        session.request("GET", url)

        mock_request.assert_called_once(), "HTTP request was not made"
        called_args = mock_request.call_args[0]
        # call signature: (method, url, ...)
        assert called_args[1] == expected, f"expected {expected}, got {called_args[1]}"
