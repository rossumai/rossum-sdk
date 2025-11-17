from __future__ import annotations

import asyncio
import logging
import typing

import httpx
import tenacity

from rossum_api.domain_logic.annotations import (
    build_export_query_params,
    get_http_method_for_annotation_export,
)
from rossum_api.domain_logic.pagination import build_pagination_params
from rossum_api.domain_logic.resources import NON_PAGINATED_RESOURCES
from rossum_api.domain_logic.retry import ForceRetry, should_retry
from rossum_api.domain_logic.sideloads import build_sideload_params, embed_sideloads
from rossum_api.domain_logic.upload import build_upload_files
from rossum_api.domain_logic.urls import (
    DEFAULT_BASE_URL,
    build_export_url,
    build_full_login_url,
    build_upload_url,
    build_url,
)
from rossum_api.exceptions import APIClientError
from rossum_api.utils import enforce_domain

if typing.TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence
    from typing import Any

    from aiofiles.threadpool.binary import AsyncBufferedReader

    from rossum_api.domain_logic.resources import Resource
    from rossum_api.models import ResponsePostProcessor
    from rossum_api.types import HttpMethod, JsonDict, Sideload


RETRIED_HTTP_CODES = (408, 429, 500, 502, 503, 504)
logger = logging.getLogger(__name__)


class InternalAsyncClient:
    """Perform CRUD operations over resources provided by Elis API.

    Requests will be retried up to `n_retries` times with exponential backoff.
    The backoff is applied after the second attempt and its length is determined
    by following equation `retry_backoff_factor * (2 ** (nth_attempt - 1)) + random_jitter`.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        *,
        timeout: float | None = None,
        n_retries: int = 3,
        retry_backoff_factor: float = 1.0,
        retry_max_jitter: float = 1.0,
        max_in_flight_requests: int = 4,
        response_post_processor: ResponsePostProcessor | None = None,
    ):
        if token is None and (username is None and password is None):
            raise TypeError(
                "__init__() missing arguments: 'username' + 'password' OR 'token' must be specified!"
            )

        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = token
        self.client = httpx.AsyncClient(timeout=timeout)
        self.n_retries = n_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.retry_max_jitter = retry_max_jitter
        self.max_in_flight_requests = max_in_flight_requests
        self.response_post_processor = response_post_processor

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    async def fetch_one(
        self, resource: Resource, id_: int | str, request_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Retrieve a single object in a specific resource.

        Allows passing extra params specifically to allow disabling redirects feature of Tasks.
        See https://elis.rossum.ai/api/docs/#task.
        If redirects are desired, our raise_for_status wrapper must account for that.
        """
        return await self.request_json("GET", build_url(resource, id_), params=request_params)

    async def fetch_all(
        self,
        resource: Resource,
        ordering: Sequence[str] = (),
        sideloads: Sequence[Sideload] = (),
        content_schema_ids: Sequence[str] = (),
        method: HttpMethod = "GET",
        max_pages: int | None = None,
        json: JsonDict | None = None,
        **filters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Retrieve a list of objects in a specific resource.

        Arguments
        ---------
        resource
            name of the resource provided by Elis API
        ordering
            comma-delimited fields of the resource, prepend the field with - for descending
        sideloads
            A sequence of resources to be fetched along with the requested resource,
            e.g. ["content", "automation_blockers"] when fetching `annotations` resource.
        content_schema_ids
            sideloads only particular `content` fields when fetching `annotations` resource,
            has no effect when fetching other resources
        method
            export endpoints have different semantics when POST is used, allow customization of
            method so that export() can re-use fetch_all() implementation
        max_pages
            maximum number of pages to fetch
        json
            json payload sent with the request. Used for POST requests.
        filters
            mapping from resource field to value used to filter records
        """
        async for result in self.fetch_all_by_url(
            resource.value,
            ordering,
            sideloads,
            content_schema_ids,
            method,
            max_pages,
            json,
            paginated=resource not in NON_PAGINATED_RESOURCES,
            **filters,
        ):
            yield result

    async def fetch_all_by_url(
        self,
        url: str,
        ordering: Sequence[str] = (),
        sideloads: Sequence[Sideload] = (),
        content_schema_ids: Sequence[str] = (),
        method: HttpMethod = "GET",
        max_pages: int | None = None,
        json: JsonDict | None = None,
        paginated: bool = True,
        **filters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Retrieve a list of objects from a specified URL.

        Arguments
        ---------
        url
            url relative to the Elis API domain, e.g. "/annotations/search"
        ordering
            comma-delimited fields of the resource, prepend the field with - for descending
        sideloads
            A sequence of resources to be fetched along with the requested resource,
            e.g. ["content", "automation_blockers"] when fetching `annotations` resource.
        content_schema_ids
            sideloads only particular `content` fields when fetching `annotations` resource,
            has no effect when fetching other resources
        method
            export endpoints have different semantics when POST is used, allow customization of
            method so that export() can re-use fetch_all() implementation
        max_pages
            maximum number of pages to fetch
        json
            json payload sent with the request. Used for POST requests.
        filters
            mapping from resource field to value used to filter records
        """
        query_params = {
            **build_pagination_params(ordering),
            **build_sideload_params(sideloads, content_schema_ids),
            **filters,
        }

        if not paginated:
            data = await self.request_json(method, url, params=query_params, json=json)
            embed_sideloads(data, sideloads)
            for r in data["results"]:
                yield r
            return

        results, total_pages = await self._fetch_page(
            url, method, query_params, sideloads, json=json
        )
        # Fire async tasks to fetch the rest of the pages and start yielding results from page 1
        last_page = min(total_pages, max_pages or total_pages)

        in_flight_guard = asyncio.Semaphore(self.max_in_flight_requests)

        async def _fetch_page(page_number: int) -> tuple[list[dict[str, Any]], int]:
            async with in_flight_guard:
                return await self._fetch_page(
                    url, method, {**query_params, "page": page_number}, sideloads, json=json
                )

        page_requests = [asyncio.create_task(_fetch_page(i)) for i in range(2, last_page + 1)]
        for r in results:
            yield r
        # Await requests one by one to yield results in correct order to ensure the same order of
        # results next time the same resource is fetched. This slightly decreases throughput.
        for request in page_requests:
            results, _ = await request
            for r in results:
                yield r

    async def _fetch_page(
        self,
        url: str,
        method: HttpMethod,
        query_params: dict[str, Any],
        sideload_groups: Sequence[Sideload],
        json: JsonDict | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        data = await self.request_json(method, url, params=query_params, json=json)
        embed_sideloads(data, sideload_groups)
        return data["results"], data["pagination"]["total_pages"]

    async def create(self, resource: Resource, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object."""
        return await self.request_json("POST", resource.value, json=data)

    async def replace(self, resource: Resource, id_: int, data: dict[str, Any]) -> dict[str, Any]:
        """Modify an entire existing object."""
        return await self.request_json("PUT", build_url(resource, id_), json=data)

    async def update(self, resource: Resource, id_: int, data: dict[str, Any]) -> dict[str, Any]:
        """Modify particular fields of an existing object."""
        return await self.request_json("PATCH", build_url(resource, id_), json=data)

    async def delete(self, resource: Resource, id_: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        await self._request("DELETE", build_url(resource, id_))

    async def upload(
        self,
        resource: Resource,
        id_: int,
        fp: AsyncBufferedReader,
        filename: str,
        values: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Upload a file to a resource that supports this.

        Arguments
        ---------
            filename
                name that will be used by Elis for the uploaded file
            metadata
                metadata will be set to the object created by the upload
            values
                may be used to initialize values of the object created from the uploaded file,
                semantics is different for each resource
        """
        url = build_upload_url(resource, id_)
        files = build_upload_files(await fp.read(), filename, values, metadata)
        return await self.request_json("POST", url, files=files)

    async def export(  # noqa: D102
        self,
        resource: Resource,
        id_: int,
        export_format: str,
        columns: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[dict[str, Any] | bytes]:
        query_params = build_export_query_params(export_format, columns, **filters)
        url = build_export_url(resource, id_)
        # to_status parameter is valid only in POST requests, we can use GET in all other cases
        method = get_http_method_for_annotation_export(**filters)
        if export_format == "json":
            # JSON export is paginated just like a regular fetch_all, it abuses **filters kwargs of
            # fetch_all_by_url to pass export-specific query params
            async for result in self.fetch_all_by_url(url, method=method, **query_params):  # type: ignore
                yield result
        else:
            # In CSV/XML/XLSX case, all annotations are returned, i.e. the response can be large,
            # chunks of bytes are yielded from HTTP stream to keep memory consumption low.
            async for bytes_chunk in self._stream(method, url, params=query_params):
                yield bytes_chunk

    async def request_json(self, method: HttpMethod, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: D102
        response = await self._request(method, *args, **kwargs)
        if response.status_code == 204:
            return {}
        return response.json()  # type: ignore[no-any-return]

    async def request(self, method: HttpMethod, *args: Any, **kwargs: Any) -> httpx.Response:  # noqa: D102
        return await self._request(method, *args, **kwargs)

    async def get_token(self, refresh: bool = False) -> str:
        """Return the current token. Authentication is done automatically if needed.

        Parameters
        ----------
        refresh
            force refreshing the token
        """
        if refresh or self.token is None:
            await self._authenticate()
        return self.token  # type: ignore[return-value] # self.token is set in _authenticate method

    async def _authenticate(self) -> None:
        async for attempt in self._retrying():
            with attempt:
                url = build_full_login_url(self.base_url)
                response = await self.client.post(
                    url,
                    data={"username": self.username, "password": self.password},
                )
                if self.response_post_processor is not None:
                    self.response_post_processor(response)
                await self._raise_for_status(response, "POST")
        self.token = response.json()["key"]

    def _retrying(self) -> tenacity.AsyncRetrying:
        """Build Tenacity retrying according to desired settings."""
        return tenacity.AsyncRetrying(
            wait=tenacity.wait_exponential_jitter(
                initial=self.retry_backoff_factor, jitter=self.retry_max_jitter
            ),
            retry=tenacity.retry_if_exception(should_retry),
            stop=tenacity.stop_after_attempt(self.n_retries),
            reraise=True,
        )

    async def _request(  # noqa: RET503 (false positive)
        self, method: HttpMethod, url: str, *args: Any, **kwargs: Any
    ) -> httpx.Response:
        """Perform the actual HTTP call and does error handling.

        Parameters
        ----------
        url
            base URL is prepended with base_url if needed
        """
        if not self.token:
            await self._authenticate()
        url = enforce_domain(url, self.base_url)

        async for attempt in self._retrying():
            with attempt:
                response = await self.client.request(
                    method, url, headers=self._headers, *args, **kwargs
                )
                if self.response_post_processor is not None:
                    self.response_post_processor(response)
                if response.status_code == 401 and self.username and self.password:
                    await self._authenticate()
                    if attempt.retry_state.attempt_number == 1:
                        raise ForceRetry()
                await self._raise_for_status(response, method)
                return response

    async def _stream(
        self, method: HttpMethod, url: str, *args: Any, **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Perform a streaming HTTP call."""
        if not self.token:
            await self._authenticate()
        url = enforce_domain(url, self.base_url)

        async for attempt in self._retrying():
            with attempt:
                async with self.client.stream(
                    method, url, headers=self._headers, *args, **kwargs
                ) as response:
                    if self.response_post_processor is not None:
                        self.response_post_processor(response)
                    if response.status_code == 401 and self.username and self.password:
                        await self._authenticate()
                        if attempt.retry_state.attempt_number == 1:
                            raise ForceRetry()
                    await self._raise_for_status(response, method)
                    async for chunk in response.aiter_bytes():
                        yield chunk

    async def _raise_for_status(self, response: httpx.Response, method: HttpMethod) -> None:
        """Raise an exception in case of HTTP error.

        Re-pack to our own exception class to shield users from the fact that we're using
        httpx which should be an implementation detail.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            content = response.content if response.stream is None else await response.aread()
            raise APIClientError(
                method, response.url, response.status_code, content.decode("utf-8")
            ) from e
