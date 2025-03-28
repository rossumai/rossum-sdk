from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from rossum_api.domain_logic.annotations import ExportFileFormats
from rossum_api.domain_logic.resources import Resource
from rossum_api.models.annotation import Annotation
from rossum_api.models.queue import Queue
from rossum_api.models.task import Task, TaskStatus, TaskType


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
    async def test_list_queues(self, elis_client, dummy_queue, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_queue)

        queues = client.list_queues()

        async for q in queues:
            assert q == Queue(**dummy_queue)

        http_client.fetch_all.assert_called_with(Resource.Queue, ())

    async def test_retrieve_queue(self, elis_client, dummy_queue):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_queue

        qid = dummy_queue["id"]
        queue = await client.retrieve_queue(qid)

        assert queue == Queue(**dummy_queue)

        http_client.fetch_one.assert_called_with(Resource.Queue, qid)

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

        http_client.create.assert_called_with(Resource.Queue, data)

    async def test_delete_queue(self, elis_client, dummy_queue):
        client, http_client = elis_client
        http_client.delete.return_value = None

        qid = dummy_queue["id"]
        await client.delete_queue(qid)

        http_client.delete.assert_called_with(Resource.Queue, qid)

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
            call(Resource.Queue, 123, open_mock_first, "document.pdf", {"a": 1}, {"b": 2}),
            call(Resource.Queue, 123, open_mock_second, "document 🎁.pdf", {"a": 1}, {"b": 2}),
        ]
        http_client.upload.assert_has_calls(calls, any_order=True)

    async def test_create_upload(self, elis_client):
        client, http_client = elis_client

        dummy_task = Task(
            id=16508,
            url="https://api.elis.master.r8.lol/v1/tasks/16508",
            type=TaskType.UPLOAD_CREATED,
            status=TaskStatus.RUNNING,
            detail=None,
            expires_at="2024-07-31T19:06:47.916608Z",
            content={"upload": "https://api.elis.master.r8.lol/v1/uploads/37626"},
            result_url="https://api.elis.master.r8.lol/v1/uploads/37626",
        )

        dummy_task_two = Task(
            id=16509,
            url="https://api.elis.master.r8.lol/v1/tasks/16509",
            type=TaskType.UPLOAD_CREATED,
            status=TaskStatus.RUNNING,
            detail=None,
            expires_at="2024-07-31T19:06:47.916608Z",
            content={"upload": "https://api.elis.master.r8.lol/v1/uploads/37626"},
            result_url="https://api.elis.master.r8.lol/v1/uploads/37626",
        )

        client._create_upload = AsyncMock(side_effect=[dummy_task, dummy_task_two])
        files = [
            ("tests/data/sample_invoice.pdf", "document.pdf"),
            ("tests/data/sample_invoice.pdf", "document_test.pdf"),
        ]
        tasks = await client.upload_document(
            queue_id=123, files=files, values={"a": 1}, metadata={"b": 2}
        )

        assert tasks == [dummy_task, dummy_task_two]
        calls = [
            call("tests/data/sample_invoice.pdf", 123, "document.pdf", {"a": 1}, {"b": 2}),
            call("tests/data/sample_invoice.pdf", 123, "document_test.pdf", {"a": 1}, {"b": 2}),
        ]

        client._create_upload.assert_has_calls(calls, any_order=True)

    async def test_export_annotations_to_json(self, elis_client, dummy_annotation, mock_generator):
        client, http_client = elis_client
        http_client.export.return_value = mock_generator(dummy_annotation)

        qid = 123
        export_format = "json"

        async for a in client.export_annotations_to_json(queue_id=qid):
            assert a == Annotation(**dummy_annotation)

        http_client.export.assert_called_with(Resource.Queue, qid, export_format)

    async def test_export_annotations_to_file(self, elis_client, mock_file_read):
        client, http_client = elis_client
        http_client.export.return_value = mock_file_read("tests/data/annotation_export.xml")

        qid = 123
        export_format = ExportFileFormats.XML

        result = b""
        async for a in client.export_annotations_to_file(
            queue_id=qid, export_format=export_format
        ):
            result += a

        http_client.export.assert_called_with(Resource.Queue, qid, export_format.value)

        with open("tests/data/annotation_export.xml", "rb") as fp:
            assert result == fp.read()


class TestQueuesSync:
    def test_list_queues(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_queue,))

        queues = client.list_queues()

        for q in queues:
            assert q == Queue(**dummy_queue)

        http_client.fetch_resources.assert_called_with(Resource.Queue, ())

    def test_retrieve_queue(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_queue

        qid = dummy_queue["id"]
        queue = client.retrieve_queue(qid)

        assert queue == Queue(**dummy_queue)

        http_client.fetch_resource.assert_called_with(Resource.Queue, qid)

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

        http_client.create.assert_called_with(Resource.Queue, data)

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
        http_client.upload.side_effect = results

        open_mock_first = MagicMock()
        open_mock_first.read.return_value = b"first content"
        open_mock_second = MagicMock()
        open_mock_second.read.return_value = b"second content"
        fp_mock = MagicMock()
        fp_mock.__enter__.side_effect = [open_mock_first, open_mock_second]

        with patch("builtins.open", return_value=fp_mock):
            files = [
                ("tests/data/sample_invoice.pdf", "document.pdf"),
                ("tests/data/sample_invoice.pdf", "document 🎁.pdf"),
            ]
            annotation_ids = client.import_document(
                queue_id=123, files=files, values={"a": 1}, metadata={"b": 2}
            )

        assert annotation_ids == [111, 222]
        calls = [
            call(
                "queues/123/upload",
                {
                    "content": ("document.pdf", b"first content", "application/octet-stream"),
                    "values": ("", b'{"a": 1}', "application/json"),
                    "metadata": ("", b'{"b": 2}', "application/json"),
                },
            ),
            call(
                "queues/123/upload",
                {
                    "content": ("document 🎁.pdf", b"second content", "application/octet-stream"),
                    "values": ("", b'{"a": 1}', "application/json"),
                    "metadata": ("", b'{"b": 2}', "application/json"),
                },
            ),
        ]

        http_client.upload.assert_has_calls(calls, any_order=True)

    def test_delete_queue(self, elis_client_sync, dummy_queue):
        client, http_client = elis_client_sync
        http_client.delete.return_value = None

        qid = dummy_queue["id"]
        client.delete_queue(qid)

        http_client.delete.assert_called_with(Resource.Queue, qid)

    def test_export_annotations_to_json(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.export.return_value = iter((dummy_annotation,))

        qid = 123
        export_format = "json"

        for a in client.export_annotations_to_json(queue_id=qid):
            assert a == Annotation(**dummy_annotation)

        http_client.export.assert_called_with(Resource.Queue, qid, export_format)

    def test_export_annotations_to_file(self, elis_client_sync, mock_file_read_sync):
        client, http_client = elis_client_sync
        http_client.export.return_value = mock_file_read_sync("tests/data/annotation_export.xml")

        qid = 123
        export_format = ExportFileFormats.XML

        result = b""
        for a in client.export_annotations_to_file(queue_id=qid, export_format=export_format):
            result += a

        http_client.export.assert_called_with(Resource.Queue, qid, export_format.value)

        with open("tests/data/annotation_export.xml", "rb") as fp:
            assert result == fp.read()
