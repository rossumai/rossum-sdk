import pytest

from rossum_ng.models.organization import Organization


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
    async def test_get_organizations(self, elis_client, dummy_organization, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_organization)

        organizations = client.list_all_organizations()

        async for o in organizations:
            assert o == Organization(**dummy_organization)

        http_client.fetch_all.assert_called_with("organizations", ())

    async def test_get_organization(self, elis_client, dummy_organization):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_organization

        oid = dummy_organization["id"]
        organization = await client.retrieve_organization(oid)

        assert organization == Organization(**dummy_organization)

        http_client.fetch_one.assert_called_with("organizations", oid)


class TestOrganizationsSync:
    def test_get_organizations(self, elis_client_sync, dummy_organization, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_organization)

        organizations = client.list_all_organizations()

        for o in organizations:
            assert o == Organization(**dummy_organization)

        http_client.fetch_all.assert_called_with("organizations", ())

    def test_get_organization(self, elis_client_sync, dummy_organization):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_organization

        oid = dummy_organization["id"]
        organization = client.retrieve_organization(oid)

        assert organization == Organization(**dummy_organization)

        http_client.fetch_one.assert_called_with("organizations", oid)
