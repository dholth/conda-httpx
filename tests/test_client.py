"""
Test the conda-httpx client.
"""

from __future__ import annotations

import ssl
from pathlib import Path

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

    # In httpx, it seems like we must pass the proxy auth to the Proxy() object,
    # instead of dealing with it inside CondaHttpAuth as if it was part of the
    # tunneled protocol. That's good, but this part of conda's auth won't
    # translate exactly into httpx.

    cert = Path("~/.mitmproxy/mitmproxy-ca-cert.pem").expanduser()
    assert cert.exists()
    cert_text = cert.read_text(encoding="ascii")
    verify_paths = ssl.get_default_verify_paths()
    default_certs = Path(verify_paths[0]).read_text(encoding="ascii", errors="replace")
    cacerts = default_certs  # "\n".join((default_certs, cert_text))
    cacerts = cacerts.encode(
        "ascii", errors="replace"
    )  # one of the comments contains non-ascii names
    certs_only = []
    in_cert = False
    for line in cacerts.splitlines():
        if line == b"-----BEGIN CERTIFICATE-----":
            in_cert = True
        if in_cert:
            certs_only.append(line)
        if line == b"-----END CERTIFICATE-----":
            in_cert = False

    # ssl really hates the mitmproxy ca cert?
    ctx = ssl.create_default_context(
        # ssl.Purpose.CLIENT_AUTH  # , cadata=b"\n".join(certs_only)
    )

    transport = httpx.MockTransport(build_handler(407))

    # This will not use MockTransport:
    proxy_mounts = {
        "http://": httpx.HTTPTransport(proxy="http://localhost:8080", verify=False),
        "https://": httpx.HTTPTransport(proxy="http://localhost:8080", verify=False),
    }
    client = get_client(
        transport=transport,
        mounts=proxy_mounts,
    )
    response = client.get(
        "https://conda.anaconda.org/main/noarch/repodata.json",
    )
    # print("With 403 response, headers were", transport.handler.headers)
    assert response.status_code == 407
    # assert "authorization" in transport.handler.headers
