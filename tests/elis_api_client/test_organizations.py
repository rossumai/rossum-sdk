from __future__ import annotations

from unittest.mock import call

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.organization import Organization


@pytest.fixture
def dummy_organization():
    return {
        "id": 406,
        "url": "https://elis.rossum.ai/api/v1/organizations/406",
        "name": "East West Trading Co",
        "workspaces": ["https://elis.rossum.ai/api/v1/workspaces/7540"],
        "users": ["https://elis.rossum.ai/api/v1/users/10775"],
        "organization_group": "https://elis.rossum.ai/api/v1/organization_groups/17",
        "ui_settings": {},
        "metadata": {},
        "created_at": "2019-09-02T14:28:11.000000Z",
        "trial_expires_at": "2020-09-02T14:28:11.000000Z",
        "is_trial": True,
        "oidc_provider": "some_oidc_provider",
    }


@pytest.mark.asyncio
class TestOrganizations:
    async def test_list_organizations(self, elis_client, dummy_organization, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_organization)

        organizations = client.list_organizations()

        async for o in organizations:
            assert o == Organization(**dummy_organization)

        http_client.fetch_all.assert_called_with(Resource.Organization, ())

    async def test_retrieve_organization(self, elis_client, dummy_organization):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_organization

        oid = dummy_organization["id"]
        organization = await client.retrieve_organization(oid)

        assert organization == Organization(**dummy_organization)

        http_client.fetch_one.assert_called_with(Resource.Organization, oid)

    async def test_retrieve_own_organization(self, elis_client, dummy_user, dummy_organization):
        client, http_client = elis_client
        http_client.fetch_one.side_effect = [dummy_user, dummy_organization]

        organization = await client.retrieve_own_organization()

        assert organization == Organization(**dummy_organization)

        http_client.fetch_one.assert_has_calls(
            [call(Resource.Auth, "user"), call(Resource.Organization, 406)]
        )


class TestOrganizationsSync:
    def test_list_organizations(self, elis_client_sync, dummy_organization):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_organization,))

        organizations = client.list_organizations()

        for o in organizations:
            assert o == Organization(**dummy_organization)

        http_client.fetch_resources.assert_called_with(Resource.Organization, ())

    def test_retrieve_organization(self, elis_client_sync, dummy_organization):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_organization

        oid = dummy_organization["id"]
        organization = client.retrieve_organization(oid)

        assert organization == Organization(**dummy_organization)

        http_client.fetch_resource.assert_called_with(Resource.Organization, oid)

    def test_retrieve_my_organization(self, elis_client_sync, dummy_user, dummy_organization):
        client, http_client = elis_client_sync
        http_client.fetch_resource.side_effect = [dummy_user, dummy_organization]

        organization = client.retrieve_my_organization()

        assert organization == Organization(**dummy_organization)

        http_client.fetch_resource.assert_has_calls(
            [call(Resource.Auth, "user"), call(Resource.Organization, 406)]
        )
