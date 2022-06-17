from unittest.mock import MagicMock

import pytest

from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.models.workspace import Workspace


@pytest.fixture
def dummy_workspace():
    return {
        "id": 7540,
        "name": "East West Trading Co",
        "url": "https://elis.rossum.ai/api/v1/workspaces/7540",
        "autopilot": True,
        "organization": "https://elis.rossum.ai/api/v1/organizations/406",
        "queues": [
            "https://elis.rossum.ai/api/v1/queues/8199",
            "https://elis.rossum.ai/api/v1/queues/8236",
        ],
        "metadata": {},
    }


@pytest.mark.asyncio
class TestWorkspaces:
    async def test_list_all_workspaces(
        self, http_client: MagicMock, dummy_workspace, mock_generator
    ):
        http_client.fetch_all.return_value = mock_generator(dummy_workspace)

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        workspaces = client.list_all_workspaces()

        async for w in workspaces:
            assert w == Workspace(**dummy_workspace)

        http_client.fetch_all.assert_called_with("workspaces", ())

    async def test_retrieve_workspace(self, http_client: MagicMock, dummy_workspace):
        http_client.fetch_one.return_value = dummy_workspace

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        oid = dummy_workspace["id"]
        workspace = await client.retrieve_workspace(oid)

        assert workspace == Workspace(**dummy_workspace)

        http_client.fetch_one.assert_called_with("workspaces", oid)

    async def test_create_new_organization(self, http_client: MagicMock, dummy_workspace):
        http_client.create.return_value = dummy_workspace

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        data = {
            "organization": "https://elis.rossum.ai/api/v1/workspaces/406",
            "username": "jane@east-west-trading.com",
            "email": "jane@east-west-trading.com",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
            "groups": ["https://elis.rossum.ai/api/v1/groups/2"],
        }
        workspace = await client.create_new_workspace(data)

        assert workspace == Workspace(**dummy_workspace)

        http_client.create.assert_called_with("workspaces", data)
