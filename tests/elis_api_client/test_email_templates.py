from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.email_template import EmailTemplate


@pytest.fixture
def dummy_email_template():
    return {
        "id": 1500,
        "name": "My email_template",
        "queue": "https://elis.rossum.ai/api/v1/queues/8199",
        "url": "https://elis.rossum.ai/api/v1/email_templates/1500",
        "organization": "https://elis.rossum.ai/api/v1/organizations/1500",
        "subject": "test subject",
        "message": "Hehe",
        "type": "custom",
        "enabled": True,
        "automate": False,
        "triggers": [],
        "to": [],
        "cc": [],
        "bcc": [],
    }


@pytest.mark.asyncio
class TestEmailTemplates:
    async def test_list_email_templates(self, elis_client, dummy_email_template, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_email_template)

        email_templates = client.list_email_templates()

        async for c in email_templates:
            assert c == EmailTemplate(**dummy_email_template)

        http_client.fetch_all.assert_called_with(Resource.EmailTemplate, ())

    @pytest.mark.asyncio
    async def test_retrieve_email_template(self, elis_client, dummy_email_template):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_email_template

        cid = dummy_email_template["id"]
        email_template = await client.retrieve_email_template(cid)

        assert email_template == EmailTemplate(**dummy_email_template)

        http_client.fetch_one.assert_called_with(Resource.EmailTemplate, cid)

    async def test_create_new_email_template(self, elis_client, dummy_email_template):
        client, http_client = elis_client
        http_client.create.return_value = dummy_email_template

        data = {
            "name": "MyQ email_template",
            "queue": "https://elis.rossum.ai/api/v1/queues/8199",
            "subject": "Subject",
            "message": "<p>My Email Template Message</p>",
            "type": "custom",
        }
        email_template = await client.create_new_email_template(data)

        assert email_template == EmailTemplate(**dummy_email_template)

        http_client.create.assert_called_with(Resource.EmailTemplate, data)


class TestEmailTemplatesSync:
    def test_list_email_templates(self, elis_client_sync, dummy_email_template):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_email_template,))

        email_templates = client.list_email_templates()

        for c in email_templates:
            assert c == EmailTemplate(**dummy_email_template)

        http_client.fetch_resources.assert_called_with(Resource.EmailTemplate, ())

    def test_retrieve_email_template(self, elis_client_sync, dummy_email_template):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_email_template

        cid = dummy_email_template["id"]
        email_template = client.retrieve_email_template(cid)

        assert email_template == EmailTemplate(**dummy_email_template)

        http_client.fetch_resource.assert_called_with(Resource.EmailTemplate, cid)

    def test_create_new_email_template(self, elis_client_sync, dummy_email_template):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_email_template

        data = {
            "name": "MyQ email_template",
            "queue": "https://elis.rossum.ai/api/v1/queues/8199",
            "subject": "Subject",
            "message": "<p>My Email Template Message</p>",
            "type": "custom",
        }
        email_template = client.create_new_email_template(data)

        assert email_template == EmailTemplate(**dummy_email_template)

        http_client.create.assert_called_with(Resource.EmailTemplate, data)
