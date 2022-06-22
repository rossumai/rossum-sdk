from __future__ import annotations

"""
TODO
* export annotations: /v1/queues/{id}/export
* enum with resource types instead of strings
* password reset
* rate limiting?
"""
import asyncio
import functools
import json
import logging
import typing
import urllib.parse

import httpx

if typing.TYPE_CHECKING:
    from typing import Any, AsyncIterator, Dict, Iterable, Optional, Tuple

    from aiofiles.threadpool.binary import AsyncFileIO

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    def __init__(self, status_code, error):
        self.status_code = status_code
        self.error = error

    def __str__(self):
        return f"HTTP {self.status_code}, content: {self.error}"


def authenticate_if_needed(method):
    """Decore a method to perform authentication if a APIClient method fails on 401.

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
            logger.debug(f"Token expired, authenticating user {self.username!r}...")
            await self._authenticate()
            return await method(self, *args, **kwargs)

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

    async def _authenticate(self):
        response = await self._request(
            self.client.post,
            "auth/login",
            data={"username": self.username, "password": self.password},
        )
        self.token = response.json()["key"]

    @property
    def _headers(self):
        return {"Authorization": f"token {self.token}"}

    @authenticate_if_needed
    async def fetch_one(self, resource: str, id: int) -> Dict[str, Any]:
        """Retrieve a single object in a specific resource."""
        response = await self._request(self.client.get, f"{resource}/{id}", headers=self._headers)
        return response.json()

    async def fetch_all(
        self, resource: str, ordering: Iterable[str] = (), **filters: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Retrieve a list of objects in a specific resource.

        Arguments
        ---------
        resource
            name of the resource provided by Elis API
        ordering
            comma-delimited fields of the resource, prepend the field with - for descending
        filters
            mapping from resource field to value used to filter records
        """
        query_params = urllib.parse.urlencode(
            {
                "page_size": 100,
                "ordering": ",".join(ordering),
                **filters,
            }
        )
        results, total_pages = await self._fetch_page(f"{resource}?{query_params}")
        # Fire async tasks to fetch the rest of the pages and start yielding results from page 1
        page_requests = [
            asyncio.create_task(self._fetch_page(f"{resource}?page={i}&{query_params}"))
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

    @authenticate_if_needed
    async def _fetch_page(self, page_url) -> Tuple[Dict[str, Any], int]:
        response = await self._request(self.client.get, page_url, headers=self._headers)
        data = response.json()
        return data["results"], data["pagination"]["total_pages"]

    @authenticate_if_needed
    async def create(self, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object."""
        response = await self._request(
            self.client.post, resource, headers={**self._headers}, json=data
        )
        return response.json()

    @authenticate_if_needed
    async def replace(self, resource: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify an entire existing object."
        response = await self._request(
            self.client.put, f"{resource}/{id}", headers={**self._headers}, json=data
        )
        return response.json()

    @authenticate_if_needed
    async def update(self, resource: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify particular fields of an existing object."
        response = await self._request(
            self.client.patch, f"{resource}/{id}", headers={**self._headers}, json=data
        )
        return response.json()

    @authenticate_if_needed
    async def delete(self, resource: str, id: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        await self._request(self.client.delete, f"{resource}/{id}", headers=self._headers)

    @authenticate_if_needed
    async def upload(
        self,
        resource: str,
        id: int,
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

        url = f"{resource}/{id}/upload"
        files = {"content": (filename, await fp.read(), "application/octet-stream")}

        # Filename of values and metadata must be "", otherwise Elis API returns HTTP 400 with body
        # "Value must be valid JSON."
        if values is not None:
            files["values"] = ("", json.dumps(values).encode("utf-8"), "application/json")
        if metadata is not None:
            files["metadata"] = ("", json.dumps(metadata).encode("utf-8"), "application/json")
        response = await self._request(
            self.client.post, url, headers={**self._headers}, files=files
        )
        return response.json()

    async def _request(self, method, url_part: str, *args, **kwargs) -> httpx.Response:
        """Performs the actual HTTP call and does error handling."""
        # Do not force the calling site to alway prepend the base URL
        url = f"{self.base_url}/{url_part}"
        response = await method(url, *args, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Re-pack the exception to our own class to shield users from the fact that we're using
            # httpx which should be an implementation detail.
            raise APIClientError(response.status_code, response.content.decode("utf-8")) from e
        return response
