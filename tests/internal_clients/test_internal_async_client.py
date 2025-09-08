"""Test InternalAsyncClient methods.

* all HTTP calls are mocked using httpx_mock which results into nicer code than using unittest.mock
* `workspace` is used as resource in most tests to make the examples representative.
* all CRUD methods are tested for both a happy path and an error (400 or 404)
"""

from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import logging
import unittest.mock as mock

import aiofiles
import httpx
import pytest
import pytest_httpx

from rossum_api.clients.internal_async_client import InternalAsyncClient
from rossum_api.domain_logic.resources import Resource
from rossum_api.domain_logic.urls import build_full_login_url
from rossum_api.exceptions import APIClientError
from tests.conftest import ANNOTATIONS, AUTOMATION_BLOCKERS, CONTENT
from tests.internal_clients.conftest import (
    CSV_EXPORT,
    EXPECTED_UPLOAD_CONTENT,
    FAKE_TOKEN,
    NEW_TOKEN,
    UPLOAD_RESPONSE,
    USER,
    WORKSPACES,
    count_calls,
    response_post_processor,
)


@pytest.fixture
def client():
    # Set retrying parameters to zero to keep tests fast
    client = InternalAsyncClient(
        username="username", password="password", retry_backoff_factor=0, retry_max_jitter=0
    )
    client.token = FAKE_TOKEN
    return client


@pytest.mark.asyncio
async def test_authenticate(client, login_mock):
    assert client.token != "our-token"
    await client._authenticate()
    assert client.token == "our-token"

    # HTTP 401 is propagated via an exception
    login_mock.add_response(
        method="POST", url="https://elis.rossum.ai/api/v1/auth/login", status_code=401
    )
    with pytest.raises(APIClientError, match="401"):
        await client._authenticate()


@pytest.mark.asyncio
async def test_authenticate_is_retried(client, httpx_mock):
    @count_calls
    def custom_response(request: httpx.Request, n_calls: int):
        if n_calls == 1:
            raise httpx.ReadTimeout("Unable to read within timeout")

        return httpx.Response(
            status_code=200,
            json={
                "key": NEW_TOKEN,
                "domain": "custom-domain.app.rossum.ai",
            },
        )

    httpx_mock.add_callback(custom_response)

    assert client.token != "our-token"
    await client._authenticate()
    assert client.token == "our-token"


@pytest.mark.asyncio
async def test_init_token(httpx_mock):
    """Verifies that we can create client using token and call API without 'auth' call."""
    client = InternalAsyncClient(token=FAKE_TOKEN)

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        json={},
    )
    await client.fetch_one(Resource.User, 1)
    assert len(httpx_mock.get_requests()) == 1
    assert httpx_mock.get_requests()[0].headers["Authorization"] == f"Bearer {FAKE_TOKEN}"


@pytest.mark.asyncio
async def test_reauth_no_credentials(httpx_mock):
    """Invalid token used but no credentials available for re-authentication. Raise 401."""
    client = InternalAsyncClient(token=FAKE_TOKEN)

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        status_code=401,
        content=b"unauth!",
    )
    with pytest.raises(APIClientError) as err:
        await client.fetch_one(Resource.User, 1)

    assert err.value.status_code == 401


@pytest.mark.asyncio
async def test_reauth_success(login_mock, httpx_mock):
    """Invalid token used, credentials available => reauthenticate in the background. Fetch user without raising any errors."""
    client = InternalAsyncClient(username="username", password="password", token=FAKE_TOKEN)

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        status_code=401,
        match_headers={"Authorization": f"Bearer {FAKE_TOKEN}"},
        content=b"unauth!",
    )

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        match_headers={"Authorization": f"Bearer {NEW_TOKEN}"},
        json=USER,
    )

    user = await client.fetch_one(Resource.User, 1)
    assert user == USER


@pytest.mark.asyncio
async def test_retry_timeout(client, httpx_mock):
    @count_calls
    def custom_response(request: httpx.Request, n_calls: int):
        if n_calls == 1:
            raise httpx.ReadTimeout("Unable to read within timeout")

        return httpx.Response(status_code=200, json=WORKSPACES[0])

    httpx_mock.add_callback(custom_response)
    workspace = await client.fetch_one(Resource.Workspace, id_=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_retry_n_attempts(client, httpx_mock):
    @count_calls
    def custom_response(request: httpx.Request, n_calls: int):
        if n_calls <= 3:
            raise httpx.ReadTimeout("Unable to read within timeout")

        return httpx.Response(status_code=200, json=WORKSPACES[0])

    httpx_mock.add_callback(custom_response)

    with pytest.raises(httpx.ReadTimeout):
        await client.fetch_one(Resource.Workspace, id_=7694)


@pytest.mark.asyncio
async def test_fetch_one(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        json=WORKSPACES[0],
    )
    workspace = await client.fetch_one(Resource.Workspace, id_=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_fetch_all(client, httpx_mock):
    second_page = "https://elis.rossum.ai/api/v1/workspaces?page=2&page_size=100&ordering=&sideload=&content.schema_id="
    third_page = "https://elis.rossum.ai/api/v1/workspaces?page=3&page_size=100&ordering=&sideload=&content.schema_id="
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&ordering=&sideload=&content.schema_id=",
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
    workspaces = [w async for w in client.fetch_all(Resource.Workspace)]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_with_max_pages_limit(client, httpx_mock):
    second_page = "https://elis.rossum.ai/api/v1/workspaces?page=2&page_size=100&ordering=&sideload=&content.schema_id="
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&ordering=&sideload=&content.schema_id=",
        json={
            "pagination": {"total": 3, "total_pages": 3, "next": second_page, "previous": None},
            "results": WORKSPACES[:1],
        },
    )
    workspaces = [w async for w in client.fetch_all(Resource.Workspace, max_pages=1)]
    assert workspaces == WORKSPACES[:1]


@pytest.mark.asyncio
async def test_fetch_all_ordering(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&ordering=-id,name&sideload=&content.schema_id=",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": WORKSPACES,
        },
    )
    workspaces = [w async for w in client.fetch_all(Resource.Workspace, ordering=["-id", "name"])]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_filters(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&name=Test&autopilot=1&ordering=&sideload=&content.schema_id=",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": WORKSPACES,
        },
    )
    workspaces = [w async for w in client.fetch_all(Resource.Workspace, name="Test", autopilot=1)]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_sideload(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/annotations?page_size=100&sideload=content,automation_blockers&content.schema_id=invoice_id,date_issue&ordering=",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": ANNOTATIONS,
            "content": CONTENT,
            "automation_blockers": AUTOMATION_BLOCKERS,
        },
    )
    annotations = [
        w
        async for w in client.fetch_all(
            Resource.Annotation,
            sideloads=["content", "automation_blockers"],
            content_schema_ids=["invoice_id", "date_issue"],
        )
    ]

    expected_annotations = copy.deepcopy(ANNOTATIONS)
    expected_annotations[0]["content"] = [CONTENT[1]]
    expected_annotations[0]["automation_blocker"] = AUTOMATION_BLOCKERS[0]
    expected_annotations[1]["content"] = [CONTENT[0], CONTENT[2]]
    expected_annotations[1]["automation_blocker"] = AUTOMATION_BLOCKERS[0]
    expected_annotations[2]["content"] = []

    assert annotations == expected_annotations


@pytest.mark.asyncio
async def test_fetch_all_limit_in_flight_requests(client, httpx_mock):
    page_count = 10
    page_url = "https://elis.rossum.ai/api/v1/workspaces?page_size=100&ordering=&sideload=&content.schema_id="
    for i in range(2, page_count + 1):
        next_page_url = f"https://elis.rossum.ai/api/v1/workspaces?page={i}&page_size=100&ordering=&sideload=&content.schema_id="
        httpx_mock.add_response(
            method="GET",
            url=page_url,
            json={
                "pagination": {
                    "total": page_count,
                    "total_pages": page_count,
                    "next": next_page_url,
                    "previous": None,
                },
                "results": WORKSPACES[:1],
            },
        )
        page_url = next_page_url
    httpx_mock.add_response(
        method="GET",
        url=page_url,
        json={
            "pagination": {
                "total": page_count,
                "total_pages": page_count,
                "next": None,
                "previous": None,
            },
            "results": WORKSPACES[-1:],
        },
    )

    @contextlib.contextmanager
    def track_concurrency(client):
        concurrency_lock = asyncio.Semaphore(1)
        concurrency = {"current": 0, "max": 0}
        request_method = client._request

        async def _request(*args, **kwargs):
            async with concurrency_lock:
                concurrency["current"] += 1
                concurrency["max"] = max(concurrency["current"], concurrency["max"])
            await asyncio.sleep(0)  # ensure the concurrency is measurable
            results = await request_method(*args, **kwargs)
            async with concurrency_lock:
                concurrency["current"] -= 1
            return results

        with mock.patch.object(client, "_request", side_effect=_request):
            yield concurrency

    with track_concurrency(client) as concurrency:
        workspaces = [w async for w in client.fetch_all(Resource.Workspace)]
        assert workspaces == [WORKSPACES[0]] * (page_count - 1) + WORKSPACES[-1:]
        assert concurrency["max"] == 4, "default max_in_flight_requests is 4"

    with track_concurrency(client) as concurrency:
        client.max_in_flight_requests = 3
        workspaces = [w async for w in client.fetch_all(Resource.Workspace)]
        assert workspaces == [WORKSPACES[0]] * (page_count - 1) + WORKSPACES[-1:]
        assert concurrency["max"] == 3, "based on overridden max_in_flight_requests to 3"


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
    workspace = await client.create(Resource.Workspace, data=data)
    assert workspace == WORKSPACES[0]


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
    workspace = await client.replace(Resource.Workspace, id_=123, data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_update(client, httpx_mock):
    data = {"name": "Test Workspace"}
    httpx_mock.add_response(
        method="PATCH",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        match_content=json.dumps(data).encode("utf-8"),
        json=WORKSPACES[0],
    )
    workspace = await client.update(Resource.Workspace, id_=123, data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_delete(client, httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
    )
    result = await client.delete(Resource.Workspace, id_=123)
    assert result is None


@pytest.mark.asyncio
async def test_upload(client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/queues/123/upload",
        match_content=EXPECTED_UPLOAD_CONTENT,
        json=UPLOAD_RESPONSE,
    )

    # HTTPX uses a random --boundary, patch urandom to make it fixed,
    # see section 4.1 in https://www.ietf.org/rfc/rfc2388.txt for context
    with mock.patch("httpx._multipart.os.urandom", return_value=b"111"):
        async with aiofiles.tempfile.NamedTemporaryFile("wb") as fp:
            await fp.write(b"Fake PDF.")
            await fp.flush()
            async with aiofiles.open(fp.name, "rb") as fp:
                response = await client.upload(
                    Resource.Queue,
                    id_=123,
                    fp=fp,
                    filename="filename.pdf",
                    values={"upload:organization_unit": "Sales"},
                    metadata={"project": "Market ABC"},
                )
    assert response == UPLOAD_RESPONSE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filters,expected_method, first_url, second_url",
    [
        (
            {},
            "GET",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=json&page_size=100&columns=col1%2Ccol2&id=456%2C789&ordering=&sideload=&content.schema_id=",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=json&page_size=100&page=2&columns=col1%2Ccol2&id=456%2C789&ordering=&sideload=&content.schema_id=",
        ),
        (
            {"to_status": "exported"},
            "POST",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=json&page_size=100&columns=col1%2Ccol2&id=456%2C789&to_status=exported&ordering=&sideload=&content.schema_id=",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=json&page_size=100&page=2&columns=col1%2Ccol2&id=456%2C789&to_status=exported&ordering=&sideload=&content.schema_id=",
        ),
    ],
)
async def test_export_json(client, httpx_mock, filters, expected_method, first_url, second_url):
    httpx_mock.add_response(
        method=expected_method,
        url=first_url,
        json={
            "pagination": {"total": 2, "total_pages": 2, "next": second_url, "previous": None},
            "results": ANNOTATIONS[:2],
        },
    )
    httpx_mock.add_response(
        method=expected_method,
        url=second_url,
        json={
            "pagination": {"total": 2, "total_pages": 2, "next": None, "previous": None},
            "results": ANNOTATIONS[2:],
        },
    )
    cols = ["col1", "col2"]
    annotations = [
        w
        async for w in client.export(
            Resource.Queue, id_=123, export_format="json", columns=cols, id="456,789", **filters
        )
    ]
    assert annotations == ANNOTATIONS  # Annotations are yielded in correct order


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filters,expected_method, expected_url",
    [
        (
            {},
            "GET",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=csv&columns=col1%2Ccol2&id=456%2C789",
        ),
        (
            {"to_status": "exported"},
            "POST",
            "https://elis.rossum.ai/api/v1/queues/123/export?format=csv&columns=col1%2Ccol2&id=456%2C789&to_status=exported",
        ),
    ],
)
async def test_export_csv(client, httpx_mock, filters, expected_method, expected_url):
    httpx_mock.add_response(
        method=expected_method,
        url=expected_url,
        stream=pytest_httpx.IteratorStream([CSV_EXPORT[:20], CSV_EXPORT[20:]]),
    )
    cols = ["col1", "col2"]
    export_chunks = [
        w
        async for w in client.export(
            Resource.Queue, id_=123, export_format="csv", columns=cols, id="456,789", **filters
        )
    ]
    assert b"".join(export_chunks) == CSV_EXPORT  # Streamed chunks are yielded in correct order


@pytest.mark.asyncio
async def test_authenticate_if_needed_token_expired(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        headers={"Authorization": "Bearer fake-token"},
        status_code=401,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        match_headers={"Authorization": "Bearer new-token"},
        json=WORKSPACES[0],
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        workspace = await client.fetch_one(Resource.Workspace, id_=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_authenticate_generator_if_needed_token_expired(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        headers={"Authorization": "Bearer fake-token"},
        status_code=401,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        match_headers={"Authorization": "Bearer new-token"},
        stream=pytest_httpx.IteratorStream([CSV_EXPORT[:20], CSV_EXPORT[20:]]),
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        chunks = [chunk async for chunk in client._stream("GET", "queues/123/export?format=csv")]
    assert b"".join(chunks) == CSV_EXPORT


@pytest.mark.asyncio
async def test_authenticate_if_needed_no_token(httpx_mock):
    client = InternalAsyncClient(username="username", password="password")
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        match_headers={"Authorization": "Bearer new-token"},
        json=WORKSPACES[0],
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        workspace = await client.fetch_one(Resource.Workspace, id_=7694)

    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_authenticate_generator_if_needed_no_token(client, httpx_mock):
    client = InternalAsyncClient(username="username", password="password")
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        match_headers={"Authorization": "Bearer new-token"},
        stream=pytest_httpx.IteratorStream([CSV_EXPORT[:20], CSV_EXPORT[20:]]),
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        chunks = [chunk async for chunk in client._stream("GET", "queues/123/export?format=csv")]
    assert b"".join(chunks) == CSV_EXPORT


@pytest.mark.asyncio
async def test_request_json_full_url(client, httpx_mock):
    httpx_mock.add_response(
        method="GET", url="https://elis.rossum.ai/api/v1/workspaces/123", json=WORKSPACES[0]
    )
    data = await client.request_json("GET", "https://elis.rossum.ai/api/v1/workspaces/123")
    assert data == WORKSPACES[0]


@pytest.mark.asyncio
async def test_request_json_full_url_http(client, httpx_mock):
    httpx_mock.add_response(
        method="GET", url="http://localhost:8000/api/v1/workspaces/123", json=WORKSPACES[0]
    )
    data = await client.request_json("GET", "http://localhost:8000/api/v1/workspaces/123")
    assert data == WORKSPACES[0]


@pytest.mark.asyncio
async def test_request_json_204(client, httpx_mock):
    httpx_mock.add_response(
        method="DELETE", url="https://elis.rossum.ai/api/v1/workspaces/123", status_code=204
    )
    data = await client.request_json("DELETE", "https://elis.rossum.ai/api/v1/workspaces/123")
    assert data == {}


@pytest.mark.asyncio
async def test_request_binary_data(client, httpx_mock):
    httpx_mock.add_response(
        method="GET", url="https://elis.rossum.ai/api/v1/pages/123/preview", content=b"binary data"
    )
    data = await client.request("GET", "https://elis.rossum.ai/api/v1/pages/123/preview")
    assert data.content == b"binary data"


@pytest.mark.asyncio
async def test_request_repacks_exception(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
        status_code=404,
        content=b'{"detail":"Not found."}',
    )
    with pytest.raises(APIClientError) as err:
        await client._request("GET", "workspaces/123")
    assert str(err.value) == (
        "[GET] https://elis.rossum.ai/api/v1/workspaces/123 - "
        'HTTP 404 - {"detail":"Not found."}'
    )


@pytest.mark.asyncio
async def test_stream_repacks_exception(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv&exported_at=invalid",
        status_code=404,
        content=b"exported_at: Enter a valid date/time",
    )
    with pytest.raises(APIClientError) as err:
        async for _w in client._stream("GET", "queues/123/export?format=csv&exported_at=invalid"):
            pass
    assert str(err.value) == (
        "[GET] https://elis.rossum.ai/api/v1/queues/123/export?format=csv&exported_at=invalid "
        "- HTTP 404 - exported_at: Enter a valid date/time"
    )


@pytest.mark.asyncio
async def test_get_token_new(client, login_mock):
    client.token = None
    token = await client.get_token()
    assert token == NEW_TOKEN
    assert client.token == NEW_TOKEN


@pytest.mark.asyncio
async def test_get_token_old(client):
    token = await client.get_token()
    assert token == FAKE_TOKEN


@pytest.mark.asyncio
async def test_get_token_force_refresh(client, login_mock):
    token = await client.get_token(refresh=True)
    assert token == NEW_TOKEN


@pytest.fixture
def client_with_response_post_processor() -> InternalAsyncClient:
    client = InternalAsyncClient(
        username="username", password="password", response_post_processor=response_post_processor
    )
    client.token = FAKE_TOKEN
    return client


@pytest.mark.asyncio
async def test_request_response_post_processor(
    client_with_response_post_processor, httpx_mock, caplog
):
    """Test the `request` method with a custom response post processor."""
    caplog.set_level(logging.INFO)
    url = "https://elis.rossum.ai/api/v1/queues/123"
    method = "GET"
    httpx_mock.add_response(method=method, url=url)

    await client_with_response_post_processor.request(method, url)
    assert "response_post_processor visited" in caplog.text


@pytest.mark.asyncio
async def test_stream_response_post_processor(
    client_with_response_post_processor, httpx_mock, caplog
):
    """Test the `_stream` method with a custom response post processor."""
    caplog.set_level(logging.INFO)
    url = "https://elis.rossum.ai/api/v1/queues/123"
    method = "GET"
    httpx_mock.add_response(
        method=method,
        url=url,
        stream=pytest_httpx.IteratorStream([CSV_EXPORT]),
    )

    async for _ in client_with_response_post_processor._stream(method, url):
        pass
    assert "response_post_processor visited" in caplog.text


@pytest.mark.asyncio
async def test_authenticate_response_post_processor(
    client_with_response_post_processor, httpx_mock, caplog
):
    """Test the `_authenticate` method with a custom response post processor."""
    caplog.set_level(logging.INFO)
    httpx_mock.add_response(
        method="POST",
        url=build_full_login_url(client_with_response_post_processor.base_url),
        json={"key": NEW_TOKEN},
    )

    await client_with_response_post_processor._authenticate()
    assert "response_post_processor visited" in caplog.text
