"""
Find Conda auth handlers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from fnmatch import fnmatch
from functools import cache

from conda.base.context import context
from conda.common.url import (
    urlparse,
)
from conda.gateways.connection.session import (
    CondaHttpAuth,
    get_channel_name_from_url,
)

log = logging.getLogger(__name__)


@dataclass
class RequestAdapter:
    """
    Mimic the part of the requests API that existing auth handlers expect.
    """

    url: str
    hooks: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)

    def __init__(self, request):
        # use dataclass constructor?
        self.hooks = {}

        self.httpx_request = request
        self.url = str(request.url)
        self.headers = request.headers

    def register_hook(self, name, func):
        self.hooks[name] = func


@cache
def get_auth_handler(url: str):
    """
    Return auth handler for given url based on channel settings in conda context.
    If no auth handler is found, return default CondaSession.
    """
    # Would rather have universal auth handler?

    channel_name = get_channel_name_from_url(url)

    # If for whatever reason a channel name can't be determined, return CondaHttpAuth().
    if channel_name is None:
        return CondaHttpAuth()

    # We ensure here if there are duplicates defined, we choose the last one
    channel_settings = {}
    for settings in context.channel_settings:
        channel = settings.get("channel", "")
        if channel == channel_name:
            # First we check for exact match
            channel_settings = settings
            continue

        # If we don't have an exact match, we attempt to match a URL pattern
        parsed_url = urlparse(url)
        parsed_setting = urlparse(channel)

        # We require that the schemes must be identical to prevent downgrade attacks.
        # This includes the case of a scheme-less pattern like "*", which is not allowed.
        if parsed_setting.scheme != parsed_url.scheme:
            continue

        url_without_schema = parsed_url.netloc + parsed_url.path
        pattern = parsed_setting.netloc + parsed_setting.path
        if fnmatch(url_without_schema, pattern):
            channel_settings = settings

    auth_handler = channel_settings.get("auth", "").strip() or None

    # Return default session object
    if auth_handler is None:
        return CondaHttpAuth()

    auth_handler_cls = context.plugin_manager.get_auth_handler(auth_handler)

    if auth_handler_cls is None:
        return CondaHttpAuth()

    return auth_handler_cls(channel_name)
