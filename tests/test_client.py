"""
Test the conda-httpx client.
"""

from __future__ import annotations

import httpx
from conda.base.context import reset_context

from conda_httpx.client import get_client


def test_client():
    headers = {}

    def handler(request):
        nonlocal headers
        headers = request.headers
        return httpx.Response(200, json={"text": "Hello, world!"})

    reset_context()  # loads condarc
    transport = httpx.MockTransport(handler)
    client = get_client(transport=transport)
    # any url under repo.anaconda.cloud should work
    response = client.get("https://repo.anaconda.cloud/main/noarch/repodata.json")
    print("Httpx headers were", headers)
    assert response.status_code == 200
    assert "authorization" in headers
