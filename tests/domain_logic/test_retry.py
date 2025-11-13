from __future__ import annotations

import httpx
import pytest

from rossum_api.domain_logic.retry import ForceRetry, should_retry
from rossum_api.exceptions import APIClientError


@pytest.mark.parametrize(
    "exception, expected_result",
    [
        pytest.param(ForceRetry(), True, id="force_retry"),
        pytest.param(httpx.RequestError("Error"), True, id="httpx.RequestError"),
        pytest.param(
            APIClientError("GET", "url", 429, None),
            True,
            id="APIClientError_code_retriable",
        ),
        pytest.param(
            APIClientError("GET", "url", 501, None),
            False,
            id="APIClientError_code_not_retriable",
        ),
        pytest.param(
            httpx.HTTPStatusError(
                "Error", request=httpx.Request("GET", "url"), response=httpx.Response(429)
            ),
            True,
            id="httpx.HTTPStatusError_code_retriable",
        ),
        pytest.param(
            httpx.HTTPStatusError(
                "Error", request=httpx.Request("GET", "url"), response=httpx.Response(501)
            ),
            False,
            id="httpx.HTTPStatusError_code_not_retriable",
        ),
    ],
)
def test_should_retry(exception: BaseException, expected_result: bool) -> None:
    assert should_retry(exception) == expected_result
