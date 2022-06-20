"""A script that tests all operations over a single resource provided by Elis API.

It could evolve in time into an E2E test.
"""
import asyncio
import logging
import os
import random

from rossum_ng.api_client import APIClient
from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.elis_api_client_sync import ElisAPIClientSync

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.develop.r8.lol/api/v1/organizations/116390",
}


async def main():
    client = APIClient(
        os.environ["ELIS_USERNAME"],
        os.environ["ELIS_PASSWORD"],
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    response = await client.create("workspaces", data=WORKSPACE)
    workspace_id = response["id"]
    response = await client.fetch_one("workspaces", id=workspace_id)
    print("GET result:", response)
    print("LIST results:")
    async for w in client.fetch_all("workspaces", ordering=["-id"], name=WORKSPACE["name"]):
        print(w)
    response = await client.replace(
        "workspaces",
        id=workspace_id,
        data={**WORKSPACE, "name": f"{WORKSPACE['name']} {random.randint(1, 100)}"},
    )
    print("PUT result:", response)
    response = await client.update(
        "workspaces",
        id=workspace_id,
        data={"name": f"{WORKSPACE['name']} {random.randint(1, 100)}"},
    )
    print("PATCH result:", response)

    response = await client.delete("workspaces", id=workspace_id)
    print(f"Workspace {workspace_id} deleted.")


async def main_with_async_client():
    client = ElisAPIClient(
        os.environ["ELIS_USERNAME"],
        os.environ["ELIS_PASSWORD"],
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    ws = await client.create_new_workspace(data=WORKSPACE)
    workspace_id = ws.id
    ws = await client.retrieve_workspace(workspace_id)
    print("GET result:", ws)
    print("LIST results:")
    async for w in client.list_all_workspaces(["-id"], None, name=WORKSPACE["name"]):
        print(w)
    await client.delete_workspace(workspace_id)
    print(f"Workspace {workspace_id} deleted.")


def main_with_sync_client():
    client = ElisAPIClientSync(
        os.environ["ELIS_USERNAME"],
        os.environ["ELIS_PASSWORD"],
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    ws = client.create_new_workspace(data=WORKSPACE)
    workspace_id = ws.id
    ws = client.retrieve_workspace(workspace_id)
    print("GET result:", ws)
    print("LIST results:")
    for w in client.list_all_workspaces(["-id"], None, name=WORKSPACE["name"]):
        print(w)
    client.delete_workspace(workspace_id)
    print(f"Workspace {workspace_id} deleted.")


asyncio.run(main())
# asyncio.run(main_with_async_client())
# main_with_sync_client()
