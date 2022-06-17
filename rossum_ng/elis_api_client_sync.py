import asyncio
from typing import Any, AsyncIterable, Dict, Iterable, Optional, TypeVar

from rossum_ng.api_client import APIClient
from rossum_ng.elis_api_client import APIObject, ElisAPIClient
from rossum_ng.models.annotation import Annotation
from rossum_ng.models.connector import Connector
from rossum_ng.models.hook import Hook
from rossum_ng.models.inbox import Inbox
from rossum_ng.models.organization import Organization
from rossum_ng.models.queue import Queue
from rossum_ng.models.schema import Schema
from rossum_ng.models.user import User
from rossum_ng.models.user_role import UserRole
from rossum_ng.models.workspace import Workspace


class Sideload:
    pass


T = TypeVar("T")


class ElisAPIClientSync(ElisAPIClient):
    def __init__(
        self,
        username: str,
        password: str,
        base_url: Optional[str],
        http_client: Optional[APIClient] = None,
    ):
        super().__init__(username, password, base_url, http_client)
        self.event_loop = asyncio.get_event_loop()

    def _iter_over_async(self, ait: AsyncIterable[T]) -> Iterable[T]:
        ait = ait.__aiter__()
        while True:
            try:
                obj = self.event_loop.run_until_complete(ait.__anext__())
                yield obj
            except StopAsyncIteration:
                break

    # ##### QUEUE #####
    # https://elis.rossum.ai/api/docs/#retrieve-a-queue-2
    def retrieve_queue(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> Queue:
        return self.event_loop.run_until_complete(super().retrieve_queue(id, sideloads))

    # https://elis.rossum.ai/api/docs/#list-all-queues
    def list_all_queues(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Queue]:
        return self._iter_over_async(super().list_all_queues(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#create-new-queue
    def create_new_queue(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Queue:
        return self.event_loop.run_until_complete(super().create_new_queue(data, sideloads))

    # TODO: specific method in APICLient
    def upload_document(
        self,
        id_: int,
        file: Optional[str] = "",
        filename_overwrite: str = "",
        values: Dict[str, str] = None,
        metadata: Optional[Dict] = None,
        file_bytes: Optional[bytes] = None,
    ) -> dict:
        return {}

    # TODO: specific method in APICLient
    def export_annotations(self, id_: int, annotation_ids: Iterable[int], format_: str) -> dict:
        return {}

    # ##### ORGANIZATIONS #####
    # https://elis.rossum.ai/api/docs/#list-all-organizations
    def list_all_organizations(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ):
        return self._iter_over_async(super().list_all_organizations(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-an-organization
    def retrieve_organization(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Organization:
        return self.event_loop.run_until_complete(super().retrieve_organization(id, sideloads))

    # ##### SCHEMAS #####
    # https://elis.rossum.ai/api/docs/#list-all-schemas
    def list_all_schemas(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Schema]:
        return self._iter_over_async(super().list_all_schemas(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-a-schema
    def retrieve_schema(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> Schema:
        return self.event_loop.run_until_complete(super().retrieve_schema(id, sideloads))

    # https://elis.rossum.ai/api/docs/#create-a-new-schema
    def create_new_schema(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Schema:
        return self.event_loop.run_until_complete(super().create_new_schema(data, sideloads))

    # ##### USERS #####
    # https://elis.rossum.ai/api/docs/#list-all-users
    def list_all_users(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[User]:
        return self._iter_over_async(super().list_all_users(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-a-user-2
    def retrieve_user(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> User:
        return self.event_loop.run_until_complete(super().retrieve_user(id, sideloads))

    # https://elis.rossum.ai/api/docs/#create-new-user
    def create_new_user(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> User:
        return self.event_loop.run_until_complete(super().create_new_user(data, sideloads))

    # TODO: specific method in APICLient
    def change_user_password(self, new_password: str) -> dict:
        return {}

    # TODO: specific method in APICLient
    def reset_user_password(self, email: str) -> dict:
        return {}

    # ##### ANNOTATIONS #####
    # https://elis.rossum.ai/api/docs/#list-all-annotations
    def list_all_annotations(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Annotation]:
        return self._iter_over_async(super().list_all_annotations(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-an-annotation
    def retrieve_annotation(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Annotation:
        return self.event_loop.run_until_complete(super().retrieve_annotation(id, sideloads))

    # https://elis.rossum.ai/api/docs/#update-an-annotation
    def update_annotation(self, id: int, data: Dict[str, Any]) -> Annotation:
        return self.event_loop.run_until_complete(super().update_annotation(id, data))

    # https://elis.rossum.ai/api/docs/#update-part-of-an-annotation
    def update_part_annotation(self, id: int, data: Dict[str, Any]) -> Annotation:
        return self.event_loop.run_until_complete(super().update_part_annotation(id, data))

    # ##### WORKSPACES #####
    # https://elis.rossum.ai/api/docs/#list-all-workspaces
    def list_all_workspaces(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Workspace]:
        return self._iter_over_async(super().list_all_workspaces(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-a-workspace
    def retrieve_workspace(self, id, sideloads: Optional[Iterable[APIObject]] = None) -> Workspace:
        return self.event_loop.run_until_complete(super().retrieve_workspace(id, sideloads))

    # https://elis.rossum.ai/api/docs/#create-a-new-workspace
    def create_new_workspace(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Workspace:
        return self.event_loop.run_until_complete(super().create_new_workspace(data, sideloads))

    # ##### INBOX #####
    # https://elis.rossum.ai/api/docs/#create-a-new-inbox
    def create_new_inbox(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Inbox:
        return self.event_loop.run_until_complete(super().create_new_inbox(data, sideloads))

    # ##### CONNECTORS #####
    # https://elis.rossum.ai/api/docs/#list-all-connectors
    def list_all_connectors(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Connector]:

        return self._iter_over_async(super().list_all_connectors(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-a-connector
    def retrieve_connector(self, id, sideloads: Optional[Iterable[APIObject]] = None) -> Connector:
        return self.event_loop.run_until_complete(super().retrieve_connector(id, sideloads))

    # https://elis.rossum.ai/api/docs/#create-a-new-connector
    def create_new_connector(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Connector:
        return self.event_loop.run_until_complete(super().create_new_connector(data, sideloads))

    # ##### HOOKS #####
    # https://elis.rossum.ai/api/docs/#list-all-hooks
    def list_all_hooks(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[Hook]:
        return self._iter_over_async(super().list_all_hooks(ordering, sideloads, **filters))

    # https://elis.rossum.ai/api/docs/#retrieve-a-hook
    def retrieve_hook(self, id, sideloads: Optional[Iterable[APIObject]] = None) -> Hook:
        return self.event_loop.run_until_complete(super().retrieve_hook(id, sideloads))

    # https://elis.rossum.ai/api/docs/#create-a-new-hook
    def create_new_hook(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Hook:
        return self.event_loop.run_until_complete(super().create_new_hook(data, sideloads))

    # ##### USER ROLES #####
    # https://elis.rossum.ai/api/docs/#list-all-user-roles
    def list_all_user_roles(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> Iterable[UserRole]:
        return self._iter_over_async(super().list_all_user_roles(ordering, sideloads, **filters))
