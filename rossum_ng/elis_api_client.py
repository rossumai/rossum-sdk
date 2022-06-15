from rossum_ng.api_client import APIClient
from rossum_ng.models.organization import Organization
from rossum_ng.models.queue import Queue
from typing import Optional, Union, Dict, List, Iterable, Sequence, Any

from rossum_ng.models.schema import Schema
from rossum_ng.models.user import User
from rossum_ng.models.annotation import Annotation


class APIObject:
    pass


class Sideload:
    pass


class ElisAPIClient:
    def __init__(
        self,
        endpoint="https://api.elis.rossum.ai",
        auth_token=None,
        version="v1",
        http_client: Optional[APIClient] = None,
    ):
        """Setups connection. If credentials is None, it reads $ELIS_CONFIG by configparser
        (default is config/elis.ini)
        """
        self.endpoint = endpoint.strip("/") + "/" + version
        self._auth_token = auth_token
        self._auth_header = None
        self._http_client = http_client or APIClient()

    def get_queue(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> Queue:
        queue: Dict[Any, Any] = self._http_client.get(f"/queues/{id}")

        return Queue(**queue)

    # https://elis.rossum.ai/api/docs/#list-all-queues
    def get_queues(
        self, sideloads: Optional[Iterable[APIObject]] = None, **filters
    ) -> Iterable[Queue]:
        queues: Iterable[Dict[Any, Any]] = self._http_client.get("/queues", filters)

        return (Queue(**q) for q in queues)

    def get_organizations(self, sideloads: Optional[Iterable[APIObject]] = None, **filters):
        organizations: Iterable[Dict[Any, Any]] = self._http_client.get("/organizations", filters)

        return (Organization(**o) for o in organizations)

    def get_organization(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Organization:
        organization: Dict[Any, Any] = self._http_client.get(f"/organizations/{id}")

        return Organization(**organization)

    def get_schemas(
        self, sideloads: Optional[Iterable[APIObject]] = None, **filters
    ) -> Iterable[Schema]:
        schemas: Iterable[Dict[Any, Any]] = self._http_client.get(f"/schemas", filters)

        return (Schema(**s) for s in schemas)

    def get_schema(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> Schema:
        schema: Dict[Any, Any] = self._http_client.get(f"/schemas/{id}")

        return Schema(**schema)

    def get_users(
        self, sideloads: Optional[Iterable[APIObject]] = None, **filters
    ) -> Iterable[User]:
        users: Iterable[Dict[Any, Any]] = self._http_client.get(f"/users", filters)

        return (User(**u) for u in users)

    def get_user(self, id: int, sideloads: Optional[Iterable[APIObject]] = None) -> User:
        user: Dict[Any, Any] = self._http_client.get(f"/users/{id}")

        return User(**user)

    def get_annotations(self, sideloads: Optional[Iterable[APIObject]] = None, **filters):
        annotations: Iterable[Dict[Any, Any]] = self._http_client.get(f"/annotations", filters)

        return (Annotation(**u) for u in annotations)

    def get_annotation(
        self, id: int, sideloads: Optional[Iterable[APIObject]] = None
    ) -> Annotation:
        annotation: Dict[Any, Any] = self._http_client.get(f"/annotations/{id}")

        return Annotation(**annotation)

    def get_paginated(
        self,
        url: str,
        params: Dict[str, Any] = None,
        sideloads: Sequence[str] = None,
        page_count: int = None,
    ):
        pass

    def get_queue_metadata(self, queue):
        pass

    def update_queue_metadata(self, queue, data):
        pass

    def update_queue_metadata_key(self, queue, key, value):
        pass

    def update_annotation_metadata(self, annotation, data):
        pass

    def update_annotation(self, annotation, data):
        pass

    def upload(self, file_name, queue):
        pass

    def get_workspaces(
        self,
        sideloads: Optional[Iterable[APIObject]] = None,
        *,
        organization: Optional[int] = None,
    ) -> List[dict]:
        return []

    def get_workspace(
        self, id_: Optional[int] = None, sideloads: Optional[Iterable[APIObject]] = None
    ) -> dict:
        return {}

    def get_groups(self, *, group_name: Optional[str]) -> List[dict]:
        return []

    def get_connectors(self, sideloads: Optional[Iterable[APIObject]] = None) -> List[dict]:
        return []

    def get_hooks(
        self, sideloads: Optional[Iterable[APIObject]] = None, query: Dict = None
    ) -> List[dict]:
        return []

    # def get_annotations(
    # self,
    # filters: Dict[str, Any] = None,
    # fields: Sequence[str] = None,
    # page_size: int = None,
    # sideload: Sequence[str] = None,
    # page_count: int = None,
    # ):
    # pass

    def create_workspace(
        self, name: str, organization: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        return {}

    def create_schema(self, name: str, content: List[dict]) -> dict:
        return {}

    def create_queue(
        self,
        name: str,
        workspace_url: str,
        schema_url: str,
        connector_url: Optional[str] = None,
        hooks_urls: Optional[List] = None,
        locale: Optional[str] = None,
        rir_url: str = "https://all.rir.rossum.ai",
        rir_params: str = "",
    ) -> dict:
        return {}

    def create_inbox(
        self,
        name: str,
        email_prefix: Optional[str],
        bounce_email: Optional[str],
        queue_url: str,
        email: Optional[str] = None,
    ) -> dict:
        return {}

    def create_user(
        self,
        username: str,
        organization: str,
        queues: List[str],
        password: str,
        group: str,
        locale: str,
    ) -> dict:
        return {}

    def change_user_password(self, new_password: str) -> dict:
        return {}

    def reset_user_password(self, email: str) -> dict:
        return {}

    def create_connector(
        self,
        name: str,
        queues: List[str],
        service_url: str,
        authorization_token: str = None,
        params: Optional[str] = None,
        asynchronous: Optional[bool] = True,
    ) -> dict:
        return {}

    def create_hook(
        self,
        name: str,
        hook_type: str,
        queues: List[str],
        active: bool,
        events: List[str],
        sideload: List[str],
        config: Dict,
        run_after: List[str] = None,
        metadata: Optional[Dict] = None,
        token_owner: Optional[str] = "",
        test: Optional[Dict] = None,
        **kwargs: Any,
    ) -> dict:
        return {}

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

    def set_metadata(self, object_type: APIObject, object_id: int, metadata: Dict[str, Any]):
        pass

    def export_data(self, id_: int, annotation_ids: Iterable[int], format_: str) -> dict:
        return {}
