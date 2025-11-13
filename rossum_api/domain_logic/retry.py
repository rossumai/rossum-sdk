from __future__ import annotations

import httpx

from rossum_api.exceptions import APIClientError

RETRIED_HTTP_CODES = (408, 429, 500, 502, 503, 504)


class ForceRetry(Exception):  # noqa: D101
    pass


def should_retry(exc: BaseException) -> bool:  # noqa: D103
    if isinstance(exc, (ForceRetry, httpx.RequestError)):
        return True
    if isinstance(exc, APIClientError):
        return exc.status_code in RETRIED_HTTP_CODES
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRIED_HTTP_CODES
    return False
