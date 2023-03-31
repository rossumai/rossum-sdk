from __future__ import annotations

import pytest

from rossum_api.models.user import User


@pytest.mark.asyncio
class TestUsers:
    async def test_list_all_users(self, elis_client, dummy_user, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_user)

        users = client.list_all_users()

        async for u in users:
            assert u == User(**dummy_user)

        http_client.fetch_all.assert_called_with("users", ())

    async def test_retrieve_user(self, elis_client, dummy_user):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_user

        uid = dummy_user["id"]
        user = await client.retrieve_user(uid)

        assert user == User(**dummy_user)

        http_client.fetch_one.assert_called_with("users", uid)

    async def test_create_new_user(self, elis_client, dummy_user):
        client, http_client = elis_client
        http_client.create.return_value = dummy_user

        data = {
            "organization": "https://elis.rossum.ai/api/v1/organizations/406",
            "username": "jane@east-west-trading.com",
            "email": "jane@east-west-trading.com",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
            "groups": ["https://elis.rossum.ai/api/v1/groups/2"],
        }
        user = await client.create_new_user(data)

        assert user == User(**dummy_user)

        http_client.create.assert_called_with("users", data)


class TestUsersSync:
    def test_list_all_users(self, elis_client_sync, dummy_user, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_user)

        users = client.list_all_users()

        for u in users:
            assert u == User(**dummy_user)

        http_client.fetch_all.assert_called_with("users", ())

    def test_retrieve_user(self, elis_client_sync, dummy_user):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_user

        uid = dummy_user["id"]
        user = client.retrieve_user(uid)

        assert user == User(**dummy_user)

        http_client.fetch_one.assert_called_with("users", uid)

    def test_create_new_user(self, elis_client_sync, dummy_user):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_user

        data = {
            "organization": "https://elis.rossum.ai/api/v1/organizations/406",
            "username": "jane@east-west-trading.com",
            "email": "jane@east-west-trading.com",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
            "groups": ["https://elis.rossum.ai/api/v1/groups/2"],
        }
        user = client.create_new_user(data)

        assert user == User(**dummy_user)

        http_client.create.assert_called_with("users", data)
