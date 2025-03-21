from __future__ import annotations

import asyncio
import threading
import typing
from concurrent.futures import ThreadPoolExecutor
from queue import Queue as ThreadSafeQueue

from rossum_api import ElisAPIClient
from rossum_api.domain_logic.urls import DEFAULT_BASE_URL
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

if typing.TYPE_CHECKING:
    import pathlib
    from typing import (
        Any,
        AsyncIterator,
        Callable,
        Dict,
        Iterator,
        List,
        Optional,
        Sequence,
        Tuple,
        TypeVar,
        Union,
    )

    import httpx

    from rossum_api import ExportFileFormats
    from rossum_api.api_client import APIClient
    from rossum_api.models import Deserializer, ResponsePostProcessor

    T = TypeVar("T")

AnnotationType = typing.TypeVar("AnnotationType")
ConnectorType = typing.TypeVar("ConnectorType")
DocumentType = typing.TypeVar("DocumentType")
EmailTemplateType = typing.TypeVar("EmailTemplateType")
EngineType = typing.TypeVar("EngineType")
EngineFieldType = typing.TypeVar("EngineFieldType")
GroupType = typing.TypeVar("GroupType")
HookType = typing.TypeVar("HookType")
InboxType = typing.TypeVar("InboxType")
OrganizationType = typing.TypeVar("OrganizationType")
QueueType = typing.TypeVar("QueueType")
SchemaType = typing.TypeVar("SchemaType")
TaskType = typing.TypeVar("TaskType")
UploadType = typing.TypeVar("UploadType")
UserType = typing.TypeVar("UserType")
WorkspaceType = typing.TypeVar("WorkspaceType")

thread_local = threading.local()


def get_or_create_event_loop():
    if not hasattr(thread_local, "loop"):
        thread_local.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_local.loop)
    return thread_local.loop


def run_coroutine_in_thread(coroutine):
    loop = get_or_create_event_loop()
    return loop.run_until_complete(coroutine)


class Sideload:
    pass


class AsyncRuntimeError(Exception):
    pass


class ElisAPIClientSync(
    typing.Generic[
        AnnotationType,
        ConnectorType,
        DocumentType,
        EmailTemplateType,
        EngineType,
        EngineFieldType,
        GroupType,
        HookType,
        InboxType,
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
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        http_client: Optional[APIClient] = None,
        deserializer: Optional[Deserializer] = None,
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
            pass a custom response post-processing callable
        """
        self.elis_api_client: ElisAPIClient[
            AnnotationType,
            ConnectorType,
            DocumentType,
            EmailTemplateType,
            EngineType,
            EngineFieldType,
            GroupType,
            HookType,
            InboxType,
            OrganizationType,
            QueueType,
            SchemaType,
            TaskType,
            UploadType,
            UserType,
            WorkspaceType,
        ] = ElisAPIClient(
            username, password, token, base_url, http_client, deserializer, response_post_processor
        )
        # The executor is never terminated. We would either need to turn the client into a context manager which is inconvenient for users or terminate it after each request which is wasteful. Keeping one thread around seems like the lesser evil.
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _iter_over_async(self, ait: AsyncIterator[T]) -> Iterator[T]:
        """Iterate over an async generator from sync code without materializing all items into memory."""
        queue: ThreadSafeQueue = (
            ThreadSafeQueue()
        )  # To communicate with the thread executing the async generator

        async def async_iter_to_list(ait: AsyncIterator[T], queue: ThreadSafeQueue):
            try:
                async for obj in ait:
                    queue.put(obj)
            finally:
                queue.put(None)  # Signal iterator was consumed

        future = self.executor.submit(run_coroutine_in_thread, async_iter_to_list(ait, queue))  # type: ignore

        # Consume the queue until completion to retain the iterator nature even in sync context
        while True:
            item = queue.get()
            if item is None:  # None is used to signal completion
                break
            yield item

        future.result()

    def _run_coroutine(self, coroutine):
        future = self.executor.submit(run_coroutine_in_thread, coroutine)
        return future.result()

    # ##### QUEUE #####
    def retrieve_queue(self, queue_id: int) -> QueueType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        return self._run_coroutine(self.elis_api_client.retrieve_queue(queue_id))

    def list_all_queues(self, ordering: Sequence[str] = (), **filters: Any) -> Iterator[QueueType]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        return self._iter_over_async(self.elis_api_client.list_all_queues(ordering, **filters))

    def create_new_queue(self, data: Dict[str, Any]) -> QueueType:
        """https://elis.rossum.ai/api/docs/#create-new-queue."""
        return self._run_coroutine(self.elis_api_client.create_new_queue(data))

    def delete_queue(self, queue_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue."""
        return self._run_coroutine(self.elis_api_client.delete_queue(queue_id))

    def import_document(
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
        return self._run_coroutine(
            self.elis_api_client.import_document(queue_id, files, values, metadata)
        )

    # ##### UPLOAD #####
    def upload_document(
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
        return self._run_coroutine(
            self.elis_api_client.upload_document(queue_id, files, values, metadata)
        )

    def retrieve_upload(self, upload_id: int) -> UploadType:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-upload."""

        return self._run_coroutine(self.elis_api_client.retrieve_upload(upload_id))

    def export_annotations_to_json(
        self, queue_id: int, **filters: Any
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        return self._iter_over_async(
            self.elis_api_client.export_annotations_to_json(queue_id, **filters)
        )

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats, **filters: Any
    ) -> Iterator[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        return self._iter_over_async(
            self.elis_api_client.export_annotations_to_file(queue_id, export_format, **filters)
        )

    # ##### ORGANIZATIONS #####
    def list_all_organizations(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[OrganizationType]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        return self._iter_over_async(
            self.elis_api_client.list_all_organizations(ordering, **filters)
        )

    def retrieve_organization(
        self,
        org_id: int,
    ) -> OrganizationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        return self._run_coroutine(self.elis_api_client.retrieve_organization(org_id))

    def retrieve_own_organization(self) -> OrganizationType:
        """Retrieve organization of currently logged in user."""
        return self._run_coroutine(self.elis_api_client.retrieve_own_organization())

    # ##### SCHEMAS #####
    def list_all_schemas(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[SchemaType]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        return self._iter_over_async(self.elis_api_client.list_all_schemas(ordering, **filters))

    def retrieve_schema(self, schema_id: int) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        return self._run_coroutine(self.elis_api_client.retrieve_schema(schema_id))

    def create_new_schema(self, data: Dict[str, Any]) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        return self._run_coroutine(self.elis_api_client.create_new_schema(data))

    def delete_schema(self, schema_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return self._run_coroutine(self.elis_api_client.delete_schema(schema_id))

    # ##### ENGINES #####
    def retrieve_engine(self, engine_id: int) -> EngineType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        return self._run_coroutine(self.elis_api_client.retrieve_engine(engine_id))

    def list_all_engines(
        self, ordering: Sequence[str] = (), sideloads: Sequence[str] = (), **filters: Any
    ) -> Iterator[EngineType]:
        """https://elis.rossum.ai/api/docs/internal/#list-all-engines."""
        return self._iter_over_async(
            self.elis_api_client.list_all_engines(ordering, sideloads, **filters)
        )

    def retrieve_engine_fields(self, engine_id: int | None = None) -> Iterator[EngineFieldType]:
        """https://elis.rossum.ai/api/docs/internal/#engine-field."""
        return self._iter_over_async(self.elis_api_client.retrieve_engine_fields(engine_id))

    def retrieve_engine_queues(self, engine_id: int) -> Iterator[QueueType]:
        """https://elis.rossum.ai/api/docs/internal/#list-all-queues."""
        return self._iter_over_async(self.elis_api_client.retrieve_engine_queues(engine_id))

    # ##### USERS #####
    def list_all_users(self, ordering: Sequence[str] = (), **filters: Any) -> Iterator[UserType]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        return self._iter_over_async(self.elis_api_client.list_all_users(ordering, **filters))

    def retrieve_user(self, user_id: int) -> UserType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        return self._run_coroutine(self.elis_api_client.retrieve_user(user_id))

    def create_new_user(self, data: Dict[str, Any]) -> UserType:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        return self._run_coroutine(self.elis_api_client.create_new_user(data))

    # TODO: specific method in APICLient
    def change_user_password(self, new_password: str) -> dict:
        return {}

    # TODO: specific method in APICLient
    def reset_user_password(self, email: str) -> dict:
        return {}

    # ##### ANNOTATIONS #####
    def list_all_annotations(
        self,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        content_schema_ids: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations."""
        return self._iter_over_async(
            self.elis_api_client.list_all_annotations(
                ordering, sideloads, content_schema_ids, **filters
            )
        )

    def search_for_annotations(
        self,
        query: Optional[dict] = None,
        query_string: Optional[dict] = None,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        **kwargs: Any,
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/internal/#search-for-annotations."""
        return self._iter_over_async(
            self.elis_api_client.search_for_annotations(
                query, query_string, ordering, sideloads, **kwargs
            )
        )

    def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[str] = ()
    ) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        return self._run_coroutine(
            self.elis_api_client.retrieve_annotation(annotation_id, sideloads)
        )

    def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[AnnotationType], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> AnnotationType:
        """Poll on Annotation until predicate is true.

        Sideloading is done only once after the predicate becomes true to avoid spamming the server.
        """
        return self._run_coroutine(
            self.elis_api_client.poll_annotation(annotation_id, predicate, sleep_s, sideloads)
        )

    def poll_task(
        self, task_id: int, predicate: Callable[[TaskType], bool], sleep_s: int = 3
    ) -> TaskType:
        """Poll on Task until predicate is true."""
        return self._run_coroutine(self.elis_api_client.poll_task(task_id, predicate, sleep_s))

    def poll_task_until_succeeded(self, task_id: int, sleep_s: int = 3) -> TaskType:
        """Poll on Task until it is succeeded."""
        return self._run_coroutine(
            self.elis_api_client.poll_task_until_succeeded(task_id, sleep_s)
        )

    def retrieve_task(self, task_id: int) -> TaskType:
        """https://elis.rossum.ai/api/docs/#retrieve-task."""
        return self._run_coroutine(self.elis_api_client.retrieve_task(task_id))

    def poll_annotation_until_imported(
        self, annotation_id: int, **poll_kwargs: Any
    ) -> AnnotationType:
        """A shortcut for waiting until annotation is imported."""
        return self._run_coroutine(
            self.elis_api_client.poll_annotation_until_imported(annotation_id, **poll_kwargs)
        )

    def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> AnnotationType:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        return self._run_coroutine(
            self.elis_api_client.upload_and_wait_until_imported(
                queue_id, filepath, filename, **poll_kwargs
            )
        )

    def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        self._run_coroutine(self.elis_api_client.start_annotation(annotation_id))

    def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        return self._run_coroutine(self.elis_api_client.update_annotation(annotation_id, data))

    def update_part_annotation(self, annotation_id: int, data: Dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        return self._run_coroutine(
            self.elis_api_client.update_part_annotation(annotation_id, data)
        )

    def bulk_update_annotation_data(
        self, annotation_id: int, operations: List[Dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""
        self._run_coroutine(
            self.elis_api_client.bulk_update_annotation_data(annotation_id, operations)
        )

    def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        self._run_coroutine(self.elis_api_client.confirm_annotation(annotation_id))

    def create_new_annotation(self, data: dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        return self._run_coroutine(self.elis_api_client.create_new_annotation(data))

    def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        return self._run_coroutine(self.elis_api_client.delete_annotation(annotation_id))

    def cancel_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#cancel-annotation"""
        return self._run_coroutine(self.elis_api_client.cancel_annotation(annotation_id))

    # ##### DOCUMENTS #####
    def retrieve_document(self, document_id: int) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document"""
        return self._run_coroutine(self.elis_api_client.retrieve_document(document_id))

    def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        return self._run_coroutine(self.elis_api_client.retrieve_document_content(document_id))

    def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#create-document"""
        return self._run_coroutine(
            self.elis_api_client.create_new_document(file_name, file_data, metadata, parent)
        )

    # ##### WORKSPACES #####
    def list_all_workspaces(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[WorkspaceType]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        return self._iter_over_async(self.elis_api_client.list_all_workspaces(ordering, **filters))

    def retrieve_workspace(self, workspace_id: int) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        return self._run_coroutine(self.elis_api_client.retrieve_workspace(workspace_id))

    def create_new_workspace(self, data: Dict[str, Any]) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        return self._run_coroutine(self.elis_api_client.create_new_workspace(data))

    def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        return self._run_coroutine(self.elis_api_client.delete_workspace(workspace_id))

    # ##### INBOX #####
    def create_new_inbox(self, data: Dict[str, Any]) -> InboxType:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        return self._run_coroutine(self.elis_api_client.create_new_inbox(data))

    # ##### EMAIL TEMPLATES #####
    def list_all_email_templates(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[ConnectorType]:
        """https://elis.rossum.ai/api/docs/#list-all-email-templates."""
        return self._iter_over_async(
            self.elis_api_client.list_all_email_templates(ordering, **filters)
        )

    def retrieve_email_template(self, email_template_id: int) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object."""
        return self._run_coroutine(self.elis_api_client.retrieve_email_template(email_template_id))

    def create_new_email_template(self, data: Dict[str, Any]) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#create-new-email-template-object."""
        return self._run_coroutine(self.elis_api_client.create_new_email_template(data))

    # ##### CONNECTORS #####
    def list_all_connectors(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[ConnectorType]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        return self._iter_over_async(self.elis_api_client.list_all_connectors(ordering, **filters))

    def retrieve_connector(self, connector_id: int) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        return self._run_coroutine(self.elis_api_client.retrieve_connector(connector_id))

    def create_new_connector(self, data: Dict[str, Any]) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        return self._run_coroutine(self.elis_api_client.create_new_connector(data))

    # ##### HOOKS #####
    def list_all_hooks(self, ordering: Sequence[str] = (), **filters: Any) -> Iterator[HookType]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        return self._iter_over_async(self.elis_api_client.list_all_hooks(ordering, **filters))

    def retrieve_hook(self, hook_id: int) -> HookType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        return self._run_coroutine(self.elis_api_client.retrieve_hook(hook_id))

    def create_new_hook(self, data: Dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        return self._run_coroutine(self.elis_api_client.create_new_hook(data))

    def update_part_hook(self, hook_id: int, data: Dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-hook"""
        return self._run_coroutine(self.elis_api_client.update_part_hook(hook_id, data))

    def delete_hook(self, hook_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-hook"""
        return self._run_coroutine(self.elis_api_client.delete_hook(hook_id))

    # ##### USER ROLES #####
    def list_all_user_roles(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[GroupType]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        return self._iter_over_async(self.elis_api_client.list_all_user_roles(ordering, **filters))

    def request_paginated(self, url: str, *args, **kwargs) -> Iterator[dict]:
        """Use to perform requests to seldomly used or experimental endpoints with paginated response that do not have
        direct support in the client and return Iterator.
        """
        return self._iter_over_async(self.elis_api_client.request_paginated(url, *args, **kwargs))

    def request_json(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return JSON.
        """
        return self._run_coroutine(self.elis_api_client.request_json(method, *args, **kwargs))

    def request(self, method: str, *args, **kwargs) -> httpx.Response:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return the raw response.
        """
        return self._run_coroutine(self.elis_api_client.request(method, *args, **kwargs))

    def get_token(self, refresh: bool = False) -> str:
        """Returns the current token. Authentication is done automatically if needed.

        Parameters
        ----------
        refresh
            force refreshing the token
        """
        return self._run_coroutine(self.elis_api_client.get_token(refresh))


# Type alias for an ElisAPIClientSync that uses the default deserializer
ElisAPIClientSyncWithDefaultSerializer = ElisAPIClientSync[
    Annotation,
    Connector,
    Document,
    EmailTemplate,
    Engine,
    EngineField,
    Group,
    Hook,
    Inbox,
    Organization,
    Queue,
    Schema,
    Task,
    Upload,
    User,
    Workspace,
]
