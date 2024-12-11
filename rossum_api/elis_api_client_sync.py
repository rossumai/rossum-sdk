from __future__ import annotations

import pathlib
import time
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Sequence, Tuple, Union, cast

from rossum_api import ExportFileFormats
from rossum_api.api_client import Resource
from rossum_api.domain_logic.annotations import (
    get_http_method_for_annotation_export,
    is_annotation_imported,
    validate_list_annotations_params,
)
from rossum_api.domain_logic.documents import build_create_document_params
from rossum_api.domain_logic.search import build_search_params, validate_search_params
from rossum_api.domain_logic.upload import build_upload_files
from rossum_api.domain_logic.urls import build_upload_url, parse_resource_id_from_url
from rossum_api.dtos import Token, UserCredentials
from rossum_api.internal_sync_client import InternalSyncRossumAPIClient
from rossum_api.models import (
    Annotation,
    Connector,
    Deserializer,
    Document,
    EmailTemplate,
    Engine,
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
    deserialize_default,
)
from rossum_api.models.task import TaskStatus


class ElisAPIClientSync:
    def __init__(
        self,
        base_url: str,
        credentials: UserCredentials | Token,
        deserializer: Optional[Deserializer] = None,
    ):
        self._deserializer = deserializer or deserialize_default
        self.internal_client = InternalSyncRossumAPIClient(base_url, credentials)

    # ##### QUEUES #####

    def retrieve_queue(
        self,
        queue_id: int,
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        queue = self.internal_client.fetch_resource(Resource.Queue, queue_id)
        return self._deserializer(Resource.Queue, queue)

    def list_queues(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Queue]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        for q in self.internal_client.fetch_resources(Resource.Queue, ordering, **filters):
            yield self._deserializer(Resource.Queue, q)

    def create_new_queue(self, data: dict[str, Any]) -> Queue:
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
    ) -> list[Task]:
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
    ) -> Upload:
        """Implements https://elis.rossum.ai/api/docs/#retrieve-upload."""
        upload = self.internal_client.fetch_resource(Resource.Upload, upload_id)
        return self._deserializer(Resource.Upload, upload)

    # ##### EXPORT #####

    def export_annotations_to_json(
        self,
        queue_id: int,
    ) -> Iterator[Annotation]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        for chunk in self.internal_client.export(
            Resource.Queue, queue_id, "json", get_http_method_for_annotation_export()
        ):
            # JSON export can be translated directly to Annotation object
            yield self._deserializer(Resource.Annotation, cast(dict, chunk))

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats
    ) -> Iterator[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        for chunk in self.internal_client.export(
            Resource.Queue, queue_id, str(export_format), get_http_method_for_annotation_export()
        ):
            yield cast(bytes, chunk)

    # ##### ORGANIZATIONS #####

    def list_organizations(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Organization]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        for o in self.internal_client.fetch_resources(Resource.Organization, ordering, **filters):
            yield self._deserializer(Resource.Organization, o)

    def retrieve_organization(self, org_id: int) -> Organization:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        organization = self.internal_client.fetch_resource(Resource.Organization, org_id)
        return self._deserializer(Resource.Organization, organization)

    def retrieve_my_organization(self) -> Organization:
        """Retrieve organization of currently logged in user."""
        user: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Auth, "user")
        organization_id = parse_resource_id_from_url(user["organization"])
        return self.retrieve_organization(organization_id)

    # ##### SCHEMAS #####

    def list_schemas(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Schema]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        for s in self.internal_client.fetch_resources(Resource.Schema, ordering, **filters):
            yield self._deserializer(Resource.Schema, s)

    def retrieve_schema(self, schema_id: int) -> Schema:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        schema: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Schema, schema_id)
        return self._deserializer(Resource.Schema, schema)

    def create_new_schema(self, data: dict[str, Any]) -> Schema:
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
    ) -> Iterator[User]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        for u in self.internal_client.fetch_resources(Resource.User, ordering, **filters):
            yield self._deserializer(Resource.User, u)

    def retrieve_user(self, user_id: int) -> User:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        user = self.internal_client.fetch_resource(Resource.User, user_id)
        return self._deserializer(Resource.User, user)

    # TODO: specific method in InternalSyncRossumAPIClient
    def change_user_password(self, new_password: str) -> dict:
        raise NotImplementedError

    # TODO: specific method in InternalSyncRossumAPIClient
    def reset_user_password(self, email: str) -> dict:
        raise NotImplementedError

    def create_new_user(self, data: dict[str, Any]) -> User:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        user = self.internal_client.create(Resource.User, data)
        return self._deserializer(Resource.User, user)

    # ##### ANNOTATIONS #####

    def retrieve_annotation(self, annotation_id: int, sideloads: Sequence[str] = ()) -> Annotation:
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
    ) -> Iterator[Annotation]:
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
    ) -> Iterator[Annotation]:
        """https://elis.rossum.ai/api/docs/#search-for-annotations."""
        validate_search_params(query, query_string)
        json_payload = build_search_params(query, query_string)
        for annotation in self.internal_client.fetch_resources_by_url(
            f"{Resource.Annotation.value}/search",
            ordering,
            sideloads,
            json=json_payload,
            method="POST",
            **kwargs,
        ):
            yield self._deserializer(Resource.Annotation, annotation)

    def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[Annotation], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> Annotation:
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

    def poll_annotation_until_imported(self, annotation_id: int, **poll_kwargs: Any) -> Annotation:
        """A shortcut for waiting until annotation is imported."""
        return self.poll_annotation(annotation_id, is_annotation_imported, **poll_kwargs)

    # ##### TASKS #####

    def retrieve_task(self, task_id: int) -> Task:
        """https://elis.rossum.ai/api/docs/#retrieve-task."""
        task = self.internal_client.fetch_resource(
            Resource.Task, task_id, request_params={"no_redirect": "True"}
        )
        return self._deserializer(Resource.Task, task)

    def poll_task(
        self,
        task_id: int,
        predicate: Callable[[Task], bool],
        sleep_s: int = 3,
    ) -> Task:
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
    ) -> Task:
        """Poll on Task until it is succeeded."""
        return self.poll_task(task_id, lambda a: a.status == TaskStatus.SUCCEEDED, sleep_s)

    def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> Annotation:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        (annotation_id,) = self.import_document(queue_id, [(filepath, filename)])
        return self.poll_annotation_until_imported(annotation_id, **poll_kwargs)

    def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        self.internal_client.request_json(
            "POST", f"{Resource.Annotation.value}/{annotation_id}/start"
        )

    def update_annotation(self, annotation_id: int, data: dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        annotation = self.internal_client.replace(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def update_part_annotation(self, annotation_id: int, data: dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        annotation = self.internal_client.update(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def bulk_update_annotation_data(
        self, annotation_id: int, operations: list[dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""

        self.internal_client.request_json(
            "POST",
            f"{Resource.Annotation.value}/{annotation_id}/content/operations",
            json={"operations": operations},
        )

    def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        self.internal_client.request_json(
            "POST", f"{Resource.Annotation.value}/{annotation_id}/confirm"
        )

    def create_new_annotation(self, data: dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        annotation = self.internal_client.create(Resource.Annotation, data)
        return self._deserializer(Resource.Annotation, annotation)

    def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        self.internal_client.request(
            "POST", url=f"{Resource.Annotation.value}/{annotation_id}/delete"
        )

    def cancel_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#cancel-annotation"""
        self.internal_client.request(
            "POST", url=f"{Resource.Annotation.value}/{annotation_id}/cancel"
        )

    # ##### DOCUMENTS #####

    def retrieve_document(self, document_id: int) -> Document:
        """https://elis.rossum.ai/api/docs/#retrieve-a-document"""
        document: dict[Any, Any] = self.internal_client.fetch_resource(
            Resource.Document, document_id
        )
        return self._deserializer(Resource.Document, document)

    def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        document_content = self.internal_client.request(
            "GET", url=f"{Resource.Document.value}/{document_id}/content"
        )
        return document_content.content

    def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> Document:
        """https://elis.rossum.ai/api/docs/#create-document"""
        files = build_create_document_params(file_name, file_data, metadata, parent)
        document = self.internal_client.request_json(
            "POST", url=Resource.Document.value, files=files
        )
        return self._deserializer(Resource.Document, document)

    # ##### WORKSPACES #####

    def list_workspaces(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Workspace]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        for w in self.internal_client.fetch_resources(Resource.Workspace, ordering, **filters):
            yield self._deserializer(Resource.Workspace, w)

    def retrieve_workspace(self, workspace_id: int) -> Workspace:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        workspace = self.internal_client.fetch_resource(Resource.Workspace, workspace_id)

        return self._deserializer(Resource.Workspace, workspace)

    def create_new_workspace(self, data: dict[str, Any]) -> Workspace:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        workspace = self.internal_client.create(Resource.Workspace, data)

        return self._deserializer(Resource.Workspace, workspace)

    def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-workspace."""
        return self.internal_client.delete(Resource.Workspace, workspace_id)

    # ##### ENGINE #####

    def retrieve_engine(self, engine_id: int) -> Engine:
        """https://elis.rossum.ai/api/docs/#retrieve-an-engine."""
        engine = self.internal_client.fetch_resource(Resource.Engine, engine_id)
        return self._deserializer(Resource.Engine, engine)

    # ##### INBOX #####

    def create_new_inbox(self, data: dict[str, Any]) -> Inbox:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        inbox = self.internal_client.create(Resource.Inbox, data)
        return self._deserializer(Resource.Inbox, inbox)

    # ##### EMAIL TEMPLATES #####

    def list_email_templates(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[EmailTemplate]:
        """https://elis.rossum.ai/api/docs/#list-all-email-templates."""
        for c in self.internal_client.fetch_resources(Resource.EmailTemplate, ordering, **filters):
            yield self._deserializer(Resource.EmailTemplate, c)

    def retrieve_email_template(self, email_template_id: int) -> EmailTemplate:
        """https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object."""
        email_template = self.internal_client.fetch_resource(
            Resource.EmailTemplate, email_template_id
        )
        return self._deserializer(Resource.EmailTemplate, email_template)

    def create_new_email_template(self, data: dict[str, Any]) -> EmailTemplate:
        """https://elis.rossum.ai/api/docs/#create-new-email-template-object."""
        email_template = self.internal_client.create(Resource.EmailTemplate, data)
        return self._deserializer(Resource.EmailTemplate, email_template)

    # ##### CONNECTORS #####

    def list_connectors(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        for c in self.internal_client.fetch_resources(Resource.Connector, ordering, **filters):
            yield self._deserializer(Resource.Connector, c)

    def retrieve_connector(self, connector_id: int) -> Connector:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        connector = self.internal_client.fetch_resource(Resource.Connector, connector_id)
        return self._deserializer(Resource.Connector, connector)

    def create_new_connector(self, data: dict[str, Any]) -> Connector:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        connector = self.internal_client.create(Resource.Connector, data)
        return self._deserializer(Resource.Connector, connector)

    # ##### HOOKS #####

    def list_hooks(
        self,
        ordering: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[Hook]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        for h in self.internal_client.fetch_resources(Resource.Hook, ordering, **filters):
            yield self._deserializer(Resource.Hook, h)

    def retrieve_hook(self, hook_id: int) -> Hook:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        hook = self.internal_client.fetch_resource(Resource.Hook, hook_id)
        return self._deserializer(Resource.Hook, hook)

    def create_new_hook(self, data: dict[str, Any]) -> Hook:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        hook = self.internal_client.create(Resource.Hook, data)
        return self._deserializer(Resource.Hook, hook)

    def update_part_hook(self, hook_id: int, data: dict[str, Any]) -> Hook:
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
    ) -> Iterator[Group]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        for g in self.internal_client.fetch_resources(Resource.Group, ordering, **filters):
            yield self._deserializer(Resource.Group, g)
