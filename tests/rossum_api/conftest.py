from __future__ import annotations

import aiofiles
import pytest
import pytest_asyncio
from mock import MagicMock

from rossum_sdk.rossum_api import ElisAPIClient, ElisAPIClientSync
from rossum_sdk.rossum_api.api_client import APIClient


@pytest.fixture
def http_client():
    return MagicMock(APIClient)


@pytest_asyncio.fixture
def elis_client(http_client):
    client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
    return (client, http_client)


@pytest.fixture
def elis_client_sync(http_client):
    client = ElisAPIClientSync(username="", password="", base_url=None, http_client=http_client)
    return (client, http_client)


@pytest_asyncio.fixture
async def mock_generator():
    async def f(item):
        for i in [item]:
            yield i

    return f


@pytest_asyncio.fixture
async def mock_file_read():
    async def f(path):
        async with aiofiles.open(path, "rb") as fp:
            async for line in fp:
                yield line

    return f


@pytest.fixture
def dummy_user():
    return {
        "id": 10775,
        "url": "https://elis.rossum.ai/api/v1/users/10775",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john-doe@east-west-trading.com",
        "date_joined": "2018-09-19T13:44:56.000000Z",
        "username": "john-doe@east-west-trading.com",
        "groups": ["https://elis.rossum.ai/api/v1/groups/3"],
        "organization": "https://elis.rossum.ai/api/v1/organizations/406",
        "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
        "is_active": True,
        "last_login": "2019-02-07T16:20:18.652253Z",
        "ui_settings": {},
        "metadata": {},
        "oidc_id": None,
    }
