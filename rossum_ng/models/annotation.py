import datetime as dt
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from rossum_ng.models.automation_blocker import AutomationBlocker
from rossum_ng.models.base import Base
from rossum_ng.models.document import Document
from rossum_ng.models.user import User


class Annotation(Base):
    url: str
    status: str
    schema_: Union[str, dict] = Field(alias="schema")  # schema is reserved word in pydantic
    modifier: Union[str, User, None]
    content: Union[List[dict], str]
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
    messages: Optional[List[Dict]] = Field(default_factory=list)
    time_spent: float = 0
    relations: List[str] = Field(default_factory=list)
    pages: List[str] = Field(default_factory=list)
    document: Union[str, Document, None] = None
    confirmed_at: Optional[dt.datetime] = None
    modified_at: Optional[str] = None
    exported_at: Optional[str] = None
    arrived_at: Optional[str] = None
    assigned_at: Optional[str] = None
    organization: Optional[str] = None
    metadata: Dict[Any, Any] = Field(default_factory=dict)
    automated: bool = False
    automation_blocker: Optional[Union[AutomationBlocker, str]] = None
    related_emails: List[str] = Field(default_factory=list)
