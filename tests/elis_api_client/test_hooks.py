from __future__ import annotations

import json

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.hook import Hook, HookRunData


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


@pytest.fixture
def dummy_hook_run_data():
    return {
        "log_level": "INFO",
        "action": "received",
        "event": "email",
        "request_id": "493178e7-3c4e-4015-82f3-3d9280a90ce4",
        "organization_id": 75,
        "hook_id": 61,
        "hook_type": "function",
        "queue_id": 205,
        "annotation_id": None,
        "email_id": 80,
        "message": "",
        "request": json.dumps(
            {
                "request_id": "493178e7-3c4e-4015-82f3-3d9280a90ce4",
                "timestamp": "2023-04-29T21:56:36.556422Z",
                "hook": "https://api-5462-39.review.r8.lol/v1/hooks/61",
                "action": "received",
                "event": "email",
                "rossum_authorization_token": "b259cd74b9a53ee01ea1ec5e358f1bcd01742bd2",
                "base_url": "https://5462-39.review.r8.lol",
                "settings": {},
                "headers": {
                    "from": "uptime-test@elis.develop.r8.lol",
                    "to": "test-email-prefix-f5a616@5462-39.review.r8.lol",
                    "reply-to": "reply-to@elis.develop.r8.lol",
                    "subject": "Sample invoice file",
                    "date": "Sat, 29 Apr 2023 21:56:35 +0000",
                    "message-id": "<01020187cf04903f-09cf6c13-2273-4523-bb3c-c845ba955ec8-000000@eu-west-1.amazonses.com>",
                    "authentication-results": "OpenDMARC; dmarc=none (p=none dis=none) header.from=elis.develop.r8.lol",
                },
                "body": {
                    "body_text_plain": "Subject: Test email python\\n\\nBody of your message!",
                    "body_text_html": None,
                },
                "files": [
                    {
                        "id": "1",
                        "filename": "file-2BCmvbISxmhM",
                        "mime_type": "application/pdf",
                        "n_pages": 2,
                        "width_px": 3300.0,
                        "height_px": 2550.0,
                        "document": "https://api-5462-39.review.r8.lol/v1/documents/190",
                    }
                ],
                "email": "https://api-5462-39.review.r8.lol/v1/emails/80",
                "queue": "https://api-5462-39.review.r8.lol/v1/queues/205",
            }
        ),
        "response": json.dumps({"files": []}),
        "start": "2023-04-29T21:56:36.556422Z",
        "end": "2023-04-29T21:56:37.516069Z",
        "settings": {},
        "status": None,
        "status_code": None,
        "timestamp": "2023-04-29T21:56:37.516069Z",
        "uuid": "593178e7-3c4e-4015-82f3-3d9280a90ce4",
        "output": None,
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

    async def test_list_hook_run_data(self, elis_client, dummy_hook_run_data, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_hook_run_data)

        hook_run_data = client.list_hook_run_data()

        async for data in hook_run_data:
            assert data == HookRunData(**dummy_hook_run_data)

        http_client.fetch_all.assert_called_with(Resource.HookRunData)

    async def test_list_hook_run_data_with_filters(
        self, elis_client, dummy_hook_run_data, mock_generator
    ):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_hook_run_data)

        filters = {"hook": 1500, "log_level": "INFO", "status_code": 200}
        hook_run_data = client.list_hook_run_data(**filters)

        async for data in hook_run_data:
            assert data == HookRunData(**dummy_hook_run_data)

        http_client.fetch_all.assert_called_with(
            Resource.HookRunData, hook=1500, log_level="INFO", status_code=200
        )


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

    def test_list_hook_run_data(self, elis_client_sync, dummy_hook_run_data):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_hook_run_data,))

        hook_run_data = client.list_hook_run_data()

        for data in hook_run_data:
            assert data == HookRunData(**dummy_hook_run_data)

        http_client.fetch_resources.assert_called_with(Resource.HookRunData)

    def test_list_hook_run_data_with_filters(self, elis_client_sync, dummy_hook_run_data):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_hook_run_data,))

        filters = {"hook": 1500, "log_level": "INFO", "status_code": 200}
        hook_run_data = client.list_hook_run_data(**filters)

        for data in hook_run_data:
            assert data == HookRunData(**dummy_hook_run_data)

        http_client.fetch_resources.assert_called_with(
            Resource.HookRunData, hook=1500, log_level="INFO", status_code=200
        )
