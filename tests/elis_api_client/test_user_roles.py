from __future__ import annotations

import pytest

from rossum_api.models.user_role import UserRole


@pytest.fixture
def dummy_user_role():
    return {"id": 3, "url": "https://elis.rossum.ai/api/v1/groups/3", "name": "admin"}


@pytest.mark.asyncio
class TestWorkspaces:
    async def test_list_all_user_roles(self, elis_client, dummy_user_role, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_user_role)

        user_roles = client.list_all_user_roles()

        async for u in user_roles:
            assert u == UserRole(**dummy_user_role)

        http_client.fetch_all.assert_called_with("groups", ())


class TestWorkspacesAsync:
    def test_list_all_user_roles(self, elis_client_sync, dummy_user_role, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_user_role)

        user_roles = client.list_all_user_roles()

        for u in user_roles:
            assert u == UserRole(**dummy_user_role)

        http_client.fetch_all.assert_called_with("groups", ())
