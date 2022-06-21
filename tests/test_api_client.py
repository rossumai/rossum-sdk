"""Test APIClient methods.

* all HTTP calls are mocked using httpx_mock which results into nicer code that using unittest.mock
* `workspace` is used as resource in most tests to make the examples respresentative.
* all CRUD methods are tested for both a happy path and an error (400 or 404)
"""
import json
from unittest import mock

import aiofiles
import httpx
import pytest
from rossum_ng.api_client import APIClient

WORKSPACES = [
    {
        "id": 7694,
        "name": "Test Workspace",
        "url": "https://elis.rossum.ai/api/v1/workspaces/7694",
        "autopilot": False,
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
        "queues": [],
        "metadata": {},
    },
    {
        "id": 1234,
        "name": "Test Workspace",
        "url": "https://elis.rossum.ai/api/v1/workspaces/1234",
        "autopilot": False,
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
        "queues": [],
        "metadata": {},
    },
    {
        "id": 4321,
        "name": "Test Workspace",
        "url": "https://elis.rossum.ai/api/v1/workspaces/1234",
        "autopilot": False,
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
        "queues": [],
        "metadata": {},
    },
]

UPLOAD_RESPONSE = {
    "results": [
        {
            "document": "https://elis.develop.r8.lol/api/v1/documents/3164197",
            "annotation": "https://elis.develop.r8.lol/api/v1/annotations/3154459",
        }
    ],
}


@pytest.fixture
def client():
    client = APIClient("username", "password")
    client.token = "fake-token"
    return client


@pytest.mark.asyncio
async def test_authenticate(client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/auth/login",
        json={
            "key": "our-token",
            "domain": "custom-domain.app.rossum.ai",
        },
    )
    assert client.token != "our-token"
    await client._authenticate()
    assert client.token == "our-token"

    # HTTP 401 is propagated via an exception
    httpx_mock.add_response(
        method="POST", url="https://elis.rossum.ai/api/v1/auth/login", status_code=401
    )
    with pytest.raises(httpx.HTTPStatusError, match="401"):
        await client._authenticate()


@pytest.mark.asyncio
async def test_fetch_one(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        json=WORKSPACES[0],
    )
    workspace = await client.fetch_one("workspaces", id=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_fetch_one_404(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspace/123",
        status_code=404,
    )
    with pytest.raises(httpx.HTTPStatusError, match="404"):
        await client.fetch_one("workspace", id=123)


@pytest.mark.asyncio
async def test_fetch_all(client, httpx_mock):
    second_page = "https://elis.rossum.ai/api/v1/workspaces?page=2&page_size=100"
    third_page = "https://elis.rossum.ai/api/v1/workspaces?page=3&page_size=100"
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100",
        json={
            "pagination": {"total": 3, "total_pages": 3, "next": second_page, "previous": None},
            "results": WORKSPACES[:1],
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=second_page,
        json={
            "pagination": {"total": 3, "total_pages": 3, "next": third_page, "previous": None},
            "results": WORKSPACES[1:2],
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=third_page,
        json={
            "pagination": {"total": 3, "total_pages": 3, "next": None, "previous": None},
            "results": WORKSPACES[2:],
        },
    )
    workspaces = [w async for w in client.fetch_all("workspaces")]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_ordering(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&ordering=-id,name",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": WORKSPACES,
        },
    )
    workspaces = [w async for w in client.fetch_all("workspaces", ordering=["-id", "name"])]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_filters(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&name=Test&autopilot=1",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": WORKSPACES,
        },
    )
    workspaces = [w async for w in client.fetch_all("workspaces", name="Test", autopilot=1)]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_404(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/non-existent-resource?page_size=100",
        status_code=404,
    )
    with pytest.raises(httpx.HTTPStatusError, match="404"):
        async for _ in client.fetch_all("non-existent-resource"):
            pass


@pytest.mark.asyncio
async def test_create(client, httpx_mock):
    data = {
        "name": "Test Workspace",
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/workspaces",
        match_content=json.dumps(data).encode("utf-8"),
        json=WORKSPACES[0],
    )
    workspace = await client.create("workspaces", data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_create_400(client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/workspace",
        status_code=400,
    )
    with pytest.raises(httpx.HTTPStatusError, match="400"):
        await client.create("workspace", data={})


@pytest.mark.asyncio
async def test_replace(client, httpx_mock):
    data = {
        "name": "Test Workspace",
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
    }
    httpx_mock.add_response(
        method="PUT",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        match_content=json.dumps(data).encode("utf-8"),
        json=WORKSPACES[0],
    )
    workspace = await client.replace("workspaces", id=123, data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_replace_404(client, httpx_mock):
    httpx_mock.add_response(
        method="PUT",
        url="https://elis.rossum.ai/api/v1/workspace/123",
        status_code=404,
    )
    with pytest.raises(httpx.HTTPStatusError, match="404"):
        await client.replace("workspace", id=123, data={})


@pytest.mark.asyncio
async def test_update(client, httpx_mock):
    data = {"name": "Test Workspace"}
    httpx_mock.add_response(
        method="PATCH",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        match_content=json.dumps(data).encode("utf-8"),
        json=WORKSPACES[0],
    )
    workspace = await client.update("workspaces", id=123, data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_update_404(client, httpx_mock):
    data = {"name": "Test Workspace"}
    httpx_mock.add_response(
        method="PATCH",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        match_content=json.dumps(data).encode("utf-8"),
        status_code=404,
    )
    with pytest.raises(httpx.HTTPStatusError, match="404"):
        await client.update("workspaces", id=123, data=data)


@pytest.mark.asyncio
async def test_delete(client, httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
    )
    result = await client.delete("workspaces", id=123)
    assert result is None


@pytest.mark.asyncio
async def test_delete_404(client, httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        status_code=404,
    )
    with pytest.raises(httpx.HTTPStatusError, match="404"):
        await client.delete("workspaces", id=123)


@pytest.mark.asyncio
async def test_upload(client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/queues/123/upload/filename.pdf",
        json=UPLOAD_RESPONSE,
    )

    async with aiofiles.tempfile.TemporaryFile("rb") as fp:
        await client.upload("queues", id=123, fp=fp, filename="filename.pdf")


@pytest.mark.asyncio
async def test_authenticate_if_needed_token_expired(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        headers={"Authorization": "token fake-token"},
        status_code=401,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        match_headers={"Authorization": "token new-token"},
        json=WORKSPACES[0],
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        workspace = await client.fetch_one("workspaces", id=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_authenticate_if_needed_no_token(httpx_mock):
    client = APIClient("username", "password")
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        match_headers={"Authorization": "token new-token"},
        json=WORKSPACES[0],
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        workspace = await client.fetch_one("workspaces", id=7694)

    assert workspace == WORKSPACES[0]
