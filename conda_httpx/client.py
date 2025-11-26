"""
A httpx client that knows how to authenticate with Anaconda services
by interoperating with conda auth and telemetry plugins.
"""

import httpx

from .auth import RequestAdapter, get_auth_handler


class HttpxCondaAuth(httpx.Auth):
    def auth_flow(self, request: httpx.Request):
        url: httpx.URL = request.url
        upstream_auth = get_auth_handler(str(url))
        req_ = RequestAdapter(request)
        upstream_auth(req_)

        yield request


def get_client(transport=None):
    """
    Get an httpx client configured with conda authentication plugins.
    """
    # For demonstration, we use a static token. In a real implementation,
    # you would integrate with conda's authentication plugins to get the token.
    auth = HttpxCondaAuth()
    client = httpx.Client(auth=auth, transport=transport)
    return client
