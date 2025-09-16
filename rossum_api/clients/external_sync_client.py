from __future__ import annotations

import pathlib
import time
import typing
from pathlib import Path

from rossum_api.clients.internal_sync_client import InternalSyncClient
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
from rossum_api.domain_logic.upload import build_upload_files
from rossum_api.domain_logic.urls import (
    EMAIL_IMPORT_URL,
    build_resource_cancel_url,
    build_resource_confirm_url,
    build_resource_content_operations_url,
    build_resource_content_url,
    build_resource_delete_url,
    build_resource_search_url,
    build_resource_start_url,
    build_upload_url,
    parse_resource_id_from_url,
)
from rossum_api.dtos import Token, UserCredentials
from rossum_api.models import (
    Annotation,
    Connector,
    Document,
    DocumentRelation,
    Email,
    EmailTemplate,
    Engine,
    EngineField,
    Group,
    Hook,
    Inbox,
    Organization,
    Queue,
    Schema,
    Upload,
    User,
    Workspace,
    deserialize_default,
)
from rossum_api.models.task import Task
from rossum_api.utils import ObjectWithStatus

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Iterator, Optional, Sequence, Tuple, Union

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


class SyncRossumAPIClient(
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
        self._deserializer = deserializer or deserialize_default
        self.internal_client = InternalSyncClient(
            base_url,
            credentials,
            timeout=timeout,
            n_retries=n_retries,
            response_post_processor=response_post_processor,
        )

    # ##### QUEUES #####

    def retrieve_queue(
        self,
        queue_id: int,
    ) -> QueueType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        queue = self.internal_client.fetch_resource(Resource.Queue, queue_id)
        return self._deserializer(Resource.Queue, queue)

    def list_queues(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[QueueType]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        for q in self.internal_client.fetch_resources(Resource.Queue, ordering, **filters):
            yield self._deserializer(Resource.Queue, q)

    def create_new_queue(self, data: dict[str, Any]) -> QueueType:
        """https://elis.rossum.ai/api/docs/#create-new-queue."""
        queue = self.internal_client.create(Resource.Queue, data)
        return self._deserializer(Resource.Queue, queue)

    def delete_queue(self, queue_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue."""
        return self.internal_client.delete(Resource.Queue, queue_id)

    def _import_document(
        self,
        url: str,
        files: Sequence[Tuple[Union[str, Path], str]],
        values: Optional[dict[str, Any]],
        metadata: Optional[dict[str, Any]],
    ) -> list[int]:
        """Depending on the endpoint, it either returns annotation IDs, or task IDs."""
        results = []
        for file_path, filename in files:
            with open(file_path, "rb") as fp:
                request_files = build_upload_files(fp.read(), filename, values, metadata)
                response_data = self.internal_client.upload(url, request_files)
                (result,) = response_data[
                    "results"
                ]  # We're uploading 1 file in 1 request, we can unpack
                results.append(parse_resource_id_from_url(result["annotation"]))
        return results

    def import_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, Path], str]],
        values: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[int]:
        """https://elis.rossum.ai/api/docs/#import-a-document.

        Deprecated now, consider upload_document.

        Parameters
        ---------
        queue_id
            ID of the queue to upload the files to
        files
            2-tuple containing current filepath and name to be used by Elis for the uploaded file
        values
            may be used to initialize datapoint values by setting the value of rir_field_names in the schema
        metadata
            will be set to newly created annotation object

        Returns
        -------
        annotation_ids
            list of IDs of created annotations, respects the order of `files` argument
        """
        url = build_upload_url(Resource.Queue, queue_id)
        return self._import_document(url, files, values, metadata)

    # ##### UPLOAD #####

    def upload_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[TaskType]:
        """https://elis.rossum.ai/api/docs/#create-upload

        Does the same thing as import_document method, but uses a different endpoint.

        Parameters
        ---------
        queue_id
            ID of the queue to upload the files to
        files
            2-tuple containing current filepath and name to be used by Elis for the uploaded file
        values
            may be used to initialize datapoint values by setting the value of rir_field_names in the schema
        metadata
            will be set to newly created annotation object

        Returns
        -------
        task_responses
            list of Task object responses, respects the order of `files` argument
            Tasks can be polled using poll_task and if succeeded, will contain a
            link to an Upload object that contains info on uploaded documents/annotations
        """
        url = f"uploads?queue={queue_id}"
        task_ids = self._import_document(url, files, values, metadata)
        return [self.retrieve_task(task_id) for task_id in task_ids]

    def retrieve_upload(
        self,
        upload_id: int,
    ) -> UploadType:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-upload."""
        upload = self.internal_client.fetch_resource(Resource.Upload, upload_id)
        return self._deserializer(Resource.Upload, upload)

    # ##### EXPORT #####

    def export_annotations_to_json(
        self,
        queue_id: int,
        **filters: Any,
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        for chunk in self.internal_client.export(Resource.Queue, queue_id, "json", **filters):
            # JSON export can be translated directly to Annotation object
            yield self._deserializer(Resource.Annotation, typing.cast(dict, chunk))

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats, **filters
    ) -> Iterator[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        for chunk in self.internal_client.export(
            Resource.Queue,
            queue_id,
            export_format.value,
            **filters,
        ):
            yield typing.cast(bytes, chunk)

    # ##### ORGANIZATIONS #####

    def list_organizations(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[OrganizationType]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        for o in self.internal_client.fetch_resources(Resource.Organization, ordering, **filters):
            yield self._deserializer(Resource.Organization, o)

    def retrieve_organization(self, org_id: int) -> OrganizationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        organization = self.internal_client.fetch_resource(Resource.Organization, org_id)
        return self._deserializer(Resource.Organization, organization)

    def retrieve_my_organization(self) -> OrganizationType:
        """Retrieve organization of currently logged in user."""
        user: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Auth, "user")
        organization_id = parse_resource_id_from_url(user["organization"])
        return self.retrieve_organization(organization_id)

    # ##### SCHEMAS #####

    def list_schemas(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[SchemaType]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        for s in self.internal_client.fetch_resources(Resource.Schema, ordering, **filters):
            yield self._deserializer(Resource.Schema, s)

    def retrieve_schema(self, schema_id: int) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        schema: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Schema, schema_id)
        return self._deserializer(Resource.Schema, schema)

    def create_new_schema(self, data: dict[str, Any]) -> SchemaType:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        schema = self.internal_client.create(Resource.Schema, data)
        return self._deserializer(Resource.Schema, schema)

    def delete_schema(self, schema_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return self.internal_client.delete(Resource.Schema, schema_id)

    # ##### USERS #####

    def list_users(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[UserType]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        for u in self.internal_client.fetch_resources(Resource.User, ordering, **filters):
            yield self._deserializer(Resource.User, u)

    def retrieve_user(self, user_id: int) -> UserType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        user = self.internal_client.fetch_resource(Resource.User, user_id)
        return self._deserializer(Resource.User, user)

    # TODO: specific method in InternalSyncRossumAPIClient
    def change_user_password(self, new_password: str) -> dict:
        raise NotImplementedError

    # TODO: specific method in InternalSyncRossumAPIClient
    def reset_user_password(self, email: str) -> dict:
        raise NotImplementedError

    def create_new_user(self, data: dict[str, Any]) -> UserType:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        user = self.internal_client.create(Resource.User, data)
        return self._deserializer(Resource.User, user)

    # ##### ANNOTATIONS #####

    def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[str] = ()
    ) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        annotation = self.internal_client.fetch_resource(Resource.Annotation, annotation_id)
        if sideloads:
            self.internal_client.sideload(annotation, sideloads)
        return self._deserializer(Resource.Annotation, annotation)

    def list_annotations(
        self,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        content_schema_ids: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations."""
        validate_list_annotations_params(sideloads, content_schema_ids)

        for annotation in self.internal_client.fetch_resources(
            Resource.Annotation, ordering, sideloads, content_schema_ids, **filters
        ):
            yield self._deserializer(Resource.Annotation, annotation)

    def search_for_annotations(
        self,
        query: Optional[dict] = None,
        query_string: Optional[dict] = None,
        ordering: Sequence[str] = (),
        sideloads: Sequence[str] = (),
        **kwargs: Any,
    ) -> Iterator[AnnotationType]:
        """https://elis.rossum.ai/api/docs/#search-for-annotations."""
        validate_search_params(query, query_string)
        search_params = build_search_params(query, query_string)
        for annotation in self.internal_client.fetch_resources_by_url(
            build_resource_search_url(Resource.Annotation),
            ordering,
            sideloads,
            json=search_params,
            method="POST",
            **kwargs,
        ):
            yield self._deserializer(Resource.Annotation, annotation)

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
        resource = Resource.Annotation

        annotation_response = self.internal_client.fetch_resource(resource, annotation_id)
        # Deserialize early, we want the predicate to work with Annotation instances for convenience.
        annotation = self._deserializer(resource, annotation_response)

        while not predicate(annotation):
            time.sleep(sleep_s)
            annotation_response = self.internal_client.fetch_resource(resource, annotation_id)
            annotation = self._deserializer(resource, annotation_response)

        if sideloads:
            self.internal_client.sideload(annotation_response, sideloads)
        return self._deserializer(resource, annotation_response)

    def poll_annotation_until_imported(
        self, annotation_id: int, **poll_kwargs: Any
    ) -> AnnotationType:
        """A shortcut for waiting until annotation is imported."""
        return self.poll_annotation(annotation_id, is_annotation_imported, **poll_kwargs)

    # ##### TASKS #####

    def retrieve_task(self, task_id: int) -> TaskType:
        """https://elis.rossum.ai/api/docs/#retrieve-task."""
        task = self.internal_client.fetch_resource(
            Resource.Task, task_id, request_params={"no_redirect": "True"}
        )
        return self._deserializer(Resource.Task, task)

    def poll_task(
        self,
        task_id: int,
        predicate: Callable[[TaskType], bool],
        sleep_s: int = 3,
    ) -> TaskType:
        """Poll on Task until predicate is true.

        As with Annotation polling, there is no innate retry limit."""
        task = self.retrieve_task(task_id)

        while not predicate(task):
            time.sleep(sleep_s)
            task = self.retrieve_task(task_id)

        return task

    def poll_task_until_succeeded(
        self,
        task_id: int,
        sleep_s: int = 3,
    ) -> TaskType:
        """Poll on Task until it is succeeded."""
        return self.poll_task(task_id, is_task_succeeded, sleep_s)

    def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> AnnotationType:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        (annotation_id,) = self.import_document(queue_id, [(filepath, filename)])
        return self.poll_annotation_until_imported(annotation_id, **poll_kwargs)

    def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        self.internal_client.request_json(
            "POST", build_resource_start_url(Resource.Annotation, annotation_id)
        )

    def update_annotation(self, annotation_id: int, data: dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        annotation = self.internal_client.replace(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def update_part_annotation(self, annotation_id: int, data: dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        annotation = self.internal_client.update(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def bulk_update_annotation_data(
        self, annotation_id: int, operations: list[dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""

        self.internal_client.request_json(
            "POST",
            build_resource_content_operations_url(Resource.Annotation, annotation_id),
            json={"operations": operations},
        )

    def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        self.internal_client.request_json(
            "POST", build_resource_confirm_url(Resource.Annotation, annotation_id)
        )

    def create_new_annotation(self, data: dict[str, Any]) -> AnnotationType:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        annotation = self.internal_client.create(Resource.Annotation, data)
        return self._deserializer(Resource.Annotation, annotation)

    def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        self.internal_client.request(
            "POST", url=build_resource_delete_url(Resource.Annotation, annotation_id)
        )

    def cancel_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#cancel-annotation"""
        self.internal_client.request(
            "POST", url=build_resource_cancel_url(Resource.Annotation, annotation_id)
        )

    # ##### DOCUMENTS #####

    def retrieve_document(self, document_id: int) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document"""
        document: dict[Any, Any] = self.internal_client.fetch_resource(
            Resource.Document, document_id
        )
        return self._deserializer(Resource.Document, document)

    def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        document_content = self.internal_client.request(
            "GET", url=build_resource_content_url(Resource.Document, document_id)
        )
        return document_content.content

    def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> DocumentType:
        """https://elis.rossum.ai/api/docs/#create-document"""
        files = build_create_document_params(file_name, file_data, metadata, parent)
        document = self.internal_client.request_json(
            "POST", url=Resource.Document.value, files=files
        )
        return self._deserializer(Resource.Document, document)

    # ##### DOCUMENT RELATIONS #####

    def list_document_relations(
        self, ordering: Sequence[str] = (), **filters: Any
    ) -> Iterator[DocumentRelationType]:
        """https://elis.rossum.ai/api/docs/#list-all-document-relations"""
        for dr in self.internal_client.fetch_resources(
            Resource.DocumentRelation, ordering, **filters
        ):
            yield self._deserializer(Resource.DocumentRelation, dr)

    def retrieve_document_relation(self, document_relation_id: int) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document-relation"""
        document_relation = self.internal_client.fetch_resource(
            Resource.DocumentRelation, document_relation_id
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def create_new_document_relation(self, data: dict[str, Any]) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#create-a-new-document-relation"""
        document_relation = self.internal_client.create(Resource.DocumentRelation, data)

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def update_document_relation(
        self, document_relation_id: int, data: dict[str, Any]
    ) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#update-a-document-relation"""
        document_relation = self.internal_client.replace(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def update_part_document_relation(
        self, document_relation_id: int, data: dict[str, Any]
    ) -> DocumentRelationType:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-document-relation"""
        document_relation = self.internal_client.update(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def delete_document_relation(self, document_relation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-document-relation"""
        self.internal_client.delete(Resource.DocumentRelation, document_relation_id)

    # ##### WORKSPACES #####

    def list_workspaces(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[WorkspaceType]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        for w in self.internal_client.fetch_resources(Resource.Workspace, ordering, **filters):
            yield self._deserializer(Resource.Workspace, w)

    def retrieve_workspace(self, workspace_id: int) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        workspace = self.internal_client.fetch_resource(Resource.Workspace, workspace_id)

        return self._deserializer(Resource.Workspace, workspace)

    def create_new_workspace(self, data: dict[str, Any]) -> WorkspaceType:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        workspace = self.internal_client.create(Resource.Workspace, data)

        return self._deserializer(Resource.Workspace, workspace)

    def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-workspace."""
        return self.internal_client.delete(Resource.Workspace, workspace_id)

    # ##### ENGINE #####

    def retrieve_engine(self, engine_id: int) -> EngineType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-engine."""
        engine = self.internal_client.fetch_resource(Resource.Engine, engine_id)
        return self._deserializer(Resource.Engine, engine)

    def list_engines(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[EngineType]:
        for c in self.internal_client.fetch_resources(Resource.Engine, ordering, **filters):
            yield self._deserializer(Resource.Engine, c)

    def retrieve_engine_fields(self, engine_id: int | None = None) -> Iterator[EngineFieldType]:
        """https://elis.rossum.ai/api/docs/internal/#engine-field."""
        for engine_field in self.internal_client.fetch_resources(
            Resource.EngineField, engine=engine_id
        ):
            yield self._deserializer(Resource.EngineField, engine_field)

    def retrieve_engine_queues(self, engine_id: int) -> Iterator[QueueType]:
        """https://elis.rossum.ai/api/docs/internal/#list-all-queues."""
        for queue in self.internal_client.fetch_resources(Resource.Queue, engine=engine_id):
            yield self._deserializer(Resource.Queue, queue)

    # ##### INBOX #####

    def create_new_inbox(self, data: dict[str, Any]) -> InboxType:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        inbox = self.internal_client.create(Resource.Inbox, data)
        return self._deserializer(Resource.Inbox, inbox)

    # ##### EMAILS #####
    def retrieve_email(self, email_id: int) -> EmailType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email."""
        email = self.internal_client.fetch_resource(Resource.Email, email_id)

        return self._deserializer(Resource.Email, email)

    def import_email(
        self, raw_message: bytes, recipient: str, mime_type: str | None = None
    ) -> str:
        """https://elis.rossum.ai/api/docs/#import-email.

        Returns task URL.
        """
        response = self.internal_client.request_json(
            "POST",
            url=EMAIL_IMPORT_URL,
            files=build_email_import_files(raw_message, recipient, mime_type),
        )
        return response["url"]

    # ##### EMAIL TEMPLATES #####

    def list_email_templates(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[EmailTemplateType]:
        """https://elis.rossum.ai/api/docs/#list-all-email-templates."""
        for c in self.internal_client.fetch_resources(Resource.EmailTemplate, ordering, **filters):
            yield self._deserializer(Resource.EmailTemplate, c)

    def retrieve_email_template(self, email_template_id: int) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object."""
        email_template = self.internal_client.fetch_resource(
            Resource.EmailTemplate, email_template_id
        )
        return self._deserializer(Resource.EmailTemplate, email_template)

    def create_new_email_template(self, data: dict[str, Any]) -> EmailTemplateType:
        """https://elis.rossum.ai/api/docs/#create-new-email-template-object."""
        email_template = self.internal_client.create(Resource.EmailTemplate, data)
        return self._deserializer(Resource.EmailTemplate, email_template)

    # ##### CONNECTORS #####

    def list_connectors(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[ConnectorType]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        for c in self.internal_client.fetch_resources(Resource.Connector, ordering, **filters):
            yield self._deserializer(Resource.Connector, c)

    def retrieve_connector(self, connector_id: int) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        connector = self.internal_client.fetch_resource(Resource.Connector, connector_id)
        return self._deserializer(Resource.Connector, connector)

    def create_new_connector(self, data: dict[str, Any]) -> ConnectorType:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        connector = self.internal_client.create(Resource.Connector, data)
        return self._deserializer(Resource.Connector, connector)

    # ##### HOOKS #####

    def list_hooks(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[HookType]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        for h in self.internal_client.fetch_resources(Resource.Hook, ordering, **filters):
            yield self._deserializer(Resource.Hook, h)

    def retrieve_hook(self, hook_id: int) -> HookType:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        hook = self.internal_client.fetch_resource(Resource.Hook, hook_id)
        return self._deserializer(Resource.Hook, hook)

    def create_new_hook(self, data: dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        hook = self.internal_client.create(Resource.Hook, data)
        return self._deserializer(Resource.Hook, hook)

    def update_part_hook(self, hook_id: int, data: dict[str, Any]) -> HookType:
        """https://elis.rossum.ai/api/docs/#update-part-of-a-hook"""
        hook = self.internal_client.update(Resource.Hook, hook_id, data)
        return self._deserializer(Resource.Hook, hook)

    def delete_hook(self, hook_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-hook"""
        return self.internal_client.delete(Resource.Hook, hook_id)

    # ##### USER ROLES #####

    def list_user_roles(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[GroupType]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        for g in self.internal_client.fetch_resources(Resource.Group, ordering, **filters):
            yield self._deserializer(Resource.Group, g)

    def authenticate(self) -> None:
        self.internal_client._authenticate()


# Type alias for an SyncRossumAPIClient that uses the default deserializer
SyncRossumAPIClientWithDefaultDeserializer = SyncRossumAPIClient[
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
