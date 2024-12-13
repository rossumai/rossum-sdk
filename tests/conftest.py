from __future__ import annotations

from unittest.mock import MagicMock

import aiofiles
import pytest
import pytest_asyncio

from rossum_api import ElisAPIClient, ElisAPIClientSync
from rossum_api.api_client import APIClient

ANNOTATIONS = [  # Most fields are stripped as these are not important for the test
    {
        "id": 1111,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11289",
        "content": "https://elis.develop.r8.lol/api/v1/annotations/1111/content",
        "automation_blocker": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
    },
    {
        "id": 2222,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11288",
        "content": "https://elis.develop.r8.lol/api/v1/annotations/2222/content",
        "automation_blocker": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
    },
    {
        "id": 3333,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11287",
        # URL that targets empty content should be translated to an empty list when sideloading
        "content": "https://elis.develop.r8.lol/api/v1/annotations/3333/content",
        # None URL is skipped when sideloading
        "automation_blocker": None,
    },
]

AUTOMATION_BLOCKERS = [
    {
        "id": 55,
        "url": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
        "content": [{"type": "automation_disabled", "level": "annotation"}],
        "annotation": "https://elis.develop.r8.lol/api/v1/annotations/971782",
    }
]

CONTENT = [
    {
        "id": 11,
        "schema_id": "invoice_id",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/2222/content/11",
        "content": {
            "value": "1234",
        },
    },
    {
        "id": 22,
        "schema_id": "invoice_id",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/1111/content/22",
        "content": {
            "value": "5678",
        },
    },
    {
        "id": 33,
        "schema_id": "date_issue",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/2222/content/33",
        "content": {
            "value": "2021-12-31",
        },
    },
]


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
