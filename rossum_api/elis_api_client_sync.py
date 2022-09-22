from __future__ import annotations

import asyncio
import typing

if typing.TYPE_CHECKING:
    import pathlib
    from typing import (
        Any,
        AsyncIterable,
        Callable,
        Dict,
        Iterable,
        Optional,
        Sequence,
        Tuple,
        TypeVar,
        Union,
    )

    from rossum_api.elis_api_client import APIObject, ExportFileFormats

    T = TypeVar("T")

from rossum_api.api_client import APIClient
from rossum_api.elis_api_client import ElisAPIClient
from rossum_api.models.annotation import Annotation
from rossum_api.models.connector import Connector
from rossum_api.models.hook import Hook
from rossum_api.models.inbox import Inbox
from rossum_api.models.organization import Organization
from rossum_api.models.queue import Queue
from rossum_api.models.schema import Schema
from rossum_api.models.user import User
from rossum_api.models.user_role import UserRole
from rossum_api.models.workspace import Workspace


class Sideload:
    pass


class AsyncRuntimeError(Exception):
    pass


class ElisAPIClientSync:
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[APIClient] = None,
    ):
        self.elis_api_client = ElisAPIClient(username, password, token, base_url, http_client)

        try:
            self.event_loop = asyncio.get_running_loop()
            if self.event_loop.is_running():
                raise AsyncRuntimeError(
                    "Event loop is present and already running, please use async version of the client"
                )
        except RuntimeError:
            self.event_loop = asyncio.new_event_loop()

    def _iter_over_async(self, ait: AsyncIterable[T]) -> Iterable[T]:
        ait = ait.__aiter__()
        while True:
            try:
                obj = self.event_loop.run_until_complete(ait.__anext__())
                yield obj
            except StopAsyncIteration:
                break

    # ##### QUEUE #####
    def retrieve_queue(
        self, queue_id: int, sideloads: Optional[Sequence[APIObject]] = None
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_queue(queue_id, sideloads)
        )

    def list_all_queues(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Queue]:
        """https://elis.rossum.ai/api/docs/#list-all-queues"""
        return self._iter_over_async(
            self.elis_api_client.list_all_queues(ordering, sideloads, **filters)
        )

    def create_new_queue(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#create-new-queue"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_queue(data, sideloads)
        )

    def delete_queue(self, queue_id, sideloads: Optional[Sequence[APIObject]] = None) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.delete_queue(queue_id, sideloads)
        )

    def import_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """https://elis.rossum.ai/api/docs/#import-a-document

        arguments
        ---------
            files
                2-tuple containing current filename and name to be used by elis for the uploaded file
            metadata
                metadata will be set to newly created annotation object
            values
                may be used to initialize datapoint values by setting the value of rir_field_names in the schema
        """
        return self.event_loop.run_until_complete(
            self.elis_api_client.import_document(queue_id, files, values, metadata)
        )

    def export_annotations_to_json(self, queue_id: int) -> Iterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#export-annotations

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        return self._iter_over_async(self.elis_api_client.export_annotations_to_json(queue_id))

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats
    ) -> Iterable[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        return self._iter_over_async(
            self.elis_api_client.export_annotations_to_file(queue_id, export_format)
        )

    # ##### ORGANIZATIONS #####
    def list_all_organizations(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ):
        """https://elis.rossum.ai/api/docs/#list-all-organizations"""
        return self._iter_over_async(
            self.elis_api_client.list_all_organizations(ordering, sideloads, **filters)
        )

    def retrieve_organization(
        self, org_id: int, sideloads: Optional[Sequence[APIObject]] = None
    ) -> Organization:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_organization(org_id, sideloads)
        )

    # ##### SCHEMAS #####
    def list_all_schemas(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Schema]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas"""
        return self._iter_over_async(
            self.elis_api_client.list_all_schemas(ordering, sideloads, **filters)
        )

    def retrieve_schema(
        self, schema_id: int, sideloads: Optional[Sequence[APIObject]] = None
    ) -> Schema:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_schema(schema_id, sideloads)
        )

    def create_new_schema(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Schema:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_schema(data, sideloads)
        )

    def delete_schema(self, id, sideloads: Optional[Sequence[APIObject]] = None) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema"""
        return self.event_loop.run_until_complete(self.elis_api_client.delete_schema(id, sideloads))

    # ##### USERS #####
    def list_all_users(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[User]:
        """https://elis.rossum.ai/api/docs/#list-all-users"""
        return self._iter_over_async(
            self.elis_api_client.list_all_users(ordering, sideloads, **filters)
        )

    def retrieve_user(self, user_id: int, sideloads: Optional[Sequence[APIObject]] = None) -> User:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_user(user_id, sideloads)
        )

    def create_new_user(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> User:
        """https://elis.rossum.ai/api/docs/#create-new-user"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_user(data, sideloads)
        )

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
        **filters: Dict[str, Any],
    ) -> Iterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#list-all-annotations"""
        return self._iter_over_async(
            self.elis_api_client.list_all_annotations(
                ordering, sideloads, content_schema_ids, **filters
            )
        )

    def retrieve_annotation(
        self, annotation_id: int, sideloads: Optional[Sequence[APIObject]] = None
    ) -> Annotation:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_annotation(annotation_id, sideloads)
        )

    def poll_annotation(
        self, annotation_id: int, predicate: Callable[[Annotation], bool], sleep_s: int = 3
    ) -> Annotation:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.poll_annotation(annotation_id, predicate, sleep_s)
        )

    def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-an-annotation"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.update_annotation(annotation_id, data)
        )

    def update_part_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.update_part_annotation(annotation_id, data)
        )

    # ##### WORKSPACES #####
    def list_all_workspaces(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Workspace]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces"""
        return self._iter_over_async(
            self.elis_api_client.list_all_workspaces(ordering, sideloads, **filters)
        )

    def retrieve_workspace(self, id, sideloads: Optional[Sequence[APIObject]] = None) -> Workspace:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_workspace(id, sideloads)
        )

    def create_new_workspace(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Workspace:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_workspace(data, sideloads)
        )

    def delete_workspace(self, id, sideloads: Optional[Sequence[APIObject]] = None) -> None:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.delete_workspace(id, sideloads)
        )

    # ##### INBOX #####
    def create_new_inbox(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Inbox:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_inbox(data, sideloads)
        )

    # ##### CONNECTORS #####
    def list_all_connectors(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors"""

        return self._iter_over_async(
            self.elis_api_client.list_all_connectors(ordering, sideloads, **filters)
        )

    def retrieve_connector(self, id, sideloads: Optional[Sequence[APIObject]] = None) -> Connector:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_connector(id, sideloads)
        )

    def create_new_connector(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Connector:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_connector(data, sideloads)
        )

    # ##### HOOKS #####
    def list_all_hooks(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Hook]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks"""
        return self._iter_over_async(
            self.elis_api_client.list_all_hooks(ordering, sideloads, **filters)
        )

    def retrieve_hook(self, id, sideloads: Optional[Sequence[APIObject]] = None) -> Hook:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook"""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_hook(id, sideloads))

    def create_new_hook(
        self, data: Dict[str, Any], sideloads: Optional[Sequence[APIObject]] = None
    ) -> Hook:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_hook(data, sideloads)
        )

    # ##### USER ROLES #####
    def list_all_user_roles(
        self,
        ordering: Sequence[str] = (),
        sideloads: Optional[Sequence[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[UserRole]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles"""
        return self._iter_over_async(
            self.elis_api_client.list_all_user_roles(ordering, sideloads, **filters)
        )
