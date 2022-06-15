import pytest
from rossum_ng.models.schema import Schema
from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.api_client import APIClient


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
                    ...,
                ],
            },
            ...,
        ],
        "metadata": {},
    }


class TestSchemas:
    def test_get_schemas(self, http_client: APIClient, dummy_schema):
        http_client.get.return_value = [dummy_schema]

        client = ElisAPIClient(http_client=http_client)
        schemas = client.get_schemas()

        assert list(schemas) == [Schema(**dummy_schema)]

        http_client.get.assert_called()
        http_client.get.assert_called_with(f"/schemas", {})

    def test_get_schema(self, http_client: APIClient, dummy_schema):
        http_client.get.return_value = dummy_schema

        client = ElisAPIClient(http_client=http_client)
        sid = dummy_schema["id"]
        schema = client.get_schema(sid)

        assert schema == Schema(**dummy_schema)

        http_client.get.assert_called()
        http_client.get.assert_called_with(f"/schemas/{sid}")
