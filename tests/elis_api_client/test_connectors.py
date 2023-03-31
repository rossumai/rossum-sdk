from __future__ import annotations

import pytest

from rossum_api.models.connector import Connector


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
    async def test_list_all_connectors(self, elis_client, dummy_connector, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_connector)

        connectors = client.list_all_connectors()

        async for c in connectors:
            assert c == Connector(**dummy_connector)

        http_client.fetch_all.assert_called_with("connectors", ())

    @pytest.mark.asyncio
    async def test_retrieve_connector(self, elis_client, dummy_connector):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_connector

        cid = dummy_connector["id"]
        connector = await client.retrieve_connector(cid)

        assert connector == Connector(**dummy_connector)

        http_client.fetch_one.assert_called_with("connectors", cid)

    async def test_create_new_connector(self, elis_client, dummy_connector):
        client, http_client = elis_client
        http_client.create.return_value = dummy_connector

        data = {
            "name": "MyQ Connector",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
            "service_url": "https://myq.east-west-trading.com",
            "authorization_token": "wuNg0OenyaeK4eenOovi7aiF",
        }
        connector = await client.create_new_connector(data)

        assert connector == Connector(**dummy_connector)

        http_client.create.assert_called_with("connectors", data)


class TestUsersSync:
    def test_list_all_connectors(self, elis_client_sync, dummy_connector, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_connector)

        connectors = client.list_all_connectors()

        for c in connectors:
            assert c == Connector(**dummy_connector)

        http_client.fetch_all.assert_called_with("connectors", ())

    def test_retrieve_connector(self, elis_client_sync, dummy_connector):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_connector

        cid = dummy_connector["id"]
        connector = client.retrieve_connector(cid)

        assert connector == Connector(**dummy_connector)

        http_client.fetch_one.assert_called_with("connectors", cid)

    def test_create_new_connector(self, elis_client_sync, dummy_connector):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_connector

        data = {
            "name": "MyQ Connector",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
            "service_url": "https://myq.east-west-trading.com",
            "authorization_token": "wuNg0OenyaeK4eenOovi7aiF",
        }
        connector = client.create_new_connector(data)

        assert connector == Connector(**dummy_connector)

        http_client.create.assert_called_with("connectors", data)
