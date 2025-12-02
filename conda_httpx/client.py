"""
A httpx client that knows how to authenticate with Anaconda services
by interoperating with conda auth and telemetry plugins.
"""

import httpx

from .auth import HttpxCondaAuth


def get_client(transport=None, **kwargs):
    """
    Get an httpx client configured with conda authentication plugins.
    """
    # For demonstration, we use a static token. In a real implementation,
    # you would integrate with conda's authentication plugins to get the token.
    auth = HttpxCondaAuth()
    client = httpx.Client(auth=auth, transport=transport, **kwargs)
    return client
