"""Integration tests.

These test do not run with the rest of the tests (and did not run in previous versions)
because of the filename. To manually run them, you need to:
- set envars ROSSUM_TOKEN, ROSSUM_BASE_URL and ROSSUM_ORGANIZATION_URL
- pytest tests/e2e.py

In case of permission issues these tests will fail during cleanup.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import aiofiles
import pytest
from aiofiles import os as aios

from rossum_api import AsyncRossumAPIClient
from rossum_api.domain_logic.resources import Resource
from rossum_api.dtos import Token

if TYPE_CHECKING:
    from typing import Optional

    from rossum_api.clients.external_async_client import (
        AsyncRossumAPIClientWithDefaultDeserializer,
    )
    from rossum_api.models.queue import Queue
    from rossum_api.models.schema import Schema
    from rossum_api.models.workspace import Workspace

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": os.environ["ROSSUM_ORGANIZATION_URL"],
}


@pytest.mark.asyncio
class TestE2E:
    async def test_import_document(self):
        workspace: Optional[Workspace] = None
        queue: Optional[Queue] = None
        schema: Optional[Schema] = None
        client: AsyncRossumAPIClientWithDefaultDeserializer = AsyncRossumAPIClient(
            credentials=Token(os.environ["ROSSUM_TOKEN"]),
            base_url=os.environ["ROSSUM_BASE_URL"],
        )
        try:
            workspace = await client.create_new_workspace(data=WORKSPACE)
            schema = await client.create_new_schema({"name": "E2E Test Schema", "content": []})

            queue_data = {
                "name": "Run 1",
                "workspace": workspace.url,
                "schema": schema.url,
            }
            queue = await client.create_new_queue(data=queue_data)

            files = {("./tests/data/sample_invoice.pdf", f"e2etest_doc_{i}.pdf") for i in range(2)}

            await client.import_document(queue.id, files)
            async for annotation in client.export_annotations_to_json(queue.id):
                assert annotation.document["file_name"] in [
                    f"e2etest_doc_{i}.pdf" for i in range(2)
                ]

            async with aiofiles.tempfile.TemporaryFile("wb") as f:
                tempfile_name = f.name
                async for chunk in client.export_annotations_to_file(queue.id, "xml"):
                    await f.write(chunk)

                await f.flush()
                assert (await aios.stat(tempfile_name)).st_size > 0
        finally:
            # cleanup of created entities
            if queue:
                await client.delete_queue(queue.id)
            if schema:
                await client.delete_schema(schema.id)
            if workspace:
                await client.delete_workspace(workspace.id)

    async def test_create_upload(self):
        """An idea for potential E2E test for https://elis.rossum.ai/api/docs/#create-upload."""
        workspace: Optional[Workspace] = None
        queue: Optional[Queue] = None
        schema: Optional[Schema] = None
        client: AsyncRossumAPIClientWithDefaultDeserializer = AsyncRossumAPIClient(
            credentials=Token(os.environ["ROSSUM_TOKEN"]),
            base_url=os.environ["ROSSUM_BASE_URL"],
        )
        try:
            workspace = await client.create_new_workspace(data=WORKSPACE)
            schema = await client.create_new_schema({"name": "E2E Test Schema", "content": []})

            queue_data = {
                "name": "Run 1",
                "workspace": workspace.url,
                "schema": schema.url,
            }
            queue = await client.create_new_queue(data=queue_data)

            files = {("./tests/data/sample_invoice.pdf", f"e2etest_doc_{i}.pdf") for i in range(2)}

            tasks = await client.upload_document(queue.id, files)

            annotations = []

            for task in tasks:
                task_id = task.id
                task = await client.poll_task_until_succeeded(task_id)
                upload_url = task.result_url
                upload_id = int(upload_url.split("/")[-1])
                upload = await client.retrieve_upload(upload_id)
                annotation_id = [int(a.split("/")[-1]) for a in upload.annotations]
                annotation = await client.poll_annotation_until_imported(annotation_id[0])
                annotations.append(annotation)

            for annotation in annotations:
                document_id = int(annotation.document.split("/")[-1])
                document_response = await client._http_client.fetch_one(
                    Resource.Document, document_id
                )
                document = client._deserializer(Resource.Document, document_response)

                assert document.original_file_name in [f"e2etest_doc_{i}.pdf" for i in range(2)]

        finally:
            # cleanup of created entities
            if queue:
                await client.delete_queue(queue.id)
            if schema:
                await client.delete_schema(schema.id)
            if workspace:
                await client.delete_workspace(workspace.id)
