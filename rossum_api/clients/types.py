from __future__ import annotations

from typing import Literal, TypeAlias

AnnotationOrdering: TypeAlias = Literal[
    "document",
    "document__arrived_at",
    "document__original_file_name",
    "modifier",
    "modifier__username",
    "modified_by",
    "modified_by__username",
    "creator",
    "creator__username",
    "queue",
    "status",
    "created_at",
    "assigned_at",
    "confirmed_at",
    "modified_at",
    "exported_at",
    "export_failed_at",
    "purged_at",
    "rejected_at",
    "deleted_at",
    "confirmed_by",
    "deleted_by",
    "exported_by",
    "purged_by",
    "rejected_by",
    "confirmed_by__username",
    "deleted_by__username",
    "exported_by__username",
    "purged_by__username",
    "rejected_by__username",
]

ConnectorOrdering: TypeAlias = Literal["id", "name", "service_url"]

DocumentRelationOrdering: TypeAlias = Literal["id", "type", "annotation"]

EmailTemplateOrdering: TypeAlias = Literal["id", "name"]

HookOrdering: TypeAlias = Literal[
    "id", "name", "type", "active", "config_url", "config_app_url", "events"
]

OrganizationOrdering: TypeAlias = Literal["id", "name"]

QueueOrdering: TypeAlias = Literal[
    "id",
    "name",
    "workspace",
    "connector",
    "webhooks",
    "schema",
    "inbox",
    "locale",
]

RuleOrdering: TypeAlias = Literal["id", "name", "organization"]

SchemaOrdering: TypeAlias = Literal["id"]

UserOrdering: TypeAlias = Literal[
    "id",
    "username",
    "first_name",
    "last_name",
    "email",
    "last_login",
    "date_joined",
    "deleted",
    "not_deleted",
]

UserRoleOrdering: TypeAlias = Literal["name"]

WorkspaceOrdering: TypeAlias = Literal["id", "name"]
