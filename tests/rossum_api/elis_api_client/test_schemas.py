from __future__ import annotations

import pytest

from rossum_sdk.rossum_api.models.schema import Schema


@pytest.fixture
def dummy_schema():
    return {
        "id": 31336,
        "name": "Basic Schema",
        "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
        "url": "https://elis.rossum.ai/api/v1/schemas/31336",
        "content": [
            {
                "category": "section",
                "id": "invoice_details_section",
                "label": "Invoice details",
                "children": [
                    {
                        "category": "datapoint",
                        "id": "document_id",
                        "label": "Invoice number",
                        "type": "string",
                        "rir_field_names": ["document_id"],
                        "constraints": {"required": False},
                        "default_value": None,
                    },
                ],
            },
        ],
        "metadata": {},
    }


@pytest.mark.asyncio
class TestSchemas:
    async def test_list_all_schemas(self, elis_client, dummy_schema, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_schema)

        schemas = client.list_all_schemas()

        async for s in schemas:
            assert s == Schema(**dummy_schema)

        http_client.fetch_all.assert_called_with("schemas", ())

    async def test_retrieve_schema(self, elis_client, dummy_schema):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_schema

        sid = dummy_schema["id"]
        schema = await client.retrieve_schema(sid)

        assert schema == Schema(**dummy_schema)

        http_client.fetch_one.assert_called_with("schemas", sid)

    async def test_create_new_schema(self, elis_client, dummy_schema):
        client, http_client = elis_client
        http_client.create.return_value = dummy_schema

        data = {"name": "Test Schema", "content": []}
        schema = await client.create_new_schema(data)

        assert schema == Schema(**dummy_schema)

        http_client.create.assert_called_with("schemas", data)

    async def test_delete_schema(self, elis_client, dummy_schema):
        client, http_client = elis_client
        http_client.delete.return_value = None

        sid = dummy_schema["id"]
        await client.delete_schema(sid)

        http_client.delete.assert_called_with("schemas", sid)


class TestSchemasSync:
    def test_list_all_schemas(self, elis_client_sync, dummy_schema, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_schema)

        schemas = client.list_all_schemas()

        for s in schemas:
            assert s == Schema(**dummy_schema)

        http_client.fetch_all.assert_called_with("schemas", ())

    def test_retrieve_schema(self, elis_client_sync, dummy_schema):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_schema

        sid = dummy_schema["id"]
        schema = client.retrieve_schema(sid)

        assert schema == Schema(**dummy_schema)

        http_client.fetch_one.assert_called_with("schemas", sid)

    def test_create_new_schema(self, elis_client_sync, dummy_schema):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_schema

        data = {"name": "Test Schema", "content": []}
        schema = client.create_new_schema(data)

        assert schema == Schema(**dummy_schema)

        http_client.create.assert_called_with("schemas", data)

    def test_delete_schema(self, elis_client_sync, dummy_schema):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        sid = dummy_schema["id"]
        client.delete_schema(sid)

        http_client.delete.assert_called_with("schemas", sid)
