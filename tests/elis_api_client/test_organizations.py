import pytest
from rossum_ng.models.organization import Organization
from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.api_client import APIClient


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


class TestOrganizations:
    def test_get_organizations(self, http_client: APIClient, dummy_organization):
        http_client.get.return_value = [dummy_organization]

        client = ElisAPIClient(http_client=http_client)
        organizations = client.get_organizations()

        assert list(organizations) == [Organization(**dummy_organization)]

        http_client.get.assert_called()
        http_client.get.assert_called_with(f"/organizations", {})

    def test_get_organization(self, http_client: APIClient, dummy_organization):
        http_client.get.return_value = dummy_organization

        client = ElisAPIClient(http_client=http_client)
        oid = dummy_organization["id"]
        organization = client.get_organization(oid)

        assert organization == Organization(**dummy_organization)

        http_client.get.assert_called()
        http_client.get.assert_called_with(f"/organizations/{oid}")
