from __future__ import annotations

import asyncio
import functools
import itertools
import json
import logging
import random
import typing

import httpx

if typing.TYPE_CHECKING:
    from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Sequence, Tuple, Union

    from aiofiles.threadpool.binary import AsyncBufferedReader


RETRIED_HTTP_CODES = (408, 429, 500, 502, 503, 504)
logger = logging.getLogger(__name__)


class APIClientError(Exception):
    def __init__(self, status_code, error):
        self.status_code = status_code
        self.error = error

    def __str__(self):
        return f"HTTP {self.status_code}, content: {self.error}"


def authenticate_if_needed(method):
    """Decorate a method to perform authentication if an APIClient method fails on 401.

    It is used both when starting the client when there is no token and when an existing token
    expires.
    """

    @functools.wraps(method)
    async def authenticate_if_needed(self: APIClient, *args, **kwargs):
        # Authenticate if there is no token, no need to fire the request only to get 401 and retry
        if self.token is None:
            await self._authenticate()
        try:
            return await method(self, *args, **kwargs)
        except APIClientError as e:
            if e.status_code != 401:
                raise
            logger.debug("Token expired, authenticating user %s...", self.username)
            await self._authenticate()
            return await method(self, *args, **kwargs)

    return authenticate_if_needed


def authenticate_generator_if_needed(method):
    """Decorate an async generator method to perform authentication if an APIClient method fails
    on 401.

    It is used both when starting the client when there is no token and when an existing token
    expires.

    It shares most of the code with authenticate_if_needed but we haven't found a way to create
    an async decorator that works on both coroutines and async generators.
    """

    @functools.wraps(method)
    async def authenticate_if_needed(self: APIClient, *args, **kwargs):
        # Authenticate if there is no token, no need to fire the request only to get 401 and retry
        if self.token is None:
            await self._authenticate()
        try:
            async for chunk in method(self, *args, **kwargs):
                yield chunk
        except APIClientError as e:
            if e.status_code != 401:
                raise
            logger.debug("Token expired, authenticating user %s...", self.username)
            await self._authenticate()
            async for chunk in method(self, *args, **kwargs):
                yield chunk

    return authenticate_if_needed


def exponential_backoff(factor: float) -> Iterator[float]:
    yield 0
    for n in itertools.count(2):
        yield (factor * (2 ** (n - 2))) + (factor * random.random())


class APIClient:
    """Perform CRUD operations over resources provided by Elis API.

    Requests will be retried up to `n_retries` times with exponential backoff.
    The backoff is applied after the second attempt and its length is determined
    by following equation `retry_backoff_factor * (2 ** (nth_attempt - 1)) + random_jitter`.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = "https://elis.rossum.ai/api/v1",
        timeout: Optional[float] = None,
        n_retries: int = 3,
        retry_backoff_factor: float = 1.0,
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

    @property
    def _headers(self):
        return {"Authorization": f"token {self.token}"}

    async def fetch_one(self, resource: str, id_: Union[int, str]) -> Dict[str, Any]:
        """Retrieve a single object in a specific resource."""
        return await self.request_json("GET", f"{resource}/{id_}")

    async def fetch_all(
        self,
        resource: str,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        content_schema_ids: Sequence[str] = (),
        method: str = "GET",
        **filters: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
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
        filters
            mapping from resource field to value used to filter records
        """
        query_params = {
            "page_size": 100,
            "ordering": ",".join(ordering),
            "sideload": ",".join(sideloads),
            "content.schema_id": ",".join(content_schema_ids),
            **filters,
        }
        results, total_pages = await self._fetch_page(
            f"{resource}", method, query_params, sideloads
        )
        # Fire async tasks to fetch the rest of the pages and start yielding results from page 1
        page_requests = [
            asyncio.create_task(
                self._fetch_page(f"{resource}", method, {**query_params, "page": i}, sideloads)
            )
            for i in range(2, total_pages + 1)
        ]
        for r in results:
            yield r
        # Await requests one by one to yield results in correct order to ensure the same order of
        # results next time the same resource is fetched. This slightly descreases throughput.
        for request in page_requests:
            results, _ = await request
            for r in results:
                yield r

    async def _fetch_page(
        self,
        resource: str,
        method: str,
        query_params: Dict[str, Any],
        sideload_groups: Sequence[str],
    ) -> Tuple[List[Dict[str, Any]], int]:
        data = await self.request_json(method, resource, params=query_params)
        self._embed_sideloads(data, sideload_groups)
        return data["results"], data["pagination"]["total_pages"]

    def _embed_sideloads(
        self, response_data: Dict[str, Any], sideload_groups: Sequence[str]
    ) -> None:
        """Embed sideloads into the results to enable simple access to the sideloaded objects."""
        sideloads_by_id: Dict[str, Dict[int, Union[dict, list]]] = {}
        for sideload_group in sideload_groups:
            if sideload_group == "content":
                # Datapoints from all annotations are present in content, we have to construct
                # content (list of datapoints) for each annotation
                def annotation_id(datapoint):
                    return int(
                        datapoint["url"].replace(f"/content/{datapoint['id']}", "").split("/")[-1]
                    )

                sideloads_by_id[sideload_group] = {
                    k: list(v)
                    for k, v in itertools.groupby(
                        sorted(response_data[sideload_group], key=annotation_id), key=annotation_id
                    )
                }
            else:
                sideloads_by_id[sideload_group] = {
                    s["id"]: s for s in response_data[sideload_group]
                }

        for result, sideload_group in itertools.product(response_data["results"], sideload_groups):
            sideload_name = sideload_group.rstrip("s")  # Singular form is used in results
            url = result[sideload_name]
            if url is None:
                continue
            sideload_id = int(url.replace("/content", "").split("/")[-1])

            result[sideload_name] = sideloads_by_id[sideload_group].get(
                sideload_id, []
            )  # `content` can have 0 datapoints, use [] default value in this case

    async def create(self, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object."""
        return await self.request_json("POST", resource, json=data)

    async def replace(self, resource: str, id_: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify an entire existing object."
        return await self.request_json("PUT", f"{resource}/{id_}", json=data)

    async def update(self, resource: str, id_: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify particular fields of an existing object."
        return await self.request_json("PATCH", f"{resource}/{id_}", json=data)

    async def delete(self, resource: str, id_: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        await self._request("DELETE", f"{resource}/{id_}")

    async def upload(
        self,
        resource: str,
        id_: int,
        fp: AsyncBufferedReader,
        filename: str,
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
        url = f"{resource}/{id_}/upload"
        files = {"content": (filename, await fp.read(), "application/octet-stream")}

        # Filename of values and metadata must be "", otherwise Elis API returns HTTP 400 with body
        # "Value must be valid JSON."
        if values is not None:
            files["values"] = ("", json.dumps(values).encode("utf-8"), "application/json")
        if metadata is not None:
            files["metadata"] = ("", json.dumps(metadata).encode("utf-8"), "application/json")
        return await self.request_json("POST", url, files=files)

    async def export(
        self,
        resource: str,
        id_: int,
        export_format: str,
        columns: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Union[Dict[str, Any], bytes]]:
        query_params = {"format": export_format}
        filters = filters or {}
        if filters:
            query_params = {**query_params, **filters}
        if columns:
            query_params["columns"] = ",".join(columns)
        url = f"{resource}/{id_}/export"
        # to_status parameter is valid only in POST requests, we can use GET in all other cases
        method = "POST" if "to_status" in filters else "GET"
        if export_format == "json":
            # JSON export is paginated just like a regular fetch_all, it abuses **filters kwargs of
            # fetch_all to pass export-specific query params
            async for result in self.fetch_all(url, method=method, **query_params):
                yield result
        else:
            # In CSV/XML/XLSX case, all annotations are returned, i.e. the response can be large,
            # chunks of bytes are yielded from HTTP stream to keep memory consumption low.
            async for bytes_chunk in self._stream(method, url, params=query_params):
                yield bytes_chunk

    async def request_json(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        response = await self._request(method, *args, **kwargs)
        if response.status_code == 204:
            return {}
        return response.json()

    async def request(self, method: str, *args, **kwargs) -> httpx.Response:
        response = await self._request(method, *args, **kwargs)
        return response

    async def get_token(self, refresh: bool = False) -> str:
        """Returns the current token. Authentication is done automatically if needed.

        Arguments:
        ----------
        refresh
            force refreshing the token
        """
        if refresh or self.token is None:
            await self._authenticate()
        return self.token  # type: ignore[return-value] # self.token is set in _authenticate method

    async def _authenticate(self) -> None:
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            data={"username": self.username, "password": self.password},
        )
        await self._raise_for_status(response)
        self.token = response.json()["key"]

    @authenticate_if_needed
    async def _request(self, method: str, url: str, *args, **kwargs) -> httpx.Response:
        """Performs the actual HTTP call and does error handling.

        Arguments:
        ----------
        url
            base URL is prepended with base_url if needed
        """
        # Do not force the calling site to alway prepend the base URL
        if not url.startswith("https://"):
            url = f"{self.base_url}/{url}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"token {self.token}"

        for attempt, backoff in zip(
            range(1, self.n_retries + 1), exponential_backoff(self.retry_backoff_factor)
        ):
            remaining_attempts = self.n_retries - attempt

            try:
                response = await self.client.request(method, url, headers=headers, *args, **kwargs)
                if response.status_code in RETRIED_HTTP_CODES:
                    continue
                break
            except httpx.RequestError:
                if not remaining_attempts:
                    raise
            asyncio.sleep(backoff)

        await self._raise_for_status(response)
        return response

    @authenticate_generator_if_needed
    async def _stream(self, method: str, url: str, *args, **kwargs) -> AsyncIterator[bytes]:
        """Performs a streaming HTTP call."""
        # Do not force the calling site to alway prepend the base URL
        if not url.startswith("https://"):
            url = f"{self.base_url}/{url}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"token {self.token}"
        async with self.client.stream(method, url, headers=headers, *args, **kwargs) as response:
            await self._raise_for_status(response)
            async for chunk in response.aiter_bytes():
                yield chunk

    async def _raise_for_status(self, response: httpx.Response):
        """Raise an exception in case of HTTP error.

        Re-pack to our own exception class to shield users from the fact that we're using
        httpx which should be an implementation detail.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            content = response.content if response.stream is None else await response.aread()
            raise APIClientError(response.status_code, content.decode("utf-8")) from e
