from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import dacite

from rossum_api.domain_logic.resources import Resource
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
from rossum_api.models.schema import Schema
from rossum_api.models.task import Task
from rossum_api.models.upload import Upload
from rossum_api.models.user import User
from rossum_api.models.workspace import Workspace

if TYPE_CHECKING:
    from typing import Any, Callable, Dict

    import httpx

    JsonDict = Dict[str, Any]
    Deserializer = Callable[[Resource, JsonDict], Any]
    ResponsePostProcessor = Callable[[httpx.Response], Any]


RESOURCE_TO_MODEL = {
    Resource.Annotation: Annotation,
    Resource.Connector: Connector,
    Resource.Document: Document,
    Resource.DocumentRelation: DocumentRelation,
    Resource.EmailTemplate: EmailTemplate,
    Resource.Engine: Engine,
    Resource.EngineField: EngineField,
    Resource.Group: Group,
    Resource.Hook: Hook,
    Resource.Inbox: Inbox,
    Resource.Email: Email,
    Resource.Organization: Organization,
    Resource.Queue: Queue,
    Resource.Schema: Schema,
    Resource.Task: Task,
    Resource.Upload: Upload,
    Resource.User: User,
    Resource.Workspace: Workspace,
}


def _convert_key(key: str) -> str:
    """Convert reserved words to valid ones by adding _ to the end.

    Used in Email dataclass.
    """
    if key == "from_":
        return "from"

    return key


def deserialize_default(resource: Resource, payload: JsonDict) -> Any:
    """Deserialize payload into dataclasses using dacite.

    Dacite from_dict has some limitations and not all types will work easily,
    for example datetime."""
    model_class = RESOURCE_TO_MODEL[resource]
    return dacite.from_dict(
        model_class, payload, config=dacite.Config(cast=[Enum], convert_key=_convert_key)
    )
