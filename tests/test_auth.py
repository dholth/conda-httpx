"""
Test that we can find and adapt auth handlers.
"""

from __future__ import annotations

import pytest
from conda.base.context import context

from conda_httpx.auth import RequestAdapter, get_auth_handler

# this iterates over available auth handlers and picks one based on channel settings
#  context.plugin_manager.get_auth_handler("")

# Hunting for this channel config in test:
# channel_settings:
# - channel: https://repo.anaconda.cloud/*
#   auth: anaconda-auth


@pytest.mark.parametrize(
    "channel_url,expected",
    [
        ("https://conda.anaconda.org/conda-forge", "/t"),
        ("https://repo.anaconda.com/pkgs/main", ""),
        ("https://repo.anaconda.cloud/", ""),
    ],
)
# set conda token here
def test_get_auth_handler(channel_url, expected):
    auth_handler = get_auth_handler(channel_url)
    print(channel_url, auth_handler)

    r = RequestAdapter(channel_url)

    auth_handler(r)

    print(r)

    # later, we will try to find a token header instead
    # we see /t/ for conda-forge and nothing for /pkgs/main
    assert expected in r.url
