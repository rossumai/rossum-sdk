import logging
import os

import pytest

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
        client = ElisAPIClient(
            os.environ["ELIS_USERNAME"],
            os.environ["ELIS_PASSWORD"],
            base_url="https://elis.develop.r8.lol/api/v1",
        )
        workspace = await client.create_new_workspace(data=WORKSPACE)

        queue_data = {
            "name": "Run 1",
            "workspace": workspace.url,
            "schema": os.environ["SCHEMA_URL"],
        }
        queue = await client.create_new_queue(data=queue_data)
        queue_id = queue.id

        files = {("./tests/data/sample_invoice.pdf", f"e2etest_doc_{i}.pdf") for i in range(2)}

        await client.import_document(queue_id, files)

        await client.delete_workspace(workspace.id)
