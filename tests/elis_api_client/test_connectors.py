import pytest
from rossum_ng.models.connector import Connector
from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.api_client import APIClient


@pytest.fixture
def dummy_connector():
    return {
        "id": 1500,
        "name": "MyQ Connector",
        "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
        "url": "https://elis.rossum.ai/api/v1/connectors/1500",
        "service_url": "https://myq.east-west-trading.com",
        "params": "strict=true",
        "client_ssl_certificate": "-----BEGIN CERTIFICATE-----\n...",
        "authorization_token": "wuNg0OenyaeK4eenOovi7aiF",
        "asynchronous": True,
        "metadata": {},
    }


@pytest.mark.asyncio
class TestUsers:
    async def test_list_all_connectors(
        self, http_client: APIClient, dummy_connector, mock_generator
    ):
        http_client.fetch_all.return_value = mock_generator(dummy_connector)

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        users = client.list_all_connectors()

        async for u in users:
            assert u == Connector(**dummy_connector)

        http_client.fetch_all.assert_called_with("connectors", ())

    async def test_retrieve_connector(self, http_client: APIClient, dummy_connector):
        http_client.fetch_one.return_value = dummy_connector

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        cid = dummy_connector["id"]
        user = await client.retrieve_connector(cid)

        assert user == Connector(**dummy_connector)

        http_client.fetch_one.assert_called_with("connectors", cid)

    async def test_create_new_connector(self, http_client: APIClient, dummy_connector):
        http_client.create.return_value = dummy_connector

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        data = {
            "name": "MyQ Connector",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
            "service_url": "https://myq.east-west-trading.com",
            "authorization_token": "wuNg0OenyaeK4eenOovi7aiF",
        }
        user = await client.create_new_connector(data)

        assert user == Connector(**dummy_connector)

        http_client.create.assert_called_with("connectors", data)
