"""
Test that we can find and adapt auth handlers.
"""

import pytest

from conda_httpx.auth import get_auth_handler


@pytest.mark.parametrize(
    "channel_url",
    [
        "https://conda.anaconda.org/conda-forge",
        "https://repo.anaconda.com/pkgs/main",
    ],
)
def test_get_auth_handler(channel_url):
    auth_handler = get_auth_handler(channel_url)
    print(channel_url, auth_handler)
