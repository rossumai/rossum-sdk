from __future__ import annotations

import time
import warnings
from typing import TYPE_CHECKING, Generic, cast

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
from rossum_api.models import deserialize_default
from rossum_api.models.annotation import Annotation
from rossum_api.models.connector import Connector
from rossum_api.models.document import Document
from rossum_api.models.document_relation import DocumentRelation
from rossum_api.models.email import Email
from rossum_api.models.email_template import EmailTemplate
from rossum_api.models.engine import Engine, EngineField
from rossum_api.models.group import Group
from rossum_api.models.hook import Hook
from rossum_api.models.inbox import Inbox
from rossum_api.models.organization import Organization
from rossum_api.models.queue import Queue
from rossum_api.models.rule import Rule
from rossum_api.models.schema import Schema
from rossum_api.models.task import Task
from rossum_api.models.upload import Upload
from rossum_api.models.user import User
from rossum_api.models.workspace import Workspace
from rossum_api.types import (
    AnnotationType,
    ConnectorType,
    DocumentRelationType,
    DocumentType,
    EmailTemplateType,
    EmailType,
    EngineFieldType,
    EngineType,
    GroupType,
    HookType,
    InboxType,
    OrganizationType,
    QueueType,
    RuleType,
    SchemaType,
    TaskType,
    UploadType,
    UserType,
    WorkspaceType,
)

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable, Iterator, Sequence
    from pathlib import Path
    from typing import Any

    import httpx

    from rossum_api.clients.types import (
        AnnotationOrdering,
        ConnectorOrdering,
        DocumentRelationOrdering,
        EmailTemplateOrdering,
        HookOrdering,
        OrganizationOrdering,
        QueueOrdering,
        RuleOrdering,
        SchemaOrdering,
        UserOrdering,
        UserRoleOrdering,
        WorkspaceOrdering,
    )
    from rossum_api.dtos import Token, UserCredentials
    from rossum_api.models import Deserializer, JsonDict, ResponsePostProcessor
    from rossum_api.types import HttpMethod, RossumApiType, Sideload


class SyncRossumAPIClient(
    Generic[
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
        RuleType,
        SchemaType,
        TaskType,
        UploadType,
        UserType,
        WorkspaceType,
    ]
):
    """Synchronous Rossum API Client.

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

    def __init__(
        self,
        base_url: str,
        credentials: UserCredentials | Token,
        *,
        deserializer: Deserializer | None = None,
        timeout: float | None = None,
        n_retries: int = 3,
        response_post_processor: ResponsePostProcessor | None = None,
    ) -> None:
        self._deserializer: Callable[[Resource, JsonDict], RossumApiType] = (
            deserializer or deserialize_default
        )
        self.internal_client = InternalSyncClient(
            base_url,
            credentials,
            timeout=timeout,
            n_retries=n_retries,
            response_post_processor=response_post_processor,
        )

    # ##### QUEUE #####
    def retrieve_queue(self, queue_id: int) -> QueueType:
        """Retrieve a single :class:`~rossum_api.models.queue.Queue` object.

        Parameters
        ----------
        queue_id
            ID of a queue to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-queue-2.

        https://elis.rossum.ai/api/docs/#queue.
        """
        queue = self.internal_client.fetch_resource(Resource.Queue, queue_id)
        return self._deserializer(Resource.Queue, queue)

    def list_queues(
        self, ordering: Sequence[QueueOrdering] = (), **filters: Any
    ) -> Iterator[QueueType]:
        """Retrieve all queue objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their IDs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.queue.Queue`

            name: Name of a :class:`~rossum_api.models.queue.Queue`

            workspace: ID of a :class:`~rossum_api.models.workspace.Workspace`

            inbox: ID of an :class:`~rossum_api.models.inbox.Inbox`

            connector: ID of an :class:`~rossum_api.models.connector.Connector`

            webhooks: IDs of a :class:`~rossum_api.models.hook.Hooks`

            hooks: IDs of a :class:`~rossum_api.models.hook.Hooks`

            locale: :class:`~rossum_api.models.queue.Queue` object locale.

            dedicated_engine: ID of a `dedicated engine <https://elis.rossum.ai/api/docs/#dedicated-engine>`_.

            generic_engine: ID of a `generic engine <https://elis.rossum.ai/api/docs/#generic-engine>`_.

            deleting: Boolean filter - queue is being deleted (``delete_after`` is set)

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-queues.
        """
        for q in self.internal_client.fetch_resources(Resource.Queue, ordering, **filters):
            yield self._deserializer(Resource.Queue, q)

    def create_new_queue(self, data: dict[str, Any]) -> QueueType:
        """Create a new :class:`~rossum_api.models.queue.Queue` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.queue.Queue` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-new-queue.

        https://elis.rossum.ai/api/docs/#queue.
        """
        queue = self.internal_client.create(Resource.Queue, data)
        return self._deserializer(Resource.Queue, queue)

    def delete_queue(self, queue_id: int) -> None:
        """Delete :class:`~rossum_api.models.queue.Queue` object.

        Parameters
        ----------
            ID of a queue to be deleted.

        Notes
        -----
        By default, the deletion will start after 24 hours.


        .. warning::
            It also deletes all the related objects. Please note that while the queue
            and related objects are being deleted the API may return inconsistent results.
            We strongly discourage from any interaction with the queue after being scheduled for deletion.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-queue.
        """
        return self.internal_client.delete(Resource.Queue, queue_id)

    def _import_document(
        self,
        url: str,
        files: Sequence[tuple[str | Path, str]],
        values: dict[str, Any] | None,
        metadata: dict[str, Any] | None,
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
        files: Sequence[tuple[str | Path, str]],
        values: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[int]:
        """https://elis.rossum.ai/api/docs/#import-a-document.

        Deprecated now, consider upload_document.

        Parameters
        ----------
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
        files: Sequence[tuple[str | pathlib.Path, str]],
        values: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[TaskType]:
        """Do the same thing as import_document method, but uses a different endpoint.

        Parameters
        ----------
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

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-upload
        """
        url = f"uploads?queue={queue_id}"
        task_ids = self._import_document(url, files, values, metadata)
        return [self.retrieve_task(task_id) for task_id in task_ids]

    def retrieve_upload(self, upload_id: int) -> UploadType:
        """Retrieve `rossum_api.models.upload.Upload` object.

        Parameters
        ----------
        upload_id
            ID of an upload to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-upload.
        """
        upload = self.internal_client.fetch_resource(Resource.Upload, upload_id)
        return self._deserializer(Resource.Upload, upload)

    # ##### EXPORT #####

    def export_annotations_to_json(
        self, queue_id: int, **filters: Any
    ) -> Iterator[AnnotationType]:
        """Export annotations from the queue to JSON.

        Notes
        -----
        JSON export is paginated and returns the result in a way similar to other list_all methods.

        Parameters
        ----------
        queue_id
            ID of a queue annotions should be exported from.
        filters
            id
                Id of annotation to be exported, multiple ids may be separated by a comma.
            status
                :class:`~rossum_api.models.annotation.Annotation` status.
            modifier
                :class:`~rossum_api.models.user.User` id.
            arrived_at_before
                ISO 8601 timestamp (e.g. ``arrived_at_before=2019-11-15``).
            arrived_at_after
                ISO 8601 timestamp (e.g. ``arrived_at_after=2019-11-14``).
            exported_at_after
                ISO 8601 timestamp (e.g. ``exported_at_after=2019-11-14 12:00:00``).
            export_failed_at_before
                ISO 8601 timestamp (e.g. ``export_failed_at_before=2019-11-14 22:00:00``).
            export_failed_at_after
                ISO 8601 timestamp (e.g. ``export_failed_at_after=2019-11-14 12:00:00``).
            page_size
                Number of the documents to be exported.
                To be used together with ``page`` attribute. See `pagination <https://elis.rossum.ai/api/docs/#pagination>`_.
            page
                Number of a page to be exported when using pagination.
                Useful for exports of large amounts of data.
                To be used together with the ``page_size`` attribute.

        Notes
        -----
            When the search filter is used, results are limited to 10 000.
            We suggest narrowing down the search query if there are this many results.

        References
        ----------
        https://elis.rossum.ai/api/docs/#export-annotations
        """
        for chunk in self.internal_client.export(Resource.Queue, queue_id, "json", **filters):
            # JSON export can be translated directly to Annotation object
            yield self._deserializer(Resource.Annotation, cast("dict", chunk))

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats, **filters: Any
    ) -> Iterator[bytes]:
        """Export annotations from the queue to a desired export format.

        Notes
        -----
        JSON export is paginated and returns the result in a way similar to other list_all methods.

        Parameters
        ----------
        queue_id
            ID of a queue annotions should be exported from.
        export_format
            Target export format.
        filters
            id
                Id of annotation to be exported, multiple ids may be separated by a comma.
            status
                :class:`~rossum_api.models.annotation.Annotation` status.
            modifier
                :class:`~rossum_api.models.user.User` id.
            arrived_at_before
                ISO 8601 timestamp (e.g. ``arrived_at_before=2019-11-15``).
            arrived_at_after
                ISO 8601 timestamp (e.g. ``arrived_at_after=2019-11-14``).
            exported_at_after
                ISO 8601 timestamp (e.g. ``exported_at_after=2019-11-14 12:00:00``).
            export_failed_at_before
                ISO 8601 timestamp (e.g. ``export_failed_at_before=2019-11-14 22:00:00``).
            export_failed_at_after
                ISO 8601 timestamp (e.g. ``export_failed_at_after=2019-11-14 12:00:00``).
            page_size
                Number of the documents to be exported.
                To be used together with ``page`` attribute. See `pagination <https://elis.rossum.ai/api/docs/#pagination>`_.
            page
                Number of a page to be exported when using pagination.
                Useful for exports of large amounts of data.
                To be used together with the ``page_size`` attribute.

        Notes
        -----
            When the search filter is used, results are limited to 10 000.
            We suggest narrowing down the search query if there are this many results.

        References
        ----------
        https://elis.rossum.ai/api/docs/#export-annotations
        """
        for chunk in self.internal_client.export(
            Resource.Queue,
            queue_id,
            export_format.value,
            **filters,
        ):
            yield cast("bytes", chunk)

    # ##### ORGANIZATIONS #####

    def list_organizations(
        self, ordering: Sequence[OrganizationOrdering] = (), **filters: Any
    ) -> Iterator[OrganizationType]:
        """Retrieve all organization objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their IDs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.organization.Organization`

            name: Name of a :class:`~rossum_api.models.organization.Organization`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-organizations.
        """
        for o in self.internal_client.fetch_resources(Resource.Organization, ordering, **filters):
            yield self._deserializer(Resource.Organization, o)

    def retrieve_organization(self, org_id: int) -> OrganizationType:
        """Retrieve a single :class:`~rossum_api.models.organization.Qrganization` object.

        Parameters
        ----------
        org_id
            ID of an organization to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-an-organization.
        """
        organization = self.internal_client.fetch_resource(Resource.Organization, org_id)
        return self._deserializer(Resource.Organization, organization)

    def retrieve_own_organization(self) -> OrganizationType:
        """Retrieve organization of currently logged in user."""
        user: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Auth, "user")
        organization_id = parse_resource_id_from_url(user["organization"])
        return self.retrieve_organization(organization_id)

    def retrieve_my_organization(self) -> OrganizationType:
        """Retrieve organization of currently logged in user."""
        warnings.warn(
            "`retrieve_my_organization` is deprecated and will be removed. Please use `retrieve_own_organization` instead.",
            DeprecationWarning,
            stacklevel=2,  # point to the users' code
        )
        return self.retrieve_own_organization()

    # ##### SCHEMAS #####

    def list_schemas(
        self, ordering: Sequence[SchemaOrdering] = (), **filters: Any
    ) -> Iterator[SchemaType]:
        """Retrieve all :class:`~rossum_api.models.schema.Schema` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.schema.Schema`

            name: Name of a :class:`~rossum_api.models.schema.Schema`

            queue: ID of a :class:`~rossum_api.models.queue.Queue`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-schemas.

        https://elis.rossum.ai/api/docs/#schema.
        """
        for s in self.internal_client.fetch_resources(Resource.Schema, ordering, **filters):
            yield self._deserializer(Resource.Schema, s)

    def retrieve_schema(self, schema_id: int) -> SchemaType:
        """Retrieve a single :class:`~rossum_api.models.schema.Schema` object.

        Parameters
        ----------
        schema_id
            ID of a schema to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-schema.

        https://elis.rossum.ai/api/docs/#schema.
        """
        schema: dict[Any, Any] = self.internal_client.fetch_resource(Resource.Schema, schema_id)
        return self._deserializer(Resource.Schema, schema)

    def create_new_schema(self, data: dict[str, Any]) -> SchemaType:
        """Create a new :class:`~rossum_api.models.schema.Schema` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.schema.Schema` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-schema.

        https://elis.rossum.ai/api/docs/#schema.
        """
        schema = self.internal_client.create(Resource.Schema, data)
        return self._deserializer(Resource.Schema, schema)

    def delete_schema(self, schema_id: int) -> None:
        """Delete :class:`~rossum_api.models.schema.Schema` object.

        Parameters
        ----------
        schema_id
            ID of a schema to be deleted.

        Notes
        -----
        .. warning::
            In case the schema is linked to some objects, like queue or annotation, the deletion
            is not possible and the request will fail with 409 status code.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-schema.

        https://elis.rossum.ai/api/docs/#schema.
        """
        return self.internal_client.delete(Resource.Schema, schema_id)

    # ##### USERS #####

    def list_users(
        self, ordering: Sequence[UserOrdering] = (), **filters: Any
    ) -> Iterator[UserType]:
        """Retrieve all :class:`~rossum_api.models.user.User` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.user.User`

            username: Username of a :class:`~rossum_api.models.user.User`

            first_name: First name of a :class:`~rossum_api.models.user.User`

            last_name: Last name of a :class:`~rossum_api.models.user.User`

            email: Email address of a :class:`~rossum_api.models.user.User`

            is_active: Boolean filter - whether the :class:`~rossum_api.models.user.User` is active

            last_login: ISO 8601 timestamp filter for last login date

            groups: IDs of :class:`~rossum_api.models.group.Group` objects

            queue: ID of a :class:`~rossum_api.models.queue.Queue`

            deleted: Boolean filter - whether the :class:`~rossum_api.models.user.User` is deleted


        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-users.

        https://elis.rossum.ai/api/docs/#user.
        """
        for u in self.internal_client.fetch_resources(Resource.User, ordering, **filters):
            yield self._deserializer(Resource.User, u)

    def retrieve_user(self, user_id: int) -> UserType:
        """Retrieve a single :class:`~rossum_api.models.user.User` object.

        Parameters
        ----------
        user_id
            ID of a user to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-user-2.

        https://elis.rossum.ai/api/docs/#user.
        """
        user = self.internal_client.fetch_resource(Resource.User, user_id)
        return self._deserializer(Resource.User, user)

    # TODO: specific method in InternalSyncRossumAPIClient
    def change_user_password(self, new_password: str) -> dict:  # noqa: D102
        raise NotImplementedError

    # TODO: specific method in InternalSyncRossumAPIClient
    def reset_user_password(self, email: str) -> dict:  # noqa: D102
        raise NotImplementedError

    def create_new_user(self, data: dict[str, Any]) -> UserType:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        user = self.internal_client.create(Resource.User, data)
        return self._deserializer(Resource.User, user)

    # ##### ANNOTATIONS #####

    def retrieve_annotation(
        self, annotation_id: int, sideloads: Sequence[Sideload] = ()
    ) -> AnnotationType:
        """Retrieve a single :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be retrieved.
        sideloads
            List of additional objects to sideload

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-an-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        annotation = self.internal_client.fetch_resource(Resource.Annotation, annotation_id)
        if sideloads:
            self.internal_client.sideload(annotation, sideloads)
        return self._deserializer(Resource.Annotation, annotation)

    def list_annotations(
        self,
        ordering: Sequence[AnnotationOrdering] = (),
        sideloads: Sequence[Sideload] = (),
        content_schema_ids: Sequence[str] = (),
        **filters: Any,
    ) -> Iterator[AnnotationType]:
        """Retrieve all :class:`~rossum_api.models.annotation.Annotation` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        sideloads
            List of additional objects to sideload
        content_schema_ids
            List of content schema IDs
        filters
            status: :class:`~rossum_api.models.annotation.Annotation` status, multiple values may be separated using a comma

            id: List of ids separated by a comma

            modifier: :class:`~rossum_api.models.user.User` id

            confirmed_by: :class:`~rossum_api.models.user.User` id

            deleted_by: :class:`~rossum_api.models.user.User` id

            exported_by: :class:`~rossum_api.models.user.User` id

            purged_by: :class:`~rossum_api.models.user.User` id

            rejected_by: :class:`~rossum_api.models.user.User` id

            assignees: :class:`~rossum_api.models.user.User` id, multiple values may be separated using a comma

            labels: Label id, multiple values may be separated using a comma

            document: :class:`~rossum_api.models.document.Document` id

            queue: List of :class:`~rossum_api.models.queue.Queue` ids separated by a comma

            queue__workspace: List of :class:`~rossum_api.models.workspace.Workspace` ids separated by a comma

            relations__parent: ID of parent annotation defined in related Relation object

            relations__type: Type of Relation that annotation belongs to

            relations__key: Key of Relation that annotation belongs to

            arrived_at_before: ISO 8601 timestamp (e.g. ``arrived_at_before=2019-11-15``)

            arrived_at_after: ISO 8601 timestamp (e.g. ``arrived_at_after=2019-11-14``)

            assigned_at_before: ISO 8601 timestamp (e.g. ``assigned_at_before=2019-11-15``)

            assigned_at_after: ISO 8601 timestamp (e.g. ``assigned_at_after=2019-11-14``)

            confirmed_at_before: ISO 8601 timestamp (e.g. ``confirmed_at_before=2019-11-15``)

            confirmed_at_after: ISO 8601 timestamp (e.g. ``confirmed_at_after=2019-11-14``)

            modified_at_before: ISO 8601 timestamp (e.g. ``modified_at_before=2019-11-15``)

            modified_at_after: ISO 8601 timestamp (e.g. ``modified_at_after=2019-11-14``)

            deleted_at_before: ISO 8601 timestamp (e.g. ``deleted_at_before=2019-11-15``)

            deleted_at_after: ISO 8601 timestamp (e.g. ``deleted_at_after=2019-11-14``)

            exported_at_before: ISO 8601 timestamp (e.g. ``exported_at_before=2019-11-14 22:00:00``)

            exported_at_after: ISO 8601 timestamp (e.g. ``exported_at_after=2019-11-14 12:00:00``)

            export_failed_at_before: ISO 8601 timestamp (e.g. ``export_failed_at_before=2019-11-14 22:00:00``)

            export_failed_at_after: ISO 8601 timestamp (e.g. ``export_failed_at_after=2019-11-14 12:00:00``)

            purged_at_before: ISO 8601 timestamp (e.g. ``purged_at_before=2019-11-15``)

            purged_at_after: ISO 8601 timestamp (e.g. ``purged_at_after=2019-11-14``)

            rejected_at_before: ISO 8601 timestamp (e.g. ``rejected_at_before=2019-11-15``)

            rejected_at_after: ISO 8601 timestamp (e.g. ``rejected_at_after=2019-11-14``)

            restricted_access: Boolean

            automated: Boolean

            has_email_thread_with_replies: Boolean (related email thread contains more than one incoming emails)

            has_email_thread_with_new_replies: Boolean (related email thread contains unread incoming email)

            search: String, see Annotation search

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-annotations.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        validate_list_annotations_params(sideloads, content_schema_ids)

        for annotation in self.internal_client.fetch_resources(
            Resource.Annotation, ordering, sideloads, content_schema_ids, **filters
        ):
            yield self._deserializer(Resource.Annotation, annotation)

    def search_for_annotations(
        self,
        query: dict | None = None,
        query_string: dict | None = None,
        ordering: Sequence[AnnotationOrdering] = (),
        sideloads: Sequence[Sideload] = (),
        **kwargs: Any,
    ) -> Iterator[AnnotationType]:
        """Search for :class:`~rossum_api.models.annotation.Annotation` objects.

        Parameters
        ----------
        query
            Query dictionary for advanced search
        query_string
            Query string dictionary for text search
        ordering
            List of object names. Their URLs are used for sorting the results
        sideloads
            List of additional objects to sideload
        kwargs
            Additional search parameters

        References
        ----------
        https://elis.rossum.ai/api/docs/#search-for-annotations.

        https://elis.rossum.ai/api/docs/#annotation.
        """
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
        sideloads: Sequence[Sideload] = (),
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
        """Wait until annotation is imported.

        Parameters
        ----------
        annotation_id
            ID of an annotation to poll.
        poll_kwargs
            Additional keyword arguments passed to poll_annotation.
        """
        return self.poll_annotation(annotation_id, is_annotation_imported, **poll_kwargs)

    # ##### TASKS #####

    def retrieve_task(self, task_id: int) -> TaskType:
        """https://elis.rossum.ai/api/docs/#retrieve-task."""
        task = self.internal_client.fetch_resource(
            Resource.Task, task_id, request_params={"no_redirect": "True"}
        )
        return self._deserializer(Resource.Task, task)

    def poll_task(
        self, task_id: int, predicate: Callable[[TaskType], bool], sleep_s: int = 3
    ) -> TaskType:
        """Poll on Task until predicate is true.

        As with Annotation polling, there is no innate retry limit.
        """
        task = self.retrieve_task(task_id)

        while not predicate(task):
            time.sleep(sleep_s)
            task = self.retrieve_task(task_id)

        return task

    def poll_task_until_succeeded(self, task_id: int, sleep_s: int = 3) -> TaskType:
        """Poll on Task until it is succeeded."""
        return self.poll_task(task_id, is_task_succeeded, sleep_s)

    def upload_and_wait_until_imported(
        self, queue_id: int, filepath: str | pathlib.Path, filename: str, **poll_kwargs: Any
    ) -> AnnotationType:
        """Upload a single file and waiting until its annotation is imported in a single call."""
        (annotation_id,) = self.import_document(queue_id, [(filepath, filename)])
        return self.poll_annotation_until_imported(annotation_id, **poll_kwargs)

    def start_annotation(self, annotation_id: int) -> None:
        """Start annotation processing.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be started.

        References
        ----------
        https://elis.rossum.ai/api/docs/#start-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        self.internal_client.request_json(
            "POST", build_resource_start_url(Resource.Annotation, annotation_id)
        )

    def update_annotation(self, annotation_id: int, data: dict[str, Any]) -> AnnotationType:
        """Update an :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be updated.
        data
            :class:`~rossum_api.models.annotation.Annotation` object update data.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-an-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        annotation = self.internal_client.replace(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def update_part_annotation(self, annotation_id: int, data: dict[str, Any]) -> AnnotationType:
        """Update part of an :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be updated.
        data
            Partial :class:`~rossum_api.models.annotation.Annotation` object update data.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-part-of-an-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        annotation = self.internal_client.update(Resource.Annotation, annotation_id, data)
        return self._deserializer(Resource.Annotation, annotation)

    def bulk_update_annotation_data(
        self, annotation_id: int, operations: list[dict[str, Any]]
    ) -> None:
        """Bulk update annotation data.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be updated.
        operations
            List of operations to perform on annotation data.

        References
        ----------
        https://elis.rossum.ai/api/docs/#bulk-update-annotation-data.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        self.internal_client.request_json(
            "POST",
            build_resource_content_operations_url(Resource.Annotation, annotation_id),
            json={"operations": operations},
        )

    def confirm_annotation(self, annotation_id: int) -> None:
        """Confirm annotation.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be confirmed.

        References
        ----------
        https://elis.rossum.ai/api/docs/#confirm-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        self.internal_client.request_json(
            "POST", build_resource_confirm_url(Resource.Annotation, annotation_id)
        )

    def create_new_annotation(self, data: dict[str, Any]) -> AnnotationType:
        """Create a new :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.annotation.Annotation` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-an-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        annotation = self.internal_client.create(Resource.Annotation, data)
        return self._deserializer(Resource.Annotation, annotation)

    def delete_annotation(self, annotation_id: int) -> None:
        """Delete :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be deleted.

        References
        ----------
        https://elis.rossum.ai/api/docs/#switch-to-deleted.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        self.internal_client.request(
            "POST", url=build_resource_delete_url(Resource.Annotation, annotation_id)
        )

    def cancel_annotation(self, annotation_id: int) -> None:
        """Cancel :class:`~rossum_api.models.annotation.Annotation` object.

        Parameters
        ----------
        annotation_id
            ID of an annotation to be cancelled.

        References
        ----------
        https://elis.rossum.ai/api/docs/#cancel-annotation.

        https://elis.rossum.ai/api/docs/#annotation.
        """
        self.internal_client.request(
            "POST", url=build_resource_cancel_url(Resource.Annotation, annotation_id)
        )

    # ##### DOCUMENTS #####

    def retrieve_document(self, document_id: int) -> DocumentType:
        """Retrieve a single :class:`~rossum_api.models.document.Document` object.

        Parameters
        ----------
        document_id
            ID of a document to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-document.

        https://elis.rossum.ai/api/docs/#document.
        """
        document: dict[Any, Any] = self.internal_client.fetch_resource(
            Resource.Document, document_id
        )
        return self._deserializer(Resource.Document, document)

    def retrieve_document_content(self, document_id: int) -> bytes:
        """Get the binary content of a document.

        Parameters
        ----------
        document_id
            ID of a document to retrieve content for.

        References
        ----------
        https://elis.rossum.ai/api/docs/#document-content.

        https://elis.rossum.ai/api/docs/#document.
        """
        document_content = self.internal_client.request(
            "GET", url=build_resource_content_url(Resource.Document, document_id)
        )
        return document_content.content  # type: ignore[no-any-return]

    def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: dict[str, Any] | None = None,
        parent: str | None = None,
    ) -> DocumentType:
        """Create a new :class:`~rossum_api.models.document.Document` object.

        Parameters
        ----------
        file_name
            Name of the file to be created.
        file_data
            Binary content of the file.
        metadata
            Optional metadata to attach to the document.
        parent
            Optional parent document URL.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-document.

        https://elis.rossum.ai/api/docs/#document.
        """
        files = build_create_document_params(file_name, file_data, metadata, parent)
        document = self.internal_client.request_json(
            "POST", url=Resource.Document.value, files=files
        )
        return self._deserializer(Resource.Document, document)

    # ##### DOCUMENT RELATIONS #####

    def list_document_relations(
        self, ordering: Sequence[DocumentRelationOrdering] = (), **filters: Any
    ) -> Iterator[DocumentRelationType]:
        """Retrieve all :class:`~rossum_api.models.document_relation.DocumentRelation` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.document_relation.DocumentRelation`

            type: Type of the document relation

            key: Key for the document relation

            parent: ID of a parent :class:`~rossum_api.models.document.Document`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-document-relations.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        for dr in self.internal_client.fetch_resources(
            Resource.DocumentRelation, ordering, **filters
        ):
            yield self._deserializer(Resource.DocumentRelation, dr)

    def retrieve_document_relation(self, document_relation_id: int) -> DocumentRelationType:
        """Retrieve a single :class:`~rossum_api.models.document_relation.DocumentRelation` object.

        Parameters
        ----------
        document_relation_id
            ID of a document relation to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-document-relation.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        document_relation = self.internal_client.fetch_resource(
            Resource.DocumentRelation, document_relation_id
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def create_new_document_relation(self, data: dict[str, Any]) -> DocumentRelationType:
        """Create a new :class:`~rossum_api.models.document_relation.DocumentRelation` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.document_relation.DocumentRelation` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-document-relation.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        document_relation = self.internal_client.create(Resource.DocumentRelation, data)

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def update_document_relation(
        self, document_relation_id: int, data: dict[str, Any]
    ) -> DocumentRelationType:
        """Update a :class:`~rossum_api.models.document_relation.DocumentRelation` object.

        Parameters
        ----------
        document_relation_id
            ID of a document relation to be updated.
        data
            :class:`~rossum_api.models.document_relation.DocumentRelation` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-a-document-relation.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        document_relation = self.internal_client.replace(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def update_part_document_relation(
        self, document_relation_id: int, data: dict[str, Any]
    ) -> DocumentRelationType:
        """Update part of a :class:`~rossum_api.models.document_relation.DocumentRelation` object.

        Parameters
        ----------
        document_relation_id
            ID of a document relation to be updated.
        data
            :class:`~rossum_api.models.document_relation.DocumentRelation` object partial configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-part-of-a-document-relation.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        document_relation = self.internal_client.update(
            Resource.DocumentRelation, document_relation_id, data
        )

        return self._deserializer(Resource.DocumentRelation, document_relation)

    def delete_document_relation(self, document_relation_id: int) -> None:
        """Delete a :class:`~rossum_api.models.document_relation.DocumentRelation` object.

        Parameters
        ----------
        document_relation_id
            ID of a document relation to be deleted.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-document-relation.

        https://elis.rossum.ai/api/docs/#document-relation.
        """
        self.internal_client.delete(Resource.DocumentRelation, document_relation_id)

    # ##### WORKSPACES #####

    def list_workspaces(
        self, ordering: Sequence[WorkspaceOrdering] = (), **filters: Any
    ) -> Iterator[WorkspaceType]:
        """Retrieve all :class:`~rossum_api.models.workspace.Workspace` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.workspace.Workspace`

            name: Name of a :class:`~rossum_api.models.workspace.Workspace`

            organization: ID of an :class:`~rossum_api.models.organization.Organization`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-workspaces.

        https://elis.rossum.ai/api/docs/#workspace.
        """
        for w in self.internal_client.fetch_resources(Resource.Workspace, ordering, **filters):
            yield self._deserializer(Resource.Workspace, w)

    def retrieve_workspace(self, workspace_id: int) -> WorkspaceType:
        """Retrieve a single :class:`~rossum_api.models.workspace.Workspace` object.

        Parameters
        ----------
        workspace_id
            ID of a workspace to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-workspace.

        https://elis.rossum.ai/api/docs/#workspace.
        """
        workspace = self.internal_client.fetch_resource(Resource.Workspace, workspace_id)

        return self._deserializer(Resource.Workspace, workspace)

    def create_new_workspace(self, data: dict[str, Any]) -> WorkspaceType:
        """Create a new :class:`~rossum_api.models.workspace.Workspace` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.workspace.Workspace` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-workspace.

        https://elis.rossum.ai/api/docs/#workspace.
        """
        workspace = self.internal_client.create(Resource.Workspace, data)

        return self._deserializer(Resource.Workspace, workspace)

    def delete_workspace(self, workspace_id: int) -> None:
        """Delete :class:`rossum_api.models.workspace.Workspace` object.

        Parameters
        ----------
        workspace_id
            ID of a workspace to be deleted.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-workspace.

        https://elis.rossum.ai/api/docs/#workspace.
        """
        return self.internal_client.delete(Resource.Workspace, workspace_id)

    # ##### ENGINE #####

    def retrieve_engine(self, engine_id: int) -> EngineType:
        """Retrieve a single :class:`~rossum_api.models.engine.Engine` object.

        Parameters
        ----------
        engine_id
            ID of an engine to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-an-engine.

        https://elis.rossum.ai/api/docs/#engine.
        """
        engine = self.internal_client.fetch_resource(Resource.Engine, engine_id)
        return self._deserializer(Resource.Engine, engine)

    def list_engines(
        self, ordering: Sequence[str] = (), sideloads: Sequence[Sideload] = (), **filters: Any
    ) -> Iterator[EngineType]:
        """Retrieve all :class:`~rossum_api.models.engine.Engine` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        sideloads
            List of additional objects to sideload
        filters
            id: ID of an :class:`~rossum_api.models.engine.Engine`

            name: Name of an :class:`~rossum_api.models.engine.Engine`

            description: Description of an :class:`~rossum_api.models.engine.Engine`

        References
        ----------
        https://elis.rossum.ai/api/docs/internal/#list-all-engines.

        https://elis.rossum.ai/api/docs/#engine.
        """
        for c in self.internal_client.fetch_resources(
            Resource.Engine, ordering, sideloads, **filters
        ):
            yield self._deserializer(Resource.Engine, c)

    def retrieve_engine_fields(self, engine_id: int | None = None) -> Iterator[EngineFieldType]:
        """Retrieve all :class:`~rossum_api.models.engine.EngineField` objects satisfying the specified filters.

        Parameters
        ----------
        engine_id
            ID of an engine to retrieve fields for. If None, retrieves all engine fields.

        References
        ----------
        https://elis.rossum.ai/api/docs/internal/#engine-field.

        https://elis.rossum.ai/api/docs/#engine-field.
        """
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
        """Create a new :class:`~rossum_api.models.inbox.Inbox` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.inbox.Inbox` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-inbox.

        https://elis.rossum.ai/api/docs/#inbox.
        """
        inbox = self.internal_client.create(Resource.Inbox, data)
        return self._deserializer(Resource.Inbox, inbox)

    # ##### EMAILS #####
    def retrieve_email(self, email_id: int) -> EmailType:
        """Retrieve a single `rossum_api.models.email.Email` object.

        Parameters
        ----------
        email_id
            ID of email to be retrieved

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-an-email.

        https://elis.rossum.ai/api/docs/#email.
        """
        email = self.internal_client.fetch_resource(Resource.Email, email_id)

        return self._deserializer(Resource.Email, email)

    def import_email(
        self, raw_message: bytes, recipient: str, mime_type: str | None = None
    ) -> str:
        """Import an email as raw data.

        Calling this endpoint starts an asynchronous process of creating an email object
        and importing its contents to the specified recipient inbox in Rossum.

        Parameters
        ----------
        raw_message
            Raw email data.
        recipient
            Email address of the inbox where the email will be imported.
        mime_type
            Mime type of imported files

        Returns
        -------
        str
            Task URL that can be used to track the import status.

        References
        ----------
        https://elis.rossum.ai/api/docs/#import-email.

        https://elis.rossum.ai/api/docs/#email.
        """
        response = self.internal_client.request_json(
            "POST",
            url=EMAIL_IMPORT_URL,
            files=build_email_import_files(raw_message, recipient, mime_type),
        )
        return response["url"]  # type: ignore[no-any-return]

    # ##### EMAIL TEMPLATES #####

    def list_email_templates(
        self, ordering: Sequence[EmailTemplateOrdering] = (), **filters: Any
    ) -> Iterator[EmailTemplateType]:
        """Retrieve all :class:`~rossum_api.models.email_template.EmailTemplate` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of an :class:`~rossum_api.models.email_template.EmailTemplate`

            queue: ID of a :class:`~rossum_api.models.queue.Queue`

            type: Type of the email template

            name: Name of the :class:`~rossum_api.models.email_template.EmailTemplate`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-email-templates.

        https://elis.rossum.ai/api/docs/#email-template.
        """
        for c in self.internal_client.fetch_resources(Resource.EmailTemplate, ordering, **filters):
            yield self._deserializer(Resource.EmailTemplate, c)

    def retrieve_email_template(self, email_template_id: int) -> EmailTemplateType:
        """Retrieve a single :class:`~rossum_api.models.email_template.EmailTemplate` object.

        Parameters
        ----------
        email_template_id
            ID of an email template to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-an-email-template-object.

        https://elis.rossum.ai/api/docs/#email-template.
        """
        email_template = self.internal_client.fetch_resource(
            Resource.EmailTemplate, email_template_id
        )
        return self._deserializer(Resource.EmailTemplate, email_template)

    def create_new_email_template(self, data: dict[str, Any]) -> EmailTemplateType:
        """Create a new :class:`~rossum_api.models.email_template.EmailTemplate` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.email_template.EmailTemplate` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-new-email-template-object.

        https://elis.rossum.ai/api/docs/#email-template.
        """
        email_template = self.internal_client.create(Resource.EmailTemplate, data)
        return self._deserializer(Resource.EmailTemplate, email_template)

    # ##### CONNECTORS #####

    def list_connectors(
        self, ordering: Sequence[ConnectorOrdering] = (), **filters: Any
    ) -> Iterator[ConnectorType]:
        """Retrieve all :class:`~rossum_api.models.connector.Connector` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.connector.Connector`

            name: Name of the :class:`~rossum_api.models.connector.Connector`

            service_url: Service URL of the :class:`~rossum_api.models.connector.Connector`

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-connectors.

        https://elis.rossum.ai/api/docs/#connector.
        """
        for c in self.internal_client.fetch_resources(Resource.Connector, ordering, **filters):
            yield self._deserializer(Resource.Connector, c)

    def retrieve_connector(self, connector_id: int) -> ConnectorType:
        """Retrieve a single :class:`~rossum_api.models.connector.Connector` object.

        Parameters
        ----------
        connector_id
            ID of a connector to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-connector.

        https://elis.rossum.ai/api/docs/#connector.
        """
        connector = self.internal_client.fetch_resource(Resource.Connector, connector_id)
        return self._deserializer(Resource.Connector, connector)

    def create_new_connector(self, data: dict[str, Any]) -> ConnectorType:
        """Create a new :class:`~rossum_api.models.connector.Connector` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.connector.Connector` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-connector.

        https://elis.rossum.ai/api/docs/#connector.
        """
        connector = self.internal_client.create(Resource.Connector, data)
        return self._deserializer(Resource.Connector, connector)

    # ##### HOOKS #####

    def list_hooks(
        self, ordering: Sequence[HookOrdering] = (), **filters: Any
    ) -> Iterator[HookType]:
        """Retrieve all :class:`~rossum_api.models.hook.Hook` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.hook.Hook`

            name: Name of a :class:`~rossum_api.models.hook.Hook`

            type: Hook type. Possible values: ``webhook, function``

            queue: ID of a :class:`~rossum_api.models.queue.Queue`

            active: If set to true the hook is notified.

            config_url:

            config_app_url:

            extension_source: Import source of the extension.
            For more, see `Extension sources <https://elis.rossum.ai/api/docs/#extension-sources>`_.

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-hooks.

        https://elis.rossum.ai/api/docs/#hook.
        """
        for h in self.internal_client.fetch_resources(Resource.Hook, ordering, **filters):
            yield self._deserializer(Resource.Hook, h)

    def retrieve_hook(self, hook_id: int) -> HookType:
        """Retrieve a single :class:`~rossum_api.models.hook.Hook` object.

        Parameters
        ----------
        hook_id
            ID of a hook to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-a-hook.

        https://elis.rossum.ai/api/docs/#hook.
        """
        hook = self.internal_client.fetch_resource(Resource.Hook, hook_id)
        return self._deserializer(Resource.Hook, hook)

    def create_new_hook(self, data: dict[str, Any]) -> HookType:
        """Create a new :class:`~rossum_api.models.hook.Hook` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.hook.Hook` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-hook.

        https://elis.rossum.ai/api/docs/#hook.
        """
        hook = self.internal_client.create(Resource.Hook, data)
        return self._deserializer(Resource.Hook, hook)

    def update_part_hook(self, hook_id: int, data: dict[str, Any]) -> HookType:
        """Update part of a :class:`~rossum_api.models.hook.Hook` object.

        Parameters
        ----------
        hook_id
            ID of a hook to be updated.
        data
            :class:`~rossum_api.models.hook.Hook` object partial configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-part-of-a-hook.

        https://elis.rossum.ai/api/docs/#hook.
        """
        hook = self.internal_client.update(Resource.Hook, hook_id, data)
        return self._deserializer(Resource.Hook, hook)

    def delete_hook(self, hook_id: int) -> None:
        """Delete a :class:`~rossum_api.models.hook.Hook` object.

        Parameters
        ----------
        hook_id
            ID of a hook to be deleted.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-hook.

        https://elis.rossum.ai/api/docs/#hook.
        """
        return self.internal_client.delete(Resource.Hook, hook_id)

    # ##### RULES #####
    def list_rules(
        self, ordering: Sequence[RuleOrdering] = (), **filters: Any
    ) -> Iterator[RuleType]:
        """Retrieve all :class:`~rossum_api.models.rule.Rule` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            id: ID of a :class:`~rossum_api.models.rule.Rule`.

            name: Name of a :class:`~rossum_api.models.rule.Rule`.

            schema: ID of a :class:`~rossum_api.models.schema.Schema`.

            rule_template: URL of the rule template the rule was created from.

            organization: ID of a :class:`~rossum_api.models.organization.Organization`.

        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-rules.

        https://elis.rossum.ai/api/docs/#rule.
        """
        for r in self.internal_client.fetch_resources(Resource.Rule, ordering, **filters):
            yield self._deserializer(Resource.Rule, r)

    def retrieve_rule(self, rule_id: int) -> RuleType:
        """Retrieve a single :class:`~rossum_api.models.rule.Rule` object.

        Parameters
        ----------
        rule_id
            ID of a rule to be retrieved.

        References
        ----------
        https://elis.rossum.ai/api/docs/#retrieve-rule.

        https://elis.rossum.ai/api/docs/#rule.
        """
        rule = self.internal_client.fetch_resource(Resource.Rule, rule_id)
        return self._deserializer(Resource.Rule, rule)

    def create_new_rule(self, data: dict[str, Any]) -> RuleType:
        """Create a new :class:`~rossum_api.models.rule.Rule` object.

        Parameters
        ----------
        data
            :class:`~rossum_api.models.rule.Rule` object configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#create-a-new-rule.

        https://elis.rossum.ai/api/docs/#rule.
        """
        rule = self.internal_client.create(Resource.Rule, data)
        return self._deserializer(Resource.Rule, rule)

    def update_part_rule(self, rule_id: int, data: dict[str, Any]) -> RuleType:
        """Update part of a :class:`~rossum_api.models.rule.Rule` object.

        Parameters
        ----------
        rule_id
            ID of a rule to be updated.
        data
            :class:`~rossum_api.models.rule.Rule` object partial configuration.

        References
        ----------
        https://elis.rossum.ai/api/docs/#update-a-rule.

        https://elis.rossum.ai/api/docs/#rule.
        """
        rule = self.internal_client.update(Resource.Rule, rule_id, data)
        return self._deserializer(Resource.Rule, rule)

    def delete_rule(self, rule_id: int) -> None:
        """Delete a :class:`~rossum_api.models.rule.Rule` object.

        Parameters
        ----------
        rule_id
            ID of a rule to be deleted.

        References
        ----------
        https://elis.rossum.ai/api/docs/#delete-a-rule.

        https://elis.rossum.ai/api/docs/#rule.
        """
        return self.internal_client.delete(Resource.Rule, rule_id)

    # ##### USER ROLES #####

    def list_user_roles(
        self, ordering: Sequence[UserRoleOrdering] = (), **filters: Any
    ) -> Iterator[GroupType]:
        """Retrieve all :class:`~rossum_api.models.group.Group` objects satisfying the specified filters.

        Parameters
        ----------
        ordering
            List of object names. Their URLs are used for sorting the results
        filters
            name: Name of :class:`~rossum_api.models.group.Group`


        References
        ----------
        https://elis.rossum.ai/api/docs/#list-all-user-roles.

        https://elis.rossum.ai/api/docs/#user-role.
        """
        for g in self.internal_client.fetch_resources(Resource.Group, ordering, **filters):
            yield self._deserializer(Resource.Group, g)

    # ##### GENERIC METHODS #####
    def request_paginated(self, url: str, *args: Any, **kwargs: Any) -> Iterator[dict]:
        """Request to endpoints with paginated response that do not have direct support in the client."""
        yield from self.internal_client.fetch_resources_by_url(url, *args, **kwargs)

    def request_json(self, method: HttpMethod, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Request to endpoints that do not have direct support in the client and return plain JSON."""
        return self.internal_client.request_json(method, *args, **kwargs)

    def request(self, method: HttpMethod, *args: Any, **kwargs: Any) -> httpx.Response:
        """Request to endpoints that do not have direct support in the client and return plain response."""
        return self.internal_client.request(method, *args, **kwargs)

    def authenticate(self) -> None:  # noqa: D102
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
    Rule,
    Schema,
    Task,
    Upload,
    User,
    Workspace,
]
