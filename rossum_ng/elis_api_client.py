from typing import Any, AsyncIterable, Dict, Iterable, Optional

from rossum_ng.api_client import APIClient
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


class APIObject:
    pass


class Sideload:
    pass


class ElisAPIClient:
    def __init__(
        self,
        username: str,
        password: str,
        base_url: Optional[str],
        http_client: Optional[APIClient] = None,
    ):
        self._http_client = http_client or APIClient(username, password, base_url)

    # ##### QUEUE #####
    # https://elis.rossum.ai/api/docs/#retrieve-a-queue-2
    async def retrieve_queue(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Queue:
        queue = await self._http_client.fetch_one("queues", id)

        return Queue(**queue)

    # https://elis.rossum.ai/api/docs/#list-all-queues
    async def list_all_queues(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Queue]:
        async for q in self._http_client.fetch_all("queues", ordering, **filters):
            yield Queue(**q)

    # https://elis.rossum.ai/api/docs/#create-new-queue
    async def create_new_queue(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Queue:
        queue = await self._http_client.create("queues", data)

        return Queue(**queue)

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
    async def list_all_organizations(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ):
        async for o in self._http_client.fetch_all("organizations", ordering, **filters):
            yield Organization(**o)

    # https://elis.rossum.ai/api/docs/#retrieve-an-organization
    async def retrieve_organization(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Organization:
        organization: Dict[Any, Any] = await self._http_client.fetch_one("organizations", id)

        return Organization(**organization)

    # ##### SCHEMAS #####
    # https://elis.rossum.ai/api/docs/#list-all-schemas
    async def list_all_schemas(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Schema]:
        async for s in self._http_client.fetch_all("schemas", ordering, **filters):
            yield Schema(**s)

    # https://elis.rossum.ai/api/docs/#retrieve-a-schema
    async def retrieve_schema(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Schema:
        schema: Dict[Any, Any] = await self._http_client.fetch_one("schemas", id)

        return Schema(**schema)

    # https://elis.rossum.ai/api/docs/#create-a-new-schema
    async def create_new_schema(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Schema:
        queue = await self._http_client.create("schemas", data)

        return Schema(**queue)

    # ##### USERS #####
    # https://elis.rossum.ai/api/docs/#list-all-users
    async def list_all_users(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[User]:
        async for u in self._http_client.fetch_all("users", ordering, **filters):
            yield User(**u)

    # https://elis.rossum.ai/api/docs/#retrieve-a-user-2
    async def retrieve_user(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> User:
        user = await self._http_client.fetch_one("users", id)

        return User(**user)

    # https://elis.rossum.ai/api/docs/#create-new-user
    async def create_new_user(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> User:
        user = await self._http_client.create("users", data)

        return User(**user)

    # TODO: specific method in APICLient
    def change_user_password(self, new_password: str) -> dict:
        return {}

    # TODO: specific method in APICLient
    def reset_user_password(self, email: str) -> dict:
        return {}

    # ##### ANNOTATIONS #####
    # https://elis.rossum.ai/api/docs/#list-all-annotations
    async def list_all_annotations(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Annotation]:
        async for a in self._http_client.fetch_all("annotations", ordering, **filters):
            yield Annotation(**a)

    # https://elis.rossum.ai/api/docs/#retrieve-an-annotation
    async def retrieve_annotation(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Annotation:
        annotation = await self._http_client.fetch_one("annotations", id)

        return Annotation(**annotation)

    # https://elis.rossum.ai/api/docs/#update-an-annotation
    async def update_annotation(self, id: int, data: Dict[str, Any]) -> Annotation:
        annotation = await self._http_client.replace("annotations", id, data)

        return Annotation(**annotation)

    # https://elis.rossum.ai/api/docs/#update-part-of-an-annotation
    async def update_part_annotation(self, id: int, data: Dict[str, Any]) -> Annotation:
        annotation = await self._http_client.update("annotations", id, data)

        return Annotation(**annotation)

    # ##### WORKSPACES #####
    # https://elis.rossum.ai/api/docs/#list-all-workspaces
    async def list_all_workspaces(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Workspace]:
        async for w in self._http_client.fetch_all("workspaces", ordering, **filters):
            yield Workspace(**w)

    # https://elis.rossum.ai/api/docs/#retrieve-a-workspace
    async def retrieve_workspace(
        self, id, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Workspace:
        workspace = await self._http_client.fetch_one("workspaces", id)

        return Workspace(**workspace)

    # https://elis.rossum.ai/api/docs/#create-a-new-workspace
    async def create_new_workspace(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Workspace:
        workspace = await self._http_client.create("workspaces", data)

        return Workspace(**workspace)

    # ##### INBOX #####
    # https://elis.rossum.ai/api/docs/#create-a-new-inbox
    async def create_new_inbox(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Inbox:
        inbox = await self._http_client.create("inboxes", data)

        return Inbox(**inbox)

    # ##### CONNECTORS #####
    # https://elis.rossum.ai/api/docs/#list-all-connectors
    async def list_all_connectors(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Connector]:

        async for c in self._http_client.fetch_all("connectors", ordering, **filters):
            yield Connector(**c)

    # https://elis.rossum.ai/api/docs/#retrieve-a-connector
    async def retrieve_connector(
        self, id, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Connector:
        connector = await self._http_client.fetch_one("connectors", id)

        return Connector(**connector)

    # https://elis.rossum.ai/api/docs/#create-a-new-connector
    async def create_new_connector(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Connector:
        connector = await self._http_client.create("connectors", data)

        return Connector(**connector)

    # ##### HOOKS #####
    # https://elis.rossum.ai/api/docs/#list-all-hooks
    async def list_all_hooks(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[Hook]:
        async for h in self._http_client.fetch_all("hooks", ordering, **filters):
            yield Hook(**h)

    # https://elis.rossum.ai/api/docs/#retrieve-a-hook
    async def retrieve_hook(self, id, sideloads: Optional[Iterable[APIObject]] = None) -> Hook:
        hook = await self._http_client.fetch_one("hooks", id)

        return Hook(**hook)

    # https://elis.rossum.ai/api/docs/#create-a-new-hook
    async def create_new_hook(
        self, data: Dict[str, Any], sideloads: Optional[Iterable[APIObject]] = None
    ) -> Hook:
        hook = await self._http_client.create("hooks", data)

        return Hook(**hook)

    # ##### USER ROLES #####
    # https://elis.rossum.ai/api/docs/#list-all-user-roles
    async def list_all_user_roles(
        self,
        ordering: Iterable[str] = (),
        sideloads: Optional[Iterable[APIObject]] = None,
        **filters: Dict[str, Any],
    ) -> AsyncIterable[UserRole]:
        async for u in self._http_client.fetch_all("groups", ordering, **filters):
            yield UserRole(**u)
