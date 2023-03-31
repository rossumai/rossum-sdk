from __future__ import annotations

import pytest

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
    async def test_list_all_hooks(self, elis_client, dummy_hook, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_hook)

        hooks = client.list_all_hooks()

        async for h in hooks:
            assert h == Hook(**dummy_hook)

        http_client.fetch_all.assert_called_with("hooks", ())

    async def test_retrieve_user(self, elis_client, dummy_hook):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_hook

        uid = dummy_hook["id"]
        hook = await client.retrieve_hook(uid)

        assert hook == Hook(**dummy_hook)

        http_client.fetch_one.assert_called_with("hooks", uid)

    async def test_create_new_user(self, elis_client, dummy_hook):
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

        http_client.create.assert_called_with("hooks", data)


class TestHooksAsync:
    def test_list_all_hooks(self, elis_client_sync, dummy_hook, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_hook)

        hooks = client.list_all_hooks()

        for h in hooks:
            assert h == Hook(**dummy_hook)

        http_client.fetch_all.assert_called_with("hooks", ())

    def test_retrieve_user(self, elis_client_sync, dummy_hook):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_hook

        uid = dummy_hook["id"]
        hook = client.retrieve_hook(uid)

        assert hook == Hook(**dummy_hook)

        http_client.fetch_one.assert_called_with("hooks", uid)

    def test_create_new_user(self, elis_client_sync, dummy_hook):
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

        http_client.create.assert_called_with("hooks", data)
