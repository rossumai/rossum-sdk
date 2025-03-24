from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.engine import Engine, EngineField
from rossum_api.models.queue import Queue

TEST_ENGINE_ID = 123


@pytest.mark.asyncio
class TestEngine:
    @pytest.fixture
    def dummy_engine(self):
        # https://elis.rossum.ai/api/docs/internal/#engine
        return {
            "id": TEST_ENGINE_ID,
            "url": f"https://elis.rossum.ai/api/v1/engines/{TEST_ENGINE_ID}",
            "name": "test_engine",
            "type": "extractor",
            "learning_enabled": False,
            "description": "Test engine",
            "agenda_id": "test_agenda_id",
        }

    async def test_retrieve_engine(self, elis_client, dummy_engine):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_engine

        engine: Engine = await client.retrieve_engine(TEST_ENGINE_ID)

        assert engine == Engine(**dummy_engine)
        http_client.fetch_one.assert_called_with(Resource.Engine, TEST_ENGINE_ID)

    async def test_list_engines(self, elis_client, dummy_engine, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_engine)

        engines = client.list_engines()

        async for engine in engines:
            assert engine == Engine(**dummy_engine)

        http_client.fetch_all.assert_called_with(Resource.Engine, (), ())

    async def test_retrieve_engine_queues(self, elis_client, dummy_queue, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_queue)

        queues = client.retrieve_engine_queues(TEST_ENGINE_ID)

        async for queue in queues:
            assert queue == Queue(**dummy_queue)

        http_client.fetch_all.assert_called_with(Resource.Queue, engine=TEST_ENGINE_ID)


@pytest.mark.asyncio
class TestEngineFields:
    @pytest.fixture
    def dummy_engine_field(self):
        # https://elis.rossum.ai/api/docs/internal/#engine-field
        return {
            "id": 456,  # EngineField ID, not the Engine ID
            "url": f"https://elis.rossum.ai/api/v1/engine_fields/{TEST_ENGINE_ID}",
            "engine": f"https://elis.rossum.ai/api/v1/engines/{TEST_ENGINE_ID}",
            "name": f"test_engine_field_{TEST_ENGINE_ID}",
            "label": "Test engine field",
            "type": "string",
            "subtype": "alphanumeric",
            "pre_trained_field_id": "document_id",  # https://elis.rossum.ai/api/docs/internal/#get-list-of-possible-pre_trained_field_id-fields
            "tabular": False,
            "multiline": "false",
        }

    async def test_retrieve_engine_fields(self, elis_client, dummy_engine_field, mock_generator):
        client, http_client = elis_client

        http_client.fetch_all.return_value = mock_generator(dummy_engine_field)

        engine_fields = client.retrieve_engine_fields(TEST_ENGINE_ID)

        async for engine_field in engine_fields:
            assert engine_field == EngineField(**dummy_engine_field)

        http_client.fetch_all.assert_called_with(Resource.EngineField, engine=TEST_ENGINE_ID)
