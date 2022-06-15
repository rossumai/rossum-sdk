from __future__ import annotations

"""
TODO
* pagination
* exception repacking
* filters and ordering
* upload a file: /v1/queues/{id}/upload
* export annotations: /v1/queues/{id}/export
* enum with resource types instead of strings
"""

import functools
import inspect
import logging
import types
import typing

import httpx

if typing.TYPE_CHECKING:
    from typing import Any, AsyncIterator, Dict, Iterable, List, Optional

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


def authenticate_if_needed_generator(method):
    """Perform authentication if a APIClient method fails on 401.

    This is a version for methods that are async generators.
    """

    @functools.wraps(method)
    async def authenticate_if_needed(self: APIClient, *args, **kwargs):
        # Authenticate if there is no token, no need to fire the request only to get 401 and retry
        if self.token is None:
            await self._authenticate()
        try:
            async for item in method(self, *args, **kwargs):
                yield item
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 401:
                raise
            logger.debug(f"Token expired, authenticating user {self.username!r}...")
            await self._authenticate()
            # TODO we might want to cope with expired token in the middle of yielding. The
            # try-except and authentication might need to be inlined to understand pagination,
            # i.e. to authenticate if request for page N fails and continue from N.
            async for item in method(self, *args, **kwargs):
                yield item

    return authenticate_if_needed


class APIClient:
    """Perform CRUD operations over resources provided by Elis API."""

    def __init__(
        self, username: str, password: str, base_url: str = "https://elis.rossum.ai/api/v1"
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
        """Retrieve a single object in a specific category."""
        response = await self.client.get(f"{self.base_url}/{resource}/{id}", headers=self._headers)
        response.raise_for_status()
        return response.json()

    @authenticate_if_needed_generator
    async def fetch_all(self, resource: str) -> AsyncIterator[Dict[str, Any]]:
        """Retrieve a list of objects in a specific category."""
        response = await self.client.get(
            f"{self.base_url}/{resource}?page_size=100", headers=self._headers
        )
        response.raise_for_status()
        data = response.json()
        for r in data["results"]:
            yield r

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
