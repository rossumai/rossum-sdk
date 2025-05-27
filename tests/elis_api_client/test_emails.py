from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models import deserialize_default


@pytest.fixture
def dummy_email():
    return {
        "id": 1234,
        "url": "https://elis.rossum.ai/api/v1/emails/1234",
        "queue": "https://elis.rossum.ai/api/v1/queues/4321",
        "inbox": "https://elis.rossum.ai/api/v1/inboxes/8199",
        "documents": ["https://elis.rossum.ai/api/v1/documents/5678"],
        "parent": "https://elis.rossum.ai/api/v1/emails/1230",
        "children": ["https://elis.rossum.ai/api/v1/emails/1244"],
        "created_at": "2021-03-26T14:31:46.993427Z",
        "last_thread_email_created_at": "2021-03-27T14:29:48.665478Z",
        "subject": "Some email subject",
        "from": {"email": "company@east-west.com", "name": "Company East"},
        "to": [
            {"email": "east-west-trading-co-a34f3a@elis.rossum.ai", "name": "East West Trading"}
        ],
        "cc": [],
        "bcc": [],
        "body_text_plain": "Some body",
        "body_text_html": '<div dir="ltr">Some body</div>',
        "metadata": {},
        "type": "outgoing",
        "annotation_counts": {
            "annotations": 3,
            "annotations_processed": 1,
            "annotations_purged": 0,
            "annotations_unprocessed": 1,
            "annotations_rejected": 1,
        },
        "annotations": [
            "https://elis.rossum.ai/api/v1/annotations/1",
            "https://elis.rossum.ai/api/v1/annotations/2",
            "https://elis.rossum.ai/api/v1/annotations/4",
        ],
        "related_annotations": [],
        "related_documents": ["https://elis.rossum.ai/api/v1/documents/3"],
        "filtered_out_document_count": 2,
        "labels": ["rejected"],
    }


@pytest.mark.asyncio
class TestEmails:
    @pytest.mark.asyncio
    async def test_retrieve_email(self, elis_client, dummy_email):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_email

        cid = dummy_email["id"]
        email = await client.retrieve_email(cid)

        assert email == deserialize_default(Resource.Email, dummy_email)
        assert email.from_ == dummy_email["from"]

        http_client.fetch_one.assert_called_with(Resource.Email, cid)

    @pytest.mark.asyncio
    async def test_import_email(self, elis_client):
        client, http_client = elis_client
        task_url = "https://elis.rossum.ai/api/v1/tasks/456575"
        http_client.request_json.return_value = {"url": task_url}

        raw_message = b"abc"
        recipient = "joe@east-west.com"
        result = await client.import_email(raw_message, recipient)

        assert result == task_url

        http_client.request_json.assert_called_with(
            "POST",
            url="emails/import",
            files={
                "raw_message": ("email.eml", raw_message),
                "recipient": (None, recipient),
            },
        )


class TestEmailsSync:
    def test_retrieve_email(self, elis_client_sync, dummy_email):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_email

        cid = dummy_email["id"]
        email = client.retrieve_email(cid)

        assert email == deserialize_default(Resource.Email, dummy_email)
        assert email.from_ == dummy_email["from"]

        http_client.fetch_resource.assert_called_with(Resource.Email, cid)

    def test_import_email(self, elis_client_sync):
        client, http_client = elis_client_sync
        task_url = "https://elis.rossum.ai/api/v1/tasks/456575"
        http_client.request_json.return_value = {"url": task_url}

        raw_message = b"abc"
        recipient = "joe@east-west.com"
        result = client.import_email(raw_message, recipient)

        assert result == task_url

        http_client.request_json.assert_called_with(
            "POST",
            url="emails/import",
            files={
                "raw_message": ("email.eml", raw_message),
                "recipient": (None, recipient),
            },
        )
