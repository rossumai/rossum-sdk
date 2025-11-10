"""Type definitions for the Rossum API SDK."""

from __future__ import annotations

import typing
from typing import Any, Literal

from rossum_api.utils import ObjectWithStatus

JsonDict = dict[str, Any]

HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

# Sideloads allow fetching related resources in a single request.
# See https://elis.rossum.ai/api/docs/#webhook-events for more information.
Sideload = Literal["content", "automation_blockers", "documents", "modifiers", "queues"]

# Super type for use with deserialize_default
RossumApiType = typing.TypeVar("RossumApiType")

# Specific type variables for different API entities
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
RuleType = typing.TypeVar("RuleType")
SchemaType = typing.TypeVar("SchemaType")
TaskType = typing.TypeVar("TaskType", bound=ObjectWithStatus)
UploadType = typing.TypeVar("UploadType")
UserType = typing.TypeVar("UserType")
WorkspaceType = typing.TypeVar("WorkspaceType")
