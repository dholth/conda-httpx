"""
Test that we can find and adapt auth handlers.
"""

from __future__ import annotations

import pytest
from conda.base.context import context, reset_context

from conda_httpx.auth import RequestAdapter, get_auth_handler

# this iterates over available auth handlers and picks one based on channel settings
#  context.plugin_manager.get_auth_handler("")

# Hunting for this channel config in test:
# channel_settings:
# - channel: https://repo.anaconda.cloud/*
#   auth: anaconda-auth


@pytest.mark.parametrize(
    "channel_url,expected,headers",
    [
        (
            "https://conda.anaconda.org/conda-forge",
            "conda-forge",  # we want to expect /t/ or even an auth header
            (),
        ),  # reset_context() loads some config that prevents /t/<token> from being added
        ("https://repo.anaconda.com/pkgs/main", "", ()),
        ("https://repo.anaconda.cloud/", "", ("Authorization",)),
        (
            "https://conda.anaconda.org/dholth",
            "dholth",  # we want to expect /t/ or even an auth header
            (),
        ),  # reset_context() loads some config that prevents /t/<token> from being added, probably context.add_anaconda_token
    ],
)
# set conda token here
def test_get_auth_handler(channel_url, expected, headers, monkeypatch):
    monkeypatch.setenv(
        "CONDA_TOKEN", "test-get-auth-token"
    )  # does not override the logged-in token? setting this to "" seems to log us out though.

    print(
        "\nChannel settings before reset_context()",
        context.channel_settings,
        "Add token?",
        context.add_anaconda_token,
    )  # can be empty even when in .condarc
    reset_context()
    print(
        "\nChannel settings after reset_context()",
        context.channel_settings,
        "Add token?",
        context.add_anaconda_token,
    )  # can be empty even when in .condarc
    auth_handler = get_auth_handler(channel_url)
    print(channel_url, auth_handler)

    class r:
        headers = {}
        url = channel_url

    r = RequestAdapter(r)  # type: ignore

    auth_handler(r)  # type: ignore

    print(r)

    # later, we will try to find a token header instead
    # we see /t/ for conda-forge and nothing for /pkgs/main
    assert expected in r.url
    assert set(headers).issubset(set(r.headers)), r.headers
