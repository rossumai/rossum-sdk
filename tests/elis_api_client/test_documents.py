from __future__ import annotations

import httpx
import pytest

from rossum_api.api_client import Resource


@pytest.fixture
def file_data() -> bytes:
    with open("tests/data/sample_invoice.pdf", "rb") as f:
        return f.read()


@pytest.mark.asyncio
class TestDocuments:
    async def test_retrieve_document_content(self, elis_client, file_data):
        client, http_client = elis_client
        http_client.request.return_value = httpx.Response(status_code=200, content=file_data)

        document_id = 123
        result = await client.retrieve_document_content(document_id=document_id)

        http_client.request.assert_called_with(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        assert result == file_data


class TestDocumentsSync:
    def test_retrieve_document_content(self, elis_client_sync, file_data):
        client, http_client = elis_client_sync
        http_client.request.return_value = httpx.Response(status_code=200, content=file_data)

        document_id = 123
        result = client.retrieve_document_content(document_id=document_id)

        http_client.request.assert_called_with(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        assert result == file_data
