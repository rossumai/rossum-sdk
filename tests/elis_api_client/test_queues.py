from __future__ import annotations

import pytest
from mock import MagicMock, call, patch

from rossum_api.models.annotation import Annotation
from rossum_api.models.queue import Queue


@pytest.fixture
def dummy_queue():
    return {
        "id": 8198,
        "name": "Received invoices",
        "url": "https://elis.rossum.ai/api/v1/queues/8198",
        "workspace": "https://elis.rossum.ai/api/v1/workspaces/7540",
        "connector": None,
        "webhooks": [],
        "hooks": [],
        "schema": "https://elis.rossum.ai/api/v1/schemas/31336",
        "inbox": "https://elis.rossum.ai/api/v1/inboxes/1229",
        "users": ["https://elis.rossum.ai/api/v1/users/10775"],
        "session_timeout": "01:00:00",
        "rir_url": "https://all.rir.rossum.ai",
        "rir_params": None,
        "dedicated_engine": None,
        "generic_engine": "https://api.elis.develop.r8.lol/v1/generic_engines/1",
        "counts": {
            "importing": 0,
            "split": 0,
            "failed_import": 0,
            "to_review": 2,
            "reviewing": 0,
            "confirmed": 0,
            "exporting": 0,
            "postponed": 0,
            "failed_export": 0,
            "exported": 0,
            "deleted": 0,
            "purged": 0,
            "rejected": 0,
        },
        "default_score_threshold": 0.8,
        "automation_enabled": False,
        "automation_level": "never",
        "locale": "en_US",
        "metadata": {},
        "use_confirmed_state": False,
        "document_lifetime": "01:00:00",
        "settings": {
            "columns": [{"schema_id": "tags"}],
            "hide_export_button": True,
            "automation": {"automate_duplicates": True, "automate_suggested_edit": False},
            "rejection_config": {"enabled": True},
            "email_notifications": {
                "recipient": {"email": "john.doe@company.com", "name": "John Doe"},
                "unprocessable_attachments": False,
                "email_with_no_attachments": True,
                "postponed_annotations": False,
                "deleted_annotations": False,
            },
        },
    }


@pytest.fixture
def dummy_annotation():
    return {
        "id": 315777,
        "url": "https://elis.rossum.ai/api/v1/annotations/315777",
        "status": "exported",
        "arrived_at": "2019-10-13T21:33:01.509886Z",
        "exported_at": "2019-10-14T12:00:01.000133Z",
        "document": "https://elis.rossum.ai/api/v1/documents/315877",
        "modifier": None,
        "schema": "https://elis.rossum.ai/api/v1/schemas/31336",
        "metadata": {},
        "content": [
            {
                "category": "section",
                "schema_id": "invoice_details_section",
                "children": [
                    {
                        "category": "datapoint",
                        "schema_id": "document_id",
                        "value": "12345",
                        "type": "string",
                        "rir_confidence": 0.99,
                    },
                ],
            }
        ],
    }


@pytest.mark.asyncio
class TestQueues:
    async def test_list_all_queues(self, elis_client, dummy_queue, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_queue)

        queues = client.list_all_queues()

        async for q in queues:
            assert q == Queue(**dummy_queue)

        http_client.fetch_all.assert_called_with("queues", ())

    async def test_retrieve_queue(self, elis_client, dummy_queue):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_queue

        qid = dummy_queue["id"]
        queue = await client.retrieve_queue(qid)

        assert queue == Queue(**dummy_queue)

        http_client.fetch_one.assert_called_with("queues", qid)

    async def test_create_new_queue(self, elis_client, dummy_queue):
        client, http_client = elis_client
        http_client.create.return_value = dummy_queue

        data = {
            "name": "Test Queue",
            "workspace": "https://elis.rossum.ai/api/v1/workspaces/7540",
            "schema": "https://elis.rossum.ai/api/v1/schemas/31336",
        }
        queue = await client.create_new_queue(data)

        assert queue == Queue(**dummy_queue)

        http_client.create.assert_called_with("queues", data)

    async def test_delete_queue(self, elis_client, dummy_queue):
        client, http_client = elis_client
        http_client.delete.return_value = None

        qid = dummy_queue["id"]
        await client.delete_queue(qid)

        http_client.delete.assert_called_with("queues", qid)

    async def test_import_document(self, elis_client):
        client, http_client = elis_client

        results = [
            {
                "results": [
                    {
                        "annotation": "https://elis.rossum.ai/api/v1/annotations/111",
                        "document": "https://elis.rossum.ai/api/v1/documents/315",
                    }
                ]
            },
            {
                "results": [
                    {
                        "annotation": "https://elis.rossum.ai/api/v1/annotations/222",
                        "document": "https://elis.rossum.ai/api/v1/documents/316",
                    }
                ]
            },
        ]

        async def upload(resource, id_, fp, filename, *args, **kwargs):
            # asyncio.gather returns results in same order as the submitted tasks, however, it's
            # not guaranteed which request will fire first, we need to return correct result for
            # each file so the order of annotation_ids actually match. We cannot use simple
            # http_client.upload.side_effect = [list of results]
            return results[1] if "🎁" in filename else results[0]

        http_client.upload.side_effect = upload

        open_mock_first = MagicMock()
        open_mock_second = MagicMock()
        fp_mock = MagicMock()
        fp_mock.__aenter__.side_effect = [open_mock_first, open_mock_second]

        with patch("aiofiles.open", return_value=fp_mock):
            files = [
                ("tests/data/sample_invoice.pdf", "document.pdf"),
                ("tests/data/sample_invoice.pdf", "document 🎁.pdf"),
            ]
            annotation_ids = await client.import_document(
                queue_id=123, files=files, values={"a": 1}, metadata={"b": 2}
            )

        assert annotation_ids == [111, 222]
        calls = [
            call("queues", 123, open_mock_first, "document.pdf", {"a": 1}, {"b": 2}),
            call("queues", 123, open_mock_second, "document 🎁.pdf", {"a": 1}, {"b": 2}),
        ]
        http_client.upload.assert_has_calls(calls, any_order=True)

    async def test_export_annotations_to_json(self, elis_client, dummy_annotation, mock_generator):
        client, http_client = elis_client
        http_client.export.return_value = mock_generator(dummy_annotation)

        qid = 123
        export_format = "json"

        async for a in client.export_annotations_to_json(queue_id=qid):
            assert a == Annotation(**dummy_annotation)

        http_client.export.assert_called_with("queues", qid, export_format)

    async def test_export_annotations_to_file(self, elis_client, mock_file_read):
        client, http_client = elis_client
        http_client.export.return_value = mock_file_read("tests/data/annotation_export.xml")

        qid = 123
        export_format = "xml"

        result = []
        async for a in client.export_annotations_to_file(
            queue_id=qid, export_format=export_format
        ):
            result += a

        http_client.export.assert_called_with("queues", qid, export_format)

        with open("tests/data/annotation_export.xml", "rb") as fp:
            for i, line in enumerate(fp.read()):
                assert result[i] == line


class TestQueuesSync:
    def test_list_all_queues(self, elis_client_sync, dummy_queue, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_queue)

        queues = client.list_all_queues()

        for q in queues:
            assert q == Queue(**dummy_queue)

        http_client.fetch_all.assert_called_with("queues", ())

    def test_retrieve_queue(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_queue

        qid = dummy_queue["id"]
        queue = client.retrieve_queue(qid)

        assert queue == Queue(**dummy_queue)

        http_client.fetch_one.assert_called_with("queues", qid)

    def test_create_new_queue(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_queue

        data = {
            "name": "Test Queue",
            "workspace": "https://elis.rossum.ai/api/v1/workspaces/7540",
            "schema": "https://elis.rossum.ai/api/v1/schemas/31336",
        }
        queue = client.create_new_queue(data)

        assert queue == Queue(**dummy_queue)

        http_client.create.assert_called_with("queues", data)

    def test_import_document(self, elis_client_sync):
        client, http_client = elis_client_sync

        results = [
            {
                "results": [
                    {
                        "annotation": "https://elis.rossum.ai/api/v1/annotations/111",
                        "document": "https://elis.rossum.ai/api/v1/documents/315",
                    }
                ]
            },
            {
                "results": [
                    {
                        "annotation": "https://elis.rossum.ai/api/v1/annotations/222",
                        "document": "https://elis.rossum.ai/api/v1/documents/316",
                    }
                ]
            },
        ]

        async def upload(resource, id_, fp, filename, *args, **kwargs):
            # asyncio.gather returns results in same order as the submitted tasks, however, it's
            # not guaranteed which request will fire first, we need to return correct result for
            # each file so the order of annotation_ids actually match. We cannot use simple
            # http_client.upload.side_effect = [list of results]
            return results[1] if "🎁" in filename else results[0]

        http_client.upload.side_effect = upload

        open_mock_first = MagicMock()
        open_mock_second = MagicMock()
        fp_mock = MagicMock()
        fp_mock.__aenter__.side_effect = [open_mock_first, open_mock_second]

        with patch("aiofiles.open", return_value=fp_mock):
            files = [
                ("tests/data/sample_invoice.pdf", "document.pdf"),
                ("tests/data/sample_invoice.pdf", "document 🎁.pdf"),
            ]
            annotation_ids = client.import_document(
                queue_id=123, files=files, values={"a": 1}, metadata={"b": 2}
            )

        assert annotation_ids == [111, 222]
        calls = [
            call("queues", 123, open_mock_first, "document.pdf", {"a": 1}, {"b": 2}),
            call("queues", 123, open_mock_second, "document 🎁.pdf", {"a": 1}, {"b": 2}),
        ]

        http_client.upload.assert_has_calls(calls, any_order=True)

    def test_delete_schema(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        qid = dummy_queue["id"]
        client.delete_queue(qid)

        http_client.delete.assert_called_with("queues", qid)

    def test_export_annotations_to_json(self, elis_client_sync, dummy_annotation, mock_generator):
        client, http_client = elis_client_sync
        http_client.export.return_value = mock_generator(dummy_annotation)

        qid = 123
        export_format = "json"

        for a in client.export_annotations_to_json(queue_id=qid):
            assert a == Annotation(**dummy_annotation)

        http_client.export.assert_called_with("queues", qid, export_format)

    def test_export_annotations_to_file(self, elis_client_sync, mock_file_read):
        client, http_client = elis_client_sync
        http_client.export.return_value = mock_file_read("tests/data/annotation_export.xml")

        qid = 123
        export_format = "xml"

        result = []
        for a in client.export_annotations_to_file(queue_id=qid, export_format=export_format):
            result += a

        http_client.export.assert_called_with("queues", qid, export_format)

        with open("tests/data/annotation_export.xml", "rb") as fp:
            for i, line in enumerate(fp.read()):
                assert result[i] == line
