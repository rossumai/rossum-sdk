import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Annotation:
    url: str
    status: str
    schema: str
    modifier: str
    content: str
    has_email_thread_with_replies: bool = False
    has_email_thread_with_new_replies: bool = False
    id: Optional[int] = None
    queue: Optional[str] = None
    creator: Optional[str] = None
    created_at: Optional[str] = None
    rir_poll_id: Optional[str] = None
    email: Optional[str] = None
    email_thread: Optional[str] = None
    suggested_edit: Optional[str] = None
    messages: List[Dict] = field(default_factory=list)
    time_spent: float = 0
    relations: List[str] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    document: Optional[str] = None
    confirmed_at: Optional[dt.datetime] = None
    modified_at: Optional[str] = None
    exported_at: Optional[str] = None
    arrived_at: Optional[str] = None
    assigned_at: Optional[str] = None
    metadata: Dict[Any, Any] = field(default_factory=dict)
    automated: bool = False
    automation_blocker: Optional[str] = None
    related_emails: List[str] = field(default_factory=list)
