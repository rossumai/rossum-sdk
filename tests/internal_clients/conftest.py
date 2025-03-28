from __future__ import annotations

import functools
import logging

import httpx
import pytest

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


UPLOAD_RESPONSE = {
    "results": [
        {
            "document": "https://elis.develop.r8.lol/api/v1/documents/3164197",
            "annotation": "https://elis.develop.r8.lol/api/v1/annotations/3154459",
        }
    ],
}

USER = {
    "id": 1,
    "url": "https://elis.rossum.ai/api/v1/users/1",
    "first_name": "John",
    "last_name": "Doe",
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


def response_post_processor(response: httpx.Response) -> None:
    logging.info("response_post_processor visited")
