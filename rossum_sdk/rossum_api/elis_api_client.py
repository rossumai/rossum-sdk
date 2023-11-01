from __future__ import annotations

import asyncio
import typing
from enum import Enum

import aiofiles
import dacite

from rossum_sdk.rossum_api.api_client import APIClient
from rossum_sdk.rossum_api.models.annotation import Annotation
from rossum_sdk.rossum_api.models.connector import Connector
from rossum_sdk.rossum_api.models.hook import Hook
from rossum_sdk.rossum_api.models.inbox import Inbox
from rossum_sdk.rossum_api.models.organization import Organization
from rossum_sdk.rossum_api.models.queue import Queue
from rossum_sdk.rossum_api.models.schema import Schema
from rossum_sdk.rossum_api.models.user import User
from rossum_sdk.rossum_api.models.user_role import UserRole
from rossum_sdk.rossum_api.models.workspace import Workspace

if typing.TYPE_CHECKING:
    import pathlib
    from typing import Any, AsyncIterable, Callable, Dict, List, Optional, Sequence, Tuple, Union

    import httpx


class ExportFileFormats(Enum):
    CSV = "csv"
    XML = "xml"
    XLSX = "xlsx"


class Sideload:
    pass


class ElisAPIClient:
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[APIClient] = None,
    ):
        self._http_client = http_client or APIClient(username, password, token, base_url)

    # ##### QUEUE #####
    async def retrieve_queue(
        self,
        queue_id: int,
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        queue = await self._http_client.fetch_one("queues", queue_id)

        return dacite.from_dict(Queue, queue)

    async def list_all_queues(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Queue]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        async for q in self._http_client.fetch_all("queues", ordering, **filters):
            yield dacite.from_dict(Queue, q)

    async def create_new_queue(self, data: Dict[str, Any]) -> Queue:
        """https://elis.rossum.ai/api/docs/#create-new-queue."""
        queue = await self._http_client.create("queues", data)

        return dacite.from_dict(Queue, queue)

    async def delete_queue(self, queue_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue."""
        return await self._http_client.delete("queues", queue_id)

    async def import_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[int]:
        """https://elis.rossum.ai/api/docs/#import-a-document.

        arguments
        ---------
            files
                2-tuple containing current filepath and name to be used by Elis for the uploaded file
            metadata
                metadata will be set to newly created annotation object
            values
                may be used to initialize datapoint values by setting the value of rir_field_names in the schema

        Returns
        -------
            annotation_ids
                list of IDs of created annotations, respects the order of `files` argument
        """
        tasks = [
            asyncio.create_task(self._upload(file, queue_id, filename, values, metadata))
            for file, filename in files
        ]

        return await asyncio.gather(*tasks)

    async def _upload(self, file, queue_id, filename, values, metadata) -> int:
        async with aiofiles.open(file, "rb") as fp:
            results = await self._http_client.upload(
                "queues", queue_id, fp, filename, values, metadata
            )
            (result,) = results["results"]  # We're uploading 1 file in 1 request, we can unpack
            return int(result["annotation"].split("/")[-1])

    async def export_annotations_to_json(
        self,
        queue_id: int,
    ) -> AsyncIterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        async for chunk in self._http_client.export("queues", queue_id, "json"):
            # JSON export can be translated directly to Annotation object
            yield dacite.from_dict(Annotation, typing.cast(typing.Dict, chunk))

    async def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats
    ) -> AsyncIterable[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        async for chunk in self._http_client.export("queues", queue_id, str(export_format)):
            yield typing.cast(bytes, chunk)

    # ##### ORGANIZATIONS #####
    async def list_all_organizations(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ):
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        async for o in self._http_client.fetch_all("organizations", ordering, **filters):
            yield dacite.from_dict(Organization, o)

    async def retrieve_organization(self, org_id: int) -> Organization:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        organization: Dict[Any, Any] = await self._http_client.fetch_one("organizations", org_id)

        return dacite.from_dict(Organization, organization)

    async def retrieve_own_organization(self) -> Organization:
        """Retrive organization of currently logged in user."""
        user: Dict[Any, Any] = await self._http_client.fetch_one("auth", "user")
        organization_id = user["organization"].split("/")[-1]
        return await self.retrieve_organization(organization_id)

    # ##### SCHEMAS #####
    async def list_all_schemas(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Schema]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        async for s in self._http_client.fetch_all("schemas", ordering, **filters):
            yield dacite.from_dict(Schema, s)

    async def retrieve_schema(self, schema_id: int) -> Schema:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        schema: Dict[Any, Any] = await self._http_client.fetch_one("schemas", schema_id)

        return dacite.from_dict(Schema, schema)

    async def create_new_schema(self, data: Dict[str, Any]) -> Schema:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        queue = await self._http_client.create("schemas", data)

        return dacite.from_dict(Schema, queue)

    async def delete_schema(self, schema_id) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return await self._http_client.delete("schemas", schema_id)

    # ##### USERS #####
    async def list_all_users(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[User]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        async for u in self._http_client.fetch_all("users", ordering, **filters):
            yield dacite.from_dict(User, u)

    async def retrieve_user(self, user_id: int) -> User:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        user = await self._http_client.fetch_one("users", user_id)

        return dacite.from_dict(User, user)

    async def create_new_user(self, data: Dict[str, Any]) -> User:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        user = await self._http_client.create("users", data)

        return dacite.from_dict(User, user)

    # TODO: specific method in APICLient
    def change_user_password(self, new_password: str) -> dict:
        return {}

    # TODO: specific method in APICLient
    def reset_user_password(self, email: str) -> dict:
        return {}

    # ##### ANNOTATIONS #####
    async def list_all_annotations(
        self,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        content_schema_ids: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations."""
        if sideloads and "content" in sideloads and not content_schema_ids:
            raise ValueError(
                'When content sideloading is requested, "content_schema_ids" must be provided'
            )
        async for a in self._http_client.fetch_all(
            "annotations", ordering, sideloads, content_schema_ids, **filters
        ):
            yield dacite.from_dict(Annotation, a)

    async def search_for_annotations(
        self,
        query: Optional[dict] = None,
        query_string: Optional[dict] = None,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        **kwargs: Any,
    ) -> AsyncIterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#search-for-annotations."""
        if not query and not query_string:
            raise ValueError("Either query or query_string must be provided")
        json_payload = {}
        if query:
            json_payload["query"] = query
        if query_string:
            json_payload["query_string"] = query_string

        async for a in self._http_client.fetch_all(
            "annotations/search", ordering, sideloads, json=json_payload, method="POST", **kwargs
        ):
            yield dacite.from_dict(Annotation, a)

    async def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[str] = ()
    ) -> Annotation:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        annotation_json = await self._http_client.fetch_one("annotations", annotation_id)
        if sideloads:
            await self._sideload(annotation_json, sideloads)
        return dacite.from_dict(Annotation, annotation_json)

    async def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[Annotation], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> Annotation:
        """Poll on annotation until predicate is true.

        Sideloading is done only once after the predicate becomes true to avoid spaming the server.
        """
        annotation_json = await self._http_client.fetch_one("annotations", annotation_id)
        # Parse early, we want predicate to work with Annotation instances for convenience
        annotation = dacite.from_dict(Annotation, annotation_json)

        while not predicate(annotation):
            await asyncio.sleep(sleep_s)
            annotation_json = await self._http_client.fetch_one("annotations", annotation_id)
            annotation = dacite.from_dict(Annotation, annotation_json)

        if sideloads:
            await self._sideload(annotation_json, sideloads)
        return dacite.from_dict(Annotation, annotation_json)

    async def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        annotation = await self._http_client.replace("annotations", annotation_id, data)

        return dacite.from_dict(Annotation, annotation)

    async def update_part_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        annotation = await self._http_client.update("annotations", annotation_id, data)

        return dacite.from_dict(Annotation, annotation)

    # ##### WORKSPACES #####
    async def list_all_workspaces(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Workspace]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        async for w in self._http_client.fetch_all("workspaces", ordering, **filters):
            yield dacite.from_dict(Workspace, w)

    async def retrieve_workspace(self, workspace_id) -> Workspace:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        workspace = await self._http_client.fetch_one("workspaces", workspace_id)

        return dacite.from_dict(Workspace, workspace)

    async def create_new_workspace(self, data: Dict[str, Any]) -> Workspace:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        workspace = await self._http_client.create("workspaces", data)

        return dacite.from_dict(Workspace, workspace)

    async def delete_workspace(self, workspace_id) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-workspace."""
        return await self._http_client.delete("workspaces", workspace_id)

    # ##### INBOX #####
    async def create_new_inbox(self, data: Dict[str, Any]) -> Inbox:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        inbox = await self._http_client.create("inboxes", data)

        return dacite.from_dict(Inbox, inbox)

    # ##### CONNECTORS #####
    async def list_all_connectors(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        async for c in self._http_client.fetch_all("connectors", ordering, **filters):
            yield dacite.from_dict(Connector, c)

    async def retrieve_connector(self, connector_id) -> Connector:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        connector = await self._http_client.fetch_one("connectors", connector_id)

        return dacite.from_dict(Connector, connector)

    async def create_new_connector(self, data: Dict[str, Any]) -> Connector:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        connector = await self._http_client.create("connectors", data)

        return dacite.from_dict(Connector, connector)

    # ##### HOOKS #####
    async def list_all_hooks(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[Hook]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        async for h in self._http_client.fetch_all("hooks", ordering, **filters):
            yield dacite.from_dict(Hook, h)

    async def retrieve_hook(self, hook_id) -> Hook:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        hook = await self._http_client.fetch_one("hooks", hook_id)

        return dacite.from_dict(Hook, hook)

    async def create_new_hook(self, data: Dict[str, Any]) -> Hook:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        hook = await self._http_client.create("hooks", data)

        return dacite.from_dict(Hook, hook)

    # ##### USER ROLES #####
    async def list_all_user_roles(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterable[UserRole]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        async for u in self._http_client.fetch_all("groups", ordering, **filters):
            yield dacite.from_dict(UserRole, u)

    # ##### GENERIC METHODS #####
    async def request_paginated(self, resource: str, *args, **kwargs) -> AsyncIterable[dict]:
        """Use to perform requests to seldomly used or experimental endpoints with paginated response that do not have
        direct support in the client and return iterable.
        """
        async for element in self._http_client.fetch_all(resource, *args, **kwargs):
            yield element

    async def request_json(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return JSON.
        """
        return await self._http_client.request_json(method, *args, **kwargs)

    async def request(self, method: str, *args, **kwargs) -> httpx.Response:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return the raw response.
        """
        return await self._http_client.request(method, *args, **kwargs)

    async def get_token(self, refresh: bool = False) -> str:
        """Returns the current token. Authentication is done automatically if needed.

        Arguments:
        ----------
        refresh
            force refreshing the token
        """
        return await self._http_client.get_token(refresh)

    async def _sideload(self, resource: Dict[str, Any], sideloads: Sequence[str]) -> None:
        """The API does not support sideloading when fetching a single resource, we need to load
        it manually.
        """
        sideload_tasks = [
            asyncio.create_task(self._http_client.request_json("GET", resource[sideload]))
            for sideload in sideloads
        ]
        sideloaded_jsons = await asyncio.gather(*sideload_tasks)

        for sideload, sideloaded_json in zip(sideloads, sideloaded_jsons):
            if sideload == "content":  # Content (i.e. list of sections is wrapped in a dict)
                sideloaded_json = sideloaded_json["content"]
            resource[sideload] = sideloaded_json
