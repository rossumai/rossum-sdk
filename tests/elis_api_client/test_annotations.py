import pytest

from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.models.annotation import Annotation
from rossum_ng.api_client import APIClient


@pytest.fixture
def dummy_annotation():
    return {
        "document": "https://elis.rossum.ai/api/v1/documents/314628",
        "id": 314528,
        "queue": "https://elis.rossum.ai/api/v1/queues/8199",
        "schema": "https://elis.rossum.ai/api/v1/schemas/95",
        "relations": [],
        "pages": ["https://elis.rossum.ai/api/v1/pages/558598"],
        "creator": "https://elis.rossum.ai/api/v1/users/1",
        "created_at": "2021-04-26T10:08:03.856648Z",
        "modifier": None,
        "modified_at": None,
        "confirmed_at": None,
        "exported_at": None,
        "assigned_at": None,
        "status": "to_review",
        "rir_poll_id": "54f6b9ecfa751789f71ddf12",
        "messages": None,
        "url": "https://elis.rossum.ai/api/v1/annotations/314528",
        "content": "https://elis.rossum.ai/api/v1/annotations/314528/content",
        "time_spent": 0,
        "metadata": {},
        "related_emails": [],
        "email": "https://elis.rossum.ai/api/v1/emails/96743",
        "automation_blocker": None,
        "email_thread": "https://elis.rossum.ai/api/v1/email_threads/34567",
        "has_email_thread_with_replies": True,
        "has_email_thread_with_new_replies": False,
    }


@pytest.mark.asyncio
class TestAnnotations:
    async def test_get_annotations(self, http_client: APIClient, dummy_annotation, mock_generator):
        http_client.fetch_all.return_value = mock_generator(dummy_annotation)

        client = ElisAPIClient(http_client=http_client)
        annotations = client.get_annotations()

        async for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_all.assert_called()
        http_client.fetch_all.assert_called_with("annotations")

    async def test_get_annotation(self, http_client: APIClient, dummy_annotation):
        http_client.fetch_one.return_value = dummy_annotation

        client = ElisAPIClient(http_client=http_client)
        aid = dummy_annotation["id"]
        annotation = await client.get_annotation(aid)

        assert annotation == Annotation(**dummy_annotation)

        http_client.fetch_one.assert_called()
        http_client.fetch_one.assert_called_with("annotations", aid)
