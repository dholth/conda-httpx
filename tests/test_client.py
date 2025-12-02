"""
Test the conda-httpx client.
"""

from __future__ import annotations

import anaconda_auth._conda.auth_handler
import httpx
import pytest
from conda.base.context import reset_context

from conda_httpx.client import get_client


def build_handler(code: int):
    def handler(request):
        handler.headers = request.headers  # type: ignore
        return httpx.Response(code, json={"text": "Hello, world!"})

    return handler


def test_client():
    reset_context()  # loads condarc
    transport = httpx.MockTransport(build_handler(200))
    client = get_client(transport=transport)
    # any url under repo.anaconda.cloud should work
    response = client.get("https://repo.anaconda.cloud/main/noarch/repodata.json")
    print("Httpx headers were", transport.handler.headers)
    assert response.status_code == 200
    assert "authorization" in transport.handler.headers

    # AnacondaAuth raises an exception on 403, but doesn't handle other error
    # codes. Must be configured for that channel (how to do that in the test?)
    transport = httpx.MockTransport(build_handler(403))
    client = get_client(transport=transport)
    with pytest.raises(anaconda_auth._conda.auth_handler.AnacondaAuthError):
        client.get("https://repo.anaconda.cloud/main/linux-64/repodata.json")
        # response not assigned
    assert "authorization" in transport.handler.headers


def test_client_proxy_407():
    # CondaHttpAuth tries to handle 407. In httpx, httpx.Client(proxies={}) or
    # httpx.get(url, proxies={}) (no explicit Client) is expected; by comparison
    # requests sends proxies to the kwargs of hooks.
    #
    # For multiple proxies, httpx uses mounts= which conda also wants to use for
    # URL scheme handling.
    #
    # https://www.python-httpx.org/advanced/proxies/#http-proxies

    transport = httpx.MockTransport(build_handler(407))
    client = get_client(transport=transport, proxy="http://localhost:8888/")
    response = client.get(
        "https://conda.anaconda.org/main/noarch/repodata.json",
    )
    print("With 403 response, headers were", transport.handler.headers)
    assert response.status_code == 407
    assert "authorization" in transport.handler.headers
