"""Test APIClient methods.

* all HTTP calls are mocked using httpx_mock which results into nicer code that using unittest.mock
* `workspace` is used as resource in most tests to make the examples representative.
* all CRUD methods are tested for both a happy path and an error (400 or 404)
"""
import copy
import functools
import json

import aiofiles
import httpx
import mock
import pytest
import pytest_httpx

from rossum_api.api_client import APIClient, APIClientError

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
        "organization": "https://elis.rossum.ai/api/v1/organizations/456",
        "queues": [],
        "metadata": {},
    },
    {
        "id": 4321,
        "name": "Test Workspace",
        "url": "https://elis.rossum.ai/api/v1/workspaces/4321",
        "autopilot": False,
        "organization": "https://elis.rossum.ai/api/v1/organizations/123",
        "queues": [],
        "metadata": {},
    },
]

ANNOTATIONS = [  # Most fields are stripped as these are not important for the test
    {
        "id": 1111,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11289",
        "content": "https://elis.develop.r8.lol/api/v1/annotations/1111/content",
        "automation_blocker": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
    },
    {
        "id": 2222,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11288",
        "content": "https://elis.develop.r8.lol/api/v1/annotations/2222/content",
        "automation_blocker": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
    },
    {
        "id": 3333,
        "document": "https://elis.develop.r8.lol/api/v1/documents/11287",
        # URL that targets empty content should be translated to an empty list when sideloading
        "content": "https://elis.develop.r8.lol/api/v1/annotations/3333/content",
        # None URL is skipped when sideloading
        "automation_blocker": None,
    },
]

AUTOMATION_BLOCKERS = [
    {
        "id": 55,
        "url": "https://elis.develop.r8.lol/api/v1/automation_blockers/55",
        "content": [{"type": "automation_disabled", "level": "annotation"}],
        "annotation": "https://elis.develop.r8.lol/api/v1/annotations/971782",
    }
]

CONTENT = [
    {
        "id": 11,
        "schema_id": "invoice_id",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/2222/content/11",
        "content": {
            "value": "1234",
        },
    },
    {
        "id": 22,
        "schema_id": "invoice_id",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/1111/content/22",
        "content": {
            "value": "5678",
        },
    },
    {
        "id": 33,
        "schema_id": "date_issue",
        "category": "datapoint",
        "url": "https://elis.develop.r8.lol/api/v1/annotations/2222/content/33",
        "content": {
            "value": "2021-12-31",
        },
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
EXPECTED_UPLOAD_CONTENT = b'--313131\r\nContent-Disposition: form-data; name="content"; filename="filename.pdf"\r\nContent-Type: application/octet-stream\r\n\r\nFake PDF.\r\n--313131\r\nContent-Disposition: form-data; name="values"\r\nContent-Type: application/json\r\n\r\n{"upload:organization_unit": "Sales"}\r\n--313131\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n{"project": "Market ABC"}\r\n--313131--\r\n'

CSV_EXPORT = b"meta_file_name,Invoice number\r\nfilename_1.pdf,11111\r\nfilename_2.pdf,22222"
FAKE_TOKEN = "fake-token"
NEW_TOKEN = "our-token"


def count_calls(func):
    @functools.wraps(func)
    def count_calls_(*args, **kwargs):
        count_calls_.calls += 1
        return func(*args, n_calls=count_calls_.calls, **kwargs)

    count_calls_.calls = 0
    return count_calls_


@pytest.fixture
def client():
    client = APIClient("username", "password", retry_backoff_factor=0)
    client.token = FAKE_TOKEN
    return client


@pytest.fixture
def login_mock(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://elis.rossum.ai/api/v1/auth/login",
        json={
            "key": NEW_TOKEN,
            "domain": "custom-domain.app.rossum.ai",
        },
    )
    return httpx_mock


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
async def test_init_token(httpx_mock):
    """Verifies that we can create client using token and call API without 'auth' call."""
    client = APIClient(token=FAKE_TOKEN)

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        json={},
    )
    await client.fetch_one("users", 1)
    assert len(httpx_mock.get_requests()) == 1
    assert httpx_mock.get_requests()[0].headers["Authorization"] == f"token {FAKE_TOKEN}"


@pytest.mark.asyncio
async def test_not_possible_to_reauth(httpx_mock):
    """Invalid token used, trying to to re-auth without password, get error. Transparently displays it."""
    client = APIClient(token=FAKE_TOKEN)

    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/users/1",
        status_code=401,
        content=b"unauth!",
    )
    httpx_mock.add_response(
        url="https://elis.rossum.ai/api/v1/auth/login",
        status_code=400,
        json={"password": ["This field may not be blank."]},
    )
    with pytest.raises(APIClientError) as err:
        await client.fetch_one("users", 1)

    assert err.value.status_code == 400
    assert err.value.error == '{"password": ["This field may not be blank."]}'


@pytest.mark.asyncio
async def test_retry_timeout(client, httpx_mock):
    @count_calls
    def custom_response(request: httpx.Request, n_calls: int):
        if n_calls == 1:
            raise httpx.ReadTimeout("Unable to read within timeout")

        return httpx.Response(status_code=200, json=WORKSPACES[0])

    httpx_mock.add_callback(custom_response)
    workspace = await client.fetch_one("workspaces", id_=7694)
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
        await client.fetch_one("workspaces", id_=7694)


@pytest.mark.asyncio
async def test_fetch_one(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces/7694",
        json=WORKSPACES[0],
    )
    workspace = await client.fetch_one("workspaces", id_=7694)
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
    workspaces = [w async for w in client.fetch_all("workspaces")]
    assert workspaces == WORKSPACES


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
    workspaces = [w async for w in client.fetch_all("workspaces", ordering=["-id", "name"])]
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
    workspaces = [w async for w in client.fetch_all("workspaces", name="Test", autopilot=1)]
    assert workspaces == WORKSPACES


@pytest.mark.asyncio
async def test_fetch_all_sideload(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/workspaces?page_size=100&sideload=content,automation_blockers&content.schema_id=invoice_id,date_issue&ordering=",
        json={
            "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
            "results": ANNOTATIONS,
            "content": CONTENT,
            "automation_blockers": AUTOMATION_BLOCKERS,
        },
    )
    workspaces = [
        w
        async for w in client.fetch_all(
            "workspaces",
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

    assert workspaces == expected_annotations


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
    workspace = await client.replace("workspaces", id_=123, data=data)
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
    workspace = await client.update("workspaces", id_=123, data=data)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_delete(client, httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="https://elis.rossum.ai/api/v1/workspaces/123",
    )
    result = await client.delete("workspaces", id_=123)
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
                    "queues",
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
            "queues", id_=123, export_format="json", columns=cols, id="456,789", **filters
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
            "queues", id_=123, export_format="csv", columns=cols, id="456,789", **filters
        )
    ]
    assert b"".join(export_chunks) == CSV_EXPORT  # Streamed chunks are yielded in correct order


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
        workspace = await client.fetch_one("workspaces", id_=7694)
    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_authenticate_generator_if_needed_token_expired(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        headers={"Authorization": "token fake-token"},
        status_code=401,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        match_headers={"Authorization": "token new-token"},
        stream=pytest_httpx.IteratorStream([CSV_EXPORT[:20], CSV_EXPORT[20:]]),
    )

    def set_token():
        client.token = "new-token"

    with mock.patch.object(client, "_authenticate", side_effect=set_token):
        chunks = [chunk async for chunk in client._stream("GET", "queues/123/export?format=csv")]
    assert b"".join(chunks) == CSV_EXPORT


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
        workspace = await client.fetch_one("workspaces", id_=7694)

    assert workspace == WORKSPACES[0]


@pytest.mark.asyncio
async def test_authenticate_generator_if_needed_no_token(client, httpx_mock):
    client = APIClient("username", "password")
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv",
        match_headers={"Authorization": "token new-token"},
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
    data = await client.request(
        "GET", "https://elis.rossum.ai/api/v1/pages/123/preview"
    )
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
    assert str(err.value) == 'HTTP 404, content: {"detail":"Not found."}'


@pytest.mark.asyncio
async def test_stream_repacks_exception(client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://elis.rossum.ai/api/v1/queues/123/export?format=csv&exported_at=invalid",
        status_code=404,
        content=b"exported_at: Enter a valid date/time",
    )
    with pytest.raises(APIClientError) as err:
        async for w in client._stream("GET", "queues/123/export?format=csv&exported_at=invalid"):
            pass
    assert str(err.value) == "HTTP 404, content: exported_at: Enter a valid date/time"


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
