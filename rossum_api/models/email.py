from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EmailType(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


@dataclass
class Email:
    id: int
    url: str
    queue: str
    inbox: str
    parent: str | None
    email_thread: str | None
    children: List[str]
    documents: List[str]
    created_at: str | None = None
    last_thread_email_created_at: str | None = None
    subject: str | None = None
    # "from" is converted to "from_" during the deserialization, see rossum_api.models._convert_key function.
    from_: Dict[str, Any] = field(default_factory=dict)
    to: List[Dict[str, Any]] = field(default_factory=list)
    cc: List[Dict[str, Any]] = field(default_factory=list)
    bcc: List[Dict[str, Any]] = field(default_factory=list)
    body_text_plain: str | None = None
    body_text_html: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: EmailType | None = None
    annotation_counts: Dict[str, Any] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)
    related_annotations: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    creator: str | None = None
    filtered_out_document_count: int | None = None
    labels: List[str] = field(default_factory=list)
    content: str | None = None
