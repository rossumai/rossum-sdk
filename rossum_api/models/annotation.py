from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from rossum_api.models.automation_blocker import AutomationBlocker
from rossum_api.models.document import Document
from rossum_api.models.user import User


@dataclass
class Prediction:
    source: str
    version: str | None = None


@dataclass
class Annotation:
    url: str
    status: str
    schema: str
    modifier: str | User | None
    content: List[Dict[str, Any]] | str  # No dataclass for Annotation content yet
    id: int | None = None
    queue: str | None = None
    creator: str | None = None
    created_at: str | None = None
    rir_poll_id: str | None = None
    email: str | None = None
    email_thread: str | None = None
    has_email_thread_with_replies: bool = False
    has_email_thread_with_new_replies: bool = False
    suggested_edit: str | None = None
    messages: List[dict] | None = None
    time_spent: float | None = 0
    relations: List[str] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    document: str | Document | None = None
    confirmed_at: str | None = None
    modified_at: str | None = None
    exported_at: str | None = None
    arrived_at: str | None = None
    assigned_at: str | None = None
    purged_at: str | None = None
    rejected_at: str | None = None
    deleted_at: str | None = None
    export_failed_at: str | None = None
    organization: str | None = None
    metadata: Dict[Any, Any] = field(default_factory=dict)
    automated: bool = False
    automation_blocker: AutomationBlocker | str | None = None
    related_emails: List[str] = field(default_factory=list)
    automatically_rejected: bool | None = None
    prediction: Prediction | None = None
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    restricted_access: bool | None = None
    training_enabled: bool | None = None
    einvoice: bool | None = None
    purged_by: str | None = None
    rejected_by: str | None = None
    deleted_by: str | None = None
    exported_by: str | None = None
    confirmed_by: str | None = None
    modified_by: str | None = None
