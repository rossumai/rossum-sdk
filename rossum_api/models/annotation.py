from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from rossum_api.models.automation_blocker import AutomationBlocker
from rossum_api.models.document import Document
from rossum_api.models.user import User


@dataclass
class Prediction:
    source: str
    version: Optional[str] = None


@dataclass
class Annotation:
    url: str
    status: str
    schema: str
    modifier: Optional[Union[str, User]]
    content: Union[List[Dict[str, Any]], str]  # No dataclass for Annotation content yet
    id: Optional[int] = None
    queue: Optional[str] = None
    creator: Optional[str] = None
    created_at: Optional[str] = None
    rir_poll_id: Optional[str] = None
    email: Optional[str] = None
    email_thread: Optional[str] = None
    has_email_thread_with_replies: bool = False
    has_email_thread_with_new_replies: bool = False
    suggested_edit: Optional[str] = None
    messages: Optional[List[dict]] = None
    time_spent: Optional[float] = 0
    relations: List[str] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    document: Optional[Union[str, Document]] = None
    confirmed_at: Optional[str] = None
    modified_at: Optional[str] = None
    exported_at: Optional[str] = None
    arrived_at: Optional[str] = None
    assigned_at: Optional[str] = None
    purged_at: Optional[str] = None
    rejected_at: Optional[str] = None
    deleted_at: Optional[str] = None
    export_failed_at: Optional[str] = None
    organization: Optional[str] = None
    metadata: Dict[Any, Any] = field(default_factory=dict)
    automated: bool = False
    automation_blocker: Optional[Union[AutomationBlocker, str]] = None
    related_emails: List[str] = field(default_factory=list)
    automatically_rejected: Optional[bool] = None
    prediction: Optional[Prediction] = None
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    restricted_access: Optional[bool] = None
    training_enabled: Optional[bool] = None
    einvoice: Optional[bool] = None
    purged_by: Optional[str] = None
    rejected_by: Optional[str] = None
    deleted_by: Optional[str] = None
    exported_by: Optional[str] = None
    confirmed_by: Optional[str] = None
    modified_by: Optional[str] = None
