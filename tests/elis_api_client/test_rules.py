from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.rule import Rule, RuleAction


@pytest.fixture
def dummy_rule():
    return {
        "id": 123,
        "url": "https://elis.rossum.ai/api/v1/rules/123",
        "name": "rule",
        "enabled": True,
        "organization": "https://elis.rossum.ai/api/v1/organizations/1001",
        "schema": "https://elis.rossum.ai/api/v1/schemas/1001",
        "trigger_condition": "True",
        "created_by": "https://elis.rossum.ai/api/v1/users/9524",
        "created_at": "2022-01-01T15:02:25.653324Z",
        "modified_by": "https://elis.rossum.ai/api/v1/users/2345",
        "modified_at": "2020-01-01T10:08:03.856648Z",
        "rule_template": None,
        "synchronized_from_template": False,
        "actions": [
            {
                "id": "f3c43f16-b5f1-4ac8-b789-17d4c26463d7",
                "enabled": True,
                "type": "show_message",
                "payload": {
                    "type": "error",
                    "content": "Error message!",
                    "schema_id": "invoice_id",
                },
                "event": "validation",
            }
        ],
    }


@pytest.fixture
def expected_rule(dummy_rule):
    """Creates a Rule object with properly constructed RuleAction objects."""
    rule_data = dummy_rule.copy()
    rule_data["actions"] = [RuleAction(**action) for action in dummy_rule["actions"]]
    return Rule(**rule_data)


@pytest.mark.asyncio
class TestRules:
    async def test_list_rules(self, elis_client, dummy_rule, expected_rule, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_rule)

        rules = client.list_rules()

        async for r in rules:
            assert r == expected_rule

        http_client.fetch_all.assert_called_with(Resource.Rule, ())

    async def test_retrieve_rule(self, elis_client, dummy_rule, expected_rule):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_rule

        uid = dummy_rule["id"]
        rule = await client.retrieve_rule(uid)

        assert rule == expected_rule

        http_client.fetch_one.assert_called_with(Resource.Rule, uid)

    async def test_create_new_rule(self, elis_client, dummy_rule, expected_rule):
        client, http_client = elis_client
        http_client.create.return_value = dummy_rule

        data = {
            "name": "Test Rule",
            "schema": "https://elis.rossum.ai/api/v1/schemas/1001",
            "trigger_condition": "True",
            "actions": [],
        }
        rule = await client.create_new_rule(data)

        assert rule == expected_rule

        http_client.create.assert_called_with(Resource.Rule, data)

    async def test_create_new_rule_with_formula_condition(self, elis_client, dummy_rule):
        client, http_client = elis_client
        formula_condition = "field.amount > 100"
        response_rule = {**dummy_rule, "trigger_condition": formula_condition}
        http_client.create.return_value = response_rule

        data = {
            "name": "Test Rule with Formula",
            "schema": "https://elis.rossum.ai/api/v1/schemas/1001",
            "trigger_condition": formula_condition,
            "actions": [],
        }
        rule = await client.create_new_rule(data)

        assert rule.trigger_condition == formula_condition
        http_client.create.assert_called_with(Resource.Rule, data)

    async def test_update_part_rule(self, elis_client, dummy_rule, expected_rule):
        client, http_client = elis_client
        http_client.update.return_value = dummy_rule

        rid = dummy_rule["id"]
        data = {
            "name": "New Rule Name",
        }
        rule = await client.update_part_rule(rid, data)

        assert rule == expected_rule

        http_client.update.assert_called_with(Resource.Rule, rid, data)

    async def test_delete_rule(self, elis_client, dummy_rule):
        client, http_client = elis_client
        http_client.delete.return_value = None

        rid = dummy_rule["id"]
        await client.delete_rule(rid)

        http_client.delete.assert_called_with(Resource.Rule, rid)


class TestRulesSync:
    def test_list_rules(self, elis_client_sync, dummy_rule, expected_rule):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_rule,))

        rules = client.list_rules()

        for r in rules:
            assert r == expected_rule

        http_client.fetch_resources.assert_called_with(Resource.Rule, ())

    def test_retrieve_rule(self, elis_client_sync, dummy_rule, expected_rule):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_rule

        uid = dummy_rule["id"]
        rule = client.retrieve_rule(uid)

        assert rule == expected_rule

        http_client.fetch_resource.assert_called_with(Resource.Rule, uid)

    def test_create_new_rule(self, elis_client_sync, dummy_rule, expected_rule):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_rule

        data = {
            "name": "Test Rule",
            "schema": "https://elis.rossum.ai/api/v1/schemas/1001",
            "trigger_condition": "True",
            "actions": [],
        }
        rule = client.create_new_rule(data)

        assert rule == expected_rule

        http_client.create.assert_called_with(Resource.Rule, data)

    def test_create_new_rule_with_formula_condition(self, elis_client_sync, dummy_rule):
        client, http_client = elis_client_sync
        formula_condition = "field.amount > 100"
        response_rule = {**dummy_rule, "trigger_condition": formula_condition}
        http_client.create.return_value = response_rule

        data = {
            "name": "Test Rule with Formula",
            "schema": "https://elis.rossum.ai/api/v1/schemas/1001",
            "trigger_condition": formula_condition,
            "actions": [],
        }
        rule = client.create_new_rule(data)

        assert rule.trigger_condition == formula_condition
        http_client.create.assert_called_with(Resource.Rule, data)

    def test_update_part_rule(self, elis_client_sync, dummy_rule, expected_rule):
        client, http_client = elis_client_sync
        http_client.update.return_value = dummy_rule

        rid = dummy_rule["id"]
        data = {
            "name": "New Rule Name",
        }
        rule = client.update_part_rule(rid, data)

        assert rule == expected_rule

        http_client.update.assert_called_with(Resource.Rule, rid, data)

    def test_delete_rule(self, elis_client_sync, dummy_rule):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        rid = dummy_rule["id"]
        client.delete_rule(rid)

        http_client.delete.assert_called_with(Resource.Rule, rid)
