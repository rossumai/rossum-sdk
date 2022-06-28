import logging
import os
from typing import Optional

import pytest

from rossum_ng.models.queue import Queue
from rossum_ng.models.schema import Schema
from rossum_ng.models.workspace import Workspace

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from rossum_ng.elis_api_client import ElisAPIClient

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": os.environ["ORGANIZATION_URL"],
}


@pytest.mark.asyncio
class TestE2E:
    async def test_import_document(self):
        workspace: Optional[Workspace] = None
        queue: Optional[Queue] = None
        schema: Optional[Schema] = None

        client = ElisAPIClient(
            os.environ["ELIS_USERNAME"],
            os.environ["ELIS_PASSWORD"],
            base_url="https://elis.develop.r8.lol/api/v1",
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
        finally:
            # cleanup of created entities
            if queue:
                await client.delete_queue(queue.id)
            if schema:
                await client.delete_schema(schema.id)
            if workspace:
                await client.delete_workspace(workspace.id)
