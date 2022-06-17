from __future__ import annotations

"""
TODO
* exception repacking
* upload a file: /v1/queues/{id}/upload
* export annotations: /v1/queues/{id}/export
* enum with resource types instead of strings
* password reset
* rate limiting?
"""
import asyncio
import functools
import logging
import typing
import urllib.parse

import httpx

if typing.TYPE_CHECKING:
    from typing import Any, AsyncIterator, Dict, Iterable, Optional, Tuple

logger = logging.getLogger(__name__)


class HTTPError(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


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
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 401:
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
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            data={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        self.token = response.json()["key"]

    @property
    def _headers(self):
        return {"Authorization": f"token {self.token}"}

    @authenticate_if_needed
    async def fetch_one(self, resource: str, id: int) -> Dict[str, Any]:
        """Retrieve a single object in a specific resource."""
        response = await self.client.get(f"{self.base_url}/{resource}/{id}", headers=self._headers)
        response.raise_for_status()
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
        results, next_page_url, total_pages = await self._fetch_page(
            f"{self.base_url}/{resource}?{query_params}"
        )
        # Fire async tasks to fetch the rest of the pages and start yielding results from page 1
        page_requests = [
            asyncio.create_task(
                self._fetch_page(f"{self.base_url}/{resource}?page={i}&{query_params}")
            )
            for i in range(2, total_pages + 1)
        ]
        for r in results:
            yield r
        # Await requests one by one to yield results in correct order to ensure the same order of
        # results next time the same resource is fetched. This slightly descreases throughput.
        for request in page_requests:
            results, next_page_url, _ = await request
            for r in results:
                yield r

    @authenticate_if_needed
    async def _fetch_page(self, page_url) -> Tuple[Dict[str, Any], str, int]:
        response = await self.client.get(page_url, headers=self._headers)
        response.raise_for_status()
        data = response.json()
        return data["results"], data["pagination"]["next"], data["pagination"]["total_pages"]

    @authenticate_if_needed
    async def create(self, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object."""
        response = await self.client.post(
            f"{self.base_url}/{resource}",
            headers={**self._headers},
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @authenticate_if_needed
    async def replace(self, resource: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify an entire existing object."
        response = await self.client.put(
            f"{self.base_url}/{resource}/{id}",
            headers={**self._headers},
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @authenticate_if_needed
    async def update(self, resource: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        "Modify particular fields of an existing object."
        response = await self.client.patch(
            f"{self.base_url}/{resource}/{id}",
            headers={**self._headers},
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @authenticate_if_needed
    async def delete(self, resource: str, id: int) -> None:
        """Delete a particular object.

        Use with caution: For some objects, it triggers a cascade delete of related objects.
        """
        response = await self.client.delete(
            f"{self.base_url}/{resource}/{id}", headers=self._headers
        )
        response.raise_for_status()

    @authenticate_if_needed
    async def upload(self, resource: str, id: int) -> None:
        pass
