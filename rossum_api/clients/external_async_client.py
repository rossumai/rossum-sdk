from __future__ import annotations

import asyncio
import json
import typing

import aiofiles

from rossum_api.clients.internal_async_client import InternalAsyncClient
from rossum_api.domain_logic.annotations import (
    ExportFileFormats,
    is_annotation_imported,
    validate_list_annotations_params,
)
from rossum_api.domain_logic.documents import build_create_document_params
from rossum_api.domain_logic.emails import build_email_import_files
from rossum_api.domain_logic.resources import Resource
from rossum_api.domain_logic.search import build_search_params, validate_search_params
from rossum_api.domain_logic.tasks import is_task_succeeded
from rossum_api.domain_logic.urls import (
    EMAIL_IMPORT_URL,
    build_resource_cancel_url,
    build_resource_confirm_url,
    build_resource_content_operations_url,
    build_resource_content_url,
    build_resource_delete_url,
    build_resource_search_url,
    build_resource_start_url,
    parse_resource_id_from_url,
)
from rossum_api.dtos import Token, UserCredentials
from rossum_api.models import DocumentRelation, Email, deserialize_default
from rossum_api.models.annotation import Annotation
from rossum_api.models.connector import Connector
from rossum_api.models.document import Document
from rossum_api.models.email_template import EmailTemplate
from rossum_api.models.engine import Engine, EngineField
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
from rossum_api.utils import ObjectWithStatus

if typing.TYPE_CHECKING:
    import pathlib
    from typing import (
        Any,
        AsyncIterator,
        Callable,
        Dict,
        List,
        Optional,
        Sequence,
        Tuple,
        Union,
    )

    import httpx

    from rossum_api.models import Deserializer, ResponsePostProcessor

AnnotationType = typing.TypeVar("AnnotationType", bound=ObjectWithStatus)
ConnectorType = typing.TypeVar("ConnectorType")
DocumentType = typing.TypeVar("DocumentType")
DocumentRelationType = typing.TypeVar("DocumentRelationType")
EmailTemplateType = typing.TypeVar("EmailTemplateType")
EngineType = typing.TypeVar("EngineType")
EngineFieldType = typing.TypeVar("EngineFieldType")
GroupType = typing.TypeVar("GroupType")
HookType = typing.TypeVar("HookType")
InboxType = typing.TypeVar("InboxType")
EmailType = typing.TypeVar("EmailType")
OrganizationType = typing.TypeVar("OrganizationType")
QueueType = typing.TypeVar("QueueType")
SchemaType = typing.TypeVar("SchemaType")
TaskType = typing.TypeVar("TaskType", bound=ObjectWithStatus)
UploadType = typing.TypeVar("UploadType")
UserType = typing.TypeVar("UserType")
WorkspaceType = typing.TypeVar("WorkspaceType")


class AsyncRossumAPIClient(
    typing.Generic[
        AnnotationType,
        ConnectorType,
        DocumentType,
        DocumentRelationType,
        EmailTemplateType,
        EngineType,
        EngineFieldType,
        GroupType,
        HookType,
        InboxType,
        EmailType,
        OrganizationType,
        QueueType,
        SchemaType,
        TaskType,
        UploadType,
        UserType,
        WorkspaceType,
    ]
):
    def __init__(
        self,
        base_url: str,
        credentials: UserCredentials | Token,
        *,
        deserializer: Optional[Deserializer] = None,
        timeout: Optional[float] = None,
        n_retries: int = 3,
        retry_backoff_factor: float = 1.0,
        retry_max_jitter: float = 1.0,
        max_in_flight_requests: int = 4,
        response_post_processor: Optional[ResponsePostProcessor] = None,
    ):
        """
        Parameters
        ----------
        base_url
            base API URL including the "/api" and version ("/v1") in the url path. For example
            "https://elis.rossum.ai/api/v1"
        deserializer
            pass a custom deserialization callable if different model classes should be returned
        response_post_processor
            pass a custom response post-processing callable. Applied only if `http_client` is not provided.
        """
        token = None
        username = None
        password = None
        if isinstance(credentials, UserCredentials):
            username = credentials.username
            password = credentials.password
        else:
            token = credentials.token

        self._http_client = InternalAsyncClient(
            base_url,
            username=username,
            password=password,
            token=token,
            timeout=timeout,
            n_retries=n_retries,
            retry_backoff_factor=retry_backoff_factor,
            retry_max_jitter=retry_max_jitter,
            max_in_flight_requests=max_in_flight_requests,
            response_post_processor=response_post_processor,
        )
        self._deserializer = deserializer or deserialize_default

    # ##### QUEUE #####
    async def retrieve_queue(self, queue_id: int) -> QueueType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        queue = await self._http_client.fetch_one(Resource.Queue, queue_id)

        return self._deserializer(Resource.Queue, queue)

    async def list_queues(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[QueueType]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        async for q in self._http_client.fetch_all(Resource.Queue, ordering, **filters):
            yield self._deserializer(Resource.Queue, q)

    async def create_new_queue(self, data: Dict[str, Any]) -> QueueType:
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
            return parse_resource_id_from_url(result["annotation"])

    # ##### UPLOAD #####
    async def upload_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[TaskType]:
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
        tasks: list[typing.Awaitable[TaskType]] = [
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
    ) -> TaskType:
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
            task_id = parse_resource_id_from_url(task_url["url"])

            return await self.retrieve_task(task_id)

    async def retrieve_upload(self, upload_id: int) -> UploadType:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-upload."""
        upload = await self._http_client.fetch_one(Resource.Upload, upload_id)
        return self._deserializer(Resource.Upload, upload)

    async def export_annotations_to_json(
        self, queue_id: int, **filters: Any
    ) -> AsyncIterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        async for chunk in self._http_client.export(Resource.Queue, queue_id, "json", **filters):
            # JSON export can be translated directly to Annotation object
            yield self._deserializer(Resource.Annotation, typing.cast(typing.Dict, chunk))

    async def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats, **filters: Any
    ) -> AsyncIterator[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        async for chunk in self._http_client.export(
            Resource.Queue, queue_id, export_format.value, **filters
        ):
            yield typing.cast(bytes, chunk)

    # ##### ORGANIZATIONS #####
    async def list_organizations(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[OrganizationType]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        async for o in self._http_client.fetch_all(Resource.Organization, ordering, **filters):
            yield self._deserializer(Resource.Organization, o)

    async def retrieve_organization(self, org_id: int) -> OrganizationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        organization = await self._http_client.fetch_one(Resource.Organization, org_id)

        return self._deserializer(Resource.Organization, organization)

    async def retrieve_own_organization(self) -> OrganizationType:
        """Retrieve organization of currently logged in user."""
        user: Dict[Any, Any] = await self._http_client.fetch_one(Resource.Auth, "user")
        organization_id = parse_resource_id_from_url(user["organization"])
        return await self.retrieve_organization(organization_id)

    # ##### SCHEMAS #####
    async def list_schemas(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[SchemaType]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        async for s in self._http_client.fetch_all(Resource.Schema, ordering, **filters):
            yield self._deserializer(Resource.Schema, s)

    async def retrieve_schema(self, schema_id: int) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        schema: Dict[Any, Any] = await self._http_client.fetch_one(Resource.Schema, schema_id)

        return self._deserializer(Resource.Schema, schema)

    async def create_new_schema(self, data: Dict[str, Any]) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        schema = await self._http_client.create(Resource.Schema, data)

        return self._deserializer(Resource.Schema, schema)

    async def delete_schema(self, schema_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return await self._http_client.delete(Resource.Schema, schema_id)

    # ##### USERS #####
    async def list_users(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[UserType]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        async for u in self._http_client.fetch_all(Resource.User, ordering, **filters):
            yield self._deserializer(Resource.User, u)

    async def retrieve_user(self, user_id: int) -> UserType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        user = await self._http_client.fetch_one(Resource.User, user_id)

        return self._deserializer(Resource.User, user)

    async def create_new_user(self, data: Dict[str, Any]) -> UserType:
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
    async def list_annotations(
        self,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        content_schema_ids: Sequence[str] = (),
        **filters: Any,
    ) -> AsyncIterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations."""
        validate_list_annotations_params(sideloads, content_schema_ids)
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
    ) -> AsyncIterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#search-for-annotations."""
        validate_search_params(query, query_string)
        search_params = build_search_params(query, query_string)

        async for a in self._http_client.fetch_all_by_url(
            build_resource_search_url(Resource.Annotation),
            ordering,
            sideloads,
            json=search_params,
            method="POST",
            **kwargs,
        ):
            yield self._deserializer(Resource.Annotation, a)

    async def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[str] = ()
    ) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        annotation_json = await self._http_client.fetch_one(Resource.Annotation, annotation_id)
        if sideloads:
            await self._sideload(annotation_json, sideloads)
        return self._deserializer(Resource.Annotation, annotation_json)

    async def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[AnnotationType], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> AnnotationType:
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
    ) -> AnnotationType:
        """A shortcut for waiting until annotation is imported."""
        return await self.poll_annotation(annotation_id, is_annotation_imported, **poll_kwargs)

    async def poll_task(
        self, task_id: int, predicate: Callable[[TaskType], bool], sleep_s: int = 3
    ) -> TaskType:
        """Poll on Task until predicate is true.

        As with Annotation polling, there is no innate retry limit."""
        task = await self.retrieve_task(task_id)

        while not predicate(task):
            await asyncio.sleep(sleep_s)
            task = await self.retrieve_task(task_id)

        return task

    async def poll_task_until_succeeded(self, task_id: int, sleep_s: int = 3) -> TaskType:
        """Poll on Task until it is succeeded."""
        return await self.poll_task(task_id, is_task_succeeded, sleep_s)

    async def retrieve_task(self, task_id: int) -> TaskType:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-task."""
        task = await self._http_client.fetch_one(
            Resource.Task, task_id, request_params={"no_redirect": "True"}
        )

        return self._deserializer(Resource.Task, task)

    async def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> AnnotationType:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        (annotation_id,) = await self.import_document(queue_id, [(filepath, filename)])
        return await self.poll_annotation_until_imported(annotation_id, **poll_kwargs)

    async def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        await self._http_client.request_json(
            "POST", build_resource_start_url(Resource.Annotation, annotation_id)
        )

    async def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        annotation = await self._http_client.replace(Resource.Annotation, annotation_id, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def update_part_annotation(
        self, annotation_id: int, data: Dict[str, Any]
    ) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        annotation = await self._http_client.update(Resource.Annotation, annotation_id, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def bulk_update_annotation_data(
        self, annotation_id: int, operations: List[Dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""
        await self._http_client.request_json(
            "POST",
            build_resource_content_operations_url(Resource.Annotation, annotation_id),
            json={"operations": operations},
        )

    async def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        await self._http_client.request_json(
            "POST", build_resource_confirm_url(Resource.Annotation, annotation_id)
        )

    async def create_new_annotation(self, data: dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        annotation = await self._http_client.create(Resource.Annotation, data)

        return self._deserializer(Resource.Annotation, annotation)

    async def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        await self._http_client.request(
            "POST", url=build_resource_delete_url(Resource.Annotation, annotation_id)
        )

    async def cancel_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#cancel-annotation"""
        await self._http_client.request(
            "POST", url=build_resource_cancel_url(Resource.Annotation, annotation_id)
        )

    # ##### DOCUMENTS #####
    async def retrieve_document(self, document_id: int) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document"""
        document: Dict[Any, Any] = await self._http_client.fetch_one(
            Resource.Document, document_id
        )

        return self._deserializer(Resource.Document, document)

    async def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        document_content = await self._http_client.request(
            "GET", url=build_resource_content_url(Resource.Document, document_id)
        )
        return document_content.content

    async def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#create-document"""
        files = build_create_document_params(file_name, file_data, metadata, parent)

        document = await self._http_client.request_json(
            "POST", url=Resource.Document.value, files=files
        )

        return self._deserializer(Resource.Document, document)

    # ##### DOCUMENT RELATIONS #####
    async def list_document_relations(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[DocumentRelationType]:
        """https://elis.rossum.ai/api/docs/#list-all-document-relations"""
        async for dr in self._http_client.fetch_all(
            Resource.DocumentRelation, ordering, **filters
        ):
            yield self._deserializer(Resource.DocumentRelation, dr)

    async def retrieve_document_relation(self, document_relation_id: int) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document-relation"""
        document_relation = await self._http_client.fetch_one(
            Resource.DocumentRelation, document_relation_id
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    async def create_new_document_relation(self, data: Dict[str, Any]) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#create-a-new-document-relation"""
        document_relation = await self._http_client.create(Resource.DocumentRelation, data)

        return self._deserializer(Resource.DocumentRelation, document_relation)

    async def update_document_relation(
        self, document_relation_id: int, data: Dict[str, Any]
    ) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#update-a-document-relation"""
        document_relation = await self._http_client.replace(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    async def update_part_document_relation(
        self, document_relation_id: int, data: Dict[str, Any]
    ) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-document-relation"""
        document_relation = await self._http_client.update(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    async def delete_document_relation(self, document_relation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-document-relation"""
        await self._http_client.delete(Resource.DocumentRelation, document_relation_id)

    # ##### WORKSPACES #####
    async def list_workspaces(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[WorkspaceType]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        async for w in self._http_client.fetch_all(Resource.Workspace, ordering, **filters):
            yield self._deserializer(Resource.Workspace, w)

    async def retrieve_workspace(self, workspace_id: int) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        workspace = await self._http_client.fetch_one(Resource.Workspace, workspace_id)

        return self._deserializer(Resource.Workspace, workspace)

    async def create_new_workspace(self, data: Dict[str, Any]) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        workspace = await self._http_client.create(Resource.Workspace, data)

        return self._deserializer(Resource.Workspace, workspace)

    async def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-workspace."""
        return await self._http_client.delete(Resource.Workspace, workspace_id)

    # ##### ENGINE #####
    async def retrieve_engine(self, engine_id: int) -> EngineType:
        """ "https://elis.rossum.ai/api/docs/#retrieve-an-engine."""
        engine = await self._http_client.fetch_one(Resource.Engine, engine_id)

        return self._deserializer(Resource.Engine, engine)

    async def list_engines(
        self, ordering: Sequence[str] = (), sideloads: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[EngineType]:
        """https://elis.rossum.ai/api/docs/internal/#list-all-engines."""
        async for engine in self._http_client.fetch_all(
            Resource.Engine, ordering, sideloads, **filters
        ):
            yield self._deserializer(Resource.Engine, engine)

    async def retrieve_engine_fields(
        self, engine_id: int | None = None
    ) -> AsyncIterator[EngineFieldType]:
        """https://elis.rossum.ai/api/docs/internal/#engine-field."""
        async for engine_field in self._http_client.fetch_all(
            Resource.EngineField, engine=engine_id
        ):
            yield self._deserializer(Resource.EngineField, engine_field)

    async def retrieve_engine_queues(self, engine_id: int) -> AsyncIterator[QueueType]:
        """https://elis.rossum.ai/api/docs/internal/#list-all-queues."""
        async for queue in self._http_client.fetch_all(Resource.Queue, engine=engine_id):
            yield self._deserializer(Resource.Queue, queue)

    # ##### INBOX #####
    async def create_new_inbox(self, data: Dict[str, Any]) -> InboxType:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        inbox = await self._http_client.create(Resource.Inbox, data)

        return self._deserializer(Resource.Inbox, inbox)

    # ##### EMAILS #####
    async def retrieve_email(self, email_id: int) -> EmailType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email."""
        email = await self._http_client.fetch_one(Resource.Email, email_id)

        return self._deserializer(Resource.Email, email)

    async def import_email(
        self, raw_message: bytes, recipient: str, mime_type: str | None = None
    ) -> str:
        """https://elis.rossum.ai/api/docs/#import-email.

        Returns task URL.
        """
        response = await self._http_client.request_json(
            "POST",
            url=EMAIL_IMPORT_URL,
            files=build_email_import_files(raw_message, recipient, mime_type),
        )
        return response["url"]

    # ##### EMAIL TEMPLATES #####
    async def list_email_templates(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[EmailTemplateType]:
        """https://elis.rossum.ai/api/docs/#list-all-email-templates."""
        async for c in self._http_client.fetch_all(Resource.EmailTemplate, ordering, **filters):
            yield self._deserializer(Resource.EmailTemplate, c)

    async def retrieve_email_template(self, email_template_id: int) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object."""
        email_template = await self._http_client.fetch_one(
            Resource.EmailTemplate, email_template_id
        )

        return self._deserializer(Resource.EmailTemplate, email_template)

    async def create_new_email_template(self, data: Dict[str, Any]) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#create-new-email-template-object."""
        email_template = await self._http_client.create(Resource.EmailTemplate, data)

        return self._deserializer(Resource.EmailTemplate, email_template)

    # ##### CONNECTORS #####
    async def list_connectors(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[ConnectorType]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        async for c in self._http_client.fetch_all(Resource.Connector, ordering, **filters):
            yield self._deserializer(Resource.Connector, c)

    async def retrieve_connector(self, connector_id: int) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        connector = await self._http_client.fetch_one(Resource.Connector, connector_id)

        return self._deserializer(Resource.Connector, connector)

    async def create_new_connector(self, data: Dict[str, Any]) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        connector = await self._http_client.create(Resource.Connector, data)

        return self._deserializer(Resource.Connector, connector)

    # ##### HOOKS #####
    async def list_hooks(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[HookType]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        async for h in self._http_client.fetch_all(Resource.Hook, ordering, **filters):
            yield self._deserializer(Resource.Hook, h)

    async def retrieve_hook(self, hook_id: int) -> HookType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        hook = await self._http_client.fetch_one(Resource.Hook, hook_id)

        return self._deserializer(Resource.Hook, hook)

    async def create_new_hook(self, data: Dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        hook = await self._http_client.create(Resource.Hook, data)

        return self._deserializer(Resource.Hook, hook)

    async def update_part_hook(self, hook_id: int, data: Dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-hook"""
        hook = await self._http_client.update(Resource.Hook, hook_id, data)

        return self._deserializer(Resource.Hook, hook)

    async def delete_hook(self, hook_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-hook"""
        return await self._http_client.delete(Resource.Hook, hook_id)

    # ##### USER ROLES #####
    async def list_user_roles(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> AsyncIterator[GroupType]:
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

    async def authenticate(self) -> None:
        await self._http_client._authenticate()

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


# Type alias for an AsyncRossumAPIClient that uses the default deserializer
AsyncRossumAPIClientWithDefaultDeserializer = AsyncRossumAPIClient[
    Annotation,
    Connector,
    Document,
    DocumentRelation,
    EmailTemplate,
    Engine,
    EngineField,
    Group,
    Hook,
    Inbox,
    Email,
    Organization,
    Queue,
    Schema,
    Task,
    Upload,
    User,
    Workspace,
]
