from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.upload import Upload


@pytest.fixture
def dummy_upload():
    return {
        "id": 37626,
        "url": "https://api.elis.master.r8.lol/v1/uploads/37626",
        "organization": "https://api.elis.master.r8.lol/v1/organizations/69",
        "creator": "https://api.elis.master.r8.lol/v1/users/503166",
        "created_at": "2024-07-31T13:06:47.903605Z",
        "queue": "https://api.elis.master.r8.lol/v1/queues/1403038",
        "email": None,
        "documents": ["https://api.elis.master.r8.lol/v1/documents/2944953"],
        "additional_documents": [],
        "annotations": ["https://api.elis.master.r8.lol/v1/annotations/2804885"],
    }


@pytest.mark.asyncio
class TestUploads:
    async def test_retrieve_upload(self, elis_client, dummy_upload):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_upload

        uid = dummy_upload["id"]
        upload = await client.retrieve_upload(uid)

        assert upload == Upload(**dummy_upload)

        http_client.fetch_one.assert_called_with(Resource.Upload, uid)


class TestUploadsSync:
    def test_retrieve_upload(self, elis_client_sync, dummy_upload):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_upload

        uid = dummy_upload["id"]
        upload = client.retrieve_upload(uid)

        assert upload == Upload(**dummy_upload)

        http_client.fetch_resource.assert_called_with(Resource.Upload, uid)
