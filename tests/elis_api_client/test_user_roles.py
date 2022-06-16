import pytest

from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.api_client import APIClient
from rossum_ng.models.user_role import UserRole


@pytest.fixture
def dummy_user_role():
    return {"id": 3, "url": "https://elis.rossum.ai/api/v1/groups/3", "name": "admin"}


@pytest.mark.asyncio
class TestWorkspaces:
    async def test_list_all_user_roles(
        self, http_client: APIClient, dummy_user_role, mock_generator
    ):
        http_client.fetch_all.return_value = mock_generator(dummy_user_role)

        client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
        user_roles = client.list_all_user_roles()

        async for u in user_roles:
            assert u == UserRole(**dummy_user_role)

        http_client.fetch_all.assert_called_with("groups", ())
