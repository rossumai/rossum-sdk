from __future__ import annotations

from typing import TYPE_CHECKING

import dacite

from rossum_api.api_client import Resource
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

if TYPE_CHECKING:
    from typing import Any, Callable, Dict

    JsonDict = Dict[str, Any]
    Deserializer = Callable[[Resource, JsonDict], Any]


RESOURCE_TO_MODEL = {
    Resource.Annotation: Annotation,
    Resource.Connector: Connector,
    Resource.Group: UserRole,
    Resource.Hook: Hook,
    Resource.Inbox: Inbox,
    Resource.Organization: Organization,
    Resource.Queue: Queue,
    Resource.Schema: Schema,
    Resource.User: User,
    Resource.Workspace: Workspace,
}


def deserialize_default(resource: Resource, payload: JsonDict) -> Any:
    """Deserialize payload into dataclasses using dacite."""
    model_class = RESOURCE_TO_MODEL[resource]
    return dacite.from_dict(model_class, payload)
