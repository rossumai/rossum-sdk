from __future__ import annotations

import asyncio
import json
import typing
from enum import Enum

import aiofiles

from rossum_api.api_client import APIClient, Resource
from rossum_api.models import deserialize_default
from rossum_api.models.task import TaskStatus

if typing.TYPE_CHECKING:
    import pathlib
    from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Sequence, Tuple, Union

    import httpx

    from rossum_api.models import Deserializer
    from rossum_api.models.annotation import Annotation
    from rossum_api.models.connector import Connector
    from rossum_api.models.document import Document
    from rossum_api.models.email_template import EmailTemplate
    from rossum_api.models.engine import Engine
    from rossum_api.models.group import Group
    from rossum_api.models.hook import Hook
    from rossum_api.models.inbox import Inbox
    from rossum_api.models.organization import Organization
    from rossum_api.models.queue import Queue
    from rossum_api.models.schema import Schema
    from rossum_api.models.task import Task
    from rossum_api.models.upload import Upload
    from rossum_api.models.user import User
    from rossum_api.models.workspace import Workspace


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
        deserializer: Optional[Deserializer] = None,
    ):
        """
        Parameters
        ----------
        base_url
            base API URL including the "/api" and version ("/v1") in the url path. For example
            "https://elis.rossum.ai/api/v1"
        deserializer
            pass a custom deserialization callable if different model classes should be returned
        """
        self._http_client = http_client or APIClient(username, password, token, base_url)
        self._deserializer = deserializer or deserialize_default

    # ##### QUEUE #####
    async def retrieve_queue(
        self,
        queue_id: int,
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        queue = await self._http_client.fetch_one(Resource.Queue, queue_id)

        return self._deserializer(Resource.Queue, queue)

    async def list_all_queues(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Queue]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        async for q in self._http_client.fetch_all(Resource.Queue, ordering, **filters):
            yield self._deserializer(Resource.Queue, q)

    async def create_new_queue(self, data: Dict[str, Any]) -> Queue:
        """https://elis.rossum.ai/api/docs/#create-new-queue."""
        queue = await self._http_client.create(Resource.Queue, data)

        return self._deserializer(Resource.Queue, queue)

    async def delete_queue(self, queue_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue."""
        return await self._http_client.delete(Resource.Queue, queue_id)

    async def import_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[int]:
        """https://elis.rossum.ai/api/docs/#import-a-document.

        Deprecated now, consider upload_document.

        Parameters
        ---------
        queue_id
            ID of the queue to upload the files to
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
        """A helper method used for the import document endpoint.

        This does not create an Upload object."""
        async with aiofiles.open(file, "rb") as fp:
            results = await self._http_client.upload(
                Resource.Queue, queue_id, fp, filename, values, metadata
            )
            (result,) = results["results"]  # We're uploading 1 file in 1 request, we can unpack
            return int(result["annotation"].split("/")[-1])

    # ##### UPLOAD #####
    async def upload_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Task]:
        """https://elis.rossum.ai/api/docs/#create-upload.

        Parameters
        ---------
        queue_id
            ID of the queue to upload the files to
        files
            2-tuple containing current filepath and name to be used by Elis for the uploaded file
        metadata
            metadata will be set to newly created annotation object
        values
            may be used to initialize datapoint values by setting the value of rir_field_names in the schema

        Returns
        -------
        task_responses
            list of Task object responses, respects the order of `files` argument
            Tasks can be polled using poll_task and if succeeded, will contain a
            link to an Upload object that contains info on uploaded documents/annotations
        """
        tasks: list[typing.Awaitable[Task]] = [
            asyncio.create_task(self._create_upload(file, queue_id, filename, values, metadata))
            for file, filename in files
        ]

        return list(await asyncio.gather(*tasks))

    async def _create_upload(
        self,
        file: Union[str, pathlib.Path],
        queue_id: int,
        filename: str,
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Helper method that uploads the files and gets back Task response for each.

        A successful Task will create an Upload object."""

        async with aiofiles.open(file, "rb") as fp:
            url = f"uploads?queue={queue_id}"
            files = {"content": (filename, await fp.read(), "application/octet-stream")}

            if values is not None:
                files["values"] = ("", json.dumps(values).encode("utf-8"), "application/json")
            if metadata is not None:
                files["metadata"] = ("", json.dumps(metadata).encode("utf-8"), "application/json")

            task_url = await self.request_json("POST", url, files=files)
            task_id = task_url["url"].split("/")[-1]

            return await self.retrieve_task(task_id)

    async def retrieve_upload(
        self,
        upload_id: int,
    ) -> Upload:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-upload."""
        upload = await self._http_client.fetch_one(Resource.Upload, upload_id)
        return self._deserializer(Resource.Upload, upload)

    async def export_annotations_to_json(
        self,
        queue_id: int,
    ) -> AsyncIterator[Annotation]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        async for chunk in self._http_client.export(Resource.Queue, queue_id, "json"):
            # JSON export can be translated directly to Annotation object
            yield self._deserializer(Resource.Annotation, typing.cast(typing.Dict, chunk))

    async def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats
    ) -> AsyncIterator[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        async for chunk in self._http_client.export(Resource.Queue, queue_id, str(export_format)):
            yield typing.cast(bytes, chunk)

    # ##### ORGANIZATIONS #####
    async def list_all_organizations(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Organization]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        async for o in self._http_client.fetch_all(Resource.Organization, ordering, **filters):
            yield self._deserializer(Resource.Organization, o)

    async def retrieve_organization(self, org_id: int) -> Organization:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        organization = await self._http_client.fetch_one(Resource.Organization, org_id)

        return self._deserializer(Resource.Organization, organization)

    async def retrieve_own_organization(self) -> Organization:
        """Retrieve organization of currently logged in user."""
        user: Dict[Any, Any] = await self._http_client.fetch_one(Resource.Auth, "user")
        organization_id = user["organization"].split("/")[-1]
        return await self.retrieve_organization(organization_id)

    # ##### SCHEMAS #####
    async def list_all_schemas(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Schema]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        async for s in self._http_client.fetch_all(Resource.Schema, ordering, **filters):
            yield self._deserializer(Resource.Schema, s)

    async def retrieve_schema(self, schema_id: int) -> Schema:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        schema: Dict[Any, Any] = await self._http_client.fetch_one(Resource.Schema, schema_id)

        return self._deserializer(Resource.Schema, schema)

    async def create_new_schema(self, data: Dict[str, Any]) -> Schema:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        schema = await self._http_client.create(Resource.Schema, data)

        return self._deserializer(Resource.Schema, schema)

    async def delete_schema(self, schema_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return await self._http_client.delete(Resource.Schema, schema_id)

    # ##### USERS #####
    async def list_all_users(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[User]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        async for u in self._http_client.fetch_all(Resource.User, ordering, **filters):
            yield self._deserializer(Resource.User, u)

    async def retrieve_user(self, user_id: int) -> User:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        user = await self._http_client.fetch_one(Resource.User, user_id)

        return self._deserializer(Resource.User, user)

    async def create_new_user(self, data: Dict[str, Any]) -> User:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        user = await self._http_client.create(Resource.User, data)

        return self._deserializer(Resource.User, user)

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
    ) -> AsyncIterator[Annotation]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations."""
        if sideloads and "content" in sideloads and not content_schema_ids:
            raise ValueError(
                'When content sideloading is requested, "content_schema_ids" must be provided'
            )
        async for a in self._http_client.fetch_all(
            Resource.Annotation, ordering, sideloads, content_schema_ids, **filters
        ):
            yield self._deserializer(Resource.Annotation, a)

    async def search_for_annotations(
        self,
        query: Optional[dict] = None,
        query_string: Optional[dict] = None,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        **kwargs: Any,
    ) -> AsyncIterator[Annotation]:
        """https://elis.rossum.ai/api/docs/#search-for-annotations."""
        if not query and not query_string:
            raise ValueError("Either query or query_string must be provided")
        json_payload = {}
        if query:
            json_payload["query"] = query
        if query_string:
            json_payload["query_string"] = query_string

        async for a in self._http_client.fetch_all_by_url(
            f"{Resource.Annotation.value}/search",
            ordering,
            sideloads,
            json=json_payload,
            method="POST",
            **kwargs,
        ):
            yield self._deserializer(Resource.Annotation, a)

    async def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[str] = ()
    ) -> Annotation:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        annotation_json = await self._http_client.fetch_one(Resource.Annotation, annotation_id)
        if sideloads:
            await self._sideload(annotation_json, sideloads)
        return self._deserializer(Resource.Annotation, annotation_json)

    async def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[Annotation], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> Annotation:
        """Poll on Annotation until predicate is true.

        Sideloading is done only once after the predicate becomes true to avoid spamming the server.
        """
        annotation_json = await self._http_client.fetch_one(Resource.Annotation, annotation_id)
        # Parse early, we want predicate to work with Annotation instances for convenience
        annotation = self._deserializer(Resource.Annotation, annotation_json)

        while not predicate(annotation):
            await asyncio.sleep(sleep_s)
            annotation_json = await self._http_client.fetch_one(Resource.Annotation, annotation_id)
            annotation = self._deserializer(Resource.Annotation, annotation_json)

        if sideloads:
            await self._sideload(annotation_json, sideloads)
        return self._deserializer(Resource.Annotation, annotation_json)

    async def poll_annotation_until_imported(
        self, annotation_id: int, **poll_kwargs: Any
    ) -> Annotation:
        """A shortcut for waiting until annotation is imported."""
        return await self.poll_annotation(
            annotation_id, lambda a: a.status not in ("importing", "created"), **poll_kwargs
        )

    async def poll_task(
        self,
        task_id: int,
        predicate: Callable[[Task], bool],
        sleep_s: int = 3,
    ) -> Task:
        """Poll on Task until predicate is true.

        As with Annotation polling, there is no innate retry limit."""
        task = await self.retrieve_task(task_id)

        while not predicate(task):
            await asyncio.sleep(sleep_s)
            task = await self.retrieve_task(task_id)

        return task

    async def poll_task_until_succeeded(
        self,
        task_id: int,
        sleep_s: int = 3,
    ) -> Task:
        """Poll on Task until it is succeeded."""
        return await self.poll_task(task_id, lambda a: a.status == TaskStatus.SUCCEEDED, sleep_s)

    async def retrieve_task(self, task_id: int) -> Task:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-task."""
        task = await self._http_client.fetch_one(
            Resource.Task, task_id, request_params={"no_redirect": "True"}
        )

        return self._deserializer(Resource.Task, task)

    async def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> Annotation:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        (annotation_id,) = await self.import_document(queue_id, [(filepath, filename)])
        return await self.poll_annotation_until_imported(annotation_id, **poll_kwargs)

    async def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        await self._http_client.request_json(
            "POST", f"{Resource.Annotation.value}/{annotation_id}/start"
        )

    async def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        annotation = await self._http_client.replace(Resource.Annotation, annotation_id, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def update_part_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        annotation = await self._http_client.update(Resource.Annotation, annotation_id, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def bulk_update_annotation_data(
        self, annotation_id: int, operations: List[Dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""
        await self._http_client.request_json(
            "POST",
            f"{Resource.Annotation.value}/{annotation_id}/content/operations",
            json={"operations": operations},
        )

    async def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        await self._http_client.request_json(
            "POST", f"{Resource.Annotation.value}/{annotation_id}/confirm"
        )

    async def create_new_annotation(self, data: dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        annotation = await self._http_client.create(Resource.Annotation, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        await self._http_client.request(
            "POST", url=f"{Resource.Annotation.value}/{annotation_id}/delete"
        )

    async def cancel_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#cancel-annotation"""
        await self._http_client.request(
            "POST", url=f"{Resource.Annotation.value}/{annotation_id}/cancel"
        )

    # ##### DOCUMENTS #####
    async def retrieve_document(self, document_id: int) -> Document:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document"""
        document: Dict[Any, Any] = await self._http_client.fetch_one(
            Resource.Document, document_id
        )

        return self._deserializer(Resource.Document, document)

    async def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        document_content = await self._http_client.request(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        return document_content.content

    async def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> Document:
        """https://elis.rossum.ai/api/docs/#create-document"""
        metadata = metadata or {}
        files: httpx._types.RequestFiles = {
            "content": (file_name, file_data),
            "metadata": ("", json.dumps(metadata).encode("utf-8")),
        }
        if parent:
            files["parent"] = ("", parent)

        document = await self._http_client.request_json(
            "POST", url=Resource.Document.value, files=files
        )

        return self._deserializer(Resource.Document, document)

    # ##### WORKSPACES #####
    async def list_all_workspaces(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Workspace]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        async for w in self._http_client.fetch_all(Resource.Workspace, ordering, **filters):
            yield self._deserializer(Resource.Workspace, w)

    async def retrieve_workspace(self, workspace_id: int) -> Workspace:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        workspace = await self._http_client.fetch_one(Resource.Workspace, workspace_id)

        return self._deserializer(Resource.Workspace, workspace)

    async def create_new_workspace(self, data: Dict[str, Any]) -> Workspace:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        workspace = await self._http_client.create(Resource.Workspace, data)

        return self._deserializer(Resource.Workspace, workspace)

    async def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-workspace."""
        return await self._http_client.delete(Resource.Workspace, workspace_id)

    # ##### ENGINE #####
    async def retrieve_engine(self, engine_id: int) -> Engine:
        """ "https://elis.rossum.ai/api/docs/#retrieve-an-engine."""
        engine = await self._http_client.fetch_one(Resource.Engine, engine_id)

        return self._deserializer(Resource.Engine, engine)

    # ##### INBOX #####
    async def create_new_inbox(self, data: Dict[str, Any]) -> Inbox:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        inbox = await self._http_client.create(Resource.Inbox, data)

        return self._deserializer(Resource.Inbox, inbox)

    # ##### EMAIL TEMPLATES #####
    async def list_all_email_templates(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-email-templates."""
        async for c in self._http_client.fetch_all(Resource.EmailTemplate, ordering, **filters):
            yield self._deserializer(Resource.EmailTemplate, c)

    async def retrieve_email_template(self, email_template_id: int) -> EmailTemplate:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object."""
        email_template = await self._http_client.fetch_one(
            Resource.EmailTemplate, email_template_id
        )

        return self._deserializer(Resource.EmailTemplate, email_template)

    async def create_new_email_template(self, data: Dict[str, Any]) -> EmailTemplate:
        """https://elis.rossum.ai/api/docs/#create-new-email-template-object."""
        email_template = await self._http_client.create(Resource.EmailTemplate, data)

        return self._deserializer(Resource.EmailTemplate, email_template)

    # ##### CONNECTORS #####
    async def list_all_connectors(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        async for c in self._http_client.fetch_all(Resource.Connector, ordering, **filters):
            yield self._deserializer(Resource.Connector, c)

    async def retrieve_connector(self, connector_id: int) -> Connector:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        connector = await self._http_client.fetch_one(Resource.Connector, connector_id)

        return self._deserializer(Resource.Connector, connector)

    async def create_new_connector(self, data: Dict[str, Any]) -> Connector:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        connector = await self._http_client.create(Resource.Connector, data)

        return self._deserializer(Resource.Connector, connector)

    # ##### HOOKS #####
    async def list_all_hooks(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Hook]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        async for h in self._http_client.fetch_all(Resource.Hook, ordering, **filters):
            yield self._deserializer(Resource.Hook, h)

    async def retrieve_hook(self, hook_id: int) -> Hook:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        hook = await self._http_client.fetch_one(Resource.Hook, hook_id)

        return self._deserializer(Resource.Hook, hook)

    async def create_new_hook(self, data: Dict[str, Any]) -> Hook:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        hook = await self._http_client.create(Resource.Hook, data)

        return self._deserializer(Resource.Hook, hook)

    async def update_part_hook(self, hook_id: int, data: Dict[str, Any]) -> Hook:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-hook"""
        hook = await self._http_client.update(Resource.Hook, hook_id, data)

        return self._deserializer(Resource.Hook, hook)

    async def delete_hook(self, hook_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-hook"""
        return await self._http_client.delete(Resource.Hook, hook_id)

    # ##### USER ROLES #####
    async def list_all_user_roles(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[Group]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        async for g in self._http_client.fetch_all(Resource.Group, ordering, **filters):
            yield self._deserializer(Resource.Group, g)

    # ##### GENERIC METHODS #####
    async def request_paginated(self, url: str, *args, **kwargs) -> AsyncIterator[dict]:
        """Use to perform requests to seldomly used or experimental endpoints with paginated response that do not have
        direct support in the client and return iterable.
        """
        async for element in self._http_client.fetch_all_by_url(url, *args, **kwargs):
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

        Parameters
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
