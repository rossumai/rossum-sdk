from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.hook import Hook


@pytest.fixture
def dummy_hook():
    return {
        "id": 1500,
        "type": "webhook",
        "url": "https://elis.rossum.ai/api/v1/hooks/1500",
        "name": "Change of Status",
        "metadata": {},
        "queues": [
            "https://elis.rossum.ai/api/v1/queues/8199",
            "https://elis.rossum.ai/api/v1/queues/8191",
        ],
        "run_after": [],
        "sideload": ["queues"],
        "active": True,
        "events": ["annotation_status"],
        "config": {
            "url": "https://myq.east-west-trading.com/api/hook1?strict=true",
            "secret": "secret-token",
            "insecure_ssl": False,
            "client_ssl_certificate": "-----BEGIN CERTIFICATE-----\n...",
        },
        "test": {"saved_input": {...}},
        "extension_source": "custom",
        "settings": {},
        "settings_schema": {"type": "object", "properties": {}},
        "secrets": {},
        "guide": "Here we explain how the extension should be used.",
        "read_more_url": "https://github.com/rossumai/simple-vendor-matching-webhook-python",
        "extension_image_url": "https://rossum.ai/wp-content/themes/rossum/static/img/logo.svg",
    }


@pytest.mark.asyncio
class TestHooks:
    async def test_list_hooks(self, elis_client, dummy_hook, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_hook)

        hooks = client.list_hooks()

        async for h in hooks:
            assert h == Hook(**dummy_hook)

        http_client.fetch_all.assert_called_with(Resource.Hook, ())

    async def test_retrieve_hook(self, elis_client, dummy_hook):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_hook

        uid = dummy_hook["id"]
        hook = await client.retrieve_hook(uid)

        assert hook == Hook(**dummy_hook)

        http_client.fetch_one.assert_called_with(Resource.Hook, uid)

    async def test_create_new_hook(self, elis_client, dummy_hook):
        client, http_client = elis_client
        http_client.create.return_value = dummy_hook

        data = {
            "name": "MyQ Hook",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
            "config": {"url": "https://myq.east-west-trading.com"},
            "events": [],
        }
        hook = await client.create_new_hook(data)

        assert hook == Hook(**dummy_hook)

        http_client.create.assert_called_with(Resource.Hook, data)

    async def test_update_part_hook(self, elis_client, dummy_hook):
        client, http_client = elis_client
        http_client.update.return_value = dummy_hook

        hid = dummy_hook["id"]
        data = {
            "name": "New Hook Name",
        }
        hook = await client.update_part_hook(hid, data)

        assert hook == Hook(**dummy_hook)

        http_client.update.assert_called_with(Resource.Hook, hid, data)

    async def test_delete_hook(self, elis_client, dummy_hook):
        client, http_client = elis_client
        http_client.delete.return_value = None

        hid = dummy_hook["id"]
        await client.delete_hook(hid)

        http_client.delete.assert_called_with(Resource.Hook, hid)


class TestHooksSync:
    def test_list_hooks(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_hook,))

        hooks = client.list_hooks()

        for h in hooks:
            assert h == Hook(**dummy_hook)

        http_client.fetch_resources.assert_called_with(Resource.Hook, ())

    def test_retrieve_hook(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_hook

        uid = dummy_hook["id"]
        hook = client.retrieve_hook(uid)

        assert hook == Hook(**dummy_hook)

        http_client.fetch_resource.assert_called_with(Resource.Hook, uid)

    def test_create_new_hook(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_hook

        data = {
            "name": "MyQ Hook",
            "queues": ["https://elis.rossum.ai/api/v1/queues/8199"],
            "config": {"url": "https://myq.east-west-trading.com"},
            "events": [],
        }
        hook = client.create_new_hook(data)

        assert hook == Hook(**dummy_hook)

        http_client.create.assert_called_with(Resource.Hook, data)

    def test_update_part_hook(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.update.return_value = dummy_hook

        hid = dummy_hook["id"]
        data = {
            "name": "New Hook Name",
        }
        hook = client.update_part_hook(hid, data)

        assert hook == Hook(**dummy_hook)

        http_client.update.assert_called_with(Resource.Hook, hid, data)

    def test_delete_hook(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        hid = dummy_hook["id"]
        client.delete_hook(hid)

        http_client.delete.assert_called_with(Resource.Hook, hid)
