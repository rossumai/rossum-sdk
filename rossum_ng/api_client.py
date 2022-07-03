from __future__ import annotations

"""
TODO
* convert datetimes to ISO 8601
* sideloading
* enum with resource types instead of strings
* password reset
* rate limiting?
"""
import asyncio
import functools
import json
import logging
import typing

import httpx

if typing.TYPE_CHECKING:
    from typing import Any, AsyncIterator, Dict, List, Optional, Sequence, Tuple, Union

    from aiofiles.threadpool.binary import AsyncFileIO

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


class APIClient:
    """Perform CRUD operations over resources provided by Elis API."""

    def __init__(
        self,
        username: str,
        password: str,
        base_url: Optional[str] = "https://elis.rossum.ai/api/v1",
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient()

    @property
    def _headers(self):
        return {"Authorization": f"token {self.token}"}

    async def fetch_one(self, resource: str, id_: int) -> Dict[str, Any]:
        """Retrieve a single object in a specific resource."""
        response = await self._request("GET", f"{resource}/{id_}")
        return response.json()

    async def fetch_all(
        self, resource: str, ordering: Sequence[str] = (), method: str = "GET", **filters: Any
    ) -> AsyncIterator[Dict[str, Any]]:
        """Retrieve a list of objects in a specific resource.

        Arguments
        ---------
        resource
            name of the resource provided by Elis API
        ordering
            comma-delimited fields of the resource, prepend the field with - for descending
        method
            export endpoints have different semantics when POST is used, allow customization of
            method so that export() can re-use fetch_all() implementation
        filters
            mapping from resource field to value used to filter records
        """
        query_params = {
            "page_size": 100,
            "ordering": ",".join(ordering),
            **filters,
        }
        results, total_pages = await self._fetch_page(f"{resource}", method, query_params)
        # Fire async tasks to fetch the rest of the pages and start yielding results from page 1
        page_requests = [
            asyncio.create_task(
                self._fetch_page(f"{resource}", method, {**query_params, "page": i})
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
        self, resource: str, method: str, query_params: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], int]:
        response = await self._request(method, resource, params=query_params)
        data = response.json()
        return data["results"], data["pagination"]["total_pages"]

    async def create(self, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object."""
        response = await self._request("POST", resource, json=data)
        return response.json()

    async def replace(self, resource: str, id_: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify an entire existing object."
        response = await self._request("PUT", f"{resource}/{id_}", json=data)
        return response.json()

    async def update(self, resource: str, id_: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify particular fields of an existing object."
        response = await self._request("PATCH", f"{resource}/{id_}", json=data)
        return response.json()

    async def delete(self, resource: str, id_: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        await self._request("DELETE", f"{resource}/{id_}")

    async def upload(
        self,
        resource: str,
        id_: int,
        fp: AsyncFileIO,
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
        response = await self._request("POST", url, files=files)
        return response.json()

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

    async def _authenticate(self):
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            data={"username": self.username, "password": self.password},
        )
        await self._raise_for_status(response)
        self.token = response.json()["key"]

    @authenticate_if_needed
    async def _request(self, method: str, url_part: str, *args, **kwargs) -> httpx.Response:
        """Performs the actual HTTP call and does error handling."""
        # Do not force the calling site to alway prepend the base URL
        url = f"{self.base_url}/{url_part}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"token {self.token}"
        response = await self.client.request(method, url, headers=headers, *args, **kwargs)
        await self._raise_for_status(response)
        return response

    @authenticate_generator_if_needed
    async def _stream(self, method: str, url_part: str, *args, **kwargs) -> AsyncIterator[bytes]:
        """Performs a streaming HTTP call"""
        # Do not force the calling site to alway prepend the base URL
        url = f"{self.base_url}/{url_part}"
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
