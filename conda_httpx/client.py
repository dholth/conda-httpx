"""
A httpx client that knows how to authenticate with Anaconda services
by interoperating with conda auth and telemetry plugins.
"""

import httpx
from conda.gateways import *


class MyCustomAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Send the request, with a custom `X-Authentication` header.
        request.headers["X-Authentication"] = self.token
        yield request


def get_client():
    """
    Get an httpx client configured with conda authentication plugins.
    """
    # For demonstration, we use a static token. In a real implementation,
    # you would integrate with conda's authentication plugins to get the token.
    token = "my-secret-token"
    auth = MyCustomAuth(token)
    client = httpx.Client(auth=auth)
    return client
