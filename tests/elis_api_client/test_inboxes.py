from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.inbox import Inbox


@pytest.fixture
def dummy_inbox():
    return {
        "id": 1234,
        "name": "Receipts",
        "url": "https://elis.rossum.ai/api/v1/inboxes/1234",
        "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
        "email": "east-west-trading-co-a34f3a@elis.rossum.ai",
        "email_prefix": "east-west-trading-co",
        "bounce_email_to": "bounces@east-west.com",
        "bounce_unprocessable_attachments": False,
        "bounce_deleted_annotations": False,
        "bounce_email_with_no_attachments": True,
        "metadata": {},
        "filters": {
            "allowed_senders": ["*@rossum.ai", "john.doe@company.com", "john.doe@company.??"],
            "denied_senders": ["spam@*"],
            "document_rejection_conditions": {
                "enabled": True,
                "resolution_lower_than_px": [1200, 600],
                "file_size_less_than_b": None,
                "mime_types": ["image/gif"],
                "file_name_regexes": None,
            },
        },
        "dmarc_check_action": "accept",
    }


@pytest.mark.asyncio
class TestInboxes:
    async def test_create_new_inbox(self, elis_client, dummy_inbox):
        client, http_client = elis_client
        http_client.create.return_value = dummy_inbox

        data = {
            "name": "Test Inbox",
            "email_prefix": "east-west-trading-co-test",
            "bounce_email_to": "joe@east-west-trading.com",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
            "filters": {"allowed_senders": ["*@east-west-trading.com"]},
        }

        inbox = await client.create_new_inbox(data)

        assert inbox == Inbox(**dummy_inbox)

        http_client.create.assert_called_with(Resource.Inbox, data)


class TestInboxesSync:
    def test_create_new_inbox(self, elis_client_sync, dummy_inbox):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_inbox

        data = {
            "name": "Test Inbox",
            "email_prefix": "east-west-trading-co-test",
            "bounce_email_to": "joe@east-west-trading.com",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
            "filters": {"allowed_senders": ["*@east-west-trading.com"]},
        }

        inbox = client.create_new_inbox(data)

        assert inbox == Inbox(**dummy_inbox)

        http_client.create.assert_called_with(Resource.Inbox, data)
