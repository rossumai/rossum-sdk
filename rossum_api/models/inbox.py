from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Inbox:
    id: int
    name: str
    url: str
    queues: List[str]
    email: str
    email_prefix: str
    bounce_email_to: Optional[str]
    bounce_unprocessable_attachments: bool = False
    bounce_postponed_annotations: bool = False
    bounce_deleted_annotations: bool = False
    bounce_email_with_no_attachments: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    dmarc_check_action: str = "accept"
