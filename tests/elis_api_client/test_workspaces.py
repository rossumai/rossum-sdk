from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.workspace import Workspace


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
    async def test_list_workspaces(self, elis_client, dummy_workspace, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_workspace)

        workspaces = client.list_workspaces()

        async for w in workspaces:
            assert w == Workspace(**dummy_workspace)

        http_client.fetch_all.assert_called_with(Resource.Workspace, ())

    async def test_retrieve_workspace(self, elis_client, dummy_workspace):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_workspace

        oid = dummy_workspace["id"]
        workspace = await client.retrieve_workspace(oid)

        assert workspace == Workspace(**dummy_workspace)

        http_client.fetch_one.assert_called_with(Resource.Workspace, oid)

    async def test_create_new_workspace(self, elis_client, dummy_workspace):
        client, http_client = elis_client
        http_client.create.return_value = dummy_workspace

        data = {
            "name": "Test Workspace",
            "organization": "https://elis.rossum.ai/api/v1/organizations/406",
        }

        workspace = await client.create_new_workspace(data)

        assert workspace == Workspace(**dummy_workspace)

        http_client.create.assert_called_with(Resource.Workspace, data)

    async def test_delete_workspace(self, elis_client, dummy_workspace):
        client, http_client = elis_client
        http_client.delete.return_value = None

        oid = dummy_workspace["id"]
        await client.delete_workspace(oid)

        http_client.delete.assert_called_with(Resource.Workspace, oid)


class TestWorkspacesSync:
    def test_list_workspaces(self, elis_client_sync, dummy_workspace):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_workspace,))

        workspaces = client.list_workspaces()

        for w in workspaces:
            assert w == Workspace(**dummy_workspace)

        http_client.fetch_resources.assert_called_with(Resource.Workspace, ())

    def test_retrieve_workspace(self, elis_client_sync, dummy_workspace):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_workspace

        oid = dummy_workspace["id"]
        workspace = client.retrieve_workspace(oid)

        assert workspace == Workspace(**dummy_workspace)

        http_client.fetch_resource.assert_called_with(Resource.Workspace, oid)

    def test_create_new_workspace(self, elis_client_sync, dummy_workspace):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_workspace

        data = {
            "name": "Test Workspace",
            "organization": "https://elis.rossum.ai/api/v1/organizations/406",
        }
        workspace = client.create_new_workspace(data)

        assert workspace == Workspace(**dummy_workspace)

        http_client.create.assert_called_with(Resource.Workspace, data)

    def test_delete_workspace(self, elis_client_sync, dummy_workspace):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        oid = dummy_workspace["id"]
        client.delete_workspace(oid)

        http_client.delete.assert_called_with(Resource.Workspace, oid)
