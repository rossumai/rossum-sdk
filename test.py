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
    response = await client.create(f"/v1/workspaces", data=WORKSPACE)
    workspace_id = response["id"]
    response = await client.read(f"/v1/workspaces/{workspace_id}")
    print("GET result:", response)
    response = [w async for w in client.list(f"/v1/workspaces")]
    print("LIST result:", response)
    response = await client.replace(
        f"/v1/workspaces/{workspace_id}",
        data={**WORKSPACE, "name": f"{WORKSPACE['name']} {random.randint(1, 100)}"},
    )
    print("PUT result:", response)
    response = await client.update(
        f"/v1/workspaces/{workspace_id}",
        data={"name": f"{WORKSPACE['name']} {random.randint(1, 100)}"},
    )
    print("PATCH result:", response)

    response = await client.delete(f"/v1/workspaces/{workspace_id}")
    print(f"Workspace {workspace_id} deleted.")


asyncio.run(main())
