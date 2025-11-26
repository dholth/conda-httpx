"""
Test the conda-httpx client.
"""

import os

import httpx
import pytest

from conda_httpx.client import *


def handler(request):
    return httpx.Response(200, json={"text": "Hello, world!"})


def test_client():
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    response = client.get("https://repo.anaconda.com/pkgs/main")
    assert response.status_code == 200
