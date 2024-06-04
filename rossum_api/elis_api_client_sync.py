from __future__ import annotations

import asyncio
import typing

from rossum_api import ElisAPIClient

if typing.TYPE_CHECKING:
    import pathlib
    from typing import (
        Any,
        AsyncIterable,
        Callable,
        Dict,
        Iterable,
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
    from rossum_api.models import Deserializer
    from rossum_api.models.annotation import Annotation
    from rossum_api.models.connector import Connector
    from rossum_api.models.document import Document
    from rossum_api.models.engine import Engine
    from rossum_api.models.group import Group
    from rossum_api.models.hook import Hook
    from rossum_api.models.inbox import Inbox
    from rossum_api.models.organization import Organization
    from rossum_api.models.queue import Queue
    from rossum_api.models.schema import Schema
    from rossum_api.models.user import User
    from rossum_api.models.workspace import Workspace

    T = TypeVar("T")


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
        self.elis_api_client = ElisAPIClient(
            username, password, token, base_url, http_client, deserializer
        )

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
    def retrieve_queue(self, queue_id: int) -> Queue:
        """https://elis.rossum.ai/api/docs/#retrieve-a-queue-2."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_queue(queue_id))

    def list_all_queues(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Queue]:
        """https://elis.rossum.ai/api/docs/#list-all-queues."""
        return self._iter_over_async(self.elis_api_client.list_all_queues(ordering, **filters))

    def create_new_queue(
        self,
        data: Dict[str, Any],
    ) -> Queue:
        """https://elis.rossum.ai/api/docs/#create-new-queue."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_queue(data))

    def delete_queue(self, queue_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-queue."""
        return self.event_loop.run_until_complete(self.elis_api_client.delete_queue(queue_id))

    def import_document(
        self,
        queue_id: int,
        files: Sequence[Tuple[Union[str, pathlib.Path], str]],
        values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[int]:
        """https://elis.rossum.ai/api/docs/#import-a-document.

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
        return self.event_loop.run_until_complete(
            self.elis_api_client.import_document(queue_id, files, values, metadata)
        )

    def export_annotations_to_json(self, queue_id: int) -> Iterable[Annotation]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        JSON export is paginated and returns the result in a way similar to other list_all methods.
        """
        return self._iter_over_async(self.elis_api_client.export_annotations_to_json(queue_id))

    def export_annotations_to_file(
        self, queue_id: int, export_format: ExportFileFormats
    ) -> Iterable[bytes]:
        """https://elis.rossum.ai/api/docs/#export-annotations.

        XLSX/CSV/XML exports can be huge, therefore byte streaming is used to keep memory consumption low.
        """
        return self._iter_over_async(
            self.elis_api_client.export_annotations_to_file(queue_id, export_format)
        )

    # ##### ORGANIZATIONS #####
    def list_all_organizations(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Organization]:
        """https://elis.rossum.ai/api/docs/#list-all-organizations."""
        return self._iter_over_async(
            self.elis_api_client.list_all_organizations(ordering, **filters)
        )

    def retrieve_organization(
        self,
        org_id: int,
    ) -> Organization:
        """https://elis.rossum.ai/api/docs/#retrieve-an-organization."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_organization(org_id)
        )

    def retrieve_own_organization(self) -> Organization:
        """Retrieve organization of currently logged in user."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_own_organization())

    # ##### SCHEMAS #####
    def list_all_schemas(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Schema]:
        """https://elis.rossum.ai/api/docs/#list-all-schemas."""
        return self._iter_over_async(self.elis_api_client.list_all_schemas(ordering, **filters))

    def retrieve_schema(self, schema_id: int) -> Schema:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_schema(schema_id))

    def create_new_schema(self, data: Dict[str, Any]) -> Schema:
        """https://elis.rossum.ai/api/docs/#create-a-new-schema."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_schema(data))

    def delete_schema(self, schema_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#delete-a-schema."""
        return self.event_loop.run_until_complete(self.elis_api_client.delete_schema(schema_id))

    # ##### ENGINES #####
    def retrieve_engine(self, engine_id: int) -> Engine:
        """https://elis.rossum.ai/api/docs/#retrieve-a-schema."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_engine(engine_id))

    # ##### USERS #####
    def list_all_users(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[User]:
        """https://elis.rossum.ai/api/docs/#list-all-users."""
        return self._iter_over_async(self.elis_api_client.list_all_users(ordering, **filters))

    def retrieve_user(self, user_id: int) -> User:
        """https://elis.rossum.ai/api/docs/#retrieve-a-user-2."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_user(user_id))

    def create_new_user(self, data: Dict[str, Any]) -> User:
        """https://elis.rossum.ai/api/docs/#create-new-user."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_user(data))

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
    ) -> Iterable[Annotation]:
        """https://elis.rossum.ai/api/docs/internal/#search-for-annotations."""
        return self._iter_over_async(
            self.elis_api_client.search_for_annotations(
                query, query_string, ordering, sideloads, **kwargs
            )
        )

    def retrieve_annotation(self, annotation_id: int, sideloads: Sequence[str] = ()) -> Annotation:
        """https://elis.rossum.ai/api/docs/#retrieve-an-annotation."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_annotation(annotation_id, sideloads)
        )

    def poll_annotation(
        self,
        annotation_id: int,
        predicate: Callable[[Annotation], bool],
        sleep_s: int = 3,
        sideloads: Sequence[str] = (),
    ) -> Annotation:
        """Poll on annotation until predicate is true.

        Sideloading is done only once after the predicate becomes true to avoid spaming the server.
        """
        return self.event_loop.run_until_complete(
            self.elis_api_client.poll_annotation(annotation_id, predicate, sleep_s, sideloads)
        )

    def poll_annotation_until_imported(self, annotation_id: int, **poll_kwargs: Any) -> Annotation:
        """A shortcut for waiting until annotation is imported."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.poll_annotation_until_imported(annotation_id, **poll_kwargs)
        )

    def upload_and_wait_until_imported(
        self, queue_id: int, filepath: Union[str, pathlib.Path], filename: str, **poll_kwargs
    ) -> Annotation:
        """A shortcut for uploading a single file and waiting until its annotation is imported."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.upload_and_wait_until_imported(
                queue_id, filepath, filename, **poll_kwargs
            )
        )

    def start_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#start-annotation"""
        self.event_loop.run_until_complete(self.elis_api_client.start_annotation(annotation_id))

    def update_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-an-annotation."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.update_annotation(annotation_id, data)
        )

    def update_part_annotation(self, annotation_id: int, data: Dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#update-part-of-an-annotation."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.update_part_annotation(annotation_id, data)
        )

    def bulk_update_annotation_data(
        self, annotation_id: int, operations: List[Dict[str, Any]]
    ) -> None:
        """https://elis.rossum.ai/api/docs/#bulk-update-annotation-data"""
        self.event_loop.run_until_complete(
            self.elis_api_client.bulk_update_annotation_data(annotation_id, operations)
        )

    def confirm_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#confirm-annotation"""
        self.event_loop.run_until_complete(self.elis_api_client.confirm_annotation(annotation_id))

    def create_new_annotation(self, data: dict[str, Any]) -> Annotation:
        """https://elis.rossum.ai/api/docs/#create-an-annotation"""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_annotation(data))

    def delete_annotation(self, annotation_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#switch-to-deleted"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.delete_annotation(annotation_id)
        )

    # ##### DOCUMENTS #####
    def retrieve_document_content(self, document_id: int) -> bytes:
        """https://elis.rossum.ai/api/docs/#document-content"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_document_content(document_id)
        )

    def create_new_document(
        self,
        file_name: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None,
    ) -> Document:
        """https://elis.rossum.ai/api/docs/#create-document"""
        return self.event_loop.run_until_complete(
            self.elis_api_client.create_new_document(file_name, file_data, metadata, parent)
        )

    # ##### WORKSPACES #####
    def list_all_workspaces(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Workspace]:
        """https://elis.rossum.ai/api/docs/#list-all-workspaces."""
        return self._iter_over_async(self.elis_api_client.list_all_workspaces(ordering, **filters))

    def retrieve_workspace(self, workspace_id: int) -> Workspace:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_workspace(workspace_id)
        )

    def create_new_workspace(self, data: Dict[str, Any]) -> Workspace:
        """https://elis.rossum.ai/api/docs/#create-a-new-workspace."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_workspace(data))

    def delete_workspace(self, workspace_id: int) -> None:
        """https://elis.rossum.ai/api/docs/#retrieve-a-workspace."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.delete_workspace(workspace_id)
        )

    # ##### INBOX #####
    def create_new_inbox(
        self,
        data: Dict[str, Any],
    ) -> Inbox:
        """https://elis.rossum.ai/api/docs/#create-a-new-inbox."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_inbox(data))

    # ##### CONNECTORS #####
    def list_all_connectors(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Connector]:
        """https://elis.rossum.ai/api/docs/#list-all-connectors."""
        return self._iter_over_async(self.elis_api_client.list_all_connectors(ordering, **filters))

    def retrieve_connector(self, connector_id: int) -> Connector:
        """https://elis.rossum.ai/api/docs/#retrieve-a-connector."""
        return self.event_loop.run_until_complete(
            self.elis_api_client.retrieve_connector(connector_id)
        )

    def create_new_connector(self, data: Dict[str, Any]) -> Connector:
        """https://elis.rossum.ai/api/docs/#create-a-new-connector."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_connector(data))

    # ##### HOOKS #####
    def list_all_hooks(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Hook]:
        """https://elis.rossum.ai/api/docs/#list-all-hooks."""
        return self._iter_over_async(self.elis_api_client.list_all_hooks(ordering, **filters))

    def retrieve_hook(self, hook_id: int) -> Hook:
        """https://elis.rossum.ai/api/docs/#retrieve-a-hook."""
        return self.event_loop.run_until_complete(self.elis_api_client.retrieve_hook(hook_id))

    def create_new_hook(self, data: Dict[str, Any]) -> Hook:
        """https://elis.rossum.ai/api/docs/#create-a-new-hook."""
        return self.event_loop.run_until_complete(self.elis_api_client.create_new_hook(data))

    # ##### USER ROLES #####
    def list_all_user_roles(
        self,
        ordering: Sequence[str] = (),
        **filters: Dict[str, Any],
    ) -> Iterable[Group]:
        """https://elis.rossum.ai/api/docs/#list-all-user-roles."""
        return self._iter_over_async(self.elis_api_client.list_all_user_roles(ordering, **filters))

    def request_paginated(self, url: str, *args, **kwargs) -> Iterable[dict]:
        """Use to perform requests to seldomly used or experimental endpoints with paginated response that do not have
        direct support in the client and return iterable.
        """
        return self._iter_over_async(self.elis_api_client.request_paginated(url, *args, **kwargs))

    def request_json(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return JSON.
        """
        return self.event_loop.run_until_complete(
            self.elis_api_client.request_json(method, *args, **kwargs)
        )

    def request(self, method: str, *args, **kwargs) -> httpx.Response:
        """Use to perform requests to seldomly used or experimental endpoints that do not have
        direct support in the client and return the raw response.
        """
        return self.event_loop.run_until_complete(
            self.elis_api_client.request(method, *args, **kwargs)
        )

    def get_token(self, refresh: bool = False) -> str:
        """Returns the current token. Authentication is done automatically if needed.

        Parameters
        ----------
        refresh
            force refreshing the token
        """
        return self.event_loop.run_until_complete(self.elis_api_client.get_token(refresh))
