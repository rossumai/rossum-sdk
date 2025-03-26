"""A script that tests all operations over a single resource provided by Elis API.

It could evolve in time into an E2E test.
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import typing

import aiofiles

from rossum_api import AsyncRossumAPIClient, SyncRossumAPIClient
from rossum_api.clients.internal_async_client import InternalAsyncClient
from rossum_api.domain_logic.resources import Resource
from rossum_api.dtos import UserCredentials

if typing.TYPE_CHECKING:
    from rossum_api.clients.external_async_client import (
        AsyncRossumAPIClientWithDefaultDeserializer,
    )

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.develop.r8.lol/api/v1/organizations/167",
}

SCHEMA = {
    "id": 31336,
    "name": "Rossum NG Test Schema",
    "queues": ["https://elis.rossum.ai/api/v1/queues/8236"],
    "url": "https://elis.rossum.ai/api/v1/schemas/31336",
    "content": [
        {
            "category": "section",
            "id": "invoice_details_section",
            "label": "Invoice details",
            "children": [
                {
                    "category": "datapoint",
                    "id": "document_id",
                    "label": "Invoice number",
                    "type": "string",
                    "rir_field_names": ["document_id"],
                    "constraints": {"required": False},
                    "default_value": None,
                },
            ],
        },
    ],
    "metadata": {},
}


async def main():
    client = InternalAsyncClient(
        base_url="https://elis.develop.r8.lol/api/v1",
        username=os.environ["ELIS_USERNAME"],
        password=os.environ["ELIS_PASSWORD"],
    )
    workspace = await client.create(Resource.Workspace, data=WORKSPACE)
    response = await client.fetch_one(Resource.Workspace, id_=workspace["id"])
    print("GET result:", response)
    print("LIST results:")
    async for w in client.fetch_all(Resource.Workspace, ordering=["-id"], name=WORKSPACE["name"]):
        print(w)
    response = await client.replace(
        Resource.Workspace,
        id_=workspace["id"],
        data={**WORKSPACE, "name": WORKSPACE["name"]},
    )
    print("PUT result:", response)
    response = await client.update(
        Resource.Workspace,
        id_=workspace["id"],
        data={"name": f"{WORKSPACE['name']} {random.randint(1, 100)}"},
    )
    print("PATCH result:", response)

    # Upload a document -- schema and queue must be created to do that
    schema = await client.create(Resource.Schema, data=SCHEMA)
    queue = await client.create(
        Resource.Queue,
        data={
            "workspace": workspace["url"],
            "name": "Rossum Client NG Test",
            "schema": schema["url"],
        },
    )

    async with aiofiles.open("tests/data/sample_invoice.pdf", "rb") as fp:
        response = await client.upload(
            Resource.Queue,
            id_=queue["id"],
            fp=fp,
            filename="filename.pdf",
            values={"upload:organization_unit": "Sales"},
            metadata={"project": "Market ABC"},
        )
        print("UPLOAD result:", response)

    print("EXPORT result:")
    async for chunk in client.export(
        Resource.Queue,
        id_=queue["id"],
        export_format="xml",
        page_size=200,
        columns=["meta_file_name", "document_id", "status"],
    ):
        print(chunk)

    await client.delete(Resource.Workspace, id_=workspace["id"])
    print(f"Workspace {workspace['id']} deleted.")


async def main_with_async_client():
    client: AsyncRossumAPIClientWithDefaultDeserializer = AsyncRossumAPIClient(
        credentials=UserCredentials(os.environ["ELIS_USERNAME"], os.environ["ELIS_PASSWORD"]),
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    workspace = await client.create_new_workspace(data=WORKSPACE)
    workspace = await client.retrieve_workspace(workspace.id)
    print("GET result:", workspace)
    print("LIST results:")
    async for w in client.list_workspaces(["-id"], name=WORKSPACE["name"]):
        print(w)

    schema = await client.create_new_schema(SCHEMA)
    queue = await client.create_new_queue(
        {"workspace": workspace.url, "name": "Rossum Client NG Test", "schema": schema.url}
    )
    (annotation_id,) = await client.import_document(
        queue.id, [("tests/data/sample_invoice.pdf", "Sample Invoice")]
    )

    print("Polling until annotation is ready to review...")
    annotation = await client.poll_annotation(
        annotation_id, lambda a: a.status not in ("importing", "created")
    )
    print(f"Annotation ready to review: {annotation}")

    # Cleanup
    await client.delete_queue(queue.id)
    print(f"Workspace {workspace.id} deleted.")
    await client.delete_workspace(workspace.id)
    print(f"Workspace {workspace.id} deleted.")


def main_with_sync_client():
    client = SyncRossumAPIClient(
        credentials=UserCredentials(os.environ["ELIS_USERNAME"], os.environ["ELIS_PASSWORD"]),
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    ws = client.create_new_workspace(data=WORKSPACE)
    workspace_id = ws.id
    ws = client.retrieve_workspace(workspace_id)
    print("GET result:", ws)
    print("LIST results:")
    for w in client.list_workspaces(["-id"], name=WORKSPACE["name"]):
        print(w)
    client.delete_workspace(workspace_id)
    print(f"Workspace {workspace_id} deleted.")


asyncio.run(main())
# asyncio.run(main_with_async_client())
# main_with_sync_client()
