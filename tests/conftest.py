from __future__ import annotations

import typing
from unittest.mock import MagicMock

import aiofiles
import pytest
import pytest_asyncio

from rossum_api.clients.external_async_client import AsyncRossumAPIClient
from rossum_api.clients.external_sync_client import SyncRossumAPIClient
from rossum_api.clients.internal_async_client import InternalAsyncClient
from rossum_api.clients.internal_sync_client import InternalSyncClient
from rossum_api.dtos import Token

if typing.TYPE_CHECKING:
    from rossum_api.clients.external_async_client import (
        AsyncRossumAPIClientWithDefaultDeserializer,
    )
    from rossum_api.clients.external_sync_client import SyncRossumAPIClientWithDefaultDeserializer

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
def internal_async_client() -> MagicMock:
    return MagicMock(InternalAsyncClient)


@pytest.fixture
def internal_sync_client() -> MagicMock:
    return MagicMock(InternalSyncClient)


@pytest.fixture
def elis_client(
    internal_async_client: MagicMock,
) -> tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock]:
    client: AsyncRossumAPIClientWithDefaultDeserializer = AsyncRossumAPIClient(
        base_url="", credentials=Token("abc")
    )
    client._http_client = internal_async_client
    return client, internal_async_client


@pytest.fixture
def elis_client_sync(
    internal_sync_client: MagicMock,
) -> tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock]:
    client: SyncRossumAPIClientWithDefaultDeserializer = SyncRossumAPIClient(
        base_url="", credentials=Token("abc")
    )
    client.internal_client = internal_sync_client
    return client, internal_sync_client


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


@pytest_asyncio.fixture
async def mock_file_read_sync():
    def f(path):
        with open(path, "rb") as fp:
            yield from fp

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


@pytest.fixture
def dummy_queue():
    return {
        "id": 8198,
        "name": "Received invoices",
        "url": "https://elis.rossum.ai/api/v1/queues/8198",
        "workspace": "https://elis.rossum.ai/api/v1/workspaces/7540",
        "connector": None,
        "webhooks": [],
        "hooks": [],
        "schema": "https://elis.rossum.ai/api/v1/schemas/31336",
        "inbox": "https://elis.rossum.ai/api/v1/inboxes/1229",
        "users": ["https://elis.rossum.ai/api/v1/users/10775"],
        "session_timeout": "01:00:00",
        "rir_url": "https://all.rir.rossum.ai",
        "rir_params": None,
        "dedicated_engine": None,
        "generic_engine": "https://api.elis.develop.r8.lol/v1/generic_engines/1",
        "counts": {
            "importing": 0,
            "split": 0,
            "failed_import": 0,
            "to_review": 2,
            "reviewing": 0,
            "confirmed": 0,
            "exporting": 0,
            "postponed": 0,
            "failed_export": 0,
            "exported": 0,
            "deleted": 0,
            "purged": 0,
            "rejected": 0,
        },
        "default_score_threshold": 0.8,
        "automation_enabled": False,
        "automation_level": "never",
        "locale": "en_US",
        "metadata": {},
        "use_confirmed_state": False,
        "document_lifetime": "01:00:00",
        "settings": {
            "columns": [{"schema_id": "tags"}],
            "hide_export_button": True,
            "automation": {"automate_duplicates": True, "automate_suggested_edit": False},
            "rejection_config": {"enabled": True},
            "email_notifications": {
                "recipient": {"email": "john.doe@company.com", "name": "John Doe"},
                "unprocessable_attachments": False,
                "email_with_no_attachments": True,
                "postponed_annotations": False,
                "deleted_annotations": False,
            },
        },
    }
