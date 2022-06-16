"""A script that tests all operations over a single resource provided by Elis API.

It could evolve in time into an E2E test.
"""
import asyncio
import logging
import os
import random

from rossum_ng.api_client import APIClient

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.develop.r8.lol/api/v1/organizations/167",
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
    response = [w async for w in client.fetch_all("workspaces")]
    print("LIST result:", response)
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


asyncio.run(main())
