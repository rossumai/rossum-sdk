from __future__ import annotations

from enum import Enum


class Resource(Enum):
    """Convenient representation of resources provided by Elis API.

    Value is always the corresponding URL part.
    """

    Annotation = "annotations"
    Auth = "auth"
    Connector = "connectors"
    Document = "documents"
    DocumentRelation = "document_relations"
    EmailTemplate = "email_templates"
    Engine = "engines"
    EngineField = "engine_fields"
    Group = "groups"
    Hook = "hooks"
    Inbox = "inboxes"
    Email = "emails"
    Organization = "organizations"
    Queue = "queues"
    Schema = "schemas"
    Task = "tasks"
    Upload = "uploads"
    User = "users"
    Workspace = "workspaces"
