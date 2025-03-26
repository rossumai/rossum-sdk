from __future__ import annotations

import json

import httpx
import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.document import Document


@pytest.fixture
def file_data() -> bytes:
    with open("tests/data/sample_invoice.pdf", "rb") as f:
        return f.read()


@pytest.fixture
def dummy_document() -> dict:
    return {
        "id": 3244308,
        "url": "https://elis.rossum.ai/api/v1/documents/3244308",
        "s3_name": "7731c4d28b3bf6ae5e29f933798b1393",
        "parent": "https://elis.rossum.ai/api/v1/documents/2244308",
        "email": None,
        "mime_type": "application/pdf",
        "creator": "https://elis.rossum.ai/api/v1/users/71531",
        "created_at": "2022-07-12T08:16:41.731996Z",
        "arrived_at": "2022-07-12T08:16:41.731996Z",
        "original_file_name": "sample_invoice.pdf",
        "content": "https://elis.rossum.ai/api/v1/documents/3244308/content",
        "attachment_status": None,
        "metadata": {"some": "stuff"},
        "annotations": [],
    }


@pytest.mark.asyncio
class TestDocuments:
    async def test_retrieve_document(self, elis_client, dummy_document):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_document

        did = dummy_document["id"]
        document = await client.retrieve_document(did)

        assert document == Document(**dummy_document)

        http_client.fetch_one.assert_called_with(Resource.Document, did)

    async def test_retrieve_document_content(self, elis_client, file_data):
        client, http_client = elis_client
        http_client.request.return_value = httpx.Response(status_code=200, content=file_data)

        document_id = 123
        result = await client.retrieve_document_content(document_id=document_id)

        http_client.request.assert_called_with(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        assert result == file_data

    async def test_create_new_document(self, elis_client, dummy_document, file_data):
        client, http_client = elis_client
        http_client.request_json.return_value = dummy_document

        file_name = dummy_document["original_file_name"]
        metadata = dummy_document["metadata"]
        parent = dummy_document["parent"]
        document = await client.create_new_document(file_name, file_data, metadata, parent)

        assert document == Document(**dummy_document)

        expected_files = {
            "content": (file_name, file_data),
            "metadata": ("", json.dumps(metadata).encode("utf-8")),
            "parent": ("", parent),
        }
        http_client.request_json.assert_called_with(
            "POST", url=Resource.Document.value, files=expected_files
        )


class TestDocumentsSync:
    def test_retrieve_document(self, elis_client_sync, dummy_document):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_document

        did = dummy_document["id"]
        document = client.retrieve_document(did)

        assert document == Document(**dummy_document)

        http_client.fetch_resource.assert_called_with(Resource.Document, did)

    def test_retrieve_document_content(self, elis_client_sync, file_data):
        client, http_client = elis_client_sync
        http_client.request.return_value = httpx.Response(status_code=200, content=file_data)

        document_id = 123
        result = client.retrieve_document_content(document_id=document_id)

        http_client.request.assert_called_with(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        assert result == file_data

    def test_create_new_document(self, elis_client_sync, dummy_document, file_data):
        client, http_client = elis_client_sync
        http_client.request_json.return_value = dummy_document

        file_name = dummy_document["original_file_name"]
        metadata = dummy_document["metadata"]
        parent = dummy_document["parent"]
        document = client.create_new_document(file_name, file_data, metadata, parent)

        assert document == Document(**dummy_document)

        expected_files = {
            "content": (file_name, file_data),
            "metadata": ("", json.dumps(metadata).encode("utf-8")),
            "parent": ("", parent),
        }
        http_client.request_json.assert_called_with(
            "POST", url=Resource.Document.value, files=expected_files
        )
