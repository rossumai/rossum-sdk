import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Annotation:
    id: int
    url: str
    status: str
    queue: str
    schema: str
    creator: str
    created_at: str
    modifier: str
    rir_poll_id: str
    content: str
    email: str
    email_thread: str
    has_email_thread_with_replies: bool
    has_email_thread_with_new_replies: bool
    suggested_edit: Optional[str] = None
    messages: List[Dict] = field(default_factory=list)
    time_spent: float = 0
    relations: List[str] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    document: Optional[str] = None
    confirmed_at: Optional[dt.datetime] = None
    modified_at: Optional[str] = None
    exported_at: Optional[str] = None
    assigned_at: Optional[str] = None
    metadata: Dict[Any, Any] = field(default_factory=dict)
    automated: bool = False
    automation_blocker: Optional[str] = None
    content: str
    related_emails: List[str] = field(default_factory=list)
