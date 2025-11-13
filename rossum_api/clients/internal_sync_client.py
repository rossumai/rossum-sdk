from __future__ import annotations

import typing

import httpx
import tenacity

from rossum_api.domain_logic.annotations import (
    build_export_query_params,
    get_http_method_for_annotation_export,
)
from rossum_api.domain_logic.pagination import build_pagination_params
from rossum_api.domain_logic.retry import ForceRetry, should_retry
from rossum_api.domain_logic.sideloads import build_sideload_params, embed_sideloads
from rossum_api.domain_logic.urls import build_export_url, build_full_login_url, build_url
from rossum_api.dtos import Token, UserCredentials
from rossum_api.exceptions import APIClientError
from rossum_api.utils import enforce_domain

if typing.TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from typing import Any

    from rossum_api.domain_logic.resources import Resource
    from rossum_api.models import ResponsePostProcessor
    from rossum_api.types import HttpMethod, JsonDict, Sideload


class InternalSyncClient:  # noqa: D101
    def __init__(
        self,
        base_url: str,
        credentials: UserCredentials | Token,
        *,
        timeout: float | None = None,
        n_retries: int = 3,
        retry_backoff_factor: float = 1.0,
        retry_max_jitter: float = 1.0,
        response_post_processor: ResponsePostProcessor | None = None,
    ):
        self.base_url = base_url
        self.client = httpx.Client(timeout=timeout)
        self.n_retries = n_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.retry_max_jitter = retry_max_jitter
        self.response_post_processor = response_post_processor

        self.token = None
        self.username = None
        self.password = None
        if isinstance(credentials, UserCredentials):
            self.username = credentials.username
            self.password = credentials.password
        else:
            self.token = credentials.token

    def _authenticate(self) -> None:
        for attempt in self._retrying():
            with attempt:
                response = self.client.post(
                    build_full_login_url(self.base_url),
                    data={"username": self.username, "password": self.password},
                )
                if self.response_post_processor is not None:
                    self.response_post_processor(response)
                self._raise_for_status(response)
        self.token = response.json()["key"]

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def create(self, resource: Resource, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object."""
        return self.request_json("POST", resource.value, json=data)

    def replace(self, resource: Resource, id_: int, data: dict[str, Any]) -> dict[str, Any]:
        """Modify an entire existing object."""
        return self.request_json("PUT", build_url(resource, id_), json=data)

    def update(self, resource: Resource, id_: int, data: dict[str, Any]) -> dict[str, Any]:
        """Modify particular fields of an existing object."""
        return self.request_json("PATCH", build_url(resource, id_), json=data)

    def delete(self, resource: Resource, id_: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        self._request("DELETE", build_url(resource, id_))

    def upload(self, url: str, files: dict[str, Any]) -> dict[str, Any]:
        """Upload a file to a resource that supports this."""
        return self.request_json("POST", url, files=files)

    def export(  # noqa: D102
        self,
        resource: Resource,
        id_: int,
        export_format: str,
        columns: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[dict[str, Any] | bytes]:
        query_params = build_export_query_params(export_format, columns, **filters)
        url = build_export_url(resource, id_)
        method = get_http_method_for_annotation_export(**filters)

        if export_format == "json":
            # JSON export is paginated just like a regular fetch_all, it abuses **filters kwargs of
            # fetch_all_by_url to pass export-specific query params
            yield from self.fetch_resources_by_url(url, method=method, **query_params)  # type: ignore
        else:
            # In CSV/XML/XLSX case, all annotations are returned, i.e. the response can be large,
            # chunks of bytes are yielded from HTTP stream to keep memory consumption low.
            yield from self._stream(method, url, params=query_params)

    def _stream(self, method: HttpMethod, url: str, *args: Any, **kwargs: Any) -> Iterator[bytes]:
        """Perform a streaming HTTP call."""
        if not self.token:
            self._authenticate()

        # Do not force the calling site to always prepend the base URL
        url = enforce_domain(url, self.base_url)

        for attempt in self._retrying():
            with (
                attempt,
                self.client.stream(
                    method, url, headers=self._headers, *args, **kwargs
                ) as response,
            ):
                if self.response_post_processor is not None:
                    self.response_post_processor(response)
                if response.status_code == 401:
                    self._authenticate()
                    if attempt.retry_state.attempt_number == 1:
                        raise ForceRetry()
                self._raise_for_status(response)
                yield from response.iter_bytes()

    def fetch_resource(
        self, resource: Resource, id_: int | str, request_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Retrieve a single object in a specific resource.

        Allows passing extra params specifically to allow disabling redirects feature of Tasks.
        See https://elis.rossum.ai/api/docs/#task.
        If redirects are desired, our raise_for_status wrapper must account for that.
        """
        return self.request_json("GET", build_url(resource, id_), params=request_params)

    def fetch_resources(
        self,
        resource: Resource,
        ordering: Sequence[str] = (),
        sideloads: Sequence[Sideload] = (),
        content_schema_ids: Sequence[str] = (),
        method: HttpMethod = "GET",
        json: JsonDict | None = None,
        max_pages: int | None = None,
        **filters: Any,
    ) -> Iterator[dict[str, Any]]:
        """Retrieve a list of objects in a specific resource."""
        return self.fetch_resources_by_url(
            resource.value,
            ordering,
            sideloads,
            content_schema_ids,
            method,
            json,
            max_pages,
            **filters,
        )

    def fetch_resources_by_url(  # noqa: D102
        self,
        url: str,
        ordering: Sequence[str] = (),
        sideloads: Sequence[Sideload] = (),
        content_schema_ids: Sequence[str] = (),
        method: HttpMethod = "GET",
        json: JsonDict | None = None,
        max_pages: int | None = None,
        **filters: Any,
    ) -> Iterator[dict[str, Any]]:
        query_params = build_pagination_params(ordering)
        query_params.update(build_sideload_params(sideloads, content_schema_ids))
        query_params.update(**filters)

        return self._fetch_paginated_results(url, method, query_params, sideloads, json, max_pages)

    def _fetch_paginated_results(
        self,
        url: str,
        method: HttpMethod,
        query_params: dict[str, Any],
        sideloads: Sequence[Sideload],
        json: JsonDict | None,
        max_pages: int | None,
    ) -> Iterator[dict[str, Any]]:
        first_page_results, total_pages = self._fetch_page(
            url, method, query_params, sideloads, json=json
        )

        yield from first_page_results
        last_page = min(total_pages, max_pages or total_pages)

        for page_number in range(2, last_page + 1):
            results, _ = self._fetch_page(
                url, method, {**query_params, "page": page_number}, sideloads, json=json
            )
            yield from results

    def _fetch_page(
        self,
        url: str,
        method: HttpMethod,
        query_params: dict[str, Any],
        sideload_groups: Sequence[Sideload],
        json: JsonDict | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        data = self.request_json(method, url, params=query_params, json=json)
        embed_sideloads(data, sideload_groups)
        return data["results"], data["pagination"]["total_pages"]

    def request_json(self, method: HttpMethod, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: D102
        response = self._request(method, *args, **kwargs)
        if response.status_code == 204:
            return {}
        return response.json()  # type: ignore[no-any-return]

    def request(self, method: HttpMethod, *args: Any, **kwargs: Any) -> httpx.Response:  # noqa: D102
        return self._request(method, *args, **kwargs)

    def _retrying(self) -> tenacity.Retrying:
        """Build Tenacity retrying according to desired settings."""
        return tenacity.Retrying(
            wait=tenacity.wait_exponential_jitter(
                initial=self.retry_backoff_factor, jitter=self.retry_max_jitter
            ),
            retry=tenacity.retry_if_exception(should_retry),
            stop=tenacity.stop_after_attempt(self.n_retries),
            reraise=True,
        )

    def _request(  # noqa: RET503 (false positive)
        self, method: HttpMethod, url: str, *args: Any, **kwargs: Any
    ) -> httpx.Response:
        """Perform the actual HTTP call and does error handling.

        Arguments:
        ----------
        url
            base URL is prepended with base_url if needed
        """
        if not self.token:
            self._authenticate()
        url = enforce_domain(url, self.base_url)

        for attempt in self._retrying():
            with attempt:
                response = self.client.request(method, url, headers=self._headers, *args, **kwargs)
                if self.response_post_processor is not None:
                    self.response_post_processor(response)
                if response.status_code == 401 and self.username and self.password:
                    self._authenticate()
                    if attempt.retry_state.attempt_number == 1:
                        raise ForceRetry()
                self._raise_for_status(response)
                return response

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise an exception in case of HTTP error.

        Re-pack to our own exception class to shield users from the fact that we're using
        httpx which should be an implementation detail.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            content = response.content if response.stream is None else response.read()
            raise APIClientError(
                response.request.method,
                response.url,
                response.status_code,
                content.decode("utf-8"),
            ) from e

    def sideload(self, resource: dict[str, Any], sideloads: Sequence[Sideload]) -> None:
        """Update sideloaded resources in place.

        The API does not support sideloading when fetching a single resource, we need to load
        it manually.
        """
        fetched_sideloads = []
        for sideload in sideloads:
            sideload_url = resource[sideload]
            fetched_sideloads.append(self.request_json("GET", url=sideload_url))

        for sideload, fetched_sideload in zip(sideloads, fetched_sideloads):
            if sideload == "content":  # Content (i.e. list of sections is wrapped in a dict)
                fetched_sideload = fetched_sideload["content"]
            resource[sideload] = fetched_sideload
