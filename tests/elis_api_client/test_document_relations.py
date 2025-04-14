from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from rossum_api.clients.external_async_client import AsyncRossumAPIClientWithDefaultDeserializer
from rossum_api.clients.external_sync_client import SyncRossumAPIClientWithDefaultDeserializer
from rossum_api.domain_logic.resources import Resource
from rossum_api.models.document_relation import DocumentRelation, DocumentRelationType

_CREATE_DOCUMENT_RELATION_DATA = _REPLACE_DOCUMENT_RELATION_DATA = {
    "type": DocumentRelationType.EXPORT.value,
    "annotation": "https://elis.rossum.ai/api/v1/annotations/406",
    "key": "some-key",
    "documents": [
        "https://elis.rossum.ai/api/v1/documents/124",
        "https://elis.rossum.ai/api/v1/documents/125",
    ],
}
_UPDATE_PART_DOCUMENT_RELATION_DATA = {
    "key": "some-key",
}


@pytest.fixture
def dummy_document_relation() -> dict[str, Any]:
    return {
        "id": 3025,
        "type": DocumentRelationType.EXPORT.value,
        "key": "some-key",
        "annotation": "https://elis.rossum.ai/api/v1/annotations/406",
        "documents": [
            "https://elis.rossum.ai/api/v1/documents/124",
            "https://elis.rossum.ai/api/v1/documents/125",
        ],
        "url": "https://elis.rossum.ai/api/v1/document_relations/3025",
    }


@pytest.mark.asyncio
class TestDocumentRelations:
    async def test_list_document_relations(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
        mock_generator,
    ) -> None:
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_document_relation)

        document_relations = client.list_document_relations()

        async for w in document_relations:
            assert w == DocumentRelation(**dummy_document_relation)

        http_client.fetch_all.assert_called_with(Resource.DocumentRelation, ())

    async def test_retrieve_document_relation(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = await client.retrieve_document_relation(oid)

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.fetch_one.assert_called_with(Resource.DocumentRelation, oid)

    async def test_create_new_document_relation(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client
        http_client.create.return_value = dummy_document_relation

        document_relation = await client.create_new_document_relation(
            _CREATE_DOCUMENT_RELATION_DATA
        )

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.create.assert_called_with(
            Resource.DocumentRelation, _CREATE_DOCUMENT_RELATION_DATA
        )

    async def test_update_document_relation(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client
        http_client.replace.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = await client.update_document_relation(
            oid, _REPLACE_DOCUMENT_RELATION_DATA
        )

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.replace.assert_called_with(
            Resource.DocumentRelation, oid, _REPLACE_DOCUMENT_RELATION_DATA
        )

    async def test_update_part_document_relation(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client
        http_client.update.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = await client.update_part_document_relation(
            oid, _UPDATE_PART_DOCUMENT_RELATION_DATA
        )

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.update.assert_called_with(
            Resource.DocumentRelation, oid, _UPDATE_PART_DOCUMENT_RELATION_DATA
        )

    async def test_delete_document_relation(
        self,
        elis_client: tuple[AsyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client
        http_client.delete.return_value = None

        oid = dummy_document_relation["id"]
        await client.delete_document_relation(oid)

        http_client.delete.assert_called_with(Resource.DocumentRelation, oid)


class TestDocumentRelationsSync:
    def test_list_document_relations(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_document_relation,))

        document_relations = client.list_document_relations()

        for w in document_relations:
            assert w == DocumentRelation(**dummy_document_relation)

        http_client.fetch_resources.assert_called_with(Resource.DocumentRelation, ())

    def test_retrieve_document_relation(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = client.retrieve_document_relation(oid)

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.fetch_resource.assert_called_with(Resource.DocumentRelation, oid)

    def test_create_new_document_relation(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_document_relation

        document_relation = client.create_new_document_relation(_CREATE_DOCUMENT_RELATION_DATA)

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.create.assert_called_with(
            Resource.DocumentRelation, _CREATE_DOCUMENT_RELATION_DATA
        )

    def test_update_document_relation(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.replace.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = client.update_document_relation(oid, _REPLACE_DOCUMENT_RELATION_DATA)

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.replace.assert_called_with(
            Resource.DocumentRelation, oid, _REPLACE_DOCUMENT_RELATION_DATA
        )

    def test_update_part_document_relation(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.update.return_value = dummy_document_relation

        oid = dummy_document_relation["id"]
        document_relation = client.update_part_document_relation(
            oid, _UPDATE_PART_DOCUMENT_RELATION_DATA
        )

        assert document_relation == DocumentRelation(**dummy_document_relation)

        http_client.update.assert_called_with(
            Resource.DocumentRelation, oid, _UPDATE_PART_DOCUMENT_RELATION_DATA
        )

    def test_delete_document_relation(
        self,
        elis_client_sync: tuple[SyncRossumAPIClientWithDefaultDeserializer, MagicMock],
        dummy_document_relation: dict[str, Any],
    ) -> None:
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        oid = dummy_document_relation["id"]
        client.delete_document_relation(oid)

        http_client.delete.assert_called_with(Resource.DocumentRelation, oid)
